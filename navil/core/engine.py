"""Main scan orchestration engine."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from navil.brain.agent import AdaptiveRLAgent
from navil.brain.reward import calculate_reward
from navil.brain.trainer import BrainTrainer
from navil.chains.builder import ExploitChainBuilder
from navil.config import AppConfig, load_scope
from navil.constants import MODEL_DIR
from navil.core.scope import ScopeEnforcer, ScopeViolation
from navil.core.session import SessionManager
from navil.knowledge.models import (
    DiscoveredEndpoint,
    Finding,
    ScanEvent,
    ScanRequest,
    ScanResult,
    ScanStatus,
)
from navil.knowledge.store import KnowledgeStore
from navil.knowledge.vectors import LocalVectorStore
from navil.mutator.engine import PayloadMutator
from navil.recon.auth import load_target_credentials
from navil.recon.crawler import ReconCrawler
from navil.scanner.active import ActiveScanner
from navil.scanner.detector import PluginRegistry
from navil.utils.logger import get_logger


class NavilEngine:
    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or AppConfig()
        self.logger = get_logger("navil.engine")
        self.store = KnowledgeStore(self.config.db_path)
        self.vector_store = LocalVectorStore()
        self.plugin_registry = PluginRegistry()
        self.crawler = ReconCrawler()
        self.brain = AdaptiveRLAgent(model_path=Path(MODEL_DIR) / "brain.json")
        self.trainer = BrainTrainer(self.brain)
        self.mutator = PayloadMutator()
        self.chain_builder = ExploitChainBuilder()
        self.sessions = SessionManager()
        self._tasks: dict[str, asyncio.Task[None]] = {}

    async def initialize(self) -> None:
        await self.store.initialize()
        self.brain.load()

    async def start_scan(self, request: ScanRequest) -> str:
        scope_file = load_scope(request.scope_path)
        scope = ScopeEnforcer(scope_file)

        for target in request.target_urls:
            if not scope.is_allowed(target, "GET"):
                raise ScopeViolation(f"Target not allowed by scope: {target}")

        scan_id = str(uuid4())
        scan = ScanResult(id=scan_id, targets=request.target_urls, status=ScanStatus.PENDING)
        await self.sessions.create(scan)
        await self.store.upsert_scan(scan)

        task = asyncio.create_task(self._run_scan(scan_id, request, scope, scope_file.credentials.enabled))
        self._tasks[scan_id] = task
        return scan_id

    async def _run_scan(
        self,
        scan_id: str,
        request: ScanRequest,
        scope: ScopeEnforcer,
        credentials_enabled: bool,
    ) -> None:
        await self.sessions.set_status(scan_id, ScanStatus.RUNNING)
        await self.store.set_status(scan_id, ScanStatus.RUNNING)
        await self.sessions.publish(scan_id, "status", "Scan started", {})

        try:
            selected_plugins = self.plugin_registry.select(request.plugin_names)
            ordered_names = self.brain.choose_plugin_order([plugin.name for plugin in selected_plugins])
            ordered_plugins = [self.plugin_registry.get(name) for name in ordered_names]
            active_scanner = ActiveScanner(ordered_plugins, concurrency=self.config.scan_concurrency)

            endpoints: list[DiscoveredEndpoint] = []
            requests_made = 0
            for target_url in request.target_urls:
                target_scope = scope.assert_allowed(target_url)
                target_scope.max_depth = request.max_depth or target_scope.max_depth
                credentials = load_target_credentials(load_scope(request.scope_path).credentials) if credentials_enabled else None
                crawl_report = await self.crawler.crawl(target_scope, scope, credentials)
                requests_made += crawl_report.request_count
                endpoints.extend(crawl_report.endpoints)
                await self.sessions.publish(
                    scan_id,
                    "crawl",
                    f"Crawled {target_scope.base_url}",
                    {
                        "endpoints": len(crawl_report.endpoints),
                        "technologies": crawl_report.technologies,
                    },
                )

            deduped: dict[tuple[str, str], DiscoveredEndpoint] = {}
            for endpoint in endpoints:
                key = (endpoint.url, endpoint.method)
                deduped[key] = endpoint

            unique_endpoints = list(deduped.values())[: load_scope(request.scope_path).safety.max_requests]
            await self.sessions.add_endpoints(scan_id, unique_endpoints)

            findings = await active_scanner.scan_endpoints(scan_id, unique_endpoints)

            unique_findings_map: dict[str, Finding] = {}
            for finding in findings:
                unique_findings_map[finding.identity_key()] = finding

            unique_findings = list(unique_findings_map.values())
            await self.sessions.add_findings(scan_id, unique_findings)

            for finding in unique_findings:
                await self.store.add_finding(finding)
                await self.vector_store.add(
                    finding.id,
                    f"{finding.title} {finding.evidence} {finding.url}",
                    {"severity": finding.severity.value, "plugin": finding.plugin},
                )

            reward = calculate_reward(
                unique_findings=len(unique_findings),
                suspicious_behaviors=max(0, len(unique_findings) // 2),
                new_endpoints=len(unique_endpoints),
                waf_bypasses=0,
                duplicate_findings=max(0, len(findings) - len(unique_findings)),
                timeouts_or_errors=0,
                out_of_scope_attempts=0,
            )

            plugin_hits: dict[str, int] = {}
            for finding in unique_findings:
                plugin_hits[finding.plugin] = plugin_hits.get(finding.plugin, 0) + 1
            total_hits = sum(plugin_hits.values()) or 1
            for plugin_name, hits in plugin_hits.items():
                self.brain.update(plugin_name, reward * (hits / total_hits), {"scan_id": scan_id})
            self.brain.save()

            chains = self.chain_builder.build(unique_findings)
            await self.sessions.publish(
                scan_id,
                "chains",
                "Chain analysis completed",
                {"count": len(chains), "chains": [chain.name for chain in chains]},
            )

            scan = await self.sessions.get(scan_id)
            if scan is None:
                return
            scan.status = ScanStatus.COMPLETED
            scan.metrics.requests_made = requests_made
            scan.metrics.reward_score = reward
            scan.metrics.completed_at = datetime.now(UTC)
            await self.store.upsert_scan(scan)
            await self.store.set_status(scan_id, ScanStatus.COMPLETED)
            await self.sessions.publish(
                scan_id,
                "complete",
                "Scan completed",
                {
                    "findings": len(unique_findings),
                    "reward": reward,
                },
            )
        except Exception as exc:
            message = str(exc)
            self.logger.exception("scan_failed", scan_id=scan_id, error=message)
            await self.sessions.add_error(scan_id, message)
            await self.sessions.set_status(scan_id, ScanStatus.FAILED)
            await self.store.set_status(scan_id, ScanStatus.FAILED, error=message)
            await self.sessions.publish(scan_id, "error", "Scan failed", {"error": message})

    async def get_scan(self, scan_id: str) -> ScanResult | None:
        local = await self.sessions.get(scan_id)
        if local is not None:
            return local
        return await self.store.get_scan(scan_id)

    async def list_findings(self, scan_id: str | None = None) -> list[Finding]:
        return await self.store.list_findings(scan_id)

    async def cancel_scan(self, scan_id: str) -> bool:
        task = self._tasks.get(scan_id)
        if task is None:
            return False
        task.cancel()
        await self.sessions.set_status(scan_id, ScanStatus.CANCELED)
        await self.store.set_status(scan_id, ScanStatus.CANCELED)
        await self.sessions.publish(scan_id, "status", "Scan canceled", {})
        return True

    async def subscribe(self, scan_id: str) -> asyncio.Queue[ScanEvent]:
        return await self.sessions.subscribe(scan_id)

    def brain_status(self) -> dict[str, object]:
        return self.trainer.status()
