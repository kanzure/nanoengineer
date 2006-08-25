# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
testdraw.py -- scratchpad for new code, OWNED BY BRUCE, not imported by default.

FOR NOW [060716], NO ONE BUT BRUCE SHOULD EDIT THIS FILE IN ANY WAY.

$Id$

[for doc, see testmode.py]

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

- DraggedOn and ReleasedOn are nim (and need renaming)

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
from debug import print_compact_stack, print_compact_traceback
import env
from idlelib.Delegator import Delegator

USE_DISPLAY_LIST_OPTIM = 0 # usually True, set False to see if this optim is causing bugs
    # also settable from glpane, but reloading breaks that, but if we fixed that, then editing it here would fail to also set it...
    # we could add code to let this be default only, but measure diff with prev to get a modtime,
    # compare to modtime of a manual change... ##e

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
purple = ave_colors(0.5, red, blue)

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
    vv.when_drawtest1_last_ran
    vv.state
except:
    vv = attrholder()
    vv.tex_name = 0
    vv.tex_data = None
    vv.counter = 0
    vv.displist = glGenLists(1)
    vv.havelist = 0
    vv.reload_counter = 0
    vv.when_drawtest1_last_ran = -1
    vv.state = {} # prototype of a place to store persistent state (presuming some persistent way of allocating keys, eg hardcoding)
    ##e should modify to make it easier to set up defaults; sort of like a debug_pref?

# vv.counter = 0 # just to get started (was needed when i moved file to another machine, already running, too)

# ==

print "\n%d reloads" % vv.reload_counter

if vv.havelist:
    vv.havelist = 0
    print "(fyi, this reload needed to reset vv.havelist)"
    
def Enter(glpane): # never yet called ###@@@ [still true??]
    glpane.win.setViewHome() # not tested, might be wrong; redundant now (if home view is the default)
    init_glpane_vars(glpane)

def init_glpane_vars(glpane):
    glpane._glnames = []
    glpane._testmode_stuff = []
    glpane._testmode_stuff_2 = []
    glpane._testmode_stuff_3 = []
    glpane._alpha = 1.0
    
def leftDown(self, event, glpane, super): # called from testmode.leftDown, just after it reloads this module (on empty-space clicks only)
    ###@@@ move reload condition into another func in this module? make it wait for leftUp and only if it didn't move, in empty space?
    "self is the mode, needed to call super.leftDown"
    ####@@@@ LOGIC BUG: when we reload, we replace one highlightable with a new one in the same place --
    # but don't replace selobj with the new one! So we predict not selobj_still_ok -- should print that from there ###@@@
    # [fixed now?]
    if printdraw: print "\ntestdraw leftDown" ###@@@
    vv.havelist = 0 # so editing this file (and clicking) uses the new code -- this also affects clicks on selobj which don't reload
    super.leftDown(self, event) # this might call testmode.emptySpaceLeftDown (or other class-specific leftDown methods in it)
    glpane.gl_update() # always, for now [might be redundant with super.leftDown, too]

def Draw(self, glpane, super): # called by testmode.Draw
    init_glpane_vars(glpane)
    vv.counter += 1
    glPushMatrix()
    try:
        drawtest0(glpane) # this puts some of our special drawing into a display list
        # [no point in putting the main model drawing into it, for now -- but when we can know when to inval, there might be]
    except:
        print_compact_traceback("exc ignored: ")
    glPopMatrix() # it turns out this is needed, if drawtest0 does glTranslate, or our coords are messed up when glselect code
    # [not sure what this next comment is about:]
    # makes us draw twice! noticed on g4, should happen on g5 too, did it happen but less??
    if 1 and 'draw_model':
        glPushMatrix()
        if 1:
            super.Draw(self) # needed for region selection's separate xor-drawing;
            # I suspect this is slower than the other case. Does it draw more than once (for glselect) or something like that? ####@@@@
        else:
            # region selection's drawing won't work in this case, though its selection op itself will work
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

def Draw_after_highlighting(self, pickCheckOnly, glpane, super):
    ## print "testdraw.Draw_after_highlighting(pickCheckOnly = %r)" % (pickCheckOnly,) # pickCheckOnly is True once when I click
    super.Draw_after_highlighting(self, pickCheckOnly)
    return

# ==

def havelist_counters(glpane):
    "return some counters which better have the same value or we'll treat havelist as if it was invalidated"
    assy = glpane.assy
    return (assy._view_change_counter,) # this doesn't work, since changing view doesn't actually incr that counter. ###@@@

def display_list_helper(self, glpane, drawfunc):
    "self needs .havelist and .displist"
    wantlist = USE_DISPLAY_LIST_OPTIM
    if wantlist and self.havelist == havelist_counters(glpane): ## == (disp, eltprefs, matprefs, drawLevel): # value must agree with set of havelist, below
        ##print "calllist (redraw %d)" % env.redraw_counter
        glCallList(self.displist)
    else:
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
            print_compact_traceback("exception ignored: ")

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
    "run drawtest1 inside a global display list, then run drawtest2 outside it"
    # load the texture for the courier bitmap font; params incl tex_name are in vv
    ensure_courierfile_loaded() # used to be done inside drawtest1

    vv.start_time = time.time() # drawing can use this to get time so far, but it's up to it to be drawn near the end of what we draw
    
    # drawtest1, in displist [vv has .havelist and .displist]
    drawfunc = lambda:drawtest1(glpane)
    display_list_helper( vv, glpane, drawfunc)

    # drawtest2, not in it
    drawtest2(glpane)
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

timing_data = {} # ok to zap on reload, code might change anyway (later, might be better to just mark entries as "old" then)

def drawtest2(glpane): # never in displist
    # draw some more useful and pretty text [used to show me redraw stats]
    #e should be more flexible text, at an abs location on screen; warning: slow if lots of text

    # get some timing stats
    timesofar = time.time() - vv.start_time
    timeflags = ""
    if env.redraw_counter == vv.when_drawtest1_last_ran:
        # this time is for making the dlist
        timeflags += 'd+'
    else:
        # it's for using it (faster, so 'minus')
        timeflags += 'd-'
    #e also flags for what we drew in drawtest1, and for whether selobj changed, etc

    timing_data[timeflags] = (env.redraw_counter, timesofar)

    items = timing_data.items()
    items.sort()
    msg = ""
    for flags, (redraw_counter, timesofar) in items:
        try:
            fps = int(1/timesofar)
            # note, timesofar doesn't include some (fixed?) overhead time after this point; still, higher means faster
        except:
            fps = -1
        if msg:
            msg += '\n'
        msg += "%s %4d (%4d fps)" % (flags, redraw_counter, fps)
    ## msg = "redraw %d\n(dlist %d)" % (env.redraw_counter, vv.when_drawtest1_last_ran)
    drawfont2(glpane, msg, charwidth = 18)

    try:
        glTranslate(0,1,0)
        we = displist_expr ## Overlay(Rect(1,1,green),displist_expr)
        we.draw()
    except:
        print_compact_traceback("exc ignored: ")
    pass

def drawtest1(glpane): # in displist (if flag for that is set)

    vv.when_drawtest1_last_ran = env.redraw_counter # so we see when displist gets updated
    
    glTranslatef(-9, 7, 0)
    dy = - 0.5

    # draw some lines
    
    ## drawline(color, pos1, pos2, dashEnabled = False, width = 1)
    drawline(red,   V(0,0,0),V(1,0,0),width = 2)
    glTranslatef( 0, dy, 0)
    drawline(green, V(0,0,0),V(2,0,0),width = 2)
    glTranslatef( 0, dy, 0)
    drawline(yellow,V(0,0,0),V(1,0,0),width = 2)

    # draw some text using builtin facility for that # MAYBE SLOW
    dothis = 0 # don't draw it - this speeds it up 
    
    ## def drawtext(text, color, pt, size, glpane)
    glTranslatef( 0, dy, 0)
    if dothis:
        drawtext("hi! (@[fg])", blue, V(0,0,0), 12, glpane)
    glTranslatef( 0, dy, 0)
    if dothis:
        drawtext("hi Mom...", white, V(0,0,0), 24, glpane) # ugly, but readable
    #drawtext("<b>hi Mom</b>", blue, V(0,0,0), 24, glpane) # html doesn't work, as expected
    # even \n doesn't work -- \n is a rectangle, \r is nothing, \t is single space.

    glTranslatef( 0, dy, 0.002) # 0.002 is enough to obscure the yellow line; 0.001 is not enough.

    # this used to be here:
        ##    # load the texture for the courier bitmap font; params incl tex_name are in vv
        ##    ensure_courierfile_loaded()

    # draw the whole font-texture??
    
    origin = ORIGIN
    dx = DX * 2
    dy = DY * 2
    # using a subrect eliminates the funny edges: tex_origin, tex_dx, tex_dy = V(0.1, 0.1), D2X * 0.8, D2Y * 0.8
    tex_origin, tex_dx, tex_dy = ORIGIN2, D2X, D2Y
    draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy)
