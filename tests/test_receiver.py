"""Exercise real QProcess pipes, crashes, timeouts and repeated starts.
The stand-in only tests the controller; it is not an AirPlay simulator.
"""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import sys
import tempfile
import time
import unittest
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QProcess
from airlinker.receiver import Receiver


class ScriptOptions:
    def __init__(self, script):
        self.script = script

    def arguments(self, config, windows):
        return ['-u', '-c', self.script]


class ReceiverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.receiver = Receiver()
        self.states = []
        self.receiver.state_changed.connect(self.states.append)

    def tearDown(self):
        self.receiver.shutdown()
        self.tmp.cleanup()

    def wait_until(self, condition, seconds=4):
        deadline = time.monotonic() + seconds
        while not condition() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.01)
        self.assertTrue(condition(), self.states)

    def start_script(self, script):
        self.receiver.start(Path(sys.executable), ScriptOptions(script), Path(self.tmp.name), 1)

    def test_real_pipes_and_restart(self):
        script = "import time; print('AIRLINKER/1 READY'); time.sleep(.1); print('AIRLINKER/1 STREAMING'); time.sleep(30)"
        for _ in range(2):
            self.start_script(script)
            self.wait_until(lambda: self.receiver.state == 'streaming')
            self.receiver.stop()
            self.wait_until(lambda: self.receiver.state == 'stopped')
        self.assertEqual(self.states.count('streaming'), 2)
        self.assertEqual(self.receiver.process.state(), QProcess.NotRunning)

    def test_early_idle_does_not_mark_ready(self):
        self.start_script("import time; print('AIRLINKER/1 IDLE'); time.sleep(30)")
        self.wait_until(lambda: self.receiver.process.state() == QProcess.Running)
        for _ in range(30):
            self.app.processEvents()
            time.sleep(.01)
        self.assertEqual(self.receiver.state, 'starting')

    def test_nonzero_exit_is_error(self):
        self.start_script("import sys; print('AIRLINKER/1 READY'); sys.exit(3)")
        self.wait_until(lambda: self.receiver.state == 'error')

    def test_unexpected_clean_exit_is_error(self):
        self.start_script("print('AIRLINKER/1 READY')")
        self.wait_until(lambda: self.receiver.state == 'error')

    def test_timeout_stops_process(self):
        self.receiver.deadline.setInterval(80)
        self.start_script('import time; time.sleep(30)')
        self.wait_until(lambda: self.receiver.state == 'error')
        self.assertEqual(self.receiver.process.state(), QProcess.NotRunning)

    def test_missing_executable_is_error(self):
        self.receiver.start(Path(self.tmp.name) / 'missing.exe', ScriptOptions(''), Path(self.tmp.name), 1)
        self.wait_until(lambda: self.receiver.state == 'error')

    def test_shutdown_leaves_no_process(self):
        self.start_script("import time; print('AIRLINKER/1 READY'); time.sleep(30)")
        self.wait_until(lambda: self.receiver.state == 'ready')
        self.receiver.shutdown()
        self.assertEqual(self.receiver.process.state(), QProcess.NotRunning)
