"""AGER → Google ADK emitters.

Languages: python, typescript, go, java, kotlin
Modes:
  agent — non-graph LlmAgent + sub_agents (ADK v1 style, all languages)
  graph — ADK 2.0 Workflow (Python, Go) or Sequential/Parallel/Loop templates
          (TypeScript, Java, Kotlin — Workflow 2.0 not GA there)
"""

from __future__ import annotations

import json
from ir import AgerGraph

LANGS = ("python", "typescript", "go", "java", "kotlin")
MODES = ("agent", "graph")
MODEL = "gemini-flash-latest"


def q(s: str) -> str:
    return json.dumps(s)


def ident(s: str) -> str:
    out = []
    up = False
    for ch in s.replace("-", "_"):
        if ch == "_":
            up = True
            continue
        out.append(ch.upper() if up else ch)
        up = False
    return "".join(out) or "agent"


def camel(s: str) -> str:
    i = ident(s)
    return i[:1].lower() + i[1:] if i else "agent"


def pascal(s: str) -> str:
    i = ident(s)
    return i[:1].upper() + i[1:] if i else "Agent"


def py_name(s: str) -> str:
    return s.replace("-", "_")


def generate(
    graph: AgerGraph,
    *,
    lang: str = "all",
    mode: str = "all",
    adk_version: str = "2",
) -> dict[str, str]:
    langs = LANGS if lang in ("all", "", None) else (lang,)
    modes = MODES if mode in ("all", "", None) else (mode,)
    files: dict[str, str] = {}
    files["README.md"] = _root_readme(graph, adk_version)
    files["MAPPING.md"] = _mapping_md()
    for lg in langs:
        if lg not in LANGS:
            raise SystemExit(f"unknown --lang {lg}. choose from {', '.join(LANGS)} or all")
        for md in modes:
            if md not in MODES:
                raise SystemExit(f"unknown --mode {md}. choose agent, graph, or all")
            files.update(_emit_one(graph, lg, md, adk_version))
    return files


def _emit_one(graph: AgerGraph, lang: str, mode: str, adk_version: str) -> dict[str, str]:
    fn = {
        ("python", "agent"): _py_agent,
        ("python", "graph"): _py_graph if adk_version != "1" else _py_templates,
        ("typescript", "agent"): _ts_agent,
        ("typescript", "graph"): _ts_graph,
        ("go", "agent"): _go_agent,
        ("go", "graph"): _go_graph if adk_version != "1" else _go_templates,
        ("java", "agent"): _java_agent,
        ("java", "graph"): _java_graph,
        ("kotlin", "agent"): _kt_agent,
        ("kotlin", "graph"): _kt_graph,
    }[(lang, mode)]
    return fn(graph)


def _lead(g: AgerGraph):
    return next(a for a in g.agents if a.role == "orchestrator")


def _others(g: AgerGraph):
    lead = _lead(g)
    return [a for a in g.agents if a.id != lead.id]


# --- Python -----------------------------------------------------------------

def _py_agent(g: AgerGraph) -> dict[str, str]:
    lead = _lead(g)
    blocks = []
    names = []
    for a in g.agents:
        n = py_name(a.id)
        names.append(n)
        tools = ", ".join(py_name(t) for t in a.tools)  # names only; stubs below
        tool_arg = f"tools=[{tools}]," if a.tools else ""
        blocks.append(
            f"{n} = LlmAgent(\n"
            f"    name={q(a.id)},\n"
            f"    model={q(MODEL)},\n"
            f"    description={q(a.description)},\n"
            f"    instruction={q(a.instructions)},\n"
            f"    {tool_arg}\n"
            f")"
        )
    lead_n = py_name(lead.id)
    subs = ", ".join(py_name(a.id) for a in _others(g))
    tool_stubs = "\n".join(
        f"def {py_name(t.id)}(query: str) -> str:\n    \"\"\"{t.description}\"\"\"\n    return query\n"
        for t in g.tools
    )
    code = f'''# Generated from AGER {g.ager_version}: {g.title}
# ADK non-graph (LlmAgent + sub_agents). LoopPolicy max_turns={g.max_turns} price=${g.price_budget}.
from google.adk.agents import LlmAgent

{tool_stubs}
{chr(10).join(blocks)}

# Hierarchical: lead delegates to specialists.
{lead_n}.sub_agents = [{subs}]
root_agent = {lead_n}

# LoopPolicy (host does not meter USD): goal → deadline → price → max_turns → no_progress
# max_turns={g.max_turns}  price_budget={g.price_budget}  deadline_ms={g.deadline_ms}
'''
    return {
        "python/agent/agent.py": code,
        "python/agent/README.md": _lang_readme(g, "Python", "agent", "pip install google-adk"),
    }


