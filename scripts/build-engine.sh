#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ "${MSYSTEM:-}" != UCRT64 ]]; then
  echo 'Run this script inside the MSYS2 UCRT64 terminal.' >&2
  exit 1
fi
pacman -S --needed --noconfirm \
  mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-cmake \
  mingw-w64-ucrt-x86_64-ninja mingw-w64-ucrt-x86_64-pkgconf \
  mingw-w64-ucrt-x86_64-openssl mingw-w64-ucrt-x86_64-libplist \
  mingw-w64-ucrt-x86_64-gstreamer mingw-w64-ucrt-x86_64-gst-plugins-base \
  mingw-w64-ucrt-x86_64-gst-plugins-good mingw-w64-ucrt-x86_64-gst-plugins-bad \
  mingw-w64-ucrt-x86_64-gst-libav
cmake -S vendor/uxplay -B build/engine -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DNO_MARCH_NATIVE=ON -DUSE_MDNS=ON
cmake --build build/engine --parallel 4
python scripts/package-runtime.py --prefix "$(cygpath -w /ucrt64)"
pacman -Q > runtime/packages.txt
export PATH="$PWD/runtime/bin:$PATH"
export GST_PLUGIN_SYSTEM_PATH_1_0="$PWD/runtime/lib/gstreamer-1.0"
export GST_PLUGIN_PATH_1_0="$GST_PLUGIN_SYSTEM_PATH_1_0"
export GST_PLUGIN_SCANNER="$PWD/runtime/libexec/gstreamer-1.0/gst-plugin-scanner.exe"
for plugin in d3d11videosink h264parse avdec_h264 avdec_aac avdec_alac wasapisink; do
  runtime/bin/gst-inspect-1.0.exe "$plugin" >/dev/null
done
runtime/bin/uxplay.exe -h >/dev/null
echo 'Engine and GStreamer plugins built successfully.'
