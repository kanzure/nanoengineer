# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
bond_drawer.py -- implementations of Bond.draw and Bond.writepov.

$Id$

History:

050727 bruce moved bodies of Bond.draw and Bond.writepov into functions in this file,
in preparation for further extending Bond.draw (and someday Bond.writepov) for
higher-order bonds.
'''

__author__ = "Josh"

######e needs cvs add   #####@@@@@


from VQT import *
from constants import *
import platform
from debug import print_compact_stack, print_compact_traceback

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from drawer import *

from povheader import povpoint #bruce 050413

from chem import stringVec

from bond_constants import *

from elements import Singlet

from qt import QFont, QString, QColor ###k

from handles import ave_colors

CPKSigmaBondRadius = 0.1 #bruce 050719
    ###e should make this a named constant in constants.py (or bond_constants.py?),
    # like TubeRadius (i.e. "TubesSigmaBondRadius")


def draw_bond(self, glpane, dispdef, col, level, highlighted = False):
    #bruce 050702 adding shorten_tubes option; 050727 that's now implied by new highlighted option
    """Draw the bond 'self'. This function is only meant to be called as the implementation of Bond.draw.
    See that method's docstring for details of how it's called.
    The highlighted option says to modify our appearance as appropriate for being highlighted
    (but the highlight color, if any, is passed as a non-false value of col).
    """
    atom1 = self.atom1
    atom2 = self.atom2
    
    color1 = col or atom1.element.color
    color2 = col or atom2.element.color

    disp = max(atom1.display, atom2.display)
    if disp == diDEFAULT:
        disp = dispdef

    # figure out how this display mode draws bonds; return now if it doesn't
    if disp == diLINES:
        sigmabond_cyl_radius = CPKSigmaBondRadius # used for multiple bond spacing and for pi orbital vanes
    elif disp == diCPK:
        sigmabond_cyl_radius = CPKSigmaBondRadius # also used for central cylinder, in these other cases
    elif disp == diTUBES:
        sigmabond_cyl_radius = TubeRadius
    else:
        return # bonds need not be drawn at all in the other display modes

    # figure out preferences
    if self.v6 != V_SINGLE:
        if platform.atom_debug:
            #bruce 050716 debug code (permanent, since this would always indicate a bug)
            if not self.legal_for_atomtypes():
                print_compact_stack("atom_debug: drawing bond %r which is illegal for its atomtypes: " % self)
        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False #bruce 050717, might be temporary
        draw_bond_letters = debug_pref("bond letters", Choice_boolean_False)
        draw_vanes = debug_pref("double-bond vanes", Choice_boolean_True) #e make dflt False when standard drawing available
        draw_cyls = debug_pref("double-bond cylinders", Choice_boolean_False) # cyls are nim [bruce 050725]  ###@@@
        draw_sigma_cyl = not draw_cyls
    else:
        draw_sigma_cyl = True
    
    shorten_tubes = highlighted
    
    if highlighted:
        toolong_color = ave_colors( 0.8, purple, black) ##e should improve this color, and maybe let it mix in col
    else:
        toolong_color = ave_colors( 0.8, red, black) #bruce 050727 changed this from pure red

    # set proper glname, for highlighting (must be done whether or not highlighted is true)
    if atom1.element is Singlet:
        #bruce 050708 new feature -- borrow name from our singlet
        # (only works because we have at most one)
        # (also required a change in Atom.draw_in_abs_coords)
        glname = atom1.glname
    elif atom2.element is Singlet:
        glname = atom2.glname
    else:
        glname = self.glname

    glPushName( glname) #bruce 050610
        # Note: we have to do this all the time, since display lists made outside GL_SELECT mode can be used inside it.
        # And since that display list might be used arbitrarily far into the future,
        # self.glname needs to remain the same (and we need to remain registered under it)
        # as long as we live.

    try: #bruce 050610 to ensure calling glPopName

        if disp == diLINES:
            a1pos, c1, center, c2, a2pos, toolong = self.geom
            if not toolong:
                drawline(color1, a1pos, center)
                drawline(color2, a2pos, center)
            else:
                drawline(color1, a1pos, c1)
                drawline(color2, a2pos, c2)
                drawline(red, c1, c2) # not toolong_color, since we're not sure highlighting bonds in LINES mode is good at all
        elif disp == diCPK:
            a1pos, c1, center, c2, a2pos, toolong = self.geom #e could be optimized to compute less for this case
            if draw_sigma_cyl:
                drawcylinder(col or bondColor, a1pos, a2pos, sigmabond_cyl_radius)
        elif disp == diTUBES:
            a1pos, c1, center, c2, a2pos, toolong = self.geom
            if shorten_tubes:
                rad = TubeRadius * 1.1 * 0.9 # see Atom.howdraw for tubes; the constant (0.9) might need adjusting
                    #bruce 050726 changed that constant from 1.0 to 0.9
                vec = norm(a2pos-a1pos) # warning: if atom1 is a singlet, a1pos == center, so center-a1pos is not good to use here.
                if atom1.element is not Singlet:
                    a1pos = a1pos + vec * rad
                if atom2.element is not Singlet:
                    a2pos = a2pos - vec * rad
            v1 = atom1.display != diINVISIBLE
            v2 = atom2.display != diINVISIBLE
            ###e bruce 041104 suspects v1, v2 wrong for external bonds, needs
            # to look at each mol's .hidden (but this is purely a guess)
            ###e bruce 050513 future optim idea: when color1 == color2, draw just
            # one longer cylinder, then overdraw toolong indicator if needed.
            # Significant for big parts. BUT, why spend time on this when I
            # expect we'll do this drawing in C code before too long?
            if draw_sigma_cyl: ###@@@ this seems wrong -- probably need to make this a subr to be called twice for double bonds...
                if not toolong:
                    if v1 and v2 and (not color1 != color2): # "not !=" is in case colors are Numeric arrays (don't know if possible)
                        #bruce 050516 optim: draw only one cylinder in this common case
                        drawcylinder(color1, a1pos, a2pos, sigmabond_cyl_radius)
                    else:
                        if v1:
                            drawcylinder(color1, a1pos, center, sigmabond_cyl_radius)
                        if v2:
                            drawcylinder(color2, a2pos, center, sigmabond_cyl_radius)
                        if not (v1 and v2):
                            drawsphere(black, center, sigmabond_cyl_radius, level)
                else:
                    drawcylinder(toolong_color, c1, c2, sigmabond_cyl_radius)
                    if v1:
                        drawcylinder(color1, a1pos, c1, sigmabond_cyl_radius)
                    else:
                        drawsphere(black, c1, sigmabond_cyl_radius, level)
                    if v2:
                        drawcylinder(color2, a2pos, c2, sigmabond_cyl_radius)
                    else:
                        drawsphere(black, c2, sigmabond_cyl_radius, level)
        if self.v6 != V_SINGLE:
            if draw_bond_letters:
                glDisable(GL_LIGHTING)
                ## glDisable(GL_DEPTH_TEST)
                glPushMatrix()
                font = QFont( QString("Times"), 10)
                    # fontsize 12 doesn't work, don't know why, maybe specific to "Times", since it works in other code for Helvetica
                    ###e should adjust fontsize based on scale, depth...
                    #e could optimize this, keep in glpane
                ## glpane.qglColor(QColor(75, 75, 75)) # gray
                ## glpane.qglColor(QColor(200, 40, 140)) # majenta
                glpane.qglColor(QColor(255, 255, 255)) # white
                try:
                    glpane_out = glpane.out
                except AttributeError:
                    glpane_out = V(0.0, 0.0, 1.0) # kluge for Element Selector [bruce 050507 bugfix]
                p = self.center + glpane_out * 0.6
                    ###WRONG -- depends on rotation when display list is made! But quite useful for now.
                    # Could fix this by having a separate display list, or no display list, for these kinds of things --
                    # would need a separate display list per chunk and per offset.
                v6 = self.v6
                ltr = bond_letter_from_v6(v6).upper()
                glpane.renderText(p[0], p[1], p[2], QString(ltr), font) #k need explicit QString??
                glPopMatrix()
                ## glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)
            if draw_vanes:
                if platform.atom_debug:
                    import draw_bond_vanes
                    reload(draw_bond_vanes) #e too slow to always do this here, even in debug, once devel done! #######@@@@@@@
                from draw_bond_vanes import draw_bond_vanes
                draw_bond_vanes( self, glpane, sigmabond_cyl_radius, col) # this calls self.get_pi_info()
            if draw_cyls:
                if platform.atom_debug: #e too slow (see comment above) ######@@@@@@@
                    import draw_bond_cyls
                    reload(draw_bond_cyls)
                from draw_bond_cyls import draw_bond_cyls # this is nim -- in fact, the module doesn't yet exist [bruce 050725]
                draw_bond_cyls( self, glpane, sigmabond_cyl_radius, col) ###IMPLEM
        pass

    except:
        glPopName()
        print_compact_traceback("ignoring exception when drawing bond %r: " % self)
    else:
        glPopName()
    
    return # from draw_bond, implem of Bond.draw

def writepov_bond(self, file, dispdef, col):
    "Write this bond 'self' to a povray file (always using absolute coords, even for internal bonds)."
    ##Huaicai 1/15/05: It seems the attributes from __setup__update() is not correct,
    ## at least for pov file writing, so compute it here locally. To fix bug 346,347

    #bruce 050516 comment: my guess is, those attrs were "not correct" for internal bonds
    # since in that case they're in the chunk's private "basecenter/quat" coordinate
    # system, not the absolute (model) coordinate system. So I am now comparing these
    # to what's returned by _recompute_geom with abs_coords = True. If that's correct,
    # we can change this code to use that routine.
    disp = max(self.atom1.display, self.atom2.display)
    if disp == diDEFAULT: disp = dispdef
    color1 = col or self.atom1.element.color
    color2 = col or self.atom2.element.color
    
    a1pos = self.atom1.posn()
    a2pos = self.atom2.posn()
    
    vec = a2pos - a1pos
    leng = 0.98 * vlen(vec)
    vec = norm(vec)
    # (note: as of 041217 rcovalent is always a number; it's 0.0 for Helium,
    #  etc, so the entire bond is drawn as if "too long".)
    rcov1 = self.atom1.atomtype.rcovalent
    rcov2 = self.atom2.atomtype.rcovalent
    c1 = a1pos + vec*rcov1
    c2 = a2pos - vec*rcov2
    toolong = (leng > rcov1 + rcov2)
    center = (c1 + c2) / 2.0 # before 041112 this was None when self.toolong

    if platform.atom_debug: #bruce 050516; explained above ####@@@@
        if self._recompute_geom(abs_coords = True) != (a1pos, c1, center, c2, a2pos, toolong):
            print "atom_debug: _recompute_geom wrong in writepov!" #e and say why, if this ever happens
        # if this works, we can always use _recompute_geom for external bonds,
        # and optim by using self.geom for internals.
    
    if disp < 0: disp = dispdef
    if disp == diLINES:
        file.write("line(" + povpoint(a1pos) +
                   "," + povpoint(a2pos) + ")\n")
    if disp == diCPK:
        file.write("bond(" + povpoint(a1pos) +
                   "," + povpoint(a2pos) + ")\n")
    if disp == diTUBES:
    ##Huaicai: If rcovalent is close to 0, like singlets, avoid 0 length 
    ##             cylinder written to a pov file    
        DELTA = 1.0E-5
        isSingleCylinder = False
        if  self.atom1.atomtype.rcovalent < DELTA:
                col = color2
                isSingleCylinder = True
        if  self.atom2.atomtype.rcovalent < DELTA:
                col = color1
                isSingleCylinder = True
        if isSingleCylinder:
            file.write("tube3(" + povpoint(a1pos) + ", " + povpoint(a2pos) + ", " + stringVec(col) + ")\n")
        else:
            if not toolong: #bruce 050516 changed this from self.toolong to toolong
                file.write("tube2(" + povpoint(a1pos) +
                   "," + stringVec(color1) +
                   "," + povpoint(center) + "," +
                   povpoint(a2pos) + "," +
                   stringVec(color2) + ")\n")
            else:
                file.write("tube1(" + povpoint(a1pos) +
                   "," + stringVec(color1) +
                   "," + povpoint(c1) + "," +
                   povpoint(c2) + "," + 
                   povpoint(a2pos) + "," +
                   stringVec(color2) + ")\n")
    return # from writepov_bond

# end

