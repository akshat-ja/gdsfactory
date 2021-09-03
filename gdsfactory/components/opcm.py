""" CD SEM structures
"""
import itertools as it
from functools import partial
from typing import List, Optional, Tuple

import numpy as np

from gdsfactory.cell import cell
from gdsfactory.component import Component
from gdsfactory.components.bend_circular import bend_circular
from gdsfactory.components.cd import CENTER_SHAPES_MAP, square_middle
from gdsfactory.components.manhattan_font import manhattan_text
from gdsfactory.components.rectangle import rectangle
from gdsfactory.components.straight import straight
from gdsfactory.cross_section import strip
from gdsfactory.tech import LAYER
from gdsfactory.types import ComponentFactory, CrossSectionFactory, Layer

LINE_LENGTH = 420.0


@cell
def _cdsem_generic(
    L=2.0,
    radius=2.0,
    width=0.4,
    center_shapes="SU",
    bend90_factory=bend_circular,
    straight_factory=straight,
    markers_with_slabs=False,
):
    """bends and straights connected together
    for CDSEM measurement
    """

    component = Component()
    _straight = straight_factory(length=L, width=width)
    _bend = bend90_factory(radius=radius, width=width)

    straight1 = _straight.ref(rotation=90, port_id="o1")
    component.add(straight1)

    bend1 = component.add_ref(_bend)
    bend1.connect(port="o2", destination=straight1.ports["o2"])

    straight2 = component.add_ref(_straight)
    straight2.connect(port="o1", destination=bend1.ports["o1"])

    bend2 = component.add_ref(_bend)
    bend2.connect(port="o2", destination=straight2.ports["o2"])

    # Add center shapes.
    # Center the first shape in the list
    # Then stack the others underneath

    center = np.array([radius + L / 2, L / 2])
    center_shape_side = 0.4 if markers_with_slabs else 0.5
    center_shape_spacing = 0.2
    sep = center_shape_side + center_shape_spacing
    for cs_name in center_shapes:
        _shape_func = CENTER_SHAPES_MAP[cs_name]
        _shape = _shape_func(side=center_shape_side)
        _shape_ref = _shape.ref(position=center)
        component.add(_shape_ref)
        component.absorb(_shape_ref)

        # If with slabs, add the square slab on top of each marker
        if markers_with_slabs:
            _shape = square_middle(side=0.5)
            _shape_ref = _shape.ref(position=center)
            component.add(_shape_ref)
            component.absorb(_shape_ref)

        center += (0, -sep)

    return component


@cell
def wg_line(
    length: float,
    width: float,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: Optional[List[Tuple[int, int]]] = None,
) -> Component:
    c = Component()
    _wg = c.add_ref(rectangle(size=(length, width), layer=layer))
    c.absorb(_wg)
    return c


@cell
def cdsem_straight(
    spacing_h: float = 5.0,
    spacing_v: float = 5.0,
    gaps: Tuple[float, ...] = (0.224, 0.234, 0.246),
    length: float = 10.0,
    width_center: float = 0.5,
    label: str = "A",
    straight_factory: ComponentFactory = straight,
    layer: Layer = LAYER.WG,
    layers_cladding=None,
):

    c = Component()
    x = 0
    i = 0

    widths = [width_center * 0.92, width_center, width_center * 1.08]

    marker_label = manhattan_text(
        text=label,
        size=0.4,
        layer=layer,
    )
    _marker_label = c.add_ref(marker_label)
    _marker_label.move((2 * (length + spacing_h) + 2 * spacing_h, 1.5 * spacing_v))
    c.absorb(_marker_label)

    for width in widths:
        y = 0
        # iso line
        _r = wg_line(
            length=length, width=width, layer=layer, layers_cladding=layers_cladding
        )
        _r_ref = c.add_ref(_r)
        _r_ref.move((x, y))
        c.absorb(_r_ref)

        y += width + spacing_v
        # dual lines
        for gap, col_marker_type in zip(gaps, ["S", "L", "H"]):
            wg_line(
                length=length, width=width, layer=layer, layers_cladding=layers_cladding
            )
            _r1_ref = c.add_ref(_r)
            _r1_ref.move((x, y))

            straight_factory(length=length, width=width)
            _r2_ref = c.add_ref(_r)
            _r2_ref.move((x, y + gap + width))
            c.absorb(_r1_ref)
            c.absorb(_r2_ref)

            if i < 2:
                print(col_marker_type)
                marker = CENTER_SHAPES_MAP[col_marker_type](
                    layer=layer,
                )
                _marker = c.add_ref(marker)
                _marker.move((x + length / 2 + spacing_h / 2, y + width + gap / 2))
                c.absorb(_marker)

            y += 2 * width + gap + spacing_v
        i += 1

        x += length + spacing_h

    return c


