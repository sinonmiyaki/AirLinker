"""Run in a separate process: python -m tests is not required."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
from pathlib import Path
from unittest.mock import Mock
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from airlinker.app import Window, SettingsDialog, STYLE
from airlinker.core import Options

app = QApplication([])
app.setStyleSheet(STYLE)
with tempfile.TemporaryDirectory() as directory:
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, directory)
    window = Window(autostart=False)
    window.data_dir = Path(directory)
    window.show()
    app.processEvents()
    assert window.spinner.timer.isActive()
    window.update_state('streaming')
    assert not window.spinner.isVisible()
    assert not window.spinner.timer.isActive()
    window.update_state('ready')
    assert window.spinner.isVisible()
    window.receiver.state = 'ready'
    window.receiver.stop = Mock()
    options = Options(name='Living Room')
    window.apply_settings(options, True, False)
    window.receiver.stop.assert_called_once()
    assert window.pending_restart
    window.start = Mock()
    window.update_state('stopped')
    app.processEvents()
    window.start.assert_called_once()
    window.receiver.state = 'ready'
    window.apply_settings(options, False, False)
    assert not window.pending_restart
    dialog = SettingsDialog(window)
    dialog.show()
    app.processEvents()
    dialog.grab().save('docs/settings-preview.png')
    dialog.name.setText('')
    dialog.apply()
    assert dialog.isVisible()
    dialog.close()
    window.close()
print('UI lifecycle and settings checks passed')
