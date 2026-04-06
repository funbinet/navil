"""Chain execution planner (safe dry-run mode)."""

from __future__ import annotations

from navil.chains.builder import ExploitChain


def execute_chain_dry_run(chain: ExploitChain) -> dict[str, object]:
    return {
        "chain": chain.name,
        "mode": "dry-run",
        "steps": chain.steps,
        "status": "planned",
        "impact_score": chain.impact_score,
    }
