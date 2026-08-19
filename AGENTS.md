# AGENTS.md — google-adk-ager

Translator. Compiles AGER → **Google ADK**.

- `/ager-to-google-adk`
- `python3 scripts/emit.py --bundle path/to/ager --out ./generated`
- `--lang python|typescript|go|java|kotlin|all`
- `--mode agent|graph|all`  (agent = LlmAgent non-graph; graph = Workflow / templates)
- `--adk-version 1|2`

Hosts: Agent Plugins 1.0, Claude Code, Grok Build, Codex, Cursor.