def _py_graph(g: AgerGraph) -> dict[str, str]:
    lead = _lead(g)
    nodes = []
    node_names = []
    for a in g.agents:
        n = py_name(a.id)
        node_names.append(n)
        nodes.append(
            f"{n} = Agent(\n"
            f"    name={q(a.id)},\n"
            f"    model={q(MODEL)},\n"
            f"    instruction={q(a.instructions)},\n"
            f")"
        )
    chain = ", ".join(node_names)
    code = f'''# Generated from AGER {g.ager_version}: {g.title}
# ADK 2.0 graph Workflow. LoopPolicy: {" → ".join(g.loop_priority)}.
from google.adk import Agent, Workflow

{chr(10).join(nodes)}

# Orchestrator-workers: START → lead → workers/judge/synth.
# Parallel workers are listed after the lead; ADK 2.0 fan-out is a later cut.
root_agent = Workflow(
    name={q(g.id)},
    edges=[
        ("START", {chain}),
    ],
)

# LoopPolicy (documented; Workflow does not meter USD):
# max_turns={g.max_turns}  price_budget={g.price_budget}  deadline_ms={g.deadline_ms}
# on_goal={g.on_goal}  on_exhaust={g.on_exhaust}  entry={lead.id}
'''
    return {
        "python/graph/workflow.py": code,
        "python/graph/README.md": _lang_readme(g, "Python", "graph (ADK 2.0 Workflow)", "pip install google-adk"),
    }


def _py_templates(g: AgerGraph) -> dict[str, str]:
    """v1 Sequential + Parallel + Loop templates."""
    lead = _lead(g)
    workers = [a for a in g.agents if a.role == "worker"]
    rest = [a for a in g.agents if a.role != "worker"]
    defs = []
    for a in g.agents:
        n = py_name(a.id)
        defs.append(
            f"{n} = LlmAgent(name={q(a.id)}, model={q(MODEL)}, instruction={q(a.instructions)})"
        )
    par = ", ".join(py_name(a.id) for a in workers) or py_name(lead.id)
    seq = ", ".join(py_name(a.id) for a in rest)
    code = f'''# Generated from AGER {g.ager_version}: {g.title}
# ADK v1 template workflows (Sequential / Parallel / Loop).
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent

{chr(10).join(defs)}

parallel_workers = ParallelAgent(name="workers", sub_agents=[{par}])
pipeline = SequentialAgent(name="pipeline", sub_agents=[{py_name(lead.id)}, parallel_workers{(", " + seq) if seq else ""}])
root_agent = LoopAgent(name={q(g.id + "-loop")}, max_iterations={g.max_turns}, sub_agents=[pipeline])
'''
    return {
        "python/graph/workflow.py": code,
        "python/graph/README.md": _lang_readme(g, "Python", "graph (v1 Sequential/Parallel/Loop)", "pip install google-adk"),
    }


# --- TypeScript -------------------------------------------------------------

