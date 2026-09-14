import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("generate_portal", ROOT / "scripts/generate-portal.py")
portal = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = portal
SPEC.loader.exec_module(portal)


class PortalDiscoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.site = Path(temporary.name)
        self.write("portal/index.html", (ROOT / "portal/index.html").read_text())
        self.write("index.html", "<title>Home</title>")

    def write(self, path, contents):
        file = self.site / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(contents, encoding="utf-8")
        return file

    def output(self):
        return (self.site / "portal/index.html").read_text()

    def test_adding_changing_and_deleting_redirect_needs_no_directory_edit(self):
        file = self.write("new/meeting/index.html", '''
            <title>New meeting</title>
            <meta http-equiv="refresh" content="0; url=https://example.org/first?pwd=a&amp;x=2">
        ''')
        entries = portal.generate(self.site)
        meeting = next(entry for entry in entries if entry.path == "/new/meeting")
        self.assertEqual(meeting.destination, "https://example.org/first?pwd=a&x=2")
        self.assertIn('data-copy-path="/new/meeting"', self.output())
        self.assertIn('href="https://example.org/first?pwd=a&amp;x=2"', self.output())

        file.write_text('<meta http-equiv="refresh" content="0; url=https://example.org/second">')
        portal.generate(self.site)
        self.assertIn("https://example.org/second", self.output())
        self.assertNotIn("https://example.org/first", self.output())
        once = self.output()
        portal.generate(self.site)
        self.assertEqual(self.output(), once)

        file.unlink()
        portal.generate(self.site)
        self.assertNotIn("/new/meeting", self.output())
        self.assertIn("No redirects yet.", self.output())

    def test_discovers_nested_pages_and_ignores_assets_and_portal_itself(self):
        self.write("notes/index.html", "<title>Notes</title>")
        self.write("notes/detail.html", '<title>Detail</title><link rel="canonical" href="https://example.org/article">')
        self.write("archive/old.htm", "<p>Untitled</p>")
        self.write("images/example.svg", "<svg></svg>")
        self.write("resume/example.pdf", "not a page")
        entries = portal.generate(self.site)
        self.assertEqual([entry.path for entry in entries], ["/", "/archive/old.htm", "/notes", "/notes/detail.html"])
        self.assertTrue(all(not entry.destination for entry in entries))
        self.assertIn('href="/notes/detail.html"', self.output())
        self.assertIn("<strong>Notes</strong>", self.output())

    def test_relative_redirect_and_metadata_are_encoded_for_html(self):
        self.write("team & notes/index.html", '''
            <title>Fallback title</title>
            <meta name="portal-title" content="A &quot;title&quot; &amp; &lt;script&gt;">
            <meta HTTP-EQUIV="Refresh" content="0; URL='../target.html?first=1&amp;second=2'">
        ''')
        entry = next(entry for entry in portal.generate(self.site) if entry.destination)
        self.assertEqual(entry.path, "/team%20%26%20notes")
        self.assertEqual(entry.destination, "https://zhuconv.github.io/target.html?first=1&second=2")
        self.assertEqual(entry.title, 'A "title" & <script>')
        self.assertIn("A &quot;title&quot; &amp; &lt;script&gt;", self.output())
        self.assertNotIn("Fallback title", self.output())

    def test_missing_template_marker_fails_without_writing_partial_output(self):
        damaged = self.output().replace("<!-- portal:pages:end -->", "")
        self.write("portal/index.html", damaged)
        with self.assertRaisesRegex(ValueError, "placeholder"):
            portal.generate(self.site)
        self.assertEqual(self.output(), damaged)

    def test_non_web_redirect_is_rejected(self):
        self.write("invalid.html", '<meta http-equiv="refresh" content="0; url=javascript:alert(1)">')
        with self.assertRaisesRegex(ValueError, "Unsupported redirect"):
            portal.generate(self.site)


if __name__ == "__main__":
    unittest.main()
