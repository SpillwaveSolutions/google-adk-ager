# Host matrix

`google-adk-ager` is one plugin, five install surfaces. Skills live once under `skills/`.

| Host | Manifest | Install |
| --- | --- | --- |
| Agent Plugins 1.0 | `plugin.json` | any host that reads agent-plugins.org |
| Claude Code | `.claude-plugin/plugin.json` + `marketplace.json` | `claude plugin marketplace add SpillwaveSolutions/google-adk-ager` |
| Grok Build | `.grok-plugin/marketplace.json` (Claude layout is zero-config) | drop into workspace / Claude marketplace |
| Codex | `.codex-plugin/plugin.json` | `codex plugin marketplace add SpillwaveSolutions/google-adk-ager` |
| Cursor | `.cursor-plugin/plugin.json` + `.cursor/rules/` | `/plugin install google-adk-ager` |

Command on Claude/Grok: `/ager-to-google-adk`
Command on Codex: `$ager-to-google-adk`

Depends on `okf-agent-graph` for author/validate. This plugin only compiles.

## WikiTicket SDD

Track work with the worklog plugin (`SpillwaveSolutions/wiki_ticket_sdd`). See [WORKLOG.md](WORKLOG.md).
