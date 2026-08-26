"""The design's dimensions, read from the OpenSCAD sources themselves.

Every number below is derived in OpenSCAD -- ``machine_height`` from
the build volume, ``SidePanels_distance`` from the heated bed, and so
on down a long chain.  Restating that arithmetic in Python would give
the layer a second set of dimensions free to drift from the first, so
instead OpenSCAD is asked once, at import, what each name evaluates
to.  Echo export evaluates the variable tree without rendering any
geometry, which takes a fraction of a second for the whole machine.

The nodes place parts with these values; the parts themselves are the
OpenSCAD modules.  One source of truth, two consumers.
"""

import ast
import os
import re
import subprocess
import tempfile

from metamaquina2.scad import SOURCE_DIR


_ECHO = re.compile(r'^ECHO: "PARAM (\S+) = (.*)"$')
_PRECISE = re.compile(r'^ECHO: "PRECISE (\S+) = (\S+) (\S+)"$')


def _probe(source, names):
    """Evaluate `names` in the scope of `source` and return them.

    The probe ``include``s the source, which brings its top-level
    variables into scope -- ``use`` would import only its modules and
    functions.  Top-level geometry in the included file is not a cost:
    the echo exporter never renders it.

    Each name is echoed twice.  OpenSCAD prints a number with six
    significant digits, which for a machine 434 mm wide loses the
    fourth decimal place -- enough to make two parts that should meet
    flush overlap.  So a scalar is echoed a second time split into its
    integer part and its fraction scaled by a million, and the two
    six-digit halves are recombined here into roughly twelve.
    """
    script = ['include <%s>;' % os.path.join(SOURCE_DIR, source)]
    for name in names:
        script.append('echo(str("PARAM %s = ", %s));' % (name, name))
        script.append(
            'if (is_num(%s)) echo(str("PRECISE %s = ", floor(%s), " ",'
            ' (%s - floor(%s))*1000000));' % ((name,) * 5))

    with tempfile.TemporaryDirectory() as workdir:
        probe = os.path.join(workdir, 'probe.scad')
        echoes = os.path.join(workdir, 'probe.echo')
        with open(probe, 'w') as handle:
            handle.write('\n'.join(script) + '\n')
        subprocess.run(['openscad', '-o', echoes, probe],
                       check=True, capture_output=True)
        with open(echoes) as handle:
            output = handle.read()

    values = {}
    for line in output.splitlines():
        line = line.strip()
        matched = _ECHO.match(line)
        if matched:
            values[matched.group(1)] = _value(matched.group(2))
            continue
        matched = _PRECISE.match(line)
        if matched:
            whole, fraction = matched.group(2), matched.group(3)
            values[matched.group(1)] = (
                float(whole) + float(fraction) / 1000000)

    missing = [name for name in names if values.get(name) is None]
    if missing:
        raise RuntimeError(
            '%s does not define %s' % (source, ', '.join(missing)))
    return values


def _value(text):
    """An OpenSCAD echo value as a Python one.

    OpenSCAD prints numbers, booleans, quoted strings and nested
    vectors, all of which read as Python literals once ``true``/
    ``false``/``undef`` are spelled the Python way.
    """
    literal = re.sub(r'\btrue\b', 'True', text)
    literal = re.sub(r'\bfalse\b', 'False', literal)
    literal = re.sub(r'\bundef\b', 'None', literal)
    try:
        return ast.literal_eval(literal)
    except (SyntaxError, ValueError):
        return text


