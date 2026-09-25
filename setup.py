from setuptools import find_packages, setup

setup(
    name="schematic-transit",
    version="0.1.0",
    description="Data-driven octilinear transit maps with Matplotlib",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["matplotlib>=3.7"],
    entry_points={"console_scripts": ["schematic-transit=schematic_transit.cli:main"]},
)
