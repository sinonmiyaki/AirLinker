# 검증 기록

## 이 작업에서 실행함

- macOS / Python 3.9.6 / PySide6 6.8.3.
- `python -m unittest discover -s tests -v`: **13개 통과**.
- 테스트 내용: 한글/공백 포함 인수, 잘못된 설정 차단, 분할 UTF-8 파이프 입력, 로그 버퍼 제한, 실제 QProcess 파이프의 상태 전이, 반복 시작/중지, 잘못된 실행 파일, 비정상/예상하지 않은 정상 종료, 시작 시간 초과, 앱 종료 시 프로세스 정리.
- `bash -n scripts/build-engine.sh`: 통과.
- Qt offscreen 화면 캡처와 육안 확인: `airlinker-preview.png`. 수신 중지 상태의 실제 UI 캡처이며 미러링 영상 캡처는 아닙니다.

QProcess 테스트에 쓰는 짧은 Python 프로세스는 제어 계층 테스트용입니다. 실제 AirPlay 연결/페어링/디코딩을 시험하지 않습니다.

## 아직 실행하지 못함

- Windows UCRT64 엔진 컴파일 및 PyInstaller 패키징.
- GitHub Actions 워크플로 실행.
- Windows의 실제 Direct3D11 HWND 출력, 크기 변경/전체 화면/DPI 변경.
- iPhone/iPad/Mac의 목록 표시, 페어링, 영상 및 오디오 수신.
- 회전, 세로/가로 전환, 지연/장시간 스트리밍, 중단 후 재연결.
- Windows 방화벽 및 공유기별 내장 mDNS 호환성.
- 빌드 도구가 설치되지 않은 깨끗한 Windows PC에서 실행.

## Windows 인수 시험 순서

1. 빌드 스크립트 성공 및 플러그인 검사 통과. Python/MSYS2 없는 두 번째 PC로 전체 출력 폴더를 복사해 실행.
2. 개인 LAN에서 방화벽 허용 후 iPhone/iPad/Mac 각각에서 수신 이름이 뜨는지 확인.
3. 각 기기의 홈 화면, 사진, 보호되지 않은 영상/오디오를 미러링. 앱 내부 영상 영역에 표시되는지 확인.
4. 회전, 창 크기 변경, F11/Esc, Windows 디스플레이 배율 100/150/200% 확인.
5. 기기에서 중단한 뒤 다른 기기로 연결. 앱 중지/시작을 반복. 절전/네트워크 끊김 뒤 복구 확인.
6. 오디오 끄기, 소프트웨어 디코딩, 720p/30fps를 각각 확인.
7. 30분 이상 수신 후 앱 종료. 작업 관리자에서 uxplay.exe가 남지 않는지 확인.
8. 실패하면 앱의 로그 저장 기능으로 로그와 Windows/기기 OS 버전, 공유기 모델을 함께 기록.

## 간소화 UI 수정 검증

- 기존 테스트 13개 재통과.
- `PYTHONPATH=. .venv/bin/python tests/check_ui.py`: 로딩 애니메이션 시작/중지, 설정 변경 후 재시작 예약, 수신 끄기, 잘못된 이름 차단 확인.
- `airlinker-preview.png`, `settings-preview.png` 화면 캡처 확인.
- Inno Setup 정의와 CI 설치 EXE 빌드를 추가했으나 Windows 환경 부재로 컴파일/설치/제거는 미검증.
