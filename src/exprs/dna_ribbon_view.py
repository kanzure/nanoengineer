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
from Rect import Rect, RectFrame, IsocelesTriangle, Spacer, Sphere, Line

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

import projection
reload_once(projection)
from projection import DrawInCorner

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

class Cylinder(Geom3D): #e super? ####IMPLEM - and answer the design Qs herein about state decls and model objs... #e refile
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
    center = (end1 + end2) / 2.0
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
# temporarily remove these just to make sure i don't use them anymore for phosphates --
# they work fine and can be brought back anytime after the next commit. [070204 late]
##    def _C_segments(self):
##        "compute self.segments, a list of pairs of successive path points [###e maybe they ought to be made into LineSegments]"
##        p = self.points
##        return zip(p[:-1], p[1:])
##    def _C_segment_centers(self):
##        "compute self.segment_centers [obs example use: draw base attach points (phosphates) in DNA; not presently used 070204]"
##        return [(p0 + p1)/2.0 for p0,p1 in self.segments]
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
    showballs = Option(bool, False) # show balls at points [before 070204 late, at segment centers instead] ###KLUGE: hardcoded size
    showlines = Option(bool, False) # show lines from points to helix axis (almost) [before 070204 late, at segment centers]
        # (note: the lines from paired bases don't quite meet, and form an angle) ###UNTESTED since revised
    def draw(self):
        self.draw_some(None) # None means draw all segments
    def draw_some(self, some = None):
        "#doc; some can be (i,j) to draw only points[i:j], or (i,None) to draw only points[i:]" # tested with (2,-2) and (2,None)
        cyl = self.cyl
        path = self.path
        axialwidth = self.axialwidth
        points = path.points #e supply the desired resolution?
        if some:
            i,j = some
            points = points[i:j]
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
            for c in points:
                ##e It might be interesting to set a clipping plane to cut off the sphere inside the ribbon-quad;
                # but that kind of fanciness belongs in the caller, passing us something to draw for each base
                # (in a base-relative coordsys), presumably a DisplistChunk instance. (Or a set of things to draw,
                #  for different kinds of bases, in the form of a "base view" base->expr function.)
                drawsphere(color, c, kluge_hardcoded_size, 2)
        if self.showlines:
            from drawer import drawline
            for c, n in zip(points, normals):
                nout, nin = n * 0.2, n * 1.0 # hardcoded numbers -- not too bad since there are canonical choices 
                drawline(color, c + nout, c - nin) ##k lighting??
        # draw edges? see Ribbon_oldcode_for_edges
        return
    def draw_quad_strip(self, color, offsets, points, normals): #e refile into draw_utils -- doesn't use self
        """draw a constant-color quad strip whose "ladder-rung" (inter-quad) edges (all parallel, by the following construction)
        are centered at the given points, lit using the given normals, and have width defined by offsets (each ladder-rung
        going from point + offsets[1] to point + offsets[0]).
        """
        offset1, offset2 = offsets
        ## glColor3fv(color)
        # actually I want a different color on the back, can I get that? ###k
        glDisable(GL_CULL_FACE)
        drawer.apply_material(color)
        ## glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color) # gl args partly guessed #e should add specularity, shininess...
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        glBegin(GL_QUAD_STRIP)
            # old cmts, obs??:
            # this uses CULL_FACE so it only colors the back ones... but why gray not pink?
            # the answer - see draw_vane() -- I have to do a lot of stuff to get this right:
            # - set some gl state, use apply_material, get CCW ordering right, and calculate normals.
