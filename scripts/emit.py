#!/usr/bin/env python3
"""Emit Google ADK projects from an AGER bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

from framework import LANGS, generate
from ir import AgerGraph, load_bundle
from layout import write


def emit(
    graph: AgerGraph,
    out: Path,
    *,
    lang: str = "all",
    mode: str = "all",
    adk_version: str = "2",
) -> list[Path]:
    written = []
    for rel, content in generate(graph, lang=lang, mode=mode, adk_version=adk_version).items():
        written.append(write(out, rel, content))
    return written


def main() -> None:
    p = argparse.ArgumentParser(prog="google-adk-ager")
    p.add_argument("--bundle", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--lang", default="all", help=f"all or one of: {', '.join(LANGS)}")
    p.add_argument("--mode", default="all", choices=["all", "agent", "graph"], help="agent=LlmAgent (non-graph), graph=Workflow/templates")
    p.add_argument("--adk-version", default="2", choices=["1", "2"], help="1=template workflows for Python/Go graph; 2=Workflow API")
    args = p.parse_args()
    written = emit(
        load_bundle(args.bundle),
        args.out,
        lang=args.lang,
        mode=args.mode,
        adk_version=args.adk_version,
    )
    print(f"wrote {len(written)} files to {args.out}")
    for w in written:
        print(" ", w)


if __name__ == "__main__":
    main()
