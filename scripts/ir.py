"""AGER IR + sample matching okf-agent-graph sample-ager v0.3.0."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Agent:
    id: str
    role: str
    title: str
    description: str
    instructions: str
    tools: list[str] = field(default_factory=list)
    ephemeral: bool = False
    max_workers: int = 5
    record_key: str = ""
    record_mode: str = "append"


@dataclass
class Tool:
    id: str
    title: str
    description: str
    cost_usd: float = 0.0
    rules: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class LoopControl:
    type: str
    id: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgerGraph:
    id: str
    title: str
    description: str
    ager_version: str
    entry: str
    agents: list[Agent]
    tools: list[Tool]
    max_turns: int
    price_budget: float
    deadline_ms: int
    loop_priority: list[str]
    on_goal: str = "return"
    on_exhaust: str = "return_best"


def load_sample() -> AgerGraph:
    return AgerGraph(
        id="parallel-research",
        title="Parallel research graph",
        description="Orchestrator-workers research with judge and synthesizer.",
        ager_version="0.3.0",
        entry="lead-researcher",
        max_turns=6,
        price_budget=2.5,
        deadline_ms=600_000,
        loop_priority=["goal", "deadline", "price_budget", "max_turns", "no_progress"],
        agents=[
            Agent(
                "lead-researcher",
                "orchestrator",
                "Lead researcher",
                "Plans facets and drives the outer loop.",
                "Decompose the query, spawn workers, collect findings, judge, synthesize.",
                max_workers=5,
                record_key="orchestrator_plans",
            ),
            Agent(
                "worker",
                "worker",
                "Specialist worker",
                "Isolated doer.",
                "Return structured findings only. Prefer artifact refs for large blobs.",
                tools=["web_search"],
                ephemeral=True,
                record_key="worker_outputs",
            ),
            Agent(
                "judge",
                "judge",
                "Quality judge",
                "Rubric scorer.",
                "Score coverage, citations, contradictions 0-1. Pass if score >= 0.78.",
                record_key="judgments",
            ),
            Agent(
                "synthesizer",
                "synthesizer",
                "Synthesizer",
                "Fan-in reduce.",
                "Merge findings, resolve conflicts, write a concise report with sources.",
                record_key="final_report",
                record_mode="set",
            ),
        ],
        tools=[
            Tool(
                "web_search",
                "Web search",
                "Budgeted search with duplicate block.",
                cost_usd=0.002,
                rules=[
                    {"id": "block-if-budget", "action": "block", "message": "Price budget exhausted"},
                    {"id": "block-dup", "action": "block", "message": "Duplicate query"},
                ],
            )
        ],
    )


def _frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    meta: dict[str, Any] = {}
    for line in text[3:end].splitlines():
        if ":" not in line or line.startswith(" ") or line.startswith("-"):
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta


def load_bundle(path: Path | None) -> AgerGraph:
    if path is None:
        return load_sample()
    graph_md = path / "runtime" / "agent-graph.md"
    if not graph_md.exists():
        return load_sample()
    sample = load_sample()
    meta = _frontmatter(graph_md.read_text(encoding="utf-8"))
    if meta.get("title"):
        sample.title = meta["title"]
    if meta.get("description"):
        sample.description = meta["description"]
    if meta.get("ager_version"):
        sample.ager_version = meta["ager_version"]
    return sample
