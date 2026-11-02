"""Every skill has a valid frontmatter whose name matches its folder, and the session context names every page kind."""
import re
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent / "plugins" / "suwagent"
SKILLS = PLUGIN / "skills"
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def frontmatter(path):
    m = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    assert m, f"{path} has no frontmatter"
    fields = {}
    for line in m.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


class Skills(unittest.TestCase):
    def test_every_skill_names_itself_after_its_folder_and_says_when_to_use_it(self):
        for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
            with self.subTest(skill=folder.name):
                fields = frontmatter(folder / "SKILL.md")
                self.assertEqual(folder.name, fields.get("name"))
                self.assertGreater(len(fields.get("description", "")), 80)

    def test_the_method_skills_exist(self):
        for name in ("task-triage", "review-triage", "agent-review", "visual-guardrails", "visual-spec"):
            self.assertTrue((SKILLS / name / "SKILL.md").exists(), name)

    def test_session_context_names_every_page_kind_and_the_method_skills(self):
        text = (PLUGIN / "hooks" / "context" / "visual-workflow.md").read_text(encoding="utf-8")
        self.assertIn("docs/visual/<spec|plan|recap|deviation|qa|guardrails|review>/", text)
        for kind in ("plan", "recap", "deviation", "qa", "guardrails", "review"):
            self.assertIn(f"docs/visual/{kind}/", text)
        for skill in ("task-triage", "review-triage", "agent-review", "visual-guardrails"):
            self.assertIn(f"/suwagent:{skill}", text)
        for phrase in ("living spec per feature", "one-way", "characterization tests", "always-careful"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