_machine = _probe('Metamaquina2.scad', [
    # sheet stock
    'thickness', 'acrylic_thickness', 'slot_extra_thickness', 'epsilon',
    # build volume and heated bed
    'BuildVolume_X', 'BuildVolume_Y', 'BuildVolume_Z',
    'HeatedBed_X', 'HeatedBed_Y',
    'heated_bed_pcb_thickness', 'heated_bed_glass_thickness',
    'heated_bed_pcb_width', 'heated_bed_pcb_height',
    'glass_w', 'glass_h',
    'BuildPlatform_height', 'pcb_height',
    # the frame
    'machine_height', 'machine_x_dim',
    'SidePanels_distance', 'RightPanel_basewidth', 'RightPanel_topwidth',
    'ArcPanel_width', 'ArcPanel_height', 'ArcPanel_rear_advance',
    'BottomPanel_width', 'BottomPanel_zoffset',
    'feetwidth', 'feetheight', 'baseh',
    'bar_cut_length', 'horiz_bars_length',
    'base_bars_height', 'base_bars_Zdistance',
    'rear_backtop_advance',
    # the stages
    'XZStage_offset', 'XZStage_position',
    'X_rods_distance', 'X_rods_diameter', 'X_rod_length', 'X_rod_height',
    'Y_rods_distance', 'Y_rod_length', 'Y_rod_height',
    'Z_rods_distance', 'Z_rod_length', 'Z_bar_length',
    'Z_rod_sidepanel_distance', 'z_rod_z_bar_distance',
    'XPlatform_width', 'XPlatform_height',
    'XEnd_box_size', 'XEnd_extra_width', 'XEnd_width',
    'XCarriage_width', 'XCarriage_length', 'XCarriage_height',
    'XCarriage_padding', 'XCarriage_lm8uu_distance',
    'XCarPosition', 'YCarPosition', 'ZCarPosition',
    'XMotor_height', 'XIdler_height', 'PulleyRadius', 'IdlerRadius',
    'belt_offset', 'belt_width', 'belt_clamp_height',
    'bearing_sandwich_spacing',
    'YBearings_distance', 'YEndstopHolder_distance', 'YPlatform_height',
    'nozzle_tip_distance',
    # placed subassemblies
    'RAMBo_x', 'RAMBo_y',
    'powersupply_Xposition', 'powersupply_Yposition', 'HIQUA_POWERSUPPLY',
    'z_max_endstop_x', 'z_max_endstop_y',
    'z_min_endstop_x', 'z_min_endstop_y',
    'extruder_wiring_radius',
    'ZLink_rod_height', 'Zlink_hole_height',
    # hardware
    'lm8uu_diameter', 'lm8uu_length',
    'm3_diameter', 'm3_washer_thickness', 'm3_nut_height', 'm3_spacer_radius',
    'm8_diameter', 'm8_nut_height', 'm8_washer_thickness',
    'm8_mudguard_washer_thickness',
    'NEMA17_width', 'NEMA17_height', 'NEMA17_length',
    'motor_shaft_length', 'motor_shaft_diameter',
    'coupling_shaft_depth',
    'hexspacer_length',
    # t-slot bolt lists and cable clip lists
    'SidePanel_TSLOTS', 'TopPanel_TSLOTS',
    'XEndMotor_back_face_TSLOTS', 'XEndIdler_back_face_TSLOTS',
    'top_cable_clips', 'left_cable_clips',
    'right_cable_clips', 'bottom_cable_clips',
])

# sheet stock
thickness = _machine['thickness']
acrylic_thickness = _machine['acrylic_thickness']
slot_extra_thickness = _machine['slot_extra_thickness']
epsilon = _machine['epsilon']

# build volume and heated bed
BuildVolume_X = _machine['BuildVolume_X']
BuildVolume_Y = _machine['BuildVolume_Y']
BuildVolume_Z = _machine['BuildVolume_Z']
HeatedBed_X = _machine['HeatedBed_X']
HeatedBed_Y = _machine['HeatedBed_Y']
heated_bed_pcb_thickness = _machine['heated_bed_pcb_thickness']
heated_bed_glass_thickness = _machine['heated_bed_glass_thickness']
heated_bed_pcb_width = _machine['heated_bed_pcb_width']
heated_bed_pcb_height = _machine['heated_bed_pcb_height']
glass_w = _machine['glass_w']
glass_h = _machine['glass_h']
BuildPlatform_height = _machine['BuildPlatform_height']
pcb_height = _machine['pcb_height']

# the frame
machine_height = _machine['machine_height']
machine_x_dim = _machine['machine_x_dim']
SidePanels_distance = _machine['SidePanels_distance']
RightPanel_basewidth = _machine['RightPanel_basewidth']
RightPanel_topwidth = _machine['RightPanel_topwidth']
ArcPanel_width = _machine['ArcPanel_width']
ArcPanel_height = _machine['ArcPanel_height']
ArcPanel_rear_advance = _machine['ArcPanel_rear_advance']
BottomPanel_width = _machine['BottomPanel_width']
BottomPanel_zoffset = _machine['BottomPanel_zoffset']
feetwidth = _machine['feetwidth']
feetheight = _machine['feetheight']
baseh = _machine['baseh']
bar_cut_length = _machine['bar_cut_length']
horiz_bars_length = _machine['horiz_bars_length']
base_bars_height = _machine['base_bars_height']
base_bars_Zdistance = _machine['base_bars_Zdistance']
rear_backtop_advance = _machine['rear_backtop_advance']

