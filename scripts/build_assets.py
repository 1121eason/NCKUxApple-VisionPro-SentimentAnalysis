"""Build public SVG figures from committed aggregate outputs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
audit = json.loads((ROOT/'results/historical_audit.json').read_text())
assets = ROOT/'assets'
assets.mkdir(exist_ok=True)
overview = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560" role="img" aria-labelledby="title desc">
<title id="title">Vision Pro social-listening research</title><desc id="desc">A 2023 study with a 2026 reproducibility audit: 80 stored labels, 72 retained texts, eight missing-text positive records.</desc>
<rect width="1200" height="560" rx="24" fill="#101f32"/>
<circle cx="1110" cy="50" r="230" fill="#162d44"/>
<g font-family="Arial, sans-serif">
<text x="56" y="66" fill="#71dbc8" font-size="16" letter-spacing="3">NCKU / INFORMATION MANAGEMENT</text>
<text x="56" y="140" fill="#fff" font-size="55" font-weight="700">Vision Pro</text>
<text x="56" y="187" fill="#c5d6e4" font-size="27">From online opinions to product positioning</text>
<text x="56" y="233" fill="#99b2c8" font-size="18">Web extraction / Text mining / Sentiment analysis / Evidence review</text>
<rect x="56" y="278" width="340" height="148" rx="14" fill="#1c344a"/>
<rect x="430" y="278" width="340" height="148" rx="14" fill="#1c344a"/>
<rect x="804" y="278" width="340" height="148" rx="14" fill="#1c344a"/>
<text x="82" y="344" fill="#fff" font-size="48" font-weight="700">80</text>
<text x="82" y="390" fill="#c5d6e4" font-size="19">stored sentiment labels</text>
<text x="456" y="344" fill="#71dbc8" font-size="48" font-weight="700">72</text>
<text x="456" y="390" fill="#c5d6e4" font-size="19">records with retained text</text>
<text x="830" y="344" fill="#ffa999" font-size="48" font-weight="700">8</text>
<text x="830" y="390" fill="#c5d6e4" font-size="19">positive labels without text</text>
<text x="56" y="482" fill="#fff" font-size="20">Technical enthusiasm does not establish purchase intention.</text>
<text x="56" y="519" fill="#99b2c8" font-size="16">Original study: 2023 | Portfolio reconstruction: 2026 | Eason / Li Yi-Cheng</text>
</g></svg>'''
(assets/'overview.svg').write_text(overview+'\n')

colors = {'positive':'#167b67','neutral':'#91a5b8','negative':'#db765e'}
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="430" viewBox="0 0 1120 430" role="img" aria-labelledby="title desc">',
'<title id="title">Historical sentiment labels and missing-text sensitivity</title><desc id="desc">All 80 labels: 52.50 percent positive, 11.25 neutral, 36.25 negative. Text present subset of 72: 47.22 percent positive, 12.50 neutral, 40.28 negative.</desc>',
'<rect width="1120" height="430" rx="18" fill="#f2f6f8"/><g font-family="Arial, sans-serif">',
'<text x="38" y="48" fill="#132a40" font-size="25" font-weight="700">Missing text changes the denominator</text>',
'<text x="38" y="80" fill="#526a7e" font-size="16">Stored 2023 predictions, recomputed from the recovered workbook</text>']
for y,key,label in [(139,'all_stored_labels','All stored labels / n=80'),(250,'text_present_only','Text retained / n=72')]:
    parts.append(f'<text x="38" y="{y}" fill="#132a40" font-size="18">{label}</text>')
    x=38
    for sentiment in ('positive','neutral','negative'):
        percent=audit[key]['percent'][sentiment]
        width=1044*percent/100
        parts.append(f'<rect x="{x:.3f}" y="{y+15}" width="{width:.3f}" height="49" fill="{colors[sentiment]}"/>')
        parts.append(f'<text x="{x+width/2:.3f}" y="{y+46}" text-anchor="middle" fill="white" font-size="19" font-weight="700">{percent:.2f}%</text>')
        x+=width
for x,sentiment in [(38,'positive'),(230,'neutral'),(415,'negative')]:
    parts.append(f'<rect x="{x}" y="345" width="17" height="17" fill="{colors[sentiment]}"/><text x="{x+27}" y="359" fill="#132a40" font-size="17">{sentiment.title()}</text>')
parts.append('<text x="38" y="401" fill="#526a7e" font-size="16">Exclusion removes eight stored positive labels. It does not correct semantic classification errors.</text></g></svg>')
(assets/'sentiment-comparison.svg').write_text('\n'.join(parts)+'\n')
print('Built 2 SVG figures')

