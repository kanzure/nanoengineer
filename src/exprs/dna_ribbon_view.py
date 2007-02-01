"""
dna_ribbon_view.py

$Id$

At the moment [070125], this is a scratch file mostly identical to demo_dna-outtakes.py,
whose code should be cannibalized for what this will have (and then cvs-removed --
maybe that could happen right away #e).

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
"""

# == the new stuff is at the bottom

"""
      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),
"""



from basic import *
from basic import _self

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import TextRect
reload_once(TextRect)
from TextRect import TextRect

from OpenGL.GL import * #e move what needs this into draw_utils
import drawer

#e clean up these local abbreviations
IorE = InstanceOrExpr
Macro = DelegatingInstanceOrExpr

# stubs:
Radians = Width
Rotations = Degrees = Width
Angstroms = Width

ModelObject3D = Geom3D = Widget # how would ModelObject3D & Geom3D differ?
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
    radius = ArgOrOption( Width, 1.0)
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
    turn = Option( Rotations, 1.0 / 10.5) # number of rotations of vector around axis, in every path segment
    rise = Option( Width, 0.34) ###k default
    theta_offset = Option( Radians, 0.0) # rotates entire path around cyl.axis
    color = Option(Color, black) # only needed for drawing it -- not part of Geom3D -- add a super to indicate another interface??##e
        ##e dflt should be cyl.attr for some attr related to lines on this cyl -- same with other line-drawing attrs for it
    ## start_offset = Arg( Width)
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

Corkscrew = Stub
class Ribbon_oldcode_for_edges(Corkscrew): # generates a sequence of rects (quads) from two corkscrews, then draws a ribbon using them
    def draw(self, **mods):
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self, color = interior_color)
            if 0:
                glTranslate(offset, 0,0)            
                Corkscrew.draw(self, color = interior_color) ### maybe we should make the two edges look different, since they are (major vs minor groove)
                glTranslate(-offset, 0,0)


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
    axialwidth = ArgOrOption(Width, 1.0) #e rename; distance across ribbon along cylinder axis (actual width is presumably shorter since it's diagonal)
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
        color = self.color
        interior_color = ave_colors(0.8, color, white) ### remove sometime?

        self.draw_quad_strip( interior_color, offsets, points, normals)
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

##class Ribbon2(Ribbon): # draws, using the same params needed for a corkscrew, a pair of ribbons that look like a DNA double helix
##    # radius, axis, turn, n
##    pass

class Rotate(IorE):#e refile with Translate -- in fact, reexpress it as interposing on draw and lbox methods, ignoring the rest...
        # (as discussed extensively elsewhere, not sure if in code or notesfile or paper, 1-3 days before 070131)
    # needs to transform other things too, like lbox -- same issue as Translate
    thing = Arg(Widget)
    angle = Arg(float)
    axis = ArgOrOption(Vector, DZ) ###e or LineSegment, then do translate too
    ###e should normalize axis and check for 0,0,0
    def draw(self):
        glRotatef(angle, axis[0], axis[1], axis[2]) # angle is in degrees, I guess
        thing.draw(self)
        glRotatef(-angle, axis[0], axis[1], axis[2]) # might be optional, I forget the semantics of things like Overlay ###k
    pass

call_lambda_Expr = Stub
lambda_Expr = Stub
ShareInstances = Stub