##    ### what are coords in following??? replace it with better calls...
##    width = 32
##    textureReady = True
##    opacity = 1.0
##    drawPlane(blue, width, width, textureReady, opacity, SOLID=True, pickCheckOnly=False)

    if 0:
        # draw a blue rect for some reason [might obscure the text]
        draw_filled_rect(origin + 0.2*DZ + DX, dx, dy, halfblue) # note, it matters that dx/dy is right-handed.

##    Rect(1,1,red).draw() ####@@@@ not working
##    print "is it an Expr?",Rect(1,1,red),Rect(1,1,red).draw
##    return #####@@@@@@
    
    # draw 1 copy of testexpr, our test widget expr defined at end of file
    
    for i in range(1):
        glTranslatef( 0, -4, 0 )
        testexpr.draw() # it worked almost the first time!
    glTranslatef( 0, -8, -1 )

    return # drawtest1 #e rename

#e put these into an object for a texture font!
tex_width = 6 # pixel width in texture of 1 char
tex_height = 10 # guess (pixel height)

def drawfont2(glpane, msg = None, charwidth = None, charheight = None, testpattern = False):
    """draws a rect of chars using vv's font texture, in a klugy way;
    msg gives the chars to draw (lines must be shorter than charwidth or they will be truncated)
    """
    # adjust these guessed params (about the specific font image we're using as a texture) until they work right:
    tex_origin_chars = V(3,65) # guess was 0,64... changing y affects the constant color; try 0, not totally constant
    tex_size = (128,128) # guess
    tex_nx = 16
    tex_ny = 8

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
    
    ##pixelwidth = pixelheight = 0.05 * 2/3
    gap = 2 # in pixels - good for debugging
    gap = 0 # good for looking nice! but note that idlehack uses one extra pixel of vspace, and that does probably look better.
      # to do that efficiently i'd want another image to start from.
      # (or to modify this one to make the texture, by moving pixrects around)
    pixfactor = 1 # try *2... now i can see some fuzz... what if i start at origin, to draw?
        # did that, got it tolerable for pixfactor 2, then back to 1 and i've lost the niceness! Is it no longer starting at origin?

    # mousepoints
    p1junk, p2a = mymousepoints(glpane, 10, 10)
    p1junk, p2b = mymousepoints(glpane, 11, 10)
    px,py,pz = p2b - p2a # should be DX * pixelwidth
    ## print px,py,pz # 0.0313971755382 0.0 0.0 (in Ortho mode, near but not at home view, also at it (??))
        # 0.0313971755382 0.0 0.0 home ortho
        # 0.03139613018 0.0 0.0 home perspective -- still looks good (looks the same) (with false "smoother textures")
    pixelwidth = pixelheight = px * pixfactor
    # print "pixelwidth",pixelwidth
        ####@@@@ can be one of:
        #    0.0319194157846
        # or 0.0313961295259
        # or 0.00013878006302
    if pixelwidth < 0.01:
        pixelwidth = 0.0319194157846
        ### kluge, in case you didn't notice [guess: formula is wrong during highlighting]
        # but this failed to fix the bug in which a TextRect doesn't notice clicks unless you slide onto it from a Rect ####@@@@
    if pixfactor == 2:
        tex_origin_chars = V(3.5, 64.5) # 3.5 seems best, tho some shift to right; 3.55 through 3.75 are same, too much shift to left
    if pixfactor == 1:
        if "not starting at origin": # for pixfactor 1, to make it perfect, start where this does start... at origin doesn't yet work. 
            glTranslatef( 0, pixelheight / 2, 0 )
    
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
            draw_textured_rect(origin, dx, dy, tex_origin, ltex_dx, ltex_dy) # cool bug effect bfr 'l's here

    # draw some other ones? done above, with test string inside ff function.

    # interesting q -- if i use vertex arrays or displist-index arrays, can drawing 10k chars be fast? (guess: yes.)
    # some facts: this window now has 70 lines, about 135 columns... of course it's mostly blank,
    # and in fact just now it has about 3714 chars, not 70 * 135 = 9450 as if it was nowhere blank.
    # above we draw 9 * 16 = 144, so ratio is 3714 / 144 = 25, or 9450 / 144 = 65.
    # Try 65 redundant loops above & see what happens. It takes it a couple seconds! Too slow! Of course it's mostly the py code.
    # Anyway, it means we *will* have to do one of those optims mentioned, or some other one like not clearing/redrawing
    # the entire screen during most text editing, or having per-line display lists.

    return #drawfont2 #e rename, clean up

    
def mymousepoints(glpane, x, y): # modified from GLPane.mousepoints; x and y are window coords (y is 0 at top, positive as you go down)
    self = glpane
    just_beyond = 0.0
    p1 = A(gluUnProject(x, y, just_beyond))
    p2 = A(gluUnProject(x, y, 1.0))

    los = self.lineOfSight
    
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

def _create_PIL_image_obj_from_image_file(image_file):
    '''Creates and returns a PIL image object from image (png) file (i mean filename?). '''
    from ImageUtils import nEImageOps
    return nEImageOps(image_file)

def _loadTexture(image_obj, tex_name = 0): #e arg want_mipmaps
    '''Load texture data from current image object; return have_mipmaps, tex_name (also leave that texture bound, BTW)'''
    ix, iy, image = image_obj.getTextureData() 

    # allocate texture object if necessary
    if not tex_name:
        tex_name = glGenTextures(1)
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

def drawPlane(color, w, h, textureReady, opacity, SOLID=False, pickCheckOnly=False): # modified(?) from drawer.py
    '''Draw polygon with size of <w>*<h> and with color <color>. Optionally, it could be texuture mapped, translucent.
       @pickCheckOnly This is used to draw the geometry only, used for OpenGL pick selection purpose.'''
    vs = [[-0.5, 0.5, 0.0], [-0.5, -0.5, 0.0], [0.5, -0.5, 0.0], [0.5, 0.5, 0.0]]
    vt = [[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]    

    print "my drawplane"
    glDisable(GL_LIGHTING)
    glColor4fv(list(color) + [opacity])
    
    glPushMatrix()
    glScalef(w, h, 1.0)
    
    if SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glDisable(GL_CULL_FACE) 

    if not pickCheckOnly:
##        glDepthMask(GL_FALSE) # This makes sure translucent object will not occlude another translucent object
        # is this why it overwrote rendered text?? #### i guesas not, at least changing it didn't fix that 505p where i am
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
        if textureReady:
            glEnable(GL_TEXTURE_2D)  
            
    glBegin(GL_QUADS)
    for ii in range(len(vs)):
        t = vt[ii]; v = vs[ii]
        if textureReady:
            glTexCoord2fv(t)
        glVertex3fv(v)
    glEnd()
    
    if not pickCheckOnly:
        if textureReady:
            glDisable(GL_TEXTURE_2D)
        
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE) 
    
    glEnable(GL_CULL_FACE)
    if not SOLID:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    glPopMatrix()
    glEnable(GL_LIGHTING)
    return