def _ts_agent(g: AgerGraph) -> dict[str, str]:
    lead = _lead(g)
    consts = []
    for a in g.agents:
        n = camel(a.id)
        consts.append(
            f"const {n} = new LlmAgent({{\n"
            f"  name: {q(a.id)},\n"
            f"  model: {q(MODEL)},\n"
            f"  description: {q(a.description)},\n"
            f"  instruction: {q(a.instructions)},\n"
            f"}});"
        )
    subs = ", ".join(camel(a.id) for a in _others(g))
    lead_n = camel(lead.id)
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK non-graph (LlmAgent + subAgents). max_turns={g.max_turns}
import {{ LlmAgent }} from '@google/adk';

{chr(10).join(consts)}

{lead_n}.subAgents = [{subs}];
export const rootAgent = {lead_n};
'''
    return {
        "typescript/agent/agent.ts": code,
        "typescript/agent/package.json": _pkg_json(g, "agent"),
        "typescript/agent/README.md": _lang_readme(g, "TypeScript", "agent", "npm i @google/adk"),
    }


def _ts_graph(g: AgerGraph) -> dict[str, str]:
    defs = []
    for a in g.agents:
        n = camel(a.id)
        defs.append(
            f"const {n} = new LlmAgent({{ name: {q(a.id)}, model: {q(MODEL)}, instruction: {q(a.instructions)} }});"
        )
    workers = [camel(a.id) for a in g.agents if a.role == "worker"]
    lead = camel(_lead(g).id)
    seq_rest = [camel(a.id) for a in g.agents if a.role not in ("orchestrator", "worker")]
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK template graph (Sequential + Parallel + Loop). Workflow 2.0 is Python/Go GA.
import {{ LlmAgent, SequentialAgent, ParallelAgent, LoopAgent }} from '@google/adk';

{chr(10).join(defs)}

const workers = new ParallelAgent({{ name: 'workers', subAgents: [{", ".join(workers) or lead}] }});
const pipeline = new SequentialAgent({{
  name: 'pipeline',
  subAgents: [{lead}, workers{(", " + ", ".join(seq_rest)) if seq_rest else ""}],
}});
export const rootAgent = new LoopAgent({{
  name: {q(g.id + "-loop")},
  maxIterations: {g.max_turns},
  subAgents: [pipeline],
}});
'''
    return {
        "typescript/graph/workflow.ts": code,
        "typescript/graph/package.json": _pkg_json(g, "graph"),
        "typescript/graph/README.md": _lang_readme(g, "TypeScript", "graph (Sequential/Parallel/Loop)", "npm i @google/adk"),
    }


def _pkg_json(g: AgerGraph, kind: str) -> str:
    return json.dumps(
        {
            "name": f"{g.id}-adk-{kind}",
            "version": "0.1.0",
            "private": True,
            "type": "module",
            "dependencies": {"@google/adk": "*"},
        },
        indent=2,
    ) + "\n"


# --- Go ---------------------------------------------------------------------

def _go_agent(g: AgerGraph) -> dict[str, str]:
    lead = _lead(g)
    builders = []
    vars_ = []
    for a in g.agents:
        n = camel(a.id)
        vars_.append(n)
        builders.append(
            f"\t{n}, err := llmagent.New(llmagent.Config{{\n"
            f"\t\tName:        {q(a.id)},\n"
            f"\t\tModel:       model,\n"
            f"\t\tDescription: {q(a.description)},\n"
            f"\t\tInstruction: {q(a.instructions)},\n"
            f"\t}})\n"
            f"\tif err != nil {{\n\t\treturn nil, err\n\t}}"
        )
    sub = ", ".join(camel(a.id) for a in _others(g))
    lead_n = camel(lead.id)
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK non-graph (llmagent + SubAgents). max_turns={g.max_turns}
package agent

import (
\t"google.golang.org/adk/v2/agent"
\t"google.golang.org/adk/v2/agent/llmagent"
\t"google.golang.org/adk/v2/model"
)

