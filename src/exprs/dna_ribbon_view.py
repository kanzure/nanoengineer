"""
dna_ribbon_view.py

$Id$


070125: started this from a copy of demo_dna-outtakes.py.

[Since then, that file has been cvs-removed -- see 070201 comment below.]

Eventually this will have some display styles for DNA double helix segments,
with the model aspects of those defined in separate files,
but to get started, we might make self-contained exprs which handle two parts of this
that ought to be separated:

- think of some external "control point" state as "state describing a DNA double helix segment";

- draw a "DNA double helix segment" in various ways.

We'll break it down into separate expr classes for the operations:

- make dna seg params from control points,

- generate various useful geometric objects from those and from simpler or higherlevel ones,

- draw those individually,

- put that together to draw a DNA segment.

Then it can all be put together into a demo in which the control points are draggable.

In the future we can let a "dna model object" know how to get its params
from a variety of input types in different ways, and know how to display itself
or make it work to find the display rules externally and apply them to it.
To some extend we can prefigure that now if we break things down in the right way.


070130: the tension between arrays of unlabeled numbers (efficiency, LL code convenience)
and typesafe geometric objects (points, knowing their coords intrinsicness & coordsys & space, etc)
is a problem, but the best-guess resolution is to make "rich objects" available (with all such
type info, metainfo, extra info -- e.g. normal and surface (incl its own local coordsys vectors
within the tangent plane, or enough info to derive them) and object-we-mark for points),
but also make coords available, in standard coordsystems, informal at first, later available
as metainfo for specific attrs; and someday to bridge the gap by working primarily with rich *arrays*
of data, so the number ops can be done by Numeric or the like, expressing the HL ops with exprs.
In the meantime it's a continual hassle, seen in the present Qs about types like Cylinder and
Cylinder_HelicalPath.


070131/070201: for now, coordinates are handled by using all the same ones (same as drawing coords)
in any given object. The object is responsible for knowing what coords it uses in kids it makes
(and the ones here just use the same ones in kids and in themselves).

This means a cylinder with markings, to be efficient re display lists when moved/rotated [which is nim],
should have that move/rotate done outside it (not modifying anything it stores), in a manner not yet
worked out. Maybe the easiest way is for it to make an exception and contain an outer repositioner
wrapping everything else it draws... tho if that repositioner could be entirely outside it, that might be better --
but only if not having one is an option; especially useful if there can be different kinds, e.g. for gridded drags.
The outer repositioner could also be temporary, with coord changes reflected inside the object eventually
(similar to chunks, which often reset their base coords to abs coords or a translated version of them).
This is all TBD. ###e


070201: for now, length units will be handled by using nm everywhere. This is a kluge for the lack of
an adjustable relation between NE1 model-drawing-coords and physical distance; it will make DNA look the
right size on screen. But it's incompatible with drawing atoms (assuming you want them to look in the same
scale as the DNA -- not clear, if they are in a different model that happens to be shown at the same time!)
Later we'll have to coexist better with atoms using angstroms, perhaps by making physical & drawing units
explicit for each object -- or for individual numbers and numeric arrays if we can do that efficiently
(which probably means, if we implement the unit/coord compatibility checks and wrapping/unwrapping in C).


070201: moved still-useful scraps we're not using now to another file,
dna_ribbon_view_scraps.py, including most of what remains from demo_dna-outtakes.py,
which I'm cvs-removing. (The only reason I might want to look it up in cvs would be
for help making the OpenGL do what it used to do, if that's ever needed.)

"""

from basic import *
from basic import _self, _this, _my

import Overlay
reload_once(Overlay)
from Overlay import Overlay

from OpenGL.GL import * #e move what needs this into draw_utils
import drawer

# needed for code modified from demo_drag: not sure it's all still needed #k

import world
reload_once(world)
from world import World

import Rect
reload_once(Rect)
from Rect import Rect, RectFrame, IsocelesTriangle, Spacer, Sphere

import Column
reload_once(Column)
from Column import SimpleColumn, SimpleRow

import DisplistChunk # works 070103, with important caveats re Highlightable
reload_once(DisplistChunk)
from DisplistChunk import DisplistChunk

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

#k some of this might also be needed, prob not all:

import transforms
reload_once(transforms)
from transforms import Translate