# new LL helpers
def draw_textured_rect(origin, dx, dy, tex_origin, tex_dx, tex_dy):
    """Fill a spatial rect defined by the 3d points (origin, dx, dy)
    with the 2d-texture subrect defined by the 2d points (tex_origin, tex_dx, tex_dy)
    in the currently bound texture object.
    """
    glEnable(GL_TEXTURE_2D) 
    glBegin(GL_QUADS)
    glTexCoord2fv(tex_origin) # tex coords have to come before vertices, I think! ###k
    glVertex3fv(origin)
    glTexCoord2fv(tex_origin + tex_dx)
    glVertex3fv(origin + dx)
    glTexCoord2fv(tex_origin + tex_dx + tex_dy)
    glVertex3fv(origin + dx + dy)
    glTexCoord2fv(tex_origin + tex_dy)
    glVertex3fv(origin + dy)
    glEnd()
    glDisable(GL_TEXTURE_2D)

# Ideally we'd modularize the following to separate the fill/color info from the shape-info. (And optimize them.)
# For now they're just demos that might be useful.

def draw_filled_rect(origin, dx, dy, color):
##    print 'draw_filled_rect',(origin, dx, dy, color) #####@@@@@
    glDisable(GL_LIGHTING) # this allows the specified color to work. Otherwise it doesn't work (I always get dark blue). Why???
     # guess: if i want lighting, i have to specify a materialcolor, not just a regular color. (and vertex normals)
    if len(color) == 4:
        glColor4fv(color)
        if 0 and color[3] != 1.0:
            print "color has alpha",color ####@@@@
    else:
        glColor3fv(color)
##    glRectfv(origin, origin + dx + dy) # won't work for most coords! also, ignores Z. color still not working.
    glBegin(GL_QUADS)
    glVertex3fv(origin)
    #glColor3fv(white)#
    glVertex3fv(origin + dx)
    # glColor3fv(white) # hack, see if works - yes!
    #glColor3fv(color)#
    glVertex3fv(origin + dx + dy)
    #glColor3fv(white)#
    glVertex3fv(origin + dy)
    glEnd()
    glEnable(GL_LIGHTING) # should be outside of glEnd! when inside, i got infloop! (not sure that was why; quit/reran after that)

def draw_filled_triangle(origin, dx, dy, color):
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glBegin(GL_TRIANGLES)
    glVertex3fv(origin)
    glVertex3fv(origin + dx)
    glVertex3fv(origin + dy)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_filled_rect_frame(origin, dx, dy, thickness, color):
    "draw something that looks like a picture frame of a single filled color."
    tx = thickness * norm(dx)
    ty = thickness * norm(dy)
    glColor3fv(color)
    glDisable(GL_LIGHTING)
    glBegin(GL_QUAD_STRIP)
    glVertex3fv(origin)
    glVertex3fv(origin + tx + ty)
    glVertex3fv(origin + dx)
    glVertex3fv(origin + dx - tx + ty)
    glVertex3fv(origin + dx + dy)
    glVertex3fv(origin + dx + dy - tx - ty)
    glVertex3fv(origin + dy)
    glVertex3fv(origin + dy + tx - ty)
    glVertex3fv(origin)
    glVertex3fv(origin + tx + ty)
    glEnd()
    glEnable(GL_LIGHTING)
    
# == selobj interface

###e should define this; see class Highlightable --
# draw_in_abs_coords,
# ClickedOn/leftClick,
# mouseover_statusbar_message
# highlight_color_for_modkeys
# selobj_still_ok, maybe more

# == drag handler interface

class DragHandler:
    "document the drag_handler interface, and provide default method implems" # example subclass: class Highlightable
    ### how does this relate to the selobj interface? often the same object, but different API;
    # drag_handlers are retvals from a selobj method
    def handles_updates(self):
        """Return True if you will do mt and glpane updates as needed,
        False if you want client mode to guess when to do them for you
        (it will probably guess: do both, on mouse down, drag, up;
         but do neither, on baremotion == move, except when selobj changes)
        """
        return False # otherwise subclass is likely to forget to do them
    def DraggedOn(self, event, mode): ### might need better args (the mouseray, as two points? offset? or just ask mode  #e rename
        pass
    def ReleasedOn(self, selobj, mode): ### will need better args ### NOT YET CALLED  #e rename
        pass
    pass

# == widget exprs

class WidgetExpr(InvalMixin):
        # InvalMixin is for _get_ methods -- replace later with getter/setter properties in each one,
        # or maybe make those from _get_ methods once per class
##    bleft = 0
##    bbottom = 0
##    bright = 1 # reasonable default??
##    btop = 1
        # bright is bbox size on right, bleft on left (both positive or zero) #e rename, bright is a word
    def _get_bleft(self):
        return 0
    def _get_bbottom(self):
        return 0
    def _get_bright(self): # default is a _get_ method (formula) so it's overridable by another _get_ method
        return 1 # reasonable default??
    def _get_btop(self):
        return 1
    def __init__(self, *args, **kws):
        self.args = args #####@@@@@ maybe don't do this, but pass them to init, let it do it instead, into self.__args instead
        self.kws = kws
        try:
            self.init()
        except:
            print "info about exception in %r.init method: args = %r, kws = %r" % ( self, args, kws) #e use safe_repr for self
            raise
        return
    def init(self):
        pass
    def _get_width(self):
        return self.bright + self.bleft
    #e _get_height

    # helper methods (some really belong on other objects)
    def disable_color(self): ### really should be a glpane method
        "don't draw color pixels (but keep drawing depth pixels, if you were)"
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
        pass
    def enable_color(self):
        # nested ones would break, due to this in the inner one -- could be fixed by a counter, if we used them in matched pairs
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        pass
    def push_saved_names(self): # truer args would be: both glpane and transient_state object
        for glname in self.saved_glnames:
            glPushName(glname)
    def pop_saved_names(self):
        for glname in self.saved_glnames: # wrong order, but only the total number matters
            glPopName()
    pass

class DelegatingWidgetExpr(Delegator, WidgetExpr):
    def __init__(self, *args, **kws):
        WidgetExpr.__init__(self, *args, **kws)
        Delegator.__init__(self, self.args[0]) # usually same as args[0], but this way, init method can modify self.args[0] if it needs to
    pass

def _kluge_glpane():
    import env
    return env.mainwindow().assy.o
    
def PushName(glname, drawenv = 'fake'):
    glPushName(glname)
    glpane = _kluge_glpane()
    glpane._glnames.append(glname)
            ###e actually we'll want to pass it to something in env, in case we're in a display list ####@@@@
    return

def PopName(glname, drawenv = 'fake'):
    glPopName() ##e should protect this from exceptions
            #e (or have a WE-wrapper to do that for us, for .draw() -- or just a helper func, draw_and_catch_exceptions)
    glpane = _kluge_glpane()
    popped = glpane._glnames.pop()
    assert glname == popped
    return

class Highlightable(DelegatingWidgetExpr, DragHandler):#060722
    "Highlightable(plain, highlight) renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight"
    # Works, except I suspect the docstring is inaccurate when it says "plain plus highlight" (rather than just highlight), 
    # and there's an exception if you try to ask selectMode for a cmenu for this object, or if you just click on it
    # (I can guess why -- it's a selobj-still-valid check I vaguely recall, selobj_still_ok):
    #   atom_debug: ignoring exception: exceptions.AttributeError: killed
    #   [modes.py:928] (i.e. selobj_still_ok) [Delegator.py:10] [inval.py:192] [inval.py:309]
    #
