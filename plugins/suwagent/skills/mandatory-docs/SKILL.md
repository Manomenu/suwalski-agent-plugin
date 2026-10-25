---
name: mandatory-docs
description: Read the current official documentation before writing code or answering anything that depends on a third-party library, framework, CLI, cloud service, provider API or SDK (Claude and Claude Code included), on adding or upgrading a dependency, on auth, OAuth, payments, webhooks, migrations, deploys or limits, or on an error that hints at API drift (unknown option, missing export, deprecated, version mismatch). Use it so answers come from the docs of the installed version, not from memory.
when_to_use: The user asks for the latest, current, official or recommended way, or says "sprawdź w dokumentacji", "read the docs", "jak to się teraz robi"; or you are about to write "usually", "probably", "I think" or code from memory for an external API.
---

# Mandatory docs

Memory of an API is a guess about its past. Before relying on it, read what the docs of the
**installed version** say now, and build from that.

## When it applies

Read the docs before writing code or answering when:

- the work adds, upgrades, configures or imports a package, SDK, framework, plugin, CLI,
  model or cloud resource;
- the API moves fast (AI SDKs, the Claude / OpenAI / Google APIs, Claude Code itself,
  Next.js, React, Tailwind, Vite, ORMs, Stripe, GitHub, auth libraries, deploy platforms);
- the behaviour involves auth, OAuth scopes, secrets, webhooks, payments, personal data,
  retries, rate limits, quotas, caching, migrations or deploys;
- an error mentions a deprecation, an unknown option, a missing export, an invalid config,
  or a version mismatch;
- the choice is expensive to undo: a public format, a database schema, persistent IDs,
  event names, customer-visible behaviour;
- the user asks for the latest, current, official or recommended way.

It does **not** apply to plain language syntax, typos, formatting, or self-contained code
with no external contract. When the answer is already in the repository (a helper used
nearby, typed interfaces, tests, an ADR, a package README), reading that locally is enough.

## How

1. **Pin the surface**: the package and its **installed** version (from the lockfile or
   `package.json`, `pyproject.toml`, `go.mod` and so on), the target version if upgrading,
   and the exact feature, endpoint, command or config key.
2. **Find the authoritative source**, in this order:
   1. the repository's own docs, specs, schemas, generated types and tests (for project
      behaviour);
   2. the official docs, API reference, migration guide or changelog for that major version
      (use web search and web fetch when the URL isn't known). For Claude Code itself, use
      code.claude.com/docs;
   3. the library's source or type definitions when the docs are incomplete.

   Before adding a dependency, check its current version (`npm view <pkg> version`,
   `pip index versions <pkg>`, or the ecosystem's equivalent). Blog posts, Stack Overflow
   and snippets are only for debugging symptoms once the contract is known.
3. **Extract the few facts the task needs**: names, imports, defaults, limits, required
   permissions, breaking changes, and an example for this version.
4. **Build from those facts.** Where the docs disagree with existing code, look at the code
   path and say so; don't silently pick one.
5. **Verify with the smallest real check**: the type check, a test, a build, a dry run of the
   CLI, or one real call.
6. **Name the sources** in the answer (a URL or a file path) when they shaped the decision.

## When the docs can't be read

No network, a missing page, or a login wall: say so plainly before falling back on memory,
narrow what is uncertain, check the source or the types if they're available, and don't
present the result as confirmed-current.
