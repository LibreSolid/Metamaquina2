"""The hobbed bolt that grips and drives the filament."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import extruder


class HobbedBolt(ScadPart):
    """The one part of the extruder that touches the filament.

    Modelled as a plain shank with a hex head; the design notes that
    the hobbing itself is not drawn.
    """

    color = materials.METAL

    def render(self):
        return extruder.hobbed_bolt()
