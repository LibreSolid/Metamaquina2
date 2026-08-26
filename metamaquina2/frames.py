"""The coordinate frames of the machine's panels.

A panel is drawn flat, on its own plane, and then stood up somewhere in
the machine.  Everything that mounts to that panel -- the t-slot bolts,
the electronics, the cable clips, the endstops -- is positioned in the
panel's flat plane too, and then follows it up.  So the transform from
a panel's plane into machine coordinates is written down once, here,
and applied by every assembly that has something to put on that panel.

Each function takes a node already positioned in the panel's plane and
returns it placed on the machine, so the calls read the way the
assembly reads: make the part, put it where it goes on the panel, hand
it to the panel's frame.

Operations compose in the order they are appended, which is the
reverse of how OpenSCAD nests them: the innermost transform of a
``translate(...) rotate(...) part()`` chain is applied first and so is
appended first.
"""

from metamaquina2.params import (
    ArcPanel_height,
    ArcPanel_rear_advance,
    BottomPanel_zoffset,
    RightPanel_basewidth,
    SidePanels_distance,
    XZStage_offset,
    machine_height,
    thickness,
)


def right_panel(node):
    """From the right panel's plane onto the machine.

    The panel stands on the +X side, facing inwards; its own +X runs
    towards the back of the machine and its own +Y runs upwards.
    """
    return (node
            .rotate(90, [1, 0, 0])
            .rotate(-90, [0, 0, 1])
            .translate([SidePanels_distance / 2,
                        RightPanel_basewidth / 2, 0]))


def left_panel(node):
    """From the left panel's plane onto the machine.

    Same orientation as the right panel, one panel width in from the
    -X side -- the panel is extruded towards +X from where it is
    placed, so the design offsets it by one `thickness`.
    """
    return (node
            .rotate(90, [1, 0, 0])
            .rotate(-90, [0, 0, 1])
            .translate([-SidePanels_distance / 2 + thickness,
                        RightPanel_basewidth / 2, 0]))


def top_panel(node):
    """From the top panel's plane onto the machine: flat, at the top."""
    return node.translate([0, -XZStage_offset, machine_height])


def bottom_panel(node):
    """From the bottom panel's plane onto the machine: flat, at the base."""
    return node.translate([0, -XZStage_offset, BottomPanel_zoffset])


def arc_panel(node):
    """From the arc panel's plane onto the machine: standing across the
    back, facing forwards."""
    return (node
            .rotate(90, [1, 0, 0])
            .translate([0, ArcPanel_rear_advance - XZStage_offset,
                        machine_height - ArcPanel_height]))
