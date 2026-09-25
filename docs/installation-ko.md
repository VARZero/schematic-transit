# 설치와 사용법

[English version](installation-en.md) · **한국어**

[← 첫 화면](../README.md) · [데이터 구조](data-format-ko.md) · [부산권 예제 데이터](../data/network.json) · [최소 예제](../examples/minimal.json)

## 1. 준비와 설치

Python 3.10 이상이 필요합니다. 터미널에서 이 프로젝트의 최상위 폴더(`README.md`가 있는 폴더)로 이동한 뒤 설치합니다.

```sh
python3 -m pip install -e .
```

`-e`는 코드를 수정하면 다시 설치하지 않아도 변경 내용이 반영되는 개발용 설치입니다. 별도 환경을 쓰려면 먼저 가상환경을 만드세요.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell에서는 활성화 명령을 `.venv\Scripts\Activate.ps1`로 바꾸면 됩니다. 설치가 어려우면 아래처럼 설치 없이 실행할 수도 있습니다.

```sh
PYTHONPATH=src python3 -m schematic_transit.cli data/network.json --output exports/busan_gimhae_ulsan_map
```

## 2. 부산권 예제 출력

```sh
schematic-transit data/network.json --output exports/busan_gimhae_ulsan_map
```

한 번 실행하면 [PNG](../exports/busan_gimhae_ulsan_map.png), [SVG](../exports/busan_gimhae_ulsan_map.svg), [PDF](../exports/busan_gimhae_ulsan_map.pdf)가 생성됩니다. `--output`은 확장자를 뺀 파일 이름입니다. SVG의 글자는 편집 가능한 텍스트로 저장됩니다.

필요한 형식만 출력할 수도 있습니다.

```sh
schematic-transit data/network.json --output exports/my_map --formats svg pdf
schematic-transit data/network.json --output exports/my_map --formats png --dpi 200
```

## 3. 다른 노선도로 시작

[최소 예제 데이터](../examples/minimal.json)를 복사해 새 JSON 파일을 만든 후 제목, 역, 노선, 기준점 좌표를 바꾸세요. JSON 필드별 의미와 작성 규칙은 [데이터 구조](data-format-ko.md)에 정리했습니다.

여러 노선이 같은 구간을 지나는 모습을 보려면 [겹침 예제 데이터](../examples/overlap.json)와 [출력 PNG](../exports/overlap_demo.png)를 확인하세요.

```sh
schematic-transit examples/minimal.json --output exports/minimal
```

## 4. Python 코드에서 사용

```python
from schematic_transit import load_network, OctilinearLayout, render

network = load_network("data/network.json")
layout = OctilinearLayout().build(network)
files = render(layout, "exports/my_map", formats=("svg", "pdf"))
print(files["svg"])
```

[공개 API](../src/schematic_transit/__init__.py)에서 `Network`, `Line`, `OctilinearLayout`, `load_network`, `render`를 가져올 수 있습니다. 내부 구현은 [모델](../src/schematic_transit/model.py), [배치](../src/schematic_transit/layout.py), [렌더러](../src/schematic_transit/render.py), [명령줄 도구](../src/schematic_transit/cli.py)로 나뉩니다.

## 5. 테스트

```sh
PYTHONPATH=src python3 -m unittest discover -s tests
```

[테스트 코드](../tests/test_layout.py)는 0°·45°·90° 경로 생성, 꺾임 방향, 환승역 좌표 검증을 확인합니다.

[← 첫 화면](../README.md) · [데이터 구조 →](data-format-ko.md)