##    __init__ = WidgetExpr.__init__ # otherwise Delegator's comes first and init() never runs
    def init(self, args = None):
        "args are what it looks like when plain, highlighted, pressed_in, pressed_out (really this makes sense mostly for Button)"
        self.transient_state = self # kluge, memory leak
        self.transient_state.in_drag = False # necessary (hope this is soon enough)
        if args is None:
            args = self.args # kluge, unless we do away with self.args as being too specific to which superclass we're talking about
        def getargs(plain, highlighted = None, pressed_in = None, pressed_out = None):
            "fill in our default args"
            if not highlighted:
                highlighted = plain # useful for things that just want a glname to avoid mouseover stickiness
            # this next stuff is really meant for Button -- maybe we split into two kinds, Button and Draggable
            if not pressed_in:
                pressed_in = highlighted # might be better to make it plain (or highlighted) but with an outline, or so...
            if not pressed_out:
                pressed_out = plain # assuming we won't operate then
            return plain, highlighted, pressed_in, pressed_out
        args = getargs(*args)
        self.plain, self.highlighted, self.pressed_in, self.pressed_out = args
        # get glname, register self (or a new obj we make for that purpose #e), define necessary methods
        glname_handler = self # self may not be the best object to register here, though it works for now
        self.glname = env.alloc_my_glselect_name(glname_handler)
            #e if we might never be drawn, we could optim by only doing this on demand
    def draw(self):
        self.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
            ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
            #e [if this (or any WE) is really a map from external state to drawables,
            #   we'd need to store self.glname and self.saved_modelview_matrix in corresponding external state]
        #e do we need to save glnames? not in present system where only one can be active. ###@@@
        PushName(self.glname)
        if self.transient_state.in_drag:
            if printdraw: print "pressed_out.draw",self
            self.pressed_out.draw() #e actually might depend on mouseover, or might not draw anything then...
        else:
            ## print "plain.draw",self
            self.plain.draw()
        PopName(self.glname)
    def draw_in_abs_coords(self, glpane, color):
        # [this API comes from GLPane behavior
        # - why does it pass color? historical: so we can just call our own draw method, with that arg (misguided even so??)
        # - what about coords? it has no way to know old ones, so we have no choice but to know or record them...
        # ]
        # restore coords [note: it won't be so simple if we're inside a display list which is drawn in its own relative coords...]
        ##glMatrixMode(GL_MODELVIEW) #k prob not needed
        glPushMatrix()
        glLoadMatrixd(self.saved_modelview_matrix)
        # examples of glLoadMatrix (and thus hopefully the glGet for that) can be found in these places on bruce's G4:
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/OpenGLContext/renderpass.py
        # - /Library/Frameworks/Python.framework/Versions/2.3/lib/python2.3/site-packages/VisionEgg/Core.py
        if self.transient_state.in_drag:
            if printdraw: print "pressed_in.draw",self
            self.pressed_in.draw() #e actually might depend on mouseover, or might not draw anything then...
        else:
            if printdraw: print "highlighted.draw",self
            self.highlighted.draw()
        glPopMatrix()
        return
    def __repr__(self):
        sbar_text = self.kws.get('sbar_text') or ""
        if sbar_text:
            sbar_text = " %r" % sbar_text
        return "<%s%s at %#x>" % (self.__class__.__name__, sbar_text, id(self))
    def mouseover_statusbar_message(self): # called in GLPane.set_selobj
        return self.kws.get('sbar_text') or "%r" % (self,)
    def highlight_color_for_modkeys(self, modkeys):
        """#doc; modkeys is e.g. "Shift+Control", taken from glpane.modkeys
        """
        return green
            # The specific color we return doesn't matter, but it matters that it's not None, to GLPane --
            # otherwise it sets selobj to None and draws no highlight for it.
            # (This color will be received by draw_in_abs_coords, but our implem of that ignores it.)
    def selobj_still_ok(self, glpane):
        ###e needs to compare glpane.part to something in selobj, and worry whether selobj is killed, current, etc
        # (it might make sense to see if it's created by current code, too;
        #  but this might be too strict: self.__class__ is Highlightable )
        # actually it ought to be ok for now:
        res = self.__class__ is Highlightable # i.e. we didn't reload this module since self was created
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None.
    ### grabbed from Button, maybe not yet fixed for here
    def leftClick(self, point, mode):
        self.transient_state.in_drag = True
        self.inval(mode)
        self.do_action('on_press')
        return self # in role of drag_handler
    def DraggedOn(self, event, mode):
        # only ok for Button so far
        #e might need better args (the mouseray, as two points?) - or get by callback
        # print "draggedon called, need to update_selobj, current selobj %r" % mode.o.selobj
        mode.update_selobj(event)
        #e someday, optim by passing a flag, which says "don't do glselect or change stencil buffer if we go off of it",
        # valid if no other objects are highlightable during this drag (typical for buttons). Can't do that yet,
        # since current GLPane code has to fully redraw just to clear the highlight, and it clears stencil buffer then too.

        # for dnd-like moving draggables, we'll have to modify the highlighting alg so the right kinds of things highlight
        # during a drag (different than what highlights during baremotion). Or we might decide that this routine has to
        # call back to the env, to do highlighting of the kind it wants [do, or provide code to do as needed??],
        # since only this object knows what kind that is.
        return
    
    def ReleasedOn(self, selobj, mode): ### will need better args
        ### written as if for Button, might not make sense for draggables
        self.transient_state.in_drag = False
        self.inval(mode)
        if selobj is self: #k is this the right selobj? NO! or, maybe -- this DH is its own selobj and vice versa
            self.do_action('on_release_in')
        else:
            self.do_action('on_release_out')
        ## mode.update_selobj(event) #k not sure if needed -- if it is, we'll need the 'event' arg
        #e need update?
        return
    
    def do_action(self, name):
        # print "do_action",name 
        action = self.kws.get(name)
        if action:
            action()
        return

    def inval(self, mode):
        """we might look different now;
        make sure display lists that might contain us are remade [stub],
        and glpanes are updated
        """
        vv.havelist = 0
        mode.o.gl_update()
        return
    
    pass # end of class Highlightable (a widgetexpr, and one kind of DragHandler)

# ==

def fix_color(color): # kluge #######@@@@@@@
    color = resolve_callables(color, 'fakeenv') ###e someday, most prims do this to most params...
    r,g,b = color # sanity check, though not a complete test of okness (if wrong, it can crash python) (support 4 elements?)
    glpane = _kluge_glpane()
    return r,g,b, glpane._alpha

class Rect(WidgetExpr): #e example, not general enough to be a good use of this name
    "Rect(width, height, color) renders as a filled rect of that color, origin on bottomleft"
    def init(self):
        self.bright = self.args[0]
        self.btop = self.args[1]
        self.color = self.args[2] # or dflt color? note, it might be symbolic
        #e let arg 2 or 3 be more drawable stuff, to center in the rect?
        #e if color None, don't draw it, just the stuff?
    def draw(self):
        glDisable(GL_CULL_FACE)
##        print "drawing Rect",self.args ####@@@@
        ### -- what could we print to indicate *which subexpr* we're drawing? esp which DebugDraw subexpr?
        # once we have a drawing env, it should have an attr for whether to print debug info like this
        # and its "address" or other sort of "posn in state".
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

class TextRect(WidgetExpr):
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

