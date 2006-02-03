# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
jigs_measurements.py -- Classes for measurement jigs.

$Id$

History: 

051104 wware - three measurement jigs (distance, angle, dihedral)
written over the last few days. No simulator support yet, but they
work fine in the CAD system, and the MMP file records should be
acceptable when the time comes for sim support.

"""

from VQT import *
from shape import *
from chem import *
from Utility import *
from HistoryWidget import redmsg, greenmsg
from povheader import povpoint #bruce 050413
from debug import print_compact_stack, print_compact_traceback
import env #bruce 050901
from jigs import Jig

# == Measurement Jigs

# rename class for clarity, remove spurious methods, wware 051103
class MeasurementJig(Jig):
    "superclass for Measurement jigs"
    # constructor moved to base class, wware 051103
    def __init__(self, assy, atomlist):
        Jig.__init__(self, assy, atomlist)        
        self.font_name = "Helvetica"
        self.font_size = 10.0 # pt size
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.
        self.cancelled = True # We will assume the user will cancel

    # move some things to base class, wware 051103
    copyable_attrs = Jig.copyable_attrs + ('font_name', 'font_size')

    # move to base class, wware 051103
    def rematom(self, atm):
        "Delete the jig if any of its atoms are deleted"
        Node.kill(self)
        
    # Set the properties for a Measure Distance jig read from a (MMP) file
    # include atomlist, wware 051103
    def setProps(self, name, color, font_name, font_size, atomlist):
        self.name = name
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.setAtoms(atomlist)

    # simplified, wware 051103
    # Following Postscript: font names NEVER have parentheses in them.
    # So we can use parentheses to delimit them.
    def mmp_record_jigspecific_midpart(self):
        return " (%s) %d" % (self.font_name, self.font_size)
        
    # unify text-drawing to base class, wware 051103
    def _drawtext(self, text):
        # use atom positions to compute center, where text should go
        pos1 = self.atoms[0].posn()
        pos2 = self.atoms[-1].posn()
        drawtext(text, self.color, (pos1 + pos2) / 2, self.font_size, self.assy.o)
    
    # move into base class, wware 051103
    def set_cntl(self):
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

    # move into base class, wware 051103
    def writepov(self, file, dispdef):
        sys.stderr.write(self.__class__.__name__ + ".writepov() not implemented yet")
    
    def will_copy_if_selected(self, sel):
        "copy only if all my atoms are selected [overrides Jig.will_copy_if_selected]"
        if not self.needs_atoms_to_survive():
            return True
        # for measurement jigs, copy only if all atoms selected, wware 051107
        for atom in self.atoms:
            if not sel.picks_atom(atom):
                msg = "Can't copy a measurement jig unless all its atoms are selected"
                env.history.message(orangemsg(msg))
                return False #e need to give a reason why not??
        return True

    pass # end of class MeasurementJig


# == Measure Distance

class MeasureDistance(MeasurementJig):
    '''A Measure Distance jig has two atoms and draws a line with a distance label between them.
    '''
    
    sym = "Distance"
    icon_names = ["measuredistance.png", "measuredistance-hide.png"]
    featurename = "Measure Distance Jig" # added, wware 20051202

    def _getinfo(self): 
        return  "[Object: Measure Distance] [Name: " + str(self.name) + "] " + \
                    "[Nuclei Distance = " + str(self.get_nuclei_distance()) + " ]" + \
                    "[VdW Distance = " + str(self.get_vdw_distance()) + " ]"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mdistance += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_nuclei_distance(self):
        '''Returns the distance between two atoms (nuclei)'''
        return vlen (self.atoms[0].posn()-self.atoms[1].posn())
        
    def get_vdw_distance(self):
        '''Returns the VdW distance between two atoms'''
        return self.get_nuclei_distance() - self.atoms[0].element.rvdw - self.atoms[1].element.rvdw
        
    # Measure Distance jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, glpane, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the VdW and nuclei distances (e.g. 1.4/3.5) is included.
        '''
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        self._drawtext("%.2f/%.2f" % (self.get_vdw_distance(), self.get_nuclei_distance()))

    mmp_record_name = "mdistance"
    
    pass # end of class MeasureDistance
        
# == Measure Angle

class MeasureAngle(MeasurementJig):
    # new class.  wware 051031
    '''A Measure Angle jig has three atoms.'''
    
    sym = "Angle"
    icon_names = ["measureangle.png", "measureangle-hide.png"]
    featurename = "Measure Angle Jig" # added, wware 20051202

    def _getinfo(self):   # add atom list, wware 051101
        return  "[Object: Measure Angle] [Name: " + str(self.name) + "] " + \
                    ("[Atoms = %s %s %s]" % (self.atoms[0], self.atoms[1], self.atoms[2])) + \
                    "[Angle = " + str(self.get_angle()) + " ]"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mangle += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_angle(self):
        '''Returns the angle between two atoms (nuclei)'''
        v01 = self.atoms[0].posn()-self.atoms[1].posn()
        v21 = self.atoms[2].posn()-self.atoms[1].posn()
        return angleBetween(v01, v21)
        
    # Measure Angle jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, glpane, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the angle is included.
        '''
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        drawline(self.color, self.atoms[1].posn(), self.atoms[2].posn())
        self._drawtext("%.2f" % self.get_angle())
    
    mmp_record_name = "mangle"
    
    pass # end of class MeasureAngle
        
# == Measure Dihedral

class MeasureDihedral(MeasurementJig):
    # new class.  wware 051031
    '''A Measure Dihedral jig has four atoms.'''
    
    sym = "Dihedral"
    icon_names = ["measuredihedral.png", "measuredihedral-hide.png"]
    featurename = "Measure Dihedral Jig" # added, wware 20051202

    def _getinfo(self):    # add atom list, wware 051101
        return  "[Object: Measure Dihedral] [Name: " + str(self.name) + "] " + \
                    ("[Atoms = %s %s %s %s]" % (self.atoms[0], self.atoms[1], self.atoms[2], self.atoms[3])) + \
                    "[Dihedral = " + str(self.get_dihedral()) + " ]"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mdihedral += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_dihedral(self):
        '''Returns the dihedral between two atoms (nuclei)'''
        wx = self.atoms[0].posn()-self.atoms[1].posn()
        yx = self.atoms[2].posn()-self.atoms[1].posn()
        xy = -yx
        zy = self.atoms[3].posn()-self.atoms[2].posn()
        u = cross(wx, yx)
        v = cross(xy, zy)
        if dot(zy, u) < 0:   # angles go from -180 to 180, wware 051101
            return -angleBetween(u, v)  # use new acos(dot) func, wware 051103
        else:
            return angleBetween(u, v)
        
    # Measure Dihedral jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, glpane, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the dihedral is included.
        '''
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        drawline(self.color, self.atoms[1].posn(), self.atoms[2].posn())
        drawline(self.color, self.atoms[2].posn(), self.atoms[3].posn())
        self._drawtext("%.2f" % self.get_dihedral())
    
    mmp_record_name = "mdihedral"
    
    pass # end of class MeasureDihedral
        
# end of module jigs_measurements.py
