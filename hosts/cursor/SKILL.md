---
name: cursor-google-adk-ager
description: Bind a Cursor agent to google-adk-ager. Compile AGER graphs. Do not author graphs.
---

# Cursor / google-adk-ager

Follow `docs/CURSOR.md` and `docs/HOSTS.md`.

1. Identity: `cursor/google-adk-ager`.
2. Local Cursor may `/plugin install google-adk-ager`.
3. Compile with `python3 scripts/emit.py --bundle <AGER> --out <OUT>`.
4. Never invent agents. Never write a new AGER graph (that is `okf-agent-graph`).
