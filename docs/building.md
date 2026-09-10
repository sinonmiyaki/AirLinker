# 빌드와 개발

대상: **Windows 10/11 x64**, Direct3D 11 지원 그래픽 장치.

1. [Python 3.11 Windows x64](https://www.python.org/downloads/windows/)를 설치합니다. `py` 런처도 설치합니다.
2. [MSYS2](https://www.msys2.org/)를 기본 경로 `C:\msys64`에 설치합니다. MSYS2 터미널에서 `pacman -Syu`로 업데이트합니다. 터미널을 다시 열라고 나오면 재실행 후 업데이트를 마칩니다.
3. [Inno Setup 6 또는 7](https://jrsoftware.org/isinfo.php)을 설치합니다.
4. 이 저장소를 Windows에 복사하고 **일반 PowerShell**에서 실행합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

스크립트는 MSYS2 빌드 의존성을 설치하고, 저장소에 포함된 UxPlay 소스를 컴파일한 뒤, GStreamer 플러그인을 확인하고 데스크톱 앱을 패키징합니다. 최초 실행에는 인터넷과 충분한 디스크 공간이 필요합니다. Python 의존성은 프로젝트의 `.venv`에 설치됩니다.

완료 후 `dist\installer\AirLinker-Setup-0.1.3-x64.exe`를 Windows PC에서 실행하면 설치됩니다. 시작 메뉴·바탕 화면 바로가기, 개인 LAN 방화벽 규칙, 제거 프로그램이 포함됩니다. Python·MSYS2·Inno Setup은 빌드 PC에만 필요합니다. 인증서로 서명한 배포판은 아닙니다.

[Windows Actions](https://github.com/sinonmiyaki/AirLinker/actions/workflows/windows.yml)에서 빌드·테스트·설치/삭제 검증을 실행합니다. 성공한 실행의 Artifacts에서 `AirLinker-Setup-Windows-x64`를 받으세요. 정확한 의존성의 소스는 같은 실행의 `AirLinker-Corresponding-Source`에 제공됩니다. 아티팩트 보관 기간은 30일이며 다운로드에는 GitHub 로그인이 필요합니다.

## 개발 및 검증

```powershell
.venv\Scripts\python.exe -m airlinker
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

macOS에서도 UI와 프로세스 제어 테스트를 실행할 수 있습니다. Windows 화면 임베딩은 Windows 전용입니다.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m airlinker --no-autostart
.venv/bin/python -m unittest discover -s tests -v
```

기본 엔진 경로는 `runtime/bin/uxplay.exe`입니다. 개발용으로 `AIRLINKER_ENGINE`에 패치된 엔진의 절대 경로를 설정할 수 있습니다. 원본 UxPlay 바이너리는 이 앱의 상태 이벤트/영상 임베딩 계약을 지원하지 않습니다.

검증된 항목 및 실제 기기로 확인할 항목은 [검증 기록](testing.md), 구조와 변경 내용은 [구현 문서](architecture.md)에 있습니다.

## 로고 재생성

`python scripts/build-icons.py`로 SVG 원본에서 PNG·ICO·설치 마법사 이미지를 다시 만듭니다. 앱 실행에는 QtSvg 모듈을 사용하지 않습니다.
