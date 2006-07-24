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
  Workaround: click after you change the view.

- we'll need to remember to reset havelist when we change other state, once we can do that.

- highlight orange is slightly wider on right than nonhighlight pink (guess: glpane translates in model space, not just depth space)

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
from debug import print_compact_stack
import env
from idlelib.Delegator import Delegator

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
halfblue = ave_colors( 0.5, blue, white)


# note: class avoidHighlightSlowness was defined here in rev. 1.6, but didn't work and probably can't work, so I zapped it.
# Its goal was to avoid the redraws on every mouseover motion of drawing that doesn't use glname to make itself highlightable.
# Instead, just get all drawing to be inside a highlightable object. (It's ok if the highlighting is not visible.
# It just needs to get into the stencil and depth buffers like the plain object, so we don't worry whether we're over other objects
# during the mouseover.)


try:
    vv
    vv.displist
    vv.havelist
except:
    vv = attrholder()
    vv.tex_name = 0
    vv.tex_data = None
    vv.counter = 0
    vv.displist = glGenLists(1)
    vv.havelist = 0
    ##e should modify to make it easier to set up defaults; sort of like a debug_pref?

# vv.counter = 0 # just to get started (was needed when i moved file to another machine, already running, too)

def leftDown(glpane, event):
    vv.havelist = 0 # so editing this file (and clicking) uses the new code

def drawtest(glpane):
    vv.counter += 1
    glPushMatrix()
    try:
        drawtest0(glpane)
    except:
        print_compact_traceback("exc ignored: ")
    glPopMatrix() # it turns out this is needed, if drawtest0 does glTranslate, or our coords are messed up when glselect code
    # makes us draw twice! noticed on g4, should happen on g5 too, did it happen but less??

# ==

def havelist_counters(glpane):
    "return some counters which better have the same value or we'll treat havelist as if it was invalidated"
    assy = glpane.assy
    return (assy._view_change_counter,)

def display_list_helper(self, glpane, drawfunc):
    "self needs .havelist and .displist"
    if self.havelist == havelist_counters(glpane): ## == (disp, eltprefs, matprefs, drawLevel): # value must agree with set of havelist, below
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
        wantlist = True
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
            print "drawfunc (redraw %d)" % env.redraw_counter
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

###@@@ bug: 
def drawtest0(glpane):
    # vv has .havelist and .displist
    drawfunc = lambda:drawtest1(glpane)
    display_list_helper( vv, glpane, drawfunc)
    return

def drawtest1(glpane):
    glTranslatef(-7,7,0)
    dy = - 0.5
    ## drawline(color, pos1, pos2, dashEnabled = False, width = 1)
    drawline(red,   V(0,0,0),V(1,0,0),width = 2)
    glTranslatef( 0, dy, 0)
    drawline(green, V(0,0,0),V(2,0,0),width = 2)
    glTranslatef( 0, dy, 0)
    drawline(yellow,V(0,0,0),V(1,0,0),width = 2)
    ## def drawtext(text, color, pt, size, glpane)
    glTranslatef( 0, dy, 0)
    drawtext("hi! (@[fg])", blue, V(0,0,0), 12, glpane)
    glTranslatef( 0, dy, 0)
    drawtext("hi Mom...", white, V(0,0,0), 24, glpane) # ugly, but readable
    #drawtext("<b>hi Mom</b>", blue, V(0,0,0), 24, glpane) # html doesn't work, as expected
    # even \n doesn't work -- \n is a rectangle, \r is nothing, \t is single space.

    glTranslatef( 0, dy, 0.002) # 0.002 is enough to obscure the yellow line; 0.001 is not enough.

    ###e only do the following when needed!
    tex_filename = courierfile ## "xxx.png" # the charset
    "courierfile"
    tex_data = (tex_filename,)
    if vv.tex_name == 0 or vv.tex_data != tex_data:
        vv.have_mipmaps, vv.tex_name = load_image_into_new_texture_name( tex_filename, vv.tex_name)
        vv.tex_data = tex_data
    else:
        pass # assume those vars are fine from last time
    setup_to_draw_texture_name(vv.have_mipmaps, vv.tex_name)
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
    draw_filled_rect(origin + 0.2*DZ + DX, dx, dy, halfblue) # note, it matters that dx/dy is right-handed.

    for i in range(1):
        glTranslatef( 0, -4, 0 )
        testexpr.draw() # it worked almost the first time!
    glTranslatef( 0, -8, -1 )
    
