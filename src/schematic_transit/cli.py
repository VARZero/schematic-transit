"""Command line interface for JSON networks."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import OctilinearLayout, load_network, render


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a schematic transit map from JSON")
    parser.add_argument("data", type=Path, help="Network JSON file")
    parser.add_argument("--output", type=Path, default=Path("map"), help="Output filename stem")
    parser.add_argument("--formats", nargs="+", choices=("png", "svg", "pdf"), default=("png", "svg", "pdf"))
    parser.add_argument("--dpi", type=int, default=150)
    parser.add_argument("--figsize", nargs=2, type=float, metavar=("WIDTH", "HEIGHT"),
                        default=(40, 28), help="Figure size in inches (default: 40 28)")
    args = parser.parse_args()
    if any(size <= 0 for size in args.figsize):
        parser.error("--figsize values must be positive")
    layout = OctilinearLayout().build(load_network(args.data))
    for path in render(layout, args.output, tuple(args.formats), args.dpi,
                       tuple(args.figsize)).values():
        print(path)


if __name__ == "__main__":
    main()
