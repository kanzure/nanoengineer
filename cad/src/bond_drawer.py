# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
bond_drawer.py -- implementations of Bond.draw and Bond.writepov.

@author: Josh, Bruce
@version: $Id$
@copyright: Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

050727 bruce moved bodies of Bond.draw and Bond.writepov into functions in this file,
in preparation for further extending Bond.draw (and someday Bond.writepov) for
higher-order bonds.
"""

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
try:
    from OpenGL.GLE import glePolyCone
except:
    from OpenGL._GLE import glePolyCone

from PyQt4.Qt import QFont, QString, QColor

from VQT import V
from VQT import norm

from drawer import ColorSorter
from drawer import drawline
from drawer import drawcylinder
from drawer import drawsphere

import env
import platform

from povheader import povpoint
from utilities.Printing import Vector3ToString
from elements import Singlet

from debug import print_compact_stack, print_compact_traceback

from constants import diDEFAULT
from constants import diLINES
from constants import diBALL
from constants import diTUBES
from constants import TubeRadius
from constants import diINVISIBLE
from constants import diBALL_SigmaBondRadius
from constants import ave_colors
from constants import green
from constants import yellow
from constants import red
from constants import blue
from constants import black
from constants import white
from constants import orange

from bond_constants import V_SINGLE
from bond_constants import V_DOUBLE
from bond_constants import V_TRIPLE
from bond_constants import bond_letter_from_v6
from bond_constants import V_AROMATIC
from bond_constants import V_GRAPHITE
from bond_constants import V_CARBOMERIC

from prefs_constants import _default_toolong_hicolor ## not yet in prefs db?
from prefs_constants import diBALL_BondCylinderRadius_prefs_key
from prefs_constants import pibondLetters_prefs_key
from prefs_constants import pibondStyle_prefs_key
from prefs_constants import arrowsOnFivePrimeEnds_prefs_key
from prefs_constants import arrowsOnThreePrimeEnds_prefs_key
from prefs_constants import arrowsOnBackBones_prefs_key
from prefs_constants import showBondStretchIndicators_prefs_key
from prefs_constants import linesDisplayModeThickness_prefs_key
from prefs_constants import bondStretchColor_prefs_key
from prefs_constants import diBALL_bondcolor_prefs_key

# ==

# To modularize drawing, I'll pass in a drawing place which has methods like drawcylinder,
# which can be either the drawer module itself (or an object made here to encapsulate it)
# or a writepov-to-specific-file object. This is experimental code, so for now it's only here
# in bond_drawer.py.
#
# In the future, it should be created once per writepov event, and write the povheader, and
# then it should be passed in to individual writepov routines. Farther ahead, it should be able
# to write new macros which embody env.prefs values as needed, so individual atom/bond drawing calls
# don't need to each incorporate the effects of prefs values, but so that single macros can be revised
# manually in the output file to effectively change prefs values (a longstanding NFR from the SAB).
#
# [bruce 060622]

class writepov_to_file:
    def __init__(self, file, col = None):
        self.file = file # a file object, not just its name
        # does not currently write the povheader -- assumes it was already written
        self.bondColor = col
        return
    # for now, the following methods have the same names and arg orders as the
    # macro calls that were used directly in writepov_bond.
    def line(self, a1pos, a2pos, color):
        self.file.write("line(" + povpoint(a1pos) +
           "," + povpoint(a2pos) + ", <" + str(color[0]) +"," + str(color[1]) + ", " + str(color[2]) + ">)\n")
    def writeradmacro(self, rad, radmacro, noradmacro):
        if rad is not None:
            self.file.write("%s(" % radmacro + str(rad) + ", " )
        else:
            self.file.write("%s(" % noradmacro )
    def bond(self, a1pos, a2pos, col, rad = None):
        self.writeradmacro(rad, "bondr", "bond")
        self.file.write( povpoint(a1pos) +
                   "," + povpoint(a2pos) + 
                   "," + Vector3ToString(col) + ")\n")
    def tube3(self, a1pos, a2pos, col, rad = None):
        self.writeradmacro(rad, "tube3r", "tube3")
        self.file.write( povpoint(a1pos) + ", " + povpoint(a2pos) + ", " + Vector3ToString(col) + ")\n")
    def tube2(self, a1pos, color1, center, a2pos, color2, rad = None):
        if 1:
            #e Possible optim: if color1 == color2, this could reduce to tube3.
            # That might speed up povray in tubes mode by a factor of 2 or so
            # (for bonds that are not toolong), or maybe by 5/4 if half of the bonds are toolong.
            # It seems to work (from manual inspection of the output) so I'll leave it in.
            # [bruce 060622]
            if color1 == color2:
                self.tube3(a1pos, a2pos, color1, rad)
                return
        self.writeradmacro(rad, "tube2r", "tube2")
        self.file.write( povpoint(a1pos) +
           "," + Vector3ToString(color1) +
           "," + povpoint(center) + "," +
           povpoint(a2pos) + "," +
           Vector3ToString(color2) + ")\n")
    def tube1(self, a1pos, color1, c1, c2, a2pos, color2, rad = None):
        self.writeradmacro(rad, "tube1r", "tube1")
        self.file.write( povpoint(a1pos) +
           "," + Vector3ToString(color1) +
           "," + povpoint(c1) + "," +
           povpoint(c2) + "," + 
           povpoint(a2pos) + "," +
           Vector3ToString(color2) + ")\n")
    def drawcylinder(self, color, pos1, pos2, radius): # arg order compatible with drawer.drawcylinder
        self.tube3(pos1, pos2, color, radius)
    def drawsphere(self, color, pos, radius): # arg order compatible with drawer.drawsphere, except no detailLevel; not yet called or tested [060622]
        ###k not compared with other calls of atom macro, or tested; kluge that it uses atom macro, since not all spheres are atoms
        self.file.write( "atom(" + str(pos) + ", " + str(radius) + ", " + Vector3ToString(color) + ")\n")
    
    def getBondColor(self):
        """
        Returns the self.bondColor (rgb value) 
        @return: L{self.bondColor}
        @see: L{self.old_writepov_bondcyl}
        @Note:  this whole file needs code cleanup.  
        """
        return self.bondColor

# ==

def draw_bond(self, glpane, dispdef, col, level, highlighted = False, bool_fullBondLength = False):
    #bruce 050702 adding shorten_tubes option; 050727 that's now implied by new highlighted option
    """
    Draw the bond 'self'. This function is only meant to be called as the implementation of Bond.draw.
    See that method's docstring for details of how it's called.
    The highlighted option says to modify our appearance as appropriate for being highlighted
    (but the highlight color, if any, is passed as a non-false value of col).
    """
    atom1 = self.atom1
    atom2 = self.atom2
    
    disp = max(atom1.display, atom2.display)
    if disp == diDEFAULT:
        disp = dispdef

    if disp not in (diLINES, diBALL, diTUBES):
        return

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

    ColorSorter.pushName(glname) #bruce 051206, part of fixing bug 1179 for non-open bonds;
        # we have to do it both immediately and in ColorSorter since bonds include both
        # sorted and non-sorted openGL drawing. Note, we don't yet protect against sorting
        # not being active now, but that should be fixed in drawer.py rather than here,
        # and for now it will always be active since all bond drawing in chunk.py is done
        # inside it (even external bonds).
    glPushName( glname) #bruce 050610
        # Note: we have to do this all the time, since display lists made outside GL_SELECT mode can be used inside it.
        # And since that display list might be used arbitrarily far into the future,
        # self.glname needs to remain the same (and we need to remain registered under it)
        # as long as we live.

    try: #bruce 050610 to ensure calling glPopName    
        povfile = None
        draw_bond_main( self, glpane, disp, col, level, highlighted, 
                        povfile, bool_fullBondLength)
    except:
        glPopName()
        print_compact_traceback("ignoring exception when drawing bond %r: " % self) #bruce 060622 moved this before ColorSorter.popName
        ColorSorter.popName() #bruce 051206
    else:
        glPopName()
        ColorSorter.popName() #bruce 051206
    
    return # from draw_bond, implem of Bond.draw

def draw_bond_main( self, glpane, disp, col, level, highlighted, povfile = None, bool_fullBondLength = False):
    """
    [private helper function for this module only.]
    self is a bond. For other doc, see the calls.
    """
    # figure out how this display mode draws bonds; return now if it doesn't [moved inside this function, bruce 060622]
    if disp == diLINES:
        sigmabond_cyl_radius = diBALL_SigmaBondRadius / 5.0
            # used for multiple bond spacing (optimized here for that, by the "/ 5.0")
            # and for pi orbital vanes (for which "/ 1.0" would probably be better)
    elif disp == diBALL:
        sigmabond_cyl_radius = diBALL_SigmaBondRadius * env.prefs[diBALL_BondCylinderRadius_prefs_key]
            # used for single, double and triple bonds
            # mark 051003 added " * env.prefs[diBALL_BondCylinderRadius_prefs_key]"
    elif disp == diTUBES:
        sigmabond_cyl_radius = TubeRadius
    else:
        return # bonds need not be drawn at all in the other display modes. (note: some callers already checked this.)

    # figure out preferences (should do this less often somehow -- once per user event,
    #  or at least, once per separate use of begin_tracking_usage/end_tracking_usage)
    if self.v6 != V_SINGLE:
        if platform.atom_debug:
            #bruce 050716 debug code (permanent, since this would always indicate a bug)
            if not self.legal_for_atomtypes():
                print_compact_stack("atom_debug: drawing bond %r which is illegal for its atomtypes: " % self)
        if povfile is not None:
            draw_bond_letters = False # not yet supported, and i worry about side effects of env usage tracking
        else:
            draw_bond_letters = not highlighted and env.prefs[ pibondLetters_prefs_key]
        pi_bond_style = env.prefs[ pibondStyle_prefs_key] # one of ['multicyl','vane','ribbon']
        draw_cyls = (pi_bond_style == 'multicyl')
        draw_vanes = not draw_cyls # this is true for either vanes or ribbons
        draw_sigma_cyl = not draw_cyls
        if povfile is not None:
            draw_vanes = False # not yet supported
    else:
        # single bond -- no need to check prefs or set variables for vanes, etc
        draw_cyls = False
        draw_sigma_cyl = True
    draw_bands = draw_cyls # whether to ever draw bands around the cylinders for aromatic/graphite bonds
    if draw_bands:
        v6_for_bands = self.v6
    else:
        v6_for_bands = V_SINGLE
    
    shorten_tubes = highlighted

    dir_info = (0, False) # usual case for non-directional bonds; draws nothing; change this below if necessary
    direction_error = False # change below if necessary
    
    if self._direction: #bruce 070415, revised 071016
        # We might want to show this bond's direction, or (someday)
        # its ability to have one. Figure out what to actually show.

        if not self.is_directional():
            direction_error = True
            # but no sensible way to set dir_info, so leave it as default,
            # partly to avoid other errors in the else case
            # which assumes the bond is directional.
        else:
            # apply this general pref test first, to be faster when it's turned off.
            
            # ninad070504: added the bond arrows preferences to Preferences dialog. 
            # using this preference key instead of debug preference.
                    
                ### POSSIBLE BUG (by experience, not understood in code, not always repeatable):
                # changing this debug_pref [back when the following prefs were debug_prefs]
                # fails to redraw internal bonds accordingly (tho fine for external bonds).
                # This is as if it's not usage tracked by the chunk display list compile,
                # or as if the change to it via the debug menu is not change tracked.
                # Workaround (not very convenient): Undo past where you created the DNA, and redo.
                # Or, probably, just change the chunk display style.
                # The bug is not always repeatable: I changed display to cpk (all arrows gone, finally correct),
                # then back to tubes, then turned arrows on, and this time they all showed up, and again as I try off/on.
                # Maybe it was an artifact of reloading this code??
                # [bruce 070415]
                # update, bruce 071016: could it have been simply that debug_prefs are not change_tracked?
                # I am not sure, but IIRC, they're not.
            
            bool_arrowsOnFivePrimeEnds = env.prefs[arrowsOnFivePrimeEnds_prefs_key]
            bool_arrowsOnThreePrimeEnds = env.prefs[arrowsOnThreePrimeEnds_prefs_key]
            
            # Determine whether cylinders of strand open bonds should be draw.
            # Atom._draw_atom_style() takes care of drawing singlets as 
            # arrowheads (or not drawing them at all) based on these 
            # two user prefs. - mark 2007-10-20.
            if self.isFivePrimeOpenBond():
                if not bool_arrowsOnFivePrimeEnds:
                    # Don't draw bond 5' open bond cylinder.
                    return
            if self.isThreePrimeOpenBond():
                if not bool_arrowsOnThreePrimeEnds:
                    # Don't draw bond 3' open bond cylinder.
                    return
                
            bool_arrowsOnAll = env.prefs[arrowsOnBackBones_prefs_key]

            if bool_arrowsOnAll:
                # draw arrow on bond unless there is some reason not to.

                # If either atom will look like an arrowhead (before prefs are applied) --
                # i.e. if either one is a strand_end -- we don't want the bond to have its
                # own arrowhead. [bruce 071016, feature requested by mark]
                # update, bruce 071018 -- an arrow-atom in front should always suppress self's arrow,
                # but an arrow atom in back should only turn it off if self is an open bond,
                # since we draw the arrow only on the front half of the bond.
                # (Front and back are relative to self's bond_direction.)
                
                # these flags might be changed during the following loop
                direction_error = False 
                suppress_self_arrow_always = False # set by arrowhead in front
                suppress_self_arrow_if_open_bond = False # set by arrowhead in back

                for atom in (self.atom1, self.atom2):
                    # does atom look like an arrowhead (i.e end_bond is not None),
                    # and if so, should that suppress_self_arrow?
                    end_bond = atom.strand_end_bond()
                    if end_bond is self:
                        if atom.is_singlet():
                            suppress_self_arrow_always = True
                        elif self.bond_direction_from(atom) == -1:
                            # atom is in front
                            suppress_self_arrow_always = True
                        else:
                            # atom is in back (since we know self has a direction set)
                            suppress_self_arrow_if_open_bond = True
                    elif end_bond is not None:
                        # end_bond not None or self -- we're directional, but not
                        # the directional bond atom thinks is a strand end! Error or bug,
                        # so always show self's arrow too.
                        ## REVIEW: are there other bond direction errors we need to
                        # indicate as well?
                        direction_error = True
                    continue
                
                if suppress_self_arrow_if_open_bond and self.is_open_bond():
                    suppress_self_arrow_always = True
                
                if direction_error or not suppress_self_arrow_always:
                    dir_info = (self.bond_direction_from(self.atom1), True)
                pass

            pass
        pass
    
    # do calcs common to all bond-cylinders for multi-cylinder bonds

    atom1 = self.atom1
    atom2 = self.atom2
    
    color1 = col or atom1.drawing_color()
    color2 = col or atom2.drawing_color()
##    if 'DEBUG_070602':
##        # indicate bugs in atom.bonds by orange color
##        #e maybe we should leave this code in permanently?? only if mouseover msg explains the color.
##        if self not in self.atom1.bonds:
##            color1 = orange 
##        if self not in self.atom2.bonds:
##            color2 = orange
    bondcolor = col or None ## if None, we look up the value when it's used [bruce 050805]

    if direction_error:
        bondcolor = orange
        #bruce 071016 (tentative -- needs mouseover msg, as said above)
        # (TODO: we could set an error message string on self, but set it to None
        #  whenever not setting the error color; since this is done whenever self
        #  is redrawn, it will always be up to date when highlighting or tooltip
        #  happens.)
   
    v1 = atom1.display != diINVISIBLE
    v2 = atom2.display != diINVISIBLE
        ###e bruce 041104 suspects v1, v2 wrong for external bonds, needs
        # to look at each mol's .hidden (but this is purely a guess)

    # compute geometry (almost always needed eventually, below)
    fix_geom = (povfile is not None) and (atom1.molecule is atom2.molecule)
    if fix_geom:
        # in this case, bond.geom is wrong, needs to be absolute but isn't 
        selfgeom = self._recompute_geom(abs_coords = True)
    else:
        selfgeom = self.geom #e perhaps could be optimized to only compute a1pos, a2pos
    
    howmany = 1 # modified below
    if draw_cyls:
        # Draw 1, 2, or 3 central cyls, depending on bond type (only 1 for aromatic bonds) (#e what's best for carbomeric?)
        # Note: this code sets howmany, and if it's not 1, draws that many cyls;
        # otherwise howmany == 1 is noticed below (not inside this 'if' statement) so the central cyl is drawn.
        howmany = { V_DOUBLE: 2, V_TRIPLE: 3 }.get( self.v6, 1)

        if howmany > 1:
            # figure out where to draw them, and cyl thickness to use; this might depend on disp and/or on sigmabond_cyl_radius
            if fix_geom:
                pi_info = self.get_pi_info(abs_coords = True)
            else:
                pi_info = self.get_pi_info() #k this could probably be the same call as above, with abs_coords = fix_geom
            if pi_info is None:
                howmany = 1 # should never happen; if it does, work around the bug this way
            else:
                ((a1py, a1pz), (a2py, a2pz), ord_pi_y, ord_pi_z) = pi_info # vectors are in bond's coordsys
                del ord_pi_y, ord_pi_z
                pvecs1 = multicyl_pvecs( howmany, a1py, a1pz )
                pvecs2 = multicyl_pvecs( howmany, a2py, a2pz ) # leaves them as unit vectors for now
                if disp == diLINES:
                    scale = 1 # arbitrary, since cylinder thickness is not used when drawing lines
                    offset = 2
                elif disp == diBALL:
                    scale = 1
                    offset = 2 # in units of sigmabond_cyl_radius
                elif disp == diTUBES:
                    scale = 0.333 # I don't like this being so small, but it's in the spec
                    offset = 0.333 * 2
                else:
                    assert 0
                # now modify geom for these other cyls
                a1pos, c1, center, c2, a2pos, toolong = selfgeom
                del c1, center, c2, toolong
                cylrad = scale * sigmabond_cyl_radius
                offset *= sigmabond_cyl_radius # use this offset in the loop
                for pvec1, pvec2 in zip( pvecs1, pvecs2 ):
                    a1posm = a1pos + offset * pvec1
                    a2posm = a2pos + offset * pvec2
                    geom = self.geom_from_posns(a1posm, a2posm) # correct in either abs or rel coords
                    draw_bond_cyl( atom1, atom2, disp, v1, v2, color1, color2, bondcolor, highlighted, level, \
                                   cylrad, shorten_tubes, geom, v6_for_bands, povfile, dir_info, bool_fullBondLength )

    if draw_sigma_cyl or howmany == 1:
        # draw one central cyl, regardless of bond type
        geom = selfgeom #e could be optimized to compute less for CPK case
        cylrad = sigmabond_cyl_radius
        draw_bond_cyl( atom1, atom2, disp, v1, v2, color1, color2, bondcolor, highlighted, level, \
                       cylrad, shorten_tubes, geom, v6_for_bands, povfile, dir_info, bool_fullBondLength)

    if self.v6 != V_SINGLE:
        if draw_vanes:
            if platform.atom_debug:
                import draw_bond_vanes, debug
                debug.reload_once_per_event(draw_bond_vanes) #bruce 050825 renabled this, using reload_once_per_event
            from draw_bond_vanes import draw_bond_vanes
            draw_bond_vanes( self, glpane, sigmabond_cyl_radius, col) # this calls self.get_pi_info()
        if draw_bond_letters and glpane.permit_draw_bond_letters:
            # note: bruce 071023 added glpane.permit_draw_bond_letters to replace
            # this test and remove some import cycles:
            ## isinstance(glpane, MMKitView):
            # [Huaicai 11/14/05: added the MMKitView test to fix bug 969,884]
            #
            # Ideally, it would be better to disable the bond letter feature
            # completely in the MMKit thumbview for Library, but not for single atoms
            # (though those use the same glpane)... could we do this by testing ratio of
            # atomcount to glpane size? or by the controlling code setting a flag?
            # (For now, just ignore the issue, and disable it in all thumbviews.)
            # [bruce 051110/071023]
            try:
                glpane_out = glpane.out
            except AttributeError:
                glpane_out = V(0.0, 0.0, 1.0) # kluge for Element Selector [bruce 050507 bugfix]
            textpos = self.center + glpane_out * 0.6
                # Note -- this depends on the current rotation when the display list is made! But it's ok for now.
                # We could fix this by having a separate display list, or no display list, for these kinds of things --
                # would need a separate display list per chunk and per offset. Not worth it for now.
            text = bond_letter_from_v6(self.v6).upper()
            text_qcolor = QColor(255, 255, 255) # white
            # fontname and fontsize: only some combos work, e.g. Times 10 (maybe) but not 12,
            # and Helvetica 12 but not 10, and this might be platform-dependent; when it fails,
            # for Mac it just draws nothing (bug 1113) but for Windows & Linux it tracebacks (bug 1112).
            # So to fix those bugs, I'm just using the same fontname/fontsize as in all our other renderText calls.
            # (Some of those have pushMatrix but that is not needed.
            #  Most of those disable depth test, but that looks bad here and is also not needed.
            #  We don't call drawer.drawtext since it always disables depth test.)
            # [bruce 051111]
            font = QFont( QString("Helvetica"), 12)
                ###e should adjust fontsize based on scale, depth... (if not for the bugs mentioned above)
                #e should construct font only once, keep in glpane
            glDisable(GL_LIGHTING)
            glpane.qglColor(text_qcolor)
            p = textpos
            glpane.renderText(p[0], p[1], p[2], QString(text), font) #k need explicit QString??
            glEnable(GL_LIGHTING) # bug 969 traceback (not on Mac) claims "illegal OpenGL op" in this line! [as of 051110 night]
    
    return # from draw_bond_main

def multicyl_pvecs( howmany, a2py, a2pz):
    if howmany == 2:
        return [a2py, -a2py] # note, for proper double-bond alignment, this has to be a2py, not a2pz!
    elif howmany == 3:
        return [a2py, - a2py * 0.5 + a2pz * 0.866, - a2py * 0.5 - a2pz * 0.866] # 0.866 is sqrt(3)/2
    else:
        assert 0
    pass

def draw_bond_cyl( atom1, atom2, disp, v1, v2, color1, color2, bondcolor, highlighted, level, \
                   sigmabond_cyl_radius, shorten_tubes, geom, v6, povfile, dir_info, bool_fullBondLength = False ):
    """
    Draw one cylinder, which might be for a sigma bond, or one of 2 or 3 cyls for double or triple bonds.
    [private function for a single caller, which is the only reason such a long arglist is tolerable]
    """
    # Note: bool_fullBondLength represent whether full bond length to be drawn
    # it is used only in select Chunks mode while highlighting the whole chunk and when
    #the atom display is Tubes display -- ninad 070214
    # REVIEW: I think bool_fullBondLength option is not needed,
    # since bool_fullBondLength = True can be implemented (here or preferably in callers)
    # just by passing shorten_tubes = False. [bruce 070920 comment]
    
    a1pos, c1, center, c2, a2pos, toolong = geom
    
    #following turns off the bond stretch indicators based on the user 
    #preference
    bool_showBondStretch = env.prefs[showBondStretchIndicators_prefs_key]
    if not bool_showBondStretch:
        toolong = False
       

    # Figure out banding (only in CPK or Tubes display modes).
    # This is only done in multicyl mode, because caller makes our v6 equal V_SINGLE otherwise.
    # If new color args are needed, they should be figured out here (perhaps by env.prefs lookup).
    # This code ought to be good enough for A6, but if Mark wants to, he and Huaicai can modify it in this file.
    # [bruce 050806]
    if v6 == V_AROMATIC:
        banding = V_AROMATIC # use aromatic banding on this cylinder (bond order 1.5)
        band_color = ave_colors(0.5, green, yellow)
    elif v6 == V_GRAPHITE:
        banding = V_GRAPHITE # use graphite banding on this cylinder (bond order 1.33)
        band_color = ave_colors(0.8, green, yellow)
    elif v6 == V_CARBOMERIC:
        banding = V_AROMATIC # use carbomeric banding on this cylinder (bond order 2.5) (length is same as aromatic for now)
        band_color = ave_colors(0.7, red, white)
    else:
        banding = None # no banding needed on this cylinder
    if banding and disp not in [diBALL, diTUBES]:
        banding = None
    if banding:
        band_order = float(banding - V_SINGLE)/V_SINGLE # 0.33, 0.5, or for carbomeric, in principle 1.5 but in practice 0.5
        bandvec = (a2pos - a1pos)/2.0 # from center to a2pos
        bandextent = band_order/2.5 # if this was 1 we'd cover it entirely; this is measured to atom centers, not just visible part...
        bandpos1 = center - bandvec * bandextent
        bandpos2 = center + bandvec * bandextent
        if highlighted:
            band_color = ave_colors(0.5, band_color, blue)
        band_color = ave_colors(0.8, band_color, black)
    # end of figuring out banding, though to use it, the code below must be modified.

    if povfile is not None:
        # Ideal situation, worth doing when we have time:
        # if povfile had the equivalent of drawcylinder and drawsphere (and took radius prefs into account in tube macros),
        # we could just run the non-povfile code below on it, and get identical pov and non-pov rendering
        # (for bonds, incl multicyl and banded, tho not for vanes/ribbons or bond letters or half-invisible bonds
        #  (with spheres -- not so great a feature anyway)
        #  until other code is modified and povfile has a few more primitives needed for those).
        #
        # Current situation: for povfiles, we just replace the rest of this routine with the old povfile bond code,
        # modified to use macros that take a radius, plus a separate call for banding.
        # This should cover: multiple cyls, banding, radius prefs; but won't cover: color prefs, other fancy things listed above.
        # [bruce 060622]
        # It also doesn't yet cover the debug_pref "draw arrows on all directional bonds?" --
        # i.e. for now that does not affect POV-Ray. [bruce 070415]
        old_writepov_bondcyl(atom1, atom2, disp, a1pos, c1, center, c2, a2pos, toolong, color1, color2, povfile, sigmabond_cyl_radius)
        if banding and disp in (diBALL, diTUBES):
            povfile.drawcylinder(band_color, bandpos1, bandpos2, sigmabond_cyl_radius * 1.2)
        return
    
    if disp == diLINES:
        width = env.prefs[linesDisplayModeThickness_prefs_key] #bruce 050831
        if width <= 0:
            # fix illegal value to prevent exception
            width = 1
        if not toolong:
            drawline(color1, a1pos, center, width = width)
            drawline(color2, a2pos, center, width = width)
        else:
            drawline(color1, a1pos, c1, width = width)
            drawline(color2, a2pos, c2, width = width)
            toolong_color = env.prefs.get( bondStretchColor_prefs_key)
                # toolong_color is never highlighted here, since we're not sure highlighting bonds in LINES mode is good at all
            drawline( toolong_color, c1, c2, width = width)
    elif disp == diBALL:
        if bondcolor is None: #bruce 050805
            bondcolor = env.prefs.get( diBALL_bondcolor_prefs_key) ## bondColor [before bruce 050805]
        drawcylinder(bondcolor, a1pos, a2pos, sigmabond_cyl_radius)
        if banding:
            drawcylinder(band_color, bandpos1, bandpos2, sigmabond_cyl_radius * 1.2)
    elif disp == diTUBES:
        if shorten_tubes:
            rad = TubeRadius * 1.1 * 0.9 # see Atom.howdraw for tubes; the constant (0.9) might need adjusting
                #bruce 050726 changed that constant from 1.0 to 0.9
            vec = norm(a2pos-a1pos) # warning: if atom1 is a singlet, a1pos == center, so center-a1pos is not good to use here.
            if atom1.element is not Singlet:
                    if not bool_fullBondLength:
                            a1pos = a1pos + vec * rad
            if atom2.element is not Singlet:
                    if not bool_fullBondLength:
                            a2pos = a2pos - vec * rad
            # note: this does not affect bandpos1, bandpos2 (which is good)
        ###e bruce 050513 future optim idea: when color1 == color2, draw just
        # one longer cylinder, then overdraw toolong indicator if needed.
        # Significant for big parts. BUT, why spend time on this when I
        # expect we'll do this drawing in C code before too long?

        if not toolong:
            if v1 and v2 and (not color1 != color2): # "not !=" is in case colors are Numeric arrays (don't know if possible)
                #bruce 050516 optim: draw only one cylinder in this common case
                drawcylinder(color1, a1pos, a2pos, sigmabond_cyl_radius)
            else:
                if v1:
                    drawcylinder(color1, a1pos, center, sigmabond_cyl_radius)
                if v2:
                    drawcylinder(color2, center, a2pos, sigmabond_cyl_radius)
                        #bruce 070921 bugfix: draw in consistent direction! This affects
                        # alignment of cylinder cross section (a 13-gon)
                        # around cylinder axis. Highlighted bond might differ
                        # from regular bond in whether color1 != color2,
                        # so without this fix, it can be slightly rotated,
                        # causing part of the unhighlighted one to show through.
                if not (v1 and v2):
                    drawsphere(black, center, sigmabond_cyl_radius, level)
        else:
            if highlighted:
                toolong_color = _default_toolong_hicolor ## not yet in prefs db
            else:
                toolong_color = env.prefs.get( bondStretchColor_prefs_key)
            drawcylinder(toolong_color, c1, c2, sigmabond_cyl_radius)
            if v1:
                drawcylinder(color1, a1pos, c1, sigmabond_cyl_radius)
            else:
                drawsphere(black, c1, sigmabond_cyl_radius, level)
            if v2:
                drawcylinder(color2, c2, a2pos, sigmabond_cyl_radius)
                    #bruce 070921 bugfix: draw in consistent direction! See comment above.
            else:
                drawsphere(black, c2, sigmabond_cyl_radius, level)
        if banding:
            drawcylinder(band_color, bandpos1, bandpos2, sigmabond_cyl_radius * 1.2)
        pass

    # maybe draw arrowhead showing bond direction [bruce 070415]
    direction, is_directional = dir_info
    if (direction or is_directional) and (disp in (diBALL, diTUBES)):        
        # If the bond has a direction, draw an arrowhead in the middle of the bond-cylinder to show it.
        # (Make that gray if this is ok, or red if this is a non-directional bond.)
        # If it has no direction but "wants one" (is_directional), draw something to indicate that, not sure what. ##e
        if direction < 0:
            a1pos, a2pos = a2pos, a1pos ###e should move into submethod to avoid error if these are used lower down
            direction = - direction
            color1, color2 = color2, color1
        error = direction and not is_directional
        if error:
            color = red
        else:
            color = color2
        if direction == 0:
            pass # print "draw a confused/unknown direction somehow" # two orange arrows? no arrow?
        else:            
            # draw arrowhead pointing from a1pos to a2pos, closer to a2pos.
            pos = a1pos
            axis = a2pos - a1pos
            drawrad = sigmabond_cyl_radius
            drawsphere(color, pos + 0.8 * axis, drawrad * 0.1, 1) ###KLUGE to set color
            glePolyCone([[pos[0] + 0.5 * axis[0], pos[1] + 0.5 * axis[1],
                          pos[2] + 0.5 * axis[2]],
                         [pos[0] + 0.6 * axis[0], pos[1] + 0.6 * axis[1],
                          pos[2] + 0.6 * axis[2]],
                         [pos[0] + 1.0 * axis[0], pos[1] + 1.0 * axis[1],
                          pos[2] + 1.0 * axis[2]],
                         [pos[0] + 1.1 * axis[0], pos[1] + 1.1 * axis[1],
                          pos[2] + 1.1 * axis[2]]], # Point array (the two end
                                                    # points not drawn)
                        None, # Color array (None means use current the color)
                        [drawrad * 2, drawrad * 2, 0, 0] # Radius array
                       )
        pass

    return # from draw_bond_cyl

# ==

def writepov_bond(self, file, dispdef, col):
    """
    Write this bond 'self' to a povray file (always using absolute coords, even for internal bonds).
    """
    disp = max(self.atom1.display, self.atom2.display)
    if disp == diDEFAULT:
        disp = dispdef
    if disp < 0:
        disp = dispdef
    if disp in (diLINES, diBALL, diTUBES):
        # (note: self is a bond.)
        povfile = writepov_to_file(file, col)
        level = 2 #k value probably has no effect
        glpane = None #k value probably has no effect
        highlighted = False
        draw_bond_main( self, glpane, disp, col, level, highlighted, povfile)
    return

def old_writepov_bondcyl(atom1, atom2, disp, a1pos, c1, center, c2, a2pos, toolong, color1, color2, povfile, rad = None):
    """
    [private function for this module, still used by new multicyl code 060622, once per cyl]
    Write one bond cylinder. atom args are only for checking rcovs vs DELTA. 
    """
    if disp == diLINES:
        if not toolong:
            povfile.line(a1pos, a2pos, color1)
        else:
            povfile.line(a1pos, center, color1)
            povfile.line(center, a2pos, color2)
    if disp == diBALL:
        bondColor = povfile.getBondColor()
        if not bondColor:
            bondColor = color1
        povfile.bond(a1pos, a2pos, bondColor, rad)
    if disp == diTUBES:
        #Huaicai: If rcovalent is close to 0, like singlets, avoid 0 length 
        # cylinder written to a pov file    
        DELTA = 1.0E-5
        isSingleCylinder = False
        if atom1.atomtype.rcovalent < DELTA:
                col = color2
                isSingleCylinder = True
        if atom2.atomtype.rcovalent < DELTA:
                col = color1
                isSingleCylinder = True
        if isSingleCylinder:
            povfile.tube3(a1pos, a2pos, col, rad)
        else:
            if not toolong:
                povfile.tube2(a1pos, color1, center, a2pos, color2, rad)
            else:
                povfile.tube1(a1pos, color1, c1, c2, a2pos, color2, rad)
    return # from old_writepov_bondcyl

# end
