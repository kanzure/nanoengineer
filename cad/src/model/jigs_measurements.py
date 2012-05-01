# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
jigs_measurements.py -- Classes for measurement jigs.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

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

import sys
import numpy
from numpy import dot

import foundation.env as env

from geometry.VQT import V, A, norm, cross, vlen, angleBetween
from foundation.Utility import Node
from utilities.Log import redmsg, greenmsg, orangemsg
from utilities.debug import print_compact_stack, print_compact_traceback
from model.jigs import Jig
from graphics.drawing.dimensions import drawLinearDimension, drawAngleDimension, drawDihedralDimension
from graphics.drawing.drawers import drawtext

from utilities.constants import black
from utilities.prefs_constants import dynamicToolTipAtomDistancePrecision_prefs_key
from utilities.prefs_constants import dynamicToolTipBendAnglePrecision_prefs_key

from OpenGL.GLU import gluUnProject

def _constrainHandleToAngle(pos, p0, p1, p2):
    """
    This works in two steps.
    (1) Project pos onto the plane defined by (p0, p1, p2).
    (2) Confine the projected point to lie within the angular arc.
    """
    u = pos - p1
    z0 = norm(p0 - p1)
    z2 = norm(p2 - p1)
    oop = norm(cross(z0, z2))
    u = u - dot(oop, u) * oop
    # clip the point so it lies within the angle
    if dot(cross(z0, u), oop) < 0:
        # Clip on the z0 side of the angle.
        u = vlen(u) * z0
    elif dot(cross(u, z2), oop) < 0:
        # Clip on the z2 side of the angle.
        u = vlen(u) * z2
    return p1 + u

# == Measurement Jigs

# rename class for clarity, remove spurious methods, wware 051103
class MeasurementJig(Jig):
    """
    superclass for Measurement jigs
    """
    # constructor moved to base class, wware 051103
    def __init__(self, assy, atomlist):
        Jig.__init__(self, assy, atomlist)        
        self.font_name = "Helvetica"
        self.font_size = 10.0 # pt size
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.
        self.cancelled = True # We will assume the user will cancel
        self.handle_offset = V(0.0, 0.0, 0.0)

    # move some things to base class, wware 051103
    copyable_attrs = Jig.copyable_attrs + ('font_name', 'font_size')

    def constrainedPosition(self):
        """
        The jig maintains an unconstrained position. Constraining
        the position can mean projecting it onto a particular surface,
        and/or confining it to a particular region satisfying some
        linear inequalities in position.
        """
        raise Exception('expected to be overloaded')

    def clickedOn(self, pos):
        self.handle_offset = pos - self.center()
        self.constrain()

    def constrain(self):
        self.handle_offset = self.constrainedPosition() - self.center()

    def move(self, offset):
        ###k NEEDS REVIEW: does this conform to the new Node API method 'move', or should it be renamed? [bruce 070501 question]
        self.handle_offset += offset
        self.constrain()

    def posn(self):
        return self.center() + self.handle_offset

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
    # [... but this is still Node.kill. Maybe Jig.kill caused a bug and someone
    #  else changed it back and didn't comment it? Who knows. REVIEW sometime.
    #  bruce 080311 comment.]
    def remove_atom(self, atom, **opts):
        # bruce 080311 added **opts to match superclass method signature
        """
        Delete self if *any* of its atoms are deleted

        [overrides superclass method]
        """
        Node.kill(self) # superclass is Jig, not Node; see long comment above

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
    def _drawtext(self, text, color):
        # use atom positions to compute center, where text should go
        if self.picked:
            # move the text to the lower left corner, and make it big
            pos = A(gluUnProject(5, 5, 0))
            drawtext(text, color, pos,
                     3 * self.font_size, self.assy.o)
        else:
            pos1 = self.atoms[0].posn()
            pos2 = self.atoms[-1].posn()
            pos = (pos1 + pos2) / 2
            drawtext(text, color, pos, self.font_size, self.assy.o)
    
    # move into base class, wware 051103
    def set_cntl(self):
        from command_support.JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

    # move into base class, wware 051103
    def writepov(self, file, dispdef):
        sys.stderr.write(self.__class__.__name__ + ".writepov() not implemented yet")
    
    def will_copy_if_selected(self, sel, realCopy):
        """
        copy only if all my atoms are selected [overrides Jig.will_copy_if_selected]
        """
        # for measurement jigs, copy only if all atoms selected, wware 051107
        # [bruce 060329 adds: this doesn't prevent the copy if the jig is inside a Group, and that causes a bug]
        for atom in self.atoms:
            if not sel.picks_atom(atom):
                if realCopy:
                    msg = "Can't copy a measurement jig [%s] unless all its atoms are selected." % (self.name,)
                    env.history.message(orangemsg(msg))
                return False
        return True

    def center(self):
        c = numpy.array((0.0, 0.0, 0.0))
        n = len(self.atoms)
        for a in self.atoms:
            c += a.posn() / n
        return c

    def writemmp_info_leaf(self, mapping):
        Node.writemmp_info_leaf(self, mapping)
        x, y, z = self.constrainedPosition()
        mapping.write("info leaf handle = %g %g %g\n" % (x, y, z))

    def readmmp_info_leaf_setitem(self, key, val, interp):
        import string, numpy
        if key == ['handle']:
            self.handle_offset = numpy.array(map(string.atof, val.split())) - self.center()
        else:
            Jig.readmmp_info_leaf_setitem(self, key, val, interp)

    pass # end of class MeasurementJig


