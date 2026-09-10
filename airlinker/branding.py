"""Shared artwork for native windows and the waiting animation."""
from pathlib import Path
from PySide6.QtGui import QIcon

ASSETS = Path(__file__).resolve().parent / 'assets'

def application_icon():
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        icon.addFile(str(ASSETS / f'icon-{size}.png'))
    return icon
