import unittest
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import rcParams

from schematic_transit import Network, OctilinearLayout, octilinear_path, find_shared_segments, load_network
from schematic_transit.render import _font, _place_labels


class LayoutTests(unittest.TestCase):
    def test_paths_use_only_octilinear_segments(self):
        network = Network.from_dict({
            "positions": {"A": [0, 0], "C": [8, 4]},
            "lines": [{"id": "r", "name": "R", "status": "open", "color": "red",
                       "stations": ["A", "B", "C"]}],
        })
        layout = OctilinearLayout().build(network)
        self.assertEqual(layout.paths["r"], ((0.0, 0.0), (4.0, 4.0), (8.0, 4.0)))
        self.assertEqual(layout.stations["A"], (0.0, 0.0))
        self.assertEqual(layout.stations["C"], (8.0, 4.0))
        for a, b in zip(layout.paths["r"], layout.paths["r"][1:]):
            dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
            self.assertTrue(dx == 0 or dy == 0 or dx == dy)

    def test_axial_first_selects_other_bend(self):
        self.assertEqual(octilinear_path((0, 0), (8, 4), "axial_first"),
                         ((0, 0), (4, 0), (8, 4)))

    def test_shared_station_requires_global_anchor(self):
        with self.assertRaisesRegex(ValueError, "Shared stations need global positions"):
            Network.from_dict({
                "positions": {"A": [0, 0], "C": [8, 0], "D": [8, 8]},
                "lines": [
                    {"id": "r", "name": "R", "status": "open", "color": "red", "stations": ["A", "B", "C"]},
                    {"id": "b", "name": "B", "status": "open", "color": "blue", "stations": ["B", "D"]},
                ],
            })

    def test_partial_overlap_and_reverse_direction_form_one_bundle(self):
        network = Network.from_dict({
            "positions": {"A": [0, 0], "B": [4, 0], "C": [12, 0], "D": [16, 0],
                          "E": [4, 4], "F": [12, 4]},
            "lines": [
                {"id": "red", "name": "Red", "status": "open", "color": "red", "stations": ["A", "D"]},
                {"id": "blue", "name": "Blue", "status": "open", "color": "blue", "stations": ["C", "B"]},
                {"id": "green", "name": "Green", "status": "open", "color": "green", "stations": ["E", "B", "C", "F"]},
            ],
        })
        shared = find_shared_segments(OctilinearLayout().build(network))
        self.assertEqual(len(shared), 1)
        self.assertEqual(shared[0].start, (4.0, 0.0))
        self.assertEqual(shared[0].end, (12.0, 0.0))
        self.assertEqual(shared[0].line_ids, ("red", "blue", "green"))

    def test_diagonal_partial_overlap(self):
        network = Network.from_dict({
            "positions": {"A": [0, 0], "B": [2, 2], "C": [6, 6], "D": [8, 8]},
            "lines": [
                {"id": "red", "name": "Red", "status": "open", "color": "red", "stations": ["A", "D"]},
                {"id": "blue", "name": "Blue", "status": "planned", "color": "blue", "stations": ["B", "C"]},
            ],
        })
        shared = find_shared_segments(OctilinearLayout().build(network))
        self.assertEqual([(s.start, s.end, s.line_ids) for s in shared],
                         [((2.0, 2.0), (6.0, 6.0), ("red", "blue"))])

    def test_busan_example_keeps_shared_and_bgl_anchors(self):
        data = Path(__file__).resolve().parents[1] / "data" / "network.json"
        network = load_network(data)
        layout = OctilinearLayout().build(network)
        for name in ("사상", "대저", "가야대"):
            self.assertEqual(layout.stations[name], network.positions[name])
        bgl = next(line for line in network.lines if line.id == "bgl")
        self.assertEqual(bgl.stations[0], "사상")
        self.assertEqual(bgl.stations[-1], "가야대")
        self.assertLess(layout.stations["가야대"][0], layout.stations["대저"][0])
        self.assertLess(layout.stations["대저"][0], layout.stations["사상"][0])

    def test_busan_example_labels_do_not_overlap(self):
        rcParams["font.family"] = _font()
        data = Path(__file__).resolve().parents[1] / "data" / "network.json"
        layout = OctilinearLayout().build(load_network(data))
        fig, ax = plt.subplots(figsize=(40, 28))
        try:
            fig.subplots_adjust(left=0.03, right=0.97, top=0.90, bottom=0.11)
            xs, ys = zip(*layout.stations.values())
            ax.set_xlim(min(xs) - 7, max(xs) + 10)
            ax.set_ylim(min(ys) - 5, max(ys) + 6)
            ax.set_aspect("equal", adjustable="box")
            memberships = defaultdict(list)
            for line in layout.network.lines:
                for index, name in enumerate(line.stations):
                    memberships[name].append((line, index))
            artists = _place_labels(ax, fig, layout, memberships)
            self.assertEqual(len(artists), len(layout.stations))
            fig.canvas.draw()
            boxes = [artist.get_window_extent(fig.canvas.get_renderer()) for artist in artists]
            self.assertFalse(any(a.overlaps(b) for i, a in enumerate(boxes)
                                 for b in boxes[i + 1:]))
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
