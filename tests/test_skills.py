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
        hot = (PLUGIN / "hooks" / "context" / "visual-workflow.md").read_text(encoding="utf-8")
        self.assertIn("docs/visual/<spec|plan|recap|deviation|qa|guardrails|review>/", hot)
        for kind in ("plan", "recap", "deviation", "qa", "guardrails", "review"):
            self.assertIn(f"docs/visual/{kind}/", hot)
        for skill in ("task-triage", "review-triage", "agent-review", "visual-guardrails"):
            self.assertIn(f"/suwagent:{skill}", hot)
        method = (PLUGIN / "hooks" / "context" / "method.md").read_text(encoding="utf-8")
        for phrase in ("living spec per feature", "one-way", "characterization tests", "always-careful", "docs/adr/"):
            self.assertIn(phrase, method)

    def test_the_hook_names_the_method_file_by_its_absolute_path(self):
        import subprocess
        out = subprocess.run(["sh", str(PLUGIN / "scripts" / "session-context.sh")], capture_output=True, text=True,
                             encoding="utf-8", env={"PATH": "/usr/bin:/bin"}, check=True).stdout
        self.assertIn(str(PLUGIN / "hooks" / "context" / "method.md"), out)



class SessionContext(unittest.TestCase):
    def test_the_session_start_output_stays_under_the_hook_output_cap(self):
        """Claude Code passes a hook's stdout to the agent only up to 10,000 characters; above that it saves a file
        and the agent sees a 2,000-character preview, so the method would drop out of every session."""
        import subprocess
        out = subprocess.run(["sh", str(PLUGIN / "scripts" / "session-context.sh")], capture_output=True, text=True,
                             encoding="utf-8", env={"PATH": "/usr/bin:/bin"}, check=True).stdout
        self.assertLess(len(out), 9500, f"session context is {len(out)} characters; shorten hooks/context/*.md")


if __name__ == "__main__":
    unittest.main()
