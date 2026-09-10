"""Run in a separate process: python -m tests is not required."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from PySide6.QtCore import QSettings, QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from airlinker.app import Window, SettingsDialog, STYLE
from airlinker.core import Options

app = QApplication([])
app.setStyleSheet(STYLE)
with tempfile.TemporaryDirectory() as directory:
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, directory)
    window = Window(autostart=False)
    window.settings = QSettings(str(Path(directory) / 'ui.ini'), QSettings.IniFormat)
    window.options = Options()
    window.data_dir = Path(directory)
    assert not window.windowIcon().isNull()
    assert not window.spinner.mark.isNull()
    window.show()
    app.processEvents()
    assert window.waiting_label.text() == '연결 대기중'
    assert window.waiting_label.isVisible()
    assert window.spinner.timer.isActive()
    window.update_state('streaming')
    assert not window.waiting_label.isVisible()
    assert not window.spinner.isVisible()
    assert not window.spinner.timer.isActive()
    with patch('airlinker.app.QCursor') as cursor, patch('airlinker.app.cursor_over_window', return_value=True):
        cursor.pos.return_value = window.mapToGlobal(QPoint(300, 300))
        window.update_controls()
        QTest.qWait(250)
        assert window.top.height() == 0
        cursor.pos.return_value = window.centralWidget().mapToGlobal(QPoint(window.width() // 2, 4))
        window.update_controls()
        QTest.qWait(250)
        assert window.top.height() == 84
        cursor.pos.return_value = window.settings_button.mapToGlobal(window.settings_button.rect().center())
        window.update_controls()
        assert window.top.expanded
        cursor.pos.return_value = window.mapToGlobal(QPoint(300, 300))
        window.settings_open = True
        window.update_controls()
        assert window.top.expanded
        window.settings_open = False
        window.update_controls()
        QTest.qWait(250)
        assert window.top.height() == 0
    window.update_state('ready')
    assert window.spinner.isVisible()
    QTest.qWait(250)
    assert window.top.height() == 84
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
