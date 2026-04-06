"""Axence-inspired desktop theme tokens and stylesheet for PyQt6."""

from __future__ import annotations

from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import QApplication

STYLE_SHEET = """
QMainWindow {
    background-color: #070f1d;
}
QWidget {
    color: #d9e9f5;
    selection-background-color: #1ec7a3;
    selection-color: #04131f;
}
QFrame#Hero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0c1f34, stop:1 #12395d);
    border: 1px solid #245176;
    border-radius: 14px;
}
QFrame#Card {
    background-color: #0f2034;
    border: 1px solid #2b4f73;
    border-radius: 12px;
}
QFrame#MetricCard {
    background-color: #112743;
    border: 1px solid #305d85;
    border-radius: 12px;
}
QPushButton#PrimaryButton {
    background-color: #1ec7a3;
    color: #021019;
    border: 0;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover {
    background-color: #31dbb7;
}
QPushButton#GhostButton {
    background-color: #0b1a2d;
    color: #d9e9f5;
    border: 1px solid #2f587c;
    border-radius: 10px;
    padding: 9px 14px;
}
QPushButton#GhostButton:hover {
    border-color: #3b6f9a;
    background-color: #112642;
}
QLineEdit, QSpinBox, QComboBox, QListWidget, QTableWidget {
    background-color: #091727;
    border: 1px solid #2d4f72;
    border-radius: 8px;
    padding: 6px;
}
QHeaderView::section {
    background-color: #0f2a46;
    color: #cde5f5;
    border: 0;
    padding: 8px;
    font-weight: 600;
}
QTableWidget {
    gridline-color: #1f3956;
}
QLabel#Title {
    font-size: 24px;
    font-weight: 700;
    color: #ebf6ff;
}
QLabel#Subtitle {
    color: #9fc0d9;
    font-size: 12px;
}
QLabel#MetricLabel {
    color: #9ec2de;
    font-size: 11px;
}
QLabel#MetricValue {
    font-size: 22px;
    font-weight: 700;
    color: #ecf9ff;
}
QStatusBar {
    background-color: #081120;
    color: #9fc2de;
}
"""


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#070f1d"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#d9e9f5"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#091727"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#112743"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#d9e9f5"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#0f2034"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d9e9f5"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#1ec7a3"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#04131f"))
    app.setPalette(palette)

    font = QFont("Poppins")
    font.setPointSize(10)
    app.setFont(font)
    app.setStyleSheet(STYLE_SHEET)
