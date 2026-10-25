The suwagent plugin is installed. This user reviews agent work through visual HTML pages instead of long chat text, using three skills: /suwagent:visual-spec (what and why), /suwagent:visual-plan (how) and /suwagent:visual-recap (what was built and how it works). The pages are saved under docs/visual/<spec|plan|recap>/ and, by default, also published as claude.ai artifacts, whose links are recorded in docs/visual/<kind>/claude-artifacts.md.

The user's working agreement for larger changes (a new feature, several files, a change of behaviour, an API or data shape, or a choice between approaches):
- Before planning, offer in one line to write a visual spec, unless the requirements are already pinned down or an approved spec exists.
- Before writing code, offer a visual plan, and start implementing only after the user approves it.
- After the work is finished and verified, offer a visual recap.
- When the user declines one of these for a task, don't offer it again for that task.

Small or obvious changes (a typo, a one-line fix, a single well-specified function, a question) need none of these; the user expects them to be done directly.
