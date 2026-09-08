# 검증 기록

## Windows CI 검증 (2026-09-08)

[검증 실행](https://github.com/sinonmiyaki/AirLinker/actions/runs/34194054771), 코드 커밋 `01af17a9e2425a9bf80482105fc944fb6d9494e4`.

- Windows Server 2022 x64 / Python 3.11 / MSYS2 UCRT64에서 UxPlay 네이티브 컴파일 통과.
- 필수 GStreamer 플러그인 검사 통과.
- 설정/프로세스 제어 테스트 13개 통과.
- PyInstaller 앱 패키징 및 Inno Setup 설치 EXE 생성 통과.
- 패키징된 앱 실행 및 offscreen 화면 캡처 통과.
- 설치 EXE로 임시 폴더에 실제 설치 → 설치된 앱 실행/화면 캡처 → 방화벽 규칙 확인 → 제거 프로그램 실행 → 앱/방화벽 규칙 제거 확인 통과.
- 정확한 런타임 패키지 소스 아카이브 수집, SHA-256 목록 작성, 라이선스 고지 동봉.

앞선 두 번의 빌드에서는 테스트의 경로 구분자 비교와 Inno Setup의 긴 라이선스 파일 경로 문제를 발견하여 수정했습니다.

## macOS 개발 검증

- Python 3.9.6 / PySide6 6.8.3.
- `python -m unittest discover -s tests -v`: 13개 통과.
- `PYTHONPATH=. .venv/bin/python tests/check_ui.py`: 로딩 애니메이션, 설정 변경 후 재시작, 수신 끄기, 잘못된 이름 차단 확인.
- 실제 UI 캡처: `airlinker-preview.png`, `settings-preview.png`. 미러링 영상 캡처는 아닙니다.

## 아직 검증하지 못한 항목

- iPhone/iPad/Mac의 실제 목록 표시, 페어링, 영상/오디오 수신.
- 실제 Windows 10/11 그래픽 장치의 Direct3D11 HWND 출력, 회전, 화면 배율 변경.
- 장시간 스트리밍, 실제 공유기별 mDNS, 네트워크 단절 후 재연결.
- 빌드 도구가 전혀 없는 사용자 PC에서 실제 미러링.

CI의 QProcess 테스트는 제어 계층을 시험하며 AirPlay 프로토콜을 시뮬레이션하지 않습니다. 앱 캡처는 offscreen으로 실행하므로 실제 GPU 영상 표시를 검증한 것은 아닙니다.
