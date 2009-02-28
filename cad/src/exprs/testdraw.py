# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
testdraw.py -- drawing code for testmode, which tests the exprs package.

[for doc, see testmode.py]

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

BUGS:

- 081204: testmode messes up ruler text and clipboard part text:
  mouse motion over a highlightable alternately turns highlighting and text colors on and off;
  with highlight on, text fg is white and bg clear (wrong but readable);
  with highlight off (a bug in itself), text fg and bg are both the same
  as whatever i set for text fg bfr renderText;
  there are two redraws per mouse motion (normal for motion over a *non*-highlighted object) when rulers are on;
  rulers *or* clipboard text also messes up some of the highlightable behavior in testmode,
  making it alternate (as described above).

  guesses as to the cause:
  - could it be related to calling qglClearColor with the text color,
    in the text rendering code?
  - could renderText mess up something else related to highlighting,
    like stencil buffer?
  mostly it's a mystery.

### WARNING: most of the rest of this docstring is obs:

known bugs:
+ slowness of redraw, and redraw happens whenever i go on or off a highlighted thing, or on or move around on something else.
  this is much worse on my iMacG4 than my iMac G5, but not because of redraw speed,
  but because on the G4, the mouse cursor stops following the mouse during the redraw!!!
  Possible fixes: different hit test alg, C-coded redraw or hit test, use of display list or saved color/depth buffer for
  nonhighlighted stuff.
  ... i put in a display list, which fixed it, but it's not invalled enough. (it also needs inval by trackball, unlike a chunk's.)

- highlight orange is slightly wider on right than nonhighlight pink (guess: glpane translates in model space, not just depth space)

- see the exception from the selobj alive test, which happens on clicks (left or cmenu) and on highlight not covering selobj,
  described below (in class Highlightable) [fixed now?]

- DraggedOn and ReleasedOn are nim (and need renaming) [no longer true, as of very long before 061120]

- region selection - works to select atoms in a rect, but the rect for it is not being drawn  [even w/o displist optim]
  - is it a failure to delegate some method to superclass, maybe emptySpaceLeftDown?
  - is it related to the reload that happens on that leftDown? (not sure why it would be)
  solved: it was failure to call super.Draw! Tested, but fix reverted, since i wanted to test the old way again. ###@@@

- singlet-drag to bond - also works but lacks rubberband line [even w/o displist optim] [might be fixed now??]

