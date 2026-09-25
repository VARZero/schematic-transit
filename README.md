# Schematic Transit

[English](README.en.md) · **한국어**

네.. 심심해서 진짜 바이브코딩으로 해서 만들어 봤습니다.. 
모든 부분을 다 만드는 사람이 밑바닥도 설계 안하고 만드니 기분이 이상하네요..  
노선 데이터로 철도 노선도를 만드는 파이썬 라이브러리입니다.    

JSON 노선 데이터로 0°·45°·90° 선분의 철도 노선도를 만드는 Python 라이브러리입니다. 역명 전체 표시, 환승역 강조, 운행·계획·구상 노선 구분, PNG·SVG·PDF 출력을 지원합니다. 여러 노선이 같은 선분을 지나면 그 구간을 넓혀 각 노선 색을 나란히 표시합니다.

## 문서 바로가기

- [설치와 사용법](docs/installation-ko.md): 설치, 명령줄, Python API, 출력, 테스트
- [데이터 구조](docs/data-format-ko.md): JSON 필드, 좌표와 배치 방식, 수정 예시
- [English installation and usage](docs/installation-en.md) · [English data format](docs/data-format-en.md)
- [최소 예제 데이터](examples/minimal.json) · [부산권 예제 데이터](data/network.json)
- [선 겹침 예제 데이터](examples/overlap.json) · [겹침 출력 PNG](exports/overlap_demo.png) · [SVG](exports/overlap_demo.svg) · [PDF](exports/overlap_demo.pdf)
- [부산권 출력 PNG](exports/busan_gimhae_ulsan_map.png) · [SVG](exports/busan_gimhae_ulsan_map.svg) · [PDF](exports/busan_gimhae_ulsan_map.pdf)

## 코드 바로가기

- [공개 API](src/schematic_transit/__init__.py) · [데이터 검증](src/schematic_transit/model.py) · [45°/90° 배치](src/schematic_transit/layout.py)
- [그리기와 파일 출력](src/schematic_transit/render.py) · [겹침 구간 검출](src/schematic_transit/overlap.py) · [명령줄 실행](src/schematic_transit/cli.py) · [테스트](tests/test_layout.py)
- [패키지 설정](pyproject.toml) · [구형 설치 도구 호환 설정](setup.py) · [필요 라이브러리](requirements.txt)

## 빠른 시작

이 폴더에서 실행합니다. Python 3.10 이상이 필요합니다.

```sh
python3 -m pip install -e .
schematic-transit data/network.json --output exports/busan_gimhae_ulsan_map
```

압축파일을 받은 경우 먼저 압축을 풀고 `schematic-transit` 폴더에서 실행하세요. 자세한 순서는 [설치와 사용법](docs/installation-ko.md)에 있습니다.

## 부산권 예제 범위

예제 데이터에는 부산 1~4호선, 부산김해경전철, 태화강까지의 동해선 광역전철과 계획 노선인 양산선·부산 5호선 사상~하단 구간·BuTX가 들어 있습니다. 경전–동해 연결은 **직결 운행이 확정된 노선이 아닌 지도용 구상**으로 표시했습니다. 계획 노선의 역명과 선형은 바뀔 수 있으며, 이 그림은 실제 거리와 일치하지 않습니다.

자료 확인: [부산교통공사 운행 노선](https://data.humetro.busan.kr/homepage/default/page/subLocation.do?menu_no=10010101), [부산김해경전철](https://www.bglrt.com/00012.web), [코레일 동해선](https://info.korail.com/info/contents.do?key=863), [양산선 역 목록](https://www.busan.go.kr/news/totalnews01/view?curPage=1&dataNo=72491), [사상~하단선 공고](https://www.busan.go.kr/nbgosi/view?curPage=2&gosiGbn=A&sno=77896), [BuTX 계획](https://www.busan.go.kr/mayor/briefing/1581500), [부전~마산선 현황](https://www.busan.go.kr/nbtnewsBU/1750969?curPage=9&srchBeginDt=&srchEndDt=&srchKey=&srchText=) (확인일: 2026-09-26).
