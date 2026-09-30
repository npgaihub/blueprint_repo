"""Minimal eval runner: sends every case in cases.jsonl to the real model and checks the answer.

Starter only - extend the checks (or add an LLM judge) for your use case.
Costs real API tokens: `uv run python evals/run.py`
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from app.llm import get_llm

CASES = Path(__file__).with_name("cases.jsonl")


def check(case: dict[str, Any], answer: str) -> bool:
    text = answer.lower()
    must_all = [str(s).lower() for s in case.get("must_contain", [])]
    must_any = [str(s).lower() for s in case.get("must_contain_any", [])]
    return all(s in text for s in must_all) and (not must_any or any(s in text for s in must_any))


async def main() -> int:
    llm = get_llm()
    cases = [json.loads(line) for line in CASES.read_text().splitlines() if line.strip()]
    answers = await asyncio.gather(
        *(llm.complete([{"role": "user", "content": c["prompt"]}]) for c in cases)
    )
    failed = 0
    for case, answer in zip(cases, answers, strict=True):
        ok = check(case, answer)
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {case['id']}")
    print(f"\n{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