class Ribbon2_try1(Macro): ###e perhaps needs some axis -> axisvector
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
    angle = 150.0
    arg1 = ArgExpr(Widget) # but it better have .axis if we use it to make arg2! BUT if it's an expr, how can it have that yet?
        #### are some attrs of exprs legal if they don't require instanceness to be computed, depending on the type?
        #### (typical for geometric stuff) or only if this kind of expr is "born an instance"? But if it's highlightable, it's not...
    # but it might have an axis anyway... but do we really mean arg2's axis? no... maybe a special instance of arg1 used in this expr alone? yes.
    _arg1_for_arg2 = Instance(arg1) # only used if arg2's dflt expr is needed; has to be an instance so we can ask for its .axis
        #e maybe this requirement can be relaxed since.axis does not depend on self?? not sure -- anyway it might... since it
        # might depend on local coords -- no, it's defined to be rel to local coords, so it doesn't.... ###k
    arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, _arg1_for_arg2.axis)) # in old code we passed a single Ribbon, used it twice
    delegate = Overlay(arg1(color = red), arg2(color = blue)) ###PROBLEM: too late to customize arg2 if it's an Instance!
        ## (unless this sets some state and is thereby possible on an instance... seems fishy even so.)
        # is the real intent of _arg1_for_arg2 to be an instance? what if arg2, using it, was made multiple times?
        # so no, that's the bug -- _arg1_for_arg2 is an expr which when made in those two places in arg2 dflt should be shared --
        # but it's not already an instance. It's like an ArgExpr with all ipath components added locally in this class already fixed
        # rather than coming from whatever gets built up -- as if we wrapped it when it came in and we did this,
        # then were able to strip off whatever ipath it got -- or equivly, we wrap it with "ignore outer ipath, just use this one".
        # As if I said _arg1_for_arg2 = ShareInstances(arg1) -- it gets an ipath but then ignores furtherly added ones. Hmm...
        # probably easy to implem if I decide it's right!
        #
        # [then I did Ribbon2_try2, then I extended this to say:]
        ### BUT IT'S WRONG, since if we use arg2 (expr) in several places here, how do we let each of *them* use different instances
        # of _arg1_for_arg2? We'd somehow have to say in arg2 dflt that we use the same instance of _arg1_for_arg2 for each inst of it --
        # but only for that, not for other instances of it. As if it had a quantifier for "what inst of arg1 to use in here".
        # As our lambda_Expr would make possible... ###DIGR can we let a call_Expr imply a lambda_Expr if arg1 is a lambda??
    if 'do this instead':
        dflt_arg2 = call_lambda_Expr( lambda myarg1: Rotate( myarg1, angle, myarg1.axis), arg1 )
        # or maybe a lambda_Expr is callable and doing so makes a call expr -- as opposed to being customizable (until called):
        dflt_arg2 = 0 and lambda_Expr( lambda arg1: Rotate( arg1, angle, arg1.axis))( arg1 ) # lambda is really called on an Instance
            # without '0 and', due to Stub bug, we get AssertionError: not permitted to re-supply already supplied positional args, in <Widget2D#17093(a)>

        arg2 = ArgExpr(Widget, dflt_arg2)
        _customized_arg2 = arg2(color=blue) ### PROBLEM: it might *still* be too late to customize,
        # since color=whatever won't burrow into things like localipathmod, let alone Rotate! #########
        # this current expr could only work if customizations on certain exprs would get passed into the interior
        # to be used by, or before, instantiations called for inside them. Hmm, same issue for If_expr(cond, expr1, expr2)(color=blue)
        # assuming expr[12] accept color customization. ####### if these custs became an OpExpr, eval could eval its arg1... might work.
        #
        # later, 070127: passthru customization seems unclear & hard but wanted:
        # maybe the feeling that customization ought to burrow into Rotate or localipathmod is related to them delegating to an arg --
        # since attr accesses delegate, so should attr definitions (but only for the attrs that actually delegate). That does make sense.
        # It's not easy to implement -- we have no list of attrs that don't delegate, we just try getattr and see if we get into __getattr__.
        # So to customize an attr -- wait, would it work to customize it at the outer level? No, because the draw call occurs inside.
        # It's as if we wanted to constrain X and Rotate(X) to have the same def and value of attr (if it delegates), e.g. color.
        # But the fact that X.draw uses X.color is not even dependent on whether Rotate delegates color! Ignoring that last point,
        # can customize mean "find the internal users of the def of color, and make them use this different def"? These internal users
        # are kid instances. They are self-contained in ability to use color. So parent would have to modify them -- presumably when it makes them.
        # So parent(color = cust) would have to instantiate, not its normal kid delegate, but kid(color = cust), I guess. I don't see an
        # easy implem, and I'm also suspicious it's the right idea.
        
        # So maybe the only soln is to do the color cust first, as the docstring had to say to describe the intent, anyway.
    pass

class Ribbon2_try2(Macro):###e perhaps needs some axis -> axisvector
    ###IMPLEM ShareInstances  - or not, if that lambda_Expr in _try1 makes it unneeded... it might be wrong anyway
    # if it provides no way to limit the sharing within the class that says to do it, or if doing that is too cumbersome or unclear.
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
    angle = 150.0
    arg1 = ArgExpr(Widget)
    _drawn_arg1 = Instance(arg1(color=red)) ###e digr: could I have said Instance(arg1, color=red)? I bet people will try that...
    _arg1_for_arg2 = ShareInstances(arg1(color=blue)) # still an expr; in fact, this ASSUMES arg1 is passed in as an expr, not as an instance! Hmm#####
    ## arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, _arg1_for_arg2.axis))
    arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, getattr_Expr( _arg1_for_arg2, 'axis') ))
    _drawn_arg2 = Instance(arg2(color=blue)) ####KLUGE: add color here in case arg2 was supplied, but in dflt expr in case we used that
    delegate = Overlay(_drawn_arg1, _drawn_arg2)

