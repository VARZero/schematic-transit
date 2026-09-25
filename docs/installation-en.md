# Installation and usage

**English** · [한국어](installation-ko.md)

[← English home](../README.en.md) · [JSON data format](data-format-en.md) · [Busan-area data](../data/network.json) · [Minimal example](../examples/minimal.json)

## 1. Install

Use Python 3.10 or later. From the project root, where `README.en.md` is located:

```sh
python3 -m pip install -e .
```

The editable install reflects source changes without reinstalling. To use a virtual environment on macOS or Linux:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. The installed `schematic-transit` command works on each platform. On macOS or Linux, you can also run without installation:

```sh
PYTHONPATH=src python3 -m schematic_transit.cli data/network.json --output exports/busan_gimhae_ulsan_map
```

## 2. Render the Busan-area example

```sh
schematic-transit data/network.json --output exports/busan_gimhae_ulsan_map
```

This creates [PNG](../exports/busan_gimhae_ulsan_map.png), [SVG](../exports/busan_gimhae_ulsan_map.svg), and [PDF](../exports/busan_gimhae_ulsan_map.pdf). `--output` is a filename stem without an extension. SVG retains editable text.

Choose formats or PNG resolution explicitly:

```sh
schematic-transit data/network.json --output exports/my_map --formats svg pdf
schematic-transit data/network.json --output exports/my_map --formats png --dpi 200
```

## 3. Create a new map

Copy the [minimal JSON example](../examples/minimal.json), then edit its title, lines, stations, and anchor coordinates. See the [data format guide](data-format-en.md) for every field.

The [overlap example](../examples/overlap.json) and its [PNG output](../exports/overlap_demo.png) show three lines sharing one corridor.

```sh
schematic-transit examples/minimal.json --output exports/minimal
```

## 4. Python API

```python
from schematic_transit import load_network, OctilinearLayout, render

network = load_network("data/network.json")
layout = OctilinearLayout().build(network)
files = render(layout, "exports/my_map", formats=("svg", "pdf"))
print(files["svg"])
```

The [public API](../src/schematic_transit/__init__.py) exports `Network`, `Line`, `OctilinearLayout`, `load_network`, and `render`. Implementation is split into [model and validation](../src/schematic_transit/model.py), [layout](../src/schematic_transit/layout.py), [rendering](../src/schematic_transit/render.py), and [CLI](../src/schematic_transit/cli.py).

## 5. Tests

```sh
PYTHONPATH=src python3 -m unittest discover -s tests
```

The [tests](../tests/test_layout.py) cover octilinear segments, bend order, and shared-station anchor validation.

[← English home](../README.en.md) · [JSON data format →](data-format-en.md)
