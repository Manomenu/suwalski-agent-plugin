---
name: visual-qa
description: Write a visual test guide for a tester on finished work, as an HTML page with no technical detail. It says where to test (environment, version, accounts, test data), what changed and where to look, and a set of scenarios as user actions, each with the expected result shown as a screenshot or sketch of the correctly working system. It ends with a results sheet the tester fills in (pass / fail / blocked) and sends back. Use when finished work goes to a tester, QA or the client for acceptance testing.
when_to_use: Finished work goes to testing, or the user says "visual qa", "qa", "dla testera", "instrukcja testów", "co testować", "scenariusze testowe", "testy akceptacyjne", "przekaż do testów".
argument-hint: "[environment, e.g. staging https://test.example.com] [who tests and how, e.g. manual UI, mobile, API]"
---

# Visual QA

A QA page is a test guide for someone who uses the system the way a user does: they click,
type and look, and they don't read code. It answers three questions: **where do I test,
what do I do, and what should I see when it works.** The tester should be able to start
without asking the developer anything, and to tell a bug from expected behaviour by
comparing the screen with the page.

Before writing, read these two files. They hold the rules shared by the visual skills and
the HTML blocks:

- `${CLAUDE_PLUGIN_ROOT}/shared/authoring.md`: where the file goes, the steps
  (`vdoc.py new` → write → `check` → publish + `register`), the review loop, and the quality bar
- `${CLAUDE_PLUGIN_ROOT}/shared/components.md`: the block catalog, especially "Screenshot
  with numbered marks", "Wireframe", "Steps" and "Open questions"

Publishing mode: **${user_config.publish_mode}**. It is `artifact` (publish as a claude.ai
artifact and record it in `claude-artifacts.md`) or `local`; see "Publishing mode" in
authoring.md. If a placeholder shows here instead of a value, use `artifact`.

Where and how to test: $ARGUMENTS

## Where and how: settle it first

There is no single way to test, so the page is written for **this** environment and
**this** tester. Before writing, have:

- **the environment**: its name and address (staging, test, a preview URL, a build or an
  app version), and how the tester checks that the new version is the one deployed there
  (a version number, a release date, a visible change);
- **access**: the accounts or roles to use, named, never with passwords or tokens. Say
  where the credentials are (the team's password manager, the person to ask);
- **the kind of testing**: manual UI on desktop (the default), mobile or particular
  browsers, an API through a tool such as Postman, or the client's acceptance test.

Take these from the arguments, the conversation, and the project (deploy configs, CI, the
README). **If the environment is still unknown, ask the user once**, in one question that
offers what was found in the project, and wait: a guide for the wrong environment is
worse than none. Everything else (scope, scenarios, language) decide yourself and say so
in the page. Write in the language the user writes in, unless they name the tester's
language.

## Find what to test

- **The baseline**: the spec of this work in `docs/visual/spec/` (its acceptance criteria and
  scenarios become test scenarios), then the recap and the deviation page if they exist
  (what was really built, and what consciously differs from the spec). Create the page
  with the **same slug**.
- **The change itself**, chosen as in visual-recap: with no other hint, everything changed on
  the current branch since it left the base branch. Read it to learn what a user can now
  do differently, not to describe code.
- **The running system.** Open the environment (or a local run of the same version) and walk
  every scenario yourself before writing it down: the button labels, messages and screens
  in the page must be the real ones. A scenario you couldn't walk is marked as written
  from the code, in a `callout assumption`.

## Write for a tester

- **Steps are user actions** with the exact words on the screen: "Click **Eksportuj CSV**
  above the table", never "call the export endpoint". No file paths, class names, endpoints,
  SQL or logs, unless the kind of testing is API testing; then name requests the way the
  tester's tool shows them.
- **Every scenario has an expected result** that can be checked by looking: what appears,
  what changes, what message is shown, what is in the downloaded file. "Works correctly" is
  not an expected result.
- **Show the correct state.** For each scenario that ends on a screen, a screenshot of that
  screen with numbered marks on what to check, shot with `vdoc.py shot` or this session's
  browser tool. Use test data only, never real customer data, especially in `artifact` mode.
  When the system can't be run from here, draw the expected screen as a wireframe grounded
  in the real components and labels, and mark it as reconstructed.
- **Say what is not a bug.** Known deviations from the spec, parts not deployed yet, and
  areas out of scope go in their own section, so the tester doesn't report them.

## Sections, in order

Aim for a page that takes 5 minutes to read; the testing itself can take longer.

1. **Header**, `doc-kind` "QA", status `draft` until the user approves it for the tester,
   then `approved`. In the meta line: the environment, the version or branch, and the date.
2. `tldr`: what changed for the user in 2-3 sentences, then `stats`: scenarios, roughly
   how long testing takes, accounts needed.
3. `environment`: **Where to test**: the address, how to check the version, the accounts or
   roles (where the credentials are), the test data to prepare and how, the browsers or
   devices, and anything to switch on (a feature flag, a setting).
4. `changes`: **What's new**: a before/after screenshot or wireframe with numbered marks
   showing where in the system the change is, so the tester knows where to look. One short
   paragraph per change, in user words.
5. `scenarios`: **What to test**, the main path first, then its variations, then the edge
   and error cases that matter for this change (wrong or empty input, no permission, cancel,
   going back, refreshing in the middle, a large amount of data). Leave out generic cases
   that this change doesn't touch. Each scenario is an `<h3>` with a number and a name
   ("S1. Eksport przefiltrowanej listy"), the preconditions in one line, the steps as a
   `steps` list, and **Expected:** with the screenshot or sketch of the correct result.
6. `known`: **Not a bug**: known deviations, not yet deployed, out of scope, each in one
   line. Leave it out when there is nothing.
7. `results`: **Results**: one `questions` form with a fieldset per scenario (`data-id` =
   the scenario number, the legend = its name) and three radio options: Pass, Fail,
   Blocked (couldn't test). The page adds a free-text box to each; say above the form that
   for a fail the tester writes what happened instead of the expected result, and that
   **Copy feedback for the agent** (or a comment on the artifact) sends the results back.

## Hand-off

Follow the hand-off step in authoring.md. In `artifact` mode, remind the user in one line
that the artifact is private until they share it with the tester. In `local` mode, the
`.html` file is what they send.

## When the results come back

Results arrive as a block that starts with `Feedback on qa` / `Feedback do qa`, as
comments on the artifact, or in plain chat. For every fail, reproduce it on the environment
or locally before changing code; a fail that is expected behaviour is answered by
improving the scenario's expected result instead. Fixed issues go back to implementation,
then the page is updated (the build to test, the scenarios to repeat) and published again
to the same artifact.
