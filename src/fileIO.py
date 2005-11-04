# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
"""

#bruce 050414 comment: surely most of these imports are no longer needed;
# but this is hard to know for sure, since both MWsemantics and GLPane
# say "from fileIO import *", thereby picking up everything we import
# below, including all symbols from 7 modules!
# When the remaining file formats are split out, they should copy only
# the ones they need, and not as "import *". Then the only code left
# in this module will be these imports -- perhaps still in use, as
# explained above.

from Numeric import *
from VQT import *
from string import * # this might no longer be needed [bruce 050414 comment]
import re
from chem import * # needed for atom, bond_atoms, maybe not anything else [bruce 050414 guess]
from jigs import *
from Utility import *
from povheader import povheader, povpoint
from mdldata import *
from HistoryWidget import redmsg
from elements import PeriodicTable

# ==

# Create a POV-Ray file
def writepovfile(part, glpane, filename): #bruce 050927 replaced assy argument with part and glpane args, added docstring
    "write the given part into a new POV-Ray file with the given name, using glpane and glpane.mode for lightig, color, etc"
    f = open(filename,"w")
    ## bruce 050325 removed this (no effect except on assy.alist which is bad now)
    ## atnums = {}
    ## atnums['NUM'] = 0
    ## assy.alist = [] 

    # POV-Ray images now look correct when Projection = ORTHOGRAPHIC.  Mark 051104.
    if glpane.ortho == PERSPECTIVE:
        cdist = 6.0 # Camera distance
    else: # ORTHOGRAPHIC
        cdist = 1600.0
    
    aspect = (glpane.width + 0.0)/(glpane.height + 0.0)
    zfactor =  0.4 # zoom factor 
    up = V(0.0, zfactor, 0.0)
    right = V( aspect * zfactor, 0.0, 0.0) ##1.33  
    import math
    angle = 2.0*atan2(aspect, cdist)*180.0/math.pi
    
    f.write("// Recommended window size: width=%d, height=%d \n\n"%(glpane.width, glpane.height))

    f.write(povheader)
    
    # Light sources.
    # These are currently hardcoded here and independent of the 3 light sources in the CAD
    # code.  This needs to be fixed (see bug 447).  Mark 051104.
    light1 = (glpane.out + glpane.left + glpane.up) * 10.0
    light2 = (glpane.right + glpane.up) * 10.0
    light3 = glpane.right + glpane.down + glpane.out/2.0
    f.write("\nlight_source {\n  " + povpoint(light1) + "\n  color Gray10 parallel\n}\n")
    f.write("\nlight_source {\n  " + povpoint(light2) + "\n  color Gray40 parallel\n}\n")
    f.write("\nlight_source {\n  " + povpoint(light3) + "\n  color Gray40 parallel\n}\n")
    
    # Camera info
    vdist = cdist
    if aspect < 1.0:
            vdist = cdist / aspect
    eyePos = vdist * glpane.scale*glpane.out-glpane.pov
    
    f.write("\ncamera {\n  location " + povpoint(eyePos)  +
            "\n  up " + povpoint(up) +
            "\n  right " + povpoint(right) +
            "\n  sky " + povpoint(glpane.up) +
            "\n angle " + str(angle) +
            "\n  look_at " + povpoint(-glpane.pov) + "\n}\n\n")

    # Background color. The SkyBlue gradient is supported, but only works correctly when in "Front View".
    # This is a work in progress (and this implementation is better than nothing).  See bug 888 for more info.
    # Mark 051104.
    if glpane.mode.backgroundGradient: # SkyBlue.  
        f.write("sky_sphere {\n" +
        "    pigment {\n" +
        "      gradient y\n" +
        "      color_map {\n" +
        "        [(1-cos(radians(" + str(90-angle/2) + ")))/2 color Gray10]\n" +
        "        [(1-cos(radians(" + str(90+angle/2) + ")))/2 color SkyBlue]\n" +
        "      }\n" +
        "      scale 2\n" +
        "      translate -1\n" +
        "    }\n" +
        "  }\n")
    else: # Solid
        f.write("background {\n  color rgb " + povpoint(glpane.mode.backgroundColor*V(1,1,-1)) + "\n}\n")
 
    # write a union object, which encloses all following objects, so it's 
    # easier to set a global modifier like "Clipped_by" for all objects
    # Huaicai 1/6/05
    f.write("\nunion {\t\n") ##Head of the union object
 
    # Write atoms and bonds in the part
    part.topnode.writepov(f, glpane.display)
        #bruce 050421 changed assy.tree to assy.part.topnode to fix an assy/part bug
        #bruce 050927 changed assy.part -> new part arg
    
    farPos = -cdist*glpane.scale*glpane.out*glpane.far + eyePos
    nearPos = -cdist*glpane.scale*glpane.out*glpane.near + eyePos
    
    pov_out = (glpane.out[0], glpane.out[1], -glpane.out[2])
    pov_far =  (farPos[0], farPos[1], -farPos[2])
    pov_near =  (nearPos[0], nearPos[1], -nearPos[2])
    pov_in = (-glpane.out[0], -glpane.out[1], glpane.out[2])
    
    ### sets the near and far clipping plane
    ## removed 050817 josh -- caused crud to appear in the output (and slowed rendering 5x!!)
    ## f.write("clipped_by { plane { " + povpoint(-glpane.out) + ", " + str(dot(pov_in, pov_far)) + " }\n")
    ## f.write("             plane { " + povpoint(glpane.out) + ", " + str(dot(pov_out, pov_near)) + " } }\n")
    f.write("}\n\n")  

    f.close()
    
# ==

# Create an MDL file - by Chris Phoenix and Mark for John Burch [04-12-03]
def writemdlfile(part, glpane, filename): #bruce 050927 replaced assy argument with part and glpane args, added docstring
    "write the given part into a new MDL file with the given name, using glpane.display"
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
    part.topnode.writemdl(alist, f, glpane.display)
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