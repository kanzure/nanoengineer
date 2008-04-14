# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaCylinderChunks.py -- defines I{DNA Cylinder} display mode, which draws 
axis chunks as a cylinder in the chunk's color.

@author: Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 

This is still considered experimental.

Initially, this is mainly intended as a fast-rendering display mode for DNA.
When the DNA data model become operative, this class will be implemented
to give faster and better ways to compute the axis path and render the
cylinder.

To do:
- Add new user pref for "DNA Cylinder Radius".
- Fix limitations/bugs listed in the class docstring.

History:

Mark 2008-02-12: Created by making a copy of CylinderChunks.py

piotr 080310: I have rewritten most of the code here from scratch. Most of 
the code computed within this function has to be moved to "getmemo" 
for a speed optimization. There are several issues with this rendering code,
including lack of highlighting and selection support, and some
weird behavior when modeltree is used to select individual strands.

The DNA display style requires DNA updater to be enabled.

There are four independent structures within the DNA display style:
axis, strands, struts and bases. Properties of these parts can be set
in the User Preferences dialog.

piotr 080317: Added POV-Ray rendering routines.

piotr 080318: Moved most of the data generation code to "getmemo"
Highlighting and selection now works. Thank you, Ninad!!!

("rainbow" strands still can't be selected nor highlighted, this will 
be fixed later)

piotr 080328: Added several "interactive" features: labels, base orientation
indicators, "2D" style.

