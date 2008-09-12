# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
fileIO.py -- reading and writing miscellaneous file formats
[see also files_mmp.py and files_pdb.py for those specific formats]

$Id$

History: bruce 050414 split out most of this module's code
into separate modules for each file format,
except for the ones that remain. These too might soon be
in format-specific modules, leaving this one empty until
it (or a new module?) acquires the higher-level file I/O
functionality from MWsemantics.py.

TODO: This should be split into files_mdl and files_povray
(using svn move to preserve the history on the povray part),
since it now only supports those two formats. [bruce 072009]
"""

import math

import foundation.env as env
from geometry.VQT import V, Q, A, vlen
from graphics.rendering.povray.povheader import povheader, povpoint
from graphics.rendering.mdl.mdldata import mdlheader
from graphics.rendering.mdl.mdldata import mdlfooter

from utilities.constants import diINVISIBLE
from utilities.prefs_constants import PERSPECTIVE
from utilities.prefs_constants import material_specular_highlights_prefs_key
from utilities.prefs_constants import material_specular_finish_prefs_key

# ==

# Create a POV-Ray file
def writepovfile(part, glpane, filename):
    """
    write the given part into a new POV-Ray file with the given name,
    using glpane for lighting, color, etc
    """
    f = open(filename,"w")

    # POV-Ray images now look correct when Projection = ORTHOGRAPHIC.  Mark 051104.
    if glpane.ortho == PERSPECTIVE:
        cdist = 6.0 # Camera distance [see also glpane.cdist]
    else: # ORTHOGRAPHIC
        cdist = 1600.0
    
    aspect = (glpane.width + 0.0)/(glpane.height + 0.0)
    zfactor =  0.4 # zoom factor 
    up = V(0.0, zfactor, 0.0)
    right = V( aspect * zfactor, 0.0, 0.0) ##1.33
    angle = 2.0*math.atan2(aspect, cdist)*180.0/math.pi
    
    f.write("// Recommended window size: width=%d, height=%d \n"%(glpane.width, glpane.height))
    f.write("// Suggested command line switches: +A +W%d +H%d\n\n"%(glpane.width, glpane.height))

    f.write(povheader)
    
    # Camera info
    vdist = cdist
    if aspect < 1.0:
            vdist = cdist / aspect
    eyePos = vdist * glpane.scale*glpane.out-glpane.pov
        # note: this is probably the same as glpane.eyeball(),
        # in perspective view, except for the aspect < 1.0 correction.
        # See comments in def eyeball about whether that correction
        # is needed there as well. [bruce 080912 comment]
    
    f.write("#declare cameraPosition = "+ povpoint(eyePos)  + ";\n" +
            "\ncamera {\n  location cameraPosition"  +
            "\n  up " + povpoint(up) +
            "\n  right " + povpoint(right) +
            "\n  sky " + povpoint(glpane.up) +
            "\n angle " + str(angle) +
            "\n  look_at " + povpoint(-glpane.pov) + "\n}\n\n")

    # Background color. The SkyBlue gradient is supported, but only works correctly when in "Front View".
    # This is a work in progress (and this implementation is better than nothing).  See bug 888 for more info.
    # Mark 051104.
    if glpane.backgroundGradient: # SkyBlue.
        dt = Q(glpane.quat)
        if not vlen(V(dt.x, dt.y, dt.z)):
            # This addresses a problem in POV-Ray when dt=0,0,0 for Axis_Rotate_Trans. mark 051111.
            dt.x = .00001  
        degY = dt.angle*180.0/math.pi
        f.write("sky_sphere {\n" +
        "    pigment {\n" +
        "      gradient y\n" +
        "      color_map {\n" +
        "        [(1-cos(radians(" + str(90-angle/2) + ")))/2 color SkyWhite]\n" +
        "        [(1-cos(radians(" + str(90+angle/2) + ")))/2 color SkyBlue]\n" +
        "      }\n" +
        "      scale 2\n" +
        "      translate -1\n" +
        "    }\n" +
        '    #include "transforms.inc"\n' +
        "    Axis_Rotate_Trans(" + povpoint(V(dt.x, dt.y, dt.z)) + ", " + str(degY) + ")\n" +
        "  }\n")
    else: # Solid
        f.write("background {\n  color rgb " + povpoint(glpane.backgroundColor*V(1,1,-1)) + "\n}\n")
    
    # Lights and Atomic finish.
    _writepovlighting(f, glpane)
 
    # write a union object, which encloses all following objects, so it's 
    # easier to set a global modifier like "Clipped_by" for all objects
    # Huaicai 1/6/05
    f.write("\nunion {\t\n") # Head of the union object
 
    # Write atoms and bonds in the part
    part.writepov(f, glpane.displayMode)
        #bruce 050421 changed assy.tree to assy.part.topnode to fix an assy/part bug
        #bruce 050927 changed assy.part -> new part arg
        #bruce 070928 call part.writepov instead of directly calling part.topnode.writepov,
        # so the part can prevent external bonds from being drawn twice.

    # set the near and far clipping plane
    # removed 050817 josh -- caused crud to appear in the output (and slowed rendering 5x!!)

    ## farPos = -cdist*glpane.scale*glpane.out*glpane.far + eyePos
    ## nearPos = -cdist*glpane.scale*glpane.out*glpane.near + eyePos
    
    ## pov_out = (glpane.out[0], glpane.out[1], -glpane.out[2])
    ## pov_far =  (farPos[0], farPos[1], -farPos[2])
    ## pov_near =  (nearPos[0], nearPos[1], -nearPos[2])
    ## pov_in = (-glpane.out[0], -glpane.out[1], glpane.out[2])
    
    ## f.write("clipped_by { plane { " + povpoint(-glpane.out) + ", " + str(dot(pov_in, pov_far)) + " }\n")
    ## f.write("             plane { " + povpoint(glpane.out) + ", " + str(dot(pov_out, pov_near)) + " } }\n")

# [and what was this for? bruce question 071009]
##    if glpane.currentCommand.commandName == 'DEPOSIT':
##        dt = -glpane.quat
##        degY = dt.angle*180.0/pi
##        f.write("plane { \n" +
##                "      z 0\n" +
##                "      pigment { color rgbf <0.29, 0.7294, 0.8863, 0.6>}\n" +
##                '    #include "transforms.inc"\n' +
##                "    Axis_Rotate_Trans(" + povpoint(V(dt.x, dt.y, dt.z)) + ", " + str(degY) + ")}\n")
       
    f.write("}\n\n")  

    f.close()

    return # from writepovfile

# _writepovlighting() added by Mark.  Feel free to ask him if you have questions.  051130.    
def _writepovlighting(f, glpane):
    """
    Writes a light source record for each light (if enabled) and the
    'Atomic' finish record. These records impact the lighting affect.
    """ 
    # Get the lighting parameters for the 3 lights.
    (((r0,g0,b0),a0,d0,s0,x0,y0,z0,e0), \
    ( (r1,g1,b1),a1,d1,s1,x1,y1,z1,e1), \
    ( (r2,g2,b2),a2,d2,s2,x2,y2,z2,e2)) = glpane.getLighting()

    # For now, we copy the coords of each light here.
    pos0 = (glpane.right * x0) + (glpane.up *y0) + (glpane.out * z0)
    pos1 = (glpane.right * x1) + (glpane.up * y1) + (glpane.out * z1)
    pos2 = (glpane.right * x2) + (glpane.up * y2) + (glpane.out * z2)

     # The ambient values of only the enabled lights are summed up. 
    # 'ambient' is used in the 'Atomic' finish record. It can have a value
    # over 1.0 (and makes a difference).
    ambient = 0.25 # Add 0.25; matches better with NE1 default lighting.
    
    # The diffuse values of only the enabled lights are summed up. 
    # 'diffuse' is used in the 'Atomic' finish record. It can have a value
    # over 1.0 (and makes a difference).
    diffuse = 0.0
    
    f.write( "\n// Light #0 (Camera Light)" +
                "\nlight_source {" +
                "\n  cameraPosition" + 
                "\n  color <0.3, 0.3, 0.3>" +
                "\n  parallel" +
                "\n  point_at <0.0, 0.0, 0.0>" +
                "\n}\n")
    
    if e0: # Light 1 is On
        ambient += a0
        diffuse += d0
        f.write( "\n// Light #1" +
                    "\nlight_source {" +
                    "\n  " + povpoint(pos0) + 
                    "\n  color <" + str(r0*d0) + ", " + str(g0*d0) + ", " + str(b0*d0) + ">" +
                    "\n  parallel" +
                    "\n  point_at <0.0, 0.0, 0.0>" +
                    "\n}\n")
    
    if e1: # Light 2 is On
        ambient += a1
        diffuse += d1
        f.write( "\n// Light #2" +
                    "\nlight_source {\n  " + povpoint(pos1) + 
                    "\n  color <" + str(r1*d1) + ", " + str(g1*d1) + ", " + str(b1*d1) + ">" +
                    "\n  parallel" +
                    "\n  point_at <0.0, 0.0, 0.0>" +
                    "\n}\n")
    
    if e2: # Light 3 is On
        ambient += a2
        diffuse += d2
        f.write("\n// Light #3" +
                    "\nlight_source {\n  " + povpoint(pos2) + 
                    "\n  color <" + str(r2*d2) + ", " + str(g2*d2) + ", " + str(b2*d2) + ">" +
                    "\n  parallel" +
                    "\n  point_at <0.0, 0.0, 0.0>" +
                    "\n}\n")
    
    # Atomic finish record.
    #
    # phong determines the brightness of the highlight, while phong_size determines its size.
    #
    # phong: 0.0 (no highlight) to 1.0 (saturated highlight)
    # 
    # phong_size: 1 (very dull) to 250 (highly polished) 
    # The larger the phong size the tighter, or smaller, the highlight and 
    # the shinier the appearance. The smaller the phong size the looser, 
    # or larger, the highlight and the less glossy the appearance.
    #
    # Good values:
    # brushed metal: phong .25, phong_size 12
    # plastic: .7, phong_size 17
    #
    # so phong ranges from .25 - .7
    # and phong_size ranges from 12-17
    #
    if env.prefs[material_specular_highlights_prefs_key]:
        # whiteness: 0.0-1.0, where 0 = metal and 1 = plastic
        phong = 0.25 + (env.prefs[material_specular_finish_prefs_key] *  0.45) #  .25-.7
        phong_size = 12.0 + (env.prefs[material_specular_finish_prefs_key] * 5.0) # 12-17
    else:
        phong = 0.0 # No specular highlights
        phong_size = 0.0

    f.write( "\n#declare Atomic =" +
                "\nfinish {" +
                "\n    ambient 0.1" + # str(ambient) + # Mark 060929
                "\n    diffuse " + str(diffuse) +
                "\n    phong " + str(phong) +
                "\n    phong_size " + str(phong_size) +
                "\n}\n")
    
    return # from _writepovlighting

# ==

# Create an MDL file - by Chris Phoenix and Mark for John Burch [04-12-03]
# ninad060802 has disabled the File > Save As option to save the MDL file. (see bug 1508. Also, since in Alpha9 we will support OpenBabel, there will be a confusion between this MDL file format and the one that OpenBabel includes extension. If we support this filetype in future, its description field should be changed. 
def writemdlfile(part, glpane, filename): #bruce 050927 replaced assy argument with part and glpane args, added docstring
    "write the given part into a new MDL file with the given name, using glpane.displayMode"
    alist = [] #bruce 050325 changed assy.alist to localvar alist
    natoms = 0
    # Specular values keyed by atom color 
    # Only Carbon, Hydrogen and Silicon supported here
    specValues = {(117,117,117):((183, 183, 183), 16, 44), \
                       (256,256,256):((183, 183, 183), 15, 44), \
                       (111,93,133):((187,176,200), 16, 44)}

    # Determine the number of visible atoms in the part.
    # Invisible atoms are drawn.  Hidden atoms are not drawn.
    # This is a bug to be fixed in the future.  Will require work in chunk/chem.writemdl, too.  
    # writepov may have this problem, too.
    # Mark [04-12-05]     
    # To test this, we need to get a copy of Animation Master.
    # Mark [05-01-14]
    for mol in part.molecules: 
        if (not mol.hidden) and (mol.display != diINVISIBLE): natoms += len(mol.atoms) #bruce 050421 disp->display (bugfix?)
#    print "fileIO: natoms =", natoms

    f = open(filename, 'w');
    
    # Write the header
    f.write(mdlheader)
    
    # Write atoms with spline coordinates
    f.write("Splines=%d\n"%(13*natoms))
    part.topnode.writemdl(alist, f, glpane.displayMode)
        #bruce 050421 changed assy.tree to assy.part.topnode to fix an assy/part bug
        #bruce 050927 changed assy.part -> new part arg
    
    # Write the GROUP information
    # Currently, each atom is 
    f.write("[ENDMESH]\n[GROUPS]\n")
    
    atomindex = 0 
    
    for mol in part.molecules:
        col = mol.color # Color of molecule
        for a in mol.atoms.values():
            
            # Begin GROUP record for this atom.
            f.write("[GROUP]\nName=Atom%d\nCount=80\n"%atomindex)
            
            # Write atom mesh IDs
            for j in range(80):
                f.write("%d\n"%(98-j+atomindex*80))

            # Write Pivot record for this atom.
#            print "a.pos = ", a.posn()
            xyz=a.posn()
            n=(float(xyz[0]), float(xyz[1]), float(xyz[2]))
            f.write("Pivot= %f %f %f\n" % n)
            
            # Add DiffuseColor record for this atom.
            color = col or a.element.color
                # if this was color = a.drawing_color() it would mess up the specularity lookup below;
                # could be fixed somehow... [bruce 070417 comment]
            rgb=map(int,A(color)*255) # rgb = 3-tuple of int
            color=(int(rgb[0]), int(rgb[1]), int(rgb[2]))
            f.write("DiffuseColor=%d %d %d\n"%color)

            # Added specularity per John Burch's request
            # Specular values keyed by atom color           
            (specColor, specSize, specIntensity) = \
             specValues.get(color, ((183,183,183),16,44))
            f.write("SpecularColor=%d %d %d\n"%specColor)
            f.write("SpecularSize=%d\n"%specSize)
            f.write("SpecularIntensity=%d\n"%specIntensity)
            
            # End the group for this atom.
            f.write("[ENDGROUP]\n")
            
            atomindex += 1
        
    # ENDGROUPS
    f.write("[ENDGROUPS]\n")

    # Write the footer and close
    fpos = f.tell()
    f.write(mdlfooter)
    f.write("FileInfoPos=%d\n"%fpos)
    f.close()

# end
