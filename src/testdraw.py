# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
testdraw.py -- scratchpad for new code, OWNED BY BRUCE, not imported by default.

FOR NOW [060716], NO ONE BUT BRUCE SHOULD EDIT THIS FILE IN ANY WAY.

$Id$

[for doc, see testmode.py]
'''

__author__ = "bruce"

from testmode import *
from debug import print_compact_stack

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

try:
    vv
except:
    vv = attrholder()
    vv.tex_name = 0
    vv.tex_data = None
    vv.counter = 0
    ##e should modify to make it easier to set up defaults; sort of like a debug_pref?

# vv.counter = 0 # just to get started (was needed when i moved file to another machine, already running, too)

def drawtest(glpane):
    ## print_compact_stack( "testdraw.drawtest: ")
    vv.counter += 1
    ## print ( "%d testdraw.drawtest: " % vv.counter)
    glPushMatrix()
    try:
        drawtest0(glpane)
    except:
        print_compact_traceback("exc ignored: ")
    glPopMatrix() # it turns out this is needed, if drawtest0 does glTranslate, or our coords are messed up when glselect code
    # makes us draw twice! noticed on g4, should happen on g5 too, did it happen but less??

def drawtest0(glpane):
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
            test = "hi mom!"
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

filename1 = "/Users/bruce/PythonModules/data/baby_tapir-256.png" # also try 1059 files, sibling files of this
courierfile = "/Users/bruce/PythonModules/data/courier-128.png"

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

from idlelib.Delegator import Delegator

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
        glDisable(GL_LIGHTING)
        glColor3fv(color)
        glBegin(GL_LINE_STRIP)
        points = self.points()
        for p in points:
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
        color = mods.get('color',color)###k kluge, should be more general
        offset = axis * 2
        halfoffset = offset / 2.0
        interior_color = ave_colors(0.8,color, white) ###
        self.args = list(self.args) # slow!
        self.args[-1] = interior_color #### kluge!
        if 1:
            # draw the ribbon-edges; looks slightly better this way in some ways, worse in other ways --
            # basically, looks good on egdes that face you, bad on edges that face away (if the ribbons had actual thickness)
            # (guess: some kluge with lighting and normals could fix this)
            Corkscrew.draw(self)
            glTranslate(offset, 0,0)
            
            if 0: Corkscrew.draw(self)
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
        for p in points:
            perpvec = norm(V(0, p[1], p[2])) # norm here means divide by radius, that might be faster
            ## perpvec = V(0,0,1) # this makes front & back different solid lightness, BUT the values depend on the glRotate we did
            glNormal3fv( perpvec)
            glVertex3fv(p + offset * DX)
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
                Closer(Rect(2, 3, pink)),
                gap = 0.2)


# end except for outtakes


##try:
##    _nowversion
##except:
##    _nowversion = -1
##    
##try:
##    nowversion = 8 ### this is too hard to hand-update -- NEED TO USE FILE MODTIME OR SO
##    assert nowversion == _nowversion # fails if this needs to be redefined when we reload
##    mynode #k not needed
##except:
##    _nowversion = nowversion # don't keep getting the exception even if the following fails
##    print_compact_traceback("hmm: " )
##    print "nowversion = %d" % nowversion
##    from jigs_planes import ESPImage
##    win = env.mainwindow()
##    assy = win.assy
##    READ_FROM_MMP = True # so it does not do self.__init_quat_center, in case that needs atoms
##    mynode = ESPImage(assy, [], READ_FROM_MMP)
##    mynode.center = ORIGIN
##    mynode.quat = Q(1,0,0,0)
##    assy.place_new_jig(mynode)
##    win.win_update() # for MT update
##
##    # WHERE I AM:
##    # not yet working due to baggage of ESPImage like a need for atoms
##    # should copy it and pare it down
    
# tex bugs:
# it's so big
# it obscures rendered text no matter what
# need nfrs to try things out with it
# edges look funny - CLAMP - funny and diff color - REPEAT - funny and same color

