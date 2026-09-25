"""Find exactly coincident portions of octilinear routes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .layout import Layout
from .model import Point

_TOLERANCE = 1e-7


@dataclass(frozen=True)
class SharedSegment:
    start: Point
    end: Point
    line_ids: tuple[str, ...]


def _axis(a: Point, b: Point) -> tuple[tuple[str, float], float, float] | None:
    x0, y0 = a
    x1, y1 = b
    dx, dy = x1 - x0, y1 - y0
    if abs(dx) <= _TOLERANCE and abs(dy) <= _TOLERANCE:
        return None
    if abs(dy) <= _TOLERANCE:
        return ("h", round(y0, 7)), min(x0, x1), max(x0, x1)
    if abs(dx) <= _TOLERANCE:
        return ("v", round(x0, 7)), min(y0, y1), max(y0, y1)
    if abs(abs(dx) - abs(dy)) <= _TOLERANCE:
        if dx * dy > 0:
            return ("up", round(y0 - x0, 7)), min(x0, x1), max(x0, x1)
        return ("down", round(y0 + x0, 7)), min(x0, x1), max(x0, x1)
    raise ValueError(f"Non-octilinear route segment: {a} to {b}")


def _point(axis: tuple[str, float], value: float) -> Point:
    kind, constant = axis
    if kind == "h":
        return value, constant
    if kind == "v":
        return constant, value
    if kind == "up":
        return value, value + constant
    return value, constant - value


def find_shared_segments(layout: Layout) -> tuple[SharedSegment, ...]:
    """Return maximal straight intervals used by at least two lines.

    Partial overlaps and reversed directions are handled. The order of
    ``line_ids`` follows the input network, keeping stripe order stable.
    """
    intervals = defaultdict(list)
    line_order = {line.id: index for index, line in enumerate(layout.network.lines)}
    for line in layout.network.lines:
        path = layout.paths[line.id]
        for a, b in zip(path, path[1:]):
            segment = _axis(a, b)
            if segment is not None:
                axis, low, high = segment
                intervals[axis].append((low, high, line.id))

    shared = []
    for axis, spans in intervals.items():
        bounds = sorted({value for low, high, _ in spans for value in (low, high)})
        active: list[tuple[float, float, tuple[str, ...]]] = []
        for low, high in zip(bounds, bounds[1:]):
            if high - low <= _TOLERANCE:
                continue
            midpoint = (low + high) / 2
            ids = {line_id for start, stop, line_id in spans
                   if start - _TOLERANCE <= midpoint <= stop + _TOLERANCE}
            if len(ids) < 2:
                continue
            ordered = tuple(sorted(ids, key=line_order.__getitem__))
            if active and active[-1][2] == ordered and abs(active[-1][1] - low) <= _TOLERANCE:
                active[-1] = (active[-1][0], high, ordered)
            else:
                active.append((low, high, ordered))
        shared.extend(SharedSegment(_point(axis, low), _point(axis, high), ids)
                      for low, high, ids in active)
    return tuple(shared)
