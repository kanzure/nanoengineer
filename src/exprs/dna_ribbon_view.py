"""
dna_ribbon_view.py

$Id$

At the moment, this is a scratch file mostly identical to demo_dna-outtakes.py,
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
"""

# == the new stuff is at the bottom

"""
      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),
"""

debug_color_override = 0

IorE = InstanceOrExpr
Macro = DelegatingInstanceOrExpr

class Corkscrew(WidgetExpr):# generates a single helix line-sequence? from geom control params (computable from its goals)
    "Corkscrew(radius, axis, turn, n, color) - axis is length in DX, turn might be 1/10.5" 
    def init(self):
        radius, axis, turn, n, color = self.args #k checks length
    def draw(self, **mods):
        radius, axis, turn, n, color = self.args
            # axis is for x, theta starts 0, at top (y), so y = cos(theta), z = sin(theta)
        color = mods.get('color',color)##kluge; see comments in Ribbon.draw
        glDisable(GL_LIGHTING) ### not doing this makes it take the color from the prior object 
        glColor3fv(color)
        glBegin(GL_LINE_STRIP)
        points = self.points()
        for p in points:
            ##glNormal3fv(-DX) #####WRONG? with lighting: doesn't help, anyway. probably we have to draw ribbon edges as tiny rects.
            # without lighting, probably has no effect.
            glVertex3fv(p)
        glEnd()
        glEnable(GL_LIGHTING)
    def points(self, theta_offset = 0.0):
        radius, axis, turn, n, color = self.args
        res = []
        for i in range(n+1):
            theta = 2*pi*turn*i + theta_offset
            y = cos(theta) * radius; z = sin(theta) * radius
            x = i * axis
            res.append(V(x,y,z)) #e or could do this in list extension notation
        return res
    def _get_bright(self):
        radius, axis, turn, n, color = self.args
        return n * axis
    def _get_btop(self):
        radius, axis, turn, n, color = self.args
        return radius
    _get_bbottom = _get_btop
    pass


class Ribbon(Corkscrew): # generates a sequence of rects (quads) from two corkscrews, then draws a ribbon using them
    def draw(self, **mods):
        radius, axis, turn, n, color = self.args
        color0 = mods.get('color',color)##kluge
            ##e todo: should be more general; maybe should get "state ref" (to show & edit) as arg, too?
        if color != color0:
            if debug_color_override:
                print "color override in %r from %r to %r" % (self, color, color0) # seems to happen to much and then get stuck... ###@@@
        else:
            if debug_color_override:
                print "no color override in %r for %r" % (self, color) 
        color = color0
        offset = axis * 2
        halfoffset = offset / 2.0
        interior_color = ave_colors(0.8,color, white) ###
        self.args = list(self.args) # slow!
        # the next line (.args[-1]) is zapped since it causes the color2-used-for-ribbon1 bug;
        # but it was needed for the edge colors to be correct.
        # Try to fix that: add color = interior_color to Corkscrew.draw. [060729 233p g4]
        #self.args[-1] = interior_color #### kluge! and/or misnamed, since used for both sides i think #####@@@@@ LIKELY CAUSE OF BUG
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self, color = interior_color)
            if 0:
                glTranslate(offset, 0,0)            
                Corkscrew.draw(self, color = interior_color) ### maybe we should make the two edges look different, since they are (major vs minor groove)
                glTranslate(-offset, 0,0)
        
        ## glColor3fv(interior_color)

        # actually I want a different color on the back, can I get that? ###k
        glDisable(GL_CULL_FACE)
        drawer.apply_material(interior_color)
        ## glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color) # gl args partly guessed #e should add specularity, shininess...
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_TRUE)

        points = self.points()
        otherpoints = self.points(theta_offset = 150/360.0 * 2*pi)
        glBegin(GL_QUAD_STRIP) # this uses CULL_FACE so it only colors the back ones... but why gray not pink?
            # the answer - see draw_vane() -- I have to do a lot of stuff to get this right:
            # - set some gl state, use apply_material, get CCW ordering right, and calculate normals.
##        glColor3fv(interior_color)
        colorkluge = 0####@@@@ (works, except white edge is opposite as i'd expect, and doesn't happen for 1 of my 4 ribbons)
        if colorkluge:
            col1 = interior_color
            col2 = white
        for p in points:
            perpvec = norm(V(0, p[1], p[2])) # norm here means divide by radius, that might be faster
            ## perpvec = V(0,0,1) # this makes front & back different solid lightness, BUT the values depend on the glRotate we did
            glNormal3fv( perpvec)
            if colorkluge:
                drawer.apply_material(col1)
                col1, col2 = col2, col1
            glVertex3fv(p + offset * DX)
            if colorkluge and 1:
                drawer.apply_material(col1)
                col1, col2 = col2, col1
            glVertex3fv(p)
        glEnd()
        glEnable(GL_CULL_FACE)
        glLightModelfv(GL_LIGHT_MODEL_TWO_SIDE, GL_FALSE)
        if 0:
            # ladder rungs - warning, they are buggy -- when they poke out, there are two in each place, but there should not be
            glDisable(GL_LIGHTING)
            glColor3fv(gray)
            glTranslate(halfoffset,0,0) # center the end within the ribbon width
            glBegin(GL_LINES)
            for p,op in zip(points,otherpoints):
                # bugs: they poke through; they look distracting (white worse than gray);
                # end1 (blue?) is not centered (fixed);
                # end2 is not clearly correct;
                # would look better in closeup if ends were inside rects (not on kinks like now), but never mind,
                # whole thing will be replaced with something better
                mid = (p + op)/2.0
                pv = p - mid
                opv = op - mid
                radfactor = 1.1 # make them poke out on purpose
                pv *= radfactor
                opv *= radfactor
                p = mid + pv
                op = mid + opv
                glVertex3fv(p)
                glVertex3fv(op)
            glEnd()
            glTranslate(-halfoffset,0,0)
            glEnable(GL_LIGHTING)
        return
    pass

