"""Chain construction from finding relationships."""

from __future__ import annotations

from dataclasses import dataclass

from navil.chains.graph import AttackGraph
from navil.knowledge.models import Finding, Severity


@dataclass(slots=True)
class ExploitChain:
    name: str
    steps: list[str]
    impact_score: int


class ExploitChainBuilder:
    def __init__(self) -> None:
        self.attack_graph = AttackGraph()

    def build(self, findings: list[Finding]) -> list[ExploitChain]:
        self.attack_graph.build(findings)
        chains: list[ExploitChain] = []

        by_plugin = {finding.plugin: finding for finding in findings}

        if "open_redirect" in by_plugin and "ssrf" in by_plugin:
            chains.append(
                ExploitChain(
                    name="Open Redirect to SSRF Pivot",
                    steps=[
                        "Trigger open redirect parameter",
                        "Pivot request toward internal endpoint",
                        "Enumerate internal responses",
                    ],
                    impact_score=75,
                )
            )

        if "xss" in by_plugin and "auth_bypass" in by_plugin:
            chains.append(
                ExploitChain(
                    name="XSS to Session Misuse",
                    steps=[
                        "Reflect script payload",
                        "Capture session context in authorized test harness",
                        "Replay against privileged route for validation",
                    ],
                    impact_score=80,
                )
            )

        if "idor" in by_plugin and "info_disclosure" in by_plugin:
            chains.append(
                ExploitChain(
                    name="IDOR Data Exposure Chain",
                    steps=[
                        "Enumerate exposed identifiers",
                        "Validate ownership checks",
                        "Extract sensitive object data",
                    ],
                    impact_score=70,
                )
            )

        if not chains and findings:
            critical = any(item.severity == Severity.CRITICAL for item in findings)
            chains.append(
                ExploitChain(
                    name="Single-Finding Escalation Candidate",
                    steps=["Validate exploitability", "Assess blast radius", "Recommend remediation"],
                    impact_score=60 if critical else 45,
                )
            )

        return chains
