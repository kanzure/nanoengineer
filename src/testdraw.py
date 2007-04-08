# Copyright (c) 2006-2007 Nanorex, Inc.  All rights reserved.
'''
testdraw.py -- scratchpad for new code, OWNED BY BRUCE, not imported by default.

FOR NOW [060716], NO ONE BUT BRUCE SHOULD EDIT THIS FILE IN ANY WAY.

$Id$

[for doc, see testmode.py]

### WARNING: most of the rest of this docstring is obs:

known bugs:
+ slowness of redraw, and redraw happens whenever i go on or off a highlighted thing, or on or move around on something else.
  this is much worse on my iMacG4 than my iMac G5, but not because of redraw speed,
  but because on the G4, the mouse cursor stops following the mouse during the redraw!!!
  Possible fixes: different hit test alg, C-coded redraw or hit test, use of display list or saved color/depth buffer for
  nonhighlighted stuff.
  ... i put in a display list, which fixed it, but it's not invalled enough. (it also needs inval by trackball, unlike a chunk's.)

- Changing the current view doesn't reset havelist = 0, and this causes the highlight posn to be wrong!
  So I made havelist care about assy._view_change_counter, but that's nim in assy (changed_view is not called by anything)
  so this didn't help! Maybe it needs to care about the view data itself? ####@@@@
  Workaround: click in empty space after you change the view.

- we'll need to remember to reset havelist when we change other state, once we can do that.

- highlight orange is slightly wider on right than nonhighlight pink (guess: glpane translates in model space, not just depth space)

+ [fixed] highlighted Ribbon2 has color bug (so does the unhighlighted one, or at least eventually that bug developed)

- Ribbon2 needs a larger highlight region w/o holes (since they cause flickering), but transparent highlight region is nim
  (could do it with depth-only writing, at end like with all transparent stuff, or a different hit-test alg)

- Ribbon2 highlighting flickers it somewhat, maybe related to the edge not being drawn in the same way???
  guess (speculation): the coords are different enough that the pixel edge effects are not identical.
  
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
'''

__author__ = "bruce"

from testmode import *
from debug import print_compact_traceback
import env

### a lot of the following constants are probably obs here, redundant with ones now defined in exprs module [070408 comment]

printdraw = False # debug flag

ORIGIN = V(0,0,0)
DX = V(1,0,0)
DY = V(0,1,0)
DZ = V(0,0,1)

ORIGIN2 = V(0.0, 0.0)
D2X = V(1.0, 0.0)
D2Y = V(0.0, 1.0)

class attrholder: pass

from constants import ave_colors # (weight, color1, color2) # weight is of color1 i think
lightblue = ave_colors( 0.2, blue, white)
lightgreen = ave_colors( 0.2, green, white)
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


try:
    vv
    vv.displist
    vv.havelist
    vv.reload_counter += 1
##    vv.when_drawtest1_last_ran
    vv.state
except:
    vv = attrholder()
    vv.tex_name = 0
    vv.tex_data = None
    vv.counter = 0
    vv.displist = glGenLists(1)
    vv.havelist = 0
    vv.reload_counter = 0
##    vv.when_drawtest1_last_ran = -1
    vv.state = {} # prototype of a place to store persistent state (presuming some persistent way of allocating keys, eg hardcoding)
    ##e should modify to make it easier to set up defaults; sort of like a debug_pref?

# vv.counter = 0 # just to get started (was needed when i moved file to another machine, already running, too)

# ==

print "\n%d reloads" % vv.reload_counter

if vv.havelist:
    vv.havelist = 0
    print "(fyi, this reload needed to reset vv.havelist)"
    
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
    vv.havelist = 0 # so editing this file (and clicking) uses the new code -- this also affects clicks on selobj which don't reload
    super.leftDown(mode, event) # this might call testmode.emptySpaceLeftDown (or other class-specific leftDown methods in it)
    glpane.gl_update() # always, for now [might be redundant with super.leftDown, too]

