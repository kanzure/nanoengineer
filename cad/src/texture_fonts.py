# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
texture_fonts.py -- OpenGL fonts based on texture images of the characters

@author: Bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""

import os

from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_TEXTURE_2D
from OpenGL.GL import glBindTexture

from OpenGL.GLU import gluProject
from OpenGL.GLU import gluUnProject

import env

from icon_utilities import image_directory # for finding texture files

from VQT import V, A, vlen

from exprs.draw_utils import draw_textured_rect, mymousepoints

from texture_helpers import load_image_into_new_texture_name
from texture_helpers import setup_to_draw_texture_name

# TODO: clean up -- these are defined in multiple files
ORIGIN = V(0,0,0)
DX = V(1,0,0)
DY = V(0,1,0)
DZ = V(0,0,1)

# ==

class _attrholder: pass

try:
    vv  # singleton texture object ### TODO: rename, make an object
except:
    vv = _attrholder()
    vv.tex_name = 0
    vv.tex_data = None
    vv.have_mipmaps = False

# == constants related to our single hardcoded texture-font

# (these should be turned into instance attributes of a texture-font object)

# font image file (same image file is used in other modules, but for different purposes)
## ## CAD_SRC_PATH = os.path.dirname(__file__)
## from constants import CAD_SRC_PATH
## courierfile = os.path.join(CAD_SRC_PATH, "experimental/textures/courier-128.png")
courierfile = os.path.join( image_directory(), "ui/exprs/text/courier-128.png")  ### TODO: RENAME

#e put these into an object for a texture font!
tex_width = 6 # pixel width of 1 char within the texture image
tex_height = 10 # pixel height (guess)

'''
()()
()()(8)
8888 -- there's one more pixel of vertical space between the chars, here in idlehack, than in my courier-128.png image file!
'''

# ==

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
    ensure_courierfile_loaded() #bruce 070706 bugfix for when drawfont2 is used outside of testmode
    # optimized part of inlined setup_to_draw_texture_name
    glBindTexture(GL_TEXTURE_2D, vv.tex_name)
    ##e note: this will need extension once images.py can change more params,
    # to do some of the other stuff now done by setup_to_draw_texture_name.
    # OTOH it's too expensive to do that all the time (and maybe even this, if same tex already bound -- remains to be seen).
    return


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
      for i in range(-1, charheight - 1): # (range was -1,tex_ny == 8, length 9) - note, increasing i goes up on screen, not down!
        for j in range(charwidth): # was tex_nx == 16
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