func NewRoot(model model.LLM) (agent.Agent, error) {{
{chr(10).join(builders)}
\t_ = []agent.Agent{{{sub}}} // specialists; attach on lead when SDK field is set
\treturn {lead_n}, nil
}}
'''
    return {
        "go/agent/agent.go": code,
        "go/agent/go.mod": f"module {g.id}/adk-agent\n\ngo 1.23\n\nrequire google.golang.org/adk/v2 v2.0.0\n",
        "go/agent/README.md": _lang_readme(g, "Go", "agent", "go get google.golang.org/adk/v2"),
    }


def _go_graph(g: AgerGraph) -> dict[str, str]:
    nodes = []
    names = []
    for a in g.agents:
        n = camel(a.id) + "Node"
        names.append(n)
        nodes.append(
            f"\t{n} := workflow.NewAgentNode({q(a.id)}, {camel(a.id)}, workflow.NodeConfig{{}})"
        )
    chain = ", ".join(names)
    agent_news = []
    for a in g.agents:
        agent_news.append(
            f"\t{camel(a.id)}, err := llmagent.New(llmagent.Config{{Name: {q(a.id)}, Model: model, Instruction: {q(a.instructions)}}})\n"
            f"\tif err != nil {{\n\t\treturn nil, err\n\t}}"
        )
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK 2.0 graph (workflow.Chain). LoopPolicy max_turns={g.max_turns}
package graph

import (
\t"google.golang.org/adk/v2/agent"
\t"google.golang.org/adk/v2/agent/llmagent"
\t"google.golang.org/adk/v2/agent/workflowagent"
\t"google.golang.org/adk/v2/model"
\t"google.golang.org/adk/v2/workflow"
)

func NewRoot(model model.LLM) (agent.Agent, error) {{
{chr(10).join(agent_news)}
{chr(10).join(nodes)}
\treturn workflowagent.New(workflowagent.Config{{
\t\tName:        {q(g.id)},
\t\tDescription: {q(g.description)},
\t\tEdges:       workflow.Chain(workflow.Start, {chain}),
\t}})
}}
'''
    return {
        "go/graph/workflow.go": code,
        "go/graph/go.mod": f"module {g.id}/adk-graph\n\ngo 1.23\n\nrequire google.golang.org/adk/v2 v2.0.0\n",
        "go/graph/README.md": _lang_readme(g, "Go", "graph (ADK 2.0 Workflow)", "go get google.golang.org/adk/v2"),
    }


def _go_templates(g: AgerGraph) -> dict[str, str]:
    return _go_graph(g)  # v1 still uses workflowagent in this cut


# --- Java -------------------------------------------------------------------

def _java_agent(g: AgerGraph) -> dict[str, str]:
    builders = []
    names = []
    for a in g.agents:
        n = camel(a.id)
        names.append(n)
        builders.append(
            f"        LlmAgent {n} = LlmAgent.builder()\n"
            f"                .name({q(a.id)})\n"
            f"                .model({q(MODEL)})\n"
            f"                .description({q(a.description)})\n"
            f"                .instruction({q(a.instructions)})\n"
            f"                .build();"
        )
    lead = camel(_lead(g).id)
    subs = ", ".join(camel(a.id) for a in _others(g))
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK non-graph (LlmAgent + subAgents). max_turns={g.max_turns}
package com.spillwave.ager.adk;

import com.google.adk.agents.LlmAgent;