def render_scene(mode, glpane): # called by testmode.render_scene # 061208
    # print "calling glpane.render_scene from testdraw.render_scene" -- works
    glpane.render_scene()
    return
    
def Draw(mode, glpane, super): # called by testmode.Draw
    
    init_glpane_vars(glpane)
    vv.counter += 1

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
    super.Draw_after_highlighting(mode, pickCheckOnly)
    return

# ==

def havelist_counters(glpane):
    "return some counters which better have the same value or we'll treat havelist as if it was invalidated"
    assy = glpane.assy
    return (assy._view_change_counter,) # this doesn't work, since changing view doesn't actually incr that counter. ###@@@

def display_list_helper(self, glpane, drawfunc):
    "self needs .havelist and .displist"
##    wantlist = USE_DISPLAY_LIST_OPTIM
##    if wantlist and self.havelist == havelist_counters(glpane): ## == (disp, eltprefs, matprefs, drawLevel): # value must agree with set of havelist, below
##        ##print "calllist (redraw %d)" % env.redraw_counter
##        glCallList(self.displist)
##    else:
    wantlist = False
    if 1:
        if 0:
            #bruce 060608: record info to help per-chunk display modes
            # figure out whether they need to invalidate their memo data.
            if not self.havelist:
                # only count when it was set to 0 externally, not just when it doesn't match and we reset it below.
                # (Note: current code will also increment this every frame, when wantlist is false.
                #  I'm not sure what to do about that. Could we set it here to False rather than 0, so we can tell?? ##e)
                self._havelist_inval_counter += 1
            ##e in future we might also record eltprefs, matprefs, drawLevel (since they're stored in .havelist)
        self.havelist = 0 #bruce 051209: this is now needed
##        try:
##            wantlist = not env.mainwindow().movie_is_playing #bruce 051209
##        except:
##            print_compact_traceback("exception (a bug) ignored: ")
##            wantlist = True
        if wantlist:
##            match_checking_code = self.begin_tracking_usage()
            glNewList(self.displist, GL_COMPILE_AND_EXECUTE)
##            ColorSorter.start() # grantham 20051205

        # bruce 041028 -- protect against exceptions while making display
        # list, or OpenGL will be left in an unusable state (due to the lack
        # of a matching glEndList) in which any subsequent glNewList is an
        # invalid operation. (Also done in shape.py; not needed in drawer.py.)
        try:
##            self.draw_displist(glpane, disp, (hd, delegate_draw_atoms, delegate_draw_chunk))
            if printdraw: print "drawfunc (redraw %d)" % env.redraw_counter
            drawfunc()
        except:
            print_compact_traceback("exception in testdraw.py's drawfunc call ignored: ")

        if wantlist:
##            ColorSorter.finish() # grantham 20051205
            glEndList()
##            self.end_tracking_usage( match_checking_code, self.inval_display_list )
            # This is the only place where havelist is set to anything true;
            # the value it's set to must match the value it's compared with, above.
            # [bruce 050415 revised what it's set to/compared with; details above]
            self.havelist = havelist_counters(glpane) ## (disp, eltprefs, matprefs, drawLevel)
            assert self.havelist, "bug: havelist must be set to a true value here, not %r" % (self.havelist,)
            # always set the self.havelist flag, even if exception happened,
            # so it doesn't keep happening with every redraw of this molecule.
            #e (in future it might be safer to remake the display list to contain
            # only a known-safe thing, like a bbox and an indicator of the bug.)
        pass
    return

# ==

# old:
####@@@@
# next up: mouse event bindings, state, programming constructs incl scope, formulas (getters? inval?), option-defaults

def drawtest0(glpane):
    "run drawtest1 inside a global display list [old, removed now: then run drawtest2 outside it]"
    # load the texture for the courier bitmap font; params incl tex_name are in vv
    ensure_courierfile_loaded() # used to be done inside drawtest1

    vv.start_time = time.time() # drawing can use this to get time so far, but it's up to it to be drawn near the end of what we draw
    
    # drawtest1, in displist [vv has .havelist and .displist]
    drawfunc = lambda:drawtest1(glpane)
    display_list_helper( vv, glpane, drawfunc)

