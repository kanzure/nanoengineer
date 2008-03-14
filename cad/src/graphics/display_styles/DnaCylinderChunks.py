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

piotr 080310: total rewrite

"""

from Numeric import dot, argmax, argmin, sqrt

import foundation.env as env
import graphics.drawing.drawer as drawer
from geometry.geometryUtilities import matrix_putting_axis_at_z
from geometry.VQT import V, norm, cross, angleBetween
from debug import print_compact_traceback
from graphics.display_styles.displaymodes import ChunkDisplayMode
from constants import ave_colors, red, white, darkgreen

from prefs_constants import atomHighlightColor_prefs_key

# piotr 080309: user pereferences for DNA style
from prefs_constants import dnaStyleStrandsColor_prefs_key
from prefs_constants import dnaStyleAxisColor_prefs_key
from prefs_constants import dnaStyleStrutsColor_prefs_key
from prefs_constants import dnaStyleBasesColor_prefs_key
from prefs_constants import dnaStyleStrandsShape_prefs_key
from prefs_constants import dnaStyleBasesShape_prefs_key
from prefs_constants import dnaStyleStrandsArrows_prefs_key
from prefs_constants import dnaStyleAxisShape_prefs_key
from prefs_constants import dnaStyleStrutsShape_prefs_key
from prefs_constants import dnaStyleStrandsScale_prefs_key
from prefs_constants import dnaStyleAxisScale_prefs_key
from prefs_constants import dnaStyleBasesScale_prefs_key
from prefs_constants import dnaStyleAxisTaper_prefs_key
from prefs_constants import dnaStyleStrutsScale_prefs_key

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
from OpenGL.GL import GL_LINE_STRIP        
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

from chunk import Chunk

chunkHighlightColor_prefs_key = atomHighlightColor_prefs_key # initial kluge

class DnaCylinderChunks(ChunkDisplayMode):
    """
    DNA Cylinder display mode, which draws "axis" chunks as a cylinder.
    
    Limitations/known bugs:
    - Cylinders are always straight. DNA axis chunks with atoms that are not 
    aligned in a straight line are not displayed correctly (i.e. they don't
    follow a curved axis path. fixed 080310 piotr
    - Hover highlighting does not work. piotr: to be done 
    - Selected chunks are not colored in the selection color. piotr: to be done
    - Cannot drag/move a selected cylinder interactively. piotr: to be done
    - DNA Cylinders are not written to POV-Ray file. piotr: to be done
    - DNA Cylinders are not written to PDB file and displayed in QuteMolX.
    piotr: to be done

    @note: Nothing else is rendered (no atoms, sugar atoms, etc) when 
        set to this display mode.
                
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
    ##e also should define icon as an icon object or filename, either in class or in each instance
    ##e also should define a featurename for wiki help
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
        
        080310 piotr
        
        I have rewritten most of the code here from scratch. Most of the code
        computed within this function has to be moved to "memo" for a speed
        optimization. There are several issues with this rendering code,
        including lack of highlighting and selection support, and some
        weird behavior when modeltree is used to select individual strands.
        
        There are four independent structures within the DNA display style:
        axis, strands, struts and bases. Properties of these parts can be set
        in the User Preferences dialog.
        
        The DNA style requires DNA updater to be enabled.
        
        """
        
        def spline(data, idx, t):
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
            return 0.5*((2.0*x1)+
                        (-x0+x2)*t+
                        (2.0*x0-5.0*x1+4.0*x2-x3)*t2+
                        (-x0+3.0*x1-3.0*x2+x3)*t3)
        
        def getRainbowColor(hue, saturation, value):
            """
            Gets a color of a full hue range limited to 0 - 0.667 (red - blue)
            """
            if hue<0.0: hue=0.0
            if hue>1.0: hue=1.0
            return colorsys.hsv_to_rgb(0.667-0.677*hue, saturation, value)
        
        def getBaseColor(base):
            """
            Returns a color according to DNA base type.
            """
            if base=="G":
                return ([0.8,0.5,0.0])
            elif base=="C":
                return ([0.8,0.1,0.0])
            if base=="A":
                return ([0.2,0.8,0.4])
            elif base=="T":
                return ([0.0,0.6,0.8])
            else:
                return ([0.5,0.5,0.5])
            
        def getRainbowColorInRange(pos, count, saturation, value):
            if count>1: count -= 1
            hue = float(pos)/float(count)
            if hue<0.0: hue = 0.0
            if hue>1.0: hue = 1.0
            return getRainbowColor(hue, saturation, value)

        def getStrandChunks(dna_group):
            """
            Returns a list of Strand chunks inside a DnaGroup object
            
            @return: A list containing all the strand chunks
                     within self.
            @rtype: list
            """
            strandChunkList = []
            def filterStrandChunks(node):
                if isinstance(node, Chunk) and node.isStrandChunk():
                    strandChunkList.append(node)    
                    
            dna_group.apply2all(filterStrandChunks)
            
            return strandChunkList
        
        def drawStrand(points, colors, radii, color_style, shape, arrows):
            """
            Renders a strand shape along points array using colors 
            and radii arrays, optionally with arrows. 
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
                if shape==1: # draw cylinders
                    gleSetJoinStyle(TUBE_JN_ROUND | TUBE_NORM_PATH_EDGE 
                                    | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED)        
                    #drawer.drawpolycone(colors[1], 
                    #                    points,
                    #                    radii)
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
                    new_points = zeros([4*(n-2)-1,3],Float)
                    new_colors = zeros([4*(n-2)-1,3],Float)
                    new_radii = zeros([4*(n-2)-1],Float)
                    o = 1
                    for p in range (1,n-2):
                        for m in range (0,4):
                            t = float(m)/4.0
                            new_points[o] = spline(points, p, t)
                            new_colors[o] = spline(colors, p, t)
                            new_radii[o] = spline(radii, p, t)
                            o += 1        
                    new_points[o] = spline(points, p, 1.0)
                    new_colors[o] = spline(colors, p, 1.0)
                    new_radii[o] = spline(radii, p, 1.0)
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
            # draw the arrows
            if arrows==1 or arrows==3:
                drawer.drawpolycone(colors[n-2],
                                    [points[n-2],
                                     points[n-2],
                                     2.0*points[n-2]-points[n-3],
                                     2.0*points[n-2]-points[n-3]],
                                     [radii[1]*2.0,
                                      radii[1]*2.0,
                                      0.0,
                                      0.0])
            if arrows==2 or arrows==3:
                drawer.drawpolycone(colors[1],
                                    [points[1],
                                     points[1],
                                     2.0*points[2]-points[3],
                                     2.0*points[2]-points[3]],
                                     [radii[1]*2.0,
                                      radii[1]*2.0,
                                      0.0,
                                      0.0])
                
        # ---------------------------------------------------------------------

        if not memo: # nothing to render
            return

        n_bases = chunk.ladder.baselength()    
        if n_bases<1: # no bases? quit
            return

        # import the style preferences from User Preferences
        dnaStyleStrandsShape = env.prefs[dnaStyleStrandsShape_prefs_key]
        dnaStyleStrandsColor = env.prefs[dnaStyleStrandsColor_prefs_key]
        dnaStyleStrandsScale = env.prefs[dnaStyleStrandsScale_prefs_key]
        dnaStyleStrandsArrows = env.prefs[dnaStyleStrandsArrows_prefs_key]        
        dnaStyleAxisShape = env.prefs[dnaStyleAxisShape_prefs_key]
        dnaStyleAxisColor = env.prefs[dnaStyleAxisColor_prefs_key]
        dnaStyleAxisScale = env.prefs[dnaStyleAxisScale_prefs_key]
        dnaStyleAxisTaper = env.prefs[dnaStyleAxisTaper_prefs_key]
        dnaStyleStrutsShape = env.prefs[dnaStyleStrutsShape_prefs_key]
        dnaStyleStrutsColor = env.prefs[dnaStyleStrutsColor_prefs_key]
        dnaStyleStrutsScale = env.prefs[dnaStyleStrutsScale_prefs_key]                
        dnaStyleBasesShape = env.prefs[dnaStyleBasesShape_prefs_key]
        dnaStyleBasesColor = env.prefs[dnaStyleBasesColor_prefs_key]
        dnaStyleBasesScale = env.prefs[dnaStyleBasesScale_prefs_key]
           
        # set a default chunk color
        chunk_color = chunk.color
        chunk_selected = False
        
        if chunk.picked: # set darkgreen color if selected
            chunk_selected = True
            chunk_color = darkgreen

        if highlighted: # set yellow color if highlighted
            chunk_selected = True
            chunk_color = yellow

        # these arrays have to be filled-in by "memo"
        points = zeros([n_bases+2,3],Float)
        colors = zeros([n_bases+2,3],Float)
        radii = zeros([n_bases+2],Float)
        
        # render axis cylinder        
        if chunk.isAxisChunk(): # this is the DNA axis           
            if dnaStyleAxisShape>0:
                # get the group color (axis chunks order)
                axis_chunks = chunk.getDnaGroup().getAxisChunks()
                group_color = getRainbowColorInRange(
                    axis_chunks.index(chunk), len(axis_chunks), 0.75, 1.0)                             

                if dnaStyleAxisShape==1:
                    rad = 7.0*dnaStyleAxisScale
                else:    
                    rad = 2.0*dnaStyleAxisScale
                if dnaStyleAxisColor==2 or dnaStyleAxisColor==3: # render discrete colors
                    points = zeros([2*n_bases+2,3],Float) # re-alloc the arrays
                    colors = zeros([2*n_bases+2,3],Float)
                    radii = zeros([2*n_bases+2],Float)                
                    pos = 2
                    for base in range (1,n_bases):
                        pos1 = chunk.ladder.axis_rail.baseatoms[base-1].posn()-chunk.center
                        pos2 = chunk.ladder.axis_rail.baseatoms[base].posn()-chunk.center                  
                        if dnaStyleAxisColor==2: 
                            color1 = getRainbowColorInRange(base-1, n_bases, 0.75, 1.0)
                            color2 = getRainbowColorInRange(base, n_bases, 0.75, 1.0)
                        else:
                            color1 = getBaseColor(
                                chunk.ladder.strand_rails[0].baseatoms[base-1].getDnaBaseName())
                            color2 = getBaseColor(
                                chunk.ladder.strand_rails[0].baseatoms[base].getDnaBaseName())
                        points[pos] = 0.5*(pos1+pos2)
                        colors[pos] = color1
                        radii[pos] = rad
                        points[pos+1] = 0.5*(pos1+pos2)
                        colors[pos+1] = color2
                        radii[pos+1] = rad
                        pos += 2
                    radii[1] = radii[2*n_bases] = rad
                    points[1] = chunk.ladder.axis_rail.baseatoms[0].posn()-chunk.center
                    colors[1] = colors[2]           
                    points[2*n_bases] = chunk.ladder.axis_rail.baseatoms[n_bases-1].posn()-chunk.center
                    colors[2*n_bases] = colors[2*n_bases-1]
                    pos = 2*n_bases+1
                    # taper the ends
                    if dnaStyleAxisTaper==2 or dnaStyleAxisTaper==3:
                        radii[1] = 0.0
                        radii[2] = 0.5*rad
                        radii[3] = 0.5*rad
                    if dnaStyleAxisTaper==1 or dnaStyleAxisTaper==3:
                        radii[pos-3] = 0.5*rad
                        radii[pos-2] = 0.5*rad
                        radii[pos-1] = 0.0
                else:
                    for pos in range (1,n_bases+1):
                        points[pos] = chunk.ladder.axis_rail.baseatoms[pos-1].posn()-chunk.center
                        if dnaStyleAxisColor==0 or chunk_selected:
                            colors[pos] = chunk_color
                        elif dnaStyleAxisColor==1:
                            colors[pos] = getRainbowColorInRange(pos-1, n_bases, 
                                                                 0.75, 1.0)
                        else:
                            colors[pos] = group_color
                        radii[pos] = rad
                        pos += 1
                    # taper the ends
                    if dnaStyleAxisTaper==2 or dnaStyleAxisTaper==3:
                        radii[1] = 0.0
                        radii[2] = 0.66*rad
                    if dnaStyleAxisTaper==1 or dnaStyleAxisTaper==3:
                        radii[pos-2] = 0.66*rad
                        radii[pos-1] = 0.0        
                
                # compute dummy first and last coordinates    
                points[0] = 2.0*points[1]-points[2]   
                points[pos] = 2.0*points[pos-1]-points[pos-2]
                
                # spherical ends    
                if dnaStyleAxisTaper==4:
                    drawer.drawsphere(colors[1], 
                                      points[1], radii[1], 2)
                    drawer.drawsphere(colors[pos-1], 
                                      points[pos-1], radii[pos-1], 2)                    
                # draw the polycone
                gleSetJoinStyle(TUBE_JN_ANGLE | TUBE_NORM_PATH_EDGE 
                                | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED) 
            if dnaStyleAxisColor==1 or dnaStyleAxisColor==2 or dnaStyleAxisColor==3: # render discrete colors                
                drawer.drawpolycone_multicolor(colors[1], points, colors, radii)
            else:   
                drawer.drawpolycone(colors[1], points, radii)

        elif chunk.isStrandChunk(): # strands, struts and bases            
            if chunk==chunk.ladder.strand_rails[0].baseatoms[0].molecule:
                chunk_strand = 0
            else:
                chunk_strand = 1
                
            # figure out the color according to strand order
            strands = chunk.getDnaGroup().getStrands()
            group_color = getRainbowColorInRange(
                strands.index(chunk.dad), len(strands), 0.75, 1.0)
            
            # render strands        
            if dnaStyleStrandsShape>0:
                for pos in range (1,n_bases+1):
                    atom_pos = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos-1].posn()-chunk.center
                    if chunk_strand==0: # 5'->3' strand
                        points[pos] = atom_pos
                    else: # 3'->5' strand
                        points[n_bases-pos+1] = atom_pos
                    if dnaStyleStrandsColor==0 or chunk_selected:
                        colors[pos] = chunk_color
                    elif dnaStyleStrandsColor==1:
                        colors[pos] = getRainbowColorInRange(pos-1, n_bases, 0.75, 1.0)
                    else:
                        colors[pos] = group_color
                    radii[pos] = 1.0*dnaStyleStrandsScale

                # compute first and last dummy atom coordinates    
                points[0] = 3.0*points[1]-3.0*points[2]+points[3]              
                points[pos+1] = 3.0*points[pos]-3.0*points[pos-1]+points[pos-2]                       
                    
                # handle external bonds, if any
                for bond in chunk.externs:
                    if bond.atom1.molecule.dad==bond.atom2.molecule.dad: # same group
                        if bond.atom1.molecule!=bond.atom2.molecule: # but different chunks
                            drawer.drawcylinder(
                                colors[1], 
                                bond.atom1.posn()-chunk.center, 
                                bond.atom2.posn()-chunk.center, 1.0*dnaStyleStrandsScale, True)                        
                            if bond.atom1==chunk.ladder.strand_rails[chunk_strand].baseatoms[0].posn():
                                points[1] = bond.atom2.posn()-chunk.center
                            if bond.atom1==chunk.ladder.strand_rails[chunk_strand].baseatoms[n_bases-1].posn():
                                points[pos] = bond.atom2.posn()-chunk.center
                            if bond.atom2==chunk.ladder.strand_rails[chunk_strand].baseatoms[0].posn():
                                points[1] = bond.atom1.posn()-chunk.center
                            if bond.atom2==chunk.ladder.strand_rails[chunk_strand].baseatoms[n_bases-1].posn():
                                points[pos] = bond.atom1.posn()-chunk.center
                
                drawStrand(points, colors, radii, dnaStyleStrandsColor, dnaStyleStrandsShape, dnaStyleStrandsArrows)

            # render struts
            if dnaStyleStrutsShape>0:
                for pos in range(0,n_bases):
                    atom1 = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos]
                    atom3 = chunk.ladder.strand_rails[1-chunk_strand].baseatoms[pos]
                    if dnaStyleStrutsShape==1:
                        atom2_pos = chunk.ladder.axis_rail.baseatoms[pos].posn()-chunk.center
                    elif dnaStyleStrutsShape==2:
                        atom2_pos = 0.5*(atom1.posn()+atom3.posn())-chunk.center
                    if dnaStyleStrutsColor==0 or chunk_selected:
                        color = chunk_color
                    elif dnaStyleStrutsColor==1:
                        color = getRainbowColorInRange(pos, n_bases, 0.75, 1.0)                        
                    elif dnaStyleStrutsColor==2:
                        color = group_color
                    else:
                        color = getBaseColor(atom1.getDnaBaseName())
                    drawer.drawcylinder(color, atom1.posn()-chunk.center, atom2_pos, 0.5*dnaStyleStrutsScale, True)

            # render bases
            if dnaStyleBasesShape>0:
                for pos in range(0,n_bases):
                    atom = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos]
                    if dnaStyleBasesColor==0 or chunk_selected:
                        color = chunk_color
                    elif dnaStyleBasesColor==1:
                        if chunk_strand==0:
                            color = getRainbowColorInRange(pos, n_bases, 0.75, 1.0)
                        else:
                            color = getRainbowColorInRange(n_bases-pos+1, n_bases, 0.75, 1.0)                        
                    elif dnaStyleBasesColor==2:
                        color = group_color
                    else:
                        color = getBaseColor(atom.getDnaBaseName())
                    if dnaStyleBasesShape==1: # draw spheres
                        drawer.drawsphere(color, atom.posn()-chunk.center, dnaStyleBasesScale, 2)
                    elif dnaStyleBasesShape==2: # draw a schematic 'cartoon' shape
                        a1posn = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos].posn()-chunk.center
                        a2posn = chunk.ladder.axis_rail.baseatoms[pos].posn()-chunk.center
                        a3posn = chunk.ladder.strand_rails[1-chunk_strand].baseatoms[pos].posn()-chunk.center
                        # figure out a normal to the bases plane
                        v1 = a1posn-a2posn
                        v2 = a1posn-a3posn
                        normal = norm(cross(v1,v2))
                        bposn = a1posn+0.66*(a2posn-a1posn)
                        drawer.drawcylinder(
                            color, 
                            a1posn, 
                            bposn, 
                            0.25*dnaStyleBasesScale, True)
                        drawer.drawcylinder(
                            color, 
                            bposn-0.33*dnaStyleBasesScale*normal,
                            bposn+0.33*dnaStyleBasesScale*normal,
                            2.0*dnaStyleBasesScale, True)
                        
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
    
    def drawchunk_realtime(self, glpane, chunk):
        """
        Draws the chunk that may depend on current view.
        """
        ### drawchunk(self, glpane, chunk, selection_frame_color, memo, highlighted)
        from constants import lightgreen
        if 0:
            if chunk.isStrandChunk(): 
                n_bases = chunk.ladder.baselength()
                if chunk==chunk.ladder.strand_rails[0].baseatoms[0].molecule:
                    chunk_strand = 0
                else:
                    chunk_strand = 1
                for pos in range(0,n_bases):
                    atom1 = chunk.ladder.strand_rails[chunk_strand].baseatoms[pos]
                    atom2 = chunk.ladder.axis_rail.baseatoms[pos]
                    # compute a normal to the view plane
                    vz = glpane.quat.unrot(V(0.0,0.0,1.0)) 
                    v2 = norm(atom1.posn()-atom2.posn())
                    a = angleBetween(vz,v2)
                    if abs(a)<30.0:
                        drawer.drawsphere(lightgreen,atom1.posn(),1.5,2)
    
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
        # Since chunk.axis is not always one of the vectors chunk.evecs (actually chunk.poly_evals_evecs_axis[2]),
        # it's best to just use the axis and center, then recompute a bounding cylinder.
        if not chunk.atoms:
            return None
        
        if not chunk.ladder:
            return None
        
        return (chunk.ladder)
    
    pass # end of class DnaCylinderChunks

ChunkDisplayMode.register_display_mode_class(DnaCylinderChunks)

# end
