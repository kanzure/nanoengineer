# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
dna_ribbon_view.py

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


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

from math import pi
from Numeric import dot, cos, sin

from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import glColor3fv
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glBegin
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd
from OpenGL.GL import glEnable
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import GL_LIGHT_MODEL_TWO_SIDE
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glLightModelfv
from OpenGL.GL import GL_QUAD_STRIP
from OpenGL.GL import glNormal3fv
from OpenGL.GL import GL_FALSE

from exprs.Overlay import Overlay

from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.gl_lighting import apply_material

from exprs.world import World

from exprs.Rect import Rect, Spacer, Sphere, Line

from exprs.Column import SimpleColumn, SimpleRow

from exprs.DisplayListChunk import DisplayListChunk

from exprs.Highlightable import Highlightable

from exprs.transforms import Translate

from exprs.Center import Center

from exprs.TextRect import TextRect

from exprs.controls import checkbox_pref, ActionButton

from exprs.draggable import DraggableObject

from exprs.projection import DrawInCenter

from exprs.pallettes import PalletteWell

from geometry.VQT import norm

from utilities.constants import gray, black, red, blue, purple, white
from utilities.constants import ave_colors, noop
from utilities.constants import green
from utilities.constants import yellow

from exprs.widget2d import Widget, Stub
from exprs.Exprs import norm_Expr, vlen_Expr, int_Expr, call_Expr, getattr_Expr, format_Expr
from exprs.Exprs import eq_Expr
from exprs.If_expr import If
from exprs.instance_helpers import ModelObject, InstanceMacro, DelegatingInstanceOrExpr
from exprs.instance_helpers import WithAttributes
from exprs.attr_decl_macros import Arg, ArgOrOption, Option, State, StateOption, StateArg
from exprs.ExprsConstants import Width, ORIGIN, DX, DY, DZ, Color, Point, Vector
from exprs.__Symbols__ import _self

# undefined symbols: object_id, nim, ditto

# temporary kluge: excerpt from cad/src/DnaGenerator.py; this copy used locally for constants [values not reviewed]:
class B_Dna:
    geometry = "B-DNA"
    TWIST_PER_BASE = -36 * pi / 180   # radians [this value is not used here since it differs from Paul's Origami values]
    BASE_SPACING = 3.391              # angstroms

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

    opacity = Option(float, 1.0) #ninad 2008-06-25 See also self.draw.

    # formulae
    ## dx = norm_Expr(axis) # ValueError: matrices are not aligned -- probably means we passed an array of V's to norm
    end2 = axis[1] #e or we might have to say axis.ends[1] etc
    end1 = axis[0]
    axisvector = end2 - end1 #e should also be axis.vector or so
    dx = norm_Expr(axisvector) #e axis.direction
    def _C__dy_dz(self):
        #e if axis has a dy, use that (some lines might come with one)
        # otherwise get an arb perp to our dx
        from model.pi_bond_sp_chain import arb_ortho_pair
            # "Given a nonzero vector, return an arbitrary pair of unit vectors perpendicular to it and to each other."
            #e refile that into geometry.py in cad/src, or use smth else in there, and grab these from a more central source in exprs
        return arb_ortho_pair(self.dx)
    dy = _self._dy_dz[0]
    dz = _self._dy_dz[1]
    length = vlen_Expr(axisvector)
    center = (end1 + end2) / 2.0
    def draw(self):
        #@ATTENTION: The new attr 'self.opacity'  was added on 2008-06-26. But
        #call to self.fix_color doesn't set the opacity (transparency) properly.
        #Also, based on test, not 'fixing the color' and directly using
        #self.color works. So, defining the following condition. (use of
        #self.fix_color may be unnecessary even for opaque objects but it is
        #untested -- Ninad 2008-06-26
        if self.opacity == 1.0:
            color = self.fix_color(self.color)
        else:
            color = self.color

        end1, end2 = self.axis #####
        radius = self.radius
        capped = self.capped

        drawcylinder(color,
                     end1,
                     end2,
                     radius,
                     capped = capped,
                     opacity = self.opacity
                     ) ###coordsys?
        return
    def perpvec_at_surfacepoint(self, point): #e rename?
        """Given a point on or near my surface (actually, on the surface of any coaxial cylinder),
        return a normal (unit length) vector to the surface at that point (pointing outward).
        Ignores end-caps or cylinder length -- treats length as infinite.
        Works in same coords as all points of self, such as self.end1, end2.
        """
        return norm( remove_unit_component( point - self.end1, self.dx)) ##e rename: norm -> normalize? unitvector? normal?
    #e bbox or the like (maybe this shape is basic enough to be an available primitive bounding shape?)
    pass