##    # drawtest2, not in it
##    drawtest2(glpane)
    return

def ensure_courierfile_loaded(): #e rename to reflect binding too
    "load font-texture if we edited the params for that in this function, or didn't load it yet; bind it for drawing"
    tex_filename = courierfile ## "xxx.png" # the charset
    "courierfile"
    tex_data = (tex_filename,)
    if vv.tex_name == 0 or vv.tex_data != tex_data:
        vv.have_mipmaps, vv.tex_name = load_image_into_new_texture_name( tex_filename, vv.tex_name)
        vv.tex_data = tex_data
    else:
        pass # assume those vars are fine from last time
    setup_to_draw_texture_name(vv.have_mipmaps, vv.tex_name)
    return

def _bind_courier_font_texture(): # kluge 061125 so exprs/images.py won't mess up drawfont2; might be slow
    """assuming everything else is set up as needed,
    including that exprs/images.py doesn't change most GL params,
    bind the texture containing the courierfile font
    """
    # optimized part of inlined setup_to_draw_texture_name
    glBindTexture(GL_TEXTURE_2D, vv.tex_name)
    ##e note: this will need extension once images.py can change more params,
    # to do some of the other stuff now done by setup_to_draw_texture_name.
    # OTOH it's too expensive to do that all the time (and maybe even this, if same tex already bound -- remains to be seen).
    return

def drawtest1(glpane):
    # main special drawing; if a global flag is set, it's all put into a global displist by caller (tho it doesn't all work there)

    # let the exprs module do it
    reload_basic_and_test()
    from exprs.test import drawtest1_innards
    drawtest1_innards(glpane)
    
    return # drawtest1 #e rename

def reload_basic_and_test():
    global basic, test, draw_utils
    from exprs import basic
    basic.reload_once(basic) # moved this before import of test [061113 late, when this was just part of drawtest1],
        # to see if it'll fix my occasional failures to actually reload test,
        # and/or errors after reload like this one:
        #   TypeError: super(type, obj): obj must be an instance or subtype of type
    from exprs import test
    basic.reload_once(test)
    # draw_utils added 070408
    from exprs import draw_utils # for draw_textured_rect
    basic.reload_once(draw_utils)
    return

#e put these into an object for a texture font!
tex_width = 6 # pixel width of 1 char within the texture image
tex_height = 10 # pixel height (guess)

