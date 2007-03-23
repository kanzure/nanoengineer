"""
demo_create_shapes.py -- some demo commands for creating shapes in the model.

$Id$
"""

from demo_draw_on_surface import * # be really lazy for now -- but don't forget the _private names

#e PLAN: do more of the kind of thing now done in demo_draw_on_surface.py,
# and integrate it all together using demo_ui.py or so.
#
# Solve some problems of relations between model objects, and savable model objects,
# and autoadding State decls (in wrappers or customizations -- use _e_extend??) to exprs for given attrs.
#
# Keep in mind the need for selection state, bindings in MT that fit with those in graphics area when sensible,
# automaking of PM groups, browsing of available commands (by name or by what they can do)...


# sources:

#e class Cylinder -- see dna_ribbon_view.py: 179: class Cylinder(Geom3D)
 # also Cylinder_HelicalPath(Geom3D)...

#e class Sphere

# other solids

# geometry_exprs.py

# demo_polyline.py  and the see also files it mentions


# also 2d shapes? they are sketch entities... i suppose so are 3d shapes...
# all shapes might be based on control points (see geometry_exprs.py)
# defined in various reference objects or grids...
# not all points in a sketch entity have to come from the same ref object!
# and they might be lnked to a snapshot of that object, or to a live instance of it in the model!
# or to a derived one (formula of ones in the model) which is not itself directly visible in the model.