public final class AgentApp {{
    public static LlmAgent root() {{
{chr(10).join(builders)}
        return LlmAgent.builder()
                .name({q(_lead(g).id)})
                .model({q(MODEL)})
                .instruction({q(_lead(g).instructions)})
                .subAgents({subs})
                .build();
    }}
}}
'''
    return {
        "java/agent/src/main/java/com/spillwave/ager/adk/AgentApp.java": code,
        "java/agent/pom.xml": _pom(g, "agent"),
        "java/agent/README.md": _lang_readme(g, "Java", "agent", "see pom.xml google-adk"),
    }


def _java_graph(g: AgerGraph) -> dict[str, str]:
    builders = []
    for a in g.agents:
        n = camel(a.id)
        builders.append(
            f"        LlmAgent {n} = LlmAgent.builder().name({q(a.id)}).model({q(MODEL)}).instruction({q(a.instructions)}).build();"
        )
    workers = [camel(a.id) for a in g.agents if a.role == "worker"]
    lead = camel(_lead(g).id)
    rest = [camel(a.id) for a in g.agents if a.role not in ("orchestrator", "worker")]
    par = ", ".join(workers) or lead
    seq = ", ".join([lead, "workers"] + rest)
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK template graph (Sequential + Parallel + Loop). max_turns={g.max_turns}
package com.spillwave.ager.adk;

import com.google.adk.agents.LlmAgent;
import com.google.adk.agents.LoopAgent;
import com.google.adk.agents.ParallelAgent;
import com.google.adk.agents.SequentialAgent;

public final class WorkflowApp {{
    public static LoopAgent root() {{
{chr(10).join(builders)}
        ParallelAgent workers = ParallelAgent.builder().name("workers").subAgents({par}).build();
        SequentialAgent pipeline = SequentialAgent.builder().name("pipeline").subAgents({seq}).build();
        return LoopAgent.builder()
                .name({q(g.id + "-loop")})
                .maxIterations({g.max_turns})
                .subAgents(pipeline)
                .build();
    }}
}}
'''
    return {
        "java/graph/src/main/java/com/spillwave/ager/adk/WorkflowApp.java": code,
        "java/graph/pom.xml": _pom(g, "graph"),
        "java/graph/README.md": _lang_readme(g, "Java", "graph (Sequential/Parallel/Loop)", "see pom.xml google-adk"),
    }


def _pom(g: AgerGraph, kind: str) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.spillwave.ager</groupId>
  <artifactId>{g.id}-adk-{kind}</artifactId>
  <version>0.1.0</version>
  <properties><maven.compiler.release>17</maven.compiler.release></properties>
  <dependencies>
    <dependency>
      <groupId>com.google.adk</groupId>
      <artifactId>google-adk</artifactId>
      <version>0.2.0</version>
    </dependency>
  </dependencies>
</project>
'''


# --- Kotlin -----------------------------------------------------------------

def _kt_agent(g: AgerGraph) -> dict[str, str]:
    defs = []
    for a in g.agents:
        n = camel(a.id)
        defs.append(
            f"    val {n} = LlmAgent(\n"
            f"        name = {q(a.id)},\n"
            f"        model = Gemini(name = {q(MODEL)}),\n"
            f"        description = {q(a.description)},\n"
            f"        instruction = Instruction({q(a.instructions)}),\n"
            f"    )"
        )
    lead = camel(_lead(g).id)
    subs = ", ".join(camel(a.id) for a in _others(g))
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK non-graph (LlmAgent + subAgents). max_turns={g.max_turns}
package com.spillwave.ager.adk

import com.google.adk.agents.Instruction
import com.google.adk.agents.LlmAgent
import com.google.adk.models.Gemini

fun rootAgent(): LlmAgent {{
{chr(10).join(defs)}
    return LlmAgent(
        name = {q(_lead(g).id)},
        model = Gemini(name = {q(MODEL)}),
        instruction = Instruction({q(_lead(g).instructions)}),
        subAgents = listOf({subs}),
    )
}}
'''
    return {
        "kotlin/agent/src/main/kotlin/com/spillwave/ager/adk/AgentApp.kt": code,
        "kotlin/agent/README.md": _lang_readme(g, "Kotlin", "agent", "google-adk Kotlin SDK"),
    }


