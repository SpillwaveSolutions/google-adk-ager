---
name: ager-to-google-adk
description: Translate a validated AGER/OKF AgentGraph into Google ADK (Python, TypeScript, Go, Java, Kotlin). Use for LlmAgent (non-graph) or Workflow graph (ADK 2.0).
---

# AGER → Google ADK

This plugin **compiles**. Authoring is `okf-agent-graph`.

## Mapping

| AGER | Non-graph (`--mode agent`) | Graph (`--mode graph`) |
| --- | --- | --- |
| OrchestratorAgent | lead `LlmAgent` + `sub_agents` | first node / Sequential head |
| WorkerAgent | sub-agent | `ParallelAgent` or Workflow node |
| Judge / Synthesizer | sub-agent | later Sequential / Workflow nodes |
| LoopPolicy.max_turns | documented | `LoopAgent.maxIterations` |
| ScratchPad | session state | session state |
| Tool | function-tool stub | tool / function node |

ADK 2.0 `Workflow` is GA for Python and Go. TypeScript, Java, and Kotlin graph mode emits template workflows.

## Steps

1. Locate the AGER bundle. Validate with `ager-validate` if present.
2. Run the deterministic emitter. Do not freehand the tree.

```bash
python3 scripts/emit.py --bundle <AGER_ROOT> --out <OUT> --lang all --mode all --adk-version 2
```

3. Report written paths. Filter with `--lang python|typescript|go|java|kotlin` and `--mode agent|graph`.
4. Never claim production-ready without tests.

## References

- `references/mapping.md`
- https://adk.dev/
