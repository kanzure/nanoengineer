"""
Column.py - provide SimpleColumn and SimpleRow, and someday, fancier Column and Row

[#e module might be renamed; otoh, if we have Table it'll be enough more complex to be in its own file]

$Id$

070129 moved old still-nim fancy Column code into new file Column_old_nim.py,
leaving only Simple{Row,Column} here for now
"""

from basic import * # autoreload of basic is done before we're imported
from basic import _self

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

debug070321 = False

class SimpleColumn_NEW(Widget2D): #061115, revised 070321 to use new ArgList -- but disabled 070322,
    # since too slow for routine use (eg in testexpr_19g),
    # until we fix that update speed bug which means a change in any element remakes them all.
    ### fyi: a test that puts too many elts for SimpleColumn_OLD into the MT: _30i, dna x 3, rects x 2

    #e or use InstanceMacro using Overlay & Translate? Could work, but slower and not needed... might help in CL with fancier gaps.
    ## a0 = Arg(Widget2D) # note: this probably doesn't preclude caller from passing None, and even if it does, nothing enforces that yet;
        # if caller does pass None (to this or to Overlay), best thing is probably to replace this with Pass = Rect(0,0,white)
        # and use it as a drawable, but have special case to use no gap under it -- or the equiv, as a simple change
        # to our btop formula so it's 0 if not a0 -- which is already done, so maybe there's no need to worry about a0 = None.
        # Maybe it should be an optional arg like the others. [061115]
##    a0 = Arg(Widget2D, None) # even the first arg can be missing, as when applying it to a list of no elts [061205]
##    a1 = Arg(Widget2D, None)
##    a2 = Arg(Widget2D, None)
##    a3 = Arg(Widget2D, None)
##    a4 = Arg(Widget2D, None)
##    a5 = Arg(Widget2D, None) # use ArgList here when that works
##    a6 = Arg(Widget2D, None)
##    a7 = Arg(Widget2D, None)
##    a8 = Arg(Widget2D, None)
##    a9 = Arg(Widget2D, None)
##    a10 = Arg(Widget2D, None)
##    a11 = Arg(Widget2D, None) # the 12th arg is 1 too many
##    toomany = Instance(TextRect("too many args to SimpleColumn"))
##        #070212 added Instance to fix mysterious bug manifesting as this debug output:
##        ## getattr_debugprint: <lexenv_ipath_Expr... <TextRect#2331(a)>> has no 'bleft'
##    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10, # could say or_Expr(a0, Spacer(0)) but here is not where it matters
##                     and_Expr(a11, toomany)
##                     )
    args = ArgList(Widget2D, (), doc = "0 or more things (that can participate in 2d layout) to show in a column")
    ## a0 = _self.a0 # kluge, but should be legal (so document it somewhere): get a0 into the class-def namespace for direct use below
        # oops, it fails like this:
        ## AssertionError: error: can't define both 'a0' and '_C_a0' in the same class 'SimpleColumn'
        ## (since ExprsMeta is its metaclass) ...
        # but that's just because the kluge to remove a0 from ns when a0 = _self.a0 fails to then permit _C_a0 to be defined.
        # I should fix that in ExprsMeta (see attr = _self.attr comment) -- but for now, use _C_a0_kluge instead:
    ## def _C_a0(self):
    a0 = _self.a0_kluge
    def _C_a0_kluge(self):
        args = self.args
        args[0:] # make sure this works (i.e. args is a sequence)
        if len(args):
            return args[0]
        else:
            return None
        pass

    def _init_instance(self):##### debug only
        super(SimpleColumn, self)._init_instance()
        try:
            args = 'bug' # for use in error message, in case of exception
            args = self.args
            len(args) # make sure this works!
            if debug070321:
                print "fyi: this SimpleColumn has %d args" % len(args)
                print "fyi: the args i mentioned are: %r" % (args,) #####
        except:
            print "following exception concerns self = %r, args = %r" % (self, args)
            raise
        return
    
    ## gap = Option(Width, 3 * PIXELS)
    pixelgap = Option(float, 3) # 070104 int -> float
    gap = pixelgap * PIXELS

    print_lbox = Option(bool, False) #061127 for debugging; should be harmless; never tested (target bug got diagnosed in another way)
    
    drawables = call_Expr(lambda args: filter(None, args) , args)
    ## empty = not drawables ###e BUG: needs more Expr support, I bet; as it is, likely to silently be a constant False; not used internally
    empty = not_Expr(drawables)
    bleft = call_Expr(lambda drawables: max([arg.bleft for arg in drawables] + [0]) , drawables)
        # 070211 arg.bleft -> getattr_debugprint(arg, 'bleft')
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
            self.drawkid(a) ## a.draw()
        glPopMatrix()
        return
    pass # end of class SimpleColumn_NEW or SimpleColumn

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
    a0 = Arg(Widget2D, None) # even the first arg can be missing, as when applying it to a list of no elts [061205]
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
    a11 = Arg(Widget2D, None) # the 12th arg is 1 too many
    toomany = Instance(TextRect("too many args to SimpleColumn"))
        #070212 added Instance to fix mysterious bug manifesting as this debug output:
        ## getattr_debugprint: <lexenv_ipath_Expr... <TextRect#2331(a)>> has no 'bleft'
    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10, # could say or_Expr(a0, Spacer(0)) but here is not where it matters
                     and_Expr(a11, toomany)
                     )
    
    ## gap = Option(Width, 3 * PIXELS)
    pixelgap = Option(float, 3) # 070104 int -> float
    gap = pixelgap * PIXELS

    print_lbox = Option(bool, False) #061127 for debugging; should be harmless; never tested (target bug got diagnosed in another way)
    
    drawables = call_Expr(lambda args: filter(None, args) , args)
    ## empty = not drawables ###e BUG: needs more Expr support, I bet; as it is, likely to silently be a constant False; not used internally
    empty = not_Expr(drawables)
    bleft = call_Expr(lambda drawables: max([arg.bleft for arg in drawables] + [0]) , drawables)
        # 070211 arg.bleft -> getattr_debugprint(arg, 'bleft')
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
            self.drawkid(a) ## a.draw()
        glPopMatrix()
        return
    pass # end of class SimpleColumn or SimpleColumn_OLD

# ==

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
    toomany = Instance(TextRect("too many args to SimpleRow"))
    args = list_Expr(a0,a1,a2,a3,a4,a5, a6,a7,a8,a9,a10,
                     and_Expr(a11, toomany)
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
            self.drawkid(a) ## a.draw()
        glPopMatrix()
        return
    pass # end of class SimpleRow

# end