import Center
reload_once(Center)
from Center import Center, CenterY

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import controls
reload_once(controls)
from controls import checkbox_pref, ActionButton

import lvals
reload_once(lvals)
from lvals import Lval, LvalDict2, call_but_discard_tracked_usage

import draggable
reload_once(draggable)
from draggable import DraggableObject

# temporary kluge: excerpt from cad/src/DnaGenerator.py; this copy used locally for constants [values not reviewed]:
class B_Dna:
    geometry = "B-DNA"
    TWIST_PER_BASE = -36 * pi / 180   # radians [this value is not used here since it differs from Paul's Origami values]
    BASE_SPACING = 3.391              # angstroms

#e clean up these local abbreviations
Macro = DelegatingInstanceOrExpr

# stubs:
Radians = Width
Rotations = Degrees = Width
Angstroms = Nanometers = Width

ModelObject3D = ModelObject ### might be wrong -- might not have fix_color -- unless it can delegate it -- usually it can, not always --
   # can default delegate have that, until we clean up delegation system? or just move that into glpane? yes for now.
   # we'll do that soon, but not in present commit which moves some code around. this vers does have a bug re that,
   # expressed as AssertionError: DelegatingMixin refuses to delegate self.delegate (which would infrecur) in <Cylinder#16801(i)>
   ###e

## ModelObject3D = Widget ###e remove soon -- see fix_color comment above; and probably buggy by its defaults hiding the delegate's

Geom3D = ModelObject3D # how would ModelObject3D & Geom3D differ? something about physicality?
PathOnSurface = Geom3D
LineSegment = Geom3D

## StateFormulaArg = StateArg

# utilities to refile (or redo)

def remove_unit_component(vec1, unitvec2): #e rename, or maybe just replace by remove_component or perp_component (no unit assumption)
    """Return the component of vec1 perp to unitvec2, by removing the component parallel to it.
    Requires, but does not verify, that vlen(unitvec2) == 1.0.
    """
    return vec1 - dot(vec1, unitvec2) * unitvec2

class Cylinder(Geom3D): #e super? ####IMPLEM - and answer the design Qs herein about state decls and model objs...
    """Be a cylinder, including as a surface... given the needed params... ###doc
    """
    ###e someday accept a variety of arg-sequences -- maybe this has to be done by naming them:
    # - line segment plus radius
    # - center plus orientation plus length plus radius
    # - circle (in space) plus length
    # But for now accept a linesegment or pair of endpoints, radius, color; let them all be mutable? or argformulae? or both??####
    # StateFormulaArg? ##e
    # OR, let creator say if they want to make it from state? hmm... ##### pro of that: in here we say Arg not StateFormulaArg.
    # If we do that, is there any easy way for creator to say "make all the args turn into state"? Or to let dflt_exprs be state??
    # Or let the model state be effectively an expr? but then how could someone assign to cyl attrs as if mutable? ####

    # args
    axis = Arg( LineSegment, (ORIGIN, ORIGIN + DX) ) #e let a pair of points coerce into a LineSegment, and let seq assign work from it
    radius = ArgOrOption( Nanometers, 1.0)
    color = ArgOrOption( Color, gray)
    capped = Option( bool, True) #e best default??
        #e should capped affect whether interior is made visible? (yes but as dflt for separate option)
        #e also provide exprs/opts for use in the caps, incl some way to be capped on one end, different colors, etc
    #e color for marks/sketch elements: point, line & fill & text -- maybe inherit defaults & option-decls for this
    #e surface texture/coordsys options

    # formulae
    ## dx = norm_Expr(axis) # ValueError: matrices are not aligned -- probably means we passed an array of V's to norm
    end2 = axis[1] #e or we might have to say axis.ends[1] etc
    end1 = axis[0]
    axisvector = end2 - end1 #e should also be axis.vector or so
    dx = norm_Expr(axisvector) #e axis.direction
    def _C__dy_dz(self):
        #e if axis has a dy, use that (some lines might come with one)
        # otherwise get an arb perp to our dx
        from pi_bond_sp_chain import arb_ortho_pair
            # "Given a nonzero vector, return an arbitrary pair of unit vectors perpendicular to it and to each other."
            #e refile that into geometry.py in cad/src, or use smth else in there, and grab these from a more central source in exprs
        return arb_ortho_pair(self.dx)
    dy = _self._dy_dz[0]
    dz = _self._dy_dz[1]
    length = vlen_Expr(axisvector)
    def draw(self):
        color = self.fix_color(self.color)
        end1, end2 = self.axis #####
        radius = self.radius
        capped = self.capped
        import drawer
        drawer.drawcylinder(color, end1, end2, radius, capped = capped) ###coordsys?
        return
    def perpvec_at_surfacepoint(self, point): #e rename?
        """Given a point on or near my surface (actually, on the surface of any coaxial cylinder),
        return a normal vector to the surface at that point (pointing outward).
        Ignores end-caps or cylinder length -- treats length as infinite.
        Works in same coords as all points of self, such as self.end1, end2.
        """
        return norm( remove_unit_component( point - self.end1, self.dx))
    #e bbox or the like (maybe this shape is basic enough to be an available primitive bounding shape?)
    pass