def drawfont2(glpane, msg = None, charwidth = None, charheight = None, testpattern = False, pixelwidth = None):
    """draws a rect of chars (dimensions given as char counts: charwidth x charheight [#e those args are misnamed])
    using vv's font texture [later 061113: assumed currently bound, i think -- see ensure_courierfile_loaded()],
    in a klugy way;
    msg gives the chars to draw (lines must be shorter than charwidth or they will be truncated)
    """
    _bind_courier_font_texture()
    # adjust these guessed params (about the specific font image we're using as a texture) until they work right:
    # (tex_origin_chars appears lower down, since it is revised there)
    tex_size = (128,128) # tex size in pixels
    tex_nx = 16 # number of chars in a row, in the tex image
    tex_ny = 8  # number of chars in a column

    if msg is None:
        msg = "(redraw %d)" % env.redraw_counter
        charwidth = tex_nx
        charheight = tex_ny + 1

    lines = msg.split('\n') # tab not supported

    if charwidth is None:
        charwidth = 14 # could be max linelength plus 1
    if charheight is None:
        charheight = len(lines)

    if not testpattern:
        while len(lines) < charheight:
            lines.append('')
    
    # draw individual chars from font-texture,
    # but first, try to position it so they look perfect (which worked for a while, but broke sometime before 060728)

    ## glTranslatef( 0, pixelheight / 2, 0 ) # perfect!
        # (Ortho mode, home view, a certain window size -- not sure if that matters but it might)
        # restoring last-saved window position (782, 44) and size (891, 749)
    
    ## gap = 2 # in pixels - good for debugging
    gap = 0 # good for looking nice! but note that idlehack uses one extra pixel of vspace, and that does probably look better.
      # to do that efficiently i'd want another image to start from.
      # (or to modify this one to make the texture, by moving pixrects around)
    pixfactor = 1 # try *2... now i can see some fuzz... what if i start at origin, to draw?
        # did that, got it tolerable for pixfactor 2, then back to 1 and i've lost the niceness! Is it no longer starting at origin?

    ##pixelwidth = pixelheight = 0.05 * 2/3

    #070124 revisions, general comment... current caveats/bugs: ####
    # - only tested in Ortho mode
    # - working well but the bugs depend on whether we add "1 or" before "pixelwidth is None" in if statement below: 
    #   bugs when it computes pixelwidth here (even when passed, as always in these tests):
    #   - textlabel for "current redraw" (in exprs/test.py bottom_left_corner) disappears during highlighting
    #   bugs when it doesn't [usual state & state I'll leave it in]:
    #   - not tested with displists off, maybe ###
    #   - fuzzy text in testexpr_18 [not yet understood]
    #   - [fixed] fuzzy text in "current redraw" textlabel during anything's highlighting [fixed by removing DisplistChunk from that]
    #   - [no bug in clarity of text in highlighted checkbox prefs themselves]
    # - works with displists on or off now
    # - is disable_translate helping?? not sure (only matters when it computes pixelwidth here -- not now)
    #   - ##e use direct drawing_phase test instead? doesn't seem to be needed anymore, from remaining bugs listed above
    disable_translate = False #070124
    if pixelwidth is None: #061211 permit caller to pass it [note: the exprs module usually or always passes it, acc'd to test 070124]
        p1junk, p2a = mymousepoints(glpane, 10, 10)
        p1junk, p2b = mymousepoints(glpane, 11, 10)
        px,py,pz = vec = p2b - p2a # should be DX * pixelwidth
        ## print px,py,pz # 0.0313971755382 0.0 0.0 (in Ortho mode, near but not at home view, also at it (??))
            # 0.0313971755382 0.0 0.0 home ortho
            # 0.03139613018 0.0 0.0 home perspective -- still looks good (looks the same) (with false "smoother textures")
        ## pixelwidth = pixelheight = px * pixfactor
        pixelwidth = pixelheight = vlen(vec) * pixfactor # 061211 work better for rotated text (still not good unless screen-parallel)
        # print "pixelwidth",pixelwidth
            ####@@@@ can be one of:
            #    0.0319194157846
            # or 0.0313961295259
            # or 0.00013878006302
        if pixelwidth < 0.01:
            # print "low pixelwidth:",pixelwidth, glpane.drawing_phase # e.g. 0.000154639183832 glselect
            pixelwidth = 0.0319194157846
            ### kluge, in case you didn't notice [guess: formula is wrong during highlighting]
            # but this failed to fix the bug in which a TextRect doesn't notice clicks unless you slide onto it from a Rect ####@@@@
            # Q 070124: when this happens (presumably due to small window in glSelect) should we disable glTranslatef below?
            # I guess yes, so try it. Not that it'll help when we re-disable always using this case.
            disable_translate = True # i'll leave this in since it seems right, but it's not obviously helping by test
            
        pass
    else:
        pixelheight = pixelwidth

    tex_origin_chars = V(3, 64) # revised 070124

    if 1 and not disable_translate: #070124 -- note that disable_translate is never set given if statements above --
            ##e use glpane.drawing_phase == 'glselect' instead? doesn't seem to be needed anymore, from remaining bugs listed above
        # Translate slightly to make characters clearer
        #   (since we're still too lazy to use glDrawPixels or whatever it's called).
        # Caveats:
        # - assumes we're either not in a displist, or it's always drawn in the same place.
        # - will only work if we're drawing at correct depth for pixelwidth, I presume -- and of course, parallel to screen.
        x,y,depth = gluProject(0.0, 0.0, 0.0) # where we'd draw without any correction (ORIGIN)

        # change x and y to a better place to draw (in pixel coords on screen)
        # (note: this int(x+0.5) was compared by test to int(x) and int(x)+0.5 -- this is best, as one might guess; not same for y...)
        x = int(x+0.5) ## if we need a "boldface kluge", using int(x)+0.5 here would be one...
        y = int(y+0.5)+0.5 ### NOT UNDERSTOOD: why x & y differ, in whether it's best to add this 0.5.
            # [btw I'd guessed y+0.5 in int() should be (y-0.5)+0.5 due to outer +0.5, but that looks worse in checkbox_pref centering;
            #  I don't know why.]
            #
            # Adding outer 0.5 to y became best after I fixed a bug of translating before glu*Project (just before this if-statement),
            # which fails inside displists since the translate effect doesn't show up in glu*Project then.
            #
            # I wonder if the x/y difference could be related to the use of CenterY around TextRect inside displists,
            # which ought to produce a similar bug if the shift is not by an exact number of pixels (which is surely the case
            #  since the caller is guessing pixelwidth as a hardcoded constant, IIRC). So the guess is that caller's pixelwidth
            # is wrong and/or CenterY shifts by an odd number of halfpixels, inside displist and not seen by this glu*Project,
            # causing a bug which this +0.5 sometimes compensates for, but not always due to pixelwidth being wrong.
            # It's not worth understanding this compared to switching over to glDrawPixels or whatever it's called. ###DO THAT SOMETIME.

        p1 = A(gluUnProject(x, y, depth)) # where we'd like to draw (p1)
        ## p1 += DY # test following code -- with this line, it should make us draw noticeably higher up the screen -- works
        glTranslatef( p1[0], p1[1], p1[2])
            # fyi: NameError if we try glTranslatefv or glTranslatev -- didn't look for other variants or in gl doc
        pass
    
    tex_dx = V(tex_width, 0) # in pixels
    tex_dy = V(0, tex_height)
    # using those guesses, come up with tex-rects for each char as triples of 2-vectors (tex_origin, tex_dx, tex_dy) 
    def ff(i,j): # i for y, j or x (is that order normal??), still starting at bottom left
        "which char to draw at this position? i is y, going up, -1 is lowest line (sorry)"
        nlines = len(lines)
        bottom = -1 # change this api sometime
        abovethat = i - bottom # this one too -- caller ought to be able to use 0 or 1 for the top (first) line
        if abovethat < nlines:
            # draw chars from lines
            test = lines[nlines-1 - abovethat]
                # few-day(?)-old comment [as of 060728], not sure why it's exactly here, maybe since this tells when we redraw,
                # but it might be correct other than that:
                #   this shows that mouseover of objects (pixels) w/o glnames causes redraws! I understand glselect ones,
                # but they should not be counted, and should not show up on the screen, so i don't understand
                # any good reason for these visible ones to happen.
                #e to try to find out, we could also record compact_stack of the first gl_update that caused this redraw...
            if j < len(test):
                # replace i,j with new ones so as to draw those chars instead
                ch1 = ord(test[j]) - 32
                j = ch1 % tex_nx
                i = 5 - (ch1 / tex_nx)
            else:
                # draw a blank instead
                ch1 = 32 - 32
                j = ch1 % tex_nx
                i = 5 - (ch1 / tex_nx)
        else:
            pass # use i,j to index the texture, meaning, draw test chars, perhaps the entire thing
        return tex_origin_chars + i * tex_dy + j * tex_dx , tex_dx, tex_dy
    # now think about where to draw all this... use a gap, but otherwise the same layout
    charwidth1 = tex_width * pixelwidth
    charheight1 = tex_height * pixelheight
    char_dx = (tex_width + gap) * pixelwidth
    char_dy = (tex_height + gap) * pixelheight
    def gg(i,j):
        return ORIGIN + j * char_dx * DX + (i + 1) * char_dy * DY, charwidth1 * DX, charheight1 * DY
    # now draw them

    if 1: #### for n in range(65): # simulate the delay of doing a whole page of chars
      # note, this is significantly slow even if we just draw 5x as many chars!
      for i in range(-1,charheight-1): # (range was -1,tex_ny==8, length 9) - note, increasing i goes up on screen, not down!
        for j in range(charwidth): # was tex_nx==16
            origin, dx, dy = gg(i,j) # where to draw this char ###k
            tex_origin, ltex_dx, ltex_dy = ff(i,j) # still in pixel ints # what tex coords to use to find it
            tex_origin, ltex_dx, ltex_dy = 1.0/tex_size[0] * V(tex_origin, ltex_dx, ltex_dy) # kluge until i look up how to use pixels directly
            #print (origin, dx, dy, tex_origin, tex_dx, tex_dy)
            draw_utils.draw_textured_rect(origin, dx, dy, tex_origin, ltex_dx, ltex_dy) # cool bug effect bfr 'l's here

    # draw some other ones? done above, with test string inside ff function.

    # interesting q -- if i use vertex arrays or displist-index arrays, can drawing 10k chars be fast? (guess: yes.)
    # some facts: this window now has 70 lines, about 135 columns... of course it's mostly blank,
    # and in fact just now it has about 3714 chars, not 70 * 135 = 9450 as if it was nowhere blank.
    # above we draw 9 * 16 = 144, so ratio is 3714 / 144 = 25, or 9450 / 144 = 65.
    # Try 65 redundant loops above & see what happens. It takes it a couple seconds! Too slow! Of course it's mostly the py code.
    # Anyway, it means we *will* have to do one of those optims mentioned, or some other one like not clearing/redrawing
    # the entire screen during most text editing, or having per-line display lists.

    return #drawfont2 #e rename, clean up

    