def _kt_graph(g: AgerGraph) -> dict[str, str]:
    defs = []
    for a in g.agents:
        n = camel(a.id)
        defs.append(
            f"    val {n} = LlmAgent(name = {q(a.id)}, model = Gemini(name = {q(MODEL)}), instruction = Instruction({q(a.instructions)}))"
        )
    workers = ", ".join(camel(a.id) for a in g.agents if a.role == "worker") or camel(_lead(g).id)
    lead = camel(_lead(g).id)
    rest = ", ".join(camel(a.id) for a in g.agents if a.role not in ("orchestrator", "worker"))
    extra = f", {rest}" if rest else ""
    code = f'''// Generated from AGER {g.ager_version}: {g.title}
// ADK template graph (Sequential + Parallel + Loop). max_turns={g.max_turns}
package com.spillwave.ager.adk

import com.google.adk.agents.Instruction
import com.google.adk.agents.LlmAgent
import com.google.adk.agents.LoopAgent
import com.google.adk.agents.ParallelAgent
import com.google.adk.agents.SequentialAgent
import com.google.adk.models.Gemini

fun rootAgent(): LoopAgent {{
{chr(10).join(defs)}
    val workers = ParallelAgent(name = "workers", subAgents = listOf({workers}))
    val pipeline = SequentialAgent(name = "pipeline", subAgents = listOf({lead}, workers{extra}))
    return LoopAgent(name = {q(g.id + "-loop")}, maxIterations = {g.max_turns}, subAgents = listOf(pipeline))
}}
'''
    return {
        "kotlin/graph/src/main/kotlin/com/spillwave/ager/adk/WorkflowApp.kt": code,
        "kotlin/graph/README.md": _lang_readme(g, "Kotlin", "graph (Sequential/Parallel/Loop)", "google-adk Kotlin SDK"),
    }


def _lang_readme(g: AgerGraph, lang: str, kind: str, install: str) -> str:
    return f"""# {g.title} — Google ADK {lang} / {kind}

Compiled from AGER {g.ager_version}. Entry `{g.entry}`.
LoopPolicy: {" → ".join(g.loop_priority)}. max_turns={g.max_turns} price=${g.price_budget}.

```
{install}
```

Not production-ready without tests.
"""


def _root_readme(g: AgerGraph, adk_version: str) -> str:
    return f"""# {g.title} — Google ADK

Compiled from AGER {g.ager_version} (emit adk_version={adk_version}).

| Path | What |
| --- | --- |
| `python/agent/` | LlmAgent + sub_agents (non-graph) |
| `python/graph/` | ADK 2.0 `Workflow` (v1: Sequential/Parallel/Loop) |
| `typescript/agent/` | `LlmAgent` |
| `typescript/graph/` | Sequential + Parallel + Loop |
| `go/agent/` | `llmagent.New` |
| `go/graph/` | ADK 2.0 `workflow.Chain` |
| `java/agent/` | `LlmAgent.builder` |
| `java/graph/` | Sequential + Parallel + Loop |
| `kotlin/agent/` | `LlmAgent(...)` |
| `kotlin/graph/` | Sequential + Parallel + Loop |

LoopPolicy max_turns={g.max_turns} price=${g.price_budget} deadline_ms={g.deadline_ms}.
"""


def _mapping_md() -> str:
    return """# AGER → Google ADK

| AGER | Non-graph (agent) | Graph |
| --- | --- | --- |
| OrchestratorAgent | lead `LlmAgent` with `sub_agents` | first node after START / Sequential head |
| WorkerAgent | sub-agent | ParallelAgent children or Workflow nodes |
| Judge / Synthesizer | sub-agent | later Sequential nodes |
| LoopPolicy.max_turns | documented on lead | `LoopAgent.maxIterations` or Workflow comment |
| ScratchPad | session state | session state |
| Tool | function tool stub | function node / tool on agent |

ADK 2.0 `Workflow` is GA for **Python** and **Go**. TypeScript / Java / Kotlin graph mode emits template workflows (`SequentialAgent`, `ParallelAgent`, `LoopAgent`).
"""
