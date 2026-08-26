"""M8 mudguard (penny) washer."""

from metamaquina2 import materials
from metamaquina2.part import ScadPart
from metamaquina2.scad import washers


class M8MudguardWasher(ScadPart):
    """The wide washer that spreads a bearing's load on the Y bars."""

    color = materials.METAL

    def render(self):
        return washers.M8_mudguard_washer()
