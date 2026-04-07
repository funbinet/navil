"""Attack graph construction for chainable findings."""

from __future__ import annotations

import networkx as nx

from navil.knowledge.models import Finding


class AttackGraph:
    def __init__(self) -> None:
        self.graph: nx.DiGraph = nx.DiGraph()

    def build(self, findings: list[Finding]) -> nx.DiGraph:
        self.graph.clear()
        for finding in findings:
            root = f"{finding.plugin}:{finding.id}"
            self.graph.add_node(root, severity=finding.severity.value, url=finding.url)
            for candidate in finding.chain_potential:
                self.graph.add_node(candidate, severity="POTENTIAL")
                self.graph.add_edge(root, candidate)
        return self.graph

    def mermaid(self) -> str:
        lines = ["graph LR"]
        for source, target in self.graph.edges:
            lines.append(f"    {source.replace(':', '_')} --> {target.replace(':', '_')}")
        return "\n".join(lines)