##    te2 = Row( testexpr, testexpr, gap = 0.3 )
##    glTranslatef( 0, 6, 0 )

##    te2.draw()

    ####@@@@
    # next up: mouse event bindings, state, programming constructs incl scope, formulas (getters? inval?), option-defaults

    #####@@@@@ new G4 stuff 060429
    ## glTranslatef( 0, pixelheight / 2, 0 ) # perfect!
        # (Ortho mode, home view, a certain window size -- not sure if that matters but it might)
        # restoring last-saved window position (782, 44) and size (891, 749)

#def drawtest0(glpane):
    # adjust these guessed params until they work right:
    tex_width = 6 # pixel width in texture of 1 char)
    tex_height = 10 # guess (pixel height)
    tex_origin_chars = V(3,65) # guess was 0,64... changing y affects the constant color; try 0, not totally constant
    tex_size = (128,128) # guess
    tex_nx = 16
    tex_ny = 8
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
    if pixfactor == 2:
        tex_origin_chars = V(3.5, 64.5) # 3.5 seems best, tho some shift to right; 3.55 through 3.75 are same, too much shift to left
    if pixfactor == 1:
        if "not starting at origin": # for pixfactor 1, to make it perfect, start where this does start... at origin doesn't yet work. 
            glTranslatef( 0, pixelheight / 2, 0 )
    
    tex_dx = V(tex_width, 0) # in pixels
    tex_dy = V(0, tex_height)
    # using those guesses, come up with tex-rects for each char as triples of 2-vectors (tex_origin, tex_dx, tex_dy) 
    def ff(i,j): # i for y, j or x (is that order normal??), still starting at bottom left
        if i == -1 or i == 7:
            test = "(redraw %d)" % env.redraw_counter
                # this shows that mouseover of objects (pixels) w/o glnames causes redraws! I understand glselect ones,
                # but they should not be counted, and should not show up on the screen, so i don't understand
                # any good reason for these visible ones to happen.
                #e to try to find out, we could also record compact_stack of the first gl_update that caused this redraw...
            if j < len(test):
                # replace i,j with new ones so as to draw those chars instead
                ch1 = ord(test[j]) - 32
                j = ch1 % tex_nx
                i = 5 - (ch1 / tex_nx)
        return tex_origin_chars + i * tex_dy + j * tex_dx , tex_dx, tex_dy
    # now think about where to draw all this... use a gap, but otherwise the same layout
    charwidth = tex_width * pixelwidth
    charheight = tex_height * pixelheight
    char_dx = (tex_width + gap) * pixelwidth
    char_dy = (tex_height + gap) * pixelheight
    def gg(i,j):
        return ORIGIN + j * char_dx * DX + i * char_dy * DY, charwidth * DX, charheight * DY
    # now draw them

    if 1: #### for n in range(65): # simulate the delay of doing a whole page of chars
      for i in range(-1,tex_ny): # 9
        for j in range(tex_nx): # 16
            origin, dx, dy = gg(i,j)
            tex_origin, ltex_dx, ltex_dy = ff(i,j) # still in pixel ints
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
    
    #####@@@@@ end new G4/G5 stuff 060429
    
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

def draw_filled_rect(origin, dx, dy, color):
    glColor3fv(color)
##    glRectfv(origin, origin + dx + dy) # won't work for most coords! also, ignores Z. color still not working.
    glDisable(GL_LIGHTING) # this allows the specified color to work. Otherwise it doesn't work (I always get dark blue). Why???
     # guess: if i want lighting, i have to specify a materialcolor, not just a regular color. (and vertex normals)
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
        self.args = args
        self.kws = kws
        self.init()
    def init(self):
        pass
    def _get_width(self):
        return self.bright + self.bleft
    #e _get_height
    pass