"""

from Numeric import dot, argmax, argmin, sqrt

import sys
import foundation.env as env
import graphics.drawing.drawer as drawer
from geometry.geometryUtilities import matrix_putting_axis_at_z
from geometry.VQT import V, Q, norm, cross, angleBetween
from utilities.debug import print_compact_traceback
from graphics.display_styles.displaymodes import ChunkDisplayMode
from utilities.constants import ave_colors, black, red, blue, white, yellow, darkgreen

from utilities.debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False

from utilities.prefs_constants import atomHighlightColor_prefs_key

# piotr 080309: user pereferences for DNA style
from utilities.prefs_constants import dnaStyleStrandsColor_prefs_key
from utilities.prefs_constants import dnaStyleAxisColor_prefs_key
from utilities.prefs_constants import dnaStyleStrutsColor_prefs_key
from utilities.prefs_constants import dnaStyleBasesColor_prefs_key
from utilities.prefs_constants import dnaStyleStrandsShape_prefs_key
from utilities.prefs_constants import dnaStyleBasesShape_prefs_key
from utilities.prefs_constants import dnaStyleStrandsArrows_prefs_key
from utilities.prefs_constants import dnaStyleAxisShape_prefs_key
from utilities.prefs_constants import dnaStyleStrutsShape_prefs_key
from utilities.prefs_constants import dnaStyleStrandsScale_prefs_key
from utilities.prefs_constants import dnaStyleAxisScale_prefs_key
from utilities.prefs_constants import dnaStyleBasesScale_prefs_key
from utilities.prefs_constants import dnaStyleAxisTaper_prefs_key
from utilities.prefs_constants import dnaStyleStrutsScale_prefs_key

# piotr 080325 added more user preferences
from utilities.prefs_constants import dnaStrandLabelsEnabled_prefs_key
from utilities.prefs_constants import dnaStrandLabelsColor_prefs_key
from utilities.prefs_constants import dnaStrandLabelsColorMode_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsEnabled_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsColor_prefs_key
from utilities.prefs_constants import dnaBaseInvIndicatorsEnabled_prefs_key
from utilities.prefs_constants import dnaBaseInvIndicatorsColor_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsAngle_prefs_key
from utilities.prefs_constants import dnaBaseIndicatorsDistance_prefs_key

from utilities.prefs_constants import dnaStyleBasesDisplayLetters_prefs_key

from model.elements import Singlet
from math import sin, cos, pi
from Numeric import zeros, Float, Float32

try:
    from OpenGL.GLE import glePolyCone
    from OpenGL.GLE import gleGetNumSides 
    from OpenGL.GLE import gleSetNumSides 
    from OpenGL.GLE import gleExtrusion
    from OpenGL.GLE import gleTwistExtrusion
    from OpenGL.GLE import glePolyCylinder 
    from OpenGL.GLE import gleSetJoinStyle
    from OpenGL.GLE import TUBE_NORM_EDGE 
    from OpenGL.GLE import TUBE_NORM_PATH_EDGE 
    from OpenGL.GLE import TUBE_JN_ROUND
    from OpenGL.GLE import TUBE_JN_ANGLE
    from OpenGL.GLE import TUBE_CONTOUR_CLOSED 
    from OpenGL.GLE import TUBE_JN_CAP 
except:
    print "DNA Cylinder: GLE module can't be imported. Now trying _GLE"
    from OpenGL._GLE import glePolyCone 
    from OpenGL._GLE import gleGetNumSides 
    from OpenGL._GLE import gleSetNumSides 
    from OpenGL._GLE import gleExtrusion
    from OpenGL._GLE import gleTwistExtrusion    
    from OpenGL._GLE import glePolyCylinder 
    from OpenGL._GLE import gleSetJoinStyle
    from OpenGL._GLE import TUBE_NORM_EDGE 
    from OpenGL._GLE import TUBE_NORM_PATH_EDGE 
    from OpenGL._GLE import TUBE_JN_ROUND
    from OpenGL._GLE import TUBE_JN_ANGLE
    from OpenGL._GLE import TUBE_CONTOUR_CLOSED 
    from OpenGL._GLE import TUBE_JN_CAP 

import colorsys
from OpenGL.GL import glBegin
from OpenGL.GL import glEnd
from OpenGL.GL import glVertex3f
from OpenGL.GL import glColor3f
from OpenGL.GL import glColor3fv
from OpenGL.GL import glTranslatef
from OpenGL.GL import GL_LINE_STRIP        
from OpenGL.GL import GL_LINES
from OpenGL.GL import GL_POLYGON
from OpenGL.GL import glEnable
from OpenGL.GL import glDisable
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_SMOOTH
from OpenGL.GL import glShadeModel
from OpenGL.GL import GL_COLOR_MATERIAL
from OpenGL.GL import GL_TRIANGLES
from OpenGL.GL import GL_FRONT_AND_BACK
from OpenGL.GL import GL_AMBIENT_AND_DIFFUSE
from OpenGL.GL import glMaterialfv
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glRotatef
from OpenGL.GL import glScalef
from OpenGL.GL import glLineWidth
from OpenGL.GL import GL_QUADS

from OpenGL.GLU import gluUnProject

from dna.model.DnaLadderRailChunk import DnaStrandChunk

from model.chunk import Chunk

chunkHighlightColor_prefs_key = atomHighlightColor_prefs_key # initial kluge

class DnaCylinderChunks(ChunkDisplayMode):
    """
    DNA Cylinder display mode, which draws "axis" chunks as a cylinder.

    Limitations/known bugs:
    - Cylinders are always straight. DNA axis chunks with atoms that are not 
    aligned in a straight line are not displayed correctly (i.e. they don't
    follow a curved axis path. fixed 080310 piotr
    - Hover highlighting does not work. fixed 080318: thank you, Ninad!!! 
    - Selected chunks are not colored in the selection color. same as above
    - Cannot drag/move a selected cylinder interactively. same as above
    - DNA Cylinders are not written to POV-Ray file. piotr: done 080317
    - DNA Cylinders are not written to PDB file and displayed in QuteMolX.
    piotr: to be done

    @note: Nothing else is rendered (no atoms, sugar atoms, etc) when 
        set to this display mode. piotr 080316: some feature can be displayed
        as "bases"

    @attention: This is still considered experimental.
    """
    # mmp_code must be a unique 3-letter code, distinct from the values in 
    # constants.dispNames or in other display modes
    mmp_code = 'dna'  
    disp_label = 'DNA Cylinder' # label for statusbar fields, menu text, etc.
    featurename = "Set Display DNA Cylinder"
    # Pretty sure Bruce's intention is to define icons for subclasses
    # of ChunkDisplayMode here, not in mticon_names[] and hideicon_names[] 
    # in chunks.py. Ask him to be sure. Mark 2008-02-12
    icon_name = "modeltree/DnaCylinder.png"
    hide_icon_name = "modeltree/DnaCylinder-hide.png"
    ### also should define icon as an icon object or filename, 
    ### either in class or in each instance
    ### also should define a featurename for wiki help
    def spline(self, data, idx, t):
        """
        Implements a Catmull-Rom spline.
        Interpolates between data[idx] and data[idx+1].
        0.0 <= t <= 1.0.
        """
        t2 = t*t
        t3 = t2*t
        x0 = data[idx-1]
        x1 = data[idx]
        x2 = data[idx+1]
        x3 = data[idx+2]
        res = 0.5*((2.0*x1)+
                   t*(-x0+x2)+
                   t2*(2.0*x0-5.0*x1+4.0*x2-x3)+
                   t3*(-x0+3.0*x1-3.0*x2+x3))
        return res

    def getRainbowColor(self, hue, saturation, value):
        """
        Gets a color of a hue range limited to 0 - 0.667 (red - blue)
        """

        hue = 0.666*(1.0-hue)
        if hue < 0.0: 
            hue = 0.0
        if hue > 0.666: 
            hue = 0.666
        return colorsys.hsv_to_rgb(hue, saturation, value)

    def getFullRainbowColor(self, hue, saturation, value):
        """
        Gets a color of a full hue range.
        """
        if hue<0.0: hue=0.0
        if hue>1.0: hue=1.0
        return colorsys.hsv_to_rgb(hue, saturation, value)

    def getBaseColor(self, base):
        """
        Returns a color according to DNA base type.
        Two-ring bases (G and A) have darker colors.
        G = red
        C = orange
        A = blue
        T = cyan
        """
        if base=="G":
            return ([1.0,0.0,0.0])
        elif base=="C":
            return ([1.0,0.5,0.0])
        if base=="A":
            return ([0.0,0.3,0.9])
        elif base=="T":
            return ([0.0,0.7,0.8])
        else:
            return ([0.5,0.5,0.5])

    def getRainbowColorInRange(self, pos, count, saturation, value):
        if count>1: count -= 1
        hue = float(pos)/float(count)        
        if hue<0.0: hue = 0.0
        if hue>1.0: hue = 1.0
        return self.getRainbowColor(hue, saturation, value)

    def getFullRainbowColorInRange(self, pos, count, saturation, value):
        if count>1: count -= 1
        hue = float(pos)/float(count)        
        if hue<0.0: hue = 0.0
        if hue>1.0: hue = 1.0
        return self.getFullRainbowColor(hue, saturation, value)

    def drawchunk(self, glpane, chunk, memo, highlighted):
        """
        Draw chunk in glpane in the whole-chunk display mode represented by 
        this ChunkDisplayMode subclass.

        Assume we're already in chunk's local coordinate system (i.e. do all
        drawing using atom coordinates in chunk.basepos, not chunk.atpos).

        If highlighted is true, draw it in hover-highlighted form (but note 
        that it may have already been drawn in unhighlighted form in the same
        frame, so normally the highlighted form should augment or obscure the
        unhighlighted form).

        Draw it as unselected, whether or not chunk.picked is true. See also
        self.drawchunk_selection_frame. (The reason that's a separate method
        is to permit future drawing optimizations when a chunk is selected
        or deselected but does not otherwise change in appearance or position.)

        If this drawing requires info about chunk which it is useful to 
        precompute (as an optimization), that info should be computed by our
        compute_memo method and will be passed as the memo argument
        (whose format and content is whatever self.compute_memo returns). 
        That info must not depend on the highlighted variable or on whether
        the chunk is selected.        
        """

        def drawStrand(points, colors, radii, dir, draw5p, draw3p,
                       color_style, shape, arrows):
            """
            Renders a strand shape along points array using colors 
            and radii arrays, with optional arrows. 

            draw5p and draw3p control arrow drawing at 5' and 3' ends.
            shape controls the strand apperance (0=cylinders, 1=tube)
            """
            n = len(points)
            if n>3:
                # copy colors and radii
                colors[0] = colors[1]
                colors[n-1] = colors[n-2]
                radii[0] = radii[1]
                radii[n-1] = radii[n-2]
                # draw the terminal spheres
                drawer.drawsphere(colors[1],points[1],radii[1],2) 
                drawer.drawsphere(colors[n-2],points[n-2],radii[1],2) 
                # draw the arrows
                if dir==1:
                    if draw5p and (arrows==1 or arrows==3):
                        qbond = 0.25 * (points[2] - points[1])
                        drawer.drawpolycone(colors[1],
                                            [points[1] + qbond,
                                             points[1] + qbond,
                                             points[1] - qbond,
                                             points[1] - qbond],
                                             [0.0, 0.0, 
                                              radii[1]*2.0, radii[1]*2.0])
                    if draw3p and (arrows==2 or arrows==3):
                        hbond = 0.5 * (points[n-3] - points[n-2])
                        drawer.drawpolycone(colors[n-2],
                                            [points[n-2],
                                             points[n-2],
                                             points[n-2] - hbond,
                                             points[n-2] - hbond],
                                             [radii[1]*2.0, radii[1]*2.0, 
                                              0.0, 0.0])
                if dir==-1:
                    if draw3p and (arrows==2 or arrows==3):
                        hbond = 0.5 * (points[2] - points[1])
                        drawer.drawpolycone(colors[1],
                                            [points[1],
                                             points[1],
                                             points[1] - hbond,
                                             points[1] - hbond],
                                             [radii[1]*2.0, radii[1]*2.0, 
                                              0.0, 0.0])
                    if draw5p and (arrows==1 or arrows==3):
                        qbond = 0.25 * (points[n-3] - points[n-2])
                        drawer.drawpolycone(colors[n-2],
                                            [points[n-2] + qbond,
                                             points[n-2] + qbond,
                                             points[n-2] - qbond,
                                             points[n-2] - qbond],
                                             [0.0, 0.0, 
                                              radii[1]*2.0, radii[1]*2.0])

                if shape==1: # draw cylinders
                    gleSetJoinStyle(TUBE_JN_ROUND | TUBE_NORM_PATH_EDGE 
                                    | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED)        
                    if color_style==1:
                        drawer.drawpolycone_multicolor(colors[1], 
                                                       points,
                                                       colors,
                                                       radii)
                    else:
                        drawer.drawpolycone(colors[1], 
                                            points,
                                            radii)
                elif shape==2: # draw spline tube
                    gleSetJoinStyle(TUBE_JN_ANGLE | TUBE_NORM_PATH_EDGE 
                                    | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED) 

                    new_points = [ None ] * (4*(n-2)-1)
                    new_colors = [ None ] * (4*(n-2)-1)
                    new_radii = [ 0.0 ] * (4*(n-2)-1)
                    for p in range(0, (4*(n-2)-1)):
                        new_points[p] = [ 0.0 ] * 3
                        new_colors[p] = [ 0.0 ] * 3

                    o = 1
                    for p in range (1,n-2):
                        for m in range (0,4):
                            t = float(m)/4.0
                            new_points[o] = self.spline(points, p, t)
                            new_colors[o] = self.spline(colors, p, t)
                            new_radii[o] = self.spline(radii, p, t)
                            o += 1        
                    new_points[o] = self.spline(points, p, 1.0)
                    new_colors[o] = self.spline(colors, p, 1.0)
                    new_radii[o] = self.spline(radii, p, 1.0)
                    o += 1
                    new_points[0] = 3.0*new_points[1]-3.0*new_points[2]+new_points[3] 
                    new_points[o] = 3.0*new_points[o-1]-3.0*new_points[o-2]+new_points[o-3] 
                    # draw the tube
                    if color_style==1:
                        drawer.drawpolycone_multicolor(
                            colors[1], new_points, new_colors, new_radii)
                    else:
                        drawer.drawpolycone(
                            colors[1], new_points, new_radii)

        def get_axis_positions(atom_list, color_style):
            """
            From an atom list create a list of positions
            extended by two dummy positions at both ends.
            """
            n_atoms = len(atom_list)
            if color_style==2 or color_style==3: # discrete colors
                positions = [None] * (2*n_atoms+2)
                pos = 2
                for i in range (1, n_atoms):
                    pos1 = chunk.abs_to_base(atom_list[i-1].posn())#-chunk.center
                    pos2 = chunk.abs_to_base(atom_list[i].posn())                
                    positions[pos] = 0.5*(pos1+pos2)
                    positions[pos+1] = 0.5*(pos1+pos2)
                    pos += 2
                positions[1] = chunk.abs_to_base(atom_list[0].posn())
                positions[0] = 2*positions[1] - positions[2]
                positions[pos] = chunk.abs_to_base(atom_list[n_atoms-1].posn())
                positions[pos+1] = 2*positions[pos] - positions[pos-1]
            else:    
                positions = [None] * (n_atoms+2)
                for i in range(1, n_atoms+1):
                    positions[i] = chunk.abs_to_base(atom_list[i-1].posn())
                positions[0] = 2*positions[1] - positions[2]
                positions[n_atoms+1] = 2*positions[n_atoms] - positions[n_atoms-1]
            return positions

        def get_axis_atom_color_per_base(pos, strand_atoms_lists):
            """
            If the axis cylinder is colored 'per base', it uses two distinct
            colors: orange for G-C pairs, and teal for A-T pairs.
            Unknown bases are colored gray. 
            """
            color = [0.5, 0.5, 0.5]
            if len(strand_atoms_lists) > 1:
                if strand_atoms_lists[0] and strand_atoms_lists[1]:
                    len1 = len(strand_atoms_lists[0])
                    len2 = len(strand_atoms_lists[1])
                    if pos>=0 and pos<len1 and pos<len2:
                        base_name = strand_atoms_lists[0][pos].getDnaBaseName()
                        if base_name=='A' or base_name=='T':
                            color = [0.0, 1.0, 0.5]
                        elif base_name=='G' or base_name=='C':
                            color = [1.0, 0.5, 0.0]
            return color                    

        def get_axis_colors(atom_list, strand_atoms_lists, color_style):
            """
            Create a list of colors from atom list.
            """
            n_atoms = len(atom_list)
            if color_style==2 or color_style==3: # discrete colors
                colors = [None] * (2*n_atoms+2)
                pos = 2
                for i in range (1, n_atoms):
                    if color_style==2: 
                        color1 = self.getRainbowColorInRange(
                            i-1, n_atoms, 0.75, 1.0)
                        color2 = self.getRainbowColorInRange(
                            i, n_atoms, 0.75, 1.0)
                    elif color_style==3:
                        color1 = get_axis_atom_color_per_base(
                            i-1, strand_atoms_lists)
                        color2 = get_axis_atom_color_per_base(
                            i, strand_atoms_lists)
                    colors[pos] = color1
                    colors[pos+1] = color2
                    pos += 2
                colors[1] = colors[2] 
                colors[0] = colors[1] 
                colors[pos] = colors[pos-1] 
                colors[pos+1] = colors[pos] 
            else:
                colors = [None] * (n_atoms+2)
                if color_style==1:                    
                    for i in range(1, n_atoms+1):
                        colors[i] = self.getRainbowColorInRange(
                            i, n_atoms, 0.75, 1.0)
                elif color_style==4:
                    for i in range(1, n_atoms+1):
                        colors[i] = group_color
                else:
                    for i in range(1, n_atoms+1):
                        colors[i] = chunk_color
                colors[0] = colors[1]
                colors[n_atoms+1] = colors[n_atoms]

            return colors

        def get_axis_radii(atom_list, color_style, shape, scale, taper):
            """
            Create a list of radii from atom list.
            """
            if shape==1:
                rad = 7.0*scale
            else:    
                rad = 2.0*scale
            n_atoms = len(atom_list)
            if color_style==2 or color_style==3: # discrete colors
                length = 2*n_atoms+2
                radii = [rad] * (length)
                if taper==2 or taper==3:
                    radii[1] = 0.0
                    radii[2] = 0.5*rad
                    radii[3] = 0.5*rad
                if taper==1 or taper==3:
                    radii[length-4] = 0.5*rad
                    radii[length-3] = 0.5*rad
                    radii[length-2] = 0.0
            else:
                length = n_atoms+2
                radii = [rad] * (length)
                if taper==2 or taper==3:
                    radii[1] = 0.0
                    radii[2] = 0.66*rad
                if taper==1 or taper==3:
                    radii[length-3] = 0.66*rad
                    radii[length-2] = 0.0        

            return radii

        def get_strand_positions(atom_list):
            """
            From an atom list create a list of positions
            extended by two dummy positions at both ends.
            """
            n_atoms = len(atom_list)
            positions = [None] * (n_atoms+2)
            for i in range(1, n_atoms+1):
                positions[i] = chunk.abs_to_base(atom_list[i-1].posn())
            if n_atoms < 2:
                positions[0] = positions[1]
                positions[n_atoms+1] = positions[n_atoms]
            else:
                positions[0] = 2 * positions[1] - positions[2]
                positions[n_atoms+1] = 2 * positions[n_atoms] - positions[n_atoms-1]
            return positions

        def get_atom_rainbow_color(atom_idx, start, end, length):
            """ 
            Calculates a single atom "rainbow" color.
            This code is partially duplicated in get_strand_colors.
            """
            if n_atoms > 1:
                step = float(end-start)/float(n_atoms-1)
            else:
                step = 0.0
            if length > 1:
                ilength = 1.0 / float(length-1)
            else:
                ilength = 1.0
            q = ilength * (start + step * idx)
            return self.getRainbowColor(q, 0.75, 1.0)
        pass

        def get_strand_colors(atom_list, color_style, start, end, length):
            """
            From an atom list create a list of colors
            extended by two dummy positions at both ends.
            """
            n_atoms = len(atom_list)
            colors = [None] * (n_atoms+2)
            pos = 0
            if n_atoms > 1:
                step = float(end-start)/float(n_atoms-1)
            else:
                step = 0.0
            if length > 1:
                ilength = 1.0 / float(length-1)
            else:
                ilength = 1.0
            r = start
            for i in range(0, n_atoms):
                if color_style == 0:
                    col = chunk_color
                elif color_style == 1:
                    q =  r * ilength               
                    col = self.getRainbowColor(q, 0.75, 1.0)
                    r += step
                else:
                    col = group_color
                colors[i+1] = V(col[0], col[1], col[2])
                # Has to convert to array otherwise spline interpolation
                # doesn't work (?).
            colors[0] = colors[1]
            colors[n_atoms+1] = colors[n_atoms]
            return colors
        pass

        def get_strand_radii(atom_list, radius):
            """
            From an atom list create a list of radii
            extended by two dummy positions at both ends.
            """
            n_atoms = len(atom_list)
            radii = [None] * (n_atoms+2)
            for i in range(1, n_atoms+1):
                radii[i] = radius
            radii[0] = radii[1]
            radii[n_atoms+1] = radii[n_atoms]
            return radii
        pass

        # ---------------------------------------------------------------------

        chunk._dnaStyleExternalBonds = []

        if not memo: # nothing to render
            return

        if self.dnaExperimentalModeEnabled: 
            # experimental mode is drawn in drawchunk_realtime
            return

        strand_atoms, axis_atoms, \
                    five_prime_atom, three_prime_atom, strand_direction, \
                    start_index, end_index, total_strand_length, \
                    chunk_color, group_color, current_strand = memo

        # render the axis cylinder        
        if chunk.isAxisChunk(): # this is the DNA axis
            axis_positions = get_axis_positions(
                axis_atoms, self.dnaStyleAxisColor)
            axis_colors = get_axis_colors(
                axis_atoms, strand_atoms, self.dnaStyleAxisColor)
            axis_radii = get_axis_radii(axis_atoms, 
                                        self.dnaStyleAxisColor, 
                                        self.dnaStyleAxisShape,
                                        self.dnaStyleAxisScale,
                                        self.dnaStyleAxisTaper)
            n_points = len(axis_positions)
            if self.dnaStyleAxisShape>0:
                # spherical ends    
                if self.dnaStyleAxisTaper==4:
                    drawer.drawsphere(axis_colors[1], 
                                      axis_positions[1], 
                                      axis_radii[1], 2)
                    drawer.drawsphere(axis_colors[n_points-2], 
                                      axis_positions[n_points-2], 
                                      axis_radii[n_points-2], 2)                    
                # set polycone parameters
                gleSetJoinStyle(TUBE_JN_ANGLE | TUBE_NORM_PATH_EDGE 
                                | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED) 
                # draw the polycone                
                if self.dnaStyleAxisColor==1 or self.dnaStyleAxisColor==2 \
                   or self.dnaStyleAxisColor==3: # render discrete colors                
                    drawer.drawpolycone_multicolor(axis_colors[1], 
                                                   axis_positions, 
                                                   axis_colors, 
                                                   axis_radii)
                else:   
                    drawer.drawpolycone(axis_colors[1], 
                                        axis_positions, 
                                        axis_radii)

        elif chunk.isStrandChunk(): # strands, struts and bases 
            strand_positions = get_strand_positions(strand_atoms[current_strand])
            strand_colors = get_strand_colors(
                strand_atoms[current_strand], 
                self.dnaStyleStrandsColor,
                start_index, end_index, total_strand_length)
            strand_radii = get_strand_radii(
                strand_atoms[current_strand], self.dnaStyleStrandsScale)

            n_atoms = len(strand_atoms[current_strand])

            if strand_direction==1:
                draw_5p = (strand_atoms[current_strand][0]==five_prime_atom)
                draw_3p = (strand_atoms[current_strand][n_atoms-1]==three_prime_atom)
            else:
                draw_5p = (strand_atoms[current_strand][n_atoms-1]==five_prime_atom)
                draw_3p = (strand_atoms[current_strand][0]==three_prime_atom)

            # render struts
            if self.dnaStyleStrutsShape>0:
                strand_num = len(chunk.ladder.strand_rails)
                if strand_num>1:
                    strand_atoms = [None, None]
                    strand_atoms[0] = chunk.ladder.strand_rails[0].baseatoms
                    strand_atoms[1] = chunk.ladder.strand_rails[1].baseatoms
                    if strand_atoms[0][0].molecule==chunk:
                        current_strand = 0
                    else:
                        current_strand = 1
                    axis_atoms = chunk.ladder.axis_rail.baseatoms
                    n_atoms = len(chunk.ladder.strand_rails[current_strand])
                    for pos in range(0, n_atoms):
                        atom1 = strand_atoms[current_strand][pos]
                        atom3 = strand_atoms[1-current_strand][pos]
                        if self.dnaStyleStrutsShape==1: # strand-axis-strand
                            atom2_pos = chunk.abs_to_base(axis_atoms[pos].posn())   
                        elif self.dnaStyleStrutsShape==2: # strand-strand
                            atom2_pos = chunk.abs_to_base(0.5 * (atom1.posn() + atom3.posn()))
                        if self.dnaStyleStrutsColor == 0:
                            color = chunk_color
                        elif self.dnaStyleStrutsColor == 1:
                            color = self.getRainbowColorInRange(
                                pos, n_atoms, 0.75, 1.0)                        
                        else:
                            color = self.getBaseColor(atom1.getDnaBaseName())
                        drawer.drawcylinder(
                            color, chunk.abs_to_base(atom1.posn()), atom2_pos, 
                            0.5*self.dnaStyleStrutsScale, True)

            # render bases
            if self.dnaStyleBasesShape>0:
                num_strands = len(strand_atoms)
                for pos in range(0, n_atoms):
                    atom = strand_atoms[current_strand][pos]
                    if self.dnaStyleBasesColor==0:
                        color = chunk_color
                    elif self.dnaStyleBasesColor==1:
                        color = self.getRainbowColorInRange(pos, n_atoms, 0.75, 1.0)
                    elif self.dnaStyleBasesColor==2:
                        color = group_color
                    else:
                        color = self.getBaseColor(atom.getDnaBaseName())
                    if self.dnaStyleBasesShape==1: # draw spheres
                        drawer.drawsphere(color, chunk.abs_to_base(atom.posn()),
                                          self.dnaStyleBasesScale, 2)
                    elif self.dnaStyleBasesShape==2 and num_strands>1: # draw a schematic 'cartoon' shape
                        atom1_pos = chunk.abs_to_base(strand_atoms[current_strand][pos].posn())
                        atom3_pos = chunk.abs_to_base(strand_atoms[1-current_strand][pos].posn())                        
                        atom2_pos = chunk.abs_to_base(axis_atoms[pos].posn())                        
                        # figure out a normal to the bases plane
                        v1 = atom1_pos-atom2_pos
                        v2 = atom1_pos-atom3_pos
                        normal = norm(cross(v1,v2))
                        aposn = atom1_pos+0.50*(atom2_pos-atom1_pos)
                        bposn = atom1_pos+0.66*(atom2_pos-atom1_pos)
                        cposn = atom1_pos+0.75*(atom2_pos-atom1_pos)
                        drawer.drawcylinder(
                            color, 
                            atom1_pos, 
                            bposn, 
                            0.20*self.dnaStyleBasesScale, True)
                        drawer.drawcylinder(
                            color, 
                            bposn-0.25*self.dnaStyleBasesScale*normal,
                            bposn+0.25*self.dnaStyleBasesScale*normal,
                            1.0*self.dnaStyleBasesScale, True)


            if self.dnaStyleStrandsShape>0: # render strands
                # Render the external bonds, if there are any.
                # Moved this to draw_realtime otherwise the struts won't be updated.
                # piotr 080411

                # It is a kludge. These bonds may need to be drawn in draw_realtime
                # to reflect orientation changes of the individual chunks.                
                for bond in chunk.externs:
                    if bond.atom1.molecule.dad == bond.atom2.molecule.dad: # same group
                        if bond.atom1.molecule != bond.atom2.molecule: # but different chunks
                            if bond.atom1.molecule == chunk:
                                idx = strand_atoms[current_strand].index(bond.atom1)
                                if self.dnaStyleStrandsColor == 0:
                                    color = chunk_color
                                elif self.dnaStyleStrandsColor == 1:
                                    color = get_atom_rainbow_color(
                                        idx, start_index, end_index, 
                                        total_strand_length)
                                else:
                                    color = group_color                                
                                chunk._dnaStyleExternalBonds.append(
                                    (bond.atom1, bond.atom2, color))

                # draw the strand itself
                drawStrand(strand_positions, 
                           strand_colors, 
                           strand_radii, 
                           strand_direction,
                           draw_5p, draw_3p,
                           self.dnaStyleStrandsColor, 
                           self.dnaStyleStrandsShape,
                           self.dnaStyleStrandsArrows)            



    def drawchunk_selection_frame(self, glpane, chunk, selection_frame_color, memo, highlighted):
        """
        Given the same arguments as drawchunk, plus selection_frame_color, 
        draw the chunk's selection frame.

        (Drawing the chunk itself as well would not cause drawing errors
        but would presumably be a highly undesirable slowdown, especially if
        redrawing after selection and deselection is optimized to not have to
        redraw the chunk at all.)

        @note: in the initial implementation of the code that calls this method,
        the highlighted argument might be false whether or not we're actually
        hover-highlighted. And if that's fixed, then just as for drawchunk, 
        we might be called twice when we're highlighted, once with 
        highlighted = False and then later with highlighted = True.
        """
        drawchunk(self, glpane, chunk, selection_frame_color, memo, highlighted)
        return

    def drawchunk_realtime(self, glpane, chunk, highlighted=False):
        """
        Draws the chunk style that may depend on a current view.
        These are experimental features, work in progress as of 080319.
        For the DNA style, draws base orientation indicators and strand labels.
        080321 piotr: added better label positioning
        and 
        """

        def realTextSize(text, fm):
            """
            Returns a pair of vectors corresponding to a width
            and a height vector of a rendered text. 
            Beware, this call is quite expensive.

            @params: text - text to be measured
                     fm - font metrics created for the text font:
                     fm = QFontMetrics(font)

            @returns: (v1,v2) - pair of vector covering the text rectangle
                                expressed in world coordinates
            """
            textwidth = fm.width(text)
            textheight = fm.ascent()
            x0, y0, z0 = gluUnProject(0, 0, 0)
            x1, y1, z1 = gluUnProject(textwidth, 0, 0)
            x2, y2, z2 = gluUnProject(0, textheight, 0)
            return (V(x1-x0, y1-y0, z1-z0),V(x2-x0, y2-y0, z2-z0))

        def get_screen_position_of_strand_atom(strand_atom):
            """
            For a given strand atom, find its on-screen position.
            """

            axis_atom = strand_atom.axis_neighbor()

            if axis_atom:
                mol = axis_atom.molecule
                axis_atoms = mol.ladder.axis_rail.baseatoms
                if axis_atoms is None:
                    return None
                n_bases = len(axis_atoms)
                pos = axis_atoms.index(axis_atom)
                atom0 = axis_atom
                if pos<n_bases-1:
                    atom1 = axis_atoms[pos+1]
                    dpos = chunk.abs_to_base(atom1.posn()) - \
                         chunk.abs_to_base(atom0.posn())
                else:
                    atom1 = axis_atoms[pos-1]
                    atom2 = axis_atoms[pos]
                    dpos = chunk.abs_to_base(atom2.posn()) - \
                         chunk.abs_to_base(atom1.posn())
                last_dpos = dpos
                dvec = norm(cross(dpos,glpane.out))
                pos0 = chunk.abs_to_base(axis_atom.posn())#-mol.center
                pos1 = pos0+7.0*dvec
                pos2 = pos0-7.0*dvec
                if mol.ladder.strand_rails[0].baseatoms[pos]==strand_atom:
                    return pos1
                elif mol.ladder.strand_rails[1].baseatoms[pos]==strand_atom:
                    return pos2

            return None

        from utilities.constants import lightgreen
        from PyQt4.Qt import QFont, QString, QColor, QFontMetrics
        from widgets.widget_helpers import RGBf_to_QColor
        from dna.model.DnaLadderRailChunk import DnaStrandChunk

        labels_enabled = env.prefs[dnaStrandLabelsEnabled_prefs_key]
        indicators_enabled = env.prefs[dnaBaseIndicatorsEnabled_prefs_key]

        if chunk.color: # sometimes the chunk.color is not defined
            chunk_color = chunk.color
        else:
            chunk_color = white

        if not self.dnaExperimentalModeEnabled:

            if indicators_enabled: # draw the orientation indicators
                self.dnaStyleStrandsShape = env.prefs[dnaStyleStrandsShape_prefs_key]
                self.dnaStyleStrutsShape = env.prefs[dnaStyleStrutsShape_prefs_key]
                self.dnaStyleBasesShape = env.prefs[dnaStyleBasesShape_prefs_key]
                indicators_angle = env.prefs[dnaBaseIndicatorsAngle_prefs_key]
                indicators_color = env.prefs[dnaBaseIndicatorsColor_prefs_key]
                inv_indicators_color = env.prefs[dnaBaseInvIndicatorsColor_prefs_key]                
                inv_indicators_enabled = env.prefs[dnaBaseInvIndicatorsEnabled_prefs_key]
                indicators_distance = env.prefs[dnaBaseIndicatorsDistance_prefs_key]
                if chunk.isStrandChunk(): 
                    if chunk.ladder.axis_rail:
                        if self.dnaStyleStrandsShape>0 or \
                           self.dnaStyleBasesShape>0 or \
                           self.dnaStyleStrutsShape>0:                   
                            n_bases = chunk.ladder.baselength()
                            if chunk == chunk.ladder.strand_rails[0].baseatoms[0].molecule:
                                chunk_strand = 0
                            else:
                                chunk_strand = 1
                            for pos in range(0,n_bases):
                                atom1 = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos]
                                atom2 = chunk.ladder.axis_rail.baseatoms[pos]
                                vz = glpane.out 
                                v2 = norm(atom1.posn()-atom2.posn())
                                # calculate an angle between this vector 
                                # and the vector towards the viewer
                                a = angleBetween(vz, v2)
                                if abs(a) < indicators_angle:
                                    drawer.drawsphere(
                                        indicators_color, 
                                        chunk.abs_to_base(atom1.posn()), 1.5, 2)
                                if inv_indicators_enabled:
                                    if abs(a) > (180.0-indicators_angle):
                                        drawer.drawsphere(
                                            inv_indicators_color, 
                                            chunk.abs_to_base(atom1.posn()), 1.5, 2)

            if chunk.isStrandChunk():       

                if hasattr(chunk, "_dnaStyleExternalBonds"):
                    for exbond in chunk._dnaStyleExternalBonds:
                        atom1, atom2, color = exbond
                        if chunk.picked:
                            color = darkgreen
                        if highlighted:
                            color = yellow
                        pos1 = chunk.abs_to_base(atom1.posn())
                        pos2 = chunk.abs_to_base(atom2.posn())
                        drawer.drawsphere(color, pos1, self.dnaStyleStrandsScale, 2)
                        drawer.drawsphere(color, pos2, self.dnaStyleStrandsScale, 2)
                        drawer.drawcylinder(color, pos1, pos2, self.dnaStyleStrandsScale, True)              

                if self.dnaStyleBasesDisplayLetters: 
                    # calculate text size
                    # this is kludgy...
                    font_scale = int(500.0/glpane.scale)
                    if sys.platform == "darwin":
                        font_scale *= 2                        
                    if font_scale<9: font_scale = 9
                    if font_scale>50: font_scale = 50

                    # create the label font
                    labelFont = QFont( QString("Lucida Grande"), font_scale)
                    # get font metrics for the current font
                    fm = QFontMetrics(labelFont)
                    glpane.qglColor(RGBf_to_QColor(black))
                    # get text size in world coordinates
                    label_text = QString("X")
                    dx, dy = realTextSize(label_text, fm)
                    # disable lighting
                    glDisable(GL_LIGHTING)            
                    for atom in chunk.atoms.itervalues():
                        # pre-compute atom position
                        textpos = chunk.abs_to_base(atom.posn())+3.0*glpane.out
                        # get atom base name
                        label_text = QString(atom.getDnaBaseName())
                        # move the text center to the atom position
                        textpos -= 0.5*(dx+dy)   
                        # render the text
                        glpane.renderText(textpos[0], textpos[1], textpos[2], 
                                          label_text, labelFont)                    

                    # done, enable lighting
                    glEnable(GL_LIGHTING)

                if labels_enabled: 
                    # draw the strand labels

                    self.dnaStyleStrandsShape = env.prefs[dnaStyleStrandsShape_prefs_key]
                    self.dnaStyleStrutsShape = env.prefs[dnaStyleStrutsShape_prefs_key]
                    self.dnaStyleBasesShape = env.prefs[dnaStyleBasesShape_prefs_key]

                    labels_color_mode = env.prefs[dnaStrandLabelsColorMode_prefs_key]

                    if labels_color_mode==1:
                        labels_color = black
                    elif labels_color_mode==2:
                        labels_color = white
                    else: 
                        labels_color = env.prefs[dnaStrandLabelsColor_prefs_key]

                    # calculate the text size
                    # this is kludgy...
                    font_scale = int(500.0/glpane.scale)
                    if sys.platform == "darwin":
                        font_scale *= 2                        
                    if font_scale<9: font_scale = 9
                    if font_scale>50: font_scale = 50

                    if chunk.isStrandChunk():                
                        if self.dnaStyleStrandsShape>0 or \
                           self.dnaStyleBasesShape>0 or \
                           self.dnaStyleStrutsShape>0:                   

                            # the following is copied from DnaStrand.py
                            # I need to find a 5' sugar atom of the strand
                            # is there any more efficient way of doing that?
                            # this is terribly slow... I need something like
                            # "get_strand_chunks_in_bond_direction"...             


                            strandGroup = chunk.parent_node_of_class(chunk.assy.DnaStrand)
                            if strandGroup is None:
                                strand = chunk
                            else:
                                    #dna_updater case which uses DnaStrand object for 
                                    #internal DnaStrandChunks
                                strand = strandGroup                  

                            # the label is positioned at 5' end of the strand
                            # get the 5' strand atom
                            atom = strand.get_five_prime_end_base_atom()
                            if atom:

                                # and the next atom for extra positioning
                                next_atom = atom.strand_next_baseatom(1)

                                if atom.molecule==chunk and atom and next_atom: 
                                    # draw labels only for the first chunk

                                    # vector to move the label slightly away from the atom center
                                    halfbond = 0.5*(atom.posn()-next_atom.posn())

                                    # create the label font
                                    labelFont = QFont( QString("Helvetica"), font_scale)

                                    # define a color of the label
                                    if labels_color_mode==0:
                                        glpane.qglColor(RGBf_to_QColor(chunk_color))
                                    else:
                                        glpane.qglColor(RGBf_to_QColor(labels_color))

                                    # get font metrics to calculate text extents
                                    fm = QFontMetrics(labelFont)
                                    label_text = QString(strand.name)+QString(" ")
                                    textsize = fm.width(label_text)

                                    # calculate the text position
                                    # move a bit into viewers direction
                                    textpos = chunk.abs_to_base(atom.posn())+halfbond+5.0*glpane.out 

                                    # calculate shift for right aligned text
                                    dx, dy = realTextSize(label_text, fm)

                                    # check if the right alignment is necessary
                                    if dot(glpane.right,halfbond)<0.0:
                                        textpos -= dx

                                    # center the label vertically
                                    textpos -= 0.5*dy

                                    # draw the label
                                    glDisable(GL_LIGHTING)
                                    glpane.renderText(textpos[0], textpos[1], textpos[2], 
                                                      label_text, labelFont)
                                    glEnable(GL_LIGHTING)


        if self.dnaExperimentalModeEnabled and chunk.isAxisChunk():
            # very exprimental, buggy and undocumented
            axis = chunk.ladder.axis_rail

            # rescale font size for OSX
            font_scale = int(500.0/glpane.scale)
            if sys.platform == "darwin":
                font_scale *= 2                        
            if font_scale<9: font_scale = 9
            if font_scale>100: font_scale = 100

            if axis:
                n_bases = len(chunk.ladder.axis_rail.baseatoms)

                atom0 = chunk.ladder.axis_rail.baseatoms[0]
                atom1 = chunk.ladder.axis_rail.baseatoms[n_bases-1]

                pos0 = chunk.abs_to_base(atom0.posn())
                pos1 = chunk.abs_to_base(atom1.posn())

                glDisable(GL_LIGHTING)
                glColor3f(0,0,0)

                # glLineWidth(5.0)
                glLineWidth(1.0+100.0/glpane.scale)
                #glBegin(GL_LINES)
                last_dpos = V(0,0,0)
                """
                for pos in range(0, n_bases):
                    a_atom = chunk.ladder.axis_rail.baseatoms[pos]
                    s1_atom = chunk.ladder.strand_rails[0].baseatoms[pos]
                    s2_atom = chunk.ladder.strand_rails[1].baseatoms[pos]

                    a_pos = a_atom.posn()-chunk.center
                    s1_pos = get_screen_postion_of_strand_atom(s1_atom)
                    s2_pos = get_screen_postion_of_strand_atom(s2_atom)

                    if s1_pos and s2_pos:
                        glVertex3f(a_pos[0], a_pos[1], a_pos[2])
                        glVertex3f(s1_pos[0], s1_pos[1], s1_pos[2])
                        glVertex3f(a_pos[0], a_pos[1], a_pos[2])
                        glVertex3f(s2_pos[0], s2_pos[1], s2_pos[2])

                glEnd()
                glEnable(GL_LIGHTING)

                return
                """

                labelFont = QFont( QString("Lucida Grande"), font_scale)
                fm = QFontMetrics(labelFont)
                glpane.qglColor(RGBf_to_QColor(black))

                dx, dy = realTextSize("X", fm)

                glBegin(GL_LINES)
                # draw bases
                for pos in range(0,n_bases):
                    atom0 = chunk.ladder.axis_rail.baseatoms[pos]
                    if pos<n_bases-1:
                        atom1 = chunk.ladder.axis_rail.baseatoms[pos+1]
                        dpos = atom1.posn()-atom0.posn()
                    else:
                        atom1 = chunk.ladder.axis_rail.baseatoms[pos-1]
                        atom2 = chunk.ladder.axis_rail.baseatoms[pos]
                        dpos = atom2.posn()-atom1.posn()                           
                    last_dpos = dpos
                    dvec = norm(cross(dpos,glpane.out))
                    pos0 = chunk.abs_to_base(atom0.posn())
                    # print "dvec = ", dvec
                    s_atom0 = chunk.ladder.strand_rails[0].baseatoms[pos]
                    s_atom1 = chunk.ladder.strand_rails[1].baseatoms[pos]
                    bvec = norm(s_atom0.posn()-s_atom1.posn())
                    #bvec = glpane.quat.unrot(dvec)
                    pos3 = pos0+7.0*dvec
                    pos4 = pos0-7.0*dvec
                    pos1 = pos3
                    pos2 = pos4
                    #angle = dot(bvec, dvec)
                    #if angle<0.0:
                    #    pos1 = pos4
                    #    pos2 = pos3
                    """
                    # this assignment should depend on a relative turn orientation
                    base_color = self.getBaseColor(s_atom0.getDnaBaseName())
                    #base_color = self.getFullRainbowColor(0.5*(angle+1.0))
                    glColor3f(base_color[0],base_color[1],base_color[2])
                    glVertex3f(pos0[0], pos0[1], pos0[2])
                    glVertex3f(pos1[0], pos1[1], pos1[2])
                    base_color = self.getBaseColor(s_atom1.getDnaBaseName())
                    #base_color = self.getFullRainbowColor(0.5*(angle+1.0))
                    glColor3f(base_color[0],base_color[1],base_color[2])
                    glVertex3f(pos0[0], pos0[1], pos0[2])
                    glVertex3f(pos2[0], pos2[1], pos2[2])

                    #dpos = norm(dpos)
                    #angle = dot(glpane.out,bvec)
                    #print "dpos = ", dpos
                    #print "bvec = ", bvec

                    #print "angle = ", angle

                    #base_color = self.getFullRainbowColor(0.5*(angle+1.0))
                    #glColor3f(base_color[0],base_color[1],base_color[2])
                    glColor3f(0,0,0)
                    """
                    glEnd()

                    textpos = pos0+0.5*(pos1-pos0)
                    label_text = QString(s_atom0.getDnaBaseName())
                    # dx, dy = realTextSize(label_text, fm)
                    textpos -= 0.5*(dx+dy)  
                    base_color = self.getBaseColor(s_atom0.getDnaBaseName())
                    glColor3f(base_color[0],base_color[1],base_color[2])
                    glpane.renderText(textpos[0], textpos[1], textpos[2], 
                                      label_text, labelFont)                    

                    textpos = pos0+0.5*(pos2-pos0)
                    label_text = QString(s_atom1.getDnaBaseName())
                    # dx, dy = realTextSize(label_text, fm)
                    textpos -= 0.5*(dx+dy)  
                    base_color = self.getBaseColor(s_atom1.getDnaBaseName())
                    glColor3f(base_color[0],base_color[1],base_color[2])
                    glpane.renderText(textpos[0], textpos[1], textpos[2], 
                                      label_text, labelFont)                    

                    if highlighted:
                        color = yellow
                    elif chunk.picked:
                        color = darkgreen
                    else:
                        color = black

                    drawer.drawFilledCircle(color, pos0, 0.5, glpane.out)

                    glDisable(GL_LIGHTING)
                    glBegin(GL_LINES)

                    if s_atom0.molecule.picked:
                        color0 = darkgreen
                    else:
                        color0 = s_atom0.molecule.color

                    if s_atom1.molecule.picked:
                        color1 = darkgreen
                    else:
                        color1 = s_atom1.molecule.color

                    if pos>0:
                        glColor3f(color0[0],
                                  color0[1],
                                  color0[2])
                        glVertex3f(last_pos3[0],last_pos3[1],last_pos3[2])
                        glVertex3f(pos3[0],pos3[1],pos3[2])
                        glColor3f(color1[0],
                                  color1[1],
                                  color1[2])
                        glVertex3f(pos4[0],pos4[1],pos4[2])
                        glVertex3f(last_pos4[0],last_pos4[1],last_pos4[2])


                    last_pos1 = pos1
                    last_pos2 = pos2
                    last_pos3 = pos3
                    last_pos4 = pos4

                # draw arrows on endatoms                    
                endatoms = (chunk.ladder.axis_rail.baseatoms[0],
                            chunk.ladder.axis_rail.baseatoms[n_bases-1])

                for atom in endatoms:
                    neighbors = atom.strand_neighbors()
                    for strand_atom in neighbors:
                        strand_chunk = strand_atom.molecule
                        strand = strand_chunk.parent_node_of_class(
                            strand_chunk.assy.DnaStrand)
                        if strand_atom==strand.get_three_prime_end_base_atom():
                            glColor3f(strand_atom.molecule.color[0],
                                      strand_atom.molecule.color[1],
                                      strand_atom.molecule.color[2])
                            a_neighbors = atom.axis_neighbors()
                            dvec = atom.posn()-a_neighbors[0].posn()
                            ovec = norm(cross(dvec,glpane.out))
                            pos0 = chunk.abs_to_base(atom.posn()) + 7.0*ovec
                            pos1 = pos0 + dvec 
                            glVertex3f(pos0[0], pos0[1], pos0[2])
                            glVertex3f(pos1[0], pos1[1], pos1[2])
                            dvec = norm(dvec)
                            avec2 = pos1-0.5*(dvec-ovec)-1.0*dvec
                            glVertex3f(pos1[0],pos1[1],pos1[2])
                            glVertex3f(avec2[0],avec2[1],avec2[2])
                            avec3 = pos1-0.5*(dvec+ovec)-1.0*dvec
                            glVertex3f(pos1[0], pos1[1], pos1[2])
                            glVertex3f(avec3[0], avec3[1], avec3[2])

                glEnd()

                """
                neighbors = endatoms[0].strand_neighbors()
                s = 1
                for strand_atom in neighbors:
                    strand_chunk = strand_atom.molecule
                    print "drawing strand ", strand_chunk
                    for atom in strand_chunk.atoms.itervalues():
                        axis_atom = atom.axis_neighbor()
                        if axis_atom:
                            a_neighbors = axis_atom.axis_neighbors()
                            if axis_atom.index<a_neighbors[0].index:
                                idx = -1
                            else:
                                idx = 1
                            dvec = axis_atom.posn()-a_neighbors[0].posn()
                            ovec = norm(cross(dvec,glpane.out))
                            pos0 = axis_atom.posn() - axis_atom.molecule.center + 7.0*s*idx*ovec                                        
                            drawFilledCircle(strand_chunk.color, pos0, 0.5, glpane.out)
                    s *= -1 # next strand            
                """

                axis_atoms = chunk.ladder.axis_rail.baseatoms
                """
                neighbors = endatoms[0].strand_neighbors()
                for strand_atom in neighbors:
                    strand_chunk = strand_atom.molecule
                    for atom in strand_chunk.atoms.itervalues():
                        if atom:
                            pos = get_screen_position_of_strand_atom(atom)
                            if pos:
                                drawFilledCircle(atom.molecule.color, pos, 0.5, glpane.out)
                """

                glBegin(GL_LINES)
                # draw the external bonds
                neighbors = endatoms[0].strand_neighbors()
                for strand_atom in neighbors:
                    strand_chunk = strand_atom.molecule
                    for bond in strand_chunk.externs:
                        if bond.atom1.molecule.dad==bond.atom2.molecule.dad: # same group
                            if bond.atom1.molecule!=bond.atom2.molecule: # but different chunks
                                pos0 = get_screen_position_of_strand_atom(bond.atom1)
                                pos1 = get_screen_position_of_strand_atom(bond.atom2)
                                if pos0 and pos1:
                                    glColor3f(bond.atom1.molecule.color[0],
                                              bond.atom1.molecule.color[1],
                                              bond.atom1.molecule.color[2])
                                    glVertex3f(pos0[0], pos0[1], pos0[2])
                                    glVertex3f(pos1[0], pos1[1], pos1[2])

                glEnd() # end line drawing

                # line width should be restored to initial value
                # but I think 1.0 is maintained within the program
                glLineWidth(1.0) 

    def writepov(self, chunk, memo, file):
        """
        Renders the chunk to a POV-Ray file.
        This is an experimental feature as of 080319.
        """

        from graphics.rendering.povray.povheader import povpoint
        from geometry.VQT import vlen

        def writetube(points, colors, radii, rainbow, smooth):
            """ 
            Writes a smooth tube in a POV-Ray format.
            """
            file.write("sphere_sweep {\n")
            if smooth==True:
                file.write("  cubic_spline\n")
            else:
                file.write("  cubic_spline\n")
            file.write("  %d,\n" % (len(points)-2))
            n = len(points)-1
            for i in range(1,n):
                file.write("  " + povpoint(points[i]) +", %d\n" % radii[i]);
            file.write("  pigment {\n")
            vec = points[n]-points[1]
            file.write("    gradient <%g,%g,%g> scale %g translate <%g,%g,%g>\n" % 
                       (vec[0], vec[1], vec[2], vlen(vec),
                        points[1][0], points[1][1], points[1][2]))
            file.write("    color_map { RainbowMap }\n")
            file.write("  }\n")
            file.write("}\n")

        def writecylinder(start, end, color):
            file.write("cylinder {\n")
            file.write("  " + povpoint(start) + ", " + povpoint(end))
            file.write(", %g\n" % (0.5*self.dnaStyleStrutsScale))
            file.write("  pigment {color <%g %g %g>}\n" % (color[0], color[1], color[2]))
            file.write("}\n")

        strand_positions, strand_sequences, axis_positions, colors, radii, \
                        chunk_color, group_color, chunk_strand, num_strands \
                        = memo

        # render axis cylinder        
        if chunk.isAxisChunk(): # this is the DNA axis           
            if self.dnaStyleAxisShape>0:
                if self.dnaStyleAxisShape==1: # shape 
                    is_spline = False # connected cylinders
                else:
                    is_spline = True # spline

                if self.dnaStyleAxisColor==1 or self.dnaStyleAxisColor==2:
                    is_rainbow = True
                else:
                    is_rainbow = False

                writetube(axis_positions, colors, radii, is_rainbow, is_spline)

        """                   
        # render the axis cylinder        
        if chunk.isAxisChunk(): # this is the DNA axis           
            if self.dnaStyleAxisShape>0:
                writetube(points, colors, radii, False, True)

        if chunk.isStrandChunk(): 
            # render strands  
            if self.dnaStyleStrandsShape>0:
                writetube(points, colors, radii, False)

            # render struts
            if self.dnaStyleStrutsShape>0:
                for pos in range(1,n_bases-1):
                    atom1 = strand_positions[chunk_strand][pos]
                    atom3 = strand_positions[1-chunk_strand][pos]
                    if self.dnaStyleStrutsShape==1:
                        atom2_pos = axis_positions[pos]
                    elif self.dnaStyleStrutsShape==2:
                        atom2_pos = 0.5*(atom1+atom3)
                    if self.dnaStyleStrutsColor==0 or chunk_selected:
                        color = chunk_color
                    elif self.dnaStyleStrutsColor==1:
                        color = self.getRainbowColorInRange(pos, n_bases, 0.75, 1.0)                        
                    elif self.dnaStyleStrutsColor==2:
                        color = group_color
                    else:
                        color = white ###self.getBaseColor(atom1.getDnaBaseName())
                    writecylinder(atom1.posn(),atom2.posn(),color)
        """


    def compute_memo(self, chunk):
        """
        If drawing chunks in this display mode can be optimized by precomputing
        some info from chunk's appearance, compute that info and return it.

        If this computation requires preference values, access them as 
        env.prefs[key], and that will cause the memo to be removed (invalidated)
        when that preference value is changed by the user.

        This computation is assumed to also depend on, and only on, chunk's
        appearance in ordinary display modes (i.e. it's invalidated whenever
        havelist is). There is not yet any way to change that, so bugs will 
        occur if any ordinarily invisible chunk info affects this rendering,
        and potential optimizations will not be done if any ordinarily visible
        info is not visible in this rendering. These can be fixed if necessary
        by having the real work done within class Chunk's _recompute_ rules,
        with this function or drawchunk just accessing the result of that
        (and sometimes causing its recomputation), and with whatever 
        invalidation is needed being added to appropriate setter methods of 
        class Chunk. If the real work can depend on more than chunk's ordinary
        appearance can, the access would need to be in drawchunk;
        otherwise it could be in drawchunk or in this method compute_memo().

        @param chunk: The chunk.
        @type  chunk: chunk
        """

        # for this example, we'll turn the chunk axes into a cylinder.
        # Since chunk.axis is not always one of the vectors chunk.evecs 
        # (actually chunk.poly_evals_evecs_axis[2]),
        # it's best to just use the axis and center, then recompute 
        # a bounding cylinder.

        # import the style preferences from User Preferences
        self.dnaStyleStrandsShape = env.prefs[dnaStyleStrandsShape_prefs_key]
        self.dnaStyleStrandsColor = env.prefs[dnaStyleStrandsColor_prefs_key]
        self.dnaStyleStrandsScale = env.prefs[dnaStyleStrandsScale_prefs_key]
        self.dnaStyleStrandsArrows = env.prefs[dnaStyleStrandsArrows_prefs_key]        
        self.dnaStyleAxisShape = env.prefs[dnaStyleAxisShape_prefs_key]
        self.dnaStyleAxisColor = env.prefs[dnaStyleAxisColor_prefs_key]
        self.dnaStyleAxisScale = env.prefs[dnaStyleAxisScale_prefs_key]
        self.dnaStyleAxisTaper = env.prefs[dnaStyleAxisTaper_prefs_key]
        self.dnaStyleStrutsShape = env.prefs[dnaStyleStrutsShape_prefs_key]
        self.dnaStyleStrutsColor = env.prefs[dnaStyleStrutsColor_prefs_key]
        self.dnaStyleStrutsScale = env.prefs[dnaStyleStrutsScale_prefs_key]                
        self.dnaStyleBasesShape = env.prefs[dnaStyleBasesShape_prefs_key]
        self.dnaStyleBasesColor = env.prefs[dnaStyleBasesColor_prefs_key]
        self.dnaStyleBasesScale = env.prefs[dnaStyleBasesScale_prefs_key]
        self.dnaStyleBasesDisplayLetters = env.prefs[dnaStyleBasesDisplayLetters_prefs_key]

        # render in experimental 2D mode?
        self.dnaExperimentalModeEnabled = debug_pref(
            "DNA CylinderStyle: enable experimental 2D mode?",
            Choice_boolean_False,
            prefs_key = True,
            non_debug = True )

        if not hasattr(chunk, 'ladder'):
            # DNA updater is off ?            
            return None

        if not chunk.atoms or not chunk.ladder: 
            # nothing to display 
            return None

        n_bases = chunk.ladder.baselength()    
        if n_bases<1: 
            # no bases? quit
            return None

        if chunk.color:
            chunk_color = chunk.color
        else:
            chunk_color = white

        strand_positions = axis_positions = None

        num_strands = chunk.ladder.num_strands()

        current_strand = 0

        strand_atoms = [None] * num_strands
        strand_colors = [None] * num_strands
        for i in range(0, num_strands):
            strand_atoms[i] = chunk.ladder.strand_rails[i].baseatoms
            if chunk.ladder.strand_rails[i].baseatoms[0].molecule==chunk:
                current_strand = i

        axis_atoms = None
        if chunk.ladder.axis_rail:
            axis_atoms = chunk.ladder.axis_rail.baseatoms

        group_color = white

        five_prime_atom = three_prime_atom = None
        strand_direction = 0

        start_index = end_index = 0
        total_strand_length = 1

        if chunk.isAxisChunk() and axis_atoms: # axis chunk           
            axis_chunks = chunk.getDnaGroup().getAxisChunks()
            group_color = self.getRainbowColorInRange(
                axis_chunks.index(chunk), len(axis_chunks), 0.75, 1.0)                             
        elif chunk.isStrandChunk(): # strand chunk
            strands = chunk.getDnaGroup().getStrands()
            group_color = self.getRainbowColorInRange(
                strands.index(chunk.dad), len(strands), 0.75, 1.0)
            strand = chunk.parent_node_of_class(chunk.assy.DnaStrand)
            if strand:
                five_prime_atom = strand.get_five_prime_end_base_atom()
                three_prime_atom = strand.get_three_prime_end_base_atom()
                strand_direction = chunk.idealized_strand_direction()
                wholechain = chunk.wholechain

                # determine strand and end atom indices
                # within the entire strand.

                # this doesn't work with PAM5 models
                ### all_atoms = chunk.get_strand_atoms_in_bond_direction()

                rawAtomList = []
                for c in strand.members:
                    if isinstance(c, DnaStrandChunk):
                        rawAtomList.extend(c.atoms.itervalues())

                all_atoms = strand.get_strand_atoms_in_bond_direction(rawAtomList)

                start_atom = strand_atoms[current_strand][0]
                end_atom = strand_atoms[current_strand][len(strand_atoms[0])-1]
                if  start_atom in all_atoms and \
                    end_atom in all_atoms:
                    start_index = all_atoms.index(start_atom) - 1
                    end_index = all_atoms.index(end_atom) - 1
                    total_strand_length = len(all_atoms) - 2           

            n_atoms = len(strand_atoms)

        return (strand_atoms,
                axis_atoms, 
                five_prime_atom,
                three_prime_atom,
                strand_direction,
                start_index, 
                end_index,
                total_strand_length,
                chunk_color,
                group_color,
                current_strand)

    pass # end of class DnaCylinderChunks

ChunkDisplayMode.register_display_mode_class(DnaCylinderChunks)

# end
