# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
jigs_measurements.py -- Classes for measurement jigs.

$Id$

History: 

051017. Copied from jigs_motors. Mark

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

class Measurement(Jig):
    "superclass for Measurement jigs"
    def __init__(self, assy, atomlist):
        Jig.__init__(self, assy, atomlist)
        
        self.quat = Q(1, 0, 0, 0)

    # for a measurement jig read from a file which includes the following "shaft" record
    def setShaft(self, shaft):
        self.setAtoms(shaft)
        self._initial_posns = None #needed in RotaryMotor, harmless in others
    
    # for a measurement jig created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shaft, los):
        self.setAtoms(shaft) #bruce 041105 code cleanup
        self.recompute_center_axis(los)
        self.edit()
        
        ##@@@--Huaicai
        self.atomPos = []
        for a in shaft:
            self.atomPos += [a.posn()]
            

    def recompute_center_axis(self, los = None):
        if los is None:
            los = self.assy.o.lineOfSight
        shaft = self.atoms
        # remaining code is a kluge, according to the comment above findcenter;
        # note that it depends on order of atoms, presumably initially derived
        # from the selatoms dict and thus arbitrary (not even related to order
        # in which user selected them or created them). [bruce 050518 comment]
        pos=A(map((lambda a: a.posn()), shaft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shaft) == 1:
            self.axis = norm(los)
        elif len(shaft) == 2:
            self.axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))
        self._initial_posns = None #bruce 050518; needed in RotaryMotor, harmless in others
        return

    def move(self, offset):
        self.center += offset
    
    def rot(self, q):
        self.quat += q
        
    def posn(self):
        return self.center

    def getaxis(self):
        return self.axis

    def axen(self):
        return self.axis

    # Set the properties for a Measure Distance jig read from a (MMP) file
    def setProps(self, name, color, font_type, font_size, center):
        self.name = name
        self.color = color
        self.font_type = font_type
        self.font_size = font_size
        self.center = center  # oops, one prop too many, wware 051101
        self._initial_posns = None # Not sure if this is needed.  Mark
   
# Not sure if this is needed.  Ask Bruce.  Mark 051017
    def rematom(self, *args, **opts):
        self._initial_posns = None 
        super = Jig
        return super.rematom(self, *args, **opts)

    # NOT SURE IF THIS IS NEEDED.  TALK TO BRUCE. MARK
    # This looks like something all measuring jigs would probably share, move it to the base class. wware 051031
    def norm_project_posns(self, posns):
        """[Private helper for getrotation]
        Given a Numeric array of position vectors relative to self.center,
        project them along self.axis and normalize them (and return that --
        but we take ownership of posns passed to us, so we might or might not
        modify it and might or might not return the same (modified) object.
        """
        axis = self.axis
        dots = dot(posns, axis)
        ## axis_times_dots = axis * dots #  guess from this line: exceptions.ValueError: frames are not aligned
        axis_times_dots = A(len(dots) * [axis]) * reshape(dots,(len(dots),1)) #k would it be ok to just use axis * ... instead?
        posns -= axis_times_dots
        ##posns = norm(posns) # some exception from this
        posns = A(map(norm, posns))
            # assumes no posns are right on the axis! now we think they are on a unit circle perp to the axis...
        # posns are now projected to a plane perp to axis and centered on self.center, and turned into unit-length vectors.
        return posns # (note: in this implem, we did modify the mutable argument posns, but are returning a different object anyway.)

    def mmp_record_jigspecific_midpart(self):
        xyz = self.posn() * 1000
        dataline = "\"%s\" %d (%d, %d, %d)" % \
           (self.font_type, self.font_size,
            int(xyz[0]), int(xyz[1]), int(xyz[2]))

        return " " + dataline + "\n" + "shaft"
        
    pass # end of class Measurement


# == Measure Distance