@cell
def cdsem_straight_column(
    spacing_v: float = 5.0,
    gaps: Tuple[float, ...] = (0.224, 0.234, 0.246),
    length: float = LINE_LENGTH,
    width_center: float = 0.5,
    label: str = "A",
    straight_factory: ComponentFactory = straight,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: List[Tuple[int, int]] = None,
    cross_section: CrossSectionFactory = strip,
) -> Component:

    c = Component()
    x = 0

    widths = [width_center * 0.92, width_center, width_center * 1.08]

    y = 0
    for j, width in enumerate(widths):
        cross_section = partial(cross_section, width=width, layer=layer)
        _r = straight_factory(length=length, cross_section=cross_section)
        _r_ref = c.add_ref(_r)
        _r_ref.move((x, y))
        c.absorb(_r_ref)

        y += width + spacing_v

        marker_label = manhattan_text(
            text="{}{}".format(label, j + 1),
            size=0.4,
            layer=layer,
        )
        _marker_label = c.add_ref(marker_label)
        _marker_label.move((length + 6, y))
        c.absorb(_marker_label)

        # dual lines
        for gap, col_marker_type in zip(gaps, ["S", "L", "H"]):
            wg_line(
                length=length, width=width, layer=layer, layers_cladding=layers_cladding
            )
            _r1_ref = c.add_ref(_r)
            _r1_ref.move((x, y))

            wg_line(
                length=length, width=width, layer=layer, layers_cladding=layers_cladding
            )
            _r2_ref = c.add_ref(_r)
            _r2_ref.move((x, y + gap + width))
            c.absorb(_r1_ref)
            c.absorb(_r2_ref)

            # if i < 2:
            marker = CENTER_SHAPES_MAP[col_marker_type](
                layer=layer,
            )
            _marker = c.add_ref(marker)
            _marker.move((length + 3, y + width + gap / 2))
            c.absorb(_marker)

            y += 2 * width + gap + spacing_v
        # i += 1
        y += spacing_v + 2 * width

    return c


@cell
def cdsem_straight_all(
    straight_factory: ComponentFactory = straight,
    cross_section: CrossSectionFactory = strip,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: List[Tuple[int, int]] = None,
    widths: Tuple[float, ...] = (0.4, 0.45, 0.5, 0.6, 0.8, 1.0),
    labels: Tuple[str, ...] = ("A", "B", "C", "D", "E", "F"),
) -> Component:
    c = Component()
    spacing_v = 10.0
    y = 0
    for width, label in zip(widths, labels):
        cross_section = partial(cross_section, width=width, layer=layer)
        _c = cdsem_straight_column(
            width_center=width,
            label=label,
            straight_factory=straight_factory,
            layer=layer,
            layers_cladding=layers_cladding,
            cross_section=cross_section,
        )
        y -= _c.size_info.south
        cr = c.add_ref(_c)
        cr.movey(y)
        y = cr.size_info.north + spacing_v

    return c


