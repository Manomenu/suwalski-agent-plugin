#!/bin/sh
# SessionStart hook: prints the working agreement, which Claude Code adds to the context.
# Silent when the user turned the suggestions off in /plugin configure.
[ "${CLAUDE_PLUGIN_OPTION_SUGGEST_VISUAL_DOCS:-true}" = "false" ] && exit 0
cat "$(dirname "$0")/../hooks/session-context.md"
