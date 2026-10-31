"""vdoc.py criteria on a sample repository: each criterion of a spec is traced to the guardrails that name its id."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

VDOC = Path(__file__).resolve().parent.parent / "plugins" / "suwagent" / "scripts" / "vdoc.py"
SPEC = "docs/visual/spec/notes.html"
CONFIG = {
    "specs": "docs/visual/spec",
    "prose": ["docs/**", "**/*.md"],
    "kinds": [
        {"kind": "integration test", "paths": ["tests/integration/**/*.py"], "how": "the id in the test name"},
        {"kind": "unit test", "paths": ["tests/*.py", "src/**/*.test.ts"], "how": "the id in the test name"},
        {"kind": "lint", "paths": [".eslintrc.json", "lint/*.toml"], "how": "a comment above the rule"},
    ],
}


class Criteria(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="vdoc-criteria-"))
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)
        self.write("criteria.json", json.dumps(CONFIG))

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def spec(self, items, prose="", path=SPEC):
        self.write(path, f'<section data-role="goals"><p>{prose}</p></section>\n<section data-role="acceptance">\n'
                         f'<h2>Criteria</h2>\n<ul class="checks">\n{items}\n</ul>\n</section>')

    def run_criteria(self, *args):
        result = subprocess.run([sys.executable, str(VDOC), "criteria", "--root", str(self.root), *args],
                                capture_output=True, text=True, encoding="utf-8")
        return result.returncode, result.stdout, result.stderr

    def test_a_guardrail_is_traced_with_its_kind_and_line(self):
        self.spec("<li><code>AC-notes-1</code> a note is saved</li>")
        self.write("tests/integration/notes/test_save.py", "x = 1\ndef test_AC_notes_1(): pass  # AC-notes-1\n")
        self.write("tests/test_notes.py", "# AC-notes-1\n")

        code, out, err = self.run_criteria()

        self.assertEqual(0, code, err)
        self.assertEqual(["AC-notes-1       integration test             tests/integration/notes/test_save.py:2",
                          "AC-notes-1       unit test                    tests/test_notes.py:1"], out.splitlines())

    def test_the_first_matching_kind_wins_and_a_glob_stays_in_its_folder(self):
        self.spec("<li>AC-notes-1</li><li>AC-notes-2</li>")
        self.write("lint/rules.toml", "# AC-notes-1\n")
        self.write("lint/deeper/rules.toml", "# AC-notes-2\n")

        code, out, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn("AC-notes-1       lint", out)
        self.assertIn("AC-notes-2 at lint/deeper/rules.toml:1: not a guardrail", err)

    def test_a_criterion_without_a_guardrail_fails_and_says_to_ask_the_owner(self):
        self.spec("<li>AC-notes-1</li>\n<li>AC-notes-2</li>")
        self.write("tests/test_notes.py", "# AC-notes-1\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn("AC-notes-2: no guardrail", err)
        self.assertIn("ask the owner", err)
        self.assertNotIn("AC-notes-1", err)

    def test_a_guardrail_naming_an_id_no_spec_defines_fails(self):
        self.spec("<li>AC-notes-1</li>")
        self.write("tests/test_notes.py", "# AC-notes-1 AC-notes-10\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn("AC-notes-10 at tests/test_notes.py:1: no spec defines this criterion", err)

    def test_an_id_where_nothing_checks_it_is_not_a_guardrail(self):
        self.spec("<li>AC-notes-1</li>")
        self.write("tests/test_notes.py", "# AC-notes-1\n")
        self.write("src/notes/store.ts", "// AC-notes-1\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn("AC-notes-1 at src/notes/store.ts:1: not a guardrail", err)

    def test_prose_and_files_ignored_by_git_are_not_read(self):
        self.spec("<li>AC-notes-1</li>")
        self.write("tests/test_notes.py", "# AC-notes-1\n")
        self.write("README.md", "AC-notes-7")
        self.write("docs/architecture.html", "AC-notes-8")
        self.write(".gitignore", "dist/\n")
        self.write("dist/bundle.js", "AC-notes-9")

        code, _, err = self.run_criteria()

        self.assertEqual(0, code, err)

    def test_a_spec_without_criteria_fails(self):
        for content, expected in (("<p>no section</p>", "no acceptance section"),
                                  ('<section data-role="acceptance"><h2>C</h2></section>', "the acceptance section has no criteria")):
            with self.subTest(expected=expected):
                self.write(SPEC, content)
                code, _, err = self.run_criteria()
                self.assertEqual(1, code)
                self.assertIn(f"{SPEC}: {expected}", err)

    def test_a_criterion_without_an_id_fails_and_quotes_it(self):
        self.spec('<li>AC-notes-1 saved</li>\n<li data-status="pass">a note is <b>pretty</b></li>')
        self.write("tests/test_notes.py", "# AC-notes-1\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn(f'{SPEC}: a criterion without an id: "a note is pretty"', err)

    def test_a_criterion_with_several_ids_fails_once(self):
        self.spec("<li>AC-notes-1 and AC-notes-2 together</li>")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn("one criterion has several ids (AC-notes-1 AC-notes-2)", err)
        self.assertNotIn("mentions", err)

    def test_an_id_defined_in_two_specs_fails_and_names_both(self):
        self.spec("<li>AC-notes-1 saved</li>")
        self.spec("<li>AC-notes-1 sorted</li>", path="docs/visual/spec/notes-list.html")
        self.write("tests/test_notes.py", "# AC-notes-1\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn(f"AC-notes-1 is defined twice (docs/visual/spec/notes-list.html,{SPEC})", err)

    def test_a_spec_may_mention_a_defined_criterion_but_not_an_undefined_one(self):
        self.spec("<li>AC-notes-1 saved</li>", prose="see AC-notes-1 and AC-notes-9")
        self.write("tests/test_notes.py", "# AC-notes-1\n")

        code, _, err = self.run_criteria()

        self.assertEqual(1, code)
        self.assertIn(f"{SPEC}:1: mentions AC-notes-9, which no acceptance section defines", err)
        self.assertNotIn("mentions AC-notes-1", err)

    def test_one_criterion_shows_only_its_guardrails_and_problems(self):
        self.spec("<li>AC-notes-1</li><li>AC-notes-2</li><li>AC-notes-3</li>")
        self.write("tests/test_notes.py", "# AC-notes-1\n# AC-notes-2\n")

        code, out, err = self.run_criteria("AC-notes-2")

        self.assertEqual(0, code, err)
        self.assertEqual(["AC-notes-2       unit test                    tests/test_notes.py:2"], out.splitlines())


if __name__ == "__main__":
    unittest.main()
