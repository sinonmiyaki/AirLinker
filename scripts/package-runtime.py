"""Collect the selected GStreamer plugins and their PE dependency closure."""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

PLUGINS = ('coreelements', 'typefindfunctions', 'app', 'playback', 'autodetect',
           'audioconvert', 'audioresample', 'volume', 'level', 'videoconvertscale',
           'videoparsersbad', 'libav', 'd3d11', 'wasapi')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prefix', type=Path, required=True)
    args = parser.parse_args()
    prefix = args.prefix.resolve()
    output = Path('runtime')
    if output.exists():
        shutil.rmtree(output)
    bins = output / 'bin'
    bins.mkdir(parents=True)
    shutil.copy2('build/engine/uxplay.exe', bins)
    files = []
    for name in PLUGINS:
        files.append(Path('lib/gstreamer-1.0') / f'libgst{name}.dll')
    files += [Path('bin/gst-inspect-1.0.exe'), Path('libexec/gstreamer-1.0/gst-plugin-scanner.exe')]
    for relative in files:
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(prefix / relative, target)
    pending = [bins / 'uxplay.exe'] + [output / file for file in files]
    installed = {p.name.lower(): p for p in (prefix / 'bin').glob('*.dll')}
    seen = set()
    while pending:
        executable = pending.pop()
        if executable.name.lower() in seen:
            continue
        seen.add(executable.name.lower())
        details = subprocess.check_output([str(prefix / 'bin/objdump.exe'), '-p', str(executable)], text=True)
        for name in re.findall(r'DLL Name:\s*(\S+)', details):
            dependency = installed.get(name.lower())
            if dependency and dependency.name.lower() not in seen:
                target = bins / dependency.name
                if not target.exists():
                    shutil.copy2(dependency, target)
                    files.append(Path('bin') / dependency.name)
                pending.append(target)
    # Resolve each file to the package that actually supplied it.
    database = prefix.parent / 'var/lib/pacman/local'
    ownership = {}
    packages = {}
    for entry in database.iterdir():
        if not (entry / 'desc').exists() or not (entry / 'files').exists():
            continue
        fields = {}
        for block in (entry / 'desc').read_text(encoding='utf-8').split('\n\n'):
            lines = block.strip().splitlines()
            if len(lines) > 1:
                fields[lines[0].strip('%')] = lines[1:]
        if not fields.get('NAME', [''])[0].startswith('mingw-w64-ucrt-x86_64-'):
            continue
        package = fields['NAME'][0]
        packages[package] = fields
        for filename in (entry / 'files').read_text(encoding='utf-8').splitlines():
            ownership[filename] = package
    selected = set()
    for filename in files:
        key = prefix.name + '/' + filename.as_posix()
        if key not in ownership:
            raise RuntimeError(f'No package ownership for {key}')
        selected.add(ownership[key])
    (output / 'packages.json').write_text(json.dumps([packages[p] for p in sorted(selected)], indent=2), encoding='utf-8')
    shutil.copytree(prefix / 'share/licenses', output / 'share/licenses')
    shutil.copy2('vendor/uxplay/AIRLINKER-UPSTREAM.txt', output)
    print(f'Packaged {len(files)} runtime files from {len(selected)} packages')


if __name__ == '__main__':
    main()