# the stages
XZStage_offset = _machine['XZStage_offset']
XZStage_position = _machine['XZStage_position']
X_rods_distance = _machine['X_rods_distance']
X_rods_diameter = _machine['X_rods_diameter']
X_rod_length = _machine['X_rod_length']
X_rod_height = _machine['X_rod_height']
Y_rods_distance = _machine['Y_rods_distance']
Y_rod_length = _machine['Y_rod_length']
Y_rod_height = _machine['Y_rod_height']
Z_rods_distance = _machine['Z_rods_distance']
Z_rod_length = _machine['Z_rod_length']
Z_bar_length = _machine['Z_bar_length']
Z_rod_sidepanel_distance = _machine['Z_rod_sidepanel_distance']
z_rod_z_bar_distance = _machine['z_rod_z_bar_distance']
XPlatform_width = _machine['XPlatform_width']
XPlatform_height = _machine['XPlatform_height']
XEnd_box_size = _machine['XEnd_box_size']
XEnd_extra_width = _machine['XEnd_extra_width']
XEnd_width = _machine['XEnd_width']
XCarriage_width = _machine['XCarriage_width']
XCarriage_length = _machine['XCarriage_length']
XCarriage_height = _machine['XCarriage_height']
XCarriage_padding = _machine['XCarriage_padding']
XCarriage_lm8uu_distance = _machine['XCarriage_lm8uu_distance']
XCarPosition = _machine['XCarPosition']
YCarPosition = _machine['YCarPosition']
ZCarPosition = _machine['ZCarPosition']
XMotor_height = _machine['XMotor_height']
XIdler_height = _machine['XIdler_height']
PulleyRadius = _machine['PulleyRadius']
IdlerRadius = _machine['IdlerRadius']
belt_offset = _machine['belt_offset']
belt_width = _machine['belt_width']
belt_clamp_height = _machine['belt_clamp_height']
bearing_sandwich_spacing = _machine['bearing_sandwich_spacing']
YBearings_distance = _machine['YBearings_distance']
YEndstopHolder_distance = _machine['YEndstopHolder_distance']
YPlatform_height = _machine['YPlatform_height']
nozzle_tip_distance = _machine['nozzle_tip_distance']

# placed subassemblies
RAMBo_x = _machine['RAMBo_x']
RAMBo_y = _machine['RAMBo_y']
powersupply_Xposition = _machine['powersupply_Xposition']
powersupply_Yposition = _machine['powersupply_Yposition']
HIQUA_POWERSUPPLY = _machine['HIQUA_POWERSUPPLY']
z_max_endstop_x = _machine['z_max_endstop_x']
z_max_endstop_y = _machine['z_max_endstop_y']
z_min_endstop_x = _machine['z_min_endstop_x']
z_min_endstop_y = _machine['z_min_endstop_y']
extruder_wiring_radius = _machine['extruder_wiring_radius']
ZLink_rod_height = _machine['ZLink_rod_height']
Zlink_hole_height = _machine['Zlink_hole_height']

# hardware
lm8uu_diameter = _machine['lm8uu_diameter']
lm8uu_length = _machine['lm8uu_length']
m3_diameter = _machine['m3_diameter']
m3_washer_thickness = _machine['m3_washer_thickness']
m3_nut_height = _machine['m3_nut_height']
m3_spacer_radius = _machine['m3_spacer_radius']
m8_diameter = _machine['m8_diameter']
m8_nut_height = _machine['m8_nut_height']
m8_washer_thickness = _machine['m8_washer_thickness']
m8_mudguard_washer_thickness = _machine['m8_mudguard_washer_thickness']
NEMA17_width = _machine['NEMA17_width']
NEMA17_height = _machine['NEMA17_height']
NEMA17_length = _machine['NEMA17_length']
motor_shaft_length = _machine['motor_shaft_length']
motor_shaft_diameter = _machine['motor_shaft_diameter']
coupling_shaft_depth = _machine['coupling_shaft_depth']
hexspacer_length = _machine['hexspacer_length']

# t-slot bolt placements, as [x, y, width, angle]
SidePanel_TSLOTS = _machine['SidePanel_TSLOTS']
TopPanel_TSLOTS = _machine['TopPanel_TSLOTS']
XEndMotor_back_face_TSLOTS = _machine['XEndMotor_back_face_TSLOTS']
XEndIdler_back_face_TSLOTS = _machine['XEndIdler_back_face_TSLOTS']

# cable clip placements, as [type, angle, y, z]
top_cable_clips = _machine['top_cable_clips']
left_cable_clips = _machine['left_cable_clips']
right_cable_clips = _machine['right_cable_clips']
bottom_cable_clips = _machine['bottom_cable_clips']


