"""Real desktop pixels, native D3D11 sink, separate process, production bridge.
Run with a Windows desktop (not QT_QPA_PLATFORM=offscreen).
"""
import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QPoint, QSettings, QProcess
from PySide6.QtWidgets import QApplication
from airlinker.app import Window, STYLE

assert sys.platform == 'win32'
os.environ.pop('QT_QPA_PLATFORM', None)
app = QApplication([])
app.setStyleSheet(STYLE)

def until(predicate, description, timeout=15):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        app.processEvents()
        if predicate():
            return
        time.sleep(0.03)
    raise AssertionError(description)

with tempfile.TemporaryDirectory() as directory:
    QSettings.setDefaultFormat(QSettings.IniFormat)
    QSettings.setPath(QSettings.IniFormat, QSettings.UserScope, directory)
    window = Window(autostart=False)
    window.data_dir = Path(directory)
    window.resize(800, 600)
    window.move(40, 40)
    window.show()
    window.raise_()
    app.processEvents()
    helper = Path('runtime/bin/airlinker-video-test.exe').resolve()
    receiver = window.receiver
    def command(value):
        receiver.process.write((value + '\n').encode())
    def color_is(channel):
        point = window.video.mapToGlobal(QPoint(window.video.width() // 2,
                                                window.video.height() // 2))
        # Capture the composited desktop; QWidget.grab misses foreign-process D3D.
        image = window.screen().grabWindow(0, point.x(), point.y(), 1, 1).toImage()
        if image.isNull():
            return False
        color = image.pixelColor(0, 0)
        rgb = [color.red(), color.green(), color.blue()]
        return rgb[channel] > 200 and all(v < 50 for i, v in enumerate(rgb) if i != channel)
    try:
        receiver.start(helper, window.options, Path(directory), int(window.video.winId()))
        until(lambda: receiver.state == 'ready', 'helper did not become ready')
        # Encoded connection readiness alone must leave the waiting UI visible.
        assert window.spinner.isVisible() and window.waiting_label.isVisible()
        assert window.waiting_label.text() == '연결 대기중'
        for color, channel in [('red', 0), ('green', 1)]:
            command(color)
            until(lambda: color_is(channel), f'{color} video pixels missing')
            until(lambda: receiver.state == 'streaming', 'no rendered frame event')
            assert not window.spinner.isVisible() and not window.waiting_label.isVisible()
        window.resize(1000, 700)
        command('red')
        until(lambda: color_is(0), 'video did not survive resize')
        window.showFullScreen()
        command('green')
        until(lambda: color_is(1), 'video did not survive fullscreen')
        window.showNormal()
        command('stop')
        until(lambda: receiver.state == 'ready', 'disconnect did not restore waiting state')
        assert window.spinner.isVisible() and window.waiting_label.isVisible()
        command('red')
        until(lambda: color_is(0) and receiver.state == 'streaming', 'reconnect did not render')
        window.screen().grabWindow(0).save('video-render-preview.png')
        command('quit')
        until(lambda: receiver.process.state() == QProcess.NotRunning, 'native bridge failed to shut down')
    except Exception:
        window.screen().grabWindow(0).save('video-render-failure.png')
        raise
    finally:
        print('\n'.join(window.log_lines))
        window.close()
print('Native cross-process video, colors, resize, fullscreen and reconnect passed')