class Cylinder_HelicalPath(Geom3D): #e super?
    """Given a cylinder (cyl), produce a helical path on its surface (of given params)
    as a series of points (at given resolution -- but specifying resolution is #NIM except as part of path spec)
    starting at the left end (on an end-circle centered at cyl.end1),
    expressing the path in the same coords as the cylinder points (like end1) are in.
       Usage note: callers desiring path points invariant to rotations or translations of cyl
    should express cyl itself in a local coordsys which is rotated or translated, so that cyl.end1 and end2
    are also invariant.
    """
    # args
    #e need docstrings, defaults, some should be Option or ArgOrOption
    #e terms need correction, even tho not meant to be dna-specific here, necessarily (tho they could be): turn, rise, n, theta_offset
    cyl = Arg(Cylinder)
    n = Option(int, 100) # number of segments in path (one less than number of points)
    turn = Option( Rotations, 1.0 / 10.5) # number of rotations of vector around axis, in every path segment ###e MISNAMED??
    rise = Option( Nanometers, 0.34) ###k default
    theta_offset = Option( Radians, 0.0) # rotates entire path around cyl.axis
    color = Option(Color, black) # only needed for drawing it -- not part of Geom3D -- add a super to indicate another interface??##e
        ##e dflt should be cyl.attr for some attr related to lines on this cyl -- same with other line-drawing attrs for it
    ## start_offset = Arg( Nanometers)
    radius_ratio = Option(float, 1.1) ###e
    def _C_points(self):
        cyl = self.cyl
        theta_offset = self.theta_offset
        n = int(self.n) #k type coercion won't be needed once Arg & Option does it
        radius = cyl.radius * self.radius_ratio
        rise = self.rise
        turn = self.turn
        end1 = self.cyl.end1
        
        axial_offset = cyl.dx * rise # note: cyl.dx == norm(cyl.axisvector)
        cY = cyl.dy # perp coords to cyl axisvector (which is always along cyl.dx) [#e is it misleading to use x,y,z for these??]
        cZ = cyl.dz
        points = []
        turn_angle = 2 * pi * turn
        p0 = end1 #e plus an optional offset along cyl.axisvector?
        for i in range(n+1): 
            theta = turn_angle * i + theta_offset # in radians
            y = cos(theta) * radius # y and z are Widths (numbers)
            z = sin(theta) * radius
            vx = i * axial_offset # a Vector
            p = p0 + vx + y * cY + z * cZ
            points.append(p)
        return points
    def _C_segments(self):
        "compute self.segments, a list of pairs of successive path points [###e maybe they ought to be made into LineSegments]"
        p = self.points
        return zip(p[:-1], p[1:])
    def _C_segment_centers(self):
        "compute self.segment_centers [example use: draw base attach points (phosphates) in DNA]"
        return [(p0 + p1)/2.0 for p0,p1 in self.segments]
    def draw(self):
        color = self.fix_color(self.color)
        points = self.points
        glDisable(GL_LIGHTING) ### not doing this makes it take the color from the prior object 
        glColor3fv(color) ##k may not be enough, not sure
        glBegin(GL_LINE_STRIP)
        for p in points:
            ##glNormal3fv(-DX) #####WRONG? with lighting: doesn't help, anyway. probably we have to draw ribbon edges as tiny rects.
            # without lighting, probably has no effect.
            glVertex3fv(p)
        glEnd()
        glEnable(GL_LIGHTING)
        return
    pass