class Ribbon2(Ribbon): # draws the same params needed for a corkcrew as a pair of ribbons that look like a DNA double helix
    def draw(self):
        radius, axis, turn, n, color1 = self.args
        color2 = self.kws.get('color2')
        angle = 150.0
        ## angle = angle/360.0 * 2*pi
        Ribbon.draw(self, color = color1)
        glRotatef(angle, 1,0,0) # accepts degrees, I guess
        Ribbon.draw(self, color = color2)
        glRotatef(-angle, 1,0,0)
    pass

Something = Anything # when we don't yet know but plan to replace it with something specific

class Rotate(IorE):#e refile with Translate
    # needs to transform other things too, like lbox -- same issue as Translate
    thing = Arg(Widget)
    angle = Arg(float)
    axis = ArgOrOption(Vector, DZ)
    ###e should normalize axis and check for 0,0,0
    def draw(self):
        glRotatef(angle, axis[0], axis[1], axis[2]) # angle is in degrees, I guess
        thing.draw(self)
        glRotatef(-angle, axis[0], axis[1], axis[2]) # might be optional, I forget the semantics of things like Overlay ###k
    pass

class Ribbon2_try1(Macro):
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
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
        dflt_arg2 = call_lambda_Expr( lambda myarg1: Rotate( myarg1, angle, myarg1.axis), arg1 )
        # or maybe a lambda_Expr is callable and doing so makes a call expr -- as opposed to being customizable (until called):
        dflt_arg2 = lambda_Expr( lambda arg1: Rotate( arg1, angle, arg1.axis))( arg1 ) # lambda is really called on an Instance
        
        arg2 = ArgExpr(Widget, dflt_arg2)
        _customized_arg2 = arg2(color=blue) ### PROBLEM: it might *still* be too late to customize,
        # since color=whatever won't burrow into things like localipathmod, let alone Rotate! #########
        # this current expr could only work if customizations on certain exprs would get passed into the interior
        # to be used by, or before, instantiations called for inside them. Hmm, same issue for If_expr(cond, expr1, expr2)(color=blue)
        # assuming expr[12] accept color customization. ####### if these custs became an OpExpr, eval could eval its arg1... might work
        
        # So maybe the only soln is to do the color cust first, as the docstring had to say to describe the intent, anyway.
    pass

class Ribbon2_try2(Macro):
    ###IMPLEM ShareInstances  - or not, if that lambda_Expr in _try1 makes it unneeded... it might be wrong anyway
    # if it provides no way to limit the sharing within the class that says to do it, or if doing that is too cumbersome or unclear.
    """Ribbon2(thing1, thing2) draws a thing1 instance in red and a thing2 instance in blue.
    If thing2 is not supplied, a rotated thing1 instance is used for it, and also drawn in blue.
    """
    arg1 = ArgExpr(Widget)
    _drawn_arg1 = Instance(arg1(color=red)) ###e digr: could I have said Instance(arg1, color=red)? I bet people will try that...
    _arg1_for_arg2 = ShareInstances(arg1(color=blue)) # still an expr; in fact, this ASSUMES arg1 is passed in as an expr, not as an instance! Hmm#####
    arg2 = ArgExpr(Widget, Rotate( _arg1_for_arg2, angle, _arg1_for_arg2.axis))
    _drawn_arg2 = Instance(arg2(color=blue)) ####KLUGE: add color here in case arg2 was supplied, but in dflt expr in case we used that
    delegate = Overlay(_drawn_arg1, _drawn_arg2)

# very old cmt:
# Ribbon2 has: radius, axis (some sort of length - of one bp?), turn (angle??), n, color1, color2, and full position/orientation
# and it will have display modes, incl cyl with helix/base/groove texture, and flexible coloring;
# and ability to show the units in it, namely strands, or basepairs, or bases (selected/opd by type)
# and for us to add cmd bindings like "make neighbor strand" (if room) or "make crossover here" (maybe only on a base?)

# but as a first step, we can select it as a unit, copy/paste, deposit, move, etc.
# In this, it is sort of like an atom or set of co-selected atoms... some relation to chunk or jig too.
# I'd get best results by letting it be its own thing... but fastest, by borrowing one of those...