def mymousepoints(glpane, x, y):
    # modified from GLPane.mousepoints; x and y are window coords (except y is 0 at bottom, positive as you go up [guess 070124])
    self = glpane
    just_beyond = 0.0
    p1 = A(gluUnProject(x, y, just_beyond))
    p2 = A(gluUnProject(x, y, 1.0))

    los = self.lineOfSight # isn't this just norm(p2 - p1)?? Probably not, if we're in perspective mode! [bruce Q 061206]
        # note: this might be in abs coords (not sure!) even though p1 and p2 would be in local coords.
        # I need to review that in GLPane.__getattr__. ###k
    
    k = dot(los, -self.pov - p1) / dot(los, p2 - p1)

    p2 = p1 + k*(p2-p1)
    return (p1, p2)

    
# working well: ease of trying a change: save and click!

# wishlist:

# archive of backcopies of this file (or diffs of that)
# (how fast to run shell diff each time it changes when we redraw? or md5, then copy it to its md5name?)
# (could do that in drawtest itself!)

# primitive layout expr - series of dy's between things to try out, enableable in MT

# (minor: archive screenshots too)

## courierfile = "/Users/bruce/PythonModules/data/courier-128.png"
courierfile = os.path.join( os.path.dirname(__file__), "experimental/textures/courier-128.png")

