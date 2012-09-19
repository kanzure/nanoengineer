# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
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


from dna_ribbon_view import Cylinder

class Stateful(InstanceOrExpr):
    """Given an expr and a list of its arg/option attrs, extract the types of those attrs from the expr,
    and act as a stateful type permitting those attrs to be set/changed.
       Also be capable of returning metainfo that would let file save/load mappings, property editors, etc,
    be generated.
       For example, Stateful(Cylinder, ['axis', 'color', 'radius']) ... #doc more
    """
    ###e what is the state-type -- a plain object, or an expr itself? (eg to support relations, ref geom, relative coords)
    # Do we pass this in? if so, how? for each attr or for all? for each type, of the types involved in the attrs?
    # how would the expr say that one arg's precise type, or coordsys, etc, is a function of another arg's value?

    # args
    expr = ArgExpr(Anything, doc = "an expr whose arguments we'll extend into state decls")
    attrs = Arg(list_Expr(str), doc = "list of some or all of its arg attrs, or a filter for them [nim]; we'll only extend these ones")
        #e can this have a useful default of "all of them"??
        #e can we pass it more info like a specific type per attr?

    #
    decls = expr._e_attr_decls # list of decls of attrs of expr, in their declared order; each is an AttrDecl object for it.attr
        ###IMPLEM this attr of an expr, and the AttrDecl object it returns;
        # I guess/hope that object is just the Arg or Option after _E_ATTR gets replaced by the real attr
        ### PROBLEM: this will fail: _e_attr can't be symbolic getattr.
        ## Q: should expr be a true expr, or an Instance representing an expr in a more first-class way? Or can those be the same thing?
        # A, I hope: those can be the same thing -- exprs (when not symbolic) can be sufficiently first-class for that.
        # This might require tracking just how symbolic each expr is... actually I guess getattr_Expr always is, since otherwise
        # it is not formed from getattr. So maybe it won't require that.

    want_decls = filter_Expr( lambda decl: (not attrs) or (decl.attr in attrs),
                                  ###IMPLEM (if review ok): not -> not_Expr, or -> or_Expr, in -> in_Expr --
                                      # BUT review will say no, if I use them in programming, e.g. not exprvar means it's None.
                                      #k Can it differ for symbolic case or not?? (All OpExprs would be symbolic, I guess...)
                                  ### PROBLEM: attrs won't get replaced with _self.attrs since it's inside a lambda body --
                                  # unless filter_Expr is smart enough to tease apart the lambda for that purpose.
                                  # (Or to eval it on a symbolic arg?? And *then* replace in it using scanner? To eval during scanner?)
                              decls )
        ###BUG: those should be in the order in the list, not the order in decls, I think
        # (unless there are issues about a partial order of definining them due to types referring to others' vals...
        #  but i doubt that should be allowed to cause a restriction on order in a file record or PM -- tho I'm not sure ##e)
    def _C_extended_expr(self):
        res = self.expr
        for decl in self.want_decls:
            kws = {decl.attr : State( decl.type, decl.dflt )} ###IMPLEM this executable form of State
            res = res._e_extend(**kws)
        return res
    ###e now, what do we do with that so that our owner can use it? Do we let it act as our "value"??? (a kind of delegate i guess)
    #e (or maybe more like a forwarding value, a val we forward to)

    pass # end of class

#e now make a command for creating a Stateful(Cylinder) in the model -- i guess we pass Stateful(Cylinder) as expr arg to another thing
# which makes a standard creator command for that expr, extracting state decls from it, and which makes a std PM too

class StandardSketchEntityCreatorCommand(InstanceOrExpr):
    "a standard creator command for a sketch entity of the type described by our arg expr"
    # note, this is useful even if it doesn't define enough and you have to subclass it (i e delegate to it) in practice,
    # eg for the mouse behavior part. or maybe you have to pass in some fancier exprs that help it implem that part.
    expr = ArgExpr(Anything, doc = "an expr for a stateful object of a certain kind...") #doc
    ##e customizations = Option(Customizations) ###IMPLEM that type, and whatever we do about it in here... see customization below
    #
    fields = expr._e_state_fields ### seems wrong -- how would it know? instead, get the types, let env make them into fields ####e
        # [besides the problem with making a getattr_Expr due to the _e_]
    field_editor_group = StandardFieldEditorGroup(fields) ###IMPLEM
    property_manager_groups = [field_editor_group] #e more? btw, don't we want to subdivide the fields into groups?
        ###e what we *really* want is to be able to apply user (or developer) customization data
        # to this very object to get a fancier one. Then to develop a type, start with this thing
        # and edit it using the app's customization features!
        # This might work by letting customizations be edit commands on the UI we make here,
        # since the developer might create them by seeing that UI in a first class way and editing it.
    ###e lots more
    pass

####  PROBLEMS   #####

# biggest uncomfortablenesses so far:
# - expr prickliness about getattr_Expr from ._e_xxx -- and for that matter the _e_ in the name --
#   if we first-classed them into UnderstoodExpr instances or so, we could use regular attrnames on them
# - some of those things should be functions anyway, I mean methods with args

from somewhere import Cylinder, Sphere, Rect, Line, Circle, Polygon, Polyline # etc
for shapeclass in (Cylinder, Sphere, Rect, Line, Circle): #e and more
    register_command( StandardSketchEntityCreatorCommand( Stateful( shapeclass)))
    #e hmm, can it really be that simple at the end??
    # what about things like their topic, organization into UI, other metainfo...
    # maybe all that can be added by interactive customization??
    # if so, it really can be that simple!
    # in fact, even simpler -- this would be a rule to apply to every "shape class" that gets registered.
    # there'd be lots of rules for lots of different kinds of classes... and lots of customization-interference-points...
    # of course you also want other registered classes to provide customization (like the ones in the same module as the main class)...

# ==

# let's think about how, in practice, we extract the arg decls from an expr...
# [continued in new edits to "Arg advice" in attr_decl_macros.py. Search for that phrase or "update 070323".]

# ==

###   TODO   ###   (besides the entire file)

# Let's do one of these entirely by hand. Problem: above won't import. Well, nevermind that for now. (The below won't either!)

from dna_ribbon_view import Cylinder, LineSegment, Nanometers

class StatefulCylinder(DelegatingInstanceOrExpr):
    axis = State(LineSegment, (ORIGIN, ORIGIN + DX)) ###e really we want StateArg, etc
        #e note: for this guy's default value, I was going to say
        ## Cylinder._e_default_attr_value('axis'), but that's as hard as impleming those Arg decl objects!
    radius = State( Nanometers, 1.0)
    color = State( Color, gray)
    capped = State( bool, True)
    delegate = Cylinder(axis, radius, color, capped = capped)
    pass

TextEditField ###IMPLEM (like run py code)

class MakeCylinder_PM(xxx):
    delegate = SimpleColumn(
        ###e what for the axis? need a PM for picking/finding/making a LineSegment. In real life it'll be by relations / ref geom, not coords...
        #e for radius, a float lineedit widget, with units, or an ability to go find a length dimension to define it from...
        #e for color, a color edit field... (shows color, lets you give it by name, or stylename, or formula, or use colorchooser, or see recent colors...)
        #e for capped, a checkbox
        # [notice how all this totally depends on the type? i think none of these egs depended on anything *but* the type!
        #  and maybe, the extent of fanciness of relations you want for it... but ideally that depends on the type too.
        #  and by this point should be encoded literally into the State type, anyway.]
     )
    pass

# ==

# end