##        glColor3fv(color)
##        print "draw_quad_strip",color, offsets, points, normals
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
    delegate = Overlay( If(
                            call_Expr( get_dna_pref, 'show central cyl', dflt = False),
                            cyl, # works when alone
                            Spacer()),
                        Cylinder_Ribbon(cyl, path1, color1, showballs = show_phosphates, showlines = show_lines ),
                        Cylinder_Ribbon(cyl, path2, color2, showballs = show_phosphates, showlines = show_lines )
                       )

    # geometric attrs should delegate to the cylinder -- until we can say that directly, do the ones we need individually [070208]
    # (for more comments about a fancier case of this, see attr center comments in draggable.py)
    center = cyl.center ###e actually the origami center might be the seam, not the geometric center -- worry about that later
    
    def make_selobj_cmenu_items(self, menu_spec, highlightable): #070204 new feature, experimental #070205 revised api
        """Add self-specific context menu items to <menu_spec> list when self is the selobj (or its delegate(?)... ###doc better).
        Only works if this obj (self) gets passed to Highlightable's cmenu_maker option (which DraggableObject(self) will do).
        [For more examples, see this method as implemented in chem.py, jigs*.py in cad/src.]
        """
        menu_spec.extend([
            ("DNA Cylinder", noop, 'disabled'), # or 'checked' or 'unchecked'; item = None for separator; submenu possible

            ("show potential crossovers", self._cmd_show_potential_crossovers), #e disable if none (or all are already shown or real)

            ("change length", [
                ("left extend by 1 base", lambda self = self, left = 1, right = 0: self.extend(left, right)),
                ("left shrink by 1 base", lambda self = self, left = -1, right = 0: self.extend(left, right)),
                ("right extend by 1 base", lambda self = self, left = 0, right = 1: self.extend(left, right)),
                ("right shrink by 1 base", lambda self = self, left = 0, right = -1: self.extend(left, right)),
                ("both extend by 1 base", lambda self = self, left = 1, right = 1: self.extend(left, right)),
                ("both shrink by 1 base", lambda self = self, left = -1, right = -1: self.extend(left, right)),
             ] ),
        ])
        # print "make_selobj_cmenu_items sees mousepoint:", highlightable.current_event_mousepoint() ###BUG: exception for this event
        #
        # That happens because glpane._leftClick_gl_event_info is not defined for this kind of event, nor are some other attrs
        # defined (in exprs module) for a drag event that comes right after a leftclick.
        #
        # That could be fixed... in a few different ways:
        # - Support general posn-specific selobj behavior (highlight image, sbar text, cmenu):
        #   That would require the baremotion-on-one-selobj optim
        #   to notice a per-selobj flag "I want baremotion calls" (a new method in selobj interface),
        #   and call it for all baremotion, with either side effects or retval saying whether new highlight image,
        #   sbar text, or cmenu point is needed. (Totally doable, but not completely trivial.)
        # - Or, have intra-selobj different 2nd glnames, and when they change, act like it is (or might be) a new selobj.
        #   This is not a lot different from just splitting things into separate selobjs (tho it might be more efficient
        #   in some cases, esp. if you wanted to use weird gl modes for highlighting, like xormode drawing; alternatively
        #   it might be simpler in some cases).
        # - Or, just support posn-specific selobj cmenu (but not sbar or highlight image changes):
        #   that could be simpler: just save the point (etc) somewhere
        #   (as computed in baremotion to choose the selobj), and have it seen by current_event_mousepoint in place of
        #   glpane._leftClick_gl_event_info (or rename that and use the same attr).
        # But customizing only the cmenu is not really enough. So: maybe we'll need this someday, and we'll use
        # one of the fancier ways when we do, but for now, do other things, so this improvement to selobj API is being put off.
        # (Except for this unused arg in the API, which can remain for now; for some of these methods maybe it could be removed.)
        return

    def extend(self, left, right):####IMPLEM (and then improve the UI for it)
        print "extend (left = %r, right = %r) is NIM" % (left, right)

    def _cmd_show_potential_crossovers(self):
        print "_cmd_show_potential_crossovers is NIM"

    # ModelTreeNodeInterface formulae
    mt_name = State(str, "DNA Cylinder #n") ###e make it unique somehow #e make it editable
    mt_kids = () #e add our crossovers, our yellow rect demos
    mt_openable = False #e
    mt_node_id = getattr_Expr( _self, '_e_serno')
    
    pass # end of class DNA_Cylinder

# ==

