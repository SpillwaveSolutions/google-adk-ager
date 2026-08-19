# google-adk-ager

AGER → **Google ADK** translator plugin.

Author graphs with [`okf-agent-graph`](https://github.com/SpillwaveSolutions/okf-agent-graph). This plugin compiles.

Emits **both** ADK shapes, in **all five official languages**:

| Mode | What | Languages |
| --- | --- | --- |
| **agent** (non-graph) | `LlmAgent` + `sub_agents` | Python, TypeScript, Go, Java, Kotlin |
| **graph** | ADK 2.0 `Workflow` / `workflow.Chain` | Python, Go |
| **graph** | Sequential + Parallel + Loop templates | TypeScript, Java, Kotlin (Workflow 2.0 not GA) |

A host gets a manifest, never a fork. See [docs/HOSTS.md](docs/HOSTS.md).

## Install

```bash
claude plugin marketplace add SpillwaveSolutions/google-adk-ager
claude plugin install google-adk-ager@google-adk-ager-marketplace

codex plugin marketplace add SpillwaveSolutions/google-adk-ager
```

Cursor: `/plugin install google-adk-ager` — [docs/CURSOR.md](docs/CURSOR.md).

## Use

```
/ager-to-google-adk
```

```bash
python3 scripts/emit.py --bundle path/to/sample-ager --out ./generated
python3 scripts/emit.py --lang python --mode graph --adk-version 2 --out ./generated/py-graph
python3 scripts/emit.py --lang java --mode agent --out ./generated/java-agent
python3 scripts/emit.py --lang kotlin --mode graph --out ./generated/kt-graph
python3 scripts/emit.py --lang go --mode all --adk-version 2 --out ./generated/go
python3 scripts/emit.py --lang typescript --mode all --out ./generated/ts
```

`--lang`: `all` (default) | `python` | `typescript` | `go` | `java` | `kotlin`  
`--mode`: `all` (default) | `agent` | `graph`  
`--adk-version`: `2` (default, Workflow for Python/Go) | `1` (template workflows)

## License

MIT
