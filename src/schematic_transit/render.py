"""Matplotlib renderer with labels, interchanges, status styles and exports."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from math import hypot

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox

from .layout import Layout
from .overlap import find_shared_segments


def _font() -> str:
    available = {item.name for item in font_manager.fontManager.ttflist}
    return next((name for name in ("Apple SD Gothic Neo", "Nanum Gothic", "Noto Sans CJK KR",
                                   "Malgun Gothic") if name in available), "DejaVu Sans")


def _draw_shared_segments(ax, fig, layout: Layout) -> None:
    """Cover coincident segments with wider, side-by-side colored strokes.

    Each colored stroke converges on the original centerline at both ends,
    so incoming and outgoing single-line routes still meet the bundle.
    """
    shared = find_shared_segments(layout)
    if not shared:
        return
    by_id = {line.id: line for line in layout.network.lines}
    fig.canvas.draw()  # Finalize the data-to-display transform before point offsets.
    inverse = ax.transData.inverted()
    points_to_pixels = fig.dpi / 72
    stripe_width = 3.8
    stripe_step = 4.0
    for segment in shared:
        a = ax.transData.transform(segment.start)
        b = ax.transData.transform(segment.end)
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = hypot(dx, dy)
        if length <= 0:
            continue
        tangent = (dx / length, dy / length)
        normal = (-tangent[1], tangent[0])
        count = len(segment.line_ids)
        total_width = (count - 1) * stripe_step + stripe_width
        ax.plot((segment.start[0], segment.end[0]), (segment.start[1], segment.end[1]),
                color="white", linewidth=total_width + 3.5, solid_capstyle="round", zorder=4)
        taper = min(9 * points_to_pixels, length * 0.28)
        for index, line_id in enumerate(segment.line_ids):
            line = by_id[line_id]
            displacement = (index - (count - 1) / 2) * stripe_step * points_to_pixels
            start_offset = (a[0] + tangent[0] * taper + normal[0] * displacement,
                            a[1] + tangent[1] * taper + normal[1] * displacement)
            end_offset = (b[0] - tangent[0] * taper + normal[0] * displacement,
                          b[1] - tangent[1] * taper + normal[1] * displacement)
            display_path = (a, start_offset, end_offset, b)
            data_path = [inverse.transform(point) for point in display_path]
            xs, ys = zip(*data_path)
            style = {"open": "solid", "planned": (0, (5, 3)), "concept": (0, (2, 3))}[line.status]
            ax.plot(xs, ys, color=line.color, linewidth=stripe_width, linestyle=style,
                    solid_capstyle="round", solid_joinstyle="round", zorder=5)


def _place_labels(ax, fig, layout: Layout, memberships: dict) -> list:
    """Place labels in display space, keeping text clear of other labels and stops.

    The map's data units can have very different on-screen sizes depending on
    figure size. Collision checks therefore use the actual output renderer.
    Explicit label offsets are tried first, then nearby alternatives.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    scale = fig.dpi / 72
    stop_points = {name: ax.transData.transform(point)
                   for name, point in layout.stations.items()}
    stop_boxes = {name: Bbox.from_bounds(px - 5 * scale, py - 5 * scale,
                                         10 * scale, 10 * scale)
                  for name, (px, py) in stop_points.items()}
    labels = []
    occupied = []

    def density(name):
        x, y = stop_points[name]
        nearest = min((hypot(x - px, y - py) for other, (px, py) in stop_points.items()
                       if other != name), default=float("inf"))
        return (nearest, -len(memberships[name]), name)

    for name in sorted(layout.stations, key=density):
        x, y = layout.stations[name]
        interchange = len(memberships[name]) > 1
        line, index = memberships[name][0]
        label = layout.network.labels.get(name, name)
        artist = ax.text(x, y, label, fontsize=7.5 if not interchange else 8.5,
                         fontweight="bold" if interchange else "normal",
                         color="#26343a", zorder=12,
                         bbox={"facecolor": "#f7f8f5", "edgecolor": "none", "alpha": 0.9, "pad": 0.4})
        if name in layout.network.label_offsets:
            dx, dy = layout.network.label_offsets[name]
            px, py = stop_points[name]
            target = ax.transData.transform((x + dx, y + dy))
            preferred = ((target[0] - px) / scale, (target[1] - py) / scale)
        elif interchange:
            preferred = (9, 9)
        else:
            route = line.stations
            before = layout.stations[route[max(0, index - 1)]]
            after = layout.stations[route[min(len(route) - 1, index + 1)]]
            tangent = (after[0] - before[0], after[1] - before[1])
            length = hypot(*tangent) or 1
            side = 1 if index % 2 == 0 else -1
            preferred = (-side * tangent[1] / length * 9,
                         side * tangent[0] / length * 9)

        directions = [preferred]
        for radius in (9, 16, 25, 36, 50, 68, 90, 120):
            directions.extend((sx * radius, sy * radius) for sx, sy in
                              ((1, 0), (-1, 0), (0, 1), (0, -1),
                               (0.72, 0.72), (-0.72, 0.72),
                               (0.72, -0.72), (-0.72, -0.72)))
        origin = stop_points[name]
        best = None
        for dx, dy in directions:
            target = (origin[0] + dx * scale, origin[1] + dy * scale)
            artist.set_position(ax.transData.inverted().transform(target))
            artist.set_ha("left" if dx > 1 else "right" if dx < -1 else "center")
            artist.set_va("bottom" if dy > 1 else "top" if dy < -1 else "center")
            box = artist.get_window_extent(renderer).padded(3 * scale)
            if not ax.bbox.contains(box.x0, box.y0) or not ax.bbox.contains(box.x1, box.y1):
                continue
            if any(box.overlaps(other) for other in occupied):
                continue
            if any(box.overlaps(other) for other_name, other in stop_boxes.items()
                   if other_name != name):
                continue
            best = (dx, dy, box)
            break
        if best is None:
            artist.remove()
            raise ValueError(f"No collision-free label position for {name}; increase figsize")
        dx, dy, box = best
        occupied.append(box)
        if hypot(dx, dy) > 25:
            # A subtle leader keeps distant labels associated with their stop.
            edge = (max(box.x0, min(origin[0], box.x1)),
                    max(box.y0, min(origin[1], box.y1)))
            start, end = ax.transData.inverted().transform((origin, edge))
            ax.plot((start[0], end[0]), (start[1], end[1]),
                    color="#aab2b2", linewidth=0.6, zorder=10)
        labels.append(artist)
    return labels