def dna_ribbon_view_toolcorner_expr_maker(world_holder): #070201 modified from demo_drag_toolcorner_expr_maker -- not yet modified enough ###e
    """given an instance of World_dna_holder (??), return an expr for the "toolcorner" for use along with
    whatever is analogous to GraphDrawDemo_FixedToolOnArg1 (on the world of the same World_dna_holder)
    """
    world = world_holder.world
    number_of_objs = getattr_Expr(world, 'number_of_objects')
        ## WARNING: when that said world.number_of_objects instead, it turned into a number not an expr, and got usage-tracked,
        # and that meant this expr-maker had to get called again (and the result presumably remade again)
        # every time world.number_of_objects changed. [For more details, see comments here in cvs rev 1.40. 070209]
        # (This would not have happened if this was an expr rather than a def, since then,
        #  world would be _self.attr (symbolic) rather than an Instance.)
        ###BUG: Are there other cases throughout our code of debug prints asking for usage-tracked things, causing spurious invals??
    expr = SimpleColumn(
        checkbox_pref( dna_pref('show central cyl'), "show central cyl?", dflt = False), # works now, didn't at first
        checkbox_pref( dna_pref('show phosphates'),   "show phosphates?",   dflt = False),
        checkbox_pref( dna_pref('show lines'),   "show lines?",   dflt = False), # temporary
        ActionButton( world_holder._cmd_Make_DNA_Cylinder, "button: make dna cyl"),
        ActionButton( world_holder._cmd_Make_some_rects, "button: make rects over cyls"),
        If( getattr_Expr( world, '_cmd_Clear_nontrivial'),
            ActionButton( world._cmd_Clear, "button: clear"),
            ActionButton( world._cmd_Clear, "button (disabled): clear", enabled = False)
         ),
        Overlay(
            DisplistChunk(TextRect( format_Expr( "(%d objects in world)" , number_of_objs ))),
            If( eq_Expr( number_of_objs, 0),
                DrawInCorner(corner = (0,0))( TextRect("(empty model)") ),
                Spacer() ),
         ),
     )
    return expr


class World_dna_holder(InstanceMacro): #070201 modified from GraphDrawDemo_FixedToolOnArg1; need to unify them as a ui-provider framework
    # args
    # options
    # internals
    world = Instance( World() ) # maintains the set of objects in the model
    _value = DisplistChunk( world)
    
    _cmd_Make_DNA_Cylinder_tooltip = "make a DNA_Cylinder" ###e or parse it out of method docstring, marked by special syntax??
    def _cmd_Make_DNA_Cylinder(self):
        ###e ideally this would be a command defined on a "dna origami raster", and would show up as a command in a workspace UI
        # only if there was a current raster or a tendency to automake one or to ask which one during or after a make cyl cmd...
        world = self.world
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
        newcyl = world.make_and_add( expr, type = "DNA_Cylinder") #070206 added type = "DNA_Cylinder"
        if 'kluge070205-v2' and world.number_of_objects > 1: # note: does not imply number of Cylinders > 1!
            ### KLUGE: move newcyl, in an incorrect klugy way -- works fine in current code,
            # but won't work if we wrap expr more above, and won't be needed once .move works.
            ### DESIGN FLAW: moving this cyl is not our business to do in the first place,
            # until we become part of a "raster guide shape's" make-new-cyl-inside-yourself command.
            cyls = world.list_all_objects_of_type(DNA_Cylinder)
                # a nominally read-only list of all cylinders in the world, in order of _e_serno (i.e. creation order as Instances)
                # (WARNING: this order might be changed in the API of list_all_objects_of_type).
                ###KLUGE -- this list should be taken only from a single raster
            if len(cyls) > 1:
                if newcyl is cyls[-1]:
                    newcyl.motion = cyls[-2].motion - DY * 2.7 ###KLUGE: assumes current alignment
                        # Note: chosen distance 2.7 nm includes "exploded view" effect (I think).
                else:
                    print "added in unexpected order" ###should never happen as long as _e_serno is ordered like cyl creation order
        return
    def _cmd_Make_some_rects(self): #070206 just to show we can make something else and not mess up adding/moving the next cyl
        world = self.world
        expr = Center(Rect(0.5, 1, yellow))
        expr = DraggableObject(expr) # note: formally these rects are not connected to their cyls (e.g. won't move with them)
        cyls = world.list_all_objects_of_type(DNA_Cylinder)
        #e could remove the ones that already have rects, but that requires storing the association -- doesn't matter for this tests
        rects = []
        for cyl in cyls:
            posn = cyl.center # includes effect of its DraggableObject motion
                ### is this being usage tracked? guess yes... what are the effects of that?? guess: too much inval!! ####k
                ###e need debug code to wra this with "show me the inval-and-recompute-causing-fate of whatever usage is tracked here"
