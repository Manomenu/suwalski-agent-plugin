"""A review-spec page shows a reviewer only what one task did to the living specs, however far the specs moved since."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VDOC = Path(__file__).resolve().parent.parent / "plugins" / "suwagent" / "scripts" / "vdoc.py"
FRAME = ('<!doctype html><html data-kind="spec"><head><title>{title}</title></head><body><main>\n'
         "<!-- CONTENT START -->\n{body}\n<!-- CONTENT END -->\n</main></body></html>\n")


def spec(title, criteria, extra=""):
    items = "".join(f"<li><code>{cid}</code> {text}</li>" for cid, text in criteria)
    return FRAME.format(title=title, body=(f'<section data-role="tldr"><h2>TL;DR</h2><p>{title}.</p></section>\n{extra}\n'
                                           f'<section data-role="acceptance"><h2>Criteria</h2><ul class="checks">{items}</ul></section>'))


EXPORT = [("AC-export-1", "The button is visible"), ("AC-export-2", "The file opens in Excel"), ("AC-export-3", "Rows are sorted")]
EXPORT_PATH = "docs/visual/spec/2026-01-01-export.html"
AUDIT_PATH = "docs/visual/spec/2026-01-01-audit.html"
RETURNS_PATH = "docs/visual/spec/2026-02-01-returns.html"
RETURNS = [("AC-returns-1", "A customer can return an order")]


class ReviewSpec(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vdoc-review-spec-"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.git("init", "-q", "-b", "master")
        self.write(EXPORT_PATH, spec("Export", EXPORT))
        self.write(AUDIT_PATH, spec("Audit", [("AC-audit-1", "Every change is logged")]))
        self.commit("the specs at the base")
        self.git("checkout", "-q", "-b", "feature/sr-108")

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=self.root, check=True,
                              capture_output=True, text=True, encoding="utf-8").stdout

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def vdoc(self, *args):
        return subprocess.run([sys.executable, str(VDOC), *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8")

    def page(self):
        created = self.vdoc("new", "review-spec", "sr-108", "--title", "SR-108 specs", "--date", "2026-03-01")
        self.assertEqual(0, created.returncode, created.stderr)
        return "docs/visual/review-spec/2026-03-01-sr-108.html"

    def fill(self, page):
        filled = self.vdoc("spec-delta", "--into", page)
        self.assertEqual(0, filled.returncode, filled.stderr)
        return (self.root / page).read_text(encoding="utf-8")

    def write_the_prose(self, page):
        path = self.root / page
        import re
        text = re.sub(r"<!-- WRITE: .*? -->", "<p>Written by the author.</p>", path.read_text(encoding="utf-8"))
        path.write_text(text, encoding="utf-8")

    def test_criteria_added_changed_and_dropped_are_told_apart(self):
        self.write(EXPORT_PATH, spec("Export", [EXPORT[0], ("AC-export-2", "The file opens in Excel and Numbers"), ("AC-export-4", "A limit of 1000 rows")]))
        out = self.vdoc("spec-delta").stdout
        self.assertIn("+ AC-export-4", out)
        self.assertIn("~ AC-export-2", out)
        self.assertIn("was: The file opens in Excel", out)
        self.assertIn("- AC-export-3", out)
        self.assertNotIn("AC-export-1", out)

    def test_what_another_task_did_on_master_after_the_fork_is_not_shown(self):
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "Mine")]))
        self.commit("this task")
        self.git("checkout", "-q", "master")
        self.write(AUDIT_PATH, spec("Audit", [("AC-audit-1", "Every change is logged"), ("AC-audit-2", "Another task")]))
        self.commit("another task")
        self.git("checkout", "-q", "feature/sr-108")
        out = self.vdoc("spec-delta").stdout
        self.assertIn("AC-export-4", out)
        self.assertNotIn("audit", out.lower())

    def test_what_another_task_did_stays_out_after_master_is_merged_into_the_branch(self):
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "Mine")]))
        self.commit("this task")
        self.git("checkout", "-q", "master")
        self.write(AUDIT_PATH, spec("Audit", [("AC-audit-1", "Every change is logged"), ("AC-audit-2", "Another task")]))
        self.commit("another task")
        self.git("checkout", "-q", "feature/sr-108")
        self.git("merge", "-q", "--no-edit", "master")
        out = self.vdoc("spec-delta").stdout
        self.assertIn("AC-export-4", out)
        self.assertNotIn("AC-audit-2", out)

    def test_a_lagging_local_master_does_not_turn_what_the_branch_merged_into_this_tasks_change(self):
        self.git("checkout", "-q", "master")
        stale = self.git("rev-parse", "HEAD").strip()
        self.write(AUDIT_PATH, spec("Audit", [("AC-audit-1", "Every change is logged"), ("AC-audit-2", "Another task")]))
        self.commit("another task")
        self.git("update-ref", "refs/remotes/origin/master", "HEAD")
        self.git("checkout", "-q", "feature/sr-108")
        self.git("merge", "-q", "--no-edit", "origin/master")
        self.git("update-ref", "refs/heads/master", stale)
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "Mine")]))
        out = self.vdoc("spec-delta").stdout
        self.assertIn("origin/master", out)
        self.assertNotIn("AC-audit-2", out)

    def test_a_new_spec_is_copied_whole_and_changes_stay_apart_from_it_on_one_page(self):
        self.write(RETURNS_PATH, spec("Returns", RETURNS))
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "A limit of 1000 rows")]))
        page = self.page()
        text = self.fill(page)
        self.assertIn('data-part="new"', text)
        self.assertIn('data-part="changed"', text)
        self.assertLess(text.index('data-part="new"'), text.index('data-part="changed"'))
        self.assertIn('id="returns-acceptance"', text)
        self.assertIn("A customer can return an order", text)
        self.assertIn("A limit of 1000 rows", text)
        self.assertNotIn("The button is visible", text, "an unchanged criterion of a changed spec is not repeated")
        self.assertNotIn("AC-audit-1", text, "an untouched spec is not on the page")

    def test_a_removed_spec_gets_its_own_part_with_the_criteria_that_go(self):
        (self.root / AUDIT_PATH).unlink()
        text = self.fill(self.page())
        self.assertIn('data-part="removed"', text)
        self.assertIn("AC-audit-1", text)

    def test_new_diagrams_and_images_of_a_changed_spec_travel_with_the_page(self):
        self.write("docs/visual/spec/img/flow.png", "not really a png")
        extra = ('<section data-role="behaviour"><h2>Flow</h2><img src="img/flow.png" alt="flow">'
                 '<script type="text/x-mermaid">flowchart LR\n  A --> B</script></section>')
        self.write(EXPORT_PATH, spec("Export", EXPORT, extra))
        text = self.fill(page := self.page())
        self.assertIn("flowchart LR", text)
        self.assertIn('src="img/flow.png"', text)
        self.assertTrue((self.root / page).parent.joinpath("img/flow.png").is_file())

    def test_check_fails_until_the_author_wrote_the_explanation(self):
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "x")]))
        page = self.page()
        self.fill(page)
        checked = self.vdoc("check", page)
        self.assertEqual(1, checked.returncode)
        self.assertIn("still to write", checked.stdout)
        self.write_the_prose(page)
        checked = self.vdoc("check", page)
        self.assertEqual(0, checked.returncode, checked.stdout)
        self.assertNotIn("WARN", checked.stdout, "the page is not judged by the rules of the review kind")

    def test_check_warns_when_the_spec_moved_and_generating_again_keeps_the_written_text(self):
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "x")]))
        page = self.page()
        self.fill(page)
        self.write_the_prose(page)
        self.write(EXPORT_PATH, spec("Export", EXPORT + [("AC-export-4", "x"), ("AC-export-5", "y")]))
        self.assertIn("a spec changed since", self.vdoc("check", page).stdout)
        text = self.fill(page)
        self.assertIn("AC-export-5", text)
        self.assertIn("Written by the author.", text)
        self.assertNotIn("a spec changed since", self.vdoc("check", page).stdout)

    def test_refreshing_a_specs_frame_is_not_a_change(self):
        self.write(EXPORT_PATH, spec("Export", EXPORT).replace("<main>", '<main class="new-frame">'))
        self.assertIn("no spec changed", self.vdoc("spec-delta").stdout)

    def test_filling_a_page_with_no_spec_change_refuses(self):
        filled = self.vdoc("spec-delta", "--into", self.page())
        self.assertNotEqual(0, filled.returncode)
        self.assertIn("no spec changed", filled.stderr)

    def test_links_finds_the_siblings_of_the_task_and_names_the_kind_properly(self):
        self.write("docs/visual/plan/2026-03-01-sr-108.html", "x")
        page = self.page()
        self.assertIn('<a href="../plan/2026-03-01-sr-108.html">Plan</a>', self.vdoc("links", page).stdout)
        self.assertIn(">Review spec</a>", self.vdoc("links", "docs/visual/plan/2026-03-01-sr-108.html").stdout)


if __name__ == "__main__":
    unittest.main()