# == Measure Distance

class MeasureDistance(MeasurementJig):
    """
    A Measure Distance jig has two atoms and draws a line with a distance label between them.
    """
    sym = "Distance"
    icon_names = ["modeltree/Measure_Distance.png", "modeltree/Measure_Distance-hide.png"]
    featurename = "Measure Distance Jig" # added, wware 20051202

    def constrainedPosition(self):
        a = self.atoms
        pos, p0, p1 = self.center() + self.handle_offset, a[0].posn(), a[1].posn()
        z = p1 - p0
        nz = norm(z)
        dotprod = dot(pos - p0, nz)
        if dotprod < 0.0:
            return pos - dotprod * nz
        elif dotprod > vlen(z):
            return pos - (dotprod - vlen(z)) * nz
        else:
            return pos

    def _getinfo(self): 
        return  "[Object: Measure Distance] [Name: " + str(self.name) + "] " + \
                    "[Nuclei Distance = " + str(self.get_nuclei_distance()) + " ]" + \
                    "[VdW Distance = " + str(self.get_vdw_distance()) + " ]"
                    
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        #honor user preferences for digit after decimal
        distPrecision = env.prefs[dynamicToolTipAtomDistancePrecision_prefs_key] 
        nucleiDist = round(self.get_nuclei_distance(),distPrecision)
        vdwDist =  round(self.get_vdw_distance(),distPrecision)
        
        attachedAtoms = str(self.atoms[0]) + "-" + str(self.atoms[1])
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Measure Distance"\
        +  "<br>" + "<font color=\"#0000FF\">Atoms: </font>" + attachedAtoms+"<br>"\
         +"<font color=\"#0000FF\">Nuclei Distance: </font>" + str(nucleiDist) +  " A" \
        +  "<br>" + "<font color=\"#0000FF\">VdW Distance: </font> " + str(vdwDist)  + " A"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mdistance += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_nuclei_distance(self):
        """
        Returns the distance between two atoms (nuclei)
        """
        return vlen (self.atoms[0].posn()-self.atoms[1].posn())
        
    def get_vdw_distance(self):
        """
        Returns the VdW distance between two atoms
        """
        return self.get_nuclei_distance() - self.atoms[0].element.rvdw - self.atoms[1].element.rvdw
        
    # Measure Distance jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw_jig(self, glpane, color, highlighted=False):
        """
        Draws a wire frame cube around two atoms and a line between them.
        A label displaying the VdW and nuclei distances (e.g. 1.4/3.5) is included.
        """
        MeasurementJig._draw_jig(self, glpane, color, highlighted)
        text = "%.2f/%.2f" % (self.get_vdw_distance(), self.get_nuclei_distance())
        # mechanical engineering style dimensions
        drawLinearDimension(color, self.assy.o.right, self.assy.o.up, self.constrainedPosition(),
                            self.atoms[0].posn(), self.atoms[1].posn(), text, highlighted=highlighted)

    mmp_record_name = "mdistance"
    
    pass # end of class MeasureDistance
        
# == Measure Angle

