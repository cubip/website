#!/usr/bin/env python3
"""Exercise failures that the website's merge check must reject."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys


sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("check_site", Path(__file__).with_name("check-site.py"))
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class SiteValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.html = ('<!DOCTYPE html><html lang="en"><head><title>cubip</title>'
                     '<meta name="viewport" content="width=device-width"></head>'
                     '<body><h1 id="intro">cubip</h1>{}</body></html>')
        for entry in CHECK.PUBLIC_PATHS:
            path = self.root / entry
            if entry in ("images", "privacy", "terms", "support"):
                path.mkdir()
                if entry != "images":
                    (path / "index.html").write_text(self.html.format(""))
            else:
                path.write_text(":root { color: black; }" if entry == "style.css" else "cubip.com")
        self.page = self.root / "index.html"

    def failures(self, content):
        self.page.write_text(self.html.format(content))
        return CHECK.check_site(self.root)

    def test_valid_navigation_and_external_links(self):
        self.assertEqual(self.failures('<a href="/privacy/">Privacy</a><a href="#intro">Intro</a>'
                                       '<a href="https://example.invalid/">External</a>'), [])

    def test_missing_asset(self):
        self.assertTrue(self.failures('<img alt="Trip" src="/missing.webp">'))

    def test_missing_fragment(self):
        self.assertTrue(self.failures('<a href="/privacy/#missing">Privacy</a>'))

    def test_duplicate_identifier(self):
        self.assertTrue(self.failures('<p id="intro">Duplicate</p>'))

    def test_missing_image_description(self):
        self.assertTrue(self.failures('<img src="https://example.invalid/photo.webp">'))

    def test_private_file_reference(self):
        (self.root / "private.txt").write_text("not published")
        self.assertTrue(self.failures('<a href="/private.txt">Private</a>'))

    def test_symlink_cannot_publish_private_file(self):
        (self.root / "private.txt").write_text("not published")
        (self.root / "images" / "linked.txt").symlink_to(self.root / "private.txt")
        self.assertTrue(self.failures(""))

    def test_css_delimiters_ignore_quoted_text(self):
        self.assertEqual(CHECK.css_errors('a { content: "}"; /* } */ color: var(--ink); }'), [])
        self.assertTrue(CHECK.css_errors("a { color: black;"))
        self.assertTrue(CHECK.css_errors("a { color: black; /* unfinished"))


if __name__ == "__main__":
    unittest.main()
