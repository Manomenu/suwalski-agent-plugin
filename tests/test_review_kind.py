"""vdoc.py knows the review kind: `new review` creates the page in docs/visual/review/ and `check` accepts it."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VDOC = Path(__file__).resolve().parent.parent / "plugins" / "suwagent" / "scripts" / "vdoc.py"


def vdoc(*args, cwd):
    return subprocess.run([sys.executable, str(VDOC), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8")


class ReviewKind(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vdoc-review-"))
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def test_new_review_page_lands_next_to_its_siblings_and_checks(self):
        created = vdoc("new", "review", "export-csv", "--title", "Export CSV review", "--date", "2026-10-25", cwd=self.root)
        self.assertEqual(0, created.returncode, created.stderr)
        page = self.root / "docs" / "visual" / "review" / "2026-10-25-export-csv.html"
        self.assertTrue(page.exists(), created.stdout)
        text = page.read_text(encoding="utf-8")
        self.assertIn('data-kind="review"', text)
        body = ('<section data-role="tldr"><h2>TL;DR</h2><p>🟢 0 blockers.</p></section>\n'
                '<section data-role="findings"><h2>Findings</h2><p>None.</p></section>')
        page.write_text(text.replace("<!-- CONTENT START -->\n\n<!-- CONTENT END -->",
                                     f"<!-- CONTENT START -->\n{body}\n<!-- CONTENT END -->"), encoding="utf-8")
        checked = vdoc("check", str(page), cwd=self.root)
        self.assertEqual(0, checked.returncode, checked.stdout + checked.stderr)
        self.assertNotIn("WARN", checked.stdout)

    def test_new_refuses_an_unknown_kind_and_names_review_among_the_known_ones(self):
        created = vdoc("new", "notes", "export-csv", "--title", "Notes", cwd=self.root)
        self.assertNotEqual(0, created.returncode)
        self.assertIn("review", created.stderr)

if __name__ == "__main__":
    unittest.main()
