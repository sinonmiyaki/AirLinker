"""Download exact source archives beside the installer, with hashes and notices."""
import concurrent.futures
import hashlib
import importlib.metadata
import json
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path('dist/corresponding-source')
NOTICES = Path('dist/AirLinker/LICENSES/upstream')


def fetch(item):
    name, urls = item
    target = ROOT / name
    if not target.exists():
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=90) as response, target.with_suffix('.part').open('wb') as out:
                    shutil.copyfileobj(response, out)
                target.with_suffix('.part').replace(target)
                break
            except Exception as exc:
                last_error = exc
        else:
            raise RuntimeError(f'Source archive unavailable: {name}: {last_error}')
    digest = hashlib.sha256()
    with target.open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    print(f'Source: {name}', flush=True)
    return {'file': name, 'sha256': digest.hexdigest(), 'urls': urls}


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    NOTICES.mkdir(parents=True, exist_ok=True)
    packages = json.loads(Path('runtime/packages.json').read_text())
    sources = {}
    for package in packages:
        base = package.get('BASE', [package['NAME'][0].replace('mingw-w64-ucrt-x86_64-', 'mingw-w64-')])[0]
        version = package['VERSION'][0].split(':')[-1]
        filename = f'{base}-{version}.src.tar.zst'
        sources[filename] = [f'https://repo.msys2.org/mingw/sources/{filename}']
    qt = '6.8.3'
    sources[f'qt-everywhere-src-{qt}.tar.xz'] = [f'https://download.qt.io/archive/qt/6.8/{qt}/single/qt-everywhere-src-{qt}.tar.xz']
    sources[f'pyside-setup-everywhere-src-{qt}.tar.xz'] = [f'https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-{qt}-src/pyside-setup-everywhere-src-{qt}.tar.xz']
    python = '.'.join(map(str, sys.version_info[:3]))
    sources[f'Python-{python}.tar.xz'] = [f'https://www.python.org/ftp/python/{python}/Python-{python}.tar.xz']
    for package in ['pyinstaller', 'pyinstaller-hooks-contrib', 'altgraph', 'pefile', 'pywin32-ctypes']:
        dist = importlib.metadata.distribution(package)
        with urllib.request.urlopen(f'https://pypi.org/pypi/{package}/{dist.version}/json') as stream:
            metadata = json.load(stream)
        source = next(item for item in metadata['urls'] if item['packagetype'] == 'sdist')
        sources[source['filename']] = [source['url']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        manifest = list(pool.map(fetch, sorted(sources.items())))
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    # Qt and Python source archives contain their own third-party notices too.
    notice_index = []
    for source in ROOT.iterdir():
        if not source.name.endswith(('.tar.xz', '.tar.gz')):
            continue
        with tarfile.open(source) as archive:
            for member in archive:
                if not member.isfile() or member.size > 2_000_000:
                    continue
                parts = Path(member.name).parts
                name = Path(member.name).name.lower()
                if not (name.startswith(('license', 'copying', 'notice')) or 'LICENSES' in parts):
                    continue
                # Never use archive paths directly as filesystem destinations.
                identifier = hashlib.sha256((source.name + '/' + member.name).encode()).hexdigest()[:24]
                destination = NOTICES / (identifier + '.txt')
                notice_index.append({'file': destination.name, 'archive': source.name, 'original_path': member.name})
                destination.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as stream:
                    destination.write_bytes(stream.read())
    (NOTICES / 'index.json').write_text(json.dumps(notice_index, indent=2), encoding='utf-8')
    for name in ['airlinker', 'vendor', 'scripts', 'installer', 'tests', 'docs', 'LICENSES', '.github']:
        shutil.copytree(name, ROOT / 'AirLinker' / name, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ['run.py', 'requirements.txt', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'README.md']:
        shutil.copy2(name, ROOT / 'AirLinker' / name)
    shutil.copy2('runtime/packages.json', ROOT)
    shutil.copy2(ROOT / 'manifest.json', 'dist/AirLinker/source-manifest.json')


if __name__ == '__main__':
    main()
