# JSON data format

**English** · [한국어](data-format-ko.md)

[← English home](../README.en.md) · [Installation and usage](installation-en.md) · [Busan-area data](../data/network.json) · [Minimal example](../examples/minimal.json)

One JSON file defines a network. Coordinates are **diagram positions**, not latitude and longitude.

## Complete example

```json
{
  "title": "Example network",
  "as_of": "2026-09-26",
  "footer": "Solid: operating · dashed: planned | not to scale",
  "positions": {"A": [0, 0], "C": [8, 4], "E": [8, 8]},
  "labels": {"C": "Central"},
  "label_offsets": {"C": [0.5, 1.0]},
  "lines": [
    {
      "id": "red",
      "name": "Red Line",
      "status": "open",
      "color": "#d84a4a",
      "stations": ["A", "B", "C"],
      "anchors": {"B": [4, 4]},
      "bend_order": "diagonal_first"
    },
    {
      "id": "blue",
      "name": "Blue Line",
      "status": "planned",
      "color": "#3478ba",
      "stations": ["C", "D", "E"]
    }
  ]
}
```

## Network fields

| Field | Required | Meaning |
| --- | --- | --- |
| `lines` | Yes | Array of lines; each needs at least two stations |
| `positions` | Conditional | `[x, y]` coordinates for shared stations and line endpoints; endpoints may instead be set in line `anchors` |
| `title` | No | Map title |
| `as_of` | No | Subtitle text, typically a reference date |
| `footer` | No | Footer text |
| `labels` | No | Display names keyed by station ID |
| `label_offsets` | No | `[horizontal, vertical]` label adjustments keyed by station ID |

Use the same station ID across lines for a shared interchange, and assign its coordinate once in `positions`. If two distinct stations share a name, use different IDs and control their displayed names with `labels`.

## Line fields

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | Yes | Unique line ID |
| `name` | Yes | Name shown in the legend |
| `status` | Yes | `open`, `planned`, or `concept` |
| `color` | Yes | Line color, such as `#d84a4a` |
| `stations` | Yes | Station IDs in travel order |
| `anchors` | No | Intermediate station positions used to shape the route |
| `bend_order` | No | `diagonal_first` (default) or `axial_first` |
| `note` | No | Stored metadata; not currently printed on the map |

## Coordinates and layout

The layout joins adjacent anchors using horizontal, vertical, and 45° segments. `diagonal_first` takes the diagonal segment first; `axial_first` takes the horizontal or vertical segment first. Intermediate stations are spaced along that path. Add more station anchors to shape long routes.

A bend can occur between two station markers. If you draw the layout yourself, use the resulting `paths` rather than joining station coordinates directly. The [layout engine](../src/schematic_transit/layout.py) and [renderer](../src/schematic_transit/render.py) already handle this.

When two or more routes share the same straight interval, the [overlap detector](../src/schematic_transit/overlap.py) identifies it. The renderer widens that interval into parallel colored stripes and tapers them back to the route centerline at each end. See the [three-line example](../examples/overlap.json).

The current version does **not** globally optimize line crossings or label collisions. Adjust routes with `positions` and `anchors`, and labels with `label_offsets`. The [model validator](../src/schematic_transit/model.py) reports invalid statuses, duplicate line IDs, and shared stations without global coordinates.

[← English home](../README.en.md) · [Installation and usage →](installation-en.md)