def render(layout: Layout, output: str | Path, formats: tuple[str, ...] = ("png", "svg", "pdf"),
           dpi: int = 150, figsize: tuple[float, float] = (40, 28)) -> dict[str, Path]:
    """Render a layout into one or more formats and return output paths.

    ``output`` is a filename stem with no extension. SVG retains editable text.
    """
    if not formats or any(ext not in {"png", "svg", "pdf"} for ext in formats):
        raise ValueError("formats must contain png, svg and/or pdf")
    if dpi < 30:
        raise ValueError("dpi must be at least 30")
    plt.rcParams.update({"font.family": _font(), "svg.fonttype": "none", "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=figsize, facecolor="#f7f8f5")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.90, bottom=0.11)
    ax.set_facecolor("#f7f8f5")
    memberships = defaultdict(list)
    sorted_lines = sorted(layout.network.lines, key=lambda line: {"concept": 0, "planned": 1, "open": 2}[line.status])
    for line in sorted_lines:
        path = layout.paths[line.id]
        xs, ys = zip(*path)
        style = {"open": "solid", "planned": (0, (5, 3)), "concept": (0, (2, 3))}[line.status]
        ax.plot(xs, ys, color="white", linewidth=10 if line.status == "open" else 8,
                linestyle=style, solid_capstyle="round", zorder=1)
        ax.plot(xs, ys, color=line.color, linewidth=5.4 if line.status == "open" else 3.5,
                linestyle=style, solid_capstyle="round", zorder=2 if line.status != "open" else 3)
        for index, name in enumerate(line.stations):
            memberships[name].append((line, index))
    all_x = [point[0] for point in layout.stations.values()]
    all_y = [point[1] for point in layout.stations.values()]
    ax.set_xlim(min(all_x) - 7, max(all_x) + 10)
    ax.set_ylim(min(all_y) - 5, max(all_y) + 6)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    _draw_shared_segments(ax, fig, layout)
    for name, (x, y) in layout.stations.items():
        services = memberships[name]
        operating = [line.color for line, _ in services if line.status == "open"]
        color = operating[0] if operating else services[0][0].color
        if len(services) > 1:
            ax.scatter(x, y, s=245, facecolors="white", edgecolors="#24333a", linewidths=2.1, zorder=7)
            ax.scatter(x, y, s=70, facecolors="#24333a", edgecolors="none", zorder=8)
        else:
            ax.scatter(x, y, s=74, facecolors="white" if operating else "#f7f8f5",
                       edgecolors=color, linewidths=2.0, zorder=6)
    _place_labels(ax, fig, layout, memberships)
    fig.text(0.055, 0.965, layout.network.title, ha="left", va="top",
             fontsize=30, fontweight="bold", color="#1e313a")
    subtitle = "SCHEMATIC TRANSIT MAP"
    if layout.network.as_of:
        subtitle += f"  ·  {layout.network.as_of}"
    fig.text(0.055, 0.965 - 0.55 / figsize[1], subtitle,
             ha="left", va="top", fontsize=13, color="#5a6a70")
    handles = [Line2D([0], [0], color=line.color, lw=5,
                      linestyle={"open": "solid", "planned": (0, (5, 3)), "concept": (0, (2, 3))}[line.status],
                      label=line.name)
               for line in layout.network.lines]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False, fontsize=11,
               bbox_to_anchor=(0.5, 0.047), columnspacing=2.4, handlelength=2.4)
    fig.text(0.055, 0.027, layout.network.footer,
             fontsize=11, ha="left", color="#4d5c62")
    stem = Path(output)
    stem.parent.mkdir(parents=True, exist_ok=True)
    files = {}
    for extension in formats:
        target = stem.with_suffix(f".{extension}")
        fig.savefig(target, dpi=dpi, facecolor=fig.get_facecolor())
        files[extension] = target
    plt.close(fig)
    return files
