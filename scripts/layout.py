"""Write Agent Plugins 1.0 + Claude + Grok + Codex + Cursor overlays.

A host gets a manifest, never a fork.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
MARKET_SCHEMA = "https://anthropic.com/claude-code/marketplace.schema.json"


def write(out: Path, rel: str, content: str) -> Path:
    dest = out / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    text = content if content.endswith("\n") else content + "\n"
    dest.write_text(text, encoding="utf-8")
    return dest


def write_json(out: Path, rel: str, data: Any) -> Path:
    return write(out, rel, json.dumps(data, indent=2))


def host_manifests(
    out: Path,
    *,
    name: str,
    title: str,
    description: str,
    version: str = "0.1.0",
    ager_version: str = "0.3.0",
    homepage: str = "",
    keywords: list[str] | None = None,
    default_prompts: list[str] | None = None,
    brand: str = "#4F46E5",
) -> list[Path]:
    """Emit every host overlay for one plugin identity."""
    written: list[Path] = []
    kws = keywords or ["ager", "okf", "translator", "claude-code", "grok-build", "codex", "cursor"]
    home = homepage or f"https://github.com/SpillwaveSolutions/{name}"
    ident = {
        "$schema": SCHEMA,
        "name": name,
        "version": version,
        "description": description,
        "author": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
        "homepage": home,
        "repository": home,
        "license": "MIT",
        "keywords": kws,
        "extensions": {
            "com.spillwave.ager": {
                "ager_version": ager_version,
                "kind": "translator",
                "title": title,
            }
        },
    }
    claude = {k: ident[k] for k in ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")}
    written.append(write_json(out, "plugin.json", ident))
    written.append(write_json(out, ".claude-plugin/plugin.json", claude))
    written.append(
        write_json(
            out,
            "marketplace.json",
            {
                "$schema": MARKET_SCHEMA,
                "name": f"{name}-marketplace",
                "owner": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
                "plugins": [{"name": name, "source": "./", "description": description, "version": version}],
            },
        )
    )
    written.append(
        write_json(
            out,
            ".claude-plugin/marketplace.json",
            {
                "$schema": MARKET_SCHEMA,
                "name": f"{name}-marketplace",
                "owner": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
                "plugins": [
                    {
                        "name": name,
                        "source": "./",
                        "description": description,
                        "version": version,
                        "category": "productivity",
                    }
                ],
            },
        )
    )
    written.append(
        write_json(
            out,
            ".grok-plugin/marketplace.json",
            {
                "name": f"{name}-marketplace",
                "description": f"{description} Grok Build loads the Claude layout with zero config.",
                "version": version,
                "plugins": [
                    {
                        "name": name,
                        "source": ".",
                        "description": description,
                        "version": version,
                        "compatibility": {"claude_plugin": True, "zero_config": True},
                        "depends_on": [
                            {
                                "plugin": "okf-agent-graph",
                                "repository": "https://github.com/SpillwaveSolutions/okf-agent-graph",
                            }
                        ],
                        "repository": home,
                    }
                ],
            },
        )
    )
    written.append(
        write_json(
            out,
            ".codex-plugin/plugin.json",
            {
                "name": name,
                "version": version,
                "description": description,
                "author": {"name": "Rick Hightower", "url": "https://github.com/RichardHightower"},
                "homepage": home,
                "repository": home,
                "license": "MIT",
                "keywords": kws,
                "skills": "./skills/",
                "interface": {
                    "displayName": title,
                    "shortDescription": description,
                    "longDescription": description,
                    "developerName": "Spillwave Solutions",
                    "category": "Developer Tools",
                    "capabilities": ["Read", "Write"],
                    "websiteURL": home,
                    "defaultPrompt": default_prompts
                    or [
                        f"Compile this AGER graph with {name}.",
                        "Prefer scripts/emit.py. Do not invent agents.",
                    ],
                    "brandColor": brand,
                },
            },
        )
    )
    written.append(
        write_json(
            out,
            ".cursor-plugin/plugin.json",
            {
                "name": name,
                "version": version,
                "description": description,
                "author": {"name": "Rick Hightower"},
                "homepage": home,
                "repository": home,
                "license": "MIT",
                "keywords": kws if "cursor" in kws else kws + ["cursor"],
                "skills": "skills/",
                "rules": ".cursor/rules/",
                "commands": "commands/",
            },
        )
    )
    written.append(
        write(
            out,
            "hosts/cursor/SKILL.md",
            f"""---
name: cursor-{name}
description: Bind Cursor (Agent Plugins 1.0) to {name}.
---

# Cursor / {name}

Cursor loads root `plugin.json` + `skills/` (Agent Plugins 1.0). No Cursor-only fork.

1. Identity: `cursor/{name}`
2. Run `python3 scripts/emit.py --bundle <AGER> --out <OUT>`
3. Never document a private remote.
""",
        )
    )
    written.append(
        write(
            out,
            ".cursor/rules/ager-run.mdc",
            f"""---
description: Compiled AGER graph {name} — Cursor always-on rules
alwaysApply: true
---

This checkout is a compiled AGER graph (`{name}`).

1. Follow `skills/ager-run/SKILL.md`. Do not invent agents.
2. LoopPolicy: goal, deadline, price, max_turns, no_progress.
3. Same skills serve Claude Code, Grok Build, Codex, Cursor, and Agent Plugins 1.0.
""",
        )
    )
    written.append(
        write(
            out,
            "hosts/grok-bot/SKILL.md",
            f"""---
name: grok-bot-{name}
description: Bind Grok Bot / Grok Build to {name}.
---

# Grok Bot / {name}

1. Identity: `grok-bot/{name}`
2. Grok Build loads Claude plugin layout with zero config.
3. Prefer `scripts/emit.py`.
""",
        )
    )
    written.append(
        write(
            out,
            "docs/HOSTS.md",
            f"""# Hosts — {name}

| Host | Manifest |
| --- | --- |
| Agent Plugins 1.0 (Cursor, Copilot, VS Code, Kiro) | `plugin.json` + `skills/` |
| Claude Code | `.claude-plugin/` |
| Grok Build | Claude layout + `.grok-plugin/` |
| Codex | `.codex-plugin/` |
| Cursor | `.cursor-plugin/plugin.json` + `.cursor/rules/` + `hosts/cursor/SKILL.md` |
""",
        )
    )
    return written
