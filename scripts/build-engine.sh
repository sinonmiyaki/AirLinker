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
mkdir -p runtime/bin runtime/lib/gstreamer-1.0 runtime/libexec/gstreamer-1.0 runtime/share/licenses
cp build/engine/uxplay.exe runtime/bin/
# Include the installed runtime DLL set: plugins have dynamically loaded dependencies
# which a direct uxplay.exe dependency walk would miss.
cp /ucrt64/bin/*.dll runtime/bin/
cp /ucrt64/lib/gstreamer-1.0/*.dll runtime/lib/gstreamer-1.0/
cp /ucrt64/libexec/gstreamer-1.0/gst-plugin-scanner.exe runtime/libexec/gstreamer-1.0/
cp /ucrt64/bin/gst-inspect-1.0.exe runtime/bin/
cp -R /ucrt64/share/licenses/. runtime/share/licenses/
pacman -Q > runtime/packages.txt
cp vendor/uxplay/AIRLINKER-UPSTREAM.txt runtime/
export PATH="$PWD/runtime/bin:$PATH"
export GST_PLUGIN_SYSTEM_PATH_1_0="$PWD/runtime/lib/gstreamer-1.0"
export GST_PLUGIN_PATH_1_0="$GST_PLUGIN_SYSTEM_PATH_1_0"
export GST_PLUGIN_SCANNER="$PWD/runtime/libexec/gstreamer-1.0/gst-plugin-scanner.exe"
for plugin in d3d11videosink h264parse avdec_h264 avdec_aac avdec_alac wasapisink; do
  runtime/bin/gst-inspect-1.0.exe "$plugin" >/dev/null
done
runtime/bin/uxplay.exe -h >/dev/null
echo 'Engine and GStreamer plugins built successfully.'
