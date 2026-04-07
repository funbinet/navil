"""Interactive menu-driven shell for Navil CLI workflows."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from queue import Empty, Queue
from threading import Lock, Thread
from typing import Any
from uuid import uuid4

from rich import box
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from navil.cli.local_audit import LocalAuditResult, audit_path, default_system_excludes
from navil.constants import DATA_DIR
from navil.core.engine import NavilEngine
from navil.knowledge.models import ScanRequest, ScanResult
from navil.reporting.generator import ReportGenerator

PANEL_BORDER = "grey54"
TITLE_STYLE = "bold cyan"
ACCENT_STYLE = "bright_cyan"
SUCCESS_STYLE = "bold green"
WARNING_STYLE = "bold yellow"
ERROR_STYLE = "bold red"
# Approximate 12cm panel width on common terminal fonts.
PANEL_WIDTH_CHARS = 68
MAX_HISTORY_ITEMS = 300


@dataclass(slots=True)
class BackgroundJob:
    id: str
    kind: str
    summary: str
    status: str = "RUNNING"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    output: dict[str, Any] | None = None
    error: str | None = None


class BackgroundJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, BackgroundJob] = {}
        self._futures: dict[str, Future[dict[str, Any]]] = {}
        self._lock = Lock()
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="navil-menu")

    def submit(self, kind: str, summary: str, runner: Callable[[], dict[str, Any]]) -> str:
        job_id = uuid4().hex[:8]
        job = BackgroundJob(id=job_id, kind=kind, summary=summary)

        with self._lock:
            self._jobs[job_id] = job

        future = self._executor.submit(runner)
        with self._lock:
            self._futures[job_id] = future
        future.add_done_callback(lambda done: self._finalize(job_id, done))
        return job_id

    def _finalize(self, job_id: str, future: Future[dict[str, Any]]) -> None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return

            job.finished_at = datetime.now(UTC)
            try:
                job.output = future.result()
                job.status = "COMPLETED"
            except Exception as exc:
                job.error = str(exc)
                job.status = "FAILED"

    def list_jobs(self) -> list[BackgroundJob]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda item: item.created_at, reverse=True)

    def get_job(self, job_id: str) -> BackgroundJob | None:
        with self._lock:
            return self._jobs.get(job_id)

    def clear_finished(self) -> int:
        removed = 0
        with self._lock:
            finished = [job_id for job_id, job in self._jobs.items() if job.status in {"COMPLETED", "FAILED"}]
            for job_id in finished:
                self._jobs.pop(job_id, None)
                self._futures.pop(job_id, None)
                removed += 1
        return removed

    def shutdown(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


def _short(value: str, limit: int = 26) -> str:
    if len(value) <= limit:
        return value
    return f"{value[: limit - 3]}..."


def _summarize_scan(scan: ScanResult) -> dict[str, Any]:
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
    for finding in scan.findings:
        key = finding.severity.value
        severity_counts[key] = severity_counts.get(key, 0) + 1

    return {
        "scan_id": scan.id,
        "status": scan.status.value,
        "targets": scan.targets,
        "findings_total": len(scan.findings),
        "reward_score": round(scan.metrics.reward_score, 3),
        "requests_made": scan.metrics.requests_made,
        "severity_breakdown": severity_counts,
        "errors": scan.errors,
    }


def run_web_scan(
    request: ScanRequest,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        engine = NavilEngine()
        if progress_callback:
            progress_callback("Bootstrapping engine")
        await engine.initialize()

        scan_id = await engine.start_scan(request)
        if progress_callback:
            progress_callback(f"Scan started {scan_id}")

        last_status = ""
        while True:
            result = await engine.get_scan(scan_id)
            if result is None:
                if progress_callback:
                    progress_callback("Waiting for scan registration")
                await asyncio.sleep(1.0)
                continue

            status = result.status.value
            if status != last_status and progress_callback:
                progress_callback(f"Status {status}")
                last_status = status

            if status in {"COMPLETED", "FAILED", "CANCELED"}:
                return _summarize_scan(result)

            await asyncio.sleep(1.0)

    return asyncio.run(_run())


def run_recent_scans(limit: int = 20) -> list[dict[str, Any]]:
    async def _run() -> list[dict[str, Any]]:
        engine = NavilEngine()
        await engine.initialize()
        return await engine.store.list_scans(limit=limit)

    return asyncio.run(_run())


def run_report(scan_id: str, fmt: str, output_path: str | None) -> dict[str, Any]:
    async def _run() -> dict[str, Any]:
        engine = NavilEngine()
        await engine.initialize()
        scan = await engine.get_scan(scan_id)
        if scan is None:
            raise ValueError(f"Unknown scan id: {scan_id}")

        generator = ReportGenerator()
        path = await generator.generate(scan, fmt=fmt, output_path=Path(output_path) if output_path else None)
        return {
            "scan_id": scan_id,
            "format": fmt,
            "output": str(path),
        }

    return asyncio.run(_run())


def run_brain_status() -> dict[str, Any]:
    engine = NavilEngine()
    return engine.brain_status()


def run_brain_train(episodes: int) -> dict[str, Any]:
    engine = NavilEngine()
    rewards = {
        "headers": min(episodes / 100, 3.0),
        "cors": min(episodes / 120, 2.5),
        "info_disclosure": min(episodes / 80, 3.5),
    }
    engine.trainer.online_update(rewards, source="menu-shell")
    engine.brain.save()
    return {
        "episodes": episodes,
        "reward_updates": rewards,
    }


def run_path_audit(
    root: str,
    max_depth: int,
    max_entries: int,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    result = audit_path(
        root,
        max_depth=max_depth,
        max_entries=max_entries,
        progress_callback=progress_callback,
    )
    return _local_audit_to_output(result)


def run_system_audit(
    max_depth: int,
    max_entries: int,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, Any]:
    result = audit_path(
        "/",
        max_depth=max_depth,
        max_entries=max_entries,
        exclude_paths=default_system_excludes(),
        progress_callback=progress_callback,
    )
    return _local_audit_to_output(result)


def _local_audit_to_output(result: LocalAuditResult) -> dict[str, Any]:
    return {
        "summary": result.summary(),
        "extension_counts": result.extension_counts,
        "findings": [
            {
                "severity": item.severity,
                "category": item.category,
                "path": item.path,
                "detail": item.detail,
            }
            for item in result.findings[:25]
        ],
    }


class NavilMenuShell:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console(width=PANEL_WIDTH_CHARS)
        self.jobs = BackgroundJobManager()
        self._state_path = DATA_DIR / "menu_state.json"
        self._state = self._load_state()
        self._last_scan_profile: dict[str, Any] | None = None

    def run(self) -> None:
        self._print_welcome()
        try:
            while True:
                choice = self._prompt_main_menu()
                if choice == "1":
                    self._web_scan_menu()
                elif choice == "2":
                    self._path_audit_menu()
                elif choice == "3":
                    self._system_audit_menu()
                elif choice == "4":
                    self._report_menu()
                elif choice == "5":
                    self._brain_menu()
                elif choice == "6":
                    self._jobs_menu()
                elif choice == "7":
                    self._quick_commands_panel()
                elif choice == "8":
                    self._history_presets_menu()
                elif choice == "0":
                    self._print_panel("Session Closed", "[bold green]Goodbye from Navil menu shell.[/bold green]")
                    return
        except KeyboardInterrupt:
            self.console.print()
            self._print_panel("Session Interrupted", "[bold yellow]Interrupted by user.[/bold yellow]")
        finally:
            self.jobs.shutdown()

    def _panel(self, title: str, body: str | Table) -> Panel:
        return Panel(
            body,
            title=f"[{TITLE_STYLE}]{title}[/{TITLE_STYLE}]",
            border_style=PANEL_BORDER,
            box=box.ROUNDED,
            width=PANEL_WIDTH_CHARS,
            expand=True,
        )

    def _print_panel(self, title: str, body: str) -> None:
        self.console.print(self._panel(title, body))
        self.console.print()

    def _print_data_panel(self, title: str, data: dict[str, Any]) -> None:
        pretty = json.dumps(data, indent=2, default=str)
        self._print_panel(title, f"[white]{pretty}[/white]")

    def _print_welcome(self) -> None:
        body = (
            "[bold cyan][center]Menu-driven operations enabled[/center][/bold cyan]\n"
            "[dim][center]Use menus/submenus and provide simple inputs.[/center][/dim]"
        )
        self._print_panel("NAVIL CLI COMMAND CENTER", body)

    def _show_action_help(
        self,
        action_name: str,
        purpose: str,
        expected_inputs: list[str],
        outcome: str,
    ) -> bool:
        expected_lines = "\n".join(f"[white]- {item}[/white]" for item in expected_inputs)
        if not expected_lines:
            expected_lines = "[dim]- none[/dim]"

        body = (
            "[bold cyan]Purpose[/bold cyan]\n"
            f"[white]{purpose}[/white]\n\n"
            "[bold cyan]Expected Inputs[/bold cyan]\n"
            f"{expected_lines}\n\n"
            "[bold cyan]What It Does[/bold cyan]\n"
            f"[white]{outcome}[/white]"
        )
        self._print_panel(f"{action_name} Help", body)
        proceed = self._ask_choice(action_name, "Proceed [y/n]", {"y": "yes", "n": "no"})
        return proceed == "y"

    def _record_history(self, field: str, action: str, value: str) -> None:
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "field": field,
            "action": action,
            "value": value,
        }
        history = self._state.get("history", [])
        history.append(entry)
        self._state["history"] = history[-MAX_HISTORY_ITEMS:]
        self._save_state()

    def _load_state(self) -> dict[str, Any]:
        default_state: dict[str, Any] = {"history": [], "presets": {}, "active_preset": None}
        try:
            if not self._state_path.exists():
                return default_state
            parsed = json.loads(self._state_path.read_text(encoding="utf-8"))
            if not isinstance(parsed, dict):
                return default_state
            if "history" not in parsed or not isinstance(parsed["history"], list):
                parsed["history"] = []
            if "presets" not in parsed or not isinstance(parsed["presets"], dict):
                parsed["presets"] = {}
            if "active_preset" not in parsed:
                parsed["active_preset"] = None
            return parsed
        except (OSError, json.JSONDecodeError):
            return default_state

    def _save_state(self) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _ask(self, field: str, action: str, *, allow_empty: bool = False) -> str:
        while True:
            self.console.print()
            prompt = Text("navil ", style="bold cyan")
            prompt.append(f"[{field}]> {action}: ", style="bold cyan")
            value = self.console.input(prompt).strip()
            self._record_history(field, action, value)
            if value or allow_empty:
                return value
            self._print_panel("Input Required", f"[{WARNING_STYLE}]Please provide a value.[/{WARNING_STYLE}]")

    def _ask_choice(self, field: str, action: str, allowed: dict[str, str]) -> str:
        while True:
            value = self._ask(field, action).lower()
            if value in allowed:
                return value
            self._print_panel(
                "Input Error",
                f"[{WARNING_STYLE}]Allowed: {', '.join(allowed.keys())}[/{WARNING_STYLE}]",
            )

    def _ask_int(
        self,
        field: str,
        action: str,
        *,
        min_value: int,
        max_value: int | None = None,
        allow_empty: bool = False,
        empty_value: int | None = None,
    ) -> int | None:
        while True:
            raw = self._ask(field, action, allow_empty=allow_empty)
            if not raw and allow_empty:
                return empty_value
            try:
                value = int(raw)
            except ValueError:
                self._print_panel("Input Error", f"[{ERROR_STYLE}]Enter a numeric value.[/{ERROR_STYLE}]")
                continue

            if value < min_value:
                self._print_panel("Input Error", f"[{ERROR_STYLE}]Minimum is {min_value}.[/{ERROR_STYLE}]")
                continue
            if max_value is not None and value > max_value:
                self._print_panel("Input Error", f"[{ERROR_STYLE}]Maximum is {max_value}.[/{ERROR_STYLE}]")
                continue
            return value

    def _stream_panel(self, title: str, frame: str, steps: list[str]) -> Panel:
        lines = [f"[{ACCENT_STYLE}]{frame} running...[/]", "[dim]step stream[/dim]"]
        if not steps:
            lines.append("[dim]initializing...[/dim]")
        else:
            for item in steps[-8:]:
                lines.append(f"[white]{item}[/white]")
        body = "\n".join(lines)
        return self._panel(title, body)

    def _run_with_stream(
        self,
        title: str,
        runner: Callable[[Callable[[str], None]], dict[str, Any]],
    ) -> dict[str, Any]:
        messages: Queue[str] = Queue()
        result_holder: dict[str, dict[str, Any]] = {}
        error_holder: dict[str, str] = {}

        def _emit(message: str) -> None:
            stamp = datetime.now().astimezone().strftime("%H:%M:%S")
            messages.put(f"{stamp} | {message}")

        def _worker() -> None:
            try:
                result_holder["value"] = runner(_emit)
            except Exception as exc:
                error_holder["value"] = str(exc)

        worker = Thread(target=_worker, daemon=True)
        worker.start()

        frames = ["-", "\\", "|", "/"]
        frame_idx = 0
        step_log: list[str] = []

        with Live(self._stream_panel(title, frames[0], step_log), console=self.console, refresh_per_second=10) as live:
            while worker.is_alive() or not messages.empty():
                try:
                    while True:
                        step_log.append(messages.get_nowait())
                except Empty:
                    pass
                step_log = step_log[-8:]
                frame = frames[frame_idx % len(frames)]
                frame_idx += 1
                live.update(self._stream_panel(title, frame, step_log))
                time.sleep(0.12)

        worker.join()

        if "value" in error_holder:
            raise RuntimeError(error_holder["value"])

        return result_holder.get("value", {})

    def _prompt_main_menu(self) -> str:
        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Opt", style="bold yellow", width=5)
        table.add_column("Action", style="bold cyan", width=23)
        table.add_row("1", "Web Scan")
        table.add_row("2", "Path Audit")
        table.add_row("3", "System Audit")
        table.add_row("4", "Reports")
        table.add_row("5", "Brain Ops")
        table.add_row("6", "Background Jobs")
        table.add_row("7", "Quick Commands")
        table.add_row("8", "History + Presets")
        table.add_row("0", "Exit")
        self.console.print(self._panel("Main Menu", table))
        return self._ask_choice(
            "menu",
            "Option",
            {
                "1": "web",
                "2": "path",
                "3": "system",
                "4": "report",
                "5": "brain",
                "6": "jobs",
                "7": "quick",
                "8": "state",
                "0": "exit",
            },
        )

    def _active_preset(self) -> tuple[str, dict[str, Any]] | None:
        name = self._state.get("active_preset")
        presets = self._state.get("presets", {})
        if isinstance(name, str) and isinstance(presets, dict):
            preset = presets.get(name)
            if isinstance(preset, dict):
                return name, preset
        return None

    def _collect_scan_request(self) -> ScanRequest | None:
        self._print_panel(
            "Web Scan Input",
            "[white]- Targets comma URLs[/white]\n"
            "[white]- Scope file path[/white]\n"
            "[white]- Plugins comma list (optional)[/white]\n"
            "[white]- Max Depth (optional)[/white]",
        )

        active_preset = self._active_preset()
        if active_preset is not None:
            preset_name, preset_values = active_preset
            use_preset = self._ask_choice(
                "Web Scan",
                f"Use Active Preset '{preset_name}' [y/n]",
                {"y": "yes", "n": "no"},
            )
            if use_preset == "y":
                request = ScanRequest(
                    target_urls=list(preset_values.get("targets", [])),
                    scope_path=str(preset_values.get("scope", ".navil-scope.yml")),
                    plugin_names=list(preset_values.get("plugins", [])) or None,
                    max_depth=preset_values.get("depth"),
                )
                self._last_scan_profile = {
                    "targets": request.target_urls,
                    "scope": request.scope_path,
                    "plugins": request.plugin_names or [],
                    "depth": request.max_depth,
                }
                return request

        targets_raw = self._ask("Web Scan", "Targets comma URLs")
        targets = [item.strip() for item in targets_raw.split(",") if item.strip()]
        if not targets:
            self._print_panel("Input Error", f"[{ERROR_STYLE}]No valid targets.[/{ERROR_STYLE}]")
            return None

        scope_path = self._ask("Web Scan", "Scope Path")
        scope_candidate = Path(scope_path).expanduser()
        if scope_candidate.is_dir():
            self._print_panel(
                "Input Error",
                f"[{ERROR_STYLE}]Scope path must be a scope file, not a directory.[/{ERROR_STYLE}]",
            )
            return None
        plugins_raw = self._ask("Web Scan", "Plugins comma list (blank=auto)", allow_empty=True)
        plugins = [item.strip() for item in plugins_raw.split(",") if item.strip()] if plugins_raw else []

        depth = self._ask_int(
            "Web Scan",
            "Max Depth (blank=scope)",
            min_value=1,
            max_value=10,
            allow_empty=True,
            empty_value=None,
        )

        request = ScanRequest(
            target_urls=targets,
            scope_path=scope_path,
            plugin_names=plugins or None,
            max_depth=depth,
        )

        self._last_scan_profile = {
            "targets": targets,
            "scope": scope_path,
            "plugins": plugins,
            "depth": depth,
        }
        return request

    def _web_scan_menu(self) -> None:
        while True:
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("Opt", style="bold yellow", width=5)
            table.add_column("Action", style="bold cyan", width=23)
            table.add_row("1", "Run Foreground")
            table.add_row("2", "Queue Background")
            table.add_row("0", "Back")
            self.console.print(self._panel("Web Scan Menu", table))
            choice = self._ask_choice("Web Scan", "Option", {"1": "run", "2": "queue", "0": "back"})
            if choice == "0":
                return

            if choice == "1":
                proceed = self._show_action_help(
                    "Web Scan Foreground",
                    "Run a scope-controlled scan and stream progress live in this terminal.",
                    [
                        "Targets comma URLs",
                        "Scope file path",
                        "Plugins comma list (optional)",
                        "Max Depth (optional)",
                    ],
                    "Executes immediately and prints scan results when complete.",
                )
            else:
                proceed = self._show_action_help(
                    "Web Scan Background",
                    "Queue a scope-controlled scan while you continue working in menus.",
                    [
                        "Targets comma URLs",
                        "Scope file path",
                        "Plugins comma list (optional)",
                        "Max Depth (optional)",
                    ],
                    "Adds a background job; results are inspected from Background Jobs menu.",
                )

            if not proceed:
                continue

            request = self._collect_scan_request()
            if request is None:
                continue

            if choice == "1":
                self._run_scan_foreground(request)
            else:
                self._run_scan_background(request)

    def _run_scan_foreground(self, request: ScanRequest) -> None:
        try:
            result = self._run_with_stream(
                "Web Scan Stream",
                lambda callback: run_web_scan(request, progress_callback=callback),
            )
        except Exception as exc:
            self._print_panel("Scan Error", f"[{ERROR_STYLE}]{exc}[/{ERROR_STYLE}]")
            return

        self._print_data_panel("Web Scan Result", result)

    def _run_scan_background(self, request: ScanRequest) -> None:
        job_id = self.jobs.submit(
            "web-scan",
            f"targets={','.join(request.target_urls)}",
            lambda: run_web_scan(request),
        )
        self._print_panel("Background Job", f"[{SUCCESS_STYLE}]Queued job {job_id}.[/{SUCCESS_STYLE}]")

    def _path_audit_menu(self) -> None:
        while True:
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("Opt", style="bold yellow", width=5)
            table.add_column("Action", style="bold cyan", width=23)
            table.add_row("1", "Run Foreground")
            table.add_row("2", "Queue Background")
            table.add_row("0", "Back")
            self.console.print(self._panel("Path Audit Menu", table))
            choice = self._ask_choice("Path Audit", "Option", {"1": "run", "2": "queue", "0": "back"})
            if choice == "0":
                return

            if choice == "1":
                proceed = self._show_action_help(
                    "Path Audit Foreground",
                    "Inspect a folder/file tree and stream local audit progress in real time.",
                    ["Path file or folder", "Max Depth", "Max Entries"],
                    "Runs now and prints audit summary, extension counts, and findings.",
                )
            else:
                proceed = self._show_action_help(
                    "Path Audit Background",
                    "Queue a local path audit and continue using other menu actions.",
                    ["Path file or folder", "Max Depth", "Max Entries"],
                    "Creates a background job; review results in Background Jobs menu.",
                )

            if not proceed:
                continue

            root = self._ask("Path Audit", "Path File or Folder")
            max_depth_value = self._ask_int("Path Audit", "Max Depth", min_value=1, max_value=32)
            max_entries_value = self._ask_int("Path Audit", "Max Entries", min_value=100, max_value=1_000_000)
            assert isinstance(max_depth_value, int)
            assert isinstance(max_entries_value, int)

            if choice == "1":
                self._run_path_audit_foreground(root, max_depth_value, max_entries_value)
            else:
                self._run_path_audit_background(root, max_depth_value, max_entries_value)

    def _run_path_audit_foreground(self, root: str, max_depth: int, max_entries: int) -> None:
        try:
            result = self._run_with_stream(
                "Path Audit Stream",
                lambda callback: run_path_audit(root, max_depth, max_entries, progress_callback=callback),
            )
        except Exception as exc:
            self._print_panel("Path Audit Error", f"[{ERROR_STYLE}]{exc}[/{ERROR_STYLE}]")
            return

        self._print_data_panel("Path Audit Result", result)

    def _run_path_audit_background(self, root: str, max_depth: int, max_entries: int) -> None:
        job_id = self.jobs.submit(
            "path-audit",
            f"root={root}",
            lambda: run_path_audit(root, max_depth, max_entries),
        )
        self._print_panel("Background Job", f"[{SUCCESS_STYLE}]Queued job {job_id}.[/{SUCCESS_STYLE}]")

    def _system_audit_menu(self) -> None:
        proceed = self._show_action_help(
            "System Audit",
            "Inspect the system filesystem from root while skipping volatile pseudo-filesystems.",
            ["Max Depth", "Max Entries", "Execution mode foreground(f)/background(b)"],
            "Builds an audit summary and findings for local filesystem hygiene checks.",
        )
        if not proceed:
            return

        max_depth_value = self._ask_int("System Audit", "Max Depth", min_value=1, max_value=32)
        max_entries_value = self._ask_int("System Audit", "Max Entries", min_value=100, max_value=2_000_000)
        mode = self._ask_choice(
            "System Audit",
            "Execution Mode [foreground(f)/background(b)]",
            {"f": "foreground", "b": "background"},
        )
        assert isinstance(max_depth_value, int)
        assert isinstance(max_entries_value, int)

        if mode == "f":
            self._run_system_audit_foreground(max_depth_value, max_entries_value)
            return

        job_id = self.jobs.submit(
            "system-audit",
            f"root=/ depth={max_depth_value}",
            lambda: run_system_audit(max_depth_value, max_entries_value),
        )
        self._print_panel("Background Job", f"[{SUCCESS_STYLE}]Queued job {job_id}.[/{SUCCESS_STYLE}]")

    def _run_system_audit_foreground(self, max_depth: int, max_entries: int) -> None:
        try:
            result = self._run_with_stream(
                "System Audit Stream",
                lambda callback: run_system_audit(max_depth, max_entries, progress_callback=callback),
            )
        except Exception as exc:
            self._print_panel("System Audit Error", f"[{ERROR_STYLE}]{exc}[/{ERROR_STYLE}]")
            return

        self._print_data_panel("System Audit Result", result)

    def _choose_report_target_from_recent(self) -> str | None:
        self._print_panel("Recent Scans", "[dim]Loading recent scan IDs...[/dim]")
        try:
            scans = run_recent_scans(limit=20)
        except Exception as exc:
            self._print_panel("Recent Scans", f"[{ERROR_STYLE}]{exc}[/{ERROR_STYLE}]")
            return None

        if not scans:
            self._print_panel("Recent Scans", "[dim]No scans found.[/dim]")
            return None

        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("No", style="bold yellow", width=4)
        table.add_column("Scan ID", style="bold cyan", width=14)
        table.add_column("Status", style="white", width=10)
        for idx, scan in enumerate(scans, start=1):
            table.add_row(str(idx), _short(str(scan.get("id", "-")), 12), str(scan.get("status", "-")))

        self.console.print(self._panel("Recent Scan IDs", table))
        pick = self._ask_int("Reports", "Select Recent Scan Number", min_value=1, max_value=len(scans))
        assert isinstance(pick, int)
        return str(scans[pick - 1]["id"])

    def _report_menu(self) -> None:
        while True:
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("Opt", style="bold yellow", width=5)
            table.add_column("Action", style="bold cyan", width=23)
            table.add_row("1", "Run by Scan ID")
            table.add_row("2", "Queue by Scan ID")
            table.add_row("3", "Run from Recent IDs")
            table.add_row("4", "Queue from Recent IDs")
            table.add_row("0", "Back")
            self.console.print(self._panel("Report Menu", table))
            choice = self._ask_choice(
                "Reports",
                "Option",
                {"1": "run", "2": "queue", "3": "recent-run", "4": "recent-queue", "0": "back"},
            )
            if choice == "0":
                return

            help_lookup = {
                "1": (
                    "Report Foreground",
                    "Generate a report now from a specific scan ID.",
                    ["Scan ID", "Format html/json/md/pdf", "Output path (optional)"],
                    "Runs report generation immediately and prints the output file path.",
                ),
                "2": (
                    "Report Background",
                    "Queue report generation from a specific scan ID.",
                    ["Scan ID", "Format html/json/md/pdf", "Output path (optional)"],
                    "Creates a background report job for later inspection.",
                ),
                "3": (
                    "Report From Recent IDs",
                    "Generate a report now by selecting a recent saved scan.",
                    ["Recent scan number", "Format html/json/md/pdf", "Output path (optional)"],
                    "Loads recent scans, then generates report immediately.",
                ),
                "4": (
                    "Report Background From Recent IDs",
                    "Queue report generation by selecting a recent saved scan.",
                    ["Recent scan number", "Format html/json/md/pdf", "Output path (optional)"],
                    "Loads recent scans and queues report in background jobs.",
                ),
            }

            help_data = help_lookup[choice]
            if not self._show_action_help(
                help_data[0],
                help_data[1],
                help_data[2],
                help_data[3],
            ):
                continue

            if choice in {"1", "2"}:
                scan_id = self._ask("Reports", "Scan ID")
            else:
                chosen = self._choose_report_target_from_recent()
                if chosen is None:
                    continue
                scan_id = chosen

            fmt = self._ask_choice(
                "Reports",
                "Format [html(h)/json(j)/md(m)/pdf(p)]",
                {"h": "html", "j": "json", "m": "md", "p": "pdf"},
            )
            fmt_map = {"h": "html", "j": "json", "m": "md", "p": "pdf"}
            output_path = self._ask("Reports", "Output Path (blank=auto)", allow_empty=True)
            output_value = output_path if output_path else None

            if choice in {"1", "3"}:
                self._run_report_foreground(scan_id, fmt_map[fmt], output_value)
            else:
                self._run_report_background(scan_id, fmt_map[fmt], output_value)

    def _run_report_foreground(self, scan_id: str, fmt: str, output_path: str | None) -> None:
        def _runner(callback: Callable[[str], None]) -> dict[str, Any]:
            callback("Loading scan")
            result = run_report(scan_id, fmt, output_path)
            callback("Report generated")
            return result

        try:
            result = self._run_with_stream("Report Stream", _runner)
        except Exception as exc:
            self._print_panel("Report Error", f"[{ERROR_STYLE}]{exc}[/{ERROR_STYLE}]")
            return

        self._print_data_panel("Report Result", result)

    def _run_report_background(self, scan_id: str, fmt: str, output_path: str | None) -> None:
        job_id = self.jobs.submit(
            "report",
            f"scan={_short(scan_id, 12)} fmt={fmt}",
            lambda: run_report(scan_id, fmt, output_path),
        )
        self._print_panel("Background Job", f"[{SUCCESS_STYLE}]Queued job {job_id}.[/{SUCCESS_STYLE}]")

    def _brain_menu(self) -> None:
        while True:
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("Opt", style="bold yellow", width=5)
            table.add_column("Action", style="bold cyan", width=23)
            table.add_row("1", "Status")
            table.add_row("2", "Train Foreground")
            table.add_row("3", "Train Background")
            table.add_row("0", "Back")
            self.console.print(self._panel("Brain Menu", table))
            choice = self._ask_choice("Brain", "Option", {"1": "status", "2": "train", "3": "queue", "0": "back"})
            if choice == "0":
                return

            if choice == "1":
                proceed = self._show_action_help(
                    "Brain Status",
                    "Show the current adaptive-brain runtime snapshot.",
                    [],
                    "Prints brain status values for quick diagnostics.",
                )
                if not proceed:
                    continue
                snapshot = run_brain_status()
                self._print_data_panel("Brain Status", snapshot)
                continue

            if choice == "2":
                proceed = self._show_action_help(
                    "Brain Train Foreground",
                    "Train the adaptive brain now and stream status in this terminal.",
                    ["Training Episodes"],
                    "Applies reward updates, saves brain state, and shows result payload.",
                )
            else:
                proceed = self._show_action_help(
                    "Brain Train Background",
                    "Queue adaptive-brain training and continue with other operations.",
                    ["Training Episodes"],
                    "Queues a background training job and stores result for inspection.",
                )

            if not proceed:
                continue

            episodes_input = self._ask_int("Brain", "Training Episodes", min_value=1, max_value=10000)
            if episodes_input is None:
                continue
            episodes_value = episodes_input

            if choice == "2":
                def _runner(
                    callback: Callable[[str], None],
                    episodes_for_job: int = episodes_value,
                ) -> dict[str, Any]:
                    callback("Preparing reward updates")
                    result = run_brain_train(episodes_for_job)
                    callback("Training state saved")
                    return result

                result = self._run_with_stream("Brain Training Stream", _runner)
                self._print_data_panel("Brain Training Result", result)
            else:
                def _job_runner(episodes_for_job: int = episodes_value) -> dict[str, Any]:
                    return run_brain_train(episodes_for_job)

                job_id = self.jobs.submit(
                    "brain-train",
                    f"episodes={episodes_value}",
                    _job_runner,
                )
                self._print_panel("Background Job", f"[{SUCCESS_STYLE}]Queued job {job_id}.[/{SUCCESS_STYLE}]")

    def _jobs_menu(self) -> None:
        while True:
            jobs = self.jobs.list_jobs()
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("ID", style="bold cyan", width=10)
            table.add_column("Kind", style="white", width=11)
            table.add_column("State", style="bold", width=10)
            for job in jobs:
                state_style = SUCCESS_STYLE if job.status == "COMPLETED" else WARNING_STYLE
                if job.status == "FAILED":
                    state_style = ERROR_STYLE
                table.add_row(job.id, _short(job.kind, 10), f"[{state_style}]{job.status}[/{state_style}]")

            if not jobs:
                self._print_panel("Background Jobs", "[dim]No jobs available.[/dim]")
            else:
                self.console.print(self._panel("Background Jobs", table))

            action = self._ask_choice(
                "Jobs",
                "Action [inspect(i)/clear(c)/refresh(r)/back(b)]",
                {"i": "inspect", "c": "clear", "r": "refresh", "b": "back"},
            )
            if action == "b":
                return
            if action == "r":
                continue
            if action == "c":
                removed = self.jobs.clear_finished()
                self._print_panel("Jobs Cleanup", f"[{SUCCESS_STYLE}]Removed {removed} finished jobs.[/{SUCCESS_STYLE}]")
                continue

            job_id = self._ask("Jobs", "Job ID")
            selected = self.jobs.get_job(job_id)
            if selected is None:
                self._print_panel("Jobs", f"[{ERROR_STYLE}]Unknown job id {job_id}.[/{ERROR_STYLE}]")
                continue

            if selected.status == "FAILED":
                self._print_panel(
                    f"Job {selected.id}",
                    f"[{ERROR_STYLE}]FAILED[/]\n[white]{selected.error or 'No error detail'}[/white]",
                )
                continue

            if selected.status == "RUNNING":
                self._print_panel(
                    f"Job {selected.id}",
                    f"[{WARNING_STYLE}]RUNNING[/]\n[white]{selected.summary}[/white]",
                )
                continue

            self._print_data_panel(f"Job {selected.id} Output", selected.output or {"status": selected.status})

    def _history_presets_menu(self) -> None:
        while True:
            table = Table(box=box.SIMPLE_HEAVY)
            table.add_column("Opt", style="bold yellow", width=5)
            table.add_column("Action", style="bold cyan", width=23)
            table.add_row("1", "View History")
            table.add_row("2", "Save Last Scan Preset")
            table.add_row("3", "List Presets")
            table.add_row("4", "Activate Preset")
            table.add_row("5", "Delete Preset")
            table.add_row("0", "Back")
            self.console.print(self._panel("History + Presets", table))
            choice = self._ask_choice(
                "State",
                "Option",
                {"1": "history", "2": "save", "3": "list", "4": "activate", "5": "delete", "0": "back"},
            )
            if choice == "0":
                return
            if choice == "1":
                self._show_history()
            elif choice == "2":
                self._save_last_scan_preset()
            elif choice == "3":
                self._show_presets()
            elif choice == "4":
                self._activate_preset()
            elif choice == "5":
                self._delete_preset()

    def _show_history(self) -> None:
        history = self._state.get("history", [])
        if not history:
            self._print_panel("History", "[dim]No history entries yet.[/dim]")
            return

        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Time", style="dim", width=9)
        table.add_column("Field", style="bold cyan", width=11)
        table.add_column("Value", style="white", width=30)
        for item in history[-20:]:
            raw_ts = str(item.get("ts", ""))
            time_part = _short(raw_ts.split("T")[-1].replace("+00:00", ""), 8)
            field = _short(str(item.get("field", "-")), 10)
            action = _short(str(item.get("action", "-")), 10)
            value = _short(str(item.get("value", "")), 16)
            table.add_row(time_part, field, f"{action}={value}")
        self.console.print(self._panel("Command History", table))

    def _save_last_scan_preset(self) -> None:
        if self._last_scan_profile is None:
            self._print_panel("Presets", "[dim]No recent scan profile to save.[/dim]")
            return

        name = self._ask("Presets", "Preset Name")
        presets = self._state.get("presets", {})
        if not isinstance(presets, dict):
            presets = {}
        presets[name] = self._last_scan_profile
        self._state["presets"] = presets
        self._state["active_preset"] = name
        self._save_state()
        self._print_panel("Presets", f"[{SUCCESS_STYLE}]Saved preset '{name}'.[/{SUCCESS_STYLE}]")

    def _show_presets(self) -> None:
        presets = self._state.get("presets", {})
        if not isinstance(presets, dict) or not presets:
            self._print_panel("Presets", "[dim]No presets saved.[/dim]")
            return

        active = self._state.get("active_preset")
        table = Table(box=box.SIMPLE_HEAVY)
        table.add_column("Name", style="bold cyan", width=16)
        table.add_column("Targets", style="white", width=30)
        for name, value in presets.items():
            targets = value.get("targets", []) if isinstance(value, dict) else []
            target_text = ",".join(targets) if isinstance(targets, list) else "-"
            marker = "*" if name == active else ""
            table.add_row(f"{name}{marker}", _short(target_text, 28))
        self.console.print(self._panel("Saved Presets", table))

    def _activate_preset(self) -> None:
        presets = self._state.get("presets", {})
        if not isinstance(presets, dict) or not presets:
            self._print_panel("Presets", "[dim]No presets available.[/dim]")
            return

        self._show_presets()
        name = self._ask("Presets", "Activate Name")
        if name not in presets:
            self._print_panel("Presets", f"[{ERROR_STYLE}]Preset not found.[/{ERROR_STYLE}]")
            return
        self._state["active_preset"] = name
        self._save_state()
        self._print_panel("Presets", f"[{SUCCESS_STYLE}]Active preset set to '{name}'.[/{SUCCESS_STYLE}]")

    def _delete_preset(self) -> None:
        presets = self._state.get("presets", {})
        if not isinstance(presets, dict) or not presets:
            self._print_panel("Presets", "[dim]No presets available.[/dim]")
            return

        self._show_presets()
        name = self._ask("Presets", "Delete Name")
        if name not in presets:
            self._print_panel("Presets", f"[{ERROR_STYLE}]Preset not found.[/{ERROR_STYLE}]")
            return

        presets.pop(name, None)
        if self._state.get("active_preset") == name:
            self._state["active_preset"] = None
        self._state["presets"] = presets
        self._save_state()
        self._print_panel("Presets", f"[{SUCCESS_STYLE}]Deleted preset '{name}'.[/{SUCCESS_STYLE}]")

    def _quick_commands_panel(self) -> None:
        body = "\n".join(
            [
                "[bold cyan]Quick command mode stays available:[/bold cyan]",
                "[white]- navil scan https://example.com --scope .navil-scope.yml[/white]",
                "[white]- navil report --scan-id <SCAN_ID> --format html[/white]",
                "[white]- navil scope validate .navil-scope.yml[/white]",
                "[white]- navil brain status[/white]",
                "[white]- navil brain train --episodes 200[/white]",
                "[white]- navel (alias)[/white]",
            ]
        )
        self._print_panel("Quick Commands", body)
