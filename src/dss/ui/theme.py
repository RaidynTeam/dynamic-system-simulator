"""Explicit light application theme, independent of the Windows color mode."""

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtWidgets import QApplication

from dss.ui.colors import PRIMARY, SUCCESS, WARNING

BACKGROUND = "#F8FAFC"
CARD = "#FFFFFF"
TEXT = "#0F172A"
SECONDARY = "#64748B"
BORDER = "#E2E8F0"
ERROR = "#DC2626"


def apply_light_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    for role, color in (
        (QPalette.ColorRole.Window, BACKGROUND),
        (QPalette.ColorRole.WindowText, TEXT),
        (QPalette.ColorRole.Base, CARD),
        (QPalette.ColorRole.AlternateBase, BACKGROUND),
        (QPalette.ColorRole.Text, TEXT),
        (QPalette.ColorRole.Button, CARD),
        (QPalette.ColorRole.ButtonText, TEXT),
        (QPalette.ColorRole.Highlight, PRIMARY),
        (QPalette.ColorRole.HighlightedText, CARD),
        (QPalette.ColorRole.ToolTipBase, CARD),
        (QPalette.ColorRole.ToolTipText, TEXT),
        (QPalette.ColorRole.Accent, PRIMARY),
        (QPalette.ColorRole.PlaceholderText, SECONDARY),
    ):
        palette.setColor(role, QColor(color))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(SECONDARY))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(SECONDARY))
    app.setPalette(palette)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(f"""
        QWidget {{ color: {TEXT}; font-size: 13px; }}
        QMainWindow, QWidget#page {{ background: {BACKGROUND}; }}
        QFrame#control_card, QFrame#plot_card {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}
        QLabel {{ background: transparent; border: none; }}
        QLabel#title {{ font-size: 24px; font-weight: 600; }}
        QLabel[role="section"] {{ font-size: 16px; font-weight: 600; }}
        QLabel[role="secondary"] {{ color: {SECONDARY}; }}
        QLabel#simulation_status {{ color: {SECONDARY}; }}
        QLabel#simulation_status[state="error"] {{ color: {ERROR}; }}
        QLabel#simulation_status[state="notice"] {{ color: {WARNING}; }}
        QLabel#status_indicator {{ color: {SUCCESS}; font-size: 17px; }}
        QLabel#status_indicator[state="error"] {{ color: {ERROR}; }}
        QLabel#status_indicator[state="notice"] {{ color: {WARNING}; }}
        QPushButton {{ background: #F1F5F9; border: 1px solid transparent; border-radius: 6px; padding: 6px 10px; }}
        QPushButton:hover {{ background: #E2E8F0; }}
        QPushButton:focus, QLineEdit:focus {{ border: 1px solid {PRIMARY}; }}
        QPushButton#run_simulation, QPushButton[case="true"]:checked {{ background: {PRIMARY}; color: white; font-weight: 600; }}
        QPushButton#run_simulation:hover {{ background: #1D4ED8; }}
        QPushButton[case="true"] {{ padding: 6px 4px; }}
        QPushButton[role="step"] {{ background: transparent; padding: 2px 6px; }}
        QPushButton[role="step"]:hover {{ background: #EFF6FF; }}
        QLineEdit {{ background: {CARD}; border: 1px solid {BORDER}; border-radius: 5px; padding: 4px 8px; selection-background-color: {PRIMARY}; }}
        QSlider {{ background: transparent; }}
        QSlider::groove:horizontal {{ height: 5px; background: #CBD5E1; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {PRIMARY}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: {PRIMARY}; border: 2px solid {CARD}; width: 10px; margin: -5px 0; border-radius: 7px; }}
        QSlider::handle:horizontal:focus {{ border-color: #93C5FD; }}
        QCheckBox {{ background: transparent; spacing: 5px; }}
        QCheckBox::indicator {{ width: 11px; height: 11px; border: 1px solid #94A3B8; border-radius: 3px; background: {CARD}; }}
        QCheckBox::indicator:checked {{ background: {PRIMARY}; border-color: {PRIMARY}; }}
        QFrame#divider {{ background: {BORDER}; max-height: 1px; border: none; }}
        QToolTip {{ background: {CARD}; color: {TEXT}; border: 1px solid {BORDER}; padding: 5px; }}
    """)
    app.setProperty("dss_light_theme", True)
