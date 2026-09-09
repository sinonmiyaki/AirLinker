# 검증 기록

## 설정 버튼 자동 숨김 (v0.1.2)

[Windows 검증 실행](https://github.com/sinonmiyaki/AirLinker/actions/runs/34340857762), 빌드 커밋 `2323e3fd2333a1d5b9c5edec5fff9d8a5dd50cdb`.

- 실제 D3D11 영상 재생 중 버튼이 위로 숨고, 상단 중앙에 마우스를 올리면 내려오는 동작 통과.
- Windows OS 마우스 입력으로 내려온 버튼 클릭 → 설정 창 열기 → 닫은 후 다시 숨기기 통과.
- 전체 화면의 호버 동작과 연결 종료 후 버튼 복원, 영상 재연결 통과.
- 상태 및 프로세스 단위 테스트 13개, 앱 패키징, 실제 설치·실행·방화벽 등록·제거 검사 통과.
- 이 빌드의 GStreamer는 1.28.7입니다. 정확한 의존성 버전과 대응 소스는 해당 Release의 manifest와 source 안내를 확인하세요.

## Windows 영상 출력 수정 (2026-09-09, v0.1.1)

[최종 빌드 실행](https://github.com/sinonmiyaki/AirLinker/actions/runs/34305132410).

- 사용자는 Apple 기기의 목록 표시·연결 성공과 연결 후 검은 화면을 보고했습니다.
- GStreamer d3d11videosink가 다른 프로세스의 Qt HWND를 subclass하던 경로를 엔진 소유 자식 HWND로 변경했습니다.
- 별도 네이티브 프로세스가 실제 제품과 동일한 `airlinker_window.c`를 사용해 D3D11로 합성 영상 프레임을 출력합니다. Qt 호스트는 실제 Windows 데스크톱의 합성된 픽셀을 캡처해 빨강/초록을 검증합니다.
- 최초 프레임 전 대기 문구, 프레임 출력 후 대기 표시 해제, 크기 변경, 전체 화면, 파이프라인 종료 후 재연결, 프로세스 종료를 검사합니다.
- 최초 검증에서는 영상 검사가 모두 통과한 뒤 테스트 자체의 QProcess 종료 판정과 CP1252 콘솔 출력 오류를 발견해 수정했습니다.
- 이 검사는 실제 Apple 송신 기기, AirPlay 페어링, H.264 디코딩 또는 오디오를 검증하지 않습니다. 아래 실기기 검증 한계가 계속 적용됩니다.

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
- 실제 Windows 10/11 사용자 GPU에서의 출력, 기기 회전, 화면 배율 변경.
- 장시간 스트리밍, 실제 공유기별 mDNS, 네트워크 단절 후 재연결.
- 빌드 도구가 전혀 없는 사용자 PC에서 실제 미러링.

QProcess 단위 테스트와 설치 앱의 offscreen 캡처는 제어 계층 및 UI를 검증합니다. v0.1.1의 별도 Windows 데스크톱 검사는 실제 D3D11 영상 출력 픽셀을 검증하지만, CI 그래픽 환경이 사용자 PC의 GPU와 같지는 않습니다.
