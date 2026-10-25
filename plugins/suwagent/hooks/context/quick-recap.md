This user wants every response that finishes a unit of work to end with one status line, so they can tell at a glance whether anything waits on them. The line is the very last line of the response, under 100 characters, with nothing after it:
- 🟢 <what is done> when the requested work is finished.
- 🟡 <what is pending> when a specific non-routine step remains; the line names that step.
- 🔴 <what is needed> only when the work is blocked on the user's input.
The status is judged from the user's side: "tests not run" or "needs a deploy" is 🟡, not 🟢.
