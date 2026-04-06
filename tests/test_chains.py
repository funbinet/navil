from __future__ import annotations

from navil.chains.builder import ExploitChainBuilder
from navil.knowledge.models import Finding, Severity


def test_chain_builder_returns_known_chain() -> None:
    findings = [
        Finding(
            id="1",
            scan_id="scan",
            plugin="open_redirect",
            severity=Severity.MEDIUM,
            category="test",
            title="A",
            url="https://example.com",
            evidence="e",
        ),
        Finding(
            id="2",
            scan_id="scan",
            plugin="ssrf",
            severity=Severity.HIGH,
            category="test",
            title="B",
            url="https://example.com/api",
            evidence="e",
        ),
    ]
    chains = ExploitChainBuilder().build(findings)
    assert chains
    assert any("SSRF" in chain.name for chain in chains)
