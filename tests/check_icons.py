"""Verify that built Windows EXEs actually contain the original brand icon."""
import glob
import sys
from pathlib import Path
import pefile

reference = (Path(__file__).resolve().parents[1] / 'airlinker/assets/icon-256.png').read_bytes()
for pattern in sys.argv[1:]:
    paths = glob.glob(pattern)
    if not paths:
        raise AssertionError(f'No built executable: {pattern}')
    for filename in paths:
        with pefile.PE(filename) as pe:
            icons = []
            for resource in pe.DIRECTORY_ENTRY_RESOURCE.entries:
                if resource.id == pefile.RESOURCE_TYPE['RT_ICON']:
                    for icon in resource.directory.entries:
                        for language in icon.directory.entries:
                            item = language.data.struct
                            icons.append(pe.get_data(item.OffsetToData, item.Size))
            assert reference in icons, f'Branded 256px icon missing from {filename}'
        print(f'Windows icon resource verified: {filename}')