class RightTriangle(Rect):
    "RightTriangle(width, height, color) renders as a filled right triangle, origin and right-angle corner on bottomleft"
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_triangle(ORIGIN, DX * self.bright, DY * self.btop, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

class IsocelesTriangle(Rect):
    "IsocelesTriangle(width, height, color) renders as a filled upright isoceles triangle, origin on bottomleft"
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_triangle(ORIGIN, DX * self.bright, DY * self.btop + DX * self.bright * 0.5, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

class RectFrame(WidgetExpr):
    """RectFrame(width, height, thickness, color) is an empty rect (of the given outer dims)
    with a filled border of the given thickness (like a picture frame with nothing inside).
    """
    def init(self):
        #e improve arglist
        self.bright = self.args[0]
        self.btop = self.args[1]
        try:
            self.thickness = self.args[2]
        except:
            self.thickness = 4
        try:
            self.color = self.args[3]
        except:
            self.color = white
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect_frame(ORIGIN, DX * self.bright, DY * self.btop, self.thickness, fix_color(self.color))
        glEnable(GL_CULL_FACE)
    pass

class Invisible(DelegatingWidgetExpr):
    """Invisible(thing) has size and hit-test behavior like thing (for use in Highlighting),
    but is not visible and does not visually obscure anything.
    (Implem note: it has to be drawn at the end, but arbitrary order among all invisibles is ok.)
    Note that thing's syntax might still require you to specify a color; which one you specify doesn't matter.
    """
    def draw(self):
        glpane = _kluge_glpane()
        # arrange to do it later... save the matrix
        self.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX )
        self.saved_glnames = tuple(glpane._glnames)
        glpane._testmode_stuff.append(self.draw_later) # assumes self has all the needed data
        # see also code in renderpass about how to sort by depth
        # but what if we're in a display list? well, we better not be... this aspect is nim too
        # self.draw_later() # this fixed the bug, made it highlight again
    def draw_later(self):
        # print "draw_later called" # only works when we disable USE_DISPLAY_LIST_OPTIM
        glPushMatrix()
        glLoadMatrixd(self.saved_modelview_matrix)
        self.push_saved_names()
        if 1:
            self.disable_color() # don't draw color pixels (but keep drawing depth pixels)
            if 1:
                self.delegate.draw()
            self.enable_color()
                # WARNING: nested Invisibles would break, due to this in the inner one -- could be fixed if we used them in matched pairs
                # WARNING: better not do this when drawing a highlight!
        self.pop_saved_names()
        glPopMatrix()
        return
    pass

class Translucent(DelegatingWidgetExpr):
    """Translucent(thing, alpha) has size and hit-test behavior like thing (for use in Highlighting),
    but is tranlucent.
    (Implem note: it has to be drawn at the end; in principle it should be depth-sorted, but this might be nim.)
    """#######@@@@@@ UNFINISHED CODE HERE
    def draw(self):
        glpane = _kluge_glpane()
        # arrange to do it later... save the matrix
        self.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX )
        self.saved_glnames = tuple(glpane._glnames)
        glpane._testmode_stuff_2.append(self.draw_later_1) # assumes self has all the needed data
        glpane._testmode_stuff_3.append(self.draw_later_2)
        # see also code in renderpass about how to sort by depth
        # but what if we're in a display list? well, we better not be... this aspect is nim too
        # self.draw_later() # this fixed the bug, made it highlight again
    def draw_later_1(self):
        "pass 1 - draw the colors (don't modify the depth buffer)"
        # we need these two passes if they are not sorted or imperfectly sorted --
        # first draw the colors, then draw the depths
        #
        # probably this only works when we disable USE_DISPLAY_LIST_OPTIM ####@@@@        
        glPushMatrix()
        glLoadMatrixd(self.saved_modelview_matrix)
        self.push_saved_names()
        if 1:
            ### wish we could change alpha factor globally; the supposed way didn't work (see comments elsewhere)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glDepthMask(GL_FALSE)
            if 1:
                glpane = _kluge_glpane()
                glpane._alpha = 0.1 ####@@@@ stub: use arg1; have a stack or save the old value
                    # bug: not translucent, but this does affect the color, as if there was a white bg.
                    # IS IT THE HIGHLIGHT DRAWING DOING THIS?
                self.delegate.draw()
                glpane._alpha = 1.0
                ######@@@@@@@ change this to use alpha in color, unless we can get CONST_ALPHA to work
            glDisable(GL_BLEND)
            glDepthMask(GL_TRUE)
        self.pop_saved_names()
        glPopMatrix()
        return
    def draw_later_2(self):
        "pass 2 - draw the depths"
        glPushMatrix()
        glLoadMatrixd(self.saved_modelview_matrix)
        self.push_saved_names()
        if 1:
            self.disable_color()
            if 1:
                self.delegate.draw()
            self.enable_color()
        self.pop_saved_names()
        glPopMatrix()
        return
    pass

# ==

class Overlay(DelegatingWidgetExpr):
    "Overlay has the size of its first arg, but draws all its args in the same place, with the same origin."
    def draw(self):
        for a in self.args[::-1]:
            #e We'd like this to work properly for little filled polys drawn over big ones.
            # We might need something like z translation or depth offset or "decal mode"(??) or a different depth test.
            # Different depth test would be best, but roundoff error might make it wrong...
            # This is definitely needed for overdrawing like that to work, but it's low priority for now.
            # Callers can kluge it using Closer, though that's imperfect in perspective mode (or when viewpoint is rotated).
            # But for now, let's just try drawing in the wrong order and see if that helps... yep!
            if a is None:
                continue # even for first arg -- but that being None would fail in other ways, since it'd be our delegate
            a.draw() #e try/except
    pass # Overlay

def printmousepos():
    glpane = _kluge_glpane()
    self = glpane
    # this code is copied from GLPane.timerEvent as of 060823 (I wonder if it needs makeCurrent to work properly?)
    cursor = self.cursor()
    cursorPos = self.mapFromGlobal(cursor.pos()) # mapFromGlobal() maps from screen coords to GLpane coords.
    ## xy_now = (cursorPos.x(), cursorPos.y()) # Current cursor position
    # consistent with x,y = 0,0 being top left, but not tested precisely; note, gluProject uses 0,0 = bottom left (y is reversed)
    # so fix that:
    xy_now = (cursorPos.x(), self.height - cursorPos.y())
    print "mousepos:", xy_now

class DebugDraw(DelegatingWidgetExpr):
    """DebugDraw(widget, name) draws like widget, but prints name and other useful info whenever widget gets drawn.
    Specifically, it prints "gotme(name) at (x,y,depth)", with x,y being mouse posn as gluProject returns it.
    (It may print nonsense x,y when we're drawn during glSelect operations.)
    Once per event in which this prints anything, it prints mousepos first.
    If name is 0 or -1 or None, the debug-printing is disabled.
    """
    def draw(self):
        # who are we?
        who = who0 = ""
        if len(self.args) > 1:
            who0 = self.args[1]
            who = "(%s)" % (who0,)
        if (who0 is not None) and who0 != 0 and who0 != -1:
##            # print "who yes: %r" % (who,), (who is not None), who != 0 , who != -1, 0 != 0
            if env.once_per_event('DebugDraw'):
                try:
                    printmousepos()
                except:
                    print_compact_traceback("ignoring exception in printmousepos(): ")
            # figure out where in the window we'd be drawing right now [this only works if we're not inside a display list]
            x,y,depth = gluProject(0,0,0)
            msg = "gotme%s at %r" % (who, (x,y,depth),)
            ## print_compact_stack(msg + ": ")
            print msg
##        else:
##            print "who no: %r" % (who,)

        self.delegate.draw()
    pass

class Row(WidgetExpr):
    "Row" # note: this is only well-defined if we assume we know how to move to the right, and that "width" works that way!
    def draw(self):
        # compute layout -- redo each time
        # widths = [a.width() for a in self.args]
        gap = self.kws.get('gap',0)
        glPushMatrix()
        pa = None
        for a in self.args:
            if a is None:
                continue
            if pa is not None:
                dx = pa.bright + a.bleft + gap
                glTranslate(dx,0,0)
            pa = a # for next loop
            a.draw() #e try/except
            ## dx = a.width() # should we assume this is only available after drawing (as optim, permit computing it then)? NO!
                # some callers will need it before.
                # should it be an attr, can be invalled, otherwise more efficient? probably yes. ####@@@@
                # but then a Row needs to subscribe to arg widths, or if it can't, needs to always recompute. (use a Property)
                # this is wrong: we want a0.rightwidth() + a1.leftwidth(). (bbox elements; assuming origin inside)
        glPopMatrix()
    def _get_width(self): # inefficient, need inval/update
        if not len(self.args):
            return 0
        w = self.kws.get('gap',0) * (len(self.args) - 1) # wrong if no args!
        for a in self.args:
            w += a.width
        return w
    def _get_bleft(self):
        if not len(self.args):
            return 0
        return self.args[0].bleft
    def _get_bright(self):
        return self.width - self.bleft
    def _get_btop(self):
        return max([a.btop for a in self.args])
    def _get_bbottom(self):
        return max([a.bbottom for a in self.args])
    pass # Row

class Column(WidgetExpr):
    "Column" # see notes for Row; this is like Row except left,right,width <-> top,bottom,height, and glTranslate is changed
    def draw(self):
        # compute layout -- redo each time
        gap = self.kws.get('gap',0)
        glPushMatrix()
        pa = None
        for a in self.args:
            if a is None:
                continue
                ###@@@ should do this more generally (for other WEs), but maybe not for all WE arglists, not sure;
                # note that for Overlay, it only makes sense for args after the first one;
                # note that we are not yet handling well the case of all Column args being None, unless
                # (by accident) we already handle the 0-arg case well (untested, unthoughtabout).
            if pa is not None:
                dy = pa.bbottom + a.btop + gap
                glTranslate(0,-dy,0) 
            pa = a # for next loop
            a.draw() #e try/except
            ## dx = a.height() # should we assume this is only available after drawing (as optim, permit computing it then)? NO!
                # some callers will need it before.
                # should it be an attr, can be invalled, otherwise more efficient? probably yes. ####@@@@
                # but then a Row needs to subscribe to arg heights, or if it can't, needs to always recompute. (use a Property)
                # this is wrong: we want a0.bottomheight() + a1.topheight(). (bbox elements; assuming origin inside)
        glPopMatrix()
    def _get_height(self): # inefficient, need inval/update
        if not len(self.args):
            return 0
        w = self.kws.get('gap',0) * (len(self.args) - 1) # wrong if no args!
        for a in self.args:
            w += a.height
        return w
    def _get_btop(self):
        if not len(self.args):
            return 0
        return self.args[0].btop
    def _get_bbottom(self):
        return self.height - self.btop
    def _get_bleft(self):
        return max([a.bleft for a in self.args])
    def _get_bright(self):
        return max([a.bright for a in self.args])
    pass # Column

