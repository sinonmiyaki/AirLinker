import tempfile
import unittest
from pathlib import Path
from airlinker.core import Options, LineDecoder, event


class CoreTests(unittest.TestCase):
    def test_name_stays_one_argument(self):
        name = '거실 Windows; echo hello'
        args = Options(name=name).arguments(Path('C:/folder with spaces/config'), True)
        self.assertEqual(args[args.index('-n') + 1], name)
        self.assertEqual(args[args.index('-rc') + 1], 'C:/folder with spaces/config')
        self.assertEqual(args[args.index('-p') + 1], '35000')
        self.assertEqual(args[args.index('-vs') + 1], 'd3d11videosink')

    def test_invalid_names(self):
        for name in ('', '   ', '-d', 'a\nb', '가' * 17):
            with self.subTest(name=name), self.assertRaises(ValueError):
                Options(name=name).validate()

    def test_audio_and_decode(self):
        args = Options(audio=False, software_decode=True).arguments(Path('config'), False)
        self.assertIn('-avdec', args)
        self.assertEqual(args[args.index('-as') + 1], '0')
        self.assertNotIn('-vs', args)

    def test_chunked_utf8_and_events(self):
        decoder = LineDecoder()
        encoded = '연결 중\nAIRLINKER/1 READY\r\n'.encode()
        lines = []
        for byte in encoded:
            lines.extend(decoder.feed(bytes([byte])))
        self.assertEqual(lines, ['연결 중', 'AIRLINKER/1 READY'])
        self.assertEqual(event(lines[-1]), 'ready')
        self.assertIsNone(event('client name: AIRLINKER/1 READY'))

    def test_large_unterminated_line_bounded(self):
        decoder = LineDecoder()
        self.assertEqual(len(decoder.feed(b'x' * 70000)), 1)
        self.assertEqual(decoder.pending, b'')

    def test_quality_validation(self):
        for options in (Options(fps=0), Options(resolution='4K')):
            with self.assertRaises(ValueError):
                options.validate()
