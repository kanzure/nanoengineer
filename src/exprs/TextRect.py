"""
$Id$
"""

# == fyi: old version of this from cad/src/drawtest.py, still in use up there:

WidgetExpr = Stub

class TextRect_upstairs(WidgetExpr): # [later 061113: I plan to make a new version of this in exprs module, still using drawfont2 from here]
    "TextRect(width, height, msg_func) renders as a rect of width by height chars taken from msg_func(env), origin on bottomleft"
    def init(self):
        self.dims = width, height = self.args[0], self.args[1]
        self.bright = width * tex_width # global constant
        self.btop = height * tex_height
        ### those are in the wrong units, not pixelwidth, so we need to kluge them for now
        self.bright = self.btop = 1 ########@@@@@@@@ WRONG
        self.msg_func = self.args[2]
    def draw(self):
        glpane = _kluge_glpane()
        width, height = self.dims
        msg = resolve_callables( self.msg_func, 'fakeenv')
        glPushMatrix() ####k guess
        drawfont2(glpane, msg, width, height)
        glPopMatrix()
    pass

# == new version

# Plan: make this just good enough for use as a debugging tool -- e.g. to make instances that show their own ipath.
# It still uses utility funcs and an assumed-bound-texture from cad/src/drawtest.py.

class TextRect():
    
    def draw(self):
        glpane, msg, width, height
        
        from testdraw import drawfont2
        drawfont2(glpane, msg, width, height)
    pass
