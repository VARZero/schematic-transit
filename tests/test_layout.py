import unittest

from schematic_transit import Network, OctilinearLayout, octilinear_path, find_shared_segments


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


if __name__ == "__main__":
    unittest.main()
