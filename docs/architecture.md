# 구현 구조

```text
Apple 기기 제어 센터
  │ mDNS 검색 + AirPlay 페어링/RTSP/RTP
  ▼
UxPlay (별도 프로세스, 고정된 수정 소스)
  ├─ 내장 mDNS: _airplay._tcp / _raop._tcp
  ├─ 화면/오디오 수신 → GStreamer 디코딩
  │                       ├─ d3d11videosink → Qt 앱의 HWND
  │                       └─ autoaudiosink → Windows 스피커
  └─ stdout 이벤트/진단 → QProcess → 앱 상태 및 연결 로그
```

- `airlinker/core.py`: 설정 검증, 셸을 사용하지 않는 인수 배열, 파이프 조각 복원.
- `airlinker/receiver.py`: 비동기 QProcess, 20초 시작 제한, 종료/강제 종료, runtime 환경 설정.
- `airlinker/app.py`: PySide6 네이티브 UI, 설정 저장, 미리 생성한 HWND, 로그 저장.
- `vendor/uxplay`: 원본 커밋과 출처는 `AIRLINKER-UPSTREAM.txt`에 기록. 다운로드 없이 이 소스로 빌드.
- `scripts`: UCRT64 엔진 빌드, 런타임 수집, Python 패키징, 선택적 방화벽 규칙.

## UxPlay에 추가한 내용

1. `renderers/video_renderer.c`의 파이프라인 버스에 동기 핸들러를 설치합니다. Windows에서 `AIRLINKER_WINDOW_HANDLE`의 정수 HWND를 `GstVideoOverlay`의 `prepare-window-handle` 메시지 처리 중 전달합니다. 핸들러는 UI 함수를 호출하지 않습니다.
2. 서비스 등록 성공 뒤 `AIRLINKER/1 READY`를 stdout에 출력합니다.
3. 첫 복호화 영상 패킷을 파이프라인에 보내는 시점에 `AIRLINKER/1 STREAMING`을 출력합니다. 이 이벤트는 수신을 뜻하며 화면에 프레임이 실제 표시됐음을 보장하지는 않습니다.
4. 렌더러 정지/마지막 연결 종료에 `AIRLINKER/1 IDLE`을 출력합니다.
5. stdout/stderr를 비버퍼링으로 설정해 파이프로 연결할 때 상태가 지연되지 않게 합니다.

상태 머신은 엔진 프로세스 생성만으로 연결 대기를 표시하지 않습니다. READY 이전의 IDLE은 무시합니다. 재시작마다 파이프 버퍼를 비우고, 의도하지 않은 종료는 종료 코드가 0이어도 오류로 처리합니다. 앱 종료 전 엔진 종료를 기다리고 필요하면 강제 종료합니다. Windows의 콘솔 종료 동작에 따라 강제 종료가 사용될 수 있으며, 이 경우 mDNS 항목이 잠시 캐시에 남을 수 있습니다.

사용자의 `.uxplayrc` 설정이 UI 설정과 충돌하지 않도록 앱 데이터 폴더의 빈 설정 파일을 명시합니다. TCP/UDP 포트는 35000–35002로 고정했습니다. 하나의 PC에서 이 기본 설정의 인스턴스를 여러 개 동시에 실행할 수 없습니다.

## 주요 참고 자료

- [UxPlay 원본 소스 및 Windows 빌드 안내](https://github.com/FDH2/UxPlay/tree/9f3c2bbc658645533fa1057e76c29ec8c947fa0f)
- [GStreamer GstVideoOverlay](https://gstreamer.freedesktop.org/documentation/video/gstvideooverlay.html)
- [GStreamer d3d11videosink](https://gstreamer.freedesktop.org/documentation/d3d11/d3d11videosink.html)

## 배포 설계

선택한 GStreamer 플러그인과 PE DLL 의존성만 수집합니다. `runtime/packages.json`에 파일을 제공한 패키지의 정확한 버전을 기록하고, 해당 MSYS2 소스 아카이브와 Qt/PySide/Python 소스를 수집하여 SHA-256 목록과 함께 제공합니다. 설치 EXE와 대응 소스는 같은 Actions 실행에서 제공됩니다. Windows 컴파일과 패키징 검증 기록은 testing.md에 있습니다. 코드 서명과 자동 업데이트는 후속 작업입니다. MSYS2 패키지는 설치 시점 버전을 사용하므로 전체 툴체인이 고정된 것은 아닙니다.

## 간소화된 화면

검은 배경, 중앙 애니메이션, 상단 설정 버튼만 표시합니다. 설정 대화상자에서 적용하면 변경된 수신 설정을 저장하고 필요한 경우 비동기로 재시작합니다. 오류 진단은 화면 설명 대신 앱 종료 시 로컬 로그로 저장합니다.
