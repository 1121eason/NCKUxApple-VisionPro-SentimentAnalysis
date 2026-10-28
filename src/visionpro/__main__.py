import argparse
import csv
import json
from pathlib import Path
from .audit import audit, read_scores
from .scrape import extract, fetch_page
from .text_mining import filter_terms, rank_documents


def main():
    parser = argparse.ArgumentParser(description='Vision Pro historical audit and explicitly labelled reconstruction tools')
    commands = parser.add_subparsers(dest='command', required=True)
    a = commands.add_parser('audit')
    a.add_argument('--input', type=Path, default=Path('data/historical_scores.csv'))
    a.add_argument('--output', type=Path, required=True)
    s = commands.add_parser('scrape')
    source = s.add_mutually_exclusive_group(required=True)
    source.add_argument('--input', type=Path)
    source.add_argument('--url')
    s.add_argument('--source-url', default='https://example.org/synthetic-fixture')
    s.add_argument('--allow-host', action='append', default=[])
    s.add_argument('--kind', choices=['ptt', 'news'], required=True)
    s.add_argument('--output', type=Path, required=True)
    t = commands.add_parser('terms')
    t.add_argument('--input', type=Path, default=Path('data/historical_token_counts.csv'))
    t.add_argument('--output', type=Path, required=True)
    m = commands.add_parser('tfidf')
    m.add_argument('--input', type=Path, required=True)
    m.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'audit':
        result = audit(read_scores(args.input))
    elif args.command == 'scrape':
        html = args.input.read_text(encoding='utf-8') if args.input else fetch_page(args.url, set(args.allow_host))
        result = extract(html, args.kind, args.source_url if args.input else args.url)
    elif args.command == 'terms':
        result = filter_terms(args.input)
    else:
        result = rank_documents(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()

