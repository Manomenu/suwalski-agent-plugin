This user reviews agent work through visual HTML pages instead of long chat text, using five skills: /suwagent:visual-spec (what and why), /suwagent:visual-plan (how), /suwagent:visual-recap (what was built and how it works), /suwagent:visual-deviation (only where the implementation departs from the spec, and why) and /suwagent:visual-qa (a test guide for a tester: where to test, what to do, what a working system shows). The pages are saved under docs/visual/<spec|plan|recap|deviation|qa>/ and, by default, also published as claude.ai artifacts, whose links are recorded in docs/visual/<kind>/claude-artifacts.md.

The user's working agreement for larger changes (a new feature, several files, a change of behaviour, an API or data shape, or a choice between approaches):
- Before planning, offer in one line to write a visual spec, unless the requirements are already pinned down or an approved spec exists.
- Before writing code, offer a visual plan, and start implementing only after the user approves it.
- After the work is finished and verified, offer a visual recap. When a spec exists and the user wants only the differences rather than the whole story, or a record to keep in the repository next to the spec, offer /suwagent:visual-deviation instead: a short page with each departure from the spec, its reason and a keep / fix / decide recommendation.
- When finished work goes to a tester, QA or the client's acceptance testing, offer /suwagent:visual-qa: a test guide without technical detail, written for the environment the user names (the agent asks for it if it isn't known).
- When the user declines one of these for a task, don't offer it again for that task.

What goes into git, the user's recommendation for every repository: plans, recaps and QA pages are gitignored (docs/visual/plan/, docs/visual/recap/ and docs/visual/qa/ in .gitignore), because they are working pages of one task; specs and deviation pages are committed, together, because they stay true after the work is merged (the contract, and where the build consciously departs from it). When the agent writes a plan, recap or QA page in a repository whose .gitignore doesn't cover them yet (check with `git check-ignore`), it recommends adding those lines in one line, and adds them only when the user agrees; after a no, it doesn't ask again in that repository.

When the user asks for a better, nicer or more visual README, recommend /suwagent:visual-readme in one line; start it only when the user asks for it. It redraws the README as light/dark pictures from a board page in docs/visual/board/.

Small or obvious changes (a typo, a one-line fix, a single well-specified function, a question) need none of these; the user expects them to be done directly.

The plugin also has ways of working for larger tasks. The user wants the agent to recommend the one that fits, in one line with a reason, when a larger task starts or its plan is approved. The agent starts autopilot, orchestrate, mr-chain, visual-readme and update only when the user explicitly asks for one of them (by its name, as in "użyj efficient-frontier", or in plain words); then it invokes the skill itself instead of asking the user to type the command. Otherwise it only names the command:
- /suwagent:autopilot when the user will leave the agent alone with the task ("idę spać", "zrób to beze mnie", "nie pytaj"), or the task is long and its decisions are routine. It works without questions, logs its decisions and ends with a visual recap.
- /suwagent:orchestrate (alias /suwagent:efficient-frontier) when the task is mostly volume: wide reading of the codebase, many files with mechanical edits, long test runs or logs. The main model decides while cheaper subagents do the volume.
- /suwagent:mr-chain when the feature is too large for one reviewable MR and should be delivered as stacked MRs, each built on the previous one. It splits the work, names the branches (e.g. SR-108-01-…) and keeps every change on the earliest branch that has its code. When the work is already on such a chain, the agent follows its rules without being asked.
- Both can apply: autopilot for autonomy, orchestrate for cost.
- plan-judge applies by itself when two or more plans exist for the same task. The agent uses it instead of choosing silently.
- limit-guard runs inside autopilot and orchestrate; it needs no recommendation.
- For an ordinary interactive task, the agent recommends nothing and just works.
The same rule applies as for the documents: after a no, the agent doesn't recommend a mode again for that task.
