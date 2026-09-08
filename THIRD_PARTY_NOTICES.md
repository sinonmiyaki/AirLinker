# 에셋·라이선스 확인

확인일: 2026-09-08. 대상: 이 저장소의 소스, requirements.txt, Windows 빌드·패키징 스크립트. **오픈소스 저작권 라이선스상 소스 공개는 가능하다. 설치 패키징은 정확한 의존성 소스 수집을 포함하지만, 모든 국가의 특허·상표 문제까지 검증 완료한 것은 아니다.**

## 시각 에셋

- 검은 배경, 알약 버튼, 로딩 원: `airlinker/app.py`의 Qt 스타일과 QPainter 코드로 그린다. 외부 이미지·아이콘·동영상·음원 에셋을 사용하지 않았다.
- `docs/*preview.png`: 이 앱을 직접 실행해 캡처한 화면. 다른 미러링 제품의 화면을 복제하거나 포함하지 않았다.
- 폰트: OS에 설치된 글꼴 이름을 참조할 뿐 Segoe UI / Apple SD Gothic Neo 폰트 파일을 저장소나 설치 패키지에 복사하지 않는다.
- LonelyScreen은 제작 동기를 설명하기 위한 제품명이다. 해당 제품의 코드·로고·이미지를 사용하지 않았다. Apple 제품명/AirPlay 표기는 호환성 설명이며 Apple의 인증·후원을 뜻하지 않는다.

## 소스와 런타임

| 구성 요소 | 확인한 조건 | 적용 / 남은 작업 |
| --- | --- | --- |
| AirLinker 자체 소스 | GPL-3.0-or-later로 제공 | 루트 LICENSE. 원저작권을 가진 제3자 파일은 원래 조건도 유지 |
| UxPlay | GPLv3 계열, 일부 파일 GPL-3.0-or-later | 고정된 원본 커밋, 수정 소스, 수정 일자, 원저작권 및 LICENSE 포함 |
| UxPlay의 shairplay/mdns 등 | 파일 헤더 LGPL-2.1-or-later | 헤더 유지, LICENSES/LGPL-2.1.txt 추가 |
| playfair | 포함 LICENSE.md는 GPLv3 | 원본 라이선스 및 코드 유지. 프로젝트 전체 배포에서 GPLv3 조건 준수 |
| llhttp, SRP 구현 | MIT, 파일별 저작권 | LICENSE-MIT 및 srp.c/h의 전체 고지 유지 |
| PySide6 / Shiboken6 / Qt 6.8.3 | LGPLv3/GPL/상용 선택 및 Qt 내부 제3자 조건 | 오픈소스 조건을 이용할 수 있음. 패키지의 정확한 라이선스·고지와 대응 소스 제공 필요. 현재 사용 모듈은 Core/Gui/Widgets |
| GStreamer | 자체 코드는 LGPL-2.1, 일부 플러그인 의존성은 GPL 등 | 실제 포함된 플러그인의 `gst-inspect` 결과와 의존 라이브러리 조건을 각각 확인해야 함 |
| FFmpeg / gst-libav | 빌드 옵션에 따라 LGPL/GPL 등이 달라짐 | 실제 MSYS2 패키지의 라이선스·빌드 설정 확인 필요. nonfree 설정이 있다면 그대로 재배포할 수 있다고 판단하면 안 됨 |
| OpenSSL / libplist / 기타 MSYS2 DLL | 버전·패키지별 조건 | 현재 모든 UCRT64 DLL을 수집하므로 목록만 보고 일괄 승인 불가. 실제 패키지 목록과 대응 소스 확보 필요 |
| Python 런타임 | PSF 및 포함된 제3자 고지 | 설치 파일에 포함되는 정확한 Python 버전의 라이선스/고지 보존 필요 |
| PyInstaller 6.12.0 | GPLv2와 번들링 예외, 일부 Apache-2.0 | 예외가 앱 번들 배포를 허용함. 함께 묶은 라이브러리 조건을 면제하지는 않음 |
| Inno Setup 6.4.3 | 자체 라이선스, 상업적 사용 포함 사용·배포 허용 조건 | 원본 license.txt 보존. 후속 버전으로 바꾸면 해당 버전 조건 재확인 |

## 설치 파일을 공개 배포할 때

1. 실제 설치 EXE에 들어간 DLL/플러그인/Python 패키지 목록과 버전을 확정한다. 빌드 스크립트가 선택한 GStreamer 플러그인과 PE DLL 의존성을 수집하고 packages.json을 기록한다.
2. 저작권·라이선스·NOTICE를 포함하고, GPL/LGPL 구성 요소의 **정확한 대응 소스와 빌드/수정 내용**을 이용자가 받을 수 있게 제공한다. 라이선스 텍스트와 일반 홈페이지 링크만 모으는 것으로 모든 소스 제공 의무가 충족되는 것은 아니다.
3. LGPL 구성 요소의 교체/재링크 및 그 수정 사항 디버깅에 필요한 권리를 제한하지 않는다. onedir/DLL 패키징을 유지하고 별도 제한 EULA를 붙이지 않는다.
4. GStreamer/FFmpeg 플러그인의 실제 유효 라이선스, OpenSSL 버전 및 전체 라이브러리 조합을 점검한다.
5. 검사되지 않은 설치 파일을 배포 완료본으로 표시하지 않는다. 현재 GitHub workflow는 대응 소스 수집과 설치/삭제 시험이 성공한 경우에만 설치 EXE와 소스를 같은 실행의 아티팩트로 업로드한다.

오픈소스 라이선스는 제3자의 코덱 특허·상표나 국가별 법적 쟁점까지 포괄적으로 허가하는 문서가 아니다. 이 기록은 확인한 저작권 라이선스 조건과 기술적 패키징 범위의 검토이며, 모든 국가에서의 무조건적인 배포 적법성 판정은 아니다.

## 근거

- [UxPlay 고정 소스](https://github.com/FDH2/UxPlay/tree/9f3c2bbc658645533fa1057e76c29ec8c947fa0f), 저장소의 vendor/uxplay/LICENSE 및 각 파일 헤더
- [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html), [LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html)
- [Qt 오픈소스 라이선스](https://www.qt.io/development/download-open-source), [Qt for Python 6.8 제3자 라이선스](https://doc.qt.io/qtforpython-6.8/licenses.html)
- [GStreamer 라이선스 FAQ](https://gstreamer.freedesktop.org/documentation/frequently-asked-questions/general.html)
- [FFmpeg 라이선스 및 배포](https://ffmpeg.org/legal.html)
- [PyInstaller 6.12.0 라이선스](https://pyinstaller.org/en/v6.12.0/license.html)
- [Inno Setup 6.4.3 라이선스 원문](https://github.com/jrsoftware/issrc/blob/is-6_4_3/license.txt)

## 빌드 대응 소스

`scripts/collect-sources.py`가 해당 버전의 실제 소스 아카이브를 내려받아 SHA-256을 기록한다. 원본 소스에 들어 있는 라이선스/고지는 설치 패키지에도 복사한다. `LICENSES/upstream/index.json`은 짧은 고지 파일명을 원본 소스 경로에 연결한다. 설치 파일을 다른 장소에 다시 배포할 때는 같은 버전의 대응 소스도 함께 제공해야 한다. 이 자동 수집은 라이선스 조합이나 코덱 특허에 대한 포괄적 법률 판정을 대신하지 않는다.