'''
()()
()()(8)
8888 -- there's one more pixel of vertical space between the chars, here in idlehack, than in my courier-128.png image file!
'''

# high-level helpers
def load_image_into_new_texture_name(image_file, tex_name = 0):
    """Allocate texture object in current GL Context (or use given one) (either way, return have_mipmaps, tex_name)
    and load image from file into it [what if wrong size??]
    """
    # took code from ESPImage
    image_obj = _create_PIL_image_obj_from_image_file( image_file)
    have_mipmaps, tex_name = _loadTexture(image_obj, tex_name)
    return have_mipmaps, tex_name

def setup_to_draw_texture_name(have_mipmaps, tex_name):
    "assume it's already set up"
    #e bind it
    glBindTexture(GL_TEXTURE_2D, tex_name)
    _initTextureEnv(have_mipmaps) # sets texture params the way we want them

    ## now you can: (from ESPImage._draw_jig, which before this did pushmatrix etc)
    ## drawPlane(self.fill_color, self.width, self.width, textureReady, self.opacity, SOLID=True, pickCheckOnly=self.pickCheckOnly)
    ##hw = self.width/2.0
    ##corners_pos = [V(-hw, hw, 0.0), V(-hw, -hw, 0.0), V(hw, -hw, 0.0), V(hw, hw, 0.0)]
    ##drawLineLoop(color, corners_pos)  
    return