@cell
def cdsem_straight_density(
    width: float = 0.372,
    trench_width: float = 0.304,
    x: float = LINE_LENGTH,
    y: float = 50.0,
    margin: float = 2.0,
    label: str = "",
    straight_factory: ComponentFactory = straight,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: Optional[Tuple[Layer, ...]] = None,
    cross_section: CrossSectionFactory = strip,
) -> Component:
    """horizontal grating etch lines

    TE: 676nm pitch, 304nm gap, 372nm line
    TM: 1110nm pitch, 506nm gap, 604nm line

    Args:
        width: width
        trench_width: trench_width
    """
    c = Component()
    period = width + trench_width
    n_o_lines = int((y - 2 * margin) / period)
    length = x - 2 * margin

    cross_section = partial(cross_section, width=width, layer=layer)
    tooth = straight_factory(length=length, cross_section=cross_section)

    for i in range(n_o_lines):
        tooth_ref = c.add_ref(tooth)
        tooth_ref.movey((-n_o_lines / 2 + 0.5 + i) * period)
        c.absorb(tooth_ref)

    marker_label = manhattan_text(
        text=f"{label}",
        size=1.0,
        layer=layer,
    )
    _marker_label = c.add_ref(marker_label)
    _marker_label.move((length + 3, 10.0))
    c.absorb(_marker_label)
    return c


@cell
def cdsem_strip(straight_factory=straight, **kwargs):
    return _cdsem_generic(
        **kwargs, bend90_factory=bend_circular, straight_factory=straight_factory
    )


@cell
def cdsem_target(
    bend90_factory: ComponentFactory = bend_circular,
    width_center: float = 0.5,
    label: str = "",
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: List[Tuple[int, int]] = None,
    radii: Tuple[float, ...] = (5.0, 10.0),
    cross_section: CrossSectionFactory = strip,
) -> Component:
    c = Component()
    a = 1.0
    w = 3 * a / 4

    for pos in [(0, 0), (w, w), (-w, w), (w, -w), (-w, -w)]:
        _c = c.add_ref(square_middle(layer=layer))
        _c.move(pos)
        c.absorb(_c)

    w_min = width_center * 0.92
    w0 = width_center
    w_max = width_center * 1.08

    for radius in radii:
        b = a + radius
        cross_section = partial(cross_section, width=w0, layer=layer)
        _b_tr = bend90_factory(radius=radius, cross_section=cross_section)
        b_tr = _b_tr.ref(position=(b, a), rotation=90, port_id="o1")

        _b_bl = bend90_factory(radius=radius, cross_section=cross_section)
        b_bl = _b_bl.ref(position=(-b, -a), rotation=270, port_id="o1")

        cross_section = partial(cross_section, width=w_max, layer=layer)
        _b_br = bend90_factory(radius=radius, cross_section=cross_section)
        b_br = _b_br.ref(position=(a, -b), rotation=0, port_id="o1")

        cross_section = partial(cross_section, width=w_min, layer=layer)
        _b_tl = bend90_factory(radius=radius, cross_section=cross_section)
        b_tl = _b_tl.ref(position=(-a, b), rotation=180, port_id="o1")

        c.add([b_tr, b_tl, b_bl, b_br])

    if label:
        marker_label = manhattan_text(text=str(label), size=1.0, layer=layer)
        _marker_label = c.add_ref(marker_label)
        _marker_label.movey(-max(radii) - 10.0)
        c.absorb(_marker_label)

    return c


