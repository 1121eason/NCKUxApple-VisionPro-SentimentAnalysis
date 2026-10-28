"""Explicit single-page collection and offline HTML extraction. Standard library only."""
import hashlib
import re
import unicodedata
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.robotparser import RobotFileParser

USER_AGENT = 'VisionProResearch/1.0'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def clean_text(text):
    """Keep negation and amounts; exclude IP addresses from research exports."""
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])', '[IP removed]', text)
    return re.sub(r'\s+', ' ', text).strip().lstrip(':：').strip()


class Extractor(HTMLParser):
    """Extract PTT push-content spans, or paragraph text inside article elements."""
    def __init__(self, kind):
        super().__init__(convert_charrefs=True)
        if kind not in {'ptt', 'news'}:
            raise ValueError('kind must be ptt or news')
        self.kind, self.stack, self.items = kind, [], []
        self.active_depth, self.fragments = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.active_depth is None:
            selected = (self.kind == 'ptt' and tag == 'span' and 'push-content' in attrs.get('class', '').split()) or (self.kind == 'news' and tag == 'p' and 'article' in self.stack)
            if selected:
                self.active_depth, self.fragments = len(self.stack), []
        if tag == 'br' and self.active_depth is not None:
            self.fragments.append(' ')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in self.stack:
            return
        index = len(self.stack) - 1 - self.stack[::-1].index(tag)
        if self.active_depth is not None and index <= self.active_depth:
            text = clean_text(''.join(self.fragments))
            if text:
                self.items.append(text)
            self.active_depth, self.fragments = None, []
        del self.stack[index:]

    def handle_data(self, data):
        if self.active_depth is not None and not any(t in self.stack for t in ('script', 'style')):
            self.fragments.append(data)


def extract(html, kind, source_url):
    parser = Extractor(kind)
    parser.feed(html)
    parser.close()
    records, seen = [], set()
    for text in parser.items:
        identity = hashlib.sha256((source_url + '\n' + text).encode()).hexdigest()
        if identity in seen:
            continue
        seen.add(identity)
        records.append({'record_id': identity[:16], 'source_url': source_url, 'text': text})
    if not records:
        raise ValueError('No selected text: inspect the HTML layout; no generic fallback was used.')
    return records


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch_page(url, allowed_hosts):
    """One explicit HTTPS URL; no cookies, pagination, gate bypass, or redirects."""
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in allowed_hosts or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('URL must be HTTPS on an explicitly allowed host, without credentials or a custom port.')
    opener = build_opener(NoRedirect())

    def read(target, limit, require_html=False):
        with opener.open(Request(target, headers={'User-Agent': USER_AGENT}), timeout=15) as response:
            if require_html and response.headers.get_content_type() not in {'text/html', 'application/xhtml+xml'}:
                raise ValueError('The target did not return HTML.')
            raw = response.read(limit + 1)
            if len(raw) > limit:
                raise ValueError('Response exceeded the size limit.')
            return raw.decode(response.headers.get_content_charset() or 'utf-8')

    robots_url = f'https://{parsed.netloc}/robots.txt'
    try:
        robots = read(robots_url, 131072)
    except (OSError, HTTPError) as error:
        raise ValueError('Cannot verify robots.txt; collection stopped.') from error
    policy = RobotFileParser()
    policy.parse(robots.splitlines())
    if not policy.can_fetch(USER_AGENT, url):
        raise ValueError('robots.txt disallows this request.')
    return read(url, 2_000_000, require_html=True)