class MeasureAngle(MeasurementJig): # new class.  wware 051031
    """
    A Measure Angle jig has three atoms.
    """
    sym = "Angle"
    icon_names = ["modeltree/Measure_Angle.png", "modeltree/Measure_Angle-hide.png"]
    featurename = "Measure Angle Jig" # added, wware 20051202

    def constrainedPosition(self):
        import types
        a = self.atoms
        return _constrainHandleToAngle(self.center() + self.handle_offset,
                                       a[0].posn(), a[1].posn(), a[2].posn())

    def _getinfo(self):   # add atom list, wware 051101
        return  "[Object: Measure Angle] [Name: " + str(self.name) + "] " + \
                    ("[Atoms = %s %s %s]" % (self.atoms[0], self.atoms[1], self.atoms[2])) + \
                    "[Angle = " + str(self.get_angle()) + " ]"
                 
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        #honor user preferences for digit after decimal
        anglePrecision = env.prefs[dynamicToolTipBendAnglePrecision_prefs_key] 
        bendAngle = round(self.get_angle(),anglePrecision)
             
        attachedAtoms = str(self.atoms[0]) + "-" + str(self.atoms[1]) + "-" + str(self.atoms[2])
        
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type: </font>Measure Angle"\
        +  "<br>" + "<font color=\"#0000FF\">Atoms: </font>" + attachedAtoms + "<br>"\
        + "<font color=\"#0000FF\">Angle </font> " + str(bendAngle)  + " Degrees"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mangle += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_angle(self):
        """
        Returns the angle between two atoms (nuclei)
        """
        v01 = self.atoms[0].posn()-self.atoms[1].posn()
        v21 = self.atoms[2].posn()-self.atoms[1].posn()
        return angleBetween(v01, v21)
        
    # Measure Angle jig is drawn as a line between two atoms with a text label between them.
    # A wire cube is also drawn around each atom.
    def _draw_jig(self, glpane, color, highlighted=False):
        """
        Draws a wire frame cube around two atoms and a line between them.
        A label displaying the angle is included.
        """
        MeasurementJig._draw_jig(self, glpane, color, highlighted) # draw boxes around each of the jig's atoms.

        text = "%.2f" % self.get_angle()
        # mechanical engineering style dimensions
        drawAngleDimension(color, self.assy.o.right, self.assy.o.up, self.constrainedPosition(),
                           self.atoms[0].posn(), self.atoms[1].posn(), self.atoms[2].posn(),
                           text, highlighted=highlighted)

    mmp_record_name = "mangle"
    
    pass # end of class MeasureAngle
        
# == Measure Dihedral

class MeasureDihedral(MeasurementJig): # new class. wware 051031
    """
    A Measure Dihedral jig has four atoms.
    """
    sym = "Dihedral"
    icon_names = ["modeltree/Measure_Dihedral.png", "modeltree/Measure_Dihedral-hide.png"]
    featurename = "Measure Dihedral Jig" # added, wware 20051202

    def constrainedPosition(self):
        a = self.atoms
        p0, p1, p2, p3 = a[0].posn(), a[1].posn(), a[2].posn(), a[3].posn()
        axis = norm(p2 - p1)
        midpoint = 0.5 * (p1 + p2)
        return _constrainHandleToAngle(self.center() + self.handle_offset,
                                       p0 - dot(p0 - midpoint, axis) * axis,
                                       midpoint,
                                       p3 - dot(p3 - midpoint, axis) * axis)

    def _getinfo(self):    # add atom list, wware 051101
        return  "[Object: Measure Dihedral] [Name: " + str(self.name) + "] " + \
                    ("[Atoms = %s %s %s %s]" % (self.atoms[0], self.atoms[1], self.atoms[2], self.atoms[3])) + \
                    "[Dihedral = " + str(self.get_dihedral()) + " ]"
                    
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        #honor user preferences for digit after decimal
        anglePrecision = env.prefs[dynamicToolTipBendAnglePrecision_prefs_key] 
        dihedral = round(self.get_dihedral(),anglePrecision)
             
        attachedAtoms = str(self.atoms[0]) + "-" + str(self.atoms[1]) + "-" + str(self.atoms[2]) + "-" + str(self.atoms[3])
        
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type: </font>Measure Dihedral"\
        +  "<br>" + "<font color=\"#0000FF\">Atoms: </font>" + attachedAtoms + "<br>"\
        + "<font color=\"#0000FF\">Angle </font> " + str(dihedral)  + " Degrees"
        
    def getstatistics(self, stats): # Should be _getstatistics().  Mark
        stats.num_mdihedral += 1
        
    # Helper functions for the measurement jigs.  Should these be general Atom functions?  Mark 051030.
    def get_dihedral(self):
        """
        Returns the dihedral between two atoms (nuclei)
        """
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
        """
        Draws a wire frame cube around two atoms and a line between them.
        A label displaying the dihedral is included.
        """
        MeasurementJig._draw_jig(self, glpane, color, highlighted) # draw boxes around each of the jig's atoms.

        text = "%.2f" % self.get_dihedral()
        # mechanical engineering style dimensions
        drawDihedralDimension(color, self.assy.o.right, self.assy.o.up, self.constrainedPosition(),
                              self.atoms[0].posn(), self.atoms[1].posn(),
                              self.atoms[2].posn(), self.atoms[3].posn(),
                              text, highlighted=highlighted)
    
    mmp_record_name = "mdihedral"
    
    pass # end of class MeasureDihedral
        
# end of module jigs_measurements.py