@cell
def cdsem_uturn(
    width: float = 0.5,
    radius: float = 10.0,
    symbol_bot: str = "S",
    symbol_top: str = "U",
    wg_length: float = LINE_LENGTH,
    straight_factory: ComponentFactory = straight,
    bend90_factory: ComponentFactory = bend_circular,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: List[Tuple[int, int]] = None,
    cross_section: CrossSectionFactory = strip,
) -> Component:
    """

    Args:
        width: of the line
        cladding_offset:
        radius: bend radius
        wg_length

    """
    c = Component()
    r = radius

    cross_section = partial(cross_section, width=width, layer=layer)
    if wg_length is None:
        wg_length = 2 * r

    bend90 = bend90_factory(cross_section=cross_section, radius=r)
    wg = straight_factory(
        cross_section=cross_section,
        length=wg_length,
    )

    # Add the U-turn on straight layer
    b1 = c.add_ref(bend90)
    b2 = c.add_ref(bend90)

    b2.connect("o2", b1.ports["o1"])

    wg1 = c.add_ref(wg)
    wg1.connect("o1", b1.ports["o2"])

    wg2 = c.add_ref(wg)
    wg2.connect("o1", b2.ports["o1"])

    label = c << manhattan_text(text=str(int(width * 1e3)), size=0.4, layer=LAYER.WG)
    label.rotate(-90)
    label.movey(r)

    c.rotate(angle=90)
    return c


@cell
def pcm_optical(
    widths: Tuple[float, ...] = (0.4, 0.45, 0.5, 0.6, 0.8, 1.0),
    labels: Tuple[str, ...] = ("A", "B", "C", "D", "E", "F"),
    widths_bend: Tuple[float, ...] = (0.4, 0.45, 0.5, 0.7, 0.8, 0.9),
    labels_bend: Tuple[str, ...] = ("A", "B", "C", "D", "E", "F"),
    dense_lines_width: float = 0.372,
    dense_lines_width_difference: float = 20e-3,
    dense_lines_gap: float = 0.304,
    dense_lines_labels: Tuple[str, ...] = ("DL", "DM", "DH"),
    straight_factory: ComponentFactory = straight,
    bend90_factory: ComponentFactory = bend_circular,
    layer: Tuple[int, int] = LAYER.WG,
    layers_cladding: List[Tuple[int, int]] = None,
    cross_section: CrossSectionFactory = strip,
) -> Component:
    """column with all optical PCMs

    Args:
        widths:  for straight

    """
    c = Component()
    _c1 = cdsem_straight_all(
        straight_factory=straight_factory,
        layer=layer,
        layers_cladding=layers_cladding,
        cross_section=cross_section,
        widths=widths,
        labels=labels,
    )

    all_devices = [_c1]

    all_devices += [
        cdsem_uturn(
            width=w,
            symbol_top=s,
            straight_factory=straight_factory,
            bend90_factory=bend90_factory,
            layer=layer,
            layers_cladding=layers_cladding,
            cross_section=cross_section,
        )
        for w, s in zip(widths_bend, labels_bend)
    ]

    density_params = [
        (
            dense_lines_width - dense_lines_width_difference,
            dense_lines_gap - dense_lines_width_difference,
            dense_lines_labels[0],
        ),
        (dense_lines_width, dense_lines_gap, dense_lines_labels[1]),
        (
            dense_lines_width + dense_lines_width_difference,
            dense_lines_gap + dense_lines_width_difference,
            dense_lines_labels[2],
        ),
    ]

    all_devices += [
        cdsem_straight_density(
            width=w,
            trench_width=t,
            label=lbl,
            straight_factory=straight_factory,
            layer=layer,
            layers_cladding=layers_cladding,
            cross_section=cross_section,
        )
        for w, t, lbl in density_params
    ]

    all_devices += [
        cdsem_target(
            bend90_factory=bend90_factory,
            width_center=w,
            label=lbl,
            layer=layer,
            layers_cladding=layers_cladding,
            cross_section=cross_section,
        )
        for w, lbl in zip(widths, labels)
    ]

    [c.add_ref(d) for d in all_devices]
    c.align(elements="all", alignment="xmin")
    return c


