import math
import unittest
from pathlib import Path
from visionpro.audit import audit, read_scores
from visionpro.scrape import clean_text, extract, fetch_page
from visionpro.text_mining import tfidf, filter_terms

ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    def test_ptt_excludes_identity_handles_entities_and_deduplicates(self):
        html = (ROOT/'tests/fixtures/ptt_synthetic.html').read_text()
        rows = extract(html, 'ptt', 'https://example.org/fixture')
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['text'], 'MR 技術很好,但價格太貴 & 內容仍不足。')
        self.assertNotIn('synthetic-user', str(rows))
        self.assertNotIn('192.0.2.1', str(rows))
        self.assertIn('沒有不適', rows[1]['text'])

    def test_news_excludes_navigation_and_footer(self):
        rows = extract((ROOT/'tests/fixtures/news_synthetic.html').read_text(), 'news', 'https://example.org')
        self.assertEqual([r['text'] for r in rows], ['AR 與 MR 提供不同的應用。', '價格與內容生態系仍需研究。'])

    def test_missing_selector_fails_explicitly(self):
        with self.assertRaises(ValueError):
            extract('<p>No PTT content</p>', 'ptt', 'https://example.org')

    def test_ip_removed_without_erasing_negation_or_amounts(self):
        self.assertEqual(clean_text('沒有不適 10.7萬 192.0.2.1'), '沒有不適 10.7萬 [IP removed]')

    def test_unsupported_url_rejected_before_network(self):
        for url in ['http://example.org/a', 'https://other.example/a', 'https://u:p@example.org/a', 'https://example.org:8443/a']:
            with self.assertRaises(ValueError):
                fetch_page(url, {'example.org'})

    def test_known_snapshot_reconciles_report_and_missing_text(self):
        result = audit(read_scores(ROOT/'data/historical_scores.csv'))
        self.assertEqual(result['all_stored_labels']['counts'], {'positive':42,'neutral':9,'negative':29})
        self.assertEqual(result['text_present_only']['counts'], {'positive':34,'neutral':9,'negative':29})
        self.assertEqual(result['excluded_empty_text']['sheet_rows'], [38,44,59,68,72,73,74,77])
        self.assertAlmostEqual(result['all_stored_labels']['mean_score'], .5003424875)
        self.assertAlmostEqual(result['text_present_only']['mean_score'], .48248054166666665)

    def test_tfidf_rare_term_and_empty_document(self):
        scores = tfidf([['common','rare','rare'], ['common'], []])
        self.assertAlmostEqual(scores[0]['rare'], 2/3*(math.log(4/2)+1))
        self.assertGreater(scores[0]['rare'], scores[0]['common'])
        self.assertEqual(scores[2], {})

    def test_historical_term_filter_preserves_domain_words(self):
        terms = {r['term'] for r in filter_terms(ROOT/'data/historical_token_counts.csv')}
        self.assertIn('mr', terms)
        self.assertIn('價格', terms)
        self.assertNotIn('的', terms)


if __name__ == '__main__':
    unittest.main()