class MeasureDistance(Measurement):
    '''A Measure Distance jig has two atoms and draws a line with a distance label between them.
    '''
    
    sym = "Distance"
    icon_names = ["measuredistance.png", "measuredistance-hide.png"]

    copyable_attrs = Jig.copyable_attrs + ('font_type', 'font_size', 'center', 'axis')

    # create a blank Measure Distance jig not connected to anything    
    def __init__(self, assy, atomlist): 
        Measurement.__init__(self, assy, atomlist)
        self.font_type = "Helvetica"
        self.font_size = 10.0 # pt size
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self._initial_posns = None #bruce 050518
        # We need to reset _initial_posns to None whenever we recompute
        # self.axis from scratch or change the atom list in any way (even reordering it).
        # For now, we do this everywhere it's needed "by hand",
        # rather than in some (not yet existing) systematic and general way.
        # set default color to black.  probably should be a different color (grounds are black).
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.
        self.cancelled = True # We will assume the user will cancel

    def set_cntl(self):
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

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
        
    def rematom(self, atm):
        "Delete the jig if either of it's two atoms are deleted"
        Node.kill(self)
        return
        
    # Measure Distance jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, win, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the VdW and nuclei distances (e.g. 1.4/3.5) is included.
        '''
        
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        self.recompute_center_axis()
        text = "%.2f/%.2f" % (self.get_vdw_distance(), self.get_nuclei_distance())
        drawtext(text, self.color, self.center, self.font_size, self.assy.o)
    
    # Not implemented yet
    def writepov(self, file, dispdef):
        return
    
    # Returns the jig-specific mmp data for the current Measure Distance jig as:
    # mdistance font_size atom1 atom2 (???)
    # MMP RECORD NOT COMPLETELY DEFINED YET.  MARK 051030.
    # cleanup parts that don't work, til we get smarter.  wware 051031
    mmp_record_name = "mdistance"
    
    pass # end of class MeasureDistance
        
# == Measure Angle

class MeasureAngle(Measurement):
    # new class.  wware 051031
    '''A Measure Angle jig has two atoms and draws a line with a angle label between them.
    '''
    
    sym = "Angle"
    icon_names = ["measureangle.png", "measureangle-hide.png"]

    copyable_attrs = Jig.copyable_attrs + ('font_type', 'font_size', 'center', 'axis')

    # create a blank Measure Angle jig not connected to anything    
    def __init__(self, assy, atomlist): 
        Measurement.__init__(self, assy, atomlist)
        self.font_type = "Helvetica"
        self.font_size = 10.0 # pt size
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self._initial_posns = None #bruce 050518
        # We need to reset _initial_posns to None whenever we recompute
        # self.axis from scratch or change the atom list in any way (even reordering it).
        # For now, we do this everywhere it's needed "by hand",
        # rather than in some (not yet existing) systematic and general way.
        # set default color to black.  probably should be a different color (grounds are black).
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.
        self.cancelled = True # We will assume the user will cancel

    def set_cntl(self):
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

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
        from math import acos   # fix error in angle formula, and degrees not radians, wware 051101
        return (180/pi) * acos(dot(v01, v21) / (vlen(v01) * vlen(v21)))
        
    def rematom(self, atm):
        "Delete the jig if any of its atoms are deleted"
        Node.kill(self)
        return
        
    # Measure Angle jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, win, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the angle is included.
        '''
        
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        drawline(self.color, self.atoms[1].posn(), self.atoms[2].posn())
        self.recompute_center_axis()
        text = "%.2f" % self.get_angle()
        drawtext(text, self.color, self.center, self.font_size, self.assy.o)
    
    # Not implemented yet
    def writepov(self, file, dispdef):
        return
    
    # Returns the jig-specific mmp data for the current Measure Angle jig as:
    # mangle font_size atom1 atom2 atom3 (???)
    mmp_record_name = "mangle"
    
    pass # end of class MeasureAngle
        
# == Measure Dihedral

class MeasureDihedral(Measurement):
    # new class.  wware 051031
    '''A Measure Dihedral jig has two atoms and draws a line with a dihedral label between them.
    '''
    
    sym = "Dihedral"
    icon_names = ["measuredihedral.png", "measuredihedral-hide.png"]

    copyable_attrs = Jig.copyable_attrs + ('font_type', 'font_size', 'center', 'axis')

    # create a blank Measure Dihedral jig not connected to anything    
    def __init__(self, assy, atomlist): 
        Measurement.__init__(self, assy, atomlist)
        self.font_type = "Helvetica"
        self.font_size = 10.0 # pt size
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self._initial_posns = None #bruce 050518
        # We need to reset _initial_posns to None whenever we recompute
        # self.axis from scratch or change the atom list in any way (even reordering it).
        # For now, we do this everywhere it's needed "by hand",
        # rather than in some (not yet existing) systematic and general way.
        # set default color to black.  probably should be a different color (grounds are black).
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.
        self.cancelled = True # We will assume the user will cancel

    def set_cntl(self):
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

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
        sign = 1.0   # angles go from -180 to 180, wware 051101
        if dot(zy, u) < 0: sign = -1.0
        from math import acos   # degrees not radians, wware 051101
        return (180/pi) * sign * acos(dot(u, v) / (vlen(u) * vlen(v)))
        
    def rematom(self, atm):
        "Delete the jig if any of its atoms are deleted"
        Node.kill(self)
        return
        
    # Measure Dihedral jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw(self, win, dispdef):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the dihedral is included.
        '''
        
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
        drawline(self.color, self.atoms[0].posn(), self.atoms[1].posn())
        drawline(self.color, self.atoms[1].posn(), self.atoms[2].posn())
        drawline(self.color, self.atoms[2].posn(), self.atoms[3].posn())
        self.recompute_center_axis()
        text = "%.2f" % self.get_dihedral()
        drawtext(text, self.color, self.center, self.font_size, self.assy.o)
    
    # Not implemented yet
    def writepov(self, file, dispdef):
        return
    
    # Returns the jig-specific mmp data for the current Measure Dihedral jig as:
    # mdihedral font_size atom1 atom2 atom3 (???)
    mmp_record_name = "mdihedral"
    
    pass # end of class MeasureDihedral
        
# end of module jigs_measurements.py