# ==

class Closer(DelegatingWidgetExpr):
    "Closer(thing, amount)"
##    __init__ = WidgetExpr.__init__ # otherwise Delegator's comes first and init() never runs
    def init(self):
        self.args = list(self.args) + [1] # default amount
        self.thing = self.args[0] # or use self.delegate
        self.amount = self.args[1]
##        Delegator.__init__(self, self.thing) # for defns like bright, bleft
    def draw(self):
        glTranslate(0, 0, self.amount)
        self.thing.draw()
        glTranslate(0, 0, -self.amount)
        return
    pass

class Rotated(DelegatingWidgetExpr):
    """Rotated(thing) has the same width and height as thing, but is drawn rotated CCW by a given number of degrees
    around the center of the width/height rectangle.
       Note: if the width and height differ, and you rotate it by 90 degrees, they are *not* swapped;
    it won't fit in them, if it filled them before. This is not an error, and indeed, it's true at the corners
    for any rotation angle.
    """
    #e would it be better to list angle first, and let the rest of the args be an implicit Overlay?
    #e would it be better to calculate width and height to enclose a rotated filled rect of the arg size?
    def init(self):
        self.args = list(self.args) + [45] # default angle
        self.thing = self.args[0] # or use self.delegate?
        self.amount = self.args[1]
    def draw(self):
        try:
            (self.bright - self.bleft)/2.0, (self.btop - self.bbottom)/2.0
        except:
            print "data related to following exception:",self.bright,self.bleft,self.btop, self.bbottom
            print_compact_traceback()
            return
        glPushMatrix()
        glTranslate((self.bright - self.bleft)/2.0, (self.btop - self.bbottom)/2.0, 0)
        glRotate(self.amount, 0,0,1)
        glTranslate(-(self.bright - self.bleft)/2.0, -(self.btop - self.bbottom)/2.0, 0)
        self.thing.draw()
        glPopMatrix()
    pass
# ==

class Corkscrew(WidgetExpr):
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

# ==

def dictset(lis):
    return dict([(e,e) for e in lis])
dset = dictset

def conn(a,b): return (a,b) #stub

def eg2():
    places = dictset([(i,j) for i in range(10) for j in range(10)])
    # xconns = dset([conn((x,y),(x+1,y)) for (x,y) in places]) # how do we also say 'if x < 10-1'?
    xconns = []
    for (x,y) in places:
        if x < 10-1:
            xconns.append(conn((x,y),(x+1,y)))
    yconns = []
    for (x,y) in places:
        if y < 10-1:
            yconns.append(conn((x,y),(x,y+1)))
    print len(xconns)
    # at each place, a cube
    # group by xconns (into strips)
    # draw...


# grid - has the set of points, the navigation functions, the paths, the set of vectors along edges, etc...
# these can all be methods on the elts, and functions coming out of the grid object
#   then we give names to various other sets of interesting features of the egg-carton-like thing we envision
#   and ops on them, code to make them, to map them between each other & other sets; how to extend a sym on grid to a sym on them
# (easy if we define them as a tuple of gridobjs which satisfy some relations, plus other params that stay constant;
#  but how to we say the class of ops we're defining on them?)

eg2()

# ==

debug_color_override = 0

class Ribbon(Corkscrew):
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

class Ribbon2(Ribbon): ##, Atom): ####@@@@ class Atom - hack kluge experiment - had no noticable effect - i guess it wouldn't...
                                    # the selobj is not this, but the Highlighted made from it
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

# Ribbon2 has: radius, axis (some sort of length - of one bp?), turn (angle??), n, color1, color2, and full position/orientation
# and it will have display modes, incl cyl with helix/base/groove texture, and flexible coloring;
# and ability to show the units in it, namely strands, or basepairs, or bases (selected/opd by type)
# and for us to add cmd bindings like "make neighbor strand" (if room) or "make crossover here" (maybe only on a base?)

# but as a first step, we can select it as a unit, copy/paste, deposit, move, etc.
# In this, it is sort of like an atom or set of co-selected atoms... some relation to chunk or jig too.
# I'd get best results by letting it be its own thing... but fastest, by borrowing one of those...

# ==

# not sure if anything in here is non-obs, tho If is used

def printfunc(*args): #e might be more useful if it could take argfuncs too (maybe as an option); or make a widget expr for that
    def printer(_guard = None, args = args):
        assert not _guard # for now
        print args
    return printer

##k are these obs?
# define these, once i'm satisfied they make sense ####@@@@
#__ - ok
#Sensor
#Overlay
#Local
#If

# for a newer Symbol, see testdraw2
##class Symbol:
##    def __init__(self, data = ('prim')):
##        self.data = data
##    def __getattr__(self, attr):
##        if attr.startswith('_'):
##            raise AttributeError, attr
##        return Symbol(('attr', attr, self)) # or could use AttrSymbol; could call this Expr or PyLikeExpr or PyExpr
##    def eval(self, env):
##        if self.data[0] == 'attr': # assume data[0] is like the subclass of Symbol
##            junk, attr, base = self.data
##            return getattr(base.eval(env), attr)
##        # otherwise assume primitive
##        return env # for now
##    pass
##
##__ = Symbol()

# I don't think Local and If can work until we get WEs to pass an env into their subexprs, as we know they need to do ####@@@@

# If will eval its cond in the env, and delegate to the right argument -- when needing to draw, or anything else
# Sensor is like Highlightable and Button code above
# Overlay is like Row with no offsetting
# Local will set up more in the env for its subexprs
# Will they be fed the env only as each method in them gets called? or by "pre-instantiation"?

##def Button(plain, highlighted, pressed_inside, pressed_outside, **actions):
##    # this time around, we have a more specific API, so just one glname will be needed (also not required, just easier, I hope)
##    return Local(__, Sensor( # I think this means __ refers to the Sensor() -- not sure... (not even sure it can work perfectly)
##        0 and Overlay( plain,
##                 If( __.in_drag, pressed_outside),
##                 If( __.mouseover, If( __.in_drag, pressed_inside, highlighted )) ),
##            # what is going to sort out the right pieces to draw in various lists?
##            # this is like "difference in what's drawn with or without this flag set" -- which is a lot to ask smth to figure out...
##            # so it might be better to just admit we're defining multiple different-role draw methods. Like this: ###@@@
##        DrawRoles( ##e bad name
##            plain, dict(
##                in_drag = pressed_outside, ### is this a standard role or what? do we have general ability to invent kinds of extras?
##                mouseover = If( __.in_drag, pressed_inside, highlighted ) # this one is standard, for a Sensor (its own code uses it)
##            )),
##        # now we tell the Sensor how to behave
##        **actions # that simple? are the Button actions so generic? I suppose they might be. (But they'll get more args...)
##    ))

class Ifbad(DelegatingWidgetExpr):
    def init(self, args): #####@@@@@ IMPLEM new init API, receives args
        if len(args) == 2:
            self.cond, self.then = args
            self.else_ = None # .else is not allowed, since else is a keyword
        else:
            self.cond, self.then, self.else_ = args
        self._delegate = self.then # override the default choice of what to pass to our super's upcoming Delegator.__init__ #####@@@@@ IMPLEM
        ###e is that correct, or should we eval cond? problem: we can't eval it until we know an env.
        # maybe the correct delegate until then is None? ###k
        return
    ###e now we want all methods, not indiv ones, to use a computed delegate.
    # note that Delegator caches... we need to know when delegate changes...
    # it won't ask us, we have to either subscribe, or be told explicitly.
    #######@@@@@@ Hmm...
    pass

