# CLAUDE.md — google-adk-ager

Translator to **Google ADK**. Author graphs with `okf-agent-graph`.

```bash
python3 scripts/emit.py --bundle <AGER> --out ./generated
```

- Do not invent agents
- LoopPolicy order: goal, deadline, price, max_turns, no_progress
- Python/Go graph mode uses ADK 2.0 Workflow; TS/Java/Kotlin use Sequential/Parallel/Loop
- Never claim production-ready without tests