@cell
def _TRCH_DASH_ISO(length=20.0, width=0.5, n=3, separation=2.0, label=""):
    c = Component()
    _r = rectangle(width, length, layer=LAYER.WG)
    for i in range(n):
        r_ref = c.add_ref(_r)
        r_ref.movey(i * (length + separation))
        c.absorb(r_ref)

    if label:
        marker_label = manhattan_text(text=label, size=0.4, layer=LAYER.WG)
        _marker_label = c.add_ref(marker_label)
        _marker_label.movey((n - 1) * (length + separation + 4.0) + length / 2)
        c.absorb(_marker_label)

    return c


@cell
def _TRCH_DASH_DUO(
    length=20.0, gap=2.0, width=0.5, separation=4.0, n=3, x_offset=0.0, label=""
):

    _trench = _TRCH_DASH_ISO(length=length, width=width, n=n, separation=separation)
    dx = x_offset
    dy = gap + width
    c = Component()
    t1 = c.add_ref(_trench)
    t2 = c.add_ref(_trench)
    t2.move((dy, dx))
    c.absorb(t1)
    c.absorb(t2)

    if label:
        marker_label = manhattan_text(text=label, size=0.4, layer=LAYER.WG)
        _marker_label = c.add_ref(marker_label)
        _marker_label.movey((n - 1) * (length + separation + 4.0) + length / 2)
        c.absorb(_marker_label)

    return c


LABEL_ITERATORS = {}


def gen_label_iterator(prefix=""):
    if not prefix:
        return ""

    if prefix and prefix not in LABEL_ITERATORS:
        LABEL_ITERATORS[prefix] = LabelIterator(prefix)
    return LABEL_ITERATORS[prefix]


class LabelIterator:
    def __init__(self, prefix):
        self.prefix = prefix
        self.counter = it.count(start=1)

    def __next__(self):
        return "{}{}".format(self.prefix, next(self.counter))

    def __iter__(self):
        return self


@cell
def TRCH_ISO(length=20.0, width=0.5):
    c = Component()
    _r = c.add_ref(rectangle(width, length, layer=LAYER.SLAB150))
    c.absorb(_r)

    lblit = gen_label_iterator("TA")
    label = next(lblit)
    marker_label = manhattan_text(text=label, size=0.4, layer=LAYER.WG)
    _marker_label = c.add_ref(marker_label)
    _marker_label.movey(length / 2 + 4.0)
    c.absorb(_marker_label)

    return c


@cell
def TRCH_ISO_DL0(width=0.5, separation=2.0):
    lblit = gen_label_iterator("TB")
    return _TRCH_DASH_ISO(
        width=width, separation=separation, length=10.0, n=5, label=next(lblit)
    )


@cell
def TRCH_ISO_L20(width=0.5, separation=2.0):
    lblit = gen_label_iterator("TC")
    return _TRCH_DASH_ISO(
        width=width, separation=separation, length=20.0, n=3, label=next(lblit)
    )


@cell
def TRCH_DUO_DL0(width=0.5, separation=2.0, gap=3.0):
    lblit = gen_label_iterator("TD")
    return _TRCH_DASH_DUO(
        width=width, separation=separation, gap=gap, length=10.0, n=5, label=next(lblit)
    )


@cell
def TRCH_DUO_L20(width=0.5, separation=2.0, gap=3.0):
    lblit = gen_label_iterator("TE")
    return _TRCH_DASH_DUO(
        width=width, separation=separation, gap=gap, length=20.0, n=3, label=next(lblit)
    )


@cell
def TRCH_STG(width=0.5, separation=2.0, gap=3.0, n=6, length=20.0):
    lblit = gen_label_iterator("TF")
    return _TRCH_DASH_DUO(
        width=width,
        separation=separation,
        gap=gap,
        length=length,
        n=n,
        x_offset=length / 2 + separation / 2,
        label=next(lblit),
    )


if __name__ == "__main__":
    # c = cdsem_straight()
    # c = cdsem_straight_all()
    # c = cdsem_uturn(width=2)
    # c = cdsem_straight_density()
    c = pcm_optical()
    c.show()
