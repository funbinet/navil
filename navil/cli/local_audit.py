"""Local filesystem and system audit helpers for CLI workflows."""

from __future__ import annotations

import os
import stat
from collections import Counter, deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(slots=True)
class LocalAuditFinding:
    severity: str
    category: str
    path: str
    detail: str


@dataclass(slots=True)
class LocalAuditResult:
    root_path: str
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    files_scanned: int = 0
    directories_scanned: int = 0
    skipped_paths: int = 0
    truncated: bool = False
    extension_counts: dict[str, int] = field(default_factory=dict)
    findings: list[LocalAuditFinding] = field(default_factory=list)

    def summary(self) -> dict[str, str | int | bool]:
        return {
            "root_path": self.root_path,
            "files_scanned": self.files_scanned,
            "directories_scanned": self.directories_scanned,
            "skipped_paths": self.skipped_paths,
            "truncated": self.truncated,
            "high_findings": sum(1 for item in self.findings if item.severity == "HIGH"),
            "medium_findings": sum(1 for item in self.findings if item.severity == "MEDIUM"),
            "low_findings": sum(1 for item in self.findings if item.severity == "LOW"),
        }


def _severity_score(level: str) -> int:
    scores = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "INFO": 3}
    return scores.get(level, 4)


def _add_finding(
    result: LocalAuditResult,
    severity: str,
    category: str,
    path: Path,
    detail: str,
    *,
    max_findings: int,
) -> None:
    if len(result.findings) >= max_findings:
        return
    result.findings.append(
        LocalAuditFinding(
            severity=severity,
            category=category,
            path=str(path),
            detail=detail,
        )
    )


def _is_under_excluded(path: Path, excluded: set[Path]) -> bool:
    for item in excluded:
        if path == item:
            return True
        if item in path.parents:
            return True
    return False


def _inspect_file(
    path: Path,
    result: LocalAuditResult,
    extensions: Counter[str],
    *,
    max_findings: int,
) -> None:
    try:
        file_stat = path.stat(follow_symlinks=False)
    except (OSError, PermissionError):
        result.skipped_paths += 1
        return

    result.files_scanned += 1

    suffix = path.suffix.lower() if path.suffix else "<none>"
    extensions[suffix] += 1

    mode = file_stat.st_mode
    if mode & stat.S_IWOTH:
        _add_finding(
            result,
            "HIGH",
            "world-writable-file",
            path,
            "File is writable by all users.",
            max_findings=max_findings,
        )

    if mode & stat.S_ISUID:
        _add_finding(
            result,
            "HIGH",
            "setuid-file",
            path,
            "File has the setuid bit enabled.",
            max_findings=max_findings,
        )

    if mode & stat.S_ISGID:
        _add_finding(
            result,
            "MEDIUM",
            "setgid-file",
            path,
            "File has the setgid bit enabled.",
            max_findings=max_findings,
        )

    if file_stat.st_size >= 250 * 1024 * 1024:
        _add_finding(
            result,
            "LOW",
            "large-file",
            path,
            f"Large file detected ({file_stat.st_size} bytes).",
            max_findings=max_findings,
        )

    sensitive_names = {
        ".env",
        "id_rsa",
        "id_dsa",
        "id_ed25519",
        ".pypirc",
        "credentials",
    }
    if path.name in sensitive_names and mode & stat.S_IROTH:
        _add_finding(
            result,
            "MEDIUM",
            "sensitive-readable-file",
            path,
            "Sensitive-looking file appears world-readable.",
            max_findings=max_findings,
        )


def audit_path(
    root: str | Path,
    *,
    max_depth: int = 8,
    max_entries: int = 50000,
    max_findings: int = 500,
    exclude_paths: list[str] | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> LocalAuditResult:
    """Audit a file or directory tree for common local security hygiene signals."""
    root_path = Path(root).expanduser().resolve()
    if not root_path.exists():
        raise FileNotFoundError(f"Path not found: {root_path}")

    excluded = {Path(item).expanduser().resolve() for item in (exclude_paths or [])}
    result = LocalAuditResult(root_path=str(root_path))
    extensions: Counter[str] = Counter()

    queue: deque[tuple[Path, int]] = deque([(root_path, 0)])
    inspected_entries = 0

    while queue:
        current, depth = queue.popleft()

        if _is_under_excluded(current, excluded):
            continue

        if current.is_file():
            inspected_entries += 1
            _inspect_file(current, result, extensions, max_findings=max_findings)
            if max_entries and inspected_entries >= max_entries:
                result.truncated = True
                break
            continue

        if not current.is_dir():
            continue

        result.directories_scanned += 1
        if depth >= max_depth:
            continue

        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    entry_path = Path(entry.path)
                    if _is_under_excluded(entry_path, excluded):
                        continue

                    if entry.is_dir(follow_symlinks=False):
                        queue.append((entry_path, depth + 1))
                        continue

                    if entry.is_file(follow_symlinks=False):
                        inspected_entries += 1
                        _inspect_file(entry_path, result, extensions, max_findings=max_findings)

                    if progress_callback and inspected_entries and inspected_entries % 500 == 0:
                        progress_callback(
                            f"Audited {inspected_entries} entries | files={result.files_scanned}"
                        )

                    if max_entries and inspected_entries >= max_entries:
                        result.truncated = True
                        break
        except (OSError, PermissionError):
            result.skipped_paths += 1

        if result.truncated:
            break

    result.extension_counts = dict(extensions.most_common(10))
    result.findings.sort(key=lambda item: (_severity_score(item.severity), item.path))
    result.finished_at = datetime.now(UTC)
    return result


def default_system_excludes() -> list[str]:
    """Return pseudo-filesystem and volatile paths to skip for system audits."""
    return [
        "/proc",
        "/sys",
        "/dev",
        "/run",
        "/tmp",
        "/var/tmp",
    ]