- draw_later doesn't make thing highlightable even when i don't touch color enablement and do it not much later,
so how can I test the real thing? [relates to Invisible] [would it work better as Transparent? Probably not yet...]
[###@@@ maybe fixed now]

- TextRect:
  - size is wrong
  - origin is wrong [probably fixed]
  + if too few lines, testchars at top rather than blanklines at bottom [fixed]
  - sometimes fuzzy (should fix several of these by using pixmap/displist text, or the bitmap text in pyrex_atoms)
  - fails to notice hits, in Button... no idea why. interesting Q - does it draw into depth buffer at all?
    yes it does; also, if i slide off black rect onto text, it works fine, only if i slide onto text does it fail.
    AHA, i bet it does something funny with size/pos, which messes up rendering by draw_in_abs_coords.

==

todo:
- try a display list optim in main draw function, for keeping non-highlighted stuff in one;
might work almost as well as a color/depth buffer, for this code;
but this requires knowing when it changed. One advantage: works across rotations
(as long as we keep any billboarded stuff out of it). Note: some text rendering here
shrinks when it gets nonparallel, but that's a bug, not a form of billboarding.
- more & better-organized widget exprs.
- widget exprs that map from external state (such as that in Nodes), and let us edit it.
  - i'm suspecting that one widget expr should often be used to draw all the things that use the same formulas it was set up with,
    so it would never carry per-object state -- it would be more like code. (But right now, Highlightable does carry some.)
  - for this to work, but fit with simple compounds like Row, the widget-subexprs need to get their own sub-state;
    this (as func of main state) could either be a code-id from their instance, or a posn from their caller,
    and done at compile time (their __init__ time) or draw time -- but it needs to work when they get reloaded/remade,
    suggesting that (for these simple compound -- not for iteratives used to describe rules)
    it's mainly positional, or "positional but sorted by type" so that a few kinds of code-changes don't destroy data.
    (But with optional explicit ids per instance, so that old data *can* be destroyed if you want, or preserved more readily.
    The auto ids are really only needed for transient things like glnames and saved modelview matrices, which any highlightable needs,
    and maybe for saved display lists, inval data, etc; so maybe it doesn't matter if those change on reload.
    And for anything referring to user-editable data, you need explicit ids anyway so you can recode and not obsolete your data.)
    - likely state implem (if we ignore letting it be "externally storable"): linked dicts; any convenient pyobj-constant keys,
    or maybe string keys.
    Possible convention (not thought through): the ids usable as attrs are the ones whose chars work in a py identifier.
- more todos findable by searching for "todo", "Drawable", and (older ones) "next up", "wishlist", and (implicit ones) "kluge".
"""

__author__ = "bruce"

import time

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glTranslate

import foundation.env as env
from utilities import debug_flags

from utilities.debug import print_compact_traceback

from utilities.constants import ave_colors
from utilities.constants import blue
from utilities.constants import white
from utilities.constants import green
from utilities.constants import red

from exprs.reload import exprs_globals
    #bruce 071102 renamed vv -> exprs_globals and moved it out of this file,
    # to avoid import cycle

exprs_globals.reload_counter += 1
    # the first time we load testdraw, this changes that counter
    # from -1 to 0; when we reload it, it changes it to 1, 2, etc;
    # thus the counter counts the number of reloads of testdraw.

### a lot of the following constants are probably obs here, redundant with ones now defined in exprs module [070408 comment]

printdraw = False # debug flag

from graphics.drawing.texture_fonts import ensure_courierfile_loaded

##lightblue = ave_colors( 0.2, blue, white)
halfblue = ave_colors( 0.5, blue, white)
##purple = ave_colors(0.5, red, blue)

def translucent_color(color, opacity = 0.5): #e refile with ave_colors
    """Make color (a 3- or 4-tuple of floats) have the given opacity (default 0.5, might be revised);
    if it was already translucent, this multiplies the opacity it had.
    """
    if len(color) == 3:
        c1, c2, c3 = color
        c4 = 1.0
    else:
        c1, c2, c3, c4 = color
    return (c1, c2, c3, c4 * opacity)

trans_blue = translucent_color(halfblue)
trans_red = translucent_color(red)
trans_green = translucent_color(green)

# ==

# note: class avoidHighlightSlowness was defined here in rev. 1.6, but didn't work and probably can't work, so I zapped it.
# Its goal was to avoid the redraws on every mouseover motion of drawing that doesn't use glname to make itself highlightable.
# Instead, just get all drawing to be inside a highlightable object. (It's ok if the highlighting is not visible.
# It just needs to get into the stencil and depth buffers like the plain object, so we don't worry whether we're over other objects
# during the mouseover.)

# ==

if debug_flags.atom_debug:
    print "\ntestdraw: %d reloads" % exprs_globals.reload_counter

def end_of_Enter(glpane):
    # called by testmode.Enter after it does everything else including super Enter; was never called before 070103
    ## glpane.win.setViewHome() # not tested, might be wrong; redundant now (if home view is the default)
    init_glpane_vars(glpane)
    # print "did end_of_Enter on",glpane # works
    
def init_glpane_vars(glpane):
    # print "init_glpane_vars on glpane %r" % glpane # called by Draw and by end_of_Enter (as of 070103)
    glpane._glnames = []
    glpane._testmode_stuff = []
    glpane._testmode_stuff_2 = []
    glpane._testmode_stuff_3 = []
    glpane._alpha = 1.0
    
def leftDown(mode, event, glpane, super): # called from testmode.leftDown
    "[mode is needed to call super.leftDown]"
    ####@@@@ LOGIC BUG: when we reload, we replace one highlightable with a new one in the same place --
    # but don't replace selobj with the new one! So we predict not selobj_still_ok -- should print that from there ###@@@
    # [fixed now? note, reload is not right here, but in super.leftDown when it calls testmode.emptySpaceLeftDown]
    if printdraw: print "\ntestdraw leftDown" ###@@@
    super.leftDown(mode, event) # this might call testmode.emptySpaceLeftDown (or other class-specific leftDown methods in it)
    glpane.gl_update() # always, for now [might be redundant with super.leftDown, too]

def render_scene(mode, glpane): # called by testmode.render_scene # 061208
    # print "calling glpane.render_scene from testdraw.render_scene" -- works
    glpane.render_scene()
    return
    
def Draw(mode, glpane, super): # called by testmode.Draw
    
    init_glpane_vars(glpane)

    if env.prefs.get("A9 devel/testdraw/super.Draw first?", True): #070404
        glPushMatrix() #k needed??
        super.Draw(mode)
        glPopMatrix()

    # glpane.part.draw(glpane) # this doesn't draw the model in any different place as when done below... [061211]
    
    glPushMatrix()
    try:
        drawtest0(glpane) # this does all our special drawing, and sometimes puts some of it into a display list
        # [no point in putting the main model drawing into it, for now -- but when we can know when to inval, there might be]
    except:
        print_compact_traceback("exc ignored: ")
    glPopMatrix() # it turns out this is needed, if drawtest0 does glTranslate, or our coords are messed up when glselect code
    # [not sure what this next comment is about:]
    # makes us draw twice! noticed on g4, should happen on g5 too, did it happen but less??
    if env.prefs.get("A9 devel/testdraw/super.Draw last?", False): # revised prefs key and default, 070404
        glPushMatrix()
        if 1:
            super.Draw(mode) # needed for region selection's separate xor-drawing;
            # I suspect this is slower than the other case. Does it draw more than once (for glselect) or something like that? ####@@@@
        else:
            # region selection's drawing [later: xor mode, i guess] won't work in this case, though its selection op itself will work
            glpane.part.draw(glpane) # highlighting works fine on this copy...
        if 0 and 'draw copy2 of model':
            glTranslate(5,0,0)
            glpane.part.draw(glpane) # but not on this one - i see why it doesn't draw it there, but why not complain about not finding it?
        glPopMatrix()
    # draw invisible stuff
    #e (we'll want to split this into stages for more than one kind of such stuff; later, to go through a "rendering pass widget expr")
    for func in glpane._testmode_stuff_2: # colors, for translucent stuff
        func()
    for func in glpane._testmode_stuff_3: # depths, for translucent stuff (matters if they are highlightable)
        func()
    for func in glpane._testmode_stuff: # depths, for invisible stuff
        func()
    return

def Draw_after_highlighting(mode, pickCheckOnly, glpane, super):
    ## print "testdraw.Draw_after_highlighting(pickCheckOnly = %r)" % (pickCheckOnly,) # pickCheckOnly is True once when I click
    return super.Draw_after_highlighting(mode, pickCheckOnly)

# ==

def drawtest0(glpane):
    """
    run drawtest1, protected from exceptions, after setting up some of its environment
    """
    # load the texture for the courier bitmap font; params incl tex_name are in private texture_fonts.vv object
    ensure_courierfile_loaded() # used to be done inside drawtest1
    glpane.kluge_reset_texture_mode_to_work_around_renderText_bug() #bruce 081205; ok this soon?

    exprs_globals.start_time = time.time()
        # anything that gets drawn can compare this with realtime
        # to get time so far in this frame, but it's up to it to be drawn
        # near the end of what we draw in the frame
    
    try:
        if printdraw:
            print "drawfunc (redraw %d)" % env.redraw_counter
        drawtest1(glpane)
    except:
        # this happens sometimes
        print_compact_traceback("exception in testdraw.py's drawfunc call ignored: ")
    return

def drawtest1(glpane):
    # main special drawing -- let the exprs module do it
    _reload_exprs_test()
    from exprs.test import drawtest1_innards
    drawtest1_innards(glpane)
    return

def _reload_exprs_test():
    # will need REVIEW when we have a new reloading system to replace heavy manual use of reload_once
    from exprs.reload import reload_once
    from exprs import test
    reload_once(test)
    return

# ==

# (some outtakes removed to bruceG5 testdraw-outtakes.py, last here in rev 1.11)
# (lots more removed 070408 over several commits, last here in rev 1.55)

# end
