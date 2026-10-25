#!/bin/sh
# SessionStart hook: prints the user's working agreement, which Claude Code adds to the context.
# The first part is always on; each other part has its own switch in /plugin → suwagent → Configure.
dir="$(dirname "$0")/../hooks/context"
part() { [ "$1" = "false" ] || { cat "$dir/$2"; echo; }; }
part true working-with-user.md
part "${CLAUDE_PLUGIN_OPTION_SUGGEST_VISUAL_DOCS:-true}" visual-workflow.md
part "${CLAUDE_PLUGIN_OPTION_QUICK_RECAP:-true}" quick-recap.md
part "${CLAUDE_PLUGIN_OPTION_MANDATORY_DOCS:-true}" mandatory-docs.md
