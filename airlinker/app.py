import argparse
import sys
from collections import deque
from pathlib import Path
from PySide6.QtCore import Qt, QSettings, QStandardPaths, QTimer, QRectF
from PySide6.QtGui import QColor, QPainter, QPen, QShortcut, QKeySequence
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLineEdit, QComboBox, QCheckBox, QDialog,
    QFormLayout, QDialogButtonBox, QLabel)
from .core import Options, find_engine
from .receiver import Receiver

STYLE = '''
QWidget { background: #000; color: #eee; font-family: "Segoe UI", "Apple SD Gothic Neo"; font-size: 14px; }
QPushButton { background: #202020; border: 1px solid #333; border-radius: 9px; padding: 10px 20px; }
QPushButton:hover { background: #303030; }
QPushButton#settingsPill { border-radius: 22px; }
QDialog { background: #171717; }
QDialog QLabel, QCheckBox { background: transparent; }
QLineEdit, QComboBox { background: #252525; border: 1px solid #393939; border-radius: 7px; padding: 9px; }
QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 16px; height: 16px; border: 1px solid #666; border-radius: 4px; background: #252525; }
QCheckBox::indicator:checked { background: #eee; border-color: #eee; }
QPushButton:disabled { color: #777; }
'''


class Spinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.advance)

    def advance(self):
        self.angle = (self.angle + 6) % 360
        self.update()

    def showEvent(self, event):
        self.timer.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        ring = QRectF(7, 7, 26, 26)
        painter.setPen(QPen(QColor('#262626'), 2.5))
        painter.drawEllipse(ring)
        painter.setPen(QPen(QColor('#dadada'), 2.5, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(ring, -self.angle * 16, 95 * 16)


class SettingsDialog(QDialog):
    def __init__(self, owner):
        super().__init__(owner)
        self.setWindowTitle('미러링 설정')
        self.setFixedWidth(350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(22)
        form = QFormLayout()
        form.setSpacing(16)
        options = owner.options
        self.name = QLineEdit(options.name)
        self.quality = QComboBox()
        self.quality.addItems(['1920x1080', '1280x720'])
        self.quality.setCurrentText(options.resolution)
        self.fps = QComboBox()
        self.fps.addItems(['60', '30'])
        self.fps.setCurrentText(str(options.fps))
        self.audio = QCheckBox()
        self.audio.setChecked(options.audio)
        self.software = QCheckBox()
        self.software.setChecked(options.software_decode)
        self.receive = QCheckBox()
        self.receive.setChecked(owner.enabled)
        self.fullscreen = QCheckBox()
        self.fullscreen.setChecked(owner.isFullScreen())
        for title, widget in [('수신 이름', self.name), ('해상도', self.quality),
                              ('프레임', self.fps), ('소리', self.audio),
                              ('호환성 모드', self.software), ('수신', self.receive),
                              ('전체 화면', self.fullscreen)]:
            form.addRow(title, widget)
        layout.addLayout(form)
        buttons = QDialogButtonBox()
        buttons.addButton('취소', QDialogButtonBox.RejectRole)
        buttons.addButton('적용', QDialogButtonBox.AcceptRole)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.apply)
        layout.addWidget(buttons)

    def apply(self):
        options = Options(self.name.text(), self.quality.currentText(), int(self.fps.currentText()),
                          self.audio.isChecked(), self.software.isChecked())
        try:
            options.validate()
        except ValueError:
            self.name.setStyleSheet('border: 1px solid #dd6666;')
            self.name.setFocus()
            return
        self.parent().apply_settings(options, self.receive.isChecked(), self.fullscreen.isChecked())
        self.accept()


class Window(QMainWindow):
    def __init__(self, autostart=True):
        super().__init__()
        self.setWindowTitle('AirLinker')
        self.resize(1100, 720)
        self.setMinimumSize(500, 360)
        self.settings = QSettings('AirLinker', 'AirLinker')
        self.data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        try:
            self.options = Options(self.settings.value('name', 'AirLinker Windows'),
                self.settings.value('resolution', '1920x1080'), int(self.settings.value('fps', '60')),
                self.settings.value('audio', True, type=bool), self.settings.value('software', False, type=bool))
            self.options.validate()
        except (ValueError, TypeError):
            self.options = Options()
        self.enabled = self.settings.value('enabled', True, type=bool)
        self.pending_restart = False
        self.closing = False
        self.log_lines = deque(maxlen=1500)
        self.receiver = Receiver(self)
        self.receiver.log.connect(self.log_lines.append)
        self.receiver.state_changed.connect(self.update_state)
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Keep controls outside the native video HWND so Direct3D cannot cover them.
        top = QWidget()
        top.setFixedHeight(84)
        bar = QHBoxLayout(top)
        bar.setContentsMargins(24, 20, 24, 20)
        bar.addStretch()
        self.settings_button = QPushButton('미러링 설정')
        self.settings_button.setObjectName('settingsPill')
        self.settings_button.setFixedSize(140, 44)
        self.settings_button.clicked.connect(self.open_settings)
        bar.addWidget(self.settings_button)
        bar.addStretch()
        layout.addWidget(top)
        self.video = QWidget()
        self.video.setAttribute(Qt.WA_NativeWindow)
        self.video.setStyleSheet('background: #000;')
        layout.addWidget(self.video, 1)
        center = QVBoxLayout(self.video)
        center.addStretch()
        self.spinner = Spinner(self.video)
        center.addWidget(self.spinner, 0, Qt.AlignHCenter)
        self.waiting_label = QLabel('연결 대기중', self.video)
        self.waiting_label.setStyleSheet('color: #999;')
        center.addWidget(self.waiting_label, 0, Qt.AlignHCenter)
        center.addStretch()
        # Compensate for the header so loading is centered in the whole client area.
        center.setContentsMargins(0, 0, 0, 84)
        QShortcut(QKeySequence('F11'), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence('Escape'), self, activated=self.showNormal)
        if autostart and self.enabled:
            QTimer.singleShot(200, self.start)

    def open_settings(self):
        SettingsDialog(self).exec()

    def start(self):
        if self.closing or not self.enabled:
            return
        engine = find_engine()
        if engine is None:
            self.log_lines.append('Missing receiver engine: runtime/bin/uxplay.exe')
            return
        try:
            self.receiver.start(engine, self.options, self.data_dir, int(self.video.winId()))
        except (ValueError, OSError) as exc:
            self.log_lines.append(str(exc))

    def apply_settings(self, options, enabled, fullscreen):
        changed = self.options != options
        self.options, self.enabled = options, enabled
        for key, value in [('name', options.name), ('resolution', options.resolution),
                           ('fps', str(options.fps)), ('audio', options.audio),
                           ('software', options.software_decode), ('enabled', enabled)]:
            self.settings.setValue(key, value)
        if fullscreen != self.isFullScreen():
            self.toggle_fullscreen()
        active = self.receiver.state in ('starting', 'ready', 'streaming', 'stopping')
        if active and (changed or not enabled or self.receiver.state == 'stopping'):
            self.pending_restart = enabled
            if self.receiver.state != 'stopping':
                self.receiver.stop()
        elif enabled and not active:
            self.start()

    def update_state(self, state):
        self.spinner.setVisible(state != 'streaming')
        self.waiting_label.setVisible(state != 'streaming')
        self.video.update()
        if state in ('stopped', 'error') and self.pending_restart:
            self.pending_restart = False
            QTimer.singleShot(0, self.start)

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def closeEvent(self, event):
        self.closing = True
        self.pending_restart = False
        self.receiver.shutdown()
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            (self.data_dir / 'AirLinker.log').write_text('\n'.join(self.log_lines), encoding='utf-8')
        except OSError:
            pass
        event.accept()


def main():
    parser = argparse.ArgumentParser(description='AirLinker')
    parser.add_argument('--no-autostart', action='store_true')
    parser.add_argument('--screenshot', type=Path)
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    app.setApplicationName('AirLinker')
    app.setStyle('Fusion')
    app.setStyleSheet(STYLE)
    window = Window(not args.no_autostart and not args.screenshot)
    window.show()
    if args.screenshot:
        def capture():
            window.grab().save(str(args.screenshot.resolve()))
            window.close()
        QTimer.singleShot(600, capture)
    return app.exec()
