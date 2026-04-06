"""Main PyQt6 window for Navil desktop operations."""

from __future__ import annotations

import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStatusBar,
    QStyle,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from navil.config import load_scope
from navil.gui.theme import ThemeMode, apply_theme, next_mode
from navil.gui.worker import ScanWorker
from navil.knowledge.models import ScanRequest, ScanResult
from navil.reporting.generator import ReportGenerator


class NavilMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.theme_mode: ThemeMode = "dark"
        self.worker: ScanWorker | None = None
        self.current_scan: dict[str, Any] | None = None
        self.current_scan_id: str | None = None
        self._last_status: str | None = None

        self.setWindowTitle("Navil | Adaptive Security Desktop")
        self.resize(1440, 900)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(14, 14, 14, 14)
        main.setSpacing(12)

        hero = QFrame()
        hero.setObjectName("Hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(18, 16, 18, 16)

        title = QLabel("Navil Command Surface")
        title.setObjectName("Title")
        subtitle = QLabel(
            "PyQt6-native dashboard inspired by axene.io aesthetics."
            " Scope-first scanning, adaptive learning, and CLI parity."
        )
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)

        hero_actions = QHBoxLayout()
        hero_actions.setSpacing(8)
        hero_actions.addStretch(1)

        self.theme_button = self._create_outline_button("Light Mode")
        self.theme_button.clicked.connect(self._toggle_theme)

        self.fullscreen_button = self._create_outline_button("Fullscreen")
        self.fullscreen_button.clicked.connect(self._toggle_fullscreen)

        self.clear_events_button = self._create_outline_button("Clear Events")
        self.clear_events_button.clicked.connect(self._clear_events)

        hero_actions.addWidget(self.theme_button)
        hero_actions.addWidget(self.fullscreen_button)
        hero_actions.addWidget(self.clear_events_button)

        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addLayout(hero_actions)
        main.addWidget(hero)

        upper_row = QHBoxLayout()
        upper_row.setSpacing(12)
        upper_row.addWidget(self._build_control_card(), 5)
        upper_row.addWidget(self._build_metrics_card(), 4)
        main.addLayout(upper_row)

        lower_row = QHBoxLayout()
        lower_row.setSpacing(12)

        self.event_feed = QListWidget()
        self.event_feed.setMinimumWidth(340)
        self.event_feed.setAlternatingRowColors(True)

        findings_card = self._build_findings_card()
        output_card = self._build_output_card()

        right_column = QVBoxLayout()
        right_column.setSpacing(12)
        right_column.addWidget(findings_card, 6)
        right_column.addWidget(output_card, 4)

        lower_row.addWidget(self.event_feed, 3)
        lower_row.addLayout(right_column, 7)
        main.addLayout(lower_row)

        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self._set_status_message("Ready")
        self._refresh_action_icons()

    def _build_control_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)

        heading = QLabel("Scan Controls")
        heading.setObjectName("Title")
        heading.setStyleSheet("font-size: 17px;")
        layout.addWidget(heading)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.targets_input = QLineEdit("https://example.com")
        self.scope_input = QLineEdit(".navil-scope.yml")
        self.plugins_input = QLineEdit("headers,cors,info_disclosure")

        self.depth_input = QSpinBox()
        self.depth_input.setMinimum(1)
        self.depth_input.setMaximum(10)
        self.depth_input.setValue(3)

        self.report_format = QComboBox()
        self.report_format.addItems(["html", "json", "md", "pdf"])

        form.addRow("Targets", self.targets_input)
        form.addRow("Scope", self.scope_input)
        form.addRow("Plugins", self.plugins_input)
        form.addRow("Depth", self.depth_input)
        form.addRow("Report", self.report_format)

        layout.addLayout(form)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.start_button = QPushButton("Start Scan")
        self.start_button.setObjectName("PrimaryButton")
        self.start_button.clicked.connect(self._start_scan)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("OutlineIconButton")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_scan)

        self.export_button = self._create_outline_button("Export Report")
        self.export_button.clicked.connect(self._export_report)

        self.scope_button = self._create_outline_button("Validate Scope")
        self.scope_button.clicked.connect(self._validate_scope)

        self.copy_summary_button = self._create_outline_button("Copy Summary")
        self.copy_summary_button.clicked.connect(self._copy_summary)

        row.addWidget(self.start_button)
        row.addWidget(self.cancel_button)
        row.addWidget(self.export_button)
        row.addWidget(self.scope_button)
        row.addWidget(self.copy_summary_button)
        layout.addLayout(row)

        return card

    def _create_outline_button(self, label: str) -> QPushButton:
        button = QPushButton(label)
        button.setObjectName("OutlineIconButton")
        return button

    def _build_findings_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        findings_title = QLabel("Findings")
        findings_title.setObjectName("Title")
        findings_title.setStyleSheet("font-size: 16px;")

        title_row.addWidget(findings_title)
        title_row.addStretch(1)

        self.copy_selected_button = self._create_outline_button("Copy Selected")
        self.copy_selected_button.setEnabled(False)
        self.copy_selected_button.clicked.connect(self._copy_selected_finding)

        self.copy_findings_button = self._create_outline_button("Copy All")
        self.copy_findings_button.clicked.connect(self._copy_all_findings)

        self.save_findings_button = self._create_outline_button("Save Findings")
        self.save_findings_button.clicked.connect(self._save_findings)

        title_row.addWidget(self.copy_selected_button)
        title_row.addWidget(self.copy_findings_button)
        title_row.addWidget(self.save_findings_button)

        self.findings_table = QTableWidget(0, 5)
        self.findings_table.setHorizontalHeaderLabels(["Severity", "Plugin", "Title", "URL", "Confidence"])
        header = self.findings_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(True)
        self.findings_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.findings_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.findings_table.itemSelectionChanged.connect(self._on_finding_selected)

        layout.addLayout(title_row)
        layout.addWidget(self.findings_table)
        return card

    def _build_output_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        output_title = QLabel("Output")
        output_title.setObjectName("Title")
        output_title.setStyleSheet("font-size: 16px;")
        title_row.addWidget(output_title)
        title_row.addStretch(1)

        self.copy_output_button = self._create_outline_button("Copy Output")
        self.copy_output_button.clicked.connect(self._copy_output)

        self.download_output_button = self._create_outline_button("Download Output")
        self.download_output_button.clicked.connect(self._download_output)

        self.clear_output_button = self._create_outline_button("Clear Output")
        self.clear_output_button.clicked.connect(self._clear_output)

        title_row.addWidget(self.copy_output_button)
        title_row.addWidget(self.download_output_button)
        title_row.addWidget(self.clear_output_button)

        self.output_view = QPlainTextEdit()
        self.output_view.setReadOnly(True)
        self.output_view.setPlaceholderText("Scan output, summary, and selected finding details appear here.")

        layout.addLayout(title_row)
        layout.addWidget(self.output_view)
        return card

    def _build_metrics_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        layout = QVBoxLayout(card)

        heading = QLabel("Live Metrics")
        heading.setObjectName("Title")
        heading.setStyleSheet("font-size: 17px;")
        layout.addWidget(heading)

        grid = QHBoxLayout()
        grid.setSpacing(10)

        self.status_value = self._metric_tile(grid, "Status", "idle")
        self.scan_id_value = self._metric_tile(grid, "Scan ID", "-")
        self.endpoints_value = self._metric_tile(grid, "Endpoints", "0")
        self.findings_value = self._metric_tile(grid, "Findings", "0")
        self.critical_value = self._metric_tile(grid, "Critical+High", "0")
        self.reward_value = self._metric_tile(grid, "Reward", "0.0")

        layout.addLayout(grid)
        return card

    def _metric_tile(self, parent: QHBoxLayout, label: str, value: str) -> QLabel:
        tile = QFrame()
        tile.setObjectName("MetricCard")
        tile_layout = QVBoxLayout(tile)

        key = QLabel(label)
        key.setObjectName("MetricLabel")
        val = QLabel(value)
        val.setObjectName("MetricValue")

        tile_layout.addWidget(key)
        tile_layout.addWidget(val)
        parent.addWidget(tile)
        return val

    def _set_standard_icon(self, button: QPushButton, icon: QStyle.StandardPixmap) -> None:
        style = self.style()
        if style is not None:
            button.setIcon(style.standardIcon(icon))

    def _refresh_action_icons(self) -> None:
        self._set_standard_icon(self.start_button, QStyle.StandardPixmap.SP_MediaPlay)
        self._set_standard_icon(self.cancel_button, QStyle.StandardPixmap.SP_BrowserStop)
        self._set_standard_icon(self.export_button, QStyle.StandardPixmap.SP_DialogSaveButton)
        self._set_standard_icon(self.scope_button, QStyle.StandardPixmap.SP_DialogApplyButton)
        self._set_standard_icon(self.copy_summary_button, QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self._set_standard_icon(self.theme_button, QStyle.StandardPixmap.SP_BrowserReload)
        self._set_standard_icon(self.clear_events_button, QStyle.StandardPixmap.SP_DialogDiscardButton)
        self._set_standard_icon(self.copy_selected_button, QStyle.StandardPixmap.SP_DialogOpenButton)
        self._set_standard_icon(self.copy_findings_button, QStyle.StandardPixmap.SP_FileDialogListView)
        self._set_standard_icon(self.save_findings_button, QStyle.StandardPixmap.SP_DialogSaveButton)
        self._set_standard_icon(self.copy_output_button, QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self._set_standard_icon(self.download_output_button, QStyle.StandardPixmap.SP_DialogSaveButton)
        self._set_standard_icon(self.clear_output_button, QStyle.StandardPixmap.SP_DialogDiscardButton)

        if self.isFullScreen():
            self.fullscreen_button.setText("Windowed")
            self._set_standard_icon(self.fullscreen_button, QStyle.StandardPixmap.SP_TitleBarNormalButton)
        else:
            self.fullscreen_button.setText("Fullscreen")
            self._set_standard_icon(self.fullscreen_button, QStyle.StandardPixmap.SP_TitleBarMaxButton)

        if self.theme_mode == "dark":
            self.theme_button.setText("Light Mode")
        else:
            self.theme_button.setText("Dark Mode")

    def _start_scan(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            self._show_info("Scan in progress", "A scan is already running.")
            return

        targets = [item.strip() for item in self.targets_input.text().split(",") if item.strip()]
        if not targets:
            self._show_error("Input error", "Please provide at least one target URL.")
            return

        plugins = [item.strip() for item in self.plugins_input.text().split(",") if item.strip()]
        request = ScanRequest(
            target_urls=targets,
            scope_path=self.scope_input.text().strip() or ".navil-scope.yml",
            plugin_names=plugins or None,
            max_depth=int(self.depth_input.value()),
        )

        self.findings_table.setRowCount(0)
        self.event_feed.clear()
        self.output_view.clear()
        self.current_scan = None
        self.current_scan_id = None
        self._last_status = None

        self.worker = ScanWorker(request)
        self.worker.progress.connect(self._on_progress)
        self.worker.completed.connect(self._on_completed)
        self.worker.failed.connect(self._on_failed)

        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self._set_status_message("Scan running")

        self._append_event("Scan scheduled", "info")
        self.worker.start()

    def _cancel_scan(self) -> None:
        if self.worker is None:
            return
        self.worker.request_cancel()
        self._append_event("Cancellation requested", "warn")

    def _on_progress(self, payload: dict[str, Any]) -> None:
        event_type = str(payload.get("type", "event"))
        if event_type == "started":
            self.current_scan_id = str(payload.get("scan_id", "-"))
            self.scan_id_value.setText(self.current_scan_id)
            self.status_value.setText("RUNNING")
            self._append_event(f"Scan started: {self.current_scan_id}", "info")
            return

        scan = payload.get("scan")
        if not isinstance(scan, dict):
            return

        self.current_scan = scan
        self._render_scan(scan)

    def _on_completed(self, scan: dict[str, Any]) -> None:
        self.current_scan = scan
        self._render_scan(scan)
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._set_status_message("Scan finished")
        self._append_event("Scan completed", "ok")

    def _on_failed(self, message: str) -> None:
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self._set_status_message("Scan failed")
        self._append_event(f"Scan failed: {message}", "error")
        self.output_view.setPlainText(f"Scan failed\n\n{message}")
        self._show_error("Scan failed", message)

    def _render_scan(self, scan: dict[str, Any]) -> None:
        scan_id = str(scan.get("id", "-"))
        status = str(scan.get("status", "-"))
        metrics = scan.get("metrics") or {}
        findings = scan.get("findings") or []

        self.scan_id_value.setText(scan_id)
        self.status_value.setText(status)
        self.endpoints_value.setText(str(metrics.get("discovered_endpoints", 0)))
        self.findings_value.setText(str(len(findings)))
        reward = metrics.get("reward_score", 0.0)
        self.reward_value.setText(f"{float(reward):.2f}")

        critical_or_high = 0
        for finding in findings:
            severity = str(finding.get("severity", "")).upper()
            if severity in {"CRITICAL", "HIGH"}:
                critical_or_high += 1
        self.critical_value.setText(str(critical_or_high))

        if status != self._last_status:
            self._append_event(f"Status update: {status}", "info")
            self._last_status = status

        self.findings_table.setRowCount(len(findings))
        for row, finding in enumerate(findings):
            severity = str(finding.get("severity", "INFO"))
            plugin = str(finding.get("plugin", "-"))
            title = str(finding.get("title", "-"))
            url = str(finding.get("url", "-"))
            confidence = f"{float(finding.get('confidence', 0.0)):.2f}"

            row_values = [severity, plugin, title, url, confidence]
            for col, value in enumerate(row_values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setForeground(self._severity_color(severity))
                self.findings_table.setItem(row, col, item)

        self.output_view.setPlainText(self._scan_summary_text(scan))
        self.copy_selected_button.setEnabled(self.findings_table.currentRow() >= 0)

    def _severity_color(self, severity: str) -> QBrush:
        if severity == "CRITICAL":
            return QBrush(QColor("#ff4d5e"))
        if severity == "HIGH":
            return QBrush(QColor("#ffa347"))
        if severity == "MEDIUM":
            return QBrush(QColor("#ffd15a"))
        if severity == "LOW":
            return QBrush(QColor("#44dd9f"))
        return QBrush(QColor("#58d4ff"))

    def _export_report(self) -> None:
        if self.current_scan is None:
            self._show_info("No scan", "Run a scan before exporting a report.")
            return

        fmt = self.report_format.currentText()
        suggestion = f"navil-report-{self.current_scan.get('id', 'scan')}.{fmt}"
        file_path, _ = QFileDialog.getSaveFileName(self, "Export report", suggestion)
        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() != f".{fmt}":
            path = path.with_suffix(f".{fmt}")

        try:
            scan_model = ScanResult.model_validate(self.current_scan)

            async def _generate() -> Path:
                return await ReportGenerator().generate(scan_model, fmt=fmt, output_path=path)

            output = asyncio.run(_generate())
        except Exception as exc:
            self._show_error("Export failed", str(exc))
            return

        self._append_event(f"Report exported: {output}", "ok")
        self._set_status_message(f"Report exported to {output}")

    def _validate_scope(self) -> None:
        path = self.scope_input.text().strip() or ".navil-scope.yml"
        try:
            scope = load_scope(path)
        except Exception as exc:
            self._show_error("Scope invalid", str(exc))
            return

        self._append_event(f"Scope validated: {scope.project}", "ok")
        self._show_info("Scope valid", f"Project: {scope.project}\nTargets: {len(scope.targets)}")

    def _append_event(self, message: str, level: str) -> None:
        stamp = datetime.now(UTC).astimezone().strftime("%H:%M:%S")
        self.event_feed.insertItem(0, f"[{stamp}] [{level.upper()}] {message}")

    def _show_error(self, title: str, text: str) -> None:
        QMessageBox.critical(self, title, text)

    def _show_info(self, title: str, text: str) -> None:
        QMessageBox.information(self, title, text)

    def _set_status_message(self, message: str) -> None:
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(message)

    def _toggle_theme(self) -> None:
        app_instance = QApplication.instance()
        if not isinstance(app_instance, QApplication):
            return

        self.theme_mode = apply_theme(app_instance, mode=next_mode(self.theme_mode))
        self._refresh_action_icons()
        self._append_event(f"Theme switched: {self.theme_mode}", "info")

    def _toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
        self._refresh_action_icons()

    def _clear_events(self) -> None:
        self.event_feed.clear()
        self._set_status_message("Events cleared")

    def _scan_summary_text(self, scan: dict[str, Any]) -> str:
        findings = scan.get("findings") or []
        metrics = scan.get("metrics") or {}
        high_impact = 0
        for finding in findings:
            severity = str(finding.get("severity", "")).upper()
            if severity in {"CRITICAL", "HIGH"}:
                high_impact += 1

        lines = [
            f"Scan ID: {scan.get('id', '-')}",
            f"Status: {scan.get('status', '-')}",
            f"Targets: {', '.join(scan.get('target_urls', [])) or '-'}",
            f"Endpoints discovered: {metrics.get('discovered_endpoints', 0)}",
            f"Total findings: {len(findings)}",
            f"Critical/High findings: {high_impact}",
            f"Reward score: {float(metrics.get('reward_score', 0.0)):.2f}",
        ]
        return "\n".join(lines)

    def _selected_finding(self) -> dict[str, Any] | None:
        if self.current_scan is None:
            return None
        findings = self.current_scan.get("findings") or []
        if not isinstance(findings, list):
            return None

        row = self.findings_table.currentRow()
        if row < 0 or row >= len(findings):
            return None
        finding = findings[row]
        if isinstance(finding, dict):
            return finding
        return None

    def _finding_text(self, finding: dict[str, Any]) -> str:
        return json.dumps(finding, indent=2, sort_keys=True)

    def _copy_to_clipboard(self, text: str, success_message: str) -> None:
        if not text.strip():
            self._show_info("Nothing to copy", "No content is available to copy.")
            return

        app_instance = QApplication.instance()
        if not isinstance(app_instance, QApplication):
            return

        clipboard = app_instance.clipboard()
        if clipboard is None:
            self._show_error("Clipboard unavailable", "Clipboard service is not available.")
            return

        clipboard.setText(text)
        self._set_status_message(success_message)

    def _copy_summary(self) -> None:
        if self.current_scan is None:
            self._show_info("No scan", "Run a scan before copying a summary.")
            return
        self._copy_to_clipboard(self._scan_summary_text(self.current_scan), "Summary copied")

    def _on_finding_selected(self) -> None:
        finding = self._selected_finding()
        has_selection = finding is not None
        self.copy_selected_button.setEnabled(has_selection)
        if finding is None:
            return
        self.output_view.setPlainText(self._finding_text(finding))

    def _copy_selected_finding(self) -> None:
        finding = self._selected_finding()
        if finding is None:
            self._show_info("No selection", "Select a finding row first.")
            return
        self._copy_to_clipboard(self._finding_text(finding), "Selected finding copied")

    def _copy_all_findings(self) -> None:
        if self.current_scan is None:
            self._show_info("No scan", "Run a scan before copying findings.")
            return
        findings = self.current_scan.get("findings") or []
        if not findings:
            self._show_info("No findings", "There are no findings to copy.")
            return
        self._copy_to_clipboard(json.dumps(findings, indent=2, sort_keys=True), "All findings copied")

    def _save_findings(self) -> None:
        if self.current_scan is None:
            self._show_info("No scan", "Run a scan before saving findings.")
            return

        findings = self.current_scan.get("findings") or []
        if not findings:
            self._show_info("No findings", "There are no findings to save.")
            return

        suggestion = f"navil-findings-{self.current_scan.get('id', 'scan')}.json"
        file_path, _ = QFileDialog.getSaveFileName(self, "Save findings", suggestion)
        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        try:
            path.write_text(json.dumps(findings, indent=2, sort_keys=True), encoding="utf-8")
        except Exception as exc:
            self._show_error("Save failed", str(exc))
            return

        self._set_status_message(f"Findings saved to {path}")

    def _copy_output(self) -> None:
        self._copy_to_clipboard(self.output_view.toPlainText(), "Output copied")

    def _download_output(self) -> None:
        output_text = self.output_view.toPlainText().strip()
        if not output_text:
            self._show_info("No output", "There is no output content to download.")
            return

        suggestion = f"navil-output-{self.current_scan.get('id', 'scan') if self.current_scan else 'latest'}.txt"
        file_path, _ = QFileDialog.getSaveFileName(self, "Download output", suggestion)
        if not file_path:
            return

        path = Path(file_path)
        if path.suffix.lower() != ".txt":
            path = path.with_suffix(".txt")

        try:
            path.write_text(self.output_view.toPlainText(), encoding="utf-8")
        except Exception as exc:
            self._show_error("Download failed", str(exc))
            return

        self._set_status_message(f"Output saved to {path}")

    def _clear_output(self) -> None:
        self.output_view.clear()
        self._set_status_message("Output cleared")
