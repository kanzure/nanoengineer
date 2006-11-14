"""
$Id$
"""

# WARNING: there is an old version of this (same name TextRect) from cad/src/drawtest.py, still in use up there.

# Note: this uses fixed size for text on screen, regardless of depth -- we'll need to revise this someday. #e


from basic import *

# Plan: make this just good enough for use as a debugging tool -- e.g. to make instances that show their own ipath.
# It still uses utility funcs and an assumed-bound-texture from cad/src/drawtest.py.

from OpenGL.GL import glPushMatrix, glPopMatrix #e replace with glpane_proxy attrs

class TextRect(Widget2D):
    """TextRect(msg, nlines, ncols) renders as a rect of ncols by nlines chars,
    taken from str(msg) (typically a formula in _self, expressed as a lambda ###HOW?),
    origin on bottomleft.
       #e future: nlines defaults to lines in msg, limited by option max_lines, default 6;
    ncols defaults to cols in msg, limited by option max_cols, default 16.
    #doc textsize issues, lbox issues
    """
    from testdraw import tex_width, tex_height # constants (#e shouldn't be; see comments where they're defined)
    # args
    msg = Arg(str)
    nlines = Arg(int, 6) # related to height, but comes first anyway (renamed from nrows) ###e try default of _self.msg_lines, etc
    ncols = Arg(int, 16) # related to width
    # options
    max_lines = Option(int, 6) ###e not yet used
    max_cols = Option(int, 16)
    margin = Option(int, 2) # in pixels -- should this be said in the type? ###k
    # formulae
    ###e msg_lines, msg_cols, and make sure those can be used in the default formulae for the args
    # lbox attrs -- in the wrong units, not pixelwidth, so we need to kluge them for now
    margin1 = margin * PIXELS # bugs: option might want to know type PIXELS, and it all shows up on the right, none on the left
    bright = ncols * PIXELS * tex_width + 2 * margin1
    btop = nlines * PIXELS * tex_height + 2 * margin1
    def draw(self):
        glpane = self.env.glpane
        msg = str(self.msg) #k str() won't always be needed, maybe isn't now ##e guess: need __mod__ in Expr
        width = self.ncols # in chars
        height = self.nlines # in chars

        if 1:
            # until we have Arg type coercion, see if this detects caller errors -- it does:
            ## ValueError: invalid literal for int(): line 1
            ## line 2
            width = int(width)
            height = int(height)
        
        from testdraw import drawfont2
        glPushMatrix() ####k guess, not sure needed
        #e translate by margin
        drawfont2(glpane, msg, width, height)
        glPopMatrix()
        return
    pass # TextRect

# end
