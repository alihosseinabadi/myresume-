"""Minimal HTML → text extraction using the stdlib parser (no BeautifulSoup)."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser

from ai.keywords import normalize

BLOCK_TAGS = {"p", "li", "br", "div", "section", "article", "h1", "h2", "h3", "h4", "tr"}
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "iframe", "template"}


class HtmlProbe(HTMLParser):
    """Collects visible text, meta tags, <title> and JSON-LD blocks in one pass."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self.meta: dict[str, str] = {}
        self.links: list[str] = []
        self.json_ld: list[str] = []
        self.title = ""
        self._skip = 0
        self._in_title = False
        self._in_json = False
        self._json_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        if tag in SKIP_TAGS:
            self._skip += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            name = (attr.get("property") or attr.get("name") or "").lower()
            if name and attr.get("content"):
                self.meta.setdefault(name, attr["content"])
        if tag == "script" and "ld+json" in (attr.get("type") or "").lower():
            self._in_json, self._json_buf = True, []
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP_TAGS and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_json:
            self._in_json = False
            raw = "".join(self._json_buf).strip()
            if raw:
                self.json_ld.append(raw)
        if tag in BLOCK_TAGS:
            self.chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_json:
            self._json_buf.append(data)
            return
        if self._in_title:
            self.title += data
        if self._skip:
            return
        text = " ".join(data.split())
        if text:
            self.chunks.append(text + " ")

    @property
    def text(self) -> str:
        return re.sub(r"\n{2,}", "\n", "".join(self.chunks)).strip()


def strip_html(raw: str) -> str:
    probe = HtmlProbe()
    try:
        probe.feed(raw)
        return probe.text
    except Exception:  # noqa: BLE001 - malformed HTML must not break the import
        return normalize(re.sub(r"<[^>]+>", " ", raw))


def json_ld_jobs(blocks: list[str]) -> list[dict]:
    """Walk nested JSON-LD graphs and return every schema.org/JobPosting node."""
    found: list[dict] = []

    def walk(node) -> None:
        if isinstance(node, dict):
            types = node.get("@type")
            type_list = types if isinstance(types, list) else [types]
            if any(isinstance(t, str) and t.lower() == "jobposting" for t in type_list):
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    for block in blocks:
        try:
            walk(json.loads(block))
        except json.JSONDecodeError:
            continue
    return found


def first_string(value) -> str:
    """Pull a human string out of the many shapes schema.org uses.

    Job locations are usually nested (``jobLocation.address.addressLocality``), so
    known keys are tried in priority order and then nested containers are walked.
    """
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list) and value:
        return first_string(value[0])
    if isinstance(value, dict):
        preferred = (
            "name", "value", "addressLocality", "@value", "addressRegion",
            "address", "addressCountry", "postalCode",
        )
        for key in preferred:
            if key in value:
                hit = first_string(value[key])
                if hit:
                    return hit
        for nested in value.values():
            if isinstance(nested, (dict, list)):
                hit = first_string(nested)
                if hit:
                    return hit
    return ""