def resolve_callables(thing, env, pred = None):
    """While thing is a callable (which does not satisfy pred, if given (typically a type-checker) -- good feature??),
    apply it to env, and repeat. Return the first non-callable result,
    optionally asserting it satisfies pred.
    """
    #e might want to also allow pred to be a list or tuple, a class or type, etc (see what isinstance will take)
    while callable(thing) and (pred is None or not pred(thing)):
        thing = thing(env)
    if pred is not None:
        assert pred(thing)
    return thing

class If_:
    "If(cond, then, [else]), when cond is a function"
    def __init__(self, cond, then, else_ = None):
        self.args = cond, then, else_ # any of these might be constants or callables -- worry when they're used
    def __call__(self, *args):
        print "call got args",args
        ###IMPLEM - this gets called with env, by resolve_callables, i think...
        ### maybe it can also be called with some options, as mods... maybe this will turn out to have a superclass handle that,
        # and handle buildup of .attr +number etc which can't run until env gets supplied (.attr is the only one really needed,
        # so this can delegate methodcalls to different objects)

        # skeptical. if someone says obj.draw, didn't they already resolve obj with env? if so, it's easy.,
        # jus handle getting env, no need for getattr, it might assertfail.
        # higher level exprs containing us will know to resolve us with env.
    #e also need __repr__, maybe more
    #e __setattr__? arithmetic??
    def __getattr__(self, attr):
        if attr.startswith('_'):
            raise AttributeError, attr
        # delegate to then or else_, according to cond (whether value is a bound method or a constant)
        # don't resolve_callables in then or else_, let caller or themselves do that [I think #k]
        cond, then, else_ = self.args
        print "kluge, will fail: using global env in If_.__getattr__"
        cond = resolve_callables(cond, env) ###### how do we know env??? hmm... LOGIC BUG #####@@@@@@ [can it be dynamic???]
        ### or, do we save up the chain of attrs (like Symbol), then wait til we get passed env by resolve_callables ????
        cond = not not cond
        clause = (else_, then)[cond]
        if clause is not None:
            return getattr(clause, attr)
        return None
    pass

def If(cond, then, else_ = None):
    if callable(cond):
        return If_(cond, then, else_)
    cond = not not cond
    clause = (else_, then)[cond]
    # often a constant; if a function, let the caller resolve it when it wants to
    # (which might not be now, and we don't know env anyway)
    return clause 

# ==

Button = Highlightable

Pass = Rect(0,0,white) # seems to work (draws nothing) (not fully tested)

def FilledSquare(fillcolor, bordercolor, size = 0.5, thickness_ratio = 0.05):
    return Overlay( Rect(size, size, fillcolor),
                    RectFrame(size, size, size * thickness_ratio, bordercolor)
    )

# kluge to test state toggling:

def bcolor(env, nextness = 0):
    n = vv.state.setdefault('buttoncolor',0)
    return (green, yellow, red)[(n + nextness) % 3]

def next_bcolor(env):
    return bcolor(env, 1)

def toggleit():
    n = vv.state.setdefault('buttoncolor',0)
    n += 1
    n = n % 3
    vv.state['buttoncolor'] = n
    return

def getit(fakeenv): # note: the bug of saying getit() rather than getit in an expr was hard to catch; will be easier when env is real
    return "use displist? %s" % ('no', 'yes')[not not USE_DISPLAY_LIST_OPTIM]

def setit(val = None):
    global USE_DISPLAY_LIST_OPTIM
    if val is None:
        # toggle it
        val = not USE_DISPLAY_LIST_OPTIM
    USE_DISPLAY_LIST_OPTIM = not not val
    vv.havelist = 0
    print "set USE_DISPLAY_LIST_OPTIM = %r" % USE_DISPLAY_LIST_OPTIM

displist_expr_BUGGY = Button(Row(Rect(0.5,0.5,black),TextRect(18, 2, getit)), on_press = setit)
    # works, but has bug: not sensitive to baremotion or click on text if you drag onto it from empty space,
    # only if you drag onto it from the Rect.
    
displist_expr = Row(
    Button( Rect(0.5,0.5,black), DebugDraw( Rect(0.5,0.5,gray), "grayguy"), on_press = setit),
    TextRect(18, 2, getit))


### testexpr was here

# try a simpler type. a tile, easy ways to attach near ones.
# a tile has pos/orient, size, color. like a Rect, really. RectParams. Do we say this? Or just write code to use & set them?
# How do we make one? Constructor of data expr?

#e define("Tile") ? note, we might keep remaking the class of commands/methods, but the data itself lives elsewhere...
# might be a Node or more likely an AtomLike.

class Tile(WidgetExpr): pass # stub, just so no syntax error below

tile1 = Tile(color = green) # standard options for pos/orient, membership in larger things, tags...

def draw_tile(self, mods, env): # nim
    width, height, color = 'stub'
    Rect(width, height, color).draw() # or use Rect.draw? that requires a real Rect, flyweight or cached.
    #e and some bindings; Highlightable; cache a drawable for it?

class MethodRunClass:pass

class Tile(MethodRunClass):
    "data and method defs useful for showing and editing Tiles" # reloads, but their state stays... it's stored as a superclass??
    def _CM_make_neighbor(self):
        "show transparent neighbor tiles (in empty positions), with some way to make one of them (submenu items? mouse up?)"
        #e can we show them just while a certain menuitem is up, so as we scan submenu, we see the options?
        # surely yes if the submenu is displayed as a 3d object... or just display them and let clicked ones become real...
        # maybe display lots of them at once... maybe let them be selected even before they are real, with cmenu on selection
        # to make them real. yes, that sounds flexible, good whenever the set of positions to extend is often deterministic.
        pass
    pass

from Utility import SimpleCopyMixin, Node, imagename_to_pixmap, genViewNum

class TestNode(Node, SimpleCopyMixin): # see TestNode.py... not yet more than a stub... see also DebugNode
    """Abstract class for a kind of Node it's easy to experiment with.
    Just make sure the subclass does the stuff needed by SimpleCopyMixin,
    and that all the attrs can be saved as info records in a simple way by the code herein --
    or maybe we'll save them in a Files Directory shelf instead? Not sure yet.
    """
    def draw(self, glpane, dispdef):
        "Use our subtype to find some rules in a widget expr..."
        # some WE is sitting there in the mode, knowing how to draw things for it...
        # so we ask it...
        # maybe it got passed to this method? ideally as dispdef, but that would break old code...
        # so simplest way is as a dynamic glpane attr, and this is tolerable until we have a chance to clean up all Node draw methods.
        pass
    pass
        
# (some outtakes removed to bruceG5 testdraw-outtakes.py, last here in rev 1.11)

### btw i decided not to use env in these lambdas -- too likely to be confusing re global env. didn't yet decide what to use instead.

# e.g.:
some_color_arg = red
some_color_arg = If( lambda env: env.lighter_blob_colors, pink, red )
some_color_arg = lambda env: env.color_for_type(env.thisAtom.type)
some_color_arg = If( lambda env: env.thisAtom.doingdrag, pink, red)
some_color_arg = lambda env: env.prefs[if_(env.thisAtom.doingdrag, key1, key2)]
# or could we overload If for this (boolean or func arg)??
#   >>> map(callable, [0,1,True,False,None,""])
#   [False, False, False, False, False, False]
# yes.
some_color_arg = lambda env: env.prefs[If(env.thisAtom.doingdrag, key1, key2)]

# ==

def Stub(*args,**kws): pass

Menu = MItem = Stub
Wirebox = Stub
DragBinding = Stub

WE_for_atom_cmenu = Menu(
    MItem("item1", Stub('command1'))
)

WE_for_atom_wirebox = Stub(#for each atom, with state or params of a kind we imply here, here is what to draw using that state
    Wirebox(black, 2.0) # give size & color & linethickness; it's centered on the atom by default, as is anything we draw here
)

# "potential" objects show as very translucent gray; "desired" objects as less-translucent color; "real" objects as solid color.
# objects being specifically offered (among a few alternatives) might be in between potential and desired, somehow.
# this applies to cyls/helices, crossovers, maybe other things. [until translucent works, use wireframes for that.]
# [keep our own stacks of glstate on the glpane, so we can restore prior one when we pop it, and copy them into draw_later code.
#  not clear how it'll interact with display lists.]