# low-level helpers modified from ESPImage
# [note: some of these are called from exprs/images.py; others are copied & modified into it [bruce 061125]]

def _create_PIL_image_obj_from_image_file(image_file, **kws): # misnamed, see docstring; added kws, 061127
    """Creates and returns an nEImageOps object (using the given kws, documented in ImageUtils.py),
    which contains (and sometimes modifies in place) a PIL image object made from the named image file.
    """
    from ImageUtils import nEImageOps
    return nEImageOps(image_file, **kws)

def _loadTexture(image_obj, tex_name = 0): #e arg want_mipmaps
    """Load texture data from current image object; return have_mipmaps, tex_name (also leave that texture bound, BTW)"""
    # note: some of this code has been copied into exprs/images.py, class texture_holder [bruce 061125]
    ix, iy, image = image_obj.getTextureData() 

    # allocate texture object if necessary
    if not tex_name:
        tex_name = glGenTextures(1)
        print "debug fyi: testdraw._loadTexture allocated tex_name %r" % (tex_name,) # it's deprecated to let this happen much [070308]
        # note: by experiment (iMac G5 Panther), this returns a single number (1L, 2L, ...), not a list or tuple,
        # but for an argument >1 it returns a list of longs. We depend on this behavior here. [bruce 060207]
        tex_name = int(tex_name) # make sure it worked as expected
        assert tex_name != 0
    
    # initialize texture data
    glBindTexture(GL_TEXTURE_2D, tex_name)   # 2d texture (x and y size)

    glPixelStorei(GL_UNPACK_ALIGNMENT,1) ###k what's this?
    have_mipmaps = False
    ## want_mipmaps = debug_pref("smoother tiny textures", Choice_boolean_False, prefs_key = True)
    want_mipmaps = True
    if want_mipmaps: 
        gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGBA, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
        have_mipmaps = True
    else:
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
            # 0 is mipmap level, GL_RGBA is internal format, ix, iy is size, 0 is borderwidth,
            # and (GL_RGBA, GL_UNSIGNED_BYTE, image) describe the external image data. [bruce 060212 comment]
    return have_mipmaps, tex_name

# this gets us ready to draw (using coords in) a texture if we have it bound, i think
def _initTextureEnv(have_mipmaps): # called during draw method [modified from ESPImage] #e need smooth = False/True
    "have_mipmaps is boolean #doc"
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        # [looks like a bug that we overwrite clamp with repeat, just below? bruce 060212 comment]
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    if 0 and "kluge" and debug_pref("smoother textures", Choice_boolean_False, prefs_key = True): ###@@@ revise to param
        #bruce 060212 new feature (only visible in debug version so far);
        # ideally it'd be controllable per-jig for side-by-side comparison;
        # also, changing its menu item ought to gl_update but doesn't ##e
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        if have_mipmaps: #####@@@@@
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        else:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    else:
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    return

# ==

# (some outtakes removed to bruceG5 testdraw-outtakes.py, last here in rev 1.11)
# (lots more removed 070408, last here in rev 1.55)

# end
