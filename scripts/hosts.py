"""Multi-host plugin manifests (Claude, Grok, Codex, Cursor, Agent Plugins 1.0)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ir import AgerGraph


VERSION = "0.1.0"
SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
AUTHOR = {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"}


def write(out: Path, rel: str, content: str) -> Path:
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not content.endswith("\n"):
        content += "\n"
    dest.write_text(content, encoding="utf-8")
    return dest


def dump(obj: Any) -> str:
    return json.dumps(obj, indent=2) + "\n"


def identity(name: str, description: str, homepage: str, keywords: list[str]) -> dict[str, Any]:
    return {
        "$schema": SCHEMA,
        "name": name,
        "version": VERSION,
        "description": description,
        "author": AUTHOR,
        "homepage": homepage,
        "repository": homepage,
        "license": "MIT",
        "keywords": keywords,
    }


def write_host_matrix(
    out: Path,
    *,
    name: str,
    description: str,
    homepage: str,
    keywords: list[str],
    command: str,
    brand: str = "#4F46E5",
    extra_prompts: list[str] | None = None,
) -> list[Path]:
    """Write the installable plugin's own multi-host manifests."""
    written: list[Path] = []
    ident = identity(name, description, homepage, keywords)
    claude = {k: v for k, v in ident.items() if k != "$schema"}
    written.append(write(out, "plugin.json", dump(ident)))
    written.append(write(out, ".claude-plugin/plugin.json", dump(claude)))
    market = {
        "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
        "name": f"{name}-marketplace",
        "description": description,
        "owner": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
        "plugins": [
            {
                "name": name,
                "source": "./",
                "description": description,
                "version": VERSION,
                "author": {"name": "Rick Hightower"},
                "homepage": homepage,
                "repository": homepage,
                "license": "MIT",
                "keywords": keywords,
                "category": "productivity",
            }
        ],
    }
    written.append(write(out, ".claude-plugin/marketplace.json", dump(market)))
    written.append(
        write(
            out,
            "marketplace.json",
            dump(
                {
                    "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
                    "name": f"{name}-marketplace",
                    "owner": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
                    "plugins": [{"name": name, "source": "./", "description": description, "version": VERSION}],
                }
            ),
        )
    )
    written.append(
        write(
            out,
            ".grok-plugin/marketplace.json",
            dump(
                {
                    "name": f"{name}-marketplace",
                    "description": f"{description} Grok Build loads the Claude layout with zero config.",
                    "version": VERSION,
                    "plugins": [
                        {
                            "name": name,
                            "source": ".",
                            "description": description,
                            "version": VERSION,
                            "compatibility": {"claude_plugin": True, "zero_config": True},
                            "depends_on": [
                                {
                                    "plugin": "okf-agent-graph",
                                    "repository": "https://github.com/SpillwaveSolutions/okf-agent-graph",
                                }
                            ],
                            "repository": homepage,
                        }
                    ],
                }
            ),
        )
    )
    written.append(
        write(
            out,
            ".codex-plugin/plugin.json",
            dump(
                {
                    "name": name,
                    "version": VERSION,
                    "description": description,
                    "author": AUTHOR,
                    "homepage": homepage,
                    "repository": homepage,
                    "license": "MIT",
                    "keywords": keywords,
                    "skills": "./skills/",
                    "interface": {
                        "displayName": name,
                        "shortDescription": description,
                        "longDescription": description,
                        "developerName": "Spillwave Solutions",
                        "category": "Developer Tools",
                        "capabilities": ["Read", "Write"],
                        "websiteURL": homepage,
                        "defaultPrompt": extra_prompts
                        or [
                            f"Run {command} on the AGER bundle in this workspace.",
                            "Compile the graph. Do not author a new AGER graph.",
                        ],
                        "brandColor": brand,
                    },
                }
            ),
        )
    )
    written.append(
        write(
            out,
            ".cursor-plugin/plugin.json",
            dump(
                {
                    "name": name,
                    "version": VERSION,
                    "description": description,
                    "author": {"name": "Rick Hightower"},
                    "homepage": homepage,
                    "repository": homepage,
                    "license": "MIT",
                    "keywords": keywords + (["cursor"] if "cursor" not in keywords else []),
                    "skills": "skills/",
                    "rules": ".cursor/rules/",
                    "commands": "commands/",
                }
            ),
        )
    )
    return written


