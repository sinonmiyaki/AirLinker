"""Pure configuration and protocol code; no platform or GUI dependency."""
from dataclasses import dataclass
from pathlib import Path
import os
import sys


@dataclass(frozen=True)
class Options:
    name: str = 'AirLinker Windows'
    resolution: str = '1920x1080'
    fps: int = 60
    audio: bool = True
    software_decode: bool = False

    def validate(self):
        if not self.name.strip() or len(self.name.strip().encode('utf-8')) > 50:
            raise ValueError('수신 이름은 UTF-8 기준 1~50바이트로 입력해 주세요.')
        if any(ord(c) < 32 for c in self.name) or self.name.startswith('-'):
            raise ValueError('수신 이름에 제어 문자 또는 맨 앞의 - 를 사용할 수 없습니다.')
        if self.resolution not in ('1280x720', '1920x1080') or self.fps not in (30, 60):
            raise ValueError('지원하지 않는 해상도 또는 프레임 설정입니다.')

    def arguments(self, config: Path, windows: bool):
        self.validate()
        result = ['-rc', str(config), '-n', self.name.strip(), '-nh',
                  '-s', self.resolution, '-fps', str(self.fps), '-p', '35000',
                  '-nofreeze', '-ble', 'off']
        if windows:
            result += ['-vs', 'd3d11videosink']
        if not self.audio:
            result += ['-as', '0']
        if self.software_decode:
            result += ['-avdec']
        return result


def app_root():
    return Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent.parent


def find_engine():
    override = os.environ.get('AIRLINKER_ENGINE')
    if override:
        path = Path(override).expanduser().resolve()
        return path if path.is_file() else None
    name = 'uxplay.exe' if sys.platform == 'win32' else 'uxplay'
    path = app_root() / 'runtime' / 'bin' / name
    return path if path.is_file() else None


class LineDecoder:
    """Keep UTF-8 and event tokens intact across arbitrary pipe read boundaries."""
    def __init__(self):
        self.pending = b''

    def feed(self, data):
        self.pending += data
        lines = self.pending.split(b'\n')
        self.pending = lines.pop()
        # Bound a malformed engine's output even if it never sends a newline.
        if len(self.pending) > 65536:
            lines.append(self.pending)
            self.pending = b''
        return [line.decode('utf-8', errors='replace').rstrip('\r') for line in lines]


def event(line):
    return {'AIRLINKER/1 READY': 'ready', 'AIRLINKER/1 STREAMING': 'streaming',
            'AIRLINKER/1 IDLE': 'ready'}.get(line)
