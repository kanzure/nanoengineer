# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaCylinderChunks.py -- defines I{DNA Cylinder} display mode, which draws 
axis chunks as a cylinder in the chunk's color.
f
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

piotr 080509: Code refactoring.

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

from utilities.debug_prefs import debug_pref, Choice, Choice_boolean_True, Choice_boolean_False

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
from utilities.prefs_constants import dnaStyleAxisEndingStyle_prefs_key
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
from OpenGL.GL import GL_BLEND
from OpenGL.GL import glEnd
from OpenGL.GL import glVertex3f
from OpenGL.GL import glVertex3fv
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
from OpenGL.GL import GL_LINE_SMOOTH

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
    
    def _compute_spline(self, data, idx, t):
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
        res = 0.5 * ((2.0 * x1) +
                     t * (-x0 + x2) +
                     t2 * (2.0 * x0 - 5.0 * x1 + 4.0 * x2 - x3) +
                     t3 * (-x0 + 3.0 * x1 - 3.0 * x2 + x3))
        return res

    def _get_rainbow_color(self, hue, saturation, value):
        """
        Gets a color of a hue range limited to 0 - 0.667 (red - blue)
        """

        hue = 0.666 * (1.0 - hue)
        if hue < 0.0: 
            hue = 0.0
        if hue > 0.666: 
            hue = 0.666
        return colorsys.hsv_to_rgb(hue, saturation, value)

    def _get_full_rainbow_color(self, hue, saturation, value):
        """
        Gets a color from a full hue range.
        """
        if hue < 0.0: 
            hue = 0.0
        if hue > 1.0: 
            hue = 1.0
        return colorsys.hsv_to_rgb(hue, saturation, value)

    def _get_nice_rainbow_color(self, hue, saturation, value):
        """
        Gets a color of a full hue range.
        """
        hue *= 0.8
        if hue < 0.0: 
            hue = 0.0
        if hue > 1.0: 
            hue = 1.0
        return colorsys.hsv_to_rgb(hue, saturation, value)

    def _get_base_color(self, base):
        """
        Returns a color according to DNA base type.
        Two-ring bases (G and A) have darker colors.
        G = red
        C = orange
        A = blue
        T = cyan
        """
        
        if base == "G":
            color = [1.0, 0.0, 0.0]
        elif base == "C":
            color = [1.0, 0.5, 0.0]
        elif base == "A":
            color = [0.0, 0.3, 0.9]
        elif base == "T":
            color = [0.0, 0.7, 0.8]
        else:
            color = [0.5, 0.5, 0.5]
        return color
    
    def _get_rainbow_color_in_range(self, pos, count, saturation, value):
        if count > 1: 
            count -= 1
        hue = float(pos)/float(count)        
        if hue < 0.0: 
            hue = 0.0
        if hue > 1.0: 
            hue = 1.0
        return self._get_rainbow_color(hue, saturation, value)

    def _get_full_rainbow_color_in_range(self, pos, count, saturation, value):
        if count > 1: 
            count -= 1
        hue = float(pos)/float(count)        
        if hue < 0.0: 
            hue = 0.0
        if hue > 1.0: 
            hue = 1.0
        return self._get_full_rainbow_color(hue, saturation, value)

    def _get_nice_rainbow_color_in_range(self, pos, count, saturation, value):
        if count > 1: 
            count -= 1
        hue = float(pos)/float(count)        
        if hue < 0.0: 
            hue = 0.0
        if hue > 1.0: 
            hue = 1.0
        return self._get_nice_rainbow_color(hue, saturation, value)

    def _draw_strand(self, points, colors, radii, dir, draw5p, draw3p,
                   color_style, shape, arrows):
        """
        Renders a strand shape along points array using colors 
        and radii arrays, with optional arrows. 

        draw5p and draw3p control arrow drawing at 5' and 3' ends.
        shape controls the strand apperance (0=cylinders, 1=tube)
        """
        n = len(points)
        if n > 3:
            # copy colors and radii
            colors[0] = colors[1]
            colors[n-1] = colors[n-2]
            radii[0] = radii[1]
            radii[n-1] = radii[n-2]
            # draw the terminal spheres
            drawer.drawsphere(colors[1], points[1], radii[1],2) 
            drawer.drawsphere(colors[n-2], points[n-2], radii[1],2) 
            # draw the arrows
            if dir == 1:
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
            if dir == -1:
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

            if shape == 1: # draw cylinders
                gleSetJoinStyle(TUBE_JN_ROUND | TUBE_NORM_PATH_EDGE 
                                | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED)        
                if color_style==1:
                    drawer.drawpolycone_multicolor([0, 0, 0, -2], 
                                                   points,
                                                   colors,
                                                   radii)
                else:
                    drawer.drawpolycone(colors[1], 
                                        points,
                                        radii)
            elif shape == 2: # draw spline tube
                gleSetJoinStyle(TUBE_JN_ANGLE | TUBE_NORM_PATH_EDGE 
                                | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED) 

                new_points = [ None ] * (4*(n-2)-1)
                new_colors = [ None ] * (4*(n-2)-1)
                new_radii = [ 0.0 ] * (4*(n-2)-1)
                for p in range(0, (4*(n-2)-1)):
                    new_points[p] = [ 0.0 ] * 3
                    new_colors[p] = [ 0.0 ] * 3

                o = 1
                for p in range (1, n-2):
                    for m in range (0, 4):
                        t = 0.25 * m
                        new_points[o] = self._compute_spline(points, p, t)
                        new_colors[o] = self._compute_spline(colors, p, t)
                        new_radii[o] = self._compute_spline(radii, p, t)
                        o += 1        
                new_points[o] = self._compute_spline(points, p, 1.0)
                new_colors[o] = self._compute_spline(colors, p, 1.0)
                new_radii[o] = self._compute_spline(radii, p, 1.0)
                o += 1
                new_points[0] = 3.0 * new_points[1] - 3.0 * new_points[2] + new_points[3] 
                new_points[o] = 3.0 * new_points[o-1] - 3.0 * new_points[o-2] + new_points[o-3] 
                
                # draw the tube
                if color_style==1:
                    drawer.drawpolycone_multicolor([0, 0, 0, -2], 
                                                   new_points, 
                                                   new_colors, 
                                                   new_radii)
                else:
                    drawer.drawpolycone(colors[1], 
                                        new_points, 
                                        new_radii)

    def _get_axis_positions(self, chunk, atom_list, color_style):
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
            if n_atoms > 1:
                positions[0] = 2 * positions[1] - positions[2]
            else:
                positions[0] = positions[1]
            if n_atoms > 1:    
                positions[n_atoms+1] = 2*positions[n_atoms] - positions[n_atoms-1]
            else:
                positions[n_atoms+1] = positions[n_atoms]                    
        return positions

    def _get_axis_atom_color_per_base(self, pos, strand_atoms_lists):
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

    def _get_axis_colors(self, atom_list, strand_atoms_lists, color_style, chunk_color, group_color):
        """
        Create a list of colors from atom list.
        """
        n_atoms = len(atom_list)
        if color_style == 2 or \
           color_style == 3: 
            # Discrete colors.
            # For discrete color scheme, the number of internal nodes has to be
            # duplicated in order to deal with (deafult) color interpolation
            # in glePolyCylinder routine (colors are interpolated on links
            # with zero length, so the interpolation effects are not visible.)
            colors = [None] * (2*n_atoms+2)
            pos = 2
            for i in range (1, n_atoms):
                if color_style==2: 
                    color1 = self._get_rainbow_color_in_range(
                        i-1, n_atoms, 0.75, 1.0)
                    color2 = self._get_rainbow_color_in_range(
                        i, n_atoms, 0.75, 1.0)
                elif color_style==3:
                    color1 = self._get_axis_atom_color_per_base(
                        i-1, strand_atoms_lists)
                    color2 = self._get_axis_atom_color_per_base(
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
            if color_style == 1:                    
                for i in range(1, n_atoms+1):
                    colors[i] = self._get_rainbow_color_in_range(
                        i, n_atoms, 0.75, 1.0)
            elif color_style == 4:
                for i in range(1, n_atoms+1):
                    colors[i] = group_color
            else:
                for i in range(1, n_atoms+1):
                    colors[i] = chunk_color
            colors[0] = colors[1]
            colors[n_atoms+1] = colors[n_atoms]

        return colors

    def _get_axis_radii(self, atom_list, color_style, shape, scale, ending_style):
        """
        Create a list of radii from atom list.
        """
        if shape==1:
            rad = 7.0*scale
        else:    
            rad = 2.0*scale
        n_atoms = len(atom_list)
        if color_style==2 or color_style==3: 
            # Discrete colors.
            # For discrete colors duplicate a number of nodes.
            length = 2*n_atoms+2
            radii = [rad] * (length)
            if ending_style==2 or ending_style==3:
                radii[1] = 0.0
                radii[2] = 0.5*rad
                radii[3] = 0.5*rad
            if ending_style==1 or ending_style==3:
                radii[length-4] = 0.5 * rad
                radii[length-3] = 0.5 * rad
                radii[length-2] = 0.0
        else:
            length = n_atoms+2
            radii = [rad] * (length)
            if ending_style==2 or ending_style==3:
                radii[1] = 0.0
                radii[2] = 0.66 * rad
            if ending_style==1 or ending_style==3:
                radii[length-3] = 0.66 * rad
                radii[length-2] = 0.0        

        return radii

    def _get_strand_positions(self, chunk, atom_list):
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

    def _get_atom_rainbow_color(self, idx, n_atoms, start, end, length):
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
        #if strand_direction == -1:
        #    q = 1.0 - q
        return self._get_rainbow_color(q, 0.75, 1.0)
    pass

    def _get_strand_colors(self, atom_list, color_style, start, end, length, chunk_color, group_color):
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
                #if strand_direction == -1:
                #    q = 1.0 - q
                col = self._get_rainbow_color(q, 0.75, 1.0)
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

    def _get_strand_radii(self, atom_list, radius):
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
        # ---------------------------------------------------------------------

        chunk._dnaStyleExternalBonds = []

        if not memo: # nothing to render
            return

        if self.dnaExperimentalMode > 0: 
            # experimental mode is drawn in drawchunk_realtime
            return

        strand_atoms, axis_atoms, \
        five_prime_atom, three_prime_atom, strand_direction, \
        start_index, end_index, total_strand_length, \
        chunk_color, group_color, current_strand, \
        polycylinder_positions, polycylinder_colors, polycylinder_radii = memo

        # render the axis cylinder        
        if chunk.isAxisChunk() and \
           polycylinder_positions: # fixed bug 2877 - piotr 080516
            axis_positions = polycylinder_positions
            axis_colors = polycylinder_colors
            axis_radii = polycylinder_radii
            n_points = len(axis_positions)            
            if self.dnaStyleAxisShape>0:
                # spherical ends    
                if self.dnaStyleAxisEndingStyle == 4:
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
                if self.dnaStyleAxisColor==1 \
                   or self.dnaStyleAxisColor==2 \
                   or self.dnaStyleAxisColor==3: # render discrete colors                
                    drawer.drawpolycone_multicolor([0, 0, 0, -2], 
                                                   axis_positions, 
                                                   axis_colors, 
                                                   axis_radii)
                else:   
                    drawer.drawpolycone(axis_colors[1], 
                                        axis_positions, 
                                        axis_radii)

        elif chunk.isStrandChunk(): # strands, struts and bases 
            """
            strand_positions = self._get_strand_positions(
                chunk, strand_atoms[current_strand])
            strand_colors = self._get_strand_colors(
                strand_atoms[current_strand], 
                self.dnaStyleStrandsColor,
                start_index, end_index, total_strand_length,
                chunk_color, group_color)
            strand_radii = self._get_strand_radii(
                strand_atoms[current_strand], self.dnaStyleStrandsScale)
            """

            strand_positions = polycylinder_positions
            strand_colors = polycylinder_colors
            strand_radii = polycylinder_radii
            
            n_atoms = len(strand_atoms[current_strand])

            if strand_direction==1:
                draw_5p = (strand_atoms[current_strand][0]==five_prime_atom)
                draw_3p = (strand_atoms[current_strand][n_atoms-1]==three_prime_atom)
            else:
                draw_5p = (strand_atoms[current_strand][n_atoms-1]==five_prime_atom)
                draw_3p = (strand_atoms[current_strand][0]==three_prime_atom)

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
                                    color = self._get_atom_rainbow_color(
                                        idx, n_atoms, start_index, end_index, 
                                        total_strand_length)
                                else:
                                    color = group_color                                
                                chunk._dnaStyleExternalBonds.append(
                                    (bond.atom1, bond.atom2, color))
    
                # draw the strand itself
                self._draw_strand(
                    strand_positions, 
                    strand_colors, 
                    strand_radii, 
                    strand_direction,
                    draw_5p, 
                    draw_3p,
                    self.dnaStyleStrandsColor, 
                    self.dnaStyleStrandsShape,
                    self.dnaStyleStrandsArrows)            

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
                            color = self._get_rainbow_color_in_range(
                                pos, n_atoms, 0.75, 1.0)                        
                        else:
                            color = self._get_base_color(atom1.getDnaBaseName())
                        drawer.drawcylinder(
                            color, 
                            chunk.abs_to_base(atom1.posn()), 
                            atom2_pos, 
                            0.5*self.dnaStyleStrutsScale, True)

            # render bases
            # this should be pre-calculated in getmemo
            
            if self.dnaStyleBasesShape > 0:
                num_strands = len(strand_atoms)
                for pos in range(0, n_atoms):
                    atom = strand_atoms[current_strand][pos]
                    if self.dnaStyleBasesColor==0:
                        color = chunk_color
                    elif self.dnaStyleBasesColor==1:
                        color = self._get_rainbow_color_in_range(pos, n_atoms, 0.75, 1.0)
                    elif self.dnaStyleBasesColor==2:
                        color = group_color
                    else:
                        color = self._get_base_color(atom.getDnaBaseName())
                    if self.dnaStyleBasesShape==1: # draw spheres
                        drawer.drawsphere(color, chunk.abs_to_base(atom.posn()),
                                          self.dnaStyleBasesScale, 2)
                    elif self.dnaStyleBasesShape==2 \
                         and num_strands > 1: # draw a schematic 'cartoon' shape
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

        def _realTextSize(text, fm):
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

        def _get_screen_position_of_strand_atom(strand_atom):
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
                if pos < n_bases-1:
                    atom1 = axis_atoms[pos+1]
                    dpos = atom1.posn() - atom0.posn()
                else:
                    atom1 = axis_atoms[pos-1]
                    atom2 = axis_atoms[pos]
                    dpos = atom2.posn() - atom1.posn()
                last_dpos = dpos
                out = mol.quat.unrot(glpane.out)
                if flipped:
                    dvec = norm(cross(dpos, -out))
                else:
                    dvec = norm(cross(dpos, out))                    
                pos0 = chunk.abs_to_base(axis_atom.posn())
                pos1 = pos0 + ssep * dvec
                pos2 = pos0 - ssep * dvec
                if mol.ladder.strand_rails[0].baseatoms[pos] == strand_atom:
                    return (pos1, dpos)
                elif mol.ladder.strand_rails[1].baseatoms[pos] == strand_atom:
                    return (pos2, -dpos)

            return (None, None)

        
        def _draw_arrow(atom):
            if atom:
                strand = atom.molecule.parent_node_of_class(
                    atom.molecule.assy.DnaStrand)
                if atom == strand.get_three_prime_end_base_atom():
                    ax_atom = atom.axis_neighbor()
                    a_neighbors = ax_atom.axis_neighbors()
                    #dvec = chunk.abs_to_base(ax_atom.posn()) - \
                    #       chunk.abs_to_base(a_neighbors[0].posn())
                    pos0, dvec = _get_screen_position_of_strand_atom(atom)
                    ovec = norm(cross(dvec, chunk.quat.unrot(glpane.out)))
                    pos1 = pos0 + 0.5 * dvec
                    if mode == 1:
                        pos1 += 1.0 * dvec
                    glVertex3fv(pos0)
                    glVertex3fv(pos1)
                    dvec = norm(dvec)
                    avec2 = pos1 - 0.5 * (dvec - ovec) - dvec
                    glVertex3fv(pos1)
                    glVertex3fv(avec2)
                    avec3 = pos1 - 0.5 * (dvec + ovec) - dvec
                    glVertex3fv(pos1)
                    glVertex3fv(avec3)
                    return True
            return False
        
        def _draw_external_bonds():
            for bond in chunk.externs:
                if bond.atom1.molecule.dad == bond.atom2.molecule.dad: # same group
                    if bond.atom1.molecule != bond.atom2.molecule: # but different chunks
                        pos0, dvec = _get_screen_position_of_strand_atom(bond.atom1)
                        pos1, dvec = _get_screen_position_of_strand_atom(bond.atom2)
                        if pos0 and pos1:
                            glVertex3f(pos0[0], pos0[1], pos0[2])
                            glVertex3f(pos1[0], pos1[1], pos1[2])
        
        def _light_color(color):
            """
            Make a lighter color
            """
            lcolor = [0.0, 0.0, 0.0]
            lcolor[0] = 0.5 * (1.0 + color[0])
            lcolor[1] = 0.5 * (1.0 + color[1])
            lcolor[2] = 0.5 * (1.0 + color[2])
            return lcolor
        
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

        if self.dnaExperimentalMode == 0:

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
                    dx, dy = _realTextSize(label_text, fm)
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
                        if self.dnaStyleStrandsShape > 0 or \
                           self.dnaStyleBasesShape > 0 or \
                           self.dnaStyleStrutsShape > 0:                   

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
                                    dx, dy = _realTextSize(label_text, fm)

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


        if self.dnaExperimentalMode > 0:
            # Very exprimental, buggy and undocumented 2D DNA display mode.
            # The helices are flattened, so sequence ond overall topology
            # can be visualized in a convenient way. Particularly
            # useful for short structural motifs and origami structures.
            # As for 080415, this work is still considered very preliminary
            # and experimental.
            
            # The structure will follow a 2D projection of the central axis.
            # Note: this mode doesn't work well for PAM5 models.
            
            axis = chunk.ladder.axis_rail

            flipped = False
            
            # if hasattr(chunk.ladder, "flipped"):
            #     flipped = chunk.ladder.flipped
                
            # print "flipped: ", flipped
            
            mode = self.dnaExperimentalMode - 1

            #if not axis:
            #    print "No axis rail for ", chunk

            no_axis = False
            
            if axis is None:
                axis = chunk.ladder.strand_rails[0]
                no_axis = True
                
            if axis:
                # Calculate the font scale.
                if mode == 0:
                    font_scale = int(500.0/glpane.scale)
                else:
                    font_scale = int(300.0/glpane.scale)
                    
                # Rescale font scale for OSX.
                if sys.platform == "darwin":
                    font_scale *= 2         
    
                # Limit the font scale.            
                if font_scale<9: font_scale = 9
                if font_scale>100: font_scale = 100
    
                # Number of bases
                n_bases = len(axis)
                
                
                # Disable lighting, we are drawing only text and lines.                
                glDisable(GL_LIGHTING)

                # Calculate the line width.
                if mode == 0 \
                   or mode == 2:
                    lw = 1.0 + 100.0 / glpane.scale

                if mode == 1:
                    lw = 2.0 + 200.0 / glpane.scale
 
                labelFont = QFont( QString("Lucida Grande"), font_scale)
                fm = QFontMetrics(labelFont)
                
                # Calculate the font extents
                dx, dy = _realTextSize("X", fm)

                # Get the axis atoms
                axis_atoms = axis.baseatoms 
                
                # Get the strand atoms
                strand_atoms = [None, None]
                for i in range(0, len(chunk.ladder.strand_rails)):
                    strand_atoms[i] = chunk.ladder.strand_rails[i].baseatoms
                            
                base_list = []
                    
                if mode == 0:
                    ssep = 7.0
                elif mode == 1 \
                     or mode == 2:
                    ssep = 5.0
                
                # Prepare a list of bases to render and their positions.
                for pos in range(0, n_bases):
                    atom0 = axis_atoms[pos]
                    if pos < n_bases-1:
                        atom1 = axis_atoms[pos+1]
                        dpos = atom1.posn() - atom0.posn()
                    else:
                        atom1 = axis_atoms[pos-1]
                        atom2 = axis_atoms[pos]
                        dpos = atom2.posn() - atom1.posn()                           
                    last_dpos = dpos
                    # Project the axis atom position onto a current view plane
                    out = chunk.quat.unrot(glpane.out)
                    if flipped:
                        dvec = norm(cross(dpos, -out))
                    else:
                        dvec = norm(cross(dpos, out))                    
                    pos0 = chunk.abs_to_base(atom0.posn())
                    s_atom0 = s_atom1 = None
                    if strand_atoms[0]:
                        if pos < len(strand_atoms[0]):
                            s_atom0 = strand_atoms[0][pos]
                    if strand_atoms[1]:
                        if pos < len(strand_atoms[1]):
                            s_atom1 = strand_atoms[1][pos]
                    s_atom0_pos = pos0 + ssep * dvec
                    s_atom1_pos = pos0 - ssep * dvec
                    str_atoms = [s_atom0, s_atom1]
                    str_pos = [s_atom0_pos, s_atom1_pos]
                    base_list.append((atom0, pos0, 
                                      str_atoms, str_pos)) 
                
                if chunk.isStrandChunk():
                    
                    glLineWidth(lw)

                    for str in [0, 1]:
                        # Draw the strand
                        atom = None
                        for base in base_list:
                            ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                            if str_atoms[str] != None:
                                atom = str_atoms[str]
                                break
        
                        if atom and \
                           chunk == atom.molecule:
                            if atom.molecule.color:
                                strand_color = atom.molecule.color
                            else:
                                strand_color = lightgreen
                            
                            if chunk.picked:
                                strand_color = darkgreen
                                
                            glColor3fv(strand_color)
                            glBegin(GL_LINES)
                            last_str_atom_pos = None
                            for base in base_list:
                                ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                if str_atoms[str]:
                                    if last_str_atom_pos:
                                        glVertex3fv(last_str_atom_pos)
                                        glVertex3fv(str_atoms_pos[str])
                                    last_str_atom_pos = str_atoms_pos[str]
                                else:
                                    last_str_atom_pos = None
        
                            glEnd()
                            
                            if mode == 0 \
                               or mode == 2:
                                glLineWidth(lw)
                            elif mode == 1:
                                glLineWidth(0.4 * lw)
                            
                            glBegin(GL_LINES)
                            # Draw an arrow on 3' atom    
                            if not _draw_arrow(atom):
                                # Check out the other end
                                atom = None
                                for base in base_list:
                                    ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                    if str_atoms[str] != None:
                                        atom = str_atoms[str]                        
                                # Draw an arrow on 3' atom    
                                _draw_arrow(atom)
    
                            
                            glEnd()
                            
                            glLineWidth(lw)

                            glBegin(GL_LINES)
                            
                            # draw the external bonds
                            _draw_external_bonds()
            
                            """
                            for bond in chunk.externs:
                                if bond.atom1.molecule.dad == bond.atom2.molecule.dad: # same group
                                    if bond.atom1.molecule != bond.atom2.molecule: # but different chunks
                                        pos0, dvec = _get_screen_position_of_strand_atom(bond.atom1)
                                        pos1, dvec = _get_screen_position_of_strand_atom(bond.atom2)
                                        if pos0 and pos1:
                                            glVertex3f(pos0[0], pos0[1], pos0[2])
                                            glVertex3f(pos1[0], pos1[1], pos1[2])
                            """
                            
                            # Line drawing done
                            glEnd()
                            
                            # Draw the base letters
                            if mode == 0:
                                for base in base_list:
                                    ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                    if str_atoms[str]:
                                        textpos = ax_atom_pos + 0.5 * (str_atoms_pos[str] - ax_atom_pos)
                                        base_name = str_atoms[str].getDnaBaseName()
                                        label_text = QString(base_name)
                                        textpos -= 0.5 * (dx + dy)  
                                        if chunk.picked:
                                            glColor3fv(darkgreen)
                                        else:
                                            base_color = self._get_base_color(base_name)
                                            glColor3fv(base_color)
                                        glpane.renderText(textpos[0], 
                                                          textpos[1], 
                                                          textpos[2], 
                                                          label_text, labelFont)                    
                            elif mode == 1 \
                                 or mode == 2:
                                if no_axis is False:
                                    glLineWidth(lw)
                                    glBegin(GL_LINES)
                                    if chunk.picked:
                                        glColor3fv(darkgreen)
                                    for base in base_list:
                                        ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                        if str_atoms[str]:
                                            if not chunk.picked:
                                                base_color = self._get_base_color(
                                                    str_atoms[str].getDnaBaseName())
                                                glColor3fv(base_color)   
                                            glVertex3fv(str_atoms_pos[str])
                                            glVertex3fv(ax_atom_pos)                                
                                    glEnd()
                                
                                if mode == 1:
                                    # draw circles interior
                                    for base in base_list:
                                        if chunk.picked:
                                            lcolor = _light_color(darkgreen)
                                        else:
                                            lcolor = _light_color(strand_color)
                                        ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                        if str_atoms[str]:
                                            drawer.drawFilledCircle(
                                                lcolor, 
                                                str_atoms_pos[str] + 3.0 * chunk.quat.unrot(glpane.out), 
                                                1.5, chunk.quat.unrot(glpane.out))                                     
                                
                                    # draw circles border
                                    glLineWidth(3.0)
                                    #glColor3fv(strand_color)
                                    for base in base_list:
                                        ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                                        if str_atoms[str]:
                                            drawer.drawCircle(
                                                strand_color, 
                                                str_atoms_pos[str] + 3.1 * chunk.quat.unrot(glpane.out), 
                                                1.5, chunk.quat.unrot(glpane.out)) 
                                    glLineWidth(1.0)
                    
                if chunk.isAxisChunk():
                    if mode == 0:
                        # Draw filled circles in the center of the axis rail.
                        if chunk.picked:
                            color = darkgreen
                        else:
                            color = black
                        for base in base_list:
                            ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                            if str_atoms[0] and str_atoms[1]:
                                drawer.drawFilledCircle(color, ax_atom_pos, 0.5, chunk.quat.unrot(glpane.out))
                            else:
                                drawer.drawFilledCircle(color, ax_atom_pos, 0.15, chunk.quat.unrot(glpane.out))
                    """
                    elif mode == 1:
                        glLineWidth(10.0)
                        glBegin(GL_LINES)
                        if chunk.picked:
                            glColor3fv(darkgreen)
                        for base in base_list:
                            ax_atom, ax_atom_pos, str_atoms, str_atoms_pos = base
                            if str_atoms[0]:
                                if not chunk.picked:
                                    base_color = self.getBaseColor(
                                        str_atoms[0].getDnaBaseName())
                                    glColor3fv(base_color)   
                                glVertex3fv(str_atoms_pos[0])
                                glVertex3fv(ax_atom_pos)
                            if str_atoms[1]:
                                if not chunk.picked:
                                    base_color = self.getBaseColor(
                                        str_atoms[1].getDnaBaseName())
                                    glColor3fv(base_color)                                    
                                glVertex3fv(str_atoms_pos[1])
                                glVertex3fv(ax_atom_pos)                        
                        
                        glEnd()
                    """
                    
                glEnable(GL_LIGHTING)              
                
                glLineWidth(1.0) 
            
                # line width should be restored to initial value
                # but I think 1.0 is maintained within the program

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
        self.dnaStyleAxisEndingStyle = env.prefs[dnaStyleAxisEndingStyle_prefs_key]
        self.dnaStyleStrutsShape = env.prefs[dnaStyleStrutsShape_prefs_key]
        self.dnaStyleStrutsColor = env.prefs[dnaStyleStrutsColor_prefs_key]
        self.dnaStyleStrutsScale = env.prefs[dnaStyleStrutsScale_prefs_key]                
        self.dnaStyleBasesShape = env.prefs[dnaStyleBasesShape_prefs_key]
        self.dnaStyleBasesColor = env.prefs[dnaStyleBasesColor_prefs_key]
        self.dnaStyleBasesScale = env.prefs[dnaStyleBasesScale_prefs_key]
        self.dnaStyleBasesDisplayLetters = env.prefs[dnaStyleBasesDisplayLetters_prefs_key]

        self.dnaExperimentalMode = 0

        # render in experimental 2D mode?
        # piotr 080416
        dna_style = debug_pref(
              "DNA style: ",
               Choice(["Default", 
                       "Experimental mode 1", 
                       "Experimental mode 2", 
                       "Experimental mode 3"], 
                      defaultValue = "Default"),
               non_debug = False, 
               prefs_key = True 
           )
        
        # set the experimental mode
        if dna_style == "Experimental mode 1":
            self.dnaExperimentalMode = 1
        
        if dna_style == "Experimental mode 2":
            self.dnaExperimentalMode = 2
        
        if dna_style == "Experimental mode 3":
            self.dnaExperimentalMode = 3
        

        if not hasattr(chunk, 'ladder'):
            # DNA updater is off ?      
            # Don't render (should display a warning message?)
            return None

        if not chunk.atoms or not chunk.ladder: 
            # nothing to display - return
            return None

        n_bases = chunk.ladder.baselength()    
        if n_bases<1: 
            # no bases - return
            return None

        # make sure there is a chunk color
        if chunk.color:
            chunk_color = chunk.color
        else:
            # sometimes the chunk.color is not defined            
            chunk_color = white

        # atom positions in strand and axis
        strand_positions = axis_positions = None

        # number of strand in the ladder
        num_strands = chunk.ladder.num_strands()

        current_strand = 0

        strand_atoms = [None] * num_strands
        strand_colors = [None] * num_strands
        for i in range(0, num_strands):
            strand_atoms[i] = chunk.ladder.strand_rails[i].baseatoms
            if chunk.ladder.strand_rails[i].baseatoms[0].molecule == chunk:
                current_strand = i

        axis_atoms = None
        if chunk.ladder.axis_rail:
            axis_atoms = chunk.ladder.axis_rail.baseatoms

        group_color = white

        five_prime_atom = three_prime_atom = None
        strand_direction = 0

        start_index = end_index = 0
        total_strand_length = 1

        if chunk.isAxisChunk() \
           and axis_atoms \
           and self.dnaStyleAxisColor == 4: # axis chunk
            
            longest_rail = None
            longest_wholechain = None
            longest_length = 0
            
            strand_rails = chunk.ladder.strand_rails      
            for rail in strand_rails:
                length = len(rail.baseatoms[0].molecule.wholechain)
                if length > longest_length:
                    longest_length = length
                    longest_rail = rail
                    longest_wholechain = rail.baseatoms[0].molecule.wholechain
                    
            wholechain = longest_wholechain
            
            pos0, pos1 = wholechain.wholechain_baseindex_range()
            idx = wholechain.wholechain_baseindex(longest_rail, 0)
            
            group_color = self._get_nice_rainbow_color_in_range(
                idx - pos0, 
                pos1 - pos0, 
                0.75,
                1.0)
            
        elif chunk.isStrandChunk(): # strand chunk
            strand_group = chunk.getDnaGroup()
            if strand_group:
                strands = strand_group.getStrands()
                group_color = self._get_rainbow_color_in_range(
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

                    """
                    print "(0) start_index end_index total_strand_length ", (start_index, end_index, total_strand_length)
                    
                    
                    pos0, pos1 = wholechain.wholechain_baseindex_range()
                    rail = chunk.ladder.strand_rails[current_strand]
                    idx0 = wholechain.wholechain_baseindex(rail, 0)
                    idx1 = wholechain.wholechain_baseindex(rail, len(strand_atoms[current_strand])-1)
                    
                    print "pos0 pos1 idx0 idx1 ", (pos0, pos1, idx0, idx1)
                    
                    total_strand_length = pos1 - pos0 + 1
                    start_index = idx0 - pos0
                    end_index = idx1 - pos0
                    
                    if strand_direction == -1:
                        tmp = start_index
                        start_index = end_index
                        end_index = tmp
                    """
                    
                n_atoms = len(strand_atoms)

        polycylinder_positions = None
        polycylinder_colors = None
        polycylinder_radii = None
        
        # pre-calculate polycylinder positions (main drawing primitive
        # for strands and/or central axis

        if chunk.isAxisChunk() \
            and num_strands > 1: 
            # make sure there are two strands present in the rail
            # piotr 080430 (fixed post-FNANO Top 20 bugs)
            polycylinder_positions = self._get_axis_positions(
                chunk, 
                axis_atoms, 
                self.dnaStyleAxisColor)
            polycylinder_colors = self._get_axis_colors(
                axis_atoms, 
                strand_atoms, 
                self.dnaStyleAxisColor, 
                chunk_color, 
                group_color)
            polycylinder_radii = self._get_axis_radii(axis_atoms, 
                self.dnaStyleAxisColor, 
                self.dnaStyleAxisShape,
                self.dnaStyleAxisScale,
                self.dnaStyleAxisEndingStyle)
        elif chunk.isStrandChunk():
            polycylinder_positions = self._get_strand_positions(
                chunk, strand_atoms[current_strand])
            polycylinder_colors = self._get_strand_colors(
                strand_atoms[current_strand], 
                self.dnaStyleStrandsColor,
                start_index, end_index, total_strand_length,
                chunk_color, group_color)
            polycylinder_radii = self._get_strand_radii(
                strand_atoms[current_strand], 
                self.dnaStyleStrandsScale)
            
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
                current_strand,
                polycylinder_positions,
                polycylinder_colors,
                polycylinder_radii)

    pass # end of class DnaCylinderChunks

ChunkDisplayMode.register_display_mode_class(DnaCylinderChunks)

# end
