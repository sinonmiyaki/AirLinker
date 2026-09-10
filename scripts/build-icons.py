"""Render original SVG artwork using the existing PySide6 dependency."""
import os
import struct
from pathlib import Path
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtCore import QRectF
from PySide6.QtGui import QGuiApplication, QImage, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer

ROOT = Path(__file__).resolve().parents[1] / 'airlinker/assets'
SIZES = (16, 24, 32, 48, 64, 128, 256)

def render(path, size):
    renderer = QSvgRenderer(str(path))
    if not renderer.isValid():
        raise ValueError(f'Invalid SVG: {path}')
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()
    return image


def main():
    app = QGuiApplication([])
    for size in SIZES:
        assert render(ROOT / 'airlinker.svg', size).save(str(ROOT / f'icon-{size}.png'))
    assert render(ROOT / 'airlinker.svg', 512).save(str(ROOT / 'airlinker.png'))
    assert render(ROOT / 'mark.svg', 128).save(str(ROOT / 'mark.png'))
    # PNG-backed ICO frames: lossless alpha and native Windows size selection.
    frames = [(size, (ROOT / f'icon-{size}.png').read_bytes()) for size in SIZES]
    offset = 6 + 16 * len(frames)
    directory = bytearray(struct.pack('<HHH', 0, 1, len(frames)))
    for size, data in frames:
        directory += struct.pack('<BBBBHHII', size % 256, size % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (ROOT / 'airlinker.ico').write_bytes(directory + b''.join(data for _, data in frames))
    # Inno Setup's wizard graphics use standard 24-bit BMPs.
    small = QImage(55, 55, QImage.Format_RGB32)
    small.fill(QColor('#ffffff'))
    painter = QPainter(small)
    painter.drawImage(3, 3, render(ROOT / 'airlinker.svg', 49))
    painter.end()
    assert small.save(str(ROOT / 'installer-small.bmp'))
    banner = QImage(164, 314, QImage.Format_RGB32)
    banner.fill(QColor('#1845C5'))
    painter = QPainter(banner)
    QSvgRenderer(str(ROOT / 'mark.svg')).render(painter, QRectF(24, 72, 116, 116))
    painter.end()
    assert banner.save(str(ROOT / 'installer-banner.bmp'))
    print('SVG, PNG sizes, ICO and installer graphics ready')

if __name__ == '__main__':
    main()