class Ribbon2_try3(Macro): #070129 ###e perhaps needs some axis -> axisvector
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue, assuming they are color-customizable.
    If thing2 is not supplied, a rotated thing1 instance (different drawable instance, same model object instance)
    is used for it (also drawn in blue).
    """
    angle = 150.0
    arg1 = Arg(ModelObject3D) ###k type implies that it has 3d shape etc, determines how much gets instantiated here (axis, not color??)
    arg2 = Arg(ModelObject3D, Rotate(arg1, angle, arg1.axis) ) # doesn't yet work... see below
        # Rotate works on a ModelObject3D instance which is like a Drawable expr
        # note: Rotate's default axis is the Z axis, not arg1.axis even if that exists
    delegate = Overlay(arg1(color = red), arg2(color = blue)) # doesn't yet work... see below
        # For all this to work requires two proposed semantic changes:
        # - Rotate delegation more like customization -- instance of Rotate produces no separate instance of its delegate
        # - partial instantiation by Arg, only of attrs that are part of its declared type (mentioned above)
        # (these changes make it likely that the 'delegate' attr will be renamed, too)
    pass


# very old cmt:
# Ribbon2 has: radius, axis (some sort of length - of one bp?), turn (angle??), n, color1, color2, and full position/orientation
# and it will have display modes, incl cyl with helix/base/groove texture, and flexible coloring;
# and ability to show the units in it, namely strands, or basepairs, or bases (selected/opd by type)
# and for us to add cmd bindings like "make neighbor strand" (if room) or "make crossover here" (maybe only on a base?)

# but as a first step, we can select it as a unit, copy/paste, deposit, move, etc.
# In this, it is sort of like an atom or set of co-selected atoms... some relation to chunk or jig too.
# I'd get best results by letting it be its own thing... but fastest, by borrowing one of those...

# ==

###e need to look up the proper parameter names -- meanwhile use fake ones that don't overlap the real ones --
# easy, just use the geometric ones in Cylinder_HelicalPath. Later we'll have our own terminology & defaults for those here.
## pitch # rise per turn
## rise

class DNA_Cylinder(Macro):##k super
    color = Option(Color, gray) #e transparent/hidden
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
    rise = StateOption(Angstroms, 3.4, doc = "distance along helix axis from one basepair to the next") #k can you say units that way?
    bpt = StateOption(Float, 10.5, doc = "bases per turn")
    pitch = rise * bpt ##k #e and make it settable?
    path1 = Cylinder_HelicalPath( cyl, rise = rise / 10.0, turn = 1/bpt, ###KLUGE /10.0 due to length units being messed up
                                  n = cyl.length / rise * 10.0 ###KLUGE * 10.0
                                  ) #e need theta_offset?
    ## should be: path2 = Rotate(path1, 150.0, cyl.axis)
        #e note, this seems to be "rotate around a line" (not just a vector), which implies translating so line goes thru origin;
        # or it might be able to be a vector, if we store a relative path... get this straight! ###e (for now assume axis could be either)
    ## here's an easier way, and better anyway (since the path's state (when it has any) should be separate):
    path2 = path1(theta_offset = 150*2*pi/360) 
    # appearance (stub -- add handles/actions, remove cyl)
    delegate = Overlay( cyl, # works
                        Cylinder_Ribbon(cyl, path1, color1),
                        Cylinder_Ribbon(cyl, path2, color2)
                       )
    pass

class obs:
    path = StateArg(Cylinder_HelicalPath)
    path.someattr = Option(Something, 'dflt') # set path.someattr to Option(...) -- ExprsMeta scanner would need to see this --
        # but what attrname would it use in the Option?? maybe the _try1 version is better since it says the name,
        # or maybe you can give it in Option as string arg1.
    
class todo:
    # might need other state, like some colors

    # and links to things made from this guide shape -- or a superclass or whatever that says we are a guide shape
    # (and all of them can have links like that)

    # and ops to make attached things like crossovers, to give posns for potential ones
    # and display styles for self and those things...
    # for now just have default drawing code, using the Ribbon classes above.
    pass

import Command_scratch_1
reload_once(Command_scratch_1)

# end