Cylinder = Stub( # much like Ribbon2; we really ought to name it Helix or DoubleHelix or DNACylinder
    # it has: enough to draw the helices and know where the potential bases are; interrelated geom variables
    # (they all have values, and there are set methods that keep them consistent; much of details of that are general but unknown)
    # (maybe you set them, leaving them inconsistent, then adjust others by name (1 or a few), making them consistent by formulas)
    
    # like any model object, it can have indiv display mode, tags, attached/sub objects, etc
    # the way it interfaces -- it can live within a raster (which can give it potential crossovers),
    # or it can get some from being in same 3d space as other cyls
    # (or maybe, other real strands -- anything offering dna-bps or cps (crossover points))

    # also like any model object, it has params (and its existence) getting saved, so it has a place in mmp file, a place in MT, etc,
    # which means it needs "creation operators", which can be by paste (copy), command with params, or creating a raster of them;
    # for prototype, just let it have an id to index state, and keep state anywhere, and pass id or state obj to methods
    # or use in creating transient-state objs...

    twist = 30, # need to look these up
    rise = 3.4,
    pitch = 10.5,
)

WE_for_dragging_strands_within_cyls = Stub(
    DragBinding(
        #e on what kind of thing? 
        # (what we bind it on can be a thing we're already drawing, described at any level,
        #  and this modifies the drawing/selobj code;
        #  or a drawable kind of place, like grid faces, even if we don't yet draw into it.)

        #e for what kinds of tools? this might depend on where we put this expr, not on the expr itself...
        #e with what doc, highlight, cursor, before it happens?

        # relates to cyls, their baseposns, seams, ends of strands... for the strand-path tool.
        # so we might find a strand to extend (or add a loop to), or find a base to start a new strand at,
        # and then, it's really the strand-end we're dragging, and the other objects (potential cyls, potential crossovers)
        # see us dragging a strand-end with some tool (& options), as they decide how to respond to that for highlight, action, etc.
        
        #e what happens as it runs: start, move, end (some of this can depend on what it's over, have overrides/defaults, etc)?
        start = Stub(),# a WE which runs in an env that includes all of this, plus info avail when we start, like posn and modkeys
        move = Stub(), # gets state from the prior event too; decide what things we moved over, change their state
            # simplest that could work: assume motion was small; see if on same or nearby cyl; find crossover it crossed; ...
            # exercise, for bitmap editor: find a path of pixels approximating a line. (not approp. in this case)
            # in this case: do a fill, guided by seams and target point. fill alg: in cyl we'll leave, pick best place --
            # as far as we can in known dir, based on seams & crossover. we either stop, or leave thru some (potential) crossover;
            # it decides direction in new cyl. so some of this is a per-cyl method -- this event sets up an env, then iterates
            # through objects which finish or which pass the buck to more objects, while growing a "path object" we're extending.
            # (initial click created one, or was on/near end of one (on an obj we drew there, marking end) and is extending it.)
        end = Stub()
    )
)

import testdraw2
reload(testdraw2)
from testdraw2 import *

# the code snippets need names for:
# - built ins
# - locals from surrounding WE's or maybe dynamically-surrounding helper-class method calls (or locals in same method)
# - dynamics (eg the ongoing drag, its start, the prior event in it)
# - the thing we're showing
# - the env and prefs
# - the glpane

# when they are in a class, it's so a set of methods know the others are there, but are sometimes overridable by name;
# it's convenient to call them with mods... which are probably mods to per-call vars anyway...
# they might be mods like color = red, or color_formula = F, which apply to various params, of the thing being drawn, etc...

"""testexpr is sort of like an experimental toplevel rendering loop,
since it doesn't refer to model state except in whatever way it says so internally.
"""

## testexpr = DebugDraw(Rect(1,1,purple), 1 and "d1")
testexpr = Row(
    #nim Button:
                Button(
                    ## Invisible(Rect(1.5, 1, blue)), # works
                    Translucent(Rect(1.5, 1, blue)), # has bug
                    Overlay( Rect(1.5, 1, lightgreen), (IsocelesTriangle(1.6, 1.1, pink))),
                        ####@@@@ where do I say this? sbar_text = "button, unpressed"
                        ##e maybe I include it with the rect itself? (as an extra drawn thing, as if drawn in a global place?)
                    IsocelesTriangle(1.5, 1, green),
                    IsocelesTriangle(1.5, 1, yellow),#e lightgreen better than yellow, once debugging sees the difference
                        ####@@@@ sbar_text = "button, pressed", 
                    # actions (other ones we don't have include baremotion_in, baremotion_out (rare I hope) and drag)
                    on_press = printfunc('pressed'),
                    on_release_in = printfunc('release in'),
                    on_release_out = printfunc('release out')
                ),
                Translucent(Rect(1.5, 1, blue)), # has same bug
                ## DrawThePart(),
                Column(
                    Rotated( Overlay( RectFrame(1.5, 1, 0.1, white),
                                      Rect(0.5,0.5,orange),
                                      RectFrame(0.5, 0.5, 0.025, ave_colors(0.5,yellow,gray))
                                      ) ),
                    Pass,
                    Overlay( RectFrame(1.5, 1, 0.1, white),
                             Button(
                                 FilledSquare(bcolor, bcolor),
                                 FilledSquare(bcolor, next_bcolor),
                                 FilledSquare(next_bcolor, black),
                                 FilledSquare(bcolor, gray),
                                 on_release_in = toggleit
                            )
                    ),
                ),
                If(1,
                    Column(
                      Rect(1.5, 1, red),
                      ##Button(Overlay(TextRect(18, 3, "line 1\nline 2...."),Rect(0.5,0.5,black)), on_press = printfunc("zz")),
                          # buggy - sometimes invis to clicks on the text part, but sees them on the black rect part ###@@@
                          # (see docstring at top for a theory about the cause)
                      
    ##                  Button(TextRect(18, 3, "line 1\nline 2...."), on_press = printfunc("zztr")), # 
    ##                  Button(Overlay(Rect(3, 1, red),Rect(0.5,0.5,black)), on_press = printfunc("zzred")), # works
    ##                  Button(Rect(0.5,0.5,black), on_press = printfunc("zz3")), # works
                      Invisible(Rect(0.2,0.2,white)), # kluge to work around origin bug in TextRect ###@@@
                      Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
                      Highlightable( Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red), sbar_text = "bottom ribbon2" ),
                      Rect(1.5, 1, green),
                      gap = 0.2
                    ## DrawThePart(),
                    ),
                ),
                Closer(Column(
                    Highlightable( Rect(2, 3, pink),
                                   # this form of highlight (same shape and depth) works from either front or back view
                                   Rect(2, 3, orange), # comment this out to have no highlight color, but still sbar_text
                                   # example of complex highlighting:
                                   #   Row(Rect(1,3,blue),Rect(1,3,green)),
                                   # example of bigger highlighting (could be used to define a nearby mouseover-tooltip as well):
                                   #   Row(Rect(1,3,blue),Rect(2,3,green)),
                                   sbar_text = "big pink rect"
                                   ),
                    #Highlightable( Rect(2, 3, pink), Closer(Rect(2, 3, orange), 0.1) ) # only works from front
                        # (presumably since glpane moves it less than 0.1; if I use 0.001 it still works from either side)
                    Highlightable( # rename? this is any highlightable/mouseoverable, cmenu/click/drag-sensitive object, maybe pickable
                        Rect(1, 1, pink), # plain form, also determines size for layouts
                        Rect(1, 1, orange), # highlighted form (can depend on active dragobj/tool if any, too) #e sbar_text?
                        # [now generalize to be more like Button, but consider it a primitive, as said above]
                        # handling_a_drag form:
                        If( True, ## won't work yet: lambda env: env.this.mouseoverme , ####@@@@ this means the Highlightable -- is that well-defined???
                            Rect(1, 1, blue),
                            Rect(1, 1, lightblue) # what to draw during the drag
                        ),
                        sbar_text = "little buttonlike rect"
                    )
                )),
                gap = 0.2)
    # end of testexpr
    
# end
