# Vision Pro: From Online Opinions to Product Positioning

[繁體中文](README.md) · [Case-study PDF](docs/vision-pro-case-study.pdf) · [Methods](docs/methodology.md) · [Reproduce](docs/reproduce.md)

![Research overview](assets/overview.svg)

**Eason / 李奕成 · National Cheng Kung University · Information Management · Original study: 2023 · Portfolio reconstruction: 2026**

## Research question

When Apple announced Vision Pro in 2023, did enthusiasm for AR and MR translate into willingness to buy? This individual study combined selected technology-media, blog and PTT text with Azure sentiment outputs and Power BI word clouds to explore technology interest, price barriers and product positioning.

## What the evidence shows

The recovered workbook contains 80 stored sentiment labels: 42 positive, nine neutral and 29 negative. Eight of the positive records no longer contain text; all eight share the same score, 0.6611. Restricting the denominator to the 72 records with retained text changes the positive share from **52.50% to 47.22%**. Negative labels account for 40.28% of the latter subset.

This is a recomputation of historical predictions, not a new Azure run or a model-accuracy estimate. Missing text today does not prove that the original model input was empty. The retained labels also contain examples of apparent semantic errors involving negation. Positive sentiment is not equivalent to purchase intention.

![Sentiment comparison](assets/sentiment-comparison.svg)

## Technical work you can inspect

| Capability | Evidence |
| --- | --- |
| Web extraction | [PTT and news HTML parser](src/visionpro/scrape.py), synthetic fixtures, explicit selectors, source URLs, content deduplication and IP removal |
| Data engineering | [Row-level score derivatives](data/historical_scores.csv), text-presence flags, digests, source reconciliation and exclusion of a summary cell |
| Sentiment analysis | [Audit code](src/visionpro/audit.py), [stored-label results](results/historical_audit.json), analysis of missing text and negation |
| Text mining | [POS filtering and TF-IDF](src/visionpro/text_mining.py); historical aggregate token counts and separately labelled synthetic document examples |
| Communication | Original Power BI word-cloud work, newly generated charts, a four-page research report and industry-oriented interpretation |

The historical report documents spreadsheet-based collection, cleaning, Azure sentiment analysis and Power BI word clouds. Original crawler code was not recovered. The Python tools in this repository were added in 2026 with AI assistance and are explicitly identified as a reconstruction.

## Run locally

Python 3.10+; no third-party packages are needed for the core pipeline.

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m visionpro audit --output output/audit.json
PYTHONPATH=src python3 -m visionpro terms --output output/terms.json
PYTHONPATH=src python3 -m visionpro scrape --input tests/fixtures/ptt_synthetic.html --kind ptt --output output/ptt.json
PYTHONPATH=src python3 -m visionpro tfidf --input tests/fixtures/segmented_synthetic.csv --output output/tfidf.json
```

The scraping and TF-IDF examples use synthetic inputs. Optional single-page HTTPS acquisition requires an explicit host allowlist and a successful robots.txt check; it was not executed against the historical sites in this publication.

## Practical interpretation

The study suggests examining price accessibility, application value and AR/MR positioning together. These are exploratory product-research directions. A convenience sample mixing editorial excerpts and forum messages cannot establish market demand, a willingness-to-pay threshold, or causal effects on sales.

Full source texts, the original 11-page report and teaching slides remain in a local private archive. Public materials contain source-attributed numeric and lexical derivatives, not usernames, IP addresses or private cloud-sharing links. See [provenance](docs/provenance.md), [contribution](docs/contribution.md) and [data documentation](data/README.md).