class Cylinder_Ribbon(Widget): #070129 #e rename?? #e super?
    """Given a cylinder and a path on its surface, draw a ribbon made from that path using an OpenGL quad strip
    (whose edges are path +- cyl.axisvector * axialwidth/2). Current implem uses one quad per path segment.
       Note: the way this is specific to Cylinder (rather than for path on any surface) is in how axialwidth is used,
    and that quad alignment and normals use cyl.axisvector.
       Note: present implem uses geom datatypes with bare coordinate vectors (ie containing no indication of their coordsys);
    it assumes all coords are in the current drawing coordsys (and has no way to check this assumption).
    """
    #args
    cyl = Arg(Cylinder)
    path = Arg(PathOnSurface) ###e on that cyl (or a coaxial one)
    color = ArgOrOption(Color, cyl.dflt_color_for_sketch_faces)
    axialwidth = ArgOrOption(Width, 1.0,
                             doc = "distance across ribbon along cylinder axis (actual width is presumably shorter since it's diagonal)"
                             ) #e rename
    showballs = Option(bool, False) # show balls at centers of segments ###KLUGE: hardcoded size
    showlines = Option(bool, False) # show lines from centers of segments to helix axis (almost)
        # (note: the lines from paired bases don't quite meet, and form an angle)
    def draw(self):
        cyl = self.cyl
        path = self.path
        axialwidth = self.axialwidth
        points = path.points #e supply the desired resolution?
        normals = map( cyl.perpvec_at_surfacepoint, points)
            ####IMPLEM perpvec_at_surfacepoint for any Surface, e.g. Cylinder (treat as infinite length; ignore end-caps)
            ####e points on it might want to keep their intrinsic coords around, to make this kind of thing efficient & well defined,
            # esp for a cyl with caps, whose caps also counted as part of the surface! (unlike in present defn of cyl.perpvec_at_surfacepoint)
        offset2 = axialwidth * cyl.dx * 0.5 # assumes Width units are 1.0 in model coords
        offset1 = - offset2
        offsets = (offset1, offset2)
        color = self.fix_color(self.color)
        interior_color = ave_colors(0.8, color, white) ### remove sometime?

        self.draw_quad_strip( interior_color, offsets, points, normals)
        if self.showballs: #070202
            kluge_hardcoded_size = 0.2
            from drawer import drawsphere # drawsphere(color, pos, radius, detailLevel)
            for c in path.segment_centers:
                ##e It might be interesting to set a clipping plane to cut off the sphere inside the ribbon-quad;
                # but that kind of fanciness belongs in the caller, passing us something to draw for each base
                # (in a base-relative coordsys), presumably a DisplistChunk instance. (Or a set of things to draw,
                #  for different kinds of bases, in the form of a "base view" base->expr function.)
                drawsphere(color, c, kluge_hardcoded_size, 2)
        if self.showlines:
            from drawer import drawline
            perpvec_at_surfacepoint = cyl.perpvec_at_surfacepoint
            for c in path.segment_centers:
                n = perpvec_at_surfacepoint(c)
                nout, nin = n * 0.2, n * 1.0 # hardcoded numbers -- not too bad since there are canonical choices 
                drawline(color, c + nout, c - nin) ##k lighting??
        # draw edges? see Ribbon_oldcode_for_edges
        return
    def draw_quad_strip(self, interior_color, offsets, points, normals):
        offset1, offset2 = offsets
        ## glColor3fv(interior_color)
        # actually I want a different color on the back, can I get that? ###k
        glDisable(GL_CULL_FACE)
        drawer.apply_material(interior_color)
        ## glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color) # gl args partly guessed #e should add specularity, shininess...
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        glBegin(GL_QUAD_STRIP)
            # old cmts, obs??:
            # this uses CULL_FACE so it only colors the back ones... but why gray not pink?
            # the answer - see draw_vane() -- I have to do a lot of stuff to get this right:
            # - set some gl state, use apply_material, get CCW ordering right, and calculate normals.
##        glColor3fv(interior_color)
##        print "draw_quad_strip",interior_color, offsets, points, normals
            ###BUG: points are 0 in y and z, normals are entirely 0 (as if radius was 0?)
        for p, n in zip( points, normals):
            glNormal3fv( n)
            glVertex3fv( p + offset2)
            glVertex3fv( p + offset1)
        glEnd()
        glEnable(GL_CULL_FACE)
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
        return
    pass

