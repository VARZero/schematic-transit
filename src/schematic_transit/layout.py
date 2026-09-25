"""Deterministic 0°/45°/90° route layout between user-provided anchors."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot, isclose

from .model import Network, Point


def octilinear_path(start: Point, end: Point, bend_order: str = "diagonal_first") -> tuple[Point, ...]:
    """Shortest one-bend octilinear connection between two points.

    The returned polyline is exact; renderers must draw this path instead of
    directly connecting station markers, which may straddle a bend.
    """
    x0, y0 = start
    x1, y1 = end
    dx, dy = x1 - x0, y1 - y0
    diagonal = min(abs(dx), abs(dy))
    if isclose(diagonal, 0) or isclose(abs(dx), abs(dy)):
        return (start, end)
    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1
    if bend_order == "diagonal_first":
        bend = (x0 + sx * diagonal, y0 + sy * diagonal)
    elif bend_order == "axial_first":
        bend = (x1 - sx * diagonal, y1 - sy * diagonal)
    else:
        raise ValueError(f"Unknown bend order: {bend_order}")
    return (start, bend, end)


def _sample(path: tuple[Point, ...], fraction: float) -> Point:
    if fraction <= 0:
        return path[0]
    if fraction >= 1:
        return path[-1]
    lengths = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(path, path[1:])]
    total = sum(lengths)
    if total == 0:
        raise ValueError("Coincident anchors cannot contain distinct stations")
    remaining = fraction * total
    for (a, b), length in zip(zip(path, path[1:]), lengths):
        if remaining <= length + 1e-9:
            t = min(1.0, max(0.0, remaining / length))
            return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        remaining -= length
    return path[-1]


@dataclass(frozen=True)
class Layout:
    network: Network
    stations: dict[str, Point]
    paths: dict[str, tuple[Point, ...]]


class OctilinearLayout:
    """Place intermediate stations along octilinear paths between anchors.

    Shared stations must have coordinates in ``Network.positions``. Additional
    bends can be controlled by adding station anchors to individual lines.
    """

    def build(self, network: Network) -> Layout:
        stations: dict[str, Point] = {}
        paths: dict[str, tuple[Point, ...]] = {}
        for line in network.lines:
            anchors = {i: network.positions[name] for i, name in enumerate(line.stations)
                       if name in network.positions}
            anchors.update({i: line.anchors[name] for i, name in enumerate(line.stations)
                            if name in line.anchors})
            route: list[Point] = []
            for first, last in zip(sorted(anchors), sorted(anchors)[1:]):
                path = octilinear_path(anchors[first], anchors[last], line.bend_order)
                route.extend(path if not route else path[1:])
                for i in range(first, last + 1):
                    name = line.stations[i]
                    point = _sample(path, (i - first) / (last - first))
                    if name in stations and (abs(stations[name][0] - point[0]) > 1e-8 or
                                             abs(stations[name][1] - point[1]) > 1e-8):
                        raise ValueError(f"Inconsistent shared station location: {name}")
                    stations[name] = point
            paths[line.id] = tuple(route)
        return Layout(network, stations, paths)
