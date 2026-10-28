"""Recompute stored historical predictions; this does not call or train Azure."""
import csv
import math
from collections import Counter
from statistics import mean

LABELS = ('positive', 'neutral', 'negative')


def read_scores(path):
    with open(path, encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    seen = set()
    for row in rows:
        if row['record_id'] in seen:
            raise ValueError('Duplicate record_id')
        seen.add(row['record_id'])
        row['score'] = float(row['score'])
        row['has_text'] = int(row['has_text'])
        if row['sentiment'] not in LABELS or row['has_text'] not in (0, 1) or not math.isfinite(row['score']) or not 0 <= row['score'] <= 1:
            raise ValueError('Invalid historical prediction')
        if bool(row['text_sha256']) != bool(row['has_text']):
            raise ValueError('Text presence and digest disagree')
    return rows


def summarize(rows):
    counts = Counter(row['sentiment'] for row in rows)
    return {'n': len(rows), 'counts': {key: counts[key] for key in LABELS},
            'percent': {key: round(100 * counts[key] / len(rows), 6) if rows else 0 for key in LABELS},
            'mean_score': mean(row['score'] for row in rows) if rows else None,
            'mean_score_by_label': {key: mean(row['score'] for row in rows if row['sentiment'] == key) if counts[key] else None for key in LABELS}}


def audit(rows):
    valid = [row for row in rows if row['has_text']]
    empty = [row for row in rows if not row['has_text']]
    return {'all_stored_labels': summarize(rows), 'text_present_only': summarize(valid),
            'excluded_empty_text': {'n': len(empty), 'record_ids': [r['record_id'] for r in empty], 'sheet_rows': [int(r['sheet_row']) for r in empty], 'scores': sorted(set(r['score'] for r in empty))},
            'by_source_text_present': {key: summarize([r for r in valid if r['source_id'] == key]) for key in sorted(set(r['source_id'] for r in rows))},
            'scope': 'Recomputation of stored 2023 labels. Not a new model run, accuracy estimate, or representative market survey.'}

