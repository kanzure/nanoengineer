# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
jigs_measurements.py -- Classes for measurement jigs.

$Id$

History: 

060324 wware - with a debug pref, we can now get a drawing style for
the distance measuring jig that looks like a dimension on a mechanical
drawing. Future plans: similar drawing styles for angle and dihedral
measurements, and switch drawing to OpenGL display lists for performance
improvement.

05(later) wware - Simulator support was added, as well as MMP file
records.

051104 wware - three measurement jigs (distance, angle, dihedral)
written over the last few days. No simulator support yet, but they
work fine in the CAD system, and the MMP file records should be
acceptable when the time comes for sim support.

"""

from VQT import *
from shape import *
from chem import *
from Utility import *
from HistoryWidget import redmsg, greenmsg, orangemsg
from povheader import povpoint #bruce 050413
from debug import print_compact_stack, print_compact_traceback
import env #bruce 050901
from jigs import Jig
from dimensions import drawLinearDimension, drawAngleDimension, drawDihedralDimension

# work in progress, wware 060719
class Handle:
    """A handle is a small visible spherical object which can be
    dragged around in 3 dimensions. Its purpose is to provide a
    draggable point on a jig, for instance to set the position where
    we display text in a length measurement jig.
    """
    def __init__(self, assy, owner, posn):
        self._posn_offset = Numeric.array((0.0, 0.0, 0.0))
        self.owner = owner

    def constrainMovement(self, posn):
        # expected to be overloaded
        return posn

    def move(self, offset):
        c = self.owner.center()
        p = c + self._posn_offset + offset
        p = self.constrainMovement(p)
        self._posn_offset = p - c

    def posn(self):
        return self.owner.center() + self._posn_offset

    def draw(self, glpane, color, highlighted=False):
        from constants import magenta, yellow
        if True:
            if highlighted:
                color = yellow
            else:
                color = magenta
        level = 1
        drawrad = 0.25
        drawsphere(color, self.posn(), drawrad, level)

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
        self.handle = Handle(assy, self, V(0.0, 0.0, 0.0))

    # move some things to base class, wware 051103
    copyable_attrs = Jig.copyable_attrs + ('font_name', 'font_size')

    # move to base class, wware 051103
    # Email from Bruce, 060327 <<<<
    # It's either a bug or a bad style error to directly call Node.kill,
    # skipping the superclass kill methods if any (and there is one,
    # at least Jig.kill).
    # In this case it might not be safe to call Jig.kill, since that might
    # recurse into this method, but (1) this needs a comment, (2) this is a
    # possible bug since removing the atoms is not happening when this jig
    # is killed, but perhaps needs to (otherwise the atoms will be listing
    # this jig as one of their jigs even after it's killed -- not sure what
    # harm this causes but it might be bad, e.g. a minor memory leak or
    # maybe some problem when copying them).
    # If you're not sure what to do about any of it, just commenting it
    # or filing a reminder bug is ok for now. It interacts with some code
    # I'm working on now in other files, so it might be just as well for me
    # to be the one to change the code. >>>>
    # For now, I think I'll go with Jig.kill, and let Bruce modify as needed.
    def rematom(self, atm):
        "Delete the jig if any of its atoms are deleted"
        Node.kill(self)

    def move(self, offset):
        self.handle.move(offset)
        
    # Set the properties for a Measure Distance jig read from a (MMP) file
    # include atomlist, wware 051103
    def setProps(self, name, color, font_name, font_size, atomlist):
        self.name = name
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.setAtoms(atomlist)
        self.handle.constrainMovement = self.handleConstraint()
        # apply the constraint to the handle position
        self.handle.move(V(0.0, 0.0, 0.0))

    def handleConstraint(self):
        return lambda pos: pos

    # simplified, wware 051103
    # Following Postscript: font names NEVER have parentheses in them.
    # So we can use parentheses to delimit them.
    def mmp_record_jigspecific_midpart(self):
        return " (%s) %d" % (self.font_name, self.font_size)
        
    # unify text-drawing to base class, wware 051103
    def _drawtext(self, text, color):
        # use atom positions to compute center, where text should go
        if self.picked:
            # move the text to the lower left corner, and make it big
            # self.assy.o is the GLPane
            drawtext(text, color, self.assy.o.selectedJigTextPosition(),
                     3 * self.font_size, self.assy.o)
        else:
            pos1 = self.atoms[0].posn()
            pos2 = self.atoms[-1].posn()
            pos = (pos1 + pos2) / 2
            drawtext(text, color, pos, self.font_size, self.assy.o)
    
    # move into base class, wware 051103
    def set_cntl(self):
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

    # move into base class, wware 051103
    def writepov(self, file, dispdef):
        sys.stderr.write(self.__class__.__name__ + ".writepov() not implemented yet")
    
    def will_copy_if_selected(self, sel, realCopy):
        "copy only if all my atoms are selected [overrides Jig.will_copy_if_selected]"
        # for measurement jigs, copy only if all atoms selected, wware 051107
        # [bruce 060329 adds: this doesn't prevent the copy if the jig is inside a Group, and that causes a bug]
        for atom in self.atoms:
            if not sel.picks_atom(atom):
                if realCopy:
                    msg = "Can't copy a measurement jig [%s] unless all its atoms are selected." % (self.name,)
                    env.history.message(orangemsg(msg))
                return False
        return True

    def _draw_jig(self, glpane, color, highlighted=False):
        Jig._draw_jig(self, glpane, color, highlighted) # draw boxes around each of the jig's atoms.
        self.handle.draw(glpane, color, highlighted)

    def center(self):
        c = Numeric.array((0.0, 0.0, 0.0))
        n = len(self.atoms)
        for a in self.atoms:
            c += a.posn() / n
        return c

    pass # end of class MeasurementJig


# == Measure Distance

class MeasureDistance(MeasurementJig):
    '''A Measure Distance jig has two atoms and draws a line with a distance label between them.
    '''
    
    sym = "Distance"
    icon_names = ["measuredistance.png", "measuredistance-hide.png"]
    featurename = "Measure Distance Jig" # added, wware 20051202

    def handleConstraint(self):
        from dimensions import constrainLinearHandle
        return lambda pos, atoms=self.atoms: constrainLinearHandle(pos, atoms[0], atoms[1])

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
    def _draw_jig(self, glpane, color, highlighted=False):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the VdW and nuclei distances (e.g. 1.4/3.5) is included.
        '''
        MeasurementJig._draw_jig(self, glpane, color, highlighted)
        text = "%.2f/%.2f" % (self.get_vdw_distance(), self.get_nuclei_distance())
        # mechanical engineering style dimensions
        drawLinearDimension(color, self.assy.o.right, self.assy.o.up, self.handle.posn(),
                            self.atoms[0].posn(), self.atoms[1].posn(), text)

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
        
    def handleConstraint(self):
        from dimensions import constrainHandleToAngle
        atoms = self.atoms
        def constrain(pos, a0=atoms[0], a1=atoms[1], a2=atoms[2]):
            return constrainHandleToAngle(pos, a0.posn(), a1.posn(), a2.posn())
        return constrain

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
    def _draw_jig(self, glpane, color, highlighted=False):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the angle is included.
        '''
        MeasurementJig._draw_jig(self, glpane, color, highlighted) # draw boxes around each of the jig's atoms.

        text = "%.2f" % self.get_angle()
        # mechanical engineering style dimensions
        drawAngleDimension(color, self.assy.o.right, self.assy.o.up, self.handle.posn(),
                           self.atoms[0].posn(), self.atoms[1].posn(), self.atoms[2].posn(),
                           text)

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
        
    def handleConstraint(self):
        from dimensions import constrainDihedralHandle
        atoms = self.atoms
        def constrain(pos, a0=atoms[0], a1=atoms[1], a2=atoms[2], a3=atoms[3]):
            return constrainDihedralHandle(pos, a0.posn(), a1.posn(), a2.posn(), a3.posn())
        return constrain

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
    def _draw_jig(self, glpane, color, highlighted=False):
        '''Draws a wire frame cube around two atoms and a line between them.
        A label displaying the dihedral is included.
        '''
        MeasurementJig._draw_jig(self, glpane, color, highlighted) # draw boxes around each of the jig's atoms.

        text = "%.2f" % self.get_dihedral()
        # mechanical engineering style dimensions
        drawDihedralDimension(color, self.assy.o.right, self.assy.o.up, self.handle.posn(),
                              self.atoms[0].posn(), self.atoms[1].posn(),
                              self.atoms[2].posn(), self.atoms[3].posn(),
                              text)
    
    mmp_record_name = "mdihedral"
    
    pass # end of class MeasureDihedral
        
# end of module jigs_measurements.py
