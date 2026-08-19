# AGER → Google ADK

Official SDKs: Python, TypeScript, Go, Java, Kotlin. See https://adk.dev/

## Versions

| ADK | Non-graph | Graph |
| --- | --- | --- |
| v1 | `LlmAgent` / `Agent` + `sub_agents` | `SequentialAgent`, `ParallelAgent`, `LoopAgent` |
| v2.0 | same | Python/Go: `Workflow` / `workflow.Chain`. Others: still templates |

## Flags

`--adk-version 2` (default) uses Workflow for Python and Go graph mode.  
`--adk-version 1` uses Sequential/Parallel/Loop for Python graph mode too.

## LoopPolicy

Hosts do not meter USD. Emit `max_turns` as `LoopAgent.maxIterations` / comments. Check order: goal, deadline, price, max_turns, no_progress.
