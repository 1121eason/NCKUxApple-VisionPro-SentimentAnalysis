"""Auditable POS filtering and TF-IDF on explicitly segmented documents."""
import csv
import math
from collections import Counter

DEFAULT_POS = {'Na', 'Nb', 'Nc', 'Nv', 'FW'}
STOPWORDS = {'人', '大家', '目前', '現在', '問題', '東西'}


def filter_terms(path):
    """Historical corpus-wide counts: document frequencies cannot be recovered."""
    counts = Counter()
    with open(path, encoding='utf-8', newline='') as stream:
        for row in csv.DictReader(stream):
            term = row['term'].casefold()
            if row['pos'] in DEFAULT_POS and term not in STOPWORDS and len(term) >= 2:
                counts[term] += int(row['count'])
    return [{'term': term, 'count': count} for term, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]


def tfidf(documents):
    """TF=count/token_count; IDF=ln((1+N)/(1+df))+1; no vector normalization."""
    counters = [Counter(d) for d in documents]
    df = Counter(term for counter in counters for term in counter)
    n = len(documents)
    return [{term: count / sum(counter.values()) * (math.log((1+n)/(1+df[term])) + 1) for term, count in counter.items()} for counter in counters]


def rank_documents(path):
    with open(path, encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    documents = [r['tokens'].split() for r in rows]
    scores = tfidf(documents)
    return [{'record_id': row['record_id'], 'top_terms': sorted(score.items(), key=lambda x: (-x[1], x[0]))[:5]} for row, score in zip(rows, scores)]

