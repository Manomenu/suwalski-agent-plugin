This user reviews agent work through visual HTML pages instead of long chat text, using three skills: /suwagent:visual-spec (what and why), /suwagent:visual-plan (how) and /suwagent:visual-recap (what was built and how it works). The pages are saved under docs/visual/<spec|plan|recap>/ and, by default, also published as claude.ai artifacts, whose links are recorded in docs/visual/<kind>/claude-artifacts.md.

The user's working agreement for larger changes (a new feature, several files, a change of behaviour, an API or data shape, or a choice between approaches):
- Before planning, offer in one line to write a visual spec, unless the requirements are already pinned down or an approved spec exists.
- Before writing code, offer a visual plan, and start implementing only after the user approves it.
- After the work is finished and verified, offer a visual recap.
- When the user declines one of these for a task, don't offer it again for that task.

When the user asks for a better, nicer or more visual README, recommend /suwagent:visual-readme in one line; only the user can start it. It redraws the README as light/dark pictures from a board page in docs/visual/board/.

Small or obvious changes (a typo, a one-line fix, a single well-specified function, a question) need none of these; the user expects them to be done directly.

The plugin also has ways of working for larger tasks. The user wants the agent to recommend the one that fits, in one line with a reason, when a larger task starts or its plan is approved. Only the user can start autopilot and orchestrate, so for those the agent names the command and the user runs it:
- /suwagent:autopilot when the user will leave the agent alone with the task ("idę spać", "zrób to beze mnie", "nie pytaj"), or the task is long and its decisions are routine. It works without questions, logs its decisions and ends with a visual recap.
- /suwagent:orchestrate (alias /suwagent:efficient-frontier) when the task is mostly volume: wide reading of the codebase, many files with mechanical edits, long test runs or logs. The main model decides while cheaper subagents do the volume.
- Both can apply: autopilot for autonomy, orchestrate for cost.
- plan-judge applies by itself when two or more plans exist for the same task. The agent uses it instead of choosing silently.
- limit-guard runs inside autopilot and orchestrate; it needs no recommendation.
- For an ordinary interactive task, the agent recommends nothing and just works.
The same rule applies as for the documents: after a no, the agent doesn't recommend a mode again for that task.