##            print "cyl.center was %r" % (posn,)
            where = posn + DZ * 1.5 ###KLUGE: assumes current alignment
            newrect = world.make_and_add(expr, type = "rect")
            newrect.motion = where ###KLUGE, I think, but works for now
            rects.append(newrect) #070211 hack experiment
        for r1,r2 in zip(rects[1:], rects[:-1]):
            junk = world.make_and_add( Line( getattr_Expr(r1,'center'), getattr_Expr(r2,'center'), red), type = "line")
        return
    def _cmd_Show_potential_crossovers(self): #070208 experimental stub prototype
        """for all pairs of cyls adjacent in a raster (more or less),
        perhaps assuming aligned as desired for now (tho for future general use this would be bad to assume),
        come up with suggested crossovers, and create them as potential model objs,
         which shows them (not if the "same ones" are already shown, not any overlapping ones --
         but shown ones can also be moved slightly as well as being made real)
        [later they can be selected and made real, or mad real using indiv cmenu ops; being real affects them and their cyls
         but is not an irreversible op! it affects the strand paths...]
        """
        world = self.world
        cyls = world.list_all_objects_of_type(DNA_Cylinder)
        cylpairs = []
        for cyl1 in cyls:
            for cyl2 in cyls:
                if id(cyl1) < id(cyl2): #e no, use the order in the list, use indices in this loop, loop over i and j in range...
                    cylpairs.append((cyl1,cyl2)) ##e make this a py_utils subroutine: unordered_pairs(cyls) ??
        for cyl1, cyl2 in cylpairs:
            # create an object (if there is not one already -- else make it visible again?)
            # which continuously shows potential crossovers between these cyls.
            # STUB: create one anew.
            # STUB: let it be a single connecting line.
            ###BUG: cyl1.center evals to current value -- but what we want here is an expr to eval later. ###FIX: use getattr_Expr
            # What do we do? Someday we'll rewrite this loop as an iterator expr in which cyl1 will be a Symbol or so,
            # so simulate that now by making it one. #####e DECIDE HOW, DO IT, IMPLEM
            ### [BUT, note, it's an academic Q once we use a new macro instead, since we pass it the cyls, not their attrs.]
            expr = Line(cyl1.center, cyl2.center, blue, thickness = 2) #e thickness or width?? ###IMPLEM Line and refile this design note:
                ###e design note: it's a line segment, but LineSegment is too long & nonstd a name,
                # and you need endpoints anyway to conveniently specify even a ray or line,
                # so have options to make it ray or line. if you want to use end1 and direction/length or vector, do so,
                # but you could want that too for any of segment, ray, or line (except you'd like option to leave out length for some).
            index = ( object_id(cyl1), object_id(cyl2) ) ### IMPLEM object_id #e rename it? make it an attr of object?
                #### design note: this is the index for the new instance (find or make; if find, maybe make visible or update prefs).
                # (or maybe just discard/replace the old one? NO, see below for why)
                # We also need an InstanceDict index, and to implem InstanceDict and use it
                # for this. These objects would be children of the common parent of the cyls (found dynamically so they go inside
                # groups etc when possible, i think, at least by default -- but if user moves them in MT, that should stick,
                # WHICH IS A BIG REASON TO FIND AND REUSE rather than replacing -- user might have done all kinds of per-obj edits).
##            # older cmt:
##            # ok, who has this op: one of the cyls, or some helper func, or *this command*?
##            # find backbone segs on cyl1 that are facing cyl2 and close enough to it, and see if cyl2 backbone is ok
##            # *or*, just find all pairs of close enough backbone segs -- seems too slow and forces us to judge lots of near ones - nah
##            # (what if the cyls actually intersect? just ignore this issue, or warn about it and refuse to find any??)
##            # (in real life, any cyl that overlaps another in some region should probably refuse to suggest any mods in that region --
##            #  but we can ignore that issue for now! but it's not too different than refusing to re-suggest the same crossover --
##            #  certain features on a cyl region (crossovers, overlaps) mean don't find new potential crossovers in that region.)
##            for seg in cyl1.backbone_segments: ###IMPLEM; note, requires coord translation into abs coords -- kluge: flush motion first??
##                pass##stub
        ######e more
        return
    pass # end of class World_dna_holder [a command-making object, I guess ###k]

# end
