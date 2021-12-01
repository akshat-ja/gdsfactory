""" You can import gdsfactory.as gf

functions:
    - import_gds(): returns a Component from a GDS

classes:

    - Component
    - Port
    - CONFIG
    - TECH

modules:

    - c: components
    - routing

isort:skip_file
"""

from functools import partial
from phidl import quickplot as plot
from phidl.device_layout import Group, Path

# NOTE: import order matters. Only change the order if you know what you are doing
from gdsfactory.component import Component, ComponentReference
from gdsfactory.config import CONFIG, call_if_func
from gdsfactory.port import Port
from gdsfactory.cell import cell
from gdsfactory.cell import cell_without_validator
from gdsfactory.cell import clear_cache
from gdsfactory.tech import LAYER
from gdsfactory.show import show
from gdsfactory.import_gds import import_gds
from gdsfactory.cross_section import CrossSection
from gdsfactory.add_text import add_text
from gdsfactory.types import Label

from gdsfactory import cross_section
from gdsfactory import asserts
from gdsfactory import components
from gdsfactory import routing
from gdsfactory import klive
from gdsfactory import port
from gdsfactory import types
from gdsfactory import path
from gdsfactory import snap
from gdsfactory import tech
from gdsfactory import read
from gdsfactory import remove
from gdsfactory import layers
from gdsfactory import add_termination
from gdsfactory import add_grating_couplers
from gdsfactory import functions
from gdsfactory import export
from gdsfactory import geometry
from gdsfactory import mask
from gdsfactory import sweep

from gdsfactory.tech import TECH
from gdsfactory.add_tapers import add_tapers
from gdsfactory.add_padding import (
    add_padding,
    get_padding_points,
    add_padding_container,
)
from gdsfactory.add_pins import add_pins, add_pins_to_references
from gdsfactory.fill import fill_rectangle
from gdsfactory.pack import pack
from gdsfactory.grid import grid


c = components

__all__ = [
    "CONFIG",
    "Component",
    "ComponentReference",
    "CrossSection",
    "Group",
    "LAYER",
    "Path",
    "Port",
    "TECH",
    "add_grating_couplers",
    "add_padding",
    "add_padding_container",
    "add_pins",
    "add_pins_to_references",
    "add_tapers",
    "add_termination",
    "add_text",
    "asserts",
    "geometry",
    "c",
    "call_if_func",
    "cell",
    "cell_without_validator",
    "clear_cache",
    "components",
    "cross_section",
    "export",
    "fill_rectangle",
    "functions",
    "get_padding_points",
    "grid",
    "import_gds",
    "klive",
    "layers",
    "mask",
    "pack",
    "path",
    "partial",
    "plot",
    "port",
    "read",
    "remove",
    "routing",
    "show",
    "snap",
    "tech",
    "types",
    "sweep",
    "Label",
]
__version__ = "3.6.7"


if __name__ == "__main__":
    print(__all__)
