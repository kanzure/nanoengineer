# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

# WARNING: there is an old version of this (same name TextRect) from cad/src/drawtest.py, still in use up there.

# Note: this uses fixed size for text on screen, regardless of depth -- we'll need to revise this someday. #e


# Plan: make this just good enough for use as a debugging tool -- e.g. to make instances that show their own ipath.
# It still uses utility funcs and an assumed-bound-texture from cad/src/drawtest.py.

from OpenGL.GL import glPushMatrix, glPopMatrix #e replace with glpane_proxy attrs

from exprs.attr_decl_macros import Arg, Option
from exprs.Exprs import min_Expr, call_Expr
from exprs.widget2d import Widget2D
from exprs.ExprsConstants import PIXELS
from exprs.__Symbols__ import _self

# TODO: see if our runtime imports from texture_fonts can be done at toplevel

class TextRect(Widget2D):
    """TextRect(msg, nlines, ncols) renders as a rect of ncols by nlines chars,
    taken from str(msg) (typically a formula in _self or _this(something)),
    origin on bottomleft.
       Arg nlines defaults to lines in msg, limited by option max_lines, default 6;
    ncols defaults to cols in msg, limited by option max_cols, default 45.
    #doc textsize issues, lbox issues, arg order reason (some caller comment explains it, i think, maybe in test.py).
    """
    from graphics.drawing.texture_fonts import tex_width, tex_height # constants (#e shouldn't be; see comments where they're defined)
    # args
    msg = Arg(str)
    nlines = Arg(int, min_Expr( _self.msg_lines, _self.max_lines) ) # related to height, but in chars
        ###e try default of _self.msg_lines, etc -- trying this 061116
    ## ncols = Arg(int, 16) # related to width, but in chars
    ncols = Arg(int, min_Expr( _self.msg_cols, _self.max_cols) ) # related to width, but in chars
    # options
    max_lines = Option(int, 6)
    max_cols = Option(int, 45) # 16 -> 45 (guess), 061211, was never used before btw
    margin = Option(int, 2) # in pixels -- should this be said in the type? ###k
    # formulae for arg defaults, from other args and options (take care to not make them circular!) [061116]
    msg_lines = call_Expr( call_Expr(msg.rstrip).count, '\n') + 1
        # i.e. msg.rstrip().count('\n') + 1, but x.y(z) syntax-combo is not allowed, as a safety feature --
        # we'll need to find a way to sometimes allow it, I think.
    msg_cols = call_Expr( lambda msg: max(map(len, msg.split('\n'))) , msg ) # finally implemented 061211
    # formulae
    ###e msg_lines, msg_cols, and make sure those can be used in the default formulae for the args
    # lbox attrs -- in the wrong units, not pixelwidth, so we need to kluge them for now
    margin1 = margin * PIXELS # bugs: option might want to know type PIXELS, and it all shows up on the right, none on the left
    bright = ncols * PIXELS * tex_width + 2 * margin1
    btop = nlines * PIXELS * tex_height + 2 * margin1
    def draw(self):
        assert self._e_is_instance, "draw called on non-Instance of TextRect" #061211
        glpane = self.env.glpane
        msg = str(self.msg) #k str() won't always be needed, maybe isn't now ##e guess: need __mod__ in Expr
        width = self.ncols # in chars
            # WARNING: every Widget2D has self.width in native Width units; don't assign ncols to self.width or you'll mess that up.
            #e probably we should rename this localvar to ncols, same for height/nlines.
        height = self.nlines # in chars

        if 1:
            # until we have Arg type coercion, see if this detects caller errors -- it does:
            ## ValueError: invalid literal for int(): line 1
            ## line 2
            width = int(width)
            height = int(height)

        from graphics.drawing.texture_fonts import drawfont2
        glPushMatrix() ####k guess, not sure needed
        #e translate by margin
        drawfont2(glpane, msg, width, height, pixelwidth = PIXELS)
            #061211 pass pixelwidth so rotation won't matter (warning: different value than before, even w/o rotation)
        glPopMatrix()
        return
    pass # TextRect

# end
