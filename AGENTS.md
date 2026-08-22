# AGENTS.md — google-adk-ager

Translator. Compiles AGER → **Google ADK**.

- `/ager-to-google-adk`
- `python3 scripts/emit.py --bundle path/to/ager --out ./generated`
- `--lang python|typescript|go|java|kotlin|all`
- `--mode agent|graph|all`  (agent = LlmAgent non-graph; graph = Workflow / templates)
- `--adk-version 1|2`

Hosts: Agent Plugins 1.0, Claude Code, Grok Build, Codex, Cursor.

<!-- worklog:policy:start -->
## WikiTicket SDD (worklog)

This plugin tracks implementation with [WikiTicket SDD](https://github.com/SpillwaveSolutions/wiki_ticket_sdd).

- Install the `worklog` plugin from `SpillwaveSolutions/wiki_ticket_sdd` (Claude Code, Grok Build, Codex, Cursor).
- Config lives in `.work/config.yml`. Event log is `.work/todo.jsonl`.
- Every plan MUST end by running `worklog plan-capture`.
- Work discovered mid-flight: `worklog add --unplanned --discovered-during <item>` BEFORE doing the work.
- Never hand-edit `.work/*.jsonl` (use `worklog`) or `docs/roadmap.md` (generated).
- After changing work items, run `worklog roadmap-render` and commit the log and roadmap together.
- CLI: `worklog` on PATH, or `python3 <wiki_ticket_sdd>/bin/worklog`.
<!-- worklog:policy:end -->

