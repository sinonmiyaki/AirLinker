from pathlib import Path
import os
import sys
from PySide6.QtCore import QObject, QProcess, QProcessEnvironment, QTimer, Signal
from .core import LineDecoder, event


class Receiver(QObject):
    state_changed = Signal(str)
    log = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.finished)
        self.process.errorOccurred.connect(self.error)
        self.state = 'stopped'
        self.stopping = False
        self.failed = False
        self.decoder = LineDecoder()
        self.deadline = QTimer(self)
        self.deadline.setSingleShot(True)
        self.deadline.setInterval(20000)
        self.deadline.timeout.connect(self.timeout)
        self.kill_timer = QTimer(self)
        self.kill_timer.setSingleShot(True)
        self.kill_timer.setInterval(2000)
        self.kill_timer.timeout.connect(self.process.kill)

    def set_state(self, state):
        self.state = state
        self.state_changed.emit(state)

    def start(self, engine: Path, options, data_dir: Path, handle: int):
        if self.process.state() != QProcess.NotRunning:
            return
        args = options.arguments(data_dir / 'receiver.conf', sys.platform == 'win32')
        data_dir.mkdir(parents=True, exist_ok=True)
        # Explicitly ignore a user's unrelated ~/.uxplayrc.
        (data_dir / 'receiver.conf').write_text('', encoding='utf-8')
        self.decoder = LineDecoder()
        self.stopping = self.failed = False
        env = QProcessEnvironment.systemEnvironment()
        runtime = engine.parent.parent
        env.insert('PATH', str(engine.parent) + os.pathsep + env.value('PATH'))
        plugins = runtime / 'lib' / 'gstreamer-1.0'
        if plugins.is_dir():
            env.insert('GST_PLUGIN_PATH_1_0', str(plugins))
            env.insert('GST_PLUGIN_SYSTEM_PATH_1_0', str(plugins))
            env.insert('GST_REGISTRY', str(data_dir / 'gstreamer-registry.bin'))
        scanner = runtime / 'libexec' / 'gstreamer-1.0' / 'gst-plugin-scanner.exe'
        if scanner.is_file():
            env.insert('GST_PLUGIN_SCANNER', str(scanner))
        if sys.platform == 'win32':
            env.insert('AIRLINKER_WINDOW_HANDLE', str(handle))
        self.process.setProcessEnvironment(env)
        self.process.setWorkingDirectory(str(data_dir))
        self.set_state('starting')
        self.log.emit('수신 엔진 시작: ' + str(engine))
        self.process.start(str(engine), args)
        self.deadline.start()

    def read_output(self):
        for line in self.decoder.feed(bytes(self.process.readAllStandardOutput())):
            self.log.emit(line)
            state = event(line)
            if state and not self.stopping and not self.failed:
                # An early renderer IDLE must not masquerade as service readiness.
                if self.state == 'starting' and line != 'AIRLINKER/1 READY':
                    continue
                self.deadline.stop()
                self.set_state(state)

    def timeout(self):
        self.failed = True
        self.log.emit('20초 안에 서비스 등록이 확인되지 않았습니다. 아래 엔진 로그를 확인해 주세요.')
        self.stop()

    def stop(self):
        self.deadline.stop()
        if self.process.state() == QProcess.NotRunning:
            self.set_state('error' if self.failed else 'stopped')
            return
        self.stopping = True
        self.set_state('stopping')
        self.process.terminate()
        self.kill_timer.start()

    def error(self, error):
        if error == QProcess.FailedToStart:
            self.deadline.stop()
            self.failed = True
            self.log.emit('엔진 실행 실패: ' + self.process.errorString())
            self.set_state('error')

    def finished(self, code, status):
        self.deadline.stop()
        self.kill_timer.stop()
        self.read_output()
        unexpected = not self.stopping
        self.log.emit(f'수신 엔진 종료 (코드 {code})')
        self.set_state('error' if self.failed or unexpected else 'stopped')

    def shutdown(self):
        self.deadline.stop()
        self.kill_timer.stop()
        if self.process.state() != QProcess.NotRunning:
            self.stopping = True
            self.process.terminate()
            if not self.process.waitForFinished(1500):
                self.process.kill()
                self.process.waitForFinished(1500)