# ==

###e need to look up the proper parameter names -- meanwhile use fake ones that don't overlap the real ones --
# easy, just use the geometric ones in Cylinder_HelicalPath. Later we'll have our own terminology & defaults for those here.
## pitch # rise per turn
## rise

kluge_dna_ribbon_view_prefs_key_prefix = "A9 devel/kluge_dna_ribbon_view_prefs_key_prefix"

def dna_pref(subkey):
    return kluge_dna_ribbon_view_prefs_key_prefix + '/' + subkey

from preferences import _NOT_PASSED ###k
def get_pref(key, dflt = _NOT_PASSED): #e see also... some stateref-maker I forget ####DUP CODE with test.py, should refile
    """Return a prefs value. Fully usage-tracked.
    [Kluge until we have better direct access from an expr to env.prefs. Suggest: use in call_Expr.]
    """
    import env
    return env.prefs.get(key, dflt)

def get_dna_pref(subkey, **kws): ###DESIGN FLAW: lack of central decl means no warning for misspelling one ref out of several
    return get_pref( dna_pref(subkey), **kws)

class DNA_Cylinder(Macro):
    color = Option(Color, gray) #e default should be transparent/hidden
    color1 = Option(Color, red)
    color2 = Option(Color, blue)
    cyl = StateArg( Cylinder(color = color, radius = 1.0), ###IMPLEM this way of giving dflts for attrs added by type coercion
                        #k radius and its units
                    ##e make this work: Automatic, #e can this be given as a default to type coercion, to make it "just create one"?
                    Cylinder(color = color, radius = 1.0)((ORIGIN-6*DX, ORIGIN+10*DX)), ###e silly defaults, change back to ORIGIN end1 soon
                        ###k why did that () not fix this warning: "warning: this expr will get 0 arguments supplied implicitly" ??
                        ###e can we make it ok to pass length and let end1 be default ORIGIN and dx be default DX?
                    doc = "cylindrical surface of double helix"
                   ) ###e add dflt args in case we typecoerce it from a line
        ###e or maybe even bring in a line and make the cyl ourselves with dflt radius? somewhere we should say dflt radius & length.
        # ah, the right place is probably in the type expr: Cylinder(radius = xxx, length = xxx)
        #e do we want to let a directly passed cyl determine color, as the above code implies it would?
        # if not, how do we express that: StateArg(...)(color = color)??
        # what if color was not passed to self, *then* do we want it fom cyl? same Q for radius.
    ###e correct the figures and terminology: rise, turn, pitch
    rise = StateOption(Angstroms, B_Dna.BASE_SPACING, doc = "distance along helix axis from one basepair to the next")
        #k can you say units that way? not yet, so we have a kluge to turn them into nm below.
    rise_nm = rise / 10.0
    bpt = StateOption(Float, 10.5, doc = "bases per turn") ###e default will depend on origami raster style
    pitch = rise * bpt ##k #e and make it settable?
    path1 = Cylinder_HelicalPath( cyl, rise = rise_nm, turn = 1/bpt,
                                  n = cyl.length / rise_nm
                                  ) #e need theta_offset?
    ## should be: path2 = Rotate(path1, 150.0, cyl.axis)
        #e note, this seems to be "rotate around a line" (not just a vector), which implies translating so line goes thru origin;
        # or it might be able to be a vector, if we store a relative path... get this straight! ###e (for now assume axis could be either)
    ## here's an easier way, and better anyway (since the path's state (when it has any) should be separate):
    path2 = path1(theta_offset = 150*2*pi/360)
    # prefs values used in appearance [##e in future, we'll also use these to index a set of display lists, or so]
    show_phosphates = call_Expr( get_dna_pref, 'show phosphates', dflt = False)
    show_lines = call_Expr( get_dna_pref, 'show lines', dflt = False)
    # appearance (stub -- add handles/actions, remove cyl)
    delegate = Overlay( If_kluge(
                            call_Expr( get_dna_pref, 'show central cyl', dflt = False),
                            cyl, # works when alone
                            Spacer()),
                        Cylinder_Ribbon(cyl, path1, color1, showballs = show_phosphates, showlines = show_lines ),
                        Cylinder_Ribbon(cyl, path2, color2, showballs = show_phosphates, showlines = show_lines )
                       )
    pass

