# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
writemdlfile.py -- write a Part into an MDL (Animation Master Model) file
(available from NE1's File -> Export menu)

@author: Chris Phoenix and Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 080917 split this out of graphics/rendering/fileIO.py.
For earlier history see that file's repository log.
"""

import math

from geometry.VQT import A
from graphics.rendering.mdl.mdldata import mdlheader
from graphics.rendering.mdl.mdldata import mdlfooter

from utilities.constants import diINVISIBLE

# ==

# Create an MDL file - by Chris Phoenix and Mark for John Burch [04-12-03]
# ninad060802 has disabled the File > Save As option to save the MDL file. (see bug 1508. Also, since in Alpha9 we will support OpenBabel, there will be a confusion between this MDL file format and the one that OpenBabel includes extension. If we support this filetype in future, its description field should be changed. 
def writemdlfile(part, glpane, filename): #bruce 050927 replaced assy argument with part and glpane args, added docstring
    """
    write the given part into a new MDL file with the given name,
    using glpane.displayMode
    """
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

    return

# end
