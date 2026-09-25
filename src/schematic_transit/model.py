"""Validated, transport-agnostic network data model."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

Status = Literal["open", "planned", "concept"]
Point = tuple[float, float]


def _point(value: object, description: str) -> Point:
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise ValueError(f"{description} must be [x, y]")
    try:
        return float(value[0]), float(value[1])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{description} must contain numbers") from exc


@dataclass(frozen=True)
class Line:
    id: str
    name: str
    status: Status
    color: str
    stations: tuple[str, ...]
    anchors: dict[str, Point] = field(default_factory=dict)
    bend_order: Literal["diagonal_first", "axial_first"] = "diagonal_first"
    note: str = ""


@dataclass(frozen=True)
class Network:
    lines: tuple[Line, ...]
    positions: dict[str, Point]
    labels: dict[str, str] = field(default_factory=dict)
    label_offsets: dict[str, Point] = field(default_factory=dict)
    title: str = "Schematic transit map"
    as_of: str = ""
    footer: str = "Solid: operating  ·  long dash: planned  ·  short dash: concept  |  schematic, not to scale"

    @classmethod
    def from_dict(cls, source: dict) -> "Network":
        if not isinstance(source, dict) or not isinstance(source.get("lines"), list) or not source["lines"]:
            raise ValueError("A network needs a nonempty lines list")
        positions = {key: _point(value, f"position {key}") for key, value in source.get("positions", {}).items()}
        labels = source.get("labels", {})
        if not isinstance(labels, dict):
            raise ValueError("labels must be an object")
        label_offsets = {key: _point(value, f"label offset {key}")
                         for key, value in source.get("label_offsets", {}).items()}
        lines = []
        all_stations = Counter()
        ids = set()
        for entry in source["lines"]:
            line_id = entry["id"]
            stations = tuple(entry["stations"])
            if line_id in ids:
                raise ValueError(f"Duplicate line id: {line_id}")
            ids.add(line_id)
            if entry["status"] not in ("open", "planned", "concept"):
                raise ValueError(f"Unknown status on {line_id}")
            if len(stations) < 2 or len(stations) != len(set(stations)):
                raise ValueError(f"Line {line_id} needs at least two distinct stations")
            anchors = {key: _point(value, f"anchor {line_id}/{key}") for key, value in entry.get("anchors", {}).items()}
            if set(anchors) - set(stations):
                raise ValueError(f"Anchor does not belong to line {line_id}")
            bend_order = entry.get("bend_order", "diagonal_first")
            if bend_order not in ("diagonal_first", "axial_first"):
                raise ValueError(f"Unknown bend order on {line_id}")
            for station in stations:
                if station in positions and station in anchors and positions[station] != anchors[station]:
                    raise ValueError(f"Conflicting coordinates for {station}")
                all_stations[station] += 1
            lines.append(Line(line_id, entry["name"], entry["status"], entry["color"],
                              stations, anchors, bend_order, entry.get("note", "")))
        unanchored_interchanges = [station for station, count in all_stations.items()
                                   if count > 1 and station not in positions]
        if unanchored_interchanges:
            raise ValueError(f"Shared stations need global positions: {', '.join(unanchored_interchanges)}")
        for line in lines:
            for station in (line.stations[0], line.stations[-1]):
                if station not in positions and station not in line.anchors:
                    raise ValueError(f"End station {station} on {line.id} needs an anchor")
        return cls(tuple(lines), positions, labels, label_offsets, source.get("title", "Schematic transit map"),
                   source.get("as_of", ""),
                   source.get("footer", "Solid: operating  ·  long dash: planned  ·  short dash: concept  |  schematic, not to scale"))


def load_network(path: str | Path) -> Network:
    return Network.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