# ==

World_dna = World # try to use the same world as in demo_drag... generalize it as needed for that, keeping both examples working. ##e

def dna_ribbon_view_toolcorner_expr_maker(world_holder): #070201 modified from demo_drag_toolcorner_expr_maker -- not yet modified enough ###e
    """given an instance of World_dna_holder (??), return an expr for the "toolcorner" for use along with
    whatever is analogous to GraphDrawDemo_FixedToolOnArg1 (on the world of the same World_dna_holder)
    """
    world = world_holder.world
##    if "kluge" and not world._cmd_Clear_nontrivial:
##        # ###BUG: this modifies world in the same draw event that shows it, evidently (guess from console warning),
##        # so we need to clean it up somehow -- make it as if it was an auto-open command when we set up this demo.
##        #
##        # ###BAD UI: this makes the clear command act more like "reset";
##        # since we have no add or mod command, the reset cmd is prob not needed yet at all.
##        # Remove it from this UI (for now) when this is verified. ###e
##        ## world.append_node( DNA_Cylinder())
##        world_holder.make_and_add(DNA_Cylinder())
    expr = SimpleColumn(
        checkbox_pref( dna_pref('show central cyl'), "show central cyl?", dflt = False), # works now, didn't at first
        checkbox_pref( dna_pref('show phosphates'),   "show phosphates?",   dflt = False),
        checkbox_pref( dna_pref('show lines'),   "show lines?",   dflt = False), # temporary
        ActionButton( world_holder._cmd_Make_DNA_Cylinder, "button: make dna cyl"),
        If_kluge( getattr_Expr( world, '_cmd_Clear_nontrivial'),
                  ActionButton( world._cmd_Clear, "button: clear"),
                  ActionButton( world._cmd_Clear, "button (disabled): clear", enabled = False)
         ),
        DisplistChunk(TextRect( format_Expr( "(%d items)" , len(world.nodelist) )))
     )
    return expr


class World_dna_holder(InstanceMacro): #070201 modified from GraphDrawDemo_FixedToolOnArg1; need to unify it as a ui-provider framework
    # args
    # options
    # internals
    world = Instance( World_dna() ) # has .nodelist I'm allowed to extend
    _value = DisplistChunk( world)
    
    _cmd_Make_DNA_Cylinder_tooltip = "make a DNA_Cylinder" ###e or parse it out of method docstring, marked by special syntax??
    def _cmd_Make_DNA_Cylinder(self):
        expr = DNA_Cylinder()
        # Note: ideally, only that much (expr, at this point) would be stored as world's state, with the following wrappers
        # added on more dynamically as part of finding the viewer for the model objects in world. ###e
        # (Nice side effect: then code-reloading of the viewer would not require clearing and remaking the model objs.)
        expr = DisplistChunk( expr) # displist around cylinder itself -- speeds(unverified) redraw of cyl while it's dragged, or anywhen [070203]
            ###BUG (though this being the cause is only suspected): prefs changes remake the displist only the first time in a series of them,
            # until the next time the object is highlighted or certain other things happen (exact conditions not yet clear); not yet diagnosed;
            # might relate to nested displists, since this is apparently the first time we've used them.
            # This is now in BUGS.txt as "070203 DisplistChunk update bug: series of prefs checkbox changes (eg show central cyl,
            #  testexpr_30g) fails to remake the displist after the first change", along with suggestions for investigating it. #####TRYTHEM
        expr = DraggableObject( expr)
        ## expr = DisplistChunk( expr) # displist around drag-repositioned cyl -- prevents drag of this cyl from recompiling world's dlist
            ###BUG: seems to be messed up by highlighting/displist known bug, enough that I can't tell if it's working in other ways --
            # the printed recompile graph makes sense, but the number of recomps (re changetrack prediction as I drag more)
            # seems wrong (it only recompiles when the drag first starts, but I think every motion ought to do it),
            # but maybe the highlight/displist bug is preventing the drag events from working properly before they get that far.
            # So try it again after fixing that old issue (not simple). [070203 9pm]
        self.world.make_and_add( expr)
        return
    
    pass # end of class World_dna_holder [a command-making object, I guess ###k]

# end
