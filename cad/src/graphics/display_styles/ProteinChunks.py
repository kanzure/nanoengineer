# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ProteinChunks.py -- defines I{Reduced Protein} display modes.

@author: Piotr
@version: 
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details. 

History:

piotr 080623: First preliminary version of the protein display style.

"""

from model.chunk import Chunk

from geometry.VQT import V, norm

from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.CS_draw_primitives import drawpolycone
from graphics.drawing.CS_draw_primitives import drawpolycone_multicolor
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.CS_draw_primitives import drawtriangle_strip

from OpenGL.GL import glBegin
from OpenGL.GL import glColor3f
from OpenGL.GL import glEnd
from OpenGL.GL import GL_QUADS
from OpenGL.GL import glVertex3fv

import colorsys

from graphics.drawing.gl_lighting import apply_material

from utilities.constants import blue, cyan, green, orange, red, white, black

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
    print "Protein Chunks: GLE module can't be imported. Now trying _GLE"
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


# protein coloring styles    
PROTEIN_COLOR_CHUNK       = 0
PROTEIN_COLOR_ORDER       = 1
PROTEIN_COLOR_POLAR       = 2
PROTEIN_COLOR_SIZE        = 3
PROTEIN_COLOR_TEMPERATURE = 4


# 3-letter to 1-letter conversion
AA_3_TO_1 = {
    "ALA" : "A",
    "ARG" : "R",
    "ASN" : "N",
    "ASP" : "D",
    "CYS" : "C",
    "GLN" : "E",
    "GLU" : "Q",
    "GLY" : "G",
    "HIS" : "H",
    "ILE" : "I",
    "LEU" : "L",
    "LYS" : "K",
    "MET" : "M",
    "PHE" : "F",
    "PRO" : "P",
    "SER" : "S",
    "THR" : "T",
    "TRP" : "W",
    "TYR" : "Y",
    "VAL" : "V" }
    
# coloring according to amino acid hydropathy scale (Kyte-Doolittle)
AA_COLORS_HYDROPATHY = { 
    "ALA" : orange,
    "ARG" : blue,
    "ASN" : blue,
    "ASP" : blue,
    "CYS" : orange,
    "GLN" : blue,
    "GLU" : blue,
    "GLY" : green,
    "HIS" : blue,
    "ILE" : red,
    "LEU" : red,
    "LYS" : blue,
    "MET" : orange,
    "PHE" : orange,
    "PRO" : cyan,
    "SER" : green,
    "THR" : green,
    "TRP" : green,
    "TYR" : cyan,
    "VAL" : red }

# coloring according to amino acid polarity
AA_COLORS_POLARITY = { 
    "ALA" : red,
    "ARG" : green,
    "ASN" : green,
    "ASP" : green,
    "CYS" : green,
    "GLN" : green,
    "GLU" : green,
    "GLY" : red,
    "HIS" : green,
    "ILE" : red,
    "LEU" : red,
    "LYS" : green,
    "MET" : red,
    "PHE" : red,
    "PRO" : red,
    "SER" : green,
    "THR" : green,
    "TRP" : red,
    "TYR" : red,
    "VAL" : red }

# coloring according to amino acid acidity
AA_COLORS_ACIDITY = { 
    "ALA" : green,
    "ARG" : blue,
    "ASN" : green,
    "ASP" : red,
    "CYS" : green,
    "GLN" : green,
    "GLU" : red,
    "GLY" : green,
    "HIS" : blue,
    "ILE" : green,
    "LEU" : green,
    "LYS" : blue,
    "MET" : green,
    "PHE" : green,
    "PRO" : green,
    "SER" : green,
    "THR" : green,
    "TRP" : green,
    "TYR" : green,
    "VAL" : green }

def postprocess_pdb_line(line, mol, atom):
    ###print "postprocessing line ", line
    
    if mol is None:
        return
    
    key = line[:6].lower().replace(" ", "")
    
    ###print "key = ", key
    
    if atom and \
       key in ["atom", "hetatm"]:
        atom_name = line[12:15].replace(" ", "").replace("_", "")
        ##print "atom_name = ", atom_name
        if atom_name == "CA":
            atom._protein_ca = True
            ##print "has ca"
        else:
            atom._protein_ca = False
    
        if atom_name == "CB":
            atom._protein_cb = True
            ##print "has ca"
        else:
            atom._protein_cb = False
    
        if atom_name == "N":
            atom._protein_n = True
        else:
            atom._protein_n = False
    
        if atom_name == "C":
            atom._protein_c = True
        else:
            atom._protein_c = False
    
        if atom_name == "O":
            atom._protein_o = True
        else:
            atom._protein_o = False
    
        ##print "to map: ", line[61:67]
        temp = map(float, [line[61:67]])
        ###print "temp = ", temp
        atom._protein_temp_factor = temp
        atom._protein_res_name = line[17:20]
        ##print "res name = ", atom._protein_res_name
        pass

    if key in ["helix"]:
        print "HELIX: ", line
        begin = map(int, [line[22:25]])
        end = map(int, [line[34:37]])
        print "begin, end = ", (begin, end)
        if not hasattr(mol, "_protein_helix"):
            mol._protein_helix = []
        for s in range(begin[0], end[0]+1):
            mol._protein_helix.append(s)
            print "helix: ", s
        pass
    
    if key in ["sheet"]:
        print "SHEET: ", line
        begin = map(int, [line[23:26]])
        end = map(int, [line[34:37]])
        print "begin, end = ", (begin, end)
        if not hasattr(mol, "_protein_sheet"):
            mol._protein_sheet = []
        for s in range(begin[0], end[0]+1):
            mol._protein_sheet.append(s)
            print "sheet: ", s
        pass
    
    if key in ["turn"]:
        print "TURN: ", line
        pass
    

def compute_spline(data, idx, t):
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

def make_tube(points, colors, radii, resolution=8):
    """
    Converts a polycylinder tube to a smooth, curved tube
    using spline interpolation of points, colors and radii.
    """
    n = len(points)
    print "points = ", points
    if n > 3:
        new_points = []
        new_colors = []
        new_radii = []
        o = 1
        new_points.append(points[0])
        new_colors.append(colors[0])
        new_radii.append(radii[0])
        ir = 1.0/float(resolution)
        for p in range (1, n-2):
            for m in range (0, resolution):
                t = ir * m
                sp = compute_spline(points, p, t)
                sc = compute_spline(colors, p, t)
                sr = compute_spline(radii, p, t)
                new_points.append(sp)
                new_colors.append(sc)
                new_radii.append(sr)
        new_points.append(sp)
        new_colors.append(sc)
        new_radii.append(sr)
        return (new_points, new_colors, new_radii)
    else:
        return (points, colors, radii)
    
def get_rainbow_color(hue, saturation, value):
    """
    Gets a color of a hue range limited to 0 - 0.667 (red - blue)
    """

    hue = 0.666 * (1.0 - hue)
    if hue < 0.0: 
        hue = 0.0
    if hue > 0.666: 
        hue = 0.666
    return colorsys.hsv_to_rgb(hue, saturation, value)
    
def get_rainbow_color_in_range(pos, count, saturation, value):
    if count > 1: 
        count -= 1
    hue = float(pos)/float(count)        
    if hue < 0.0: 
        hue = 0.0
    if hue > 1.0: 
        hue = 1.0
    return get_rainbow_color(hue, saturation, value)

def display_protein(chunk, style, color):
    from utilities.constants import gray, cyan, green, orange, white

    print "display protein"
        
    n_ca = 0
    for atom in chunk.atoms.itervalues():
        if hasattr(atom, "_protein_ca"):
            if atom._protein_ca:
                n_ca += 1
            
    if n_ca:
        points = []
        colors = []
        radii  = []

        ### strands

        last_ca_atom = None
        last_c_atom = None
        last_o_atom = None
        
        ca = 0
        apply_material(white)
        
        line_points = []
        line_plates = []
        
        from Numeric import dot
        
        helix = []
        sheet = []
        
        if hasattr(chunk, "_protein_helix"):
            helix = chunk._protein_helix
            
        if hasattr(chunk, "_protein_sheet"):
            sheet = chunk._protein_sheet
            
        last_dpos = None
        for atom in chunk.atoms.itervalues():
            if hasattr(atom, "_protein_ca"):
                
                if atom._protein_ca:
                    if last_ca_atom and last_c_atom and last_o_atom:
                        pos0 = chunk.abs_to_base(last_ca_atom.posn())
                        pos1 = chunk.abs_to_base(atom.posn())
                        dpos = last_o_atom.posn() - last_c_atom.posn()
                        if last_dpos:
                            n0 = norm(last_dpos)
                            n1 = norm(dpos)
                            d = dot(n0, n1)
                            #print "d = ", d
                            if dot(n0, n1) < 0.0:
                                #print "invert ", dpos
                                dpos = -1.0 * dpos
                                #print " = ", dpos
                        line_points.append(pos0)
                        line_plates.append(dpos)
                        last_dpos = dpos
                        #color = get_rainbow_color_in_range(ca, n_ca, 1.0, 1.0)
                        #for i in range(0, 10):
                        #    di = 0.2 * i - 1.0
                        #    p0 = pos0 + di * dpos
                        #    p1 = pos1 + di * dpos
                        #    points
                        #    drawline(color, p0, p1, width=2)
                        pass
                    
                    ca += 1           
                    last_ca_atom = atom

                if atom._protein_c:
                    last_c_atom = atom
                    
                if atom._protein_o:
                    last_o_atom = atom

        
        # average C-alpha positions
        
        for iter in range(0, 2):
            n_points = len(line_points)
            line_points_avg = []        
            line_plates_avg = []        
            print "iter = ", iter
            for p in range(0, n_points):
                #if p > 0:
                #    drawline(cyan, line_points[p-1], line_points[p], width=3)
                avg_pt = line_points[p]
                avg_pl = line_plates[p]
                if p+1 in helix or \
                    p in helix or \
                    p+2 in helix:
                    if p-1 >= 0 and p+1 < n_points:
                        ##avg_pt = 0.25 * (line_points[p-2] + line_points[p-1] + line_points[p+1] + line_points[p+2])
                        avg_pt = 0.333 * (line_points[p-1] + line_points[p] + line_points[p+1])
                        dd = 2.0 * norm(line_points[p] - avg_pt)
                        ##avg_pt = dd
                    if iter == 1:
                        dd = 2.0 * norm(line_points[p] - avg_pt)
                        avg_pt += dd
                    if iter < 3:
                        avg_pl = V(0, 0, 0)
                        na = 0
                        for a in range (-1, 2):
                            if p + a >= 0 and \
                               p + a < n_points:
                                avg_pl = avg_pl + line_plates[p + a]
                                na += 1
                        avg_pl *= (1.0 / na )
                elif iter == 0:
                    if p+1 in sheet or \
                       p in sheet or \
                       p+2 in sheet:
                        na = 0
                        """
                        for a in range (-1, 2):
                            if a != 0 and \
                               p + a >= 0 and \
                               p + a < n_points:
                                avg_pt = avg_pt + line_points[p + a]
                                avg_pl = avg_pl + line_plates[p + a]
                                na += 1
                        """
                        if p-1 >= 0 and p+1 < n_points:
                            #d = 0.5 * (line_points[p-1]-line_points[p]) + line_points[p]
                            #e = 0.5 * (line_points[p+1]-line_points[p]) + line_points[p]
                            #drawline(cyan, d, e, width=2)                    
                            avg_pt = 0.5 * (line_points[p] + 0.5 * (line_points[p-1] + line_points[p+1]))
                            avg_pl = V(0,0,0)
                            na = 0
                            if p in sheet:
                                avg_pl += line_plates[p-1]
                                na += 1
                            if p+1 in sheet:
                                avg_pl += line_plates[p]
                                na += 1
                            if p+2 in sheet:
                                avg_pl += line_plates[p+1]
                                na += 1
                            avg_pl *= (1.0 / na)
                            #drawline(red, line_points[p], line_points[p] + line_plates[p], width=2)
                        #avg_pt *= (1.0 / na )
                        #avg_pl *= (1.0 / na )
                    
                line_points_avg.append(avg_pt)
                line_plates_avg.append(avg_pl)
                
            line_points = line_points_avg
            line_plates = line_plates_avg

        n_points = len(line_points)
        print "n_points = ", n_points
        
        for i in range(n_points-5, n_points):
            print "i, pos : ", (i, line_points[i])
        
        p0 = line_points[n_points-2]
        p1 = line_points[n_points-3]
        p2 = line_points[n_points-1] + (p0 - p1)
        line_points.append(p2)
        line_plates.append(avg_pl)
        
        n_points = len(line_points)
        print "n_points = ", n_points
        
        for i in range(n_points-5, n_points):
            print "i, pos : ", (i, line_points[i])
        
        p0 = line_points[n_points-2]
        p1 = line_points[n_points-3]
        p2 = line_points[n_points-1] + (p0 - p1)
        line_points.append(p2)
        line_plates.append(avg_pl)
        
        n_points = len(line_points)
        print "n_points = ", n_points
        
        for i in range(n_points-5, n_points):
            print "i, pos : ", (i, line_points[i])

        last_sp = None
        last_pp = None
        last_mult = None
        last_pair = None
        n_points = len(line_points)-2
        n_sec = 1
        for p in range(1, n_points):
            if (p not in helix and p not in sheet) and \
               (p+1 in helix or p+1 in sheet):
                n_sec += 1

        tri = []
        sec = 0
        for p in range(1, n_points):
            color = gray
            mult = 0.0
            acolor = get_rainbow_color_in_range(p, n_points, 1.0, 1.0)
            if p+1 in helix:
                color = orange
                mult = 1.0
            elif p+1 in sheet:
                color = cyan
                mult = 1.0
                if p+2 not in sheet:
                    mult = 1.5                    
            
            if (p not in helix and p not in sheet) and \
               (p+1 in helix or p+1 in sheet):
                sec += 1
               
            color = get_rainbow_color_in_range(sec-1, n_sec-1, 1.0, 1.0)
            
            #color = chunk.color
            #if color is None:
            #    color = black
                
            if (p+1 not in helix and p+1 not in sheet):
                color = gray
                
            #drawline(green, line_points[p-1], line_points[p], width=3)
            #color = white
            
            ribbon_quads = []
            ribbon_normals = []
            
            for m in range (0, 16):
                t = 0.0625 * m
                sp = compute_spline(line_points, p, t)
                pp = compute_spline(line_plates, p, t)
                    
                if last_sp:
                    if m == 0:
                        lp0 = last_sp - last_mult * last_pp
                        lp1 = last_sp + last_mult * last_pp 
                        p0 = last_sp - mult * last_pp
                        p1 = last_sp + mult * last_pp 
                        drawline(color, lp0, p0, width=6)
                        drawline(color, lp1, p1, width=6)
                        lp0 = p0
                        lp1 = p1
                        p0 = sp - mult * pp
                        p1 = sp + mult * pp                     
                        #drawline(color, lp0, p0, width=6)
                        #drawline(color, lp1, p1, width=6)
                        drawcylinder(color, lp0, p0, 0.1)
                        drawcylinder(color, lp1, p1, 0.1)
                        ##drawline(color, p0, p1, width=1)
                        ##drawline(color, lp0, p1, width=1)
                        #drawline(color, lp1, p0, width=1)                    
                        drawcylinder(color, p0, p1, 0.05, 1)
                        tri.append(lp0)
                        tri.append(lp1)
                    else:
                        lp0 = last_sp - last_mult * last_pp
                        lp1 = last_sp + last_mult * last_pp 
                        p0 = sp - mult * pp
                        p1 = sp + mult * pp                     
                        #drawline(color, lp0, p0, width=6)
                        #drawline(color, lp1, p1, width=6)
                        drawcylinder(color, lp0, p0, 0.1)
                        drawcylinder(color, lp1, p1, 0.1)
                        drawcylinder(color, p0, p1, 0.05, 1)
                        ##drawline(color, p0, p1, width=1)
                        ##drawline(color, lp0, p1, width=1)
                        #drawline(color, lp1, p0, width=1)
                        tri.append(p0)
                        tri.append(p1)
                else:
                    p0 = sp - mult * pp
                    p1 = sp + mult * pp                     
                    #drawline(color, p0, p1, width=6)
                    drawcylinder(color, p0, p1, 0.1, 1)
                    tri.append(p0)
                    tri.append(p1)
                    
                    ##drawline(white, last_sp, sp, width=2)
                    
                last_sp = sp
                last_pp = pp
                last_mult = mult
                
                if p+1 in sheet and \
                   p+2 not in sheet:
                    mult -= 0.1
                                    
        drawtriangle_strip([1.0,1.0,1.0], tri, None)
        
        """
        ### backbone plates
        
        last_ca_atom = None
        last_c_atom = None
        last_o_atom = None
        
        ca = 0
        apply_material(white)
        
        for atom in chunk.atoms.itervalues():
            if hasattr(atom, "_protein_ca"):
                
                if atom._protein_ca:
                    if last_ca_atom and last_c_atom and last_o_atom:
                        pos0 = chunk.abs_to_base(last_ca_atom.posn())
                        pos1 = chunk.abs_to_base(atom.posn())
                        dpos = last_o_atom.posn() - last_c_atom.posn()
                        drawcylinder(gray, 
                                     pos0,
                                     pos0+dpos,
                                     0.05, 1)
                        drawcylinder(gray, 
                                     pos0,
                                     pos0-dpos,
                                     0.05, 1)
                        drawcylinder(gray, 
                                     pos1,
                                     pos1+dpos,
                                     0.05, 1)
                        drawcylinder(gray, 
                                     pos1,
                                     pos1-dpos,
                                     0.05, 1)
                        drawcylinder(gray, 
                                     pos0+dpos,
                                     pos1+dpos,
                                     0.05, 1)
                        drawcylinder(gray, 
                                     pos0-dpos,
                                     pos1-dpos,
                                     0.05, 1)
                        glColor3f(1,1,1)
                        glBegin(GL_QUADS)
                        glVertex3fv(pos0-dpos)
                        glVertex3fv(pos0+dpos)
                        glVertex3fv(pos1+dpos)
                        glVertex3fv(pos1-dpos)
                        glEnd()
                        pass
                                        
                    last_ca_atom = atom

                if atom._protein_c:
                    last_c_atom = atom
                    
                if atom._protein_o:
                    last_o_atom = atom
                    
        """
        
        """
        gleSetJoinStyle(TUBE_JN_ANGLE | TUBE_NORM_PATH_EDGE | TUBE_JN_CAP | TUBE_CONTOUR_CLOSED) 
        last_atom = None
        ca = 0
        for atom in chunk.atoms.itervalues():
            if hasattr(atom, "_protein_ca"):
                if atom._protein_ca:
                    
                    color = V(gray) ###V(AA_COLORS_HYDROPATHY[atom._protein_res_name])
                    ###V(gray) #V(get_rainbow_color_in_range(ca, n_ca, 0.75, 1.0))
                    if len(points) == 0:
                        drawsphere(gray, chunk.abs_to_base(atom.posn()), 0.5, 2)
                        points.append(chunk.abs_to_base(atom.posn()))
                        colors.append(color)
                        #radii.append(atom._protein_temp_factor[0]*0.1 + 0.5)
                        radii.append(0.5)
                    points.append(chunk.abs_to_base(atom.posn()))
                    colors.append(color)
                    #radii.append(atom._protein_temp_factor[0]*0.5 + 0.5)
                    radii.append(0.5)
                    last_atom = atom
                    ca += 1
                    
                if atom._protein_cb:
                    pos1 = chunk.abs_to_base(last_atom.posn())
                    pos2 = chunk.abs_to_base(atom.posn())
                    pos3 = pos1 + 2.0*norm(pos2-pos1)
                    drawsphere(AA_COLORS_HYDROPATHY[atom._protein_res_name], pos3, 0.75, 2)
                    drawcylinder(gray, pos1, pos3, 0.33, 0)
        
        drawsphere(gray, chunk.abs_to_base(last_atom.posn()), 0.5, 2)
        points.append(chunk.abs_to_base(last_atom.posn()))
        colors.append(color)
        #radii.append(last_atom._protein_temp_factor[0]*0.5 + 0.5)
        radii.append(0.5)
        
        points, colors, radii = make_tube(points, colors, radii)
        
        drawpolycone_multicolor([0,0,0,-2], points, colors, radii)
        pass
    
        """
        """
        ca = 0
        prev_atom = None
        #glLineWidth(10.0)
        #glDisable(GL_LIGHTING)
        #glBegin(GL_LINES)
        for atom in chunk.atoms.itervalues():
            if hasattr(atom, "_protein_ca"):
                if atom._protein_ca:
                    #color = self._get_nice_rainbow_color_in_range(ca, n_ca, 1.0, 1.0)
                    color = red
                    #print atom._protein_resname                            
                    #color = aa_colors[atom._protein_resname]
                    #print color
                    drawsphere(color, 
                               chunk.abs_to_base(atom.posn()), 
                               1.0, 
                               2)
                    
                    if prev_atom:
                        #glColor3fv(color)
                        #glVertex3fv(chunk.abs_to_base(prev_atom.posn()))
                        #glVertex3fv(chunk.abs_to_base(atom.posn()))
                        #lines = [chunk.abs_to_base(prev_atom.posn()), chunk.abs_to_base(atom.posn())]
                        #drawlinelist(color,lines)
                        drawcylinder(gray,
                               chunk.abs_to_base(prev_atom.posn()), 
                               chunk.abs_to_base(atom.posn()), 
                               0.5, 0, 1.0)      
                    ca += 1
                    prev_atom = atom
        #glEnd()
        #glLineWidth(1.0)
        #glEnable(GL_LIGHTING)
        """
        
    pass


class DnaCylinderChunks(ChunkDisplayMode):

    def drawchunk(self, glpane, chunk, memo, highlighted):
        return

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
        return
        
    def writepov(self, chunk, memo, file):
        """
        Renders the chunk to a POV-Ray file.
        """
        return
    
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

        if chunk is None:
            return None
        
        structure = []
        
        proteinDisplayStyle = 0
        proteinColors = 0
        proteinAuxColors = 0
        proteinCustomColor = 0
        proteinAuxCustomColor = 0
        
        helix = []
        sheet = []
        
        if hasattr(chunk, "_protein_helix"):
            helix = chunk._protein_helix
            
        if hasattr(chunk, "_protein_sheet"):
            sheet = chunk._protein_sheet        
        
        # Extract secondary structure elements
        # Every element is a list of consecutive, non-broken C-alpha atoms
        # in the same secondary structure conformation.
        last_ss = 0 
        anum = 0
        sec = []
        for atom in chunk.atoms.itervalues():
            if hasattr(atom, "_protein_ca"):
                if atom._protein_ca:
                    ss = 0
                    if anum+1 in helix:
                        ss = 1
                    if anum+1 in sheet:
                        ss = 2
                    if ss != last_ss:
                        if len(sec)>0:
                            structure.append(sec)
                        sec = []
                    
                    sec.append(atom)                    
                    
                    """
                    if last_ca_atom and last_c_atom and last_o_atom:
                        pos0 = chunk.abs_to_base(last_ca_atom.posn())
                        pos1 = chunk.abs_to_base(atom.posn())
                        dpos = last_o_atom.posn() - last_c_atom.posn()
                        if last_dpos:
                            n0 = norm(last_dpos)
                            n1 = norm(dpos)
                            d = dot(n0, n1)
                            #print "d = ", d
                            if dot(n0, n1) < 0.0:
                                #print "invert ", dpos
                                dpos = -1.0 * dpos
                                #print " = ", dpos
                        line_points.append(pos0)
                        line_plates.append(dpos)
                        last_dpos = dpos
                        #color = get_rainbow_color_in_range(ca, n_ca, 1.0, 1.0)
                        #for i in range(0, 10):
                        #    di = 0.2 * i - 1.0
                        #    p0 = pos0 + di * dpos
                        #    p1 = pos1 + di * dpos
                        #    points
                        #    drawline(color, p0, p1, width=2)
                        pass
                    
                    ca += 1           
                    last_ca_atom = atom

                if atom._protein_c:
                    last_c_atom = atom
                    
                if atom._protein_o:
                    last_o_atom = atom
                """
                    
        print "structure = ", structure
        
        return (structure)
