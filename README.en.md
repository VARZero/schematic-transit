# Schematic Transit

**English** · [한국어](README.md)

A Python library for data-driven transit diagrams. It draws 0°/45°/90° route segments, labels every station, highlights interchanges, distinguishes operating, planned, and conceptual lines, and exports PNG, SVG, and PDF. Coincident routes become a wider band with their colors shown side by side.

## Documentation

- [Installation and usage](docs/installation-en.md): setup, CLI, Python API, output, tests
- [JSON data format](docs/data-format-en.md): fields, coordinates, layout, and edits
- [Korean installation guide](docs/installation-ko.md) · [Korean data format guide](docs/data-format-ko.md)
- [Minimal example](examples/minimal.json) · [Busan-area example data](data/network.json)
- [Overlapping-lines example](examples/overlap.json) · output [PNG](exports/overlap_demo.png) · [SVG](exports/overlap_demo.svg) · [PDF](exports/overlap_demo.pdf)
- Busan-area output: [PNG](exports/busan_gimhae_ulsan_map.png) · [SVG](exports/busan_gimhae_ulsan_map.svg) · [PDF](exports/busan_gimhae_ulsan_map.pdf)

## Source files

- [Public API](src/schematic_transit/__init__.py) · [Data model and validation](src/schematic_transit/model.py) · [Octilinear layout](src/schematic_transit/layout.py)
- [Renderer](src/schematic_transit/render.py) · [Overlap detection](src/schematic_transit/overlap.py) · [CLI](src/schematic_transit/cli.py) · [Tests](tests/test_layout.py)
- [Package configuration](pyproject.toml) · [Legacy installer compatibility](setup.py) · [Dependencies](requirements.txt)

## Quick start

Run from the folder containing this README. Python 3.10 or later is required.

```sh
python3 -m pip install -e .
schematic-transit data/network.json --output exports/busan_gimhae_ulsan_map
```

See [installation and usage](docs/installation-en.md) for a virtual environment, format options, and the Python API.

## Busan-area example

The included dataset covers operating Busan Lines 1–4, Busan–Gimhae LRT, and Donghae commuter rail through Taehwagang. It also includes planned Yangsan Line, the Sasang–Hadan section of Busan Line 5, and BuTX. The Gyeongjeon–Donghae connection is a **map concept**, not an announced through service. Planned names and alignments may change. The diagram is not to scale and is unsuitable for journey planning.

Source checks (2026-09-26): [Busan Metro](https://data.humetro.busan.kr/homepage/default/page/subLocation.do?menu_no=10010101), [Busan–Gimhae LRT](https://www.bglrt.com/00012.web), [KORAIL Donghae](https://info.korail.com/info/contents.do?key=863), [Yangsan Line stations](https://www.busan.go.kr/news/totalnews01/view?curPage=1&dataNo=72491), [Sasang–Hadan construction notice](https://www.busan.go.kr/nbgosi/view?curPage=2&gosiGbn=A&sno=77896), [BuTX plan](https://www.busan.go.kr/mayor/briefing/1581500), and [Bujeon–Masan status](https://www.busan.go.kr/nbtnewsBU/1750969?curPage=9&srchBeginDt=&srchEndDt=&srchKey=&srchText=).
