# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
projection.py - utilities loosely related to setting up the projection matrix

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

"""

from OpenGL.GL import glScalef
from OpenGL.GL import GL_MODELVIEW
from OpenGL.GL import glMatrixMode
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glLoadIdentity
from OpenGL.GL import GL_PROJECTION
from OpenGL.GL import GL_VIEWPORT
from OpenGL.GL import glGetIntegerv
from OpenGL.GL import glOrtho
from OpenGL.GL import glTranslatef
from OpenGL.GL import glPopMatrix
from OpenGL.GLU import gluPickMatrix, gluUnProject

try:
    from OpenGL.GL import glScale
except:
    # The installed version of OpenGL requires argument-typed glScale calls.
    glScale = glScalef

from utilities.prefs_constants import UPPER_RIGHT, UPPER_LEFT, LOWER_LEFT, LOWER_RIGHT # note: also in basic.py as of 070302

from exprs.attr_decl_macros import Arg, ArgOrOption, Option
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.widget2d import Widget2D
from exprs.ExprsConstants import PIXELS

class DrawInCorner_projection(DelegatingInstanceOrExpr):
    """
    [DEPRECATED for general use -- use DrawInCorner instead.]
    
    This is a variant of DrawInCorner which works by changing the projection matrix,
    and which has several bugs/niys. It only works for the default corner argument,
    and any Highlightables in its main argument (delegate) only work properly for
    highlighting if they are given the option projection = True (which is not the
    default, for efficiency reasons [this may change on 081202]).

    Its usefulness is that it's the only expr (as of 070405) which changes the
    projection matrix for the subexprs it draws, so it's the only good test of
    Highlightable(projection = True).
    """
    # Note: renamed from DrawInCorner_NOTWORKING_VERSION to DrawInCorner_projection on 070405,
    # since tests show that Highlightable(projection=True) has been working inside it for awhile.
    #
    # But to make it the usual implem of DrawInCorner would require:
    # - a good reason (like pixel alignment bugs after trackballing, in the other implem -- not yet annoying enough);
    # - args fixed up to match that one;
    # - implem the other corners -- only the default one works now, I think;
    # - make it unnecessary to say projection = True to embedded Highlightables,
    #   using either a GLPane flag (with special provisions for display lists,
    #   which might need two variants depending on that flag),
    #   or a change of default value of that option,
    #   or a change of algorithm in Highlightable.
    
    delegate = Arg(Widget2D)
    corner = Arg(int, LOWER_RIGHT)
    def draw(self):
        # this code is modified from drawcompass

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glMatrixMode(GL_PROJECTION) # WARNING: we're now in nonstandard matrixmode (for sake of gluPickMatrix and glOrtho -- needed??##k)
        glPushMatrix()
        glLoadIdentity()

        try:
            glpane = self.env.glpane
            aspect = glpane.aspect # revised by bruce 070919, UNTESTED
            corner = self.corner
            delegate = self.delegate

            ###e should get glpane to do this for us (ie call a method in it to do this if necessary)
            # (this code is copied from it)
            glselect = glpane.current_glselect
            if glselect:
                # print "%r (ipath %r) setting up gluPickMatrix" % (self, self.ipath)
                x,y,w,h = glselect
                gluPickMatrix(
                        x,y,
                        w,h,
                        glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
                )

            # the first three cases here are still ###WRONG
            if corner == UPPER_RIGHT:
                glOrtho(-50 * aspect, 5.5 * aspect, -50, 5.5,  -5, 500) # Upper Right
            elif corner == UPPER_LEFT:
                glOrtho(-5 * aspect, 50.5 * aspect, -50, 5.5,  -5, 500) # Upper Left
            elif corner == LOWER_LEFT:
                glOrtho(-5 * aspect, 50.5 * aspect, -5, 50.5,  -5, 500) # Lower Left
            else:
                ## glOrtho(-50 * aspect, 5.5 * aspect, -5, 50.5,  -5, 500) # Lower Right
                ## glOrtho(-50 * aspect, 0, 0, 50,  -5, 500) # Lower Right [used now] -- x from -50 * aspect to 0, y (bot to top) from 0 to 50
                glOrtho(-glpane.width * PIXELS, 0, 0, glpane.height * PIXELS,  -5, 500)
                    # approximately right for the checkbox, but I ought to count pixels to be sure (note, PIXELS is a pretty inexact number)

            glMatrixMode(GL_MODELVIEW) ###k guess 061210 at possible bugfix (and obviously needed in general) --
                # do this last to leave the matrixmode standard
                # (status of bugs & fixes unclear -- hard to test since even Highlightable(projection=True) w/o any change to
                # projection matrix (test _9cx) doesn't work!)
            offset = (-delegate.bright, delegate.bbottom) # only correct for LOWER_RIGHT
            glTranslatef(offset[0], offset[1], 0)
            self.drawkid( delegate) ## delegate.draw()
            
        finally:
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW) # be sure to do this last, to leave the matrixmode standard
            glPopMatrix()

        return
    pass # end of class DrawInCorner_projection

# ==

# Since the above does not yet work with highlighting, try it in a completely different way for now, not using projection matrix,
# since we need the feature. Works!

corner_abbrevs = {   #070208
    LOWER_RIGHT: (+1, -1), # (x,y) where for x, -1 is left, and for y, -1 is lower
    UPPER_RIGHT: (+1, +1),
    LOWER_LEFT:  (-1, -1),
    UPPER_LEFT:  (-1, +1),
}

_DEBUG_SAVED_STUFF = False

class DrawInCorner(DelegatingInstanceOrExpr):
    """
    DrawInCorner( thing, (-1,-1)) draws thing in the lower left corner of the screen
    (positioning thing so that its layout box's lower left corner nests directly into that corner of the screen).
    The depth can be specified by the option want_depth (between 0.0 and 1.0), which by default is 0.01 (very near the front).
    [###UNTESTED: it may be that non-default depths have never been tested.]

    The "corner" can be any corner, or any edge, or the center of the screen;
    it can be specified as a 2nd argument (x,y), or by the option corner = (x,y),
    where x can be -1, 0, or 1 (for left, center, or right respectively)
    and y can be -1, 0, or 1 (for bottom, center, or top).

    For the corners, the abbreviations defined in prefs_constants (small ints called UPPER_RIGHT, UPPER_LEFT,
    LOWER_LEFT, LOWER_RIGHT) are also permitted (and for convenience can also be imported from this class's source file).

    When thing does not need to touch a screen boundary (in one or both dimensions),
    it is not shifted at all, meaning its local origin is aligned with the specified position in that dimension.
    For drawing in an edge or the center, consider wrapping thing in Center or the like to modify this.
    (Without this feature, DrawInCorner( thing, (0,0)) would be equivalent to DrawInCorner( Center(thing), (0,0)).)

    ###BUG: The current implem (as of 070210) probably doesn't work properly after coordinate changes inside display lists.
    """
    ##e should we reverse the arg order? [recent suggestion as of 070302]
    delegate = Arg(Widget2D)
    corner = ArgOrOption(int, LOWER_RIGHT,
                         doc = "the corner/edge/center to draw in, as named int or 2-tuple; see class docstring for details")
        # note: semi-misnamed option, since it can also be an edge or the center
        ###KLUGE: type spec of 'int' is wrong -- we also allow it to be a pair of ints for x,y "symbolic posn" respectively
    want_depth = Option(float, 0.01) # this choice is nearer than cov_depth (I think!) but doesn't preclude 3D effects (I hope).
    def draw(self):
        if self.delegate is None:
            # 070210 -- but I'm not sure if this is a complete ###KLUGE, or good but ought to be done more generally,
            # or if it would be better to do it totally differently by instantiating None into something like Spacer(). ##k
            return
        
        glMatrixMode(GL_MODELVIEW) # not needed
        glPushMatrix()
        glLoadIdentity()
        try:
            glpane = self.env.glpane
            aspect = glpane.aspect # revised by bruce 070919
            corner = self.corner
            delegate = self.delegate
            want_depth = self.want_depth
                # note about cov_depth:
                ## self.near = 0.25
                ## self.far = 12.0
                # so I predict cov_depth is 0.75 / 11.75 == 0.063829787234042548
                # but let's print it from a place that computes it, and see.
                # ... hmm, only place under that name is in selectMode.py, and that prints 0.765957458814 -- I bet it's something
                # different, but not sure. ###k (doesn't matter for now)

            # modified from _setup_modelview:

            saveplace = self.transient_state # see if this fixes the bug 061211 1117a mentioned below -- it does, use it.
                # BUG (probably not related to this code, but not known for sure):
                # mousewheel zoom makes checkboxes inside DrawInCorner
                # either not highlight, or if they are close enough to
                # the center of the screen (I guess), highlight in the
                # wrong size and place. For more info and a partial theory,
                # see the 081202 update in DisplayListChunk.py docstring.
                # Before I realized the connection to DisplayListChunk,
                # I tried using saveplace = self.per_frame_state instead of
                # self.transient_state above, but that had no effect on the bug.
                # That was before I fixed some bugs in same_vals related to
                # numpy.ndarray, when I was plagued with mysterious behavior
                # from those in my debug code (since solved), but I tried it
                # again afterwards and it still doesn't fix this bug, which
                # makes sense if my partial theory about it is true.
                #
                # In principle (unrelated to this bug), I'm dubious we're
                # storing this state in the right place, but I won't change
                # it for now (see related older comments below).
                #
                # Note: I fixed the bug in another way, by changing
                # Highlightable's projection option to default True.
                # [bruce 081202]
            
            if glpane.current_glselect or (0 and 'KLUGE' and hasattr(saveplace, '_saved_stuff')):
                            # kluge did make it faster; still slow, and confounded by the highlighting-delay bug;
                            # now I fixed that bug, and now it seems only normally slow for this module -- ok for now.
                
                # when that cond is false, we have a nonstandard projection matrix
                # (see also the related comments in save_coords_if_safe in Highlightable.py)
                # [bruce 081204 comment]

                x1, y1, z1 = saveplace._saved_stuff # this is needed to make highlighting work!
                ###BUG [061211 1117a; fixed now, see above, using saveplace = self.transient_state]:
                # if we click on an object in testexpr_15d (with DrawInCorner used for other objs in the testbed)
                # before it has a chance to show its highlighted form, at least after a recent reload, we get an attrerror here.
                # Easy to repeat in the test conditions mentioned (on g5). Not sure how it can affect a different obj (self)
                # than the one clicked on too quickly. Best fix would be to let glpane give us the requested info,
                # which is usually the same for all callers anyway, and the same across reloads (just not across resizes).
                # But it does depend on want_depth, and (via gluUnProject) on the current modelview coords
                # (and projection coords if we ever changed them). So it's not completely clear how to combine ease, efficiency,
                # and safety, for that optim in general, even w/o needing this bugfix.
                #    But the bug is easy to hit, so needs a soon fix... maybe memoize it with a key corresponding to your own
                # assumed choice of modelview coords and want_depth? Or maybe enough to put it into the transient_state? TRY THAT. works.
                if _DEBUG_SAVED_STUFF:
                    print "_DEBUG_SAVED_STUFF: retrieved", x1, y1, z1
            else:
                x1, y1, z1 = saveplace._saved_stuff = \
                             gluUnProject(glpane.width, glpane.height, want_depth)
                                # max x and y, i.e. right top
                # (note, to get the min x and y we'd want to pass (0, 0, want_depth),
                #  since these are windows coords -- (0, 0) is bottom left corner (not center))
                #
                # Note: Using gluUnProject is probably better than knowing and reversing _setup_projection,
                # since it doesn't depend on knowing the setup code, except meaning of glpane height & width attrs,
                # and knowing that origin is centered between them and 0.
                if _DEBUG_SAVED_STUFF:
                    print "_DEBUG_SAVED_STUFF: saved", x1, y1, z1
##            print x1,y1,z1
            # use glScale to compensate for zoom * scale in _setup_projection,
            # for error in PIXELS, and for want_depth != cov_depth
            x1wish = glpane.width / 2.0 * PIXELS # / 2.0 because in these coords, screen center indeed has x == y == 0
            r = x1 / x1wish
            glScale(r, r, r) 
##            x1 /= r
##            y1 /= r
            z1 /= r
            # now the following might work except for z, so fix z here
            glTranslatef( 0.0, 0.0, z1)
            del x1, y1 # not presently used
            if _DEBUG_SAVED_STUFF:
                print "_DEBUG_SAVED_STUFF:     r = %r, translated z by z1 == %r" % (r, z1)
            
            # I don't think we need to usage-track glpane height & width (or scale or zoomFactor etc)
            # since we'll redraw when those change, and redo this calc every time we draw.
            # The only exception would be if we're rendering into a display list.
            # I don't know if this code (gluUnProject) would even work in that case.
            # [I think I wrote a similar comment in some other file earlier today. #k]
            
            # move to desired corner, and align it with same corner of lbox
            # (#e could use an alignment prim for the corner if we had one)

            if corner in corner_abbrevs:
                # normalize how corner is expressed, into a 2-tuple of +-1's
                corner = corner_abbrevs[corner]

            x, y = corner

            if x == -1: # left
                x_offset = - glpane.width / 2.0 * PIXELS + delegate.bleft
            elif x == +1: # right
                x_offset = + glpane.width / 2.0 * PIXELS - delegate.bright
            elif x == 0: # center(x)
                x_offset = 0
                    # note: before 070210 this was (+ delegate.bleft - delegate.bright) / 2.0,
                    # which has an unwanted (since unavoidable) centering effect; use explicit Center if desired.
            else:
                print "invalid corner",corner###
                raise ValueError, "invalid corner %r" % (corner,)
                
            if y == -1: # bottom
                y_offset = - glpane.height / 2.0 * PIXELS + delegate.bbottom
            elif y == +1: # top
                y_offset = + glpane.height / 2.0 * PIXELS - delegate.btop
            elif y == 0: # center(y)
                y_offset = 0
                    # note: # note: before 070210 this was (+ delegate.bbottom - delegate.btop) / 2.0
            else:
                print "invalid corner",corner###
                raise ValueError, "invalid corner %r" % (corner,)

            offset = (x_offset, y_offset)
            glTranslatef(offset[0], offset[1], 0.0)

            if _DEBUG_SAVED_STUFF:
                print "_DEBUG_SAVED_STUFF:     offset =", offset
            
            self.drawkid( delegate) ## delegate.draw()
            
        finally:
            glMatrixMode(GL_MODELVIEW) # not needed
            glPopMatrix()

        return
    pass # end of class DrawInCorner

DrawInCenter = DrawInCorner(corner = (0,0), doc = "#doc") # a convenient abbreviation

###e we also want DrawInAbsCoords -- but its code doesn't seem very related; several implem strategies differ re displists/highlighting

###e another thing we want is more like "draw in the local coords of a given object" (DrawInThingsCoords?) --
# but that's harder -- and not even well-defined if that obj is drawn in more than one place (or nowhere) --
# unless the meaning is to redraw the argument once for each such place! See also Highlightable's "run_OpenGL_in_local_coords" or so.
# This was wanted for demo_MT.py cross-highlighting, which might have some comments about alternatives to that. [070210]

# end