class Cylinder_HelicalPath(Geom3D): #e super?
    """Given a cylinder (cyl), produce a helical path on its surface (of given params)
    as a series of points (at given resolution -- but specifying resolution is #NIM except as part of path spec)
    starting at the left end (on an end-circle centered at cyl.end1),
    expressing the path in the same coordsys as the cylinder points (like end1) are in.
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
        # (note: the lines from paired bases don't quite meet, and form an angle)
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
            for c in points:
                ##e It might be interesting to set a clipping plane to cut off the sphere inside the ribbon-quad;
                # but that kind of fanciness belongs in the caller, passing us something to draw for each base
                # (in a base-relative coordsys), presumably a DisplayListChunk instance. (Or a set of things to draw,
                #  for different kinds of bases, in the form of a "base view" base->expr function.)
                drawsphere(color, c, kluge_hardcoded_size, 2)
        if self.showlines:
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
        apply_material(color)
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

from foundation.preferences import _NOT_PASSED ###k
def get_pref(key, dflt = _NOT_PASSED): #e see also... some stateref-maker I forget ####DUP CODE with test.py, should refile
    """Return a prefs value. Fully usage-tracked.
    [Kluge until we have better direct access from an expr to env.prefs. Suggest: use in call_Expr.]
    """
    import foundation.env as env
    return env.prefs.get(key, dflt)

def get_dna_pref(subkey, **kws): ###DESIGN FLAW: lack of central decl means no warning for misspelling one ref out of several
    return get_pref( dna_pref(subkey), **kws)

class DNA_Cylinder(ModelObject): #070215 DIorE -> ModelObject (affects _e_model_type_you_make)
    #070213 started revising this to store state in self (not cyl) and know about seam...
    # [done? I guess yes, but a newer thing is not -- the strand1_theta stuff (needed for origami grid support),
    #  while partly done, is not yet used for real (tho maybe called) and not fully implem in this class either. #####e ]
    """A guide object for creating a cylindrical double-helical or "duplex" domain of DNA (with fully stacked bases,
    but not usually with fully connected backbone -- that is, strands can enter and leave its two helices).
       [#e may be renamed to something mentioning duplex or double helix, especially once it no longer needs to remain straight]
       ### doc this better -- needs intro/context:
       We think of a symmetric cylinder as having a central inter-base segment, with the same number of bases on either side.
    But there is no requirement that a specific cylinder be symmetric. (It will be if n_turns_left == n_turns_right in its state.)
    The central segment (not really central if it's not symmetric) is thought of as the seam (for origami)
    and is used as an origin for the indexing of inter-base segments and bases, as follows:
    - base-position indices are 0,1,2 to the right of (after) this origin, and -1, -2, etc to the left.
    - inter-base segments are numbered 0 at this origin (and in general, by the following base).
    This means the order is ... base(-1) -- segment(0)(== origin) -- base(0) -- ...
    (Note: this is subject to revision if it turns out some other scheme is standard or much better. ###e)
       Note that ficticious segment numbers at the ends, which have only one endpoint that's a real base index,
    might be useful in some places, but won't be included by default when iterating over inter-base helix segments.
    That is, by default (when accessing related attrs), there will be one fewer inter-base segment than base.
    """
    color_cyl = Option(Color, gray, doc = "color of inner solid cylinder (when shown)") #e default should be transparent/hidden
    color1 = Option(Color, red, doc = "default color of helix 1 of this cylinder (overridable by strand colors #nim)")
    color2 = Option(Color, blue, doc = "default color of helix 2 of this cylinder (overridable by strand colors #nim)")

    n_turns_left =  State(float, 1.5, doc = "number of turns before seam or interbase-index-origin")
    n_turns_right = State(float, 2.5, doc = "number of turns after seam or interbase-index-origin")

    bpt = StateOption(float, 10.5, doc = "bases per turn") ###e default will depend on origami raster style #e rename: bases_per_turn?

    n_bases_left = int_Expr( n_turns_left * bpt) ###IMPLEM int_Expr; make it round or truncate? If round, rename it?
    n_bases_right = int_Expr( n_turns_right * bpt)
        ### PROBLEM: base indices will change if bpt is revised -- what if crossovers were chosen first? do crossovers need to be
        # turn-indexed instead? Or something weirder, like "this turn, then this many bases away in this direction"??
        # (Does this ever happen in Paul's UI stages? #k) [mentioned in 2/19 meeting agenda]

    n_bases = n_bases_left + n_bases_right # this determines length

    ###e need options strand1_theta, strand2_theta -- one defaults to modified other, i guess... NOT SO SIMPLE --
    # each one has to do that, but not be circular -- it's our first unavoidably needed ability
    # to specify constrained dofs in more than one way. hmm.
    #####DECIDE HOW
    # idea, not sure if kluge: a circular spec would eval to None, and you could then say spec1 or spec2,
    # so if spec1 was circular when evalled, you'd get spec2.
    # - would it work in this case?
    # - is it a kluge in general, or well-defined and safe and reasonable?
    # - what if a legitimate value could be boolean-false? is a modified or_Expr ok? rather than None, use Circular (which is false)??
    #
    #   strand1_theta = Option( Degrees, FIRST_NON_CIRCULAR( _self.strand2_theta + offset, 0 ) )
    #       # catches CircularDefinitionError (only if this lval is mentioned in the cycle?), tries the next choice
    #
    #   or -- strand1_theta = Option( Degrees, first_non_circular_choice_among = ( _self.strand2_theta + offset, 0 ) )
    #
    #   strand2_theta = Option( Degrees, _self.strand1_theta - offset ) # raises CircularDefinitionError (saying the cycle it found?)
    #
    # PROBLEM: I suspect the behavior depends on the order of eval of the defs, at least if cycles break in more than one place.
    # PROBLEM: you have to manually create the proper inverse formulas -- nothing catches mistake if they're not inverses.
    # PROBLEM: the above might work for initial sets (from being unset) --
    #          but if they are State, what about how they respond to modification-sets?
    #          this requires "set all at once" and know what to keep fixed; discussed elsewhere (where? corner situations??);
    #          one way is "fix up inconsistencies later" (or on request); all ways require knowing the set of related variables.
    # (In general, you have to be able to do that -- but for simple affine cases, system ought to do it for you.
    #  So for these simple affine constraints, shouldn't we use a specialized mechanism instead?
    #  like state aliases with ops in lvals...)
    #
    ##e then use them below to make path1 and path2
    #
    # here is an ad-hoc method for now:

    strand1_theta = Option( Degrees, None)
    strand2_theta = Option( Degrees, None)

    def _C_use_strand12_theta(self):
        s1 = self.strand1_theta
        s2 = self.strand2_theta
        offset = 150 ### guess
        if s1 is None and s2 is None:
            s1 = 0 # not both undefined
        if s1 is None:
            s1 = s2 + offset
        if s2 is None:
            s2 = s1 - offset
        s1 %= 360.0
        s2 %= 360.0
        return s1, s2

    use_strand1_theta = _self.use_strand12_theta[0] ### USE ME -- note, in degrees, not necessary limited to [0,360]
    use_strand2_theta = _self.use_strand12_theta[1]


    center = State(Point, ORIGIN) ###e make these StateArgs... #e put them in the model_state layer   #e rename to position??

    def move(self, motion): ###CALL ME
        self.center = self.center + motion
        return

    direction = State(Vector, DX) # must be unit length!
        #e make center & direction get changed when we move or rotate [entirely nim, but someday soon to be called by DraggableObject]
        #e make the theta_offset (or whatever) also get changed then (the rotation around cyl axis)
    ###e should we revise direction/theta_offset to a local coordsys?? in fact, should we include center in that too?
    ###e should we define ourselves so locally that we don't bother to even store this center/direction/axisrotation at all?
    # (quite possibly, that would simplify the code greatly... otoh, we may need to get revised abs posns inside our bases somehow...)

    ###e correct the figures and terminology: rise, turn, pitch
    rise = StateOption(Angstroms, B_Dna.BASE_SPACING, doc = "distance along helix axis from one basepair to the next")
        #k can you say units that way? not yet, so we have a kluge to turn them into nm below.
    rise_nm = rise / 10.0 #e is the attr_nm suffix idea a generally useful one?? [070213]
    pitch = rise_nm * bpt ##k #e and make it settable? [not yet used]

    length_left = rise_nm * n_bases_left
    length_right = rise_nm * n_bases_right
    length = length_left + length_right

    end1 = center - direction * length_left
    end2 = center + direction * length_right

    cyl = Cylinder( (end1, end2), color = color_cyl, radius = 1.0, # cyl is a public attr for get
                    doc = "cylindrical surface of double helix"
                    ) ###k
        ###e bring in more from the comments in cyl_OBS below??
        ##e also tell cyl how much it's rotated on its axis, in case it has a texture?? what if that's a helical texture, like dna?

    cyl_OBS = StateArg( Cylinder(color = color_cyl, radius = 1.0), ###IMPLEM this way of giving dflts for attrs added by type coercion
                        #k radius and its units
                        #e put it into model_state
                    ##e make this work: Automatic, #e can this be given as a default to type coercion, to make it "just create one"?
                    Cylinder(color = color_cyl, radius = 1.0)((ORIGIN-6*DX, ORIGIN+10*DX)), ###e silly defaults, change back to ORIGIN end1 soon
                        ###k why did that () not fix this warning: "warning: this expr will get 0 arguments supplied implicitly" ??
                        ###e can we make it ok to pass length and let end1 be default ORIGIN and dx be default DX?
                    doc = "cylindrical surface of double helix"
                   ) ###e add dflt args in case we typecoerce it from a line
        ###e or maybe even bring in a line and make the cyl ourselves with dflt radius? somewhere we should say dflt radius & length.
        # ah, the right place is probably in the type expr: Cylinder(radius = xxx, length = xxx)
        #e do we want to let a directly passed cyl determine color, as the above code implies it would?
        # if not, how do we express that: StateArg(...)(color = color_cyl)??
        # what if color was not passed to self, *then* do we want it fom cyl? same Q for radius.

    path1 = Cylinder_HelicalPath( cyl,
                                  rise = rise_nm,
                                  turn = 1/bpt,
                                  n = n_bases,
                                  theta_offset = - n_bases_left / bpt * 2*pi
                                  )
    ## should be: path2 = Rotate(path1, 150.0, cyl.axis)
        #e note, this seems to be "rotate around a line" (not just a vector), which implies translating so line goes thru origin;
        # or it might be able to be a vector, if we store a relative path... get this straight! ###e (for now assume axis could be either)
    ## here's an easier way, and better anyway (since the path's state (when it has any) should be separate):
    path2 = path1(theta_offset = 150*2*pi/360 - n_bases_left / bpt * 2*pi)

    # optional extender drag handles [070418] --
    # doesn't yet work, apparently *not* due to nested HL issue, but due to coordsys being wrong for it due to outer Draggable
    # (presumed, but output from debug_pref: preDraw_glselect_dict failure consistent...)
    # If that's fixed, it might still fail if big object that includes us is drawn first as a candidate!
    # To fix that, change stencil ref value from 1 to 0 (see glpane.py for how) while drawing nested glnamed obj,
    # when inside another one drawing with stencil on (in draw_in_abs_coords, knowable by drawing_phase == 'selobj').
    handle = Highlightable(Center(Rect(0.3, 2.0, purple)),
                           Center(Rect(0.3, 2.0, white)))
    drag_handles = Overlay( Translate(handle, end1 - direction), Translate(handle, end2))

    # prefs values used in appearance [##e in future, we'll also use these to index a set of display lists, or so]
    show_phosphates = call_Expr( get_dna_pref, 'show phosphates', dflt = False) ###e phosphates -> sugars
    show_lines = call_Expr( get_dna_pref, 'show lines', dflt = False) ##e lines -> bases, or base_lines (since other ways to show bases)

    # appearance (stub -- add handles/actions, more options)
    delegate = Overlay( If( call_Expr( get_dna_pref, 'show central cyl', dflt = False),  cyl ),
                        If( call_Expr( get_dna_pref, 'show drag handles', dflt = True),  drag_handles ), #e has no checkbox yet
                        Cylinder_Ribbon(cyl, path1, color1, showballs = show_phosphates, showlines = show_lines ),
                        Cylinder_Ribbon(cyl, path2, color2, showballs = show_phosphates, showlines = show_lines )
                       )

    # geometric attrs should delegate to the cylinder -- until we can say that directly, do the ones we need individually [070208]
    # (for more comments about a fancier case of this, see attr center comments in draggable.py)
    ## center = cyl.center #e actually the origami center might be the seam, not the geometric center -- worry about that later
        # revision 070213: center is now directly set State (type Point)

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

    def extend(self, left, right):
        "change the length of this duplex on either or both ends, by the specified numbers of new bases on each end respectively"
        ###e need to improve the UI for this -- eg minibuttons to extend by 1.5 turn, or drag end to desired length
        ## self.n_bases_left += left # ... oops, this is not even a state variable!!
        ## self.n_bases_right += right
        self.n_turns_left  += (left / self.bpt) ###BUG: rotates it too -- need to compensate theta_offset
        self.n_turns_right += (right / self.bpt)
        self.KLUGE_gl_update() ###BUG: without this, doesn't do gl_update until selobj changes, or at least until mouse moves, or so

    def _cmd_show_potential_crossovers(self):
        print "_cmd_show_potential_crossovers is NIM"

    # ModelTreeNodeInterface formulae
    mt_node_id = getattr_Expr( _self, '_e_serno') # ipath might be more correct, but this also doesn't change upon reload in practice,
        # i guess since World objects are not remade [070218 late comment] ###REVIEW for possibly being ###WRONG or ###BUG
        # in fact it is surely a bug (tho harmless now); see comments re bugfix070218 and in def mt_node_id
    mt_name = State(str, format_Expr("DNA Cylinder #n (%r)", mt_node_id)) # mt_node_id is only included in name for debugging (does it change?)
        ###e make it unique somehow #e make it editable #e put this state variable into model_state layer
    mt_kids = () #e add our crossovers, our yellow rect demos
    mt_openable = False #e

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
        checkbox_pref( dna_pref('show central cyl'), "show central cyl?", dflt = False),
        checkbox_pref( dna_pref('show phosphates'),   "show base sugars?",   dflt = False), #070213 phosphates -> sugars [###k]
            ###e if indeed those balls show sugars, with phosphates lying between them (and btwn cyls, in a crossover),
            # then I need to revise some other pref keys, varnames, optnames accordingly. [070213]
        checkbox_pref( dna_pref('show lines'),   "show lines?",   dflt = False), # temporary
        ActionButton( world_holder._cmd_Make_DNA_Cylinder, "button: make dna cyl"),
        ActionButton( world_holder._cmd_Make_some_rects, "button: make rects over cyls"),
        ActionButton( world_holder._cmd_Make_red_dot, "button: make red dot"),
        SimpleRow(
            PalletteWell( ## Center(Rect(0.4, 0.4, green))(mt_name = "green rect"),
                              # customization of mt_name has no effect (since no Option decl for mt_name inside) -- need WithAttributes
                          WithAttributes( Center(Rect(0.4, 0.4, green)), mt_name = "green rect #n" ),
                          world = world,
                          type = "green rect"
                              # design flaw: type is needed in spite of WithAttributes mt_name, since that only affects Instances --
                              # and anyway, this is a type name, not an individual name. For replacing this we'd want WithModelType
                              # and I guess we want a combined thing that does both, also filling in the #n with an instance number.
                        ),
            PalletteWell( WithAttributes(
                              Overlay(Center(Spacer(0.6)),
                                      Cylinder((ORIGIN, ORIGIN+DZ*0.01), capped = True, radius = 0.3, color = yellow)),
                              mt_name = "yellow circle #n"
                           ),
                          # first try at that failed, due to no attr bleft on Cylinder (tho the exception is incomprehensible ###FIX):
                          ## Cylinder((ORIGIN, ORIGIN+DZ*0.01), capped = True, radius = 0.3, color = green), # a green dot
                          world = world,
                          type = "yellow circle" ),
            PalletteWell( WithAttributes( Sphere(0.2, blue), mt_name = "blue sphere #n"),
                          world = world,
                          type = "blue sphere" ),
         ),
        If( getattr_Expr( world, '_cmd_Clear_nontrivial'),
            ActionButton( world._cmd_Clear, "button: clear"),
            ActionButton( world._cmd_Clear, "button (disabled): clear", enabled = False)
         ),
        Overlay(
            DisplayListChunk(TextRect( format_Expr( "(%d objects in world)" , number_of_objs ))),
            If( eq_Expr( number_of_objs, 0),
                DrawInCenter(corner = (0,0))( TextRect("(empty model)") ),
                Spacer() ),
         ),
     )
    return expr

object_id = 'needs import or implem' ##### TODO

class World_dna_holder(InstanceMacro): #070201 modified from GraphDrawDemo_FixedToolOnArg1; need to unify them as a ui-provider framework
    # args
    # options
    world = Option(World, World(), doc = "the set of model objects") # revised 070228 for use in _30j
    # internals
##    world = Instance( World() ) # maintains the set of objects in the model
    _value = DisplayListChunk( world)

    _cmd_Make_DNA_Cylinder_tooltip = "make a DNA_Cylinder" ###e or parse it out of method docstring, marked by special syntax??
    def _cmd_Make_DNA_Cylinder(self):
        ###e ideally this would be a command defined on a "dna origami raster", and would show up as a command in a workspace UI
        # only if there was a current raster or a tendency to automake one or to ask which one during or after a make cyl cmd...
        world = self.world
        expr = DNA_Cylinder()
        # Note: ideally, only that much (expr, at this point) would be stored as world's state, with the following wrappers
        # added on more dynamically as part of finding the viewer for the model objects in world. ###e
        # (Nice side effect: then code-reloading of the viewer would not require clearing and remaking the model objs.)
        expr = DisplayListChunk( expr) # displist around cylinder itself -- speeds(unverified) redraw of cyl while it's dragged, or anywhen [070203]
            ###BUG (though this being the cause is only suspected): prefs changes remake the displist only the first time in a series of them,
            # until the next time the object is highlighted or certain other things happen (exact conditions not yet clear); not yet diagnosed;
            # might relate to nested displists, since this is apparently the first time we've used them.
            # This is now in BUGS.txt as "070203 DisplayListChunk update bug: series of prefs checkbox changes (eg show central cyl,
            #  testexpr_30g) fails to remake the displist after the first change", along with suggestions for investigating it. #####TRYTHEM
        expr = DraggableObject( expr)
        ## expr = DisplayListChunk( expr) # displist around drag-repositioned cyl -- prevents drag of this cyl from recompiling world's dlist
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
    def _cmd_Make_red_dot(self):#070212, so we have a fast-running 'make' command for an empty model (#e should add a posn cursor)
        expr = Cylinder((ORIGIN, ORIGIN+DZ*0.01), capped = True, radius = 0.3, color = red) # a red dot [#e implem Circle or Disk]
        expr = DraggableObject(expr)
        self.world.make_and_add(expr, type = "circle")
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

# ==

#070214 stub/experiment on higher-level Origami objects

##e refile into an Origami file, once the World_dna_holder can also be refiled

class OrigamiDomain(DelegatingInstanceOrExpr):
    """An OrigamiDomain is a guide object which organizes a geometrically coherent bunch of DNA guide objects
    (with the kind of geometric organization depending on the specific subclass of OrigamiDomain),
    in a way that facilitates their scaffolding/stapling as part of a DNA Origami design.
       The prototypical kind of OrigamiDomain is an OrigamiGrid. Other kinds will include things like
    polyhedral edge networks, single DNA duplex domains, and perhaps unstructured single strands.
    """
    pass

OrigamiScaffoldedRegion = Stub

class OrigamiGrid(OrigamiDomain):
    """An OrigamiGrid holds several pairs of DNA_Cylinders in a rasterlike pattern (perhaps with ragged edges and holes)
    and provides operations and displays useful for designing raster-style DNA Origami in them.
       An OrigamiGrid is one kind of OrigamiDomain.
       Note that an OrigamiScaffoldedRegion can in general cover all or part of one or more OrigamiDomains,
    even though it often covers exactly one OrigamiGrid.
    """
    def add_cyl_pair(self, cyl_pair, above = None, below = None):
        """Add the given cyl_pair (or perhaps list of cyl_pairs? #e) into self, at the end or at the specified relative position.
        Set both cyls' position appropriately (perhaps unless some option or cyl propert prevents that #e).
        #k Not sure whether we'd reset other properties of the cyls appropriately if they were not yet set...
        or even if they *can be* not yet set.
        #obs cmt after this?:
        #k Not sure if this is the bulk of the op for adding a new cyl created by self, or not -- probably not --
        let's say this does minimal common denominator for "add a cyl", and other ops decide what those cyls should be like.
        But this does have to renumber the existing cyls...
        Q: should we force adding them in pairs, so this op doesn't need to change which kind of cyl (a or b in pairing scheme)
        an existing cyl is? yes.
        """
        assert 0 # nim
    def make_and_add_cyl_pair(self, cyl_options = {}, cyl_class = DNA_Cylinder): #e rename cyl_class -> cyl_expr??
        """Make and add to self a new cyl pair (based on the given class or expr, and customization options),
        at the end of self (or at a specified position within self #e),
        and return the pair.
        """
        #### Q: at what point to cyl exprs get instantiated? and various indices chosen? note we should return Instances not exprs
        ## cyl_expr = cyl_class(**cyl_options)
            ### DESIGN FLAW: cyl_class(**cyl_options) would add args if there were no options given!
            ###e to fix, use an explicit "expr-customize method", e.g.
            # cyl_expr = cyl_class._e_customize(**cyl_options) # works with cyl_class = actual python class, or pure expr --
            # not sure how to implem that (might need a special descriptor to act like either a class or instance method)
            # or as initial kluge, make it require an instance... but that means, only pass an expr into here
        cyl_expr = cyl_options and cyl_class(**cyl_options) or cyl_class
        cyl1_expr = cyl_expr(strand1_theta = 180)
            # change the options for how to align it at the seam: strand 1 at bottom
            ###e Q: should we say pi, or 180?
            # A: guess: 180 -- discuss with others, see what's said in the origami figures/literature, namot2, etc
        cyl2_expr = cyl_expr(strand2_theta = 0) #e ditto: strand 2 at top

        cyl1 = self.make_and_add_to_world(cyl1_expr) ###k guess
            ##e need any options for this call? eg does index or type relate to self?? need to also add a relation, self to it?
            #e and/or is that added implicitly by this call? (only if we rename the call to say "make child obj" or whatever it is)
            #
            # note: cyl1 starts out as a child node of self in MT, a child object for delete, etc,
            # but it *can* be moved out of self and still exist in the model. Thus it really lives in the world
            # (or model -- #e rename method? worry about which config or part?) more fundamentally than in self.
        cyl2 = 'ditto...'

        pair = (cyl1, cyl2) #e does it need its own cyl-pair object wrapper, being a conceptual unit of some sort? guess: yes, someday
        self.add_cyl_pair(self, pair)
            # that sets cyl posns (and corrects existing posns if needed)
            # and (implicitly due to recomputes) modifies summary objects (grid drawing, potential crossover perceptors) as needed
        return pair
    pass # end of class OrigamiGrid

# end