_extruder = _probe('lasercut_extruder.scad', [
    'HandleWidth', 'HandleHeight',
    'idler_axis_position', 'idler_bearing_position', 'idler_angle',
    'motor_position', 'motor_angle',
    'hobbed_bolt_position', 'extruder_gear_angle',
    'LCExtruder_nut_gap', 'washer_thickness',
])

HandleWidth = _extruder['HandleWidth']
HandleHeight = _extruder['HandleHeight']
idler_axis_position = _extruder['idler_axis_position']
idler_bearing_position = _extruder['idler_bearing_position']
idler_angle = _extruder['idler_angle']
motor_position = _extruder['motor_position']
motor_angle = _extruder['motor_angle']
hobbed_bolt_position = _extruder['hobbed_bolt_position']
extruder_gear_angle = _extruder['extruder_gear_angle']
LCExtruder_nut_gap = _extruder['LCExtruder_nut_gap']
extruder_washer_thickness = _extruder['washer_thickness']


_rambo = _probe('RAMBo.scad', [
    'RAMBo_width', 'RAMBo_height', 'RAMBo_thickness', 'RAMBo_border',
    'RAMBo_pcb_thickness', 'RAMBo_cover_thickness', 'M3_bolt_head',
])

RAMBo_width = _rambo['RAMBo_width']
RAMBo_height = _rambo['RAMBo_height']
RAMBo_thickness = _rambo['RAMBo_thickness']
RAMBo_border = _rambo['RAMBo_border']
RAMBo_pcb_thickness = _rambo['RAMBo_pcb_thickness']
RAMBo_cover_thickness = _rambo['RAMBo_cover_thickness']
M3_bolt_head = _rambo['M3_bolt_head']


_spool = _probe('FilamentSpoolHolder.scad', [
    'total_width', 'total_height', 'adjust',
    'spool_holder_width', 'top_cut_height', 'top_cut_width',
    'bar_diameter', 'bar_length', 'hole_domed_cap_nut',
    'sidepanel_TSLOTS',
])

SpoolHolder_total_width = _spool['total_width']
SpoolHolder_total_height = _spool['total_height']
SpoolHolder_adjust = _spool['adjust']
SpoolHolder_width = _spool['spool_holder_width']
SpoolHolder_top_cut_height = _spool['top_cut_height']
SpoolHolder_top_cut_width = _spool['top_cut_width']
SpoolHolder_bar_diameter = _spool['bar_diameter']
SpoolHolder_bar_length = _spool['bar_length']
SpoolHolder_cap_nut_hole = _spool['hole_domed_cap_nut']
SpoolHolder_TSLOTS = _spool['sidepanel_TSLOTS']


_power_supply = _probe('PowerSupply.scad', [
    'PowerSupply_width', 'PowerSupply_height', 'PowerSupply_thickness',
    'box_height', 'bottom_offset', 'metal_sheet_thickness',
    'PSU_Female_border_height', 'mount_positions',
])

PowerSupply_width = _power_supply['PowerSupply_width']
PowerSupply_height = _power_supply['PowerSupply_height']
PowerSupply_thickness = _power_supply['PowerSupply_thickness']
PowerSupplyBox_height = _power_supply['box_height']
PowerSupply_bottom_offset = _power_supply['bottom_offset']
PowerSupply_sheet_thickness = _power_supply['metal_sheet_thickness']
PSU_Female_border_height = _power_supply['PSU_Female_border_height']
PowerSupply_mount_positions = _power_supply['mount_positions']


_endstop = _probe('endstop.scad', [
    'microswitch_width', 'microswitch_height', 'microswitch_thickness',
    'endstop_spacer_height',
])

microswitch_width = _endstop['microswitch_width']
microswitch_height = _endstop['microswitch_height']
microswitch_thickness = _endstop['microswitch_thickness']
endstop_spacer_height = _endstop['endstop_spacer_height']


# Values the design writes down inside a module body rather than at the
# top level, so the probe cannot reach them.  Each is named here with
# the module it belongs to, so a reader can check it against the source.
bearing_thickness = 7          # bearing_assembly() in Metamaquina2.scad
washer_thickness = 1.5         # bearing_assembly() in Metamaquina2.scad
mudguard_washer_thickness = 2  # bearing_assembly() in Metamaquina2.scad
barclamp_thickness = 13.5      # bar_clamp_assembly() in Metamaquina2.scad
idler_radius = 23              # idler() in lasercut_extruder.scad
handle_bolt_length = 70        # handle() in lasercut_extruder.scad
handle_nut_height = 3          # handle() in lasercut_extruder.scad
idler_bolt_length = 30         # idler_bolt_subassembly()
YPlatform_zoffset = 100 - 15   # YPlatform_subassembly() in Metamaquina2.scad