class Highlightable(Delegator, WidgetExpr):#060722
    "Highlightable(plain, highlight) renders as plain (and delegates most things to it), but on mouseover, as plain plus highlight"
    # Works, except I suspect the docstring is inaccurate when it says "plain plus highlight" (rather than just highlight), 
    # and there's an exception if you try to ask selectMode for a cmenu for this object, or if you just click on it
    # (I can guess why -- it's a selobj-still-valid check I vaguely recall):
    #   atom_debug: ignoring exception: exceptions.AttributeError: killed
    #   [modes.py:928] [Delegator.py:10] [inval.py:192] [inval.py:309]
    #
    __init__ = WidgetExpr.__init__ # otherwise Delegator's comes first and init() never runs
    def init(self):
        self.plain = self.args[0]
        try:
            self.highlight = self.args[1]
        except IndexError:
            self.highlight = self.plain # useful for things that just want a glname to avoid mouseover stickiness
        Delegator.__init__(self, self.plain) # for defns like bright, bleft
        # get glname, register self (or a new obj we make for that purpose #e), define necessary methods
        glname_handler = self # self may not be the best object to register here, though it works for now
        self.glname = env.alloc_my_glselect_name(glname_handler)
            #e if we might never be drawn, we could optim by only doing this on demand
    def draw(self):
        self.saved_modelview_matrix = glGetDoublev( GL_MODELVIEW_MATRIX ) # needed by draw_in_abs_coords
            ###WRONG if we can be used in a displaylist that might be redrawn in varying orientations/positions
            #e [if this (or any WE) is really a map from external state to drawables,
            #   we'd need to store self.glname and self.saved_modelview_matrix in corresponding external state]
        glPushName(self.glname)
        self.plain.draw()
##        if 0 and 'klugetest':
##            if env.redraw_counter % 2:
##                self.highlight.draw()
        glPopName() ##e should protect this from exceptions
            #e (or have a WE-wrapper to do that for us, for .draw() -- or just a helper func, draw_and_catch_exceptions)
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
        self.highlight.draw()
        glPopMatrix()
        return
    def __repr__(self): ### kluge -- better if selectMode called a specific method for this
        return self.kws.get('sbar_text') or "<%s at %#x>" % (self.__class__.__name__, id(self))
    def highlight_color_for_modkeys(self, modkeys):
        """#doc; modkeys is e.g. "Shift+Control", taken from glpane.modkeys
        """
        return green # color doesn't matter, but it might matter that it's a legal color, or not None, to GLPane (I don't know);
            # this color will be received by draw_in_abs_coords (which ignores it)
    pass

class Rect(WidgetExpr): #e example, not general enough to be a good use of this name
    "Rect(width, height, color) renders as a filled rect of that color, origin on bottomleft"
    def init(self):
        self.bright = self.args[0]
        self.btop = self.args[1]
        self.color = self.args[2] # or dflt color?
    def draw(self):
        glDisable(GL_CULL_FACE)
        draw_filled_rect(ORIGIN, DX * self.bright, DY * self.btop, self.color)
        glEnable(GL_CULL_FACE)
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

class Closer(Delegator, WidgetExpr):
    "Closer(thing, amount)"
    __init__ = WidgetExpr.__init__ # otherwise Delegator's comes first and init() never runs
    def init(self):
        self.args = list(self.args) + [1] # default amount
        self.thing = self.args[0] # or use self.delegate
        self.amount = self.args[1]
        Delegator.__init__(self, self.thing) # for defns like bright, bleft
    def draw(self):
        glTranslate(0, 0, self.amount)
        self.thing.draw()
        glTranslate(0, 0, -self.amount)
        return
    pass

class Corkscrew(WidgetExpr):
    "Corkscrew(radius, axis, turn, n, color) - axis is length in DX, turn might be 1/10.5"
    def init(self):
        radius, axis, turn, n, color = self.args #k checks length
    def draw(self):
        radius, axis, turn, n, color = self.args # axis is for x, theta starts 0, at top (y), so y = cos(theta), z = sin(theta)
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

