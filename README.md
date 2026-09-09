
Metamaquina2
============

Metamaquina 2 - fully parametric 3D printer

![A photo of the Metamaquina 2 desktop 3d printer](img/MM2_header.jpg)

Manufacturing Instructions
==========================

This is a 3d printer project that is completely designed using the parametric CAD tools
 provided by OpenSCAD. In order to deal with this source code you'll need to install OpenSCAD,
following the instructions at: www.openscad.org

The main structure of the machine is built using lasercut MDF panels. The curves for lasercutting 
can be exported to DXF by rendering the lasercutter_6mm_MDF.scad file. Open it in OpenSCAD, press F6 (to compile) and then click Design->Export DXF. The resulting DXF file can be used to cut 6mm thick MDF sheets (or you can change the thickness in the source if you plan to work with some other materials but be sure to review the 3d model in this case since some parts of the design depend on 6mm thickness).

There is also a panel for lasercutting 2mm acrylic to cover the electronics PCB and a panel for lasercutting 5mm acrylic for the ZMAX/ZMIN endstop holders and a couple of 5mm spacers for the LCExtruder. There can be generated from the lasercutter_2m_acrylic.scad and lasercutter_5m_acrylic.scad, respectively. 

![Laser Cutter Panel #1](https://raw.github.com/Metamaquina/Metamaquina2/master/img/lasercutter_panel1.png)
![Laser Cutter Panel #2](https://raw.github.com/Metamaquina/Metamaquina2/master/img/lasercutter_panel2.png)
![Laser Cutter Panel #3](https://raw.github.com/Metamaquina/Metamaquina2/master/img/lasercutter_panel3.png)

The complete 3D model of the machine is described by the Metamaquina2.scad file. Open is in 
OpenSCAD and press F5 to render it.

![An OpenSCAD rendering of the Metamaquina 2 desktop 3d printer](https://raw.github.com/Metamaquina/Metamaquina2/master/img/MM2.png)

The machine as a node tree
==========================

Beside the OpenSCAD design there is a second reading of it: a
solid-node tree in `metamaquina2/`, in which every part a builder
handles is a leaf and every group that gets put together before it goes
into something bigger is an assembly. The geometry is still the .scad
design's -- the nodes call its modules and read its dimensions -- and
what the tree adds is where every part goes, the three axes as drivers,
and the parts the design buys and never drew.

A printer is mostly a thing that does not move, and the tree says which
half is which. Each assembly's `render()` builds it at rest: it holds
the structure, whether the power supply is fitted at all, and the
placement of every part a builder bolts down and leaves -- the frame,
the panels, the fasteners, the boxes at both ends of the beam, the reel
stand. It reads no driver, so it is run once. What follows a driver is
declared where each part is: the carriage's slide, the bed's slide and
the beam's lift are `solid_node.motion` joints on the bodies that have
them, and `drives()` relations say that the three axes turn the screws,
the couplings and the two motor pulleys the belts are meshed on --
composed inside each rest placement, which is why a screw can spin
about its own axis and still stand where it is held. What is left in
`simulate()` is the one thing no joint states: the shape the free run
of filament is dragged into, which is molejo geometry rather than a
rigid part's pose.

    solid test metamaquina2/metamaquina2.py     # the contracts
    solid build metamaquina2/metamaquina2.py    # build the machine
    solid develop metamaquina2/metamaquina2.py  # watch and serve it

Each node declares its parameters, so the two the machine itself
declares can be set from the shell on any of those commands:

    solid build metamaquina2/metamaquina2.py --set spool_holder_offset=500
    solid build metamaquina2/metamaquina2.py --set power_supply_fitted=false

`spool_holder_offset` is how far beside the machine the filament stand
sits, along the machine's own x -- the one placement here that this
layer chooses rather than reads out of the design. Moving it moves the
reel and the free run of filament is drawn again from wherever it
lands.

`power_supply_fitted` is whether this machine is built with its power
supply in it, and it is the one part of the machine that is fitted or
not. It defaults to the brick the design configures, so the machine
that builds is the machine that has always been drawn; turn it off and
the supply, its box and its bolts are left out -- a different mass and
a shorter bill of materials, not a hole in the render.

Everything else the machine is dimensioned by comes from the OpenSCAD
sources themselves, evaluated once at import (`metamaquina2/params.py`),
and is deliberately *not* a settable parameter: the parts are drawn by
the .scad modules from those same variables, so a value overridden in
Python would move where a part is put without changing the part, and
the two readings would disagree. To change a dimension of this machine,
change it in the design.

Hacking the code
================
Feel free to send us pull requests at https://github.com/Metamaquina/Metamaquina2
 if you make any change to this design that you consider worth sharing with us.

happy hacking,

Felipe Sanches

R&D director at Metamaquina.com.br


