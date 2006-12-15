# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
testdraw1_cannib.py

$Id$
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

class attrholder: pass # copied into py_utils.py

### draw_utils.py


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
        drawtest0(glpane) # this does all our special drawing, and sometimes puts some of it into a display list
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

def drawtest2(glpane): # last stuff drawn, never put into global displist [for redraw stats]
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


#e put these into an object for a texture font!
tex_width = 6 # pixel width in texture of 1 char
tex_height = 10 # guess (pixel height)



#### drawfont2 is being edited in testdraw.py -- better not do it right here by accident [061113]
# (these testdraw*cannib files may have been more confusing than good, not sure)
from testdraw import drawfont2

    
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

####### draw_utils.py



# == widget exprs

### WidgetExpr moved to widget2d.py

class DelegatingWidgetExpr(Delegator, WidgetExpr):# obs in exprs code, use Delegating*
    def __init__(self, *args, **kws):
        WidgetExpr.__init__(self, *args, **kws)
        Delegator.__init__(self, self.args[0]) # usually same as args[0], but this way, init method can modify self.args[0] if it needs to
    pass

def _kluge_glpane():# obs in exprs code, use env.glpane
    import env
    return env.mainwindow().assy.o
    
# ==

### moved to Highlightable.py:
# class DragHandler
# def PushName, def PopName, class Highlightable

# ==

def fix_color(color): # kluge #######@@@@@@@
    color = resolve_callables(color, 'fakeenv') ###e someday, most prims do this to most params...
    r,g,b = color # sanity check, though not a complete test of okness (if wrong, it can crash python) (support 4 elements?)
    glpane = _kluge_glpane()
    return r,g,b, glpane._alpha

# Rect is now in its own file Rect.py for now
# TextRect, RectFrame, ditto

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

# Overlay moved to exprs module

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
    def move_whole_to_argi_coords(self, i): #k experiment, not intended to be actually called for now, 060830; args numbered from 0
        gap = self.kws.get('gap',0)
        pa = None
        dx = 0
        for a in self.args[i:]:
            if a is None:
                continue
            if pa is not None:
                dx += pa.bright + a.bleft + gap
            pa = a
            continue
        if dx:
            glTranslate(dx,0,0)
        return
    def _get_width(self): # inefficient, need inval/update
        if not len(self.args):
            return 0 ###e or would -gap be better, in case we're included in a larger Row with the same gap??
        w = self.kws.get('gap',0) * (len(self.args) - 1) # wrong if no args! (unless we decide to use the -gap idea then)
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

Button = Highlightable # copied into exprs module

Pass = Rect(0,0,white) # seems to work (draws nothing) (not fully tested) [not used much, 061115, so not ported to exprs module]

def FilledSquare(fillcolor, bordercolor, size = 0.5, thickness_ratio = 0.05): # copied into exprs module
    return Overlay( Rect(size, size, fillcolor),
                    RectFrame(size, size, size * thickness_ratio, bordercolor)
    )

# kluge to test state toggling: moved to exprs module


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

##TestNode

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



                Translucent(Rect(1.5, 1, blue)), # has same bug
                ## DrawThePart(),



                If(1,


                ),


                gap = 0.2)
    # end of testexpr
    
# end