def write_cursor_docs(out: Path, *, name: str, command: str) -> list[Path]:
    written: list[Path] = []
    written.append(
        write(
            out,
            "docs/CURSOR.md",
            f"""# Cursor — binding this plugin

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
/plugin marketplace add SpillwaveSolutions/{name}
/plugin install {name}
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
""",
        )
    )
    written.append(
        write(
            out,
            "docs/HOSTS.md",
            f"""# Host matrix

`{name}` is one plugin, five install surfaces. Skills live once under `skills/`.

| Host | Manifest | Install |
| --- | --- | --- |
| Agent Plugins 1.0 | `plugin.json` | any host that reads agent-plugins.org |
| Claude Code | `.claude-plugin/plugin.json` + `marketplace.json` | `claude plugin marketplace add SpillwaveSolutions/{name}` |
| Grok Build | `.grok-plugin/marketplace.json` (Claude layout is zero-config) | drop into workspace / Claude marketplace |
| Codex | `.codex-plugin/plugin.json` | `codex plugin marketplace add SpillwaveSolutions/{name}` |
| Cursor | `.cursor-plugin/plugin.json` + `.cursor/rules/` | `/plugin install {name}` |

Command on Claude/Grok: `{command}`
Command on Codex: `{command.replace('/', '$') if command.startswith('/') else '$' + command}`

Depends on `okf-agent-graph` for author/validate. This plugin only compiles.
""",
        )
    )
    written.append(
        write(
            out,
            "hosts/cursor/SKILL.md",
            f"""---
name: cursor-{name}
description: Bind a Cursor agent to {name}. Compile AGER graphs. Do not author graphs.
---

# Cursor / {name}

Follow `docs/CURSOR.md` and `docs/HOSTS.md`.

1. Identity: `cursor/{name}`.
2. Local Cursor may `/plugin install {name}`.
3. Compile with `python3 scripts/emit.py --bundle <AGER> --out <OUT>`.
4. Never invent agents. Never write a new AGER graph (that is `okf-agent-graph`).
""",
        )
    )
    written.append(
        write(
            out,
            ".cursor/rules/ager-translator.mdc",
            f"""---
description: AGER translator rules for Cursor agents
alwaysApply: true
---

You are compiling a validated AGER/OKF AgentGraph. You are not authoring one.

1. Prefer `python3 scripts/emit.py --bundle <AGER> --out <OUT>`. Do not freehand the tree.
2. Do not invent agents, tools, or edges that are not in the graph.
3. Honor LoopPolicy check order: goal, deadline, price, max_turns, no_progress.
4. If `okf-agent-graph` / `ager-validate` is available, validate first. If it fails, stop.
5. Never claim production-ready without tests. Hosts do not meter USD; document the budget and stop.
6. Same skills serve Claude Code, Grok Build, Codex, Cursor, and Agent Plugins 1.0.
""",
        )
    )
    return written


def write_compiled_hosts(out: Path, graph: AgerGraph) -> list[Path]:
    """Host matrix for a *compiled* graph (installable on every host)."""
    homepage = f"https://github.com/SpillwaveSolutions/{graph.id}"
    keywords = ["ager", "okf", "compiled", "claude-code", "grok-build", "codex", "cursor", "agent-plugins"]
    desc = f"Compiled AGER graph: {graph.title}"
    written = write_host_matrix(
        out,
        name=graph.id,
        description=desc,
        homepage=homepage,
        keywords=keywords,
        command="/ager-run",
        extra_prompts=[
            f"Run compiled AGER graph {graph.id} via /ager-run (or $ager-run on Codex).",
            f"Entry {graph.entry}. Do not invent extra agents.",
        ],
    )
    written.extend(write_cursor_docs(out, name=graph.id, command="/ager-run"))
    return written
