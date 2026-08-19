# Cursor — binding this plugin

Cursor is a first-class host. This is **not** a second copy of the skills.
Same `skills/`, same `scripts/emit.py`, same compile rules.

## How Cursor loads this pack

| Layer | What we ship | Where |
|-------|----------------|-------|
| Agent Skills | Existing `SKILL.md` files | `skills/` |
| Agent Plugins 1.0 | Root `plugin.json` | repo root |
| Cursor Plugins | Rules + skill pointer | `.cursor-plugin/plugin.json` |
| MCP | Not in this pack | deferred |

Cursor also reads `.claude/skills/` and `.codex/skills/` for compatibility.

## Install (local Cursor)

```text
/plugin marketplace add SpillwaveSolutions/google-adk-ager
/plugin install google-adk-ager
```

Or open this repo and load it as a local plugin.

Root `plugin.json` already declares the Agent Plugins 1.0 schema, so Cursor
loads skills without a rewrite.

## Cloud Cursor

A Grok Bot / Cursor cloud session usually opens the **workspace**, not this
plugin cache. The cloud agent sees `AGENTS.md` and `scripts/emit.py` if they
are present. Prefer the script:

```bash
python3 scripts/emit.py --bundle <AGER> --out ./generated
```

Do not freehand the emitted tree. Do not invent agents that are not in the graph.

## Rules

`.cursor/rules/ager-translator.mdc` is always-on when this repo is the Cursor
workspace.

## Related

- [HOSTS.md](HOSTS.md)
- https://cursor.com/docs/plugins
- https://agent-plugins.org
