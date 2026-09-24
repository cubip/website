#!/usr/bin/env python3
"""Check the static site's structure and local references without network calls."""

from html.parser import HTMLParser
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PATHS = ("index.html", "style.css", "images", "fonts", "imprint", "privacy", "terms", "support", "CNAME", "robots.txt")
VOID_TAGS = set("area base br col embed hr img input link meta param source track wbr".split())


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.errors = []
        self.ids = set()
        self.references = []
        self.stack = []
        self.tags = []
        self.doctype = False
        self.language = False
        self.viewport = False
        self.title = ""

    def handle_decl(self, decl):
        self.doctype = decl.lower() == "doctype html"

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append(tag)
        if tag == "html":
            self.language = bool(attributes.get("lang"))
        if tag == "meta" and attributes.get("name") == "viewport":
            self.viewport = bool(attributes.get("content"))
        if tag == "img" and "alt" not in attributes:
            self.errors.append("image is missing alt text")
        identifier = attributes.get("id")
        if identifier:
            if identifier in self.ids:
                self.errors.append("duplicate element ID")
            self.ids.add(identifier)
        for attribute in ("href", "src", "poster"):
            if attributes.get(attribute):
                self.references.append(attributes[attribute])
        if tag == "meta" and attributes.get("property") == "og:image":
            self.references.append(attributes.get("content", ""))
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append("mismatched closing element")
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1] == "title":
            self.title += data

    def finish(self):
        if not self.doctype or not self.language or not self.viewport:
            self.errors.append("HTML doctype, language and viewport are required")
        if not self.title.strip() or self.tags.count("h1") != 1:
            self.errors.append("a title and exactly one h1 are required")
        if any(self.tags.count(tag) != 1 for tag in ("html", "head", "body")) or self.stack:
            self.errors.append("document structure is incomplete")


def css_errors(source):
    """Catch broken delimiters/comments/strings; this is not a complete CSS parser."""
    tokens = re.compile(r'/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[{}()\[\]]|/\*|["\']', re.S)
    stack = []
    for match in tokens.finditer(source):
        token = match.group()
        if token in ("/*", '"', "'"):
            return ["unterminated CSS comment or string"]
        if len(token) != 1:
            continue
        if token in "{([":
            stack.append(token)
        elif not stack or stack.pop() != {"}": "{", ")": "(", "]": "["}[token]:
            return ["mismatched CSS delimiter"]
    return ["unclosed CSS delimiter"] if stack else []


def check_site(root):
    root = root.resolve()
    errors = []
    public_files = set()
    for entry in PUBLIC_PATHS:
        path = root / entry
        if not path.exists():
            errors.append(f"{entry}: required public path is missing")
            continue
        for item in [path, *path.rglob("*")] if path.is_dir() else [path]:
            if item.is_symlink():
                errors.append(f"{entry}: symbolic links are not allowed in published assets")
            elif item.is_file():
                public_files.add(item)

    if errors:
        return errors  # Never read through a link in a public directory.

    pages = {}
    references = []
    for path in sorted(public_files):
        if path.suffix == ".html":
            page = Page(path)
            page.feed(path.read_text(encoding="utf-8"))
            page.close()
            page.finish()
            pages[path] = page
            errors.extend(f"{path.relative_to(root)}: {error}" for error in page.errors)
            references.extend((path, value) for value in page.references)
        elif path.suffix == ".css":
            source = path.read_text(encoding="utf-8")
            errors.extend(f"{path.relative_to(root)}: {error}" for error in css_errors(source))
            references.extend((path, match.group(1).strip(" \t\r\n\"'"))
                              for match in re.finditer(r"url\(([^)]*)\)", source))

    for source, reference in references:
        parsed = urlsplit(reference)
        if parsed.scheme in ("mailto", "tel", "data"):
            continue
        if parsed.scheme and parsed.scheme not in ("http", "https"):
            errors.append(f"{source.relative_to(root)}: unsupported URL scheme")
            continue
        if parsed.netloc and parsed.hostname != "cubip.com":
            continue  # Third-party availability must not decide whether a PR passes.
        relative = unquote(parsed.path)
        target = root / relative.lstrip("/") if relative.startswith("/") else source.parent / relative
        if not relative:
            target = source
        if target.is_dir():
            target /= "index.html"
        target = target.resolve()
        if not target.is_relative_to(root) or target not in public_files:
            errors.append(f"{source.relative_to(root)}: local reference does not resolve to a published file")
        elif parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
            errors.append(f"{source.relative_to(root)}: local fragment does not exist")
    return errors


if __name__ == "__main__":
    failures = check_site(ROOT)
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        sys.exit(1)
    print("Static pages, image descriptions, local references and CSS delimiters passed.")
