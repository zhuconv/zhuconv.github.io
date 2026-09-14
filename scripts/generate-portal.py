#!/usr/bin/env python3
"""Generate the portal directory from the HTML files in a built site."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit


class PageMetadata(HTMLParser):
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.portal_title = ""
        self.redirect = ""
        self.in_title = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag != "meta":
            return
        content = attrs.get("content") or ""
        if (attrs.get("name") or "").lower() == "portal-title":
            self.portal_title = content
        if (attrs.get("http-equiv") or "").lower() == "refresh":
            match = re.match(r"\s*\d+(?:\.\d+)?\s*;\s*url\s*=\s*(.+?)\s*$", content, re.I)
            if match:
                self.redirect = match[1].strip("\"'")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return " ".join((self.portal_title or "".join(self.title_parts)).split())


@dataclass(frozen=True)
class Entry:
    path: str
    title: str
    destination: str = ""


def discover(site: Path, site_url: str) -> list[Entry]:
    entries = []
    for file in sorted(site.rglob("*")):
        relative = file.relative_to(site)
        if not file.is_file() or file.suffix.lower() not in {".html", ".htm"}:
            continue
        if relative.as_posix() == "portal/index.html":
            continue
        metadata = PageMetadata(file.read_text(encoding="utf-8"))
        route = "/" + quote(relative.as_posix(), safe="/")
        if file.name == "index.html":
            route = route.removesuffix("index.html")
        destination = ""
        if metadata.redirect:
            destination = urljoin(site_url.rstrip("/") + route, metadata.redirect)
            parsed = urlsplit(destination)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise ValueError(f"Unsupported redirect destination in {relative}")
        short_path = route.rstrip("/") or "/"
        entries.append(Entry(short_path, metadata.title or short_path, destination))
    return sorted(entries, key=lambda entry: entry.path)


def render_redirect(entry: Entry) -> str:
    path, title, destination = map(escape, (entry.path, entry.title, entry.destination))
    target = urlsplit(entry.destination)
    label = escape(target.netloc + target.path)
    return f'''          <li class="portal-link-row">
            <div class="portal-link-details">
              <a class="portal-path" href="{path}" target="_blank" rel="noopener noreferrer" aria-label="Open {path} in a new tab">{path} <span aria-hidden="true">↗</span></a>
              <h3>{title}</h3>
              <a class="portal-destination" href="{destination}" target="_blank" rel="noopener noreferrer" aria-label="Destination for {path} (opens in a new tab)">
                <span aria-hidden="true">↳</span> {label}
              </a>
            </div>
            <button class="portal-copy" type="button" data-copy-path="{path}" aria-label="Copy {path} link" hidden>
              <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M15 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h3"/></svg>
              <span>Copy link</span>
            </button>
          </li>'''


def render_page(entry: Entry) -> str:
    path, title = escape(entry.path), escape(entry.title)
    return f'''          <li>
            <a class="portal-home" href="{path}">
              <span><strong>{title}</strong><span class="portal-footer-path">{path}</span></span>
              <span aria-hidden="true">↗</span>
            </a>
          </li>'''


def generate(site: Path, site_url: str = "https://zhuconv.github.io") -> list[Entry]:
    portal = site / "portal/index.html"
    template = portal.read_text(encoding="utf-8")
    entries = discover(site, site_url)
    sections = {
        "redirects": [render_redirect(entry) for entry in entries if entry.destination],
        "pages": [render_page(entry) for entry in entries if not entry.destination],
    }
    for name, rows in sections.items():
        start = f"<!-- portal:{name}:start -->"
        end = f"<!-- portal:{name}:end -->"
        if template.count(start) != 1 or template.count(end) != 1:
            raise ValueError(f"Expected exactly one {name} directory placeholder")
        content = "\n".join(rows) or f'          <li class="portal-empty">No {name} yet.</li>'
        template, count = re.subn(
            re.escape(start) + r".*?" + re.escape(end),
            lambda _: f"{start}\n{content}\n          {end}",
            template,
            flags=re.S,
        )
        if count != 1:
            raise ValueError(f"Invalid {name} directory placeholder order")
    portal.write_text(template, encoding="utf-8")
    return entries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path("_site"), help="Built site directory")
    args = parser.parse_args()
    entries = generate(args.site)
    redirects = sum(bool(entry.destination) for entry in entries)
    print(f"Portal generated: {redirects} redirects, {len(entries) - redirects} pages")


if __name__ == "__main__":
    main()
