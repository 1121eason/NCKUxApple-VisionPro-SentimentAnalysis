"""Check data invariants, local document links and the public file manifest."""
import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from visionpro.audit import audit, read_scores

parser=argparse.ArgumentParser()
parser.add_argument('--write-manifest',action='store_true')
args=parser.parse_args()
scores=read_scores(ROOT/'data/historical_scores.csv')
assert audit(scores)==json.loads((ROOT/'results/historical_audit.json').read_text())
provenance=json.loads((ROOT/'data/provenance.json').read_text())
for key,name in [('scores_sha256','historical_scores.csv'),('token_counts_sha256','historical_token_counts.csv')]:
    assert hashlib.sha256((ROOT/'data'/name).read_bytes()).hexdigest()==provenance['snapshot_inputs'][key]
with (ROOT/'data/sources.csv').open(newline='') as f:
    source_ids={r['source_id'] for r in csv.DictReader(f)}
assert {r['source_id'] for r in scores}<=source_ids
assert sum(r['has_text'] for r in scores)==72
assert len({r['text_sha256'] for r in scores if r['has_text']})==72
links=0
for md in ROOT.rglob('*.md'):
    if '.git' in md.parts:
        continue
    for target in re.findall(r'\]\(([^)]+)\)',md.read_text()):
        if target.startswith(('http:','https:','#','mailto:')):
            continue
        file=unquote(target.split('#')[0])
        assert (md.parent/file).exists(), f'Missing link {md}: {target}'
        links+=1

def public_files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(part in {'.git','__pycache__','output','local','.venv'} for part in p.relative_to(ROOT).parts) and p.name not in {'SHA256SUMS','.DS_Store'} and p.suffix!='.pyc')

paths=public_files()
for p in paths:
    if p.suffix.lower() in {'.md','.csv','.json','.py','.svg','.yml','.txt','.html'}:
        content=p.read_text()
        assert not re.search(r'docs\.google\.com/(?:spreadsheets|document)/d/',content), f'Private cloud link in {p}'
        assert not re.search(r'\bR\d{8}\b',content), f'Private student identifier in {p}'
manifest=''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n' for p in paths)
if args.write_manifest:
    (ROOT/'SHA256SUMS').write_text(manifest)
else:
    assert (ROOT/'SHA256SUMS').read_text()==manifest, 'Manifest differs; review changes before regenerating.'
print(f'PASS: {len(scores)} label rows, 72 unique text digests, {len(source_ids)} sources, {links} local links, {len(paths)} file hashes')

