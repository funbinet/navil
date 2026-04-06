"""Axene-inspired desktop theme tokens and stylesheet for PyQt6."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

ThemeMode = Literal["dark", "light"]


@dataclass(frozen=True)
class ThemeTokens:
    name: ThemeMode
    window: str
    text: str
    text_muted: str
    base: str
    alt_base: str
    card: str
    metric_card: str
    border: str
    border_soft: str
    hero_grad_start: str
    hero_grad_end: str
    primary: str
    primary_hover: str
    primary_text: str
    icon_button_hover: str
    icon_button_pressed: str
    highlight: str
    highlight_text: str
    status_bg: str


DARK_THEME = ThemeTokens(
    name="dark",
    window="#070f1d",
    text="#d9e9f5",
    text_muted="#9fc0d9",
    base="#091727",
    alt_base="#112743",
    card="#0f2034",
    metric_card="#112743",
    border="#2b4f73",
    border_soft="#2d4f72",
    hero_grad_start="#0c1f34",
    hero_grad_end="#12395d",
    primary="#1ec7a3",
    primary_hover="#31dbb7",
    primary_text="#021019",
    icon_button_hover="#112642",
    icon_button_pressed="#0d2034",
    highlight="#1ec7a3",
    highlight_text="#04131f",
    status_bg="#081120",
)

LIGHT_THEME = ThemeTokens(
    name="light",
    window="#f4f8fc",
    text="#122436",
    text_muted="#3f5f7a",
    base="#ffffff",
    alt_base="#edf3fa",
    card="#ffffff",
    metric_card="#eef5fc",
    border="#a9c1d8",
    border_soft="#b6cadc",
    hero_grad_start="#d9ecff",
    hero_grad_end="#b7ddff",
    primary="#0ea47f",
    primary_hover="#17bc91",
    primary_text="#f7fffd",
    icon_button_hover="#e7f0fa",
    icon_button_pressed="#dce8f5",
    highlight="#0ea47f",
    highlight_text="#ffffff",
    status_bg="#e9f2fb",
)


def _stylesheet(theme: ThemeTokens) -> str:
    return f"""
QMainWindow {{
    background-color: {theme.window};
}}
QWidget {{
    color: {theme.text};
    selection-background-color: {theme.highlight};
    selection-color: {theme.highlight_text};
}}
QFrame#Hero {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {theme.hero_grad_start}, stop:1 {theme.hero_grad_end});
    border: 1px solid {theme.border};
    border-radius: 14px;
}}
QFrame#Card {{
    background-color: {theme.card};
    border: 1px solid {theme.border};
    border-radius: 12px;
}}
QFrame#MetricCard {{
    background-color: {theme.metric_card};
    border: 1px solid {theme.border};
    border-radius: 12px;
}}
QPushButton#PrimaryButton {{
    background-color: {theme.primary};
    color: {theme.primary_text};
    border: 0;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 700;
}}
QPushButton#PrimaryButton:hover {{
    background-color: {theme.primary_hover};
}}
QPushButton#GhostButton {{
    background-color: {theme.base};
    color: {theme.text};
    border: 1px solid {theme.border};
    border-radius: 10px;
    padding: 9px 14px;
}}
QPushButton#GhostButton:hover {{
    border-color: {theme.border_soft};
    background-color: {theme.alt_base};
}}
QPushButton#OutlineIconButton {{
    background: transparent;
    color: {theme.text};
    border: 1px solid {theme.border};
    border-radius: 8px;
    padding: 7px 10px;
    font-weight: 600;
}}
QPushButton#OutlineIconButton:hover {{
    background-color: {theme.icon_button_hover};
    border-color: {theme.border_soft};
}}
QPushButton#OutlineIconButton:pressed {{
    background-color: {theme.icon_button_pressed};
}}
QLineEdit, QSpinBox, QComboBox, QListWidget, QTableWidget, QPlainTextEdit {{
    background-color: {theme.base};
    border: 1px solid {theme.border_soft};
    border-radius: 8px;
    padding: 6px;
}}
QHeaderView::section {{
    background-color: {theme.alt_base};
    color: {theme.text};
    border: 0;
    padding: 8px;
    font-weight: 600;
}}
QTableWidget {{
    gridline-color: {theme.border_soft};
}}
QLabel#Title {{
    font-size: 24px;
    font-weight: 700;
    color: {theme.text};
}}
QLabel#Subtitle {{
    color: {theme.text_muted};
    font-size: 12px;
}}
QLabel#MetricLabel {{
    color: {theme.text_muted};
    font-size: 11px;
}}
QLabel#MetricValue {{
    font-size: 22px;
    font-weight: 700;
    color: {theme.text};
}}
QStatusBar {{
    background-color: {theme.status_bg};
    color: {theme.text_muted};
}}
"""


def _tokens(mode: ThemeMode) -> ThemeTokens:
    return DARK_THEME if mode == "dark" else LIGHT_THEME


def apply_theme(app: QApplication, mode: ThemeMode = "dark") -> ThemeMode:
    theme = _tokens(mode)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(theme.window))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.Base, QColor(theme.base))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme.alt_base))
    palette.setColor(QPalette.ColorRole.Text, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.Button, QColor(theme.card))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme.text))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(theme.highlight))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme.highlight_text))
    app.setPalette(palette)

    font = QFont("Poppins")
    font.setPointSize(10)
    app.setFont(font)
    app.setStyleSheet(_stylesheet(theme))
    return theme.name


def next_mode(mode: ThemeMode) -> ThemeMode:
    return "light" if mode == "dark" else "dark"