class Ribbon(Corkscrew):
    def draw(self, **mods):
        radius, axis, turn, n, color = self.args
        color = mods.get('color',color)##kluge
            ##e todo: should be more general; maybe should get "state ref" (to show & edit) as arg, too?
        offset = axis * 2
        halfoffset = offset / 2.0
        interior_color = ave_colors(0.8,color, white) ###
        self.args = list(self.args) # slow!
        self.args[-1] = interior_color #### kluge! and/or misnamed, since used for both sides i think
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self)
            if 0:
                glTranslate(offset, 0,0)            
                Corkscrew.draw(self) ### maybe we should make the two edges look different, since they are (major vs minor groove)
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

class Ribbon2(Ribbon):
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

testexpr = Row( Rect(1.5, 1, red),
                Column(
                  Rect(1.5, 1, red),
                  Ribbon2(1, 0.2, 1/10.5, 50, blue, color2 = green), # this color2 arg stuff is a kluge
                  Ribbon2(1, 0.2, 1/10.5, 50, yellow, color2 = red),
                  Rect(1.5, 1, green),
                  gap = 0.2
                ),
                Closer(
                    Highlightable( Rect(2, 3, pink),
                                   # this form of highlight (same shape and depth) works from either front or back view
                                   Rect(2, 3, orange), # comment this out to have no highlight color, but still sbar_text
                                   # example of complex highlighting:
                                   #   Row(Rect(1,3,blue),Rect(1,3,green)),
                                   # example of bigger highlighting (could be used to define a nearby mouseover-tooltip as well):
                                   #   Row(Rect(1,3,blue),Rect(2,3,green)),
                                   sbar_text = "rect1"
                                   )
                    #Highlightable( Rect(2, 3, pink), Closer(Rect(2, 3, orange), 0.1) ) # only works from front
                        # (presumably since glpane moves it less than 0.1; if I use 0.001 it still works from either side)
                ),
                gap = 0.2)

#e want: draw myself or my subobj or superobj but with modified params: super.draw(self, color = othercolor)
class xx:
    def draw(self, **mods):
        color = self.getopt('color', mods) # mods, then self attrs
        # e.g. dict(self.__dict__).update(mods)

#e want: we's for highlighting, selection, other behavior; let these things act like atoms in build, get into mmp files & undo


class Drawable: # see also Drawables.py, into which this is intended to be merged someday
    """Abstract class for things which selectAtomsMode can draw, and optionally highlight, 
    click-select, region-select, drag (alone or in a selected set of things), Fit To Window,
    perhaps View Normal To, or get a context menu from.
       Someday, they can also define custom cursors, statusbar info.
       Drawables may, but need not, own the state they should represent graphically
    (for viewing and editing) -- they may instead just hold a reference to another object
    which owns that state (and which defines methods for operating on it, saving/loading it).
       Similarly, they typically would not be defined as containing specific graphics primitives,
    but rather, rules for creating those from the state they wish to represent.
       They are likely to have similarities to, or more likely be merged with, WidgetExprs;
    their state-representing rules may have some similarity to ParseRules.
       One thing not yet well-defined is how they should interact with objects owning
    display lists into which they want to draw these drawables. This implies that the drawables
    (or at least their allocated glnames, and whatever objects they register to handle those)
    last at least as long as the display list contents. That probably means that the objects need
    to add themselves to a list of display-list content owners, available as a global for whatever
    display list (if any) is currently being compiled. Even if no display list is being compiled,
    that info is needed (and the objects in it need to last) for as long as something might keep
    the namestack results from a glRenderMode call.
    """
    # but widget exprs need a more flexible framework, maybe related to ParseRule,
    # as well as a better way of handling named options, mentioned elsewhere in this file.
    def __init__(self):
        pass
    pass

# end except for outtakes

##class glname_Drawable(Drawable): #obs, superceded by Highlightable
##    "Mixin(?) class for drawables that own one glname."
##    def __init__(self):
##        #e super __init__
##        glname_handler = self ###WRONG? self is probably not the right object to register here!
##        self.glname = env.alloc_my_glselect_name(glname_handler) #e or this could be a _compute_ rule for self.glname
##    pass

# tex bugs: [semi-obs comment? not sure]
# it's so big
# it obscures rendered text no matter what
# need nfrs to try things out with it
# edges look funny - CLAMP - funny and diff color - REPEAT - funny and same color

