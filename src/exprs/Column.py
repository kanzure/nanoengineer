"""
Column.py - provide SimpleColumn and SimpleRow, and someday, fancier Column and Row

[#e module might be renamed; otoh, if we have Table it'll be enough more complex to be in its own file]

$Id$

070129 moved old still-nim fancy Column code into new file Column_old_nim.py,
leaving only Simple{Row,Column} here for now
"""

from basic import * # autoreload of basic is done before we're imported

import draw_utils
reload_once(draw_utils)
from draw_utils import * #k needed??

import Rect
reload_once(Rect)
from Rect import Spacer

import TextRect
reload_once(TextRect)
from TextRect import TextRect

from OpenGL.GL import glPushMatrix, glPopMatrix, glTranslatef ##e revise later into glpane methods or so

# ==

# A simple Column to tide us over for testing other things
# until the real one works. (See Column_old_nim.py for the "real one";
# it includes CW, CL, CLE, which some comments herein may refer to.)

class SimpleColumn(Widget2D): #061115
    #e or use InstanceMacro using Overlay & Translate? Could work, but slower and not needed... might help in CL with fancier gaps.
    ## a0 = Arg(Widget2D) # note: this probably doesn't preclude caller from passing None, and even if it does, nothing enforces that yet;
        # if caller does pass None (to this or to Overlay), best thing is probably to replace this with Pass = Rect(0,0,white)
        # and use it as a drawable, but have special case to use no gap under it -- or the equiv, as a simple change
        # to our btop formula so it's 0 if not a0 -- which is already done, so maybe there's no need to worry about a0 = None.
        # Maybe it should be an optional arg like the others. [061115]
    a0 = Arg(Widget2D, None) # so it's not a bug to call it with no args, as when applying it to a list of no elts [061205]
    a1 = Arg(Widget2D, None)
    a2 = Arg(Widget2D, None)
    a3 = Arg(Widget2D, None)
    a4 = Arg(Widget2D, None)
    a5 = Arg(Widget2D, None) # use ArgList here when that works
    a6 = Arg(Widget2D, None)
    a7 = Arg(Widget2D, None)
    a8 = Arg(Widget2D, None)
    a9 = Arg(Widget2D, None)
    a10 = Arg(Widget2D, None)
    a11 = Arg(Widget2D, None)
    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10, # could say or_Expr(a0, Spacer(0)) but here is not where it matters
                     and_Expr(a11, TextRect("too many columns"))
                     )
    
    ## gap = Option(Width, 3 * PIXELS)
    pixelgap = Option(float, 3) # 070104 int -> float
    gap = pixelgap * PIXELS

    print_lbox = Option(bool, False) #061127 for debugging; should be harmless; never tested (target bug got diagnosed in another way)
    
    drawables = call_Expr(lambda args: filter(None, args) , args)
    ## empty = not drawables ###e BUG: needs more Expr support, I bet; as it is, likely to silently be a constant False; not used internally
    empty = not_Expr(drawables)
    bleft = call_Expr(lambda drawables: max([arg.bleft for arg in drawables] + [0]) , drawables)
    bright = call_Expr(lambda drawables: max([arg.bright for arg in drawables] + [0]) , drawables)
    height = call_Expr(lambda drawables, gap: sum([arg.height for arg in drawables]) + gap * max(len(drawables)-1,0) , drawables, gap)
    ## btop = a0 and a0.btop or 0  # bugfix -- use _Expr forms instead; i think this form silently turned into a0.btop [061205]
    btop = or_Expr( and_Expr( a0, a0.btop), 0)
    bbottom = height - btop
    def draw(self):
        if self.print_lbox:
            print "print_lbox: %r lbox attrs are %r" % (self, (self.bleft, self.bright, self.bbottom, self.btop))
        glPushMatrix()
        prior = None
        for a in self.drawables:
            if prior:
                # move from prior to a
                dy = prior.bbottom + self.gap + a.btop
                glTranslatef(0,-dy,0) # positive is up, but Column progresses down
            prior = a
            a.draw()
        glPopMatrix()
        return
    pass # end of class SimpleColumn

class SimpleRow(Widget2D):
    # copy of SimpleColumn, but bbottom <-> bright, btop <-> bleft, width <- height, and 0,-dy -> dx,0, basically
    a0 = Arg(Widget2D, None) 
    a1 = Arg(Widget2D, None)
    a2 = Arg(Widget2D, None)
    a3 = Arg(Widget2D, None)
    a4 = Arg(Widget2D, None)
    a5 = Arg(Widget2D, None) # use ArgList here when that works
    a6 = Arg(Widget2D, None)
    a7 = Arg(Widget2D, None)
    a8 = Arg(Widget2D, None)
    a9 = Arg(Widget2D, None)
    a10 = Arg(Widget2D, None)
    a11 = Arg(Widget2D, None)
    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10,
                     and_Expr(a11, TextRect("too many rows"))
                     )
    
    pixelgap = Option(int, 3)
    gap = pixelgap * PIXELS
    
    drawables = call_Expr(lambda args: filter(None, args) , args)
    empty = not_Expr( drawables)
    btop = call_Expr(lambda drawables: max([arg.btop for arg in drawables] + [0]) , drawables)
    bbottom = call_Expr(lambda drawables: max([arg.bbottom for arg in drawables] + [0]) , drawables)
    width = call_Expr(lambda drawables, gap: sum([arg.width for arg in drawables]) + gap * max(len(drawables)-1,0) , drawables, gap)
    bleft = or_Expr( and_Expr( a0, a0.bleft), 0)
    bright = width - bleft
    def draw(self):
        glPushMatrix()
        prior = None
        for a in self.drawables:
            if prior:
                # move from prior to a
                dx = prior.bright + self.gap + a.bleft
                glTranslatef(dx,0,0) # positive is right, and Row progresses right
            prior = a
            a.draw()
        glPopMatrix()
        return
    pass # end of class SimpleRow

# end
