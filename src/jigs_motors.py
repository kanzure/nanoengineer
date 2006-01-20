# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
jigs_motors.py -- Classes for motors.

$Id$

History: 

050927. Split off Motor jigs from jigs.py into this file. Mark

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

# == Motors

class Motor(Jig):
    "superclass for Motor jigs"
    axis = None #bruce 060120
    def __init__(self, assy, atomlist = []): #bruce 050526 added optional atomlist arg
        assert atomlist == [] # whether from default arg value or from caller -- for now
        Jig.__init__(self, assy, atomlist)
        
        self.quat = Q(1, 0, 0, 0)
        
    # == The following methods were moved from RotaryMotor to this class by bruce 050705,
    # since some were almost identical in LinearMotor (and those were removed from it, as well)
    # and others are wanted in it in order to implement "Recenter on atoms" in LinearMotor.
        
    # for a motor read from a file, the "shaft" record
    def setShaft(self, shaft):
        self.setAtoms(shaft) #bruce 041105 code cleanup
        self._initial_posns = None #bruce 050518; needed in RotaryMotor, harmless in others
    
    # for a motor created by the UI, center is average point and
    # axis is [as of 060120] computed as roughly normal to the shape of that set.
    def findCenterAndAxis(self, shaft, glpane): #bruce 060120 renamed this from findCenter, replaced los arg with glpane re bug 1344
        self.setAtoms(shaft) #bruce 041105 code cleanup
        self.recompute_center_axis(glpane)
        self.edit()
        
##        #bruce 060120 thinks the following looks bad and should be reviewed. The only reasonable purpose
##        # I know of would be to store initial positions for use after atoms move, and if that's the true
##        # purpose, it needs a comment explaining it. In fact, it looks like it's used for planes but not
##        # for motors, so let's zap it and find out.
##        self.atomPos = []
##        for a in shaft:
##            self.atomPos += [a.posn()]
        return

    def recompute_center_axis(self, glpane): #bruce 060120 replaced los arg with glpane re bug 1344
        # try to point in direction of prior axis, or along line of sight if no old axis (self.axis is None then)
        nears = [self.axis, glpane.lineOfSight, glpane.down]
        pos = A( map( lambda a: a.posn(), self.atoms ) )
        self.center = sum(pos)/len(pos)
        relpos = pos - self.center
        from geometry import compute_heuristic_axis
        axis = compute_heuristic_axis( relpos, 'normal', already_centered = True, nears = nears, dflt = None )
        if not axis:
            #e warning? I think so... BTW we pass dflt = None to make the warning come out more often;
            # I don't know if we'd need to check for it here if we didn't.
            env.history.message( orangemsg( "Warning: motor axis chosen arbitrarily since atom arrangement doesn't suggest one." ))
                #k can this come out too often during movie-playing? No, because we don't recompute axis then at all.
            axis = glpane.lineOfSight
        self.axis = axis
        self.assy.changed()  #bruce 060116 fix unreported bug analogous to bug 1331
        self._initial_posns = None #bruce 050518; needed in RotaryMotor, harmless in others
        return

    def recenter_on_atoms(self):
        "called from model tree cmenu command"
        self.recompute_center_axis(self.assy.o) #bruce 060120 pass glpane for its "point of view" (re bug 1344)
        #e maybe return whether we moved??
        return
    
    def __CM_Recenter_on_atoms(self): #bruce 050704 moved this from modelTree.py and made it use newer system for custom cmenu cmds
        '''Rotary or Linear Motor context menu command: "Recenter on atoms"
        '''
        ##e it might be nice to dim this menu item if the atoms haven't moved since this motor was made or recentered;
        # first we'd need to extend the __CM_ API to make that possible. [bruce 050704]
        
        cmd = greenmsg("Recenter on Atoms: ")
        
        self.recenter_on_atoms()
        info = "Recentered motor [%s] for current atom positions" % self.name 
        env.history.message( cmd + info ) 
        self.assy.w.win_update() # (glpane might be enough, but the other updates are fast so don't bother figuring it out)
        return

    def __CM_Align_to_chunk(self):
        '''Rotary or Linear Motor context menu command: "Align to chunk"
        This uses the chunk connected to the first atom of the motor.
        '''
        # I needed this when attempting to simulate the rotation of a long, skinny
        # chunk.  The axis computed from the attached atoms was not close to the axis
        # of the chunk.  I figured this would be a common feature that was easy to add.
        # 
        ##e it might be nice to dim this menu item if the chunk's axis hasn't moved since this motor was made or recentered;
        # first we'd need to extend the __CM_ API to make that possible. [mark 050717]
        
        cmd = greenmsg("Align to Chunk: ")
        
        chunk = self.atoms[0].molecule # Get the chunk attached to the motor's first atom.
        # wware 060116 bug 1330
        # The chunk's axis could have its direction exactly reversed and be equally valid.
        # We should choose between those two options for which one has the positive dot
        # product with the old axis, to avoid reversals of motor direction when going
        # between "align to chunk" and "recenter on atoms".
        #bruce 060116 modified this fix to avoid setting axis to V(0,0,0) if it's perpendicular to old axis.
        newAxis = chunk.getaxis()
        if dot(self.axis,newAxis) < 0:
            newAxis = - newAxis
        self.axis = newAxis
        self.assy.changed()   # wware 060116 bug 1331 - assembly changed when axis changed
        
        info = "Aligned motor [%s] on chunk [%s]" % (self.name, chunk.name) 
        env.history.message( cmd + info ) 
        self.assy.w.win_update()
        
        return

    def __CM_Reverse_direction(self): #bruce 060116 new feature (experimental)
        '''Rotary or Linear Motor context menu command: "Reverse direction"
        '''
        cmd = greenmsg("Reverse direction: ")
        self.reverse_direction()
        info = "Reversed direction of motor [%s]" % self.name 
        env.history.message( cmd + info ) 
        self.assy.w.win_update() # (glpane might be enough, but the other updates are fast so don't bother figuring it out)
        return

    def reverse_direction(self): #bruce 060116
        "Negate axis of this motor in order to reverse its direction."
        self.axis = - self.axis
        self.assy.changed()
        return
            
    def move(self, offset): #k can this ever be called?
        self.center += offset
    
    def rot(self, q):
        self.quat += q
        
    def posn(self):
        return self.center

    def getaxis(self):
        return self.axis


    def axen(self):
        return self.axis


    def rematom(self, *args, **opts): #bruce 050518
        self._initial_posns = None #bruce 050518; needed in RotaryMotor, harmless in others
        super = Jig
        return super.rematom(self, *args, **opts)

    pass # end of class Motor


# == RotaryMotor

class RotaryMotor(Motor):
    '''A Rotary Motor has an axis, represented as a point and
       a direction vector, a stall torque, a no-load speed, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''
    
    sym = "Rotary Motor"
    icon_names = ["rmotor.png", "rmotor-hide.png"]
    featurename = "Rotary Motor" #bruce 051203

    copyable_attrs = Motor.copyable_attrs + ('torque', 'speed', 'length', 'radius', 'sradius', 'center', 'axis', 'enable_minimize')

    # create a blank Rotary Motor not connected to anything    
    def __init__(self, assy, atomlist = []): #bruce 050526 added optional atomlist arg
        assert atomlist == [] # whether from default arg value or from caller -- for now
        Motor.__init__(self, assy, atomlist)
        self.torque = 0.0 # in nN * nm
        self.speed = 0.0 # in gHz
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self._initial_posns = None #bruce 050518
            # We need to reset _initial_posns to None whenever we recompute
            # self.axis from scratch or change the atom list in any way (even reordering it).
            # For now, we do this everywhere it's needed "by hand",
            # rather than in some (not yet existing) systematic and general way.
        # set default color of new rotary motor to gray
        self.color = gray # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = gray # This is the normal (unselected) color.
        self.length = 10.0 # default length of Rotary Motor cylinder
        self.radius = 2.0 # default cylinder radius
        self.sradius = 0.5 #default spoke radius
        # Should self.cancelled be in RotaryMotorProp.setup? - Mark 050109
        self.cancelled = True # We will assume the user will cancel

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        from RotaryMotorProp import RotaryMotorProp
        self.cntl = RotaryMotorProp(self, self.assy.o)

    # set the properties for a Rotary Motor read from a (MMP) file
    def setProps(self, name, color, torque, speed, center, axis, length, radius, sradius):
        self.name = name
        self.color = color
        self.torque = torque
        self.speed = speed
        self.center = center
        self.axis = norm(axis)
        self._initial_posns = None #bruce 050518
        self.length = length
        self.radius = radius
        self.sradius = sradius
   
    def _getinfo(self):        
        return  "[Object: Rotary Motor] [Name: " + str(self.name) + "] " + \
                    "[Torque = " + str(self.torque) + " nN-nm] " + \
                    "[Speed = " + str(self.speed) + " GHz]"
        
    def getstatistics(self, stats):
        stats.nrmotors += 1

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
        
    def getrotation(self): #bruce 050518 new feature for showing rotation of rmotor in its cap-arrow
        """Return a rotation angle for the motor. This is arbitrary, but rotates smoothly
        with the atoms, averaging out their individual thermal motion.
        It is not history-dependent -- e.g. it will be consistent regardless of how you jump around
        among the frames of a movie. But if we ever implement remaking or revising the motor position,
        or if you delete some of the motor's atoms, this angle is forgotten and essentially resets to 0.
        (That could be fixed, and the angle even saved in the mmp file, if desired. See code comments
        for other possible improvements.)
        """
        # possible future enhancements:
        # - might need to preserve rotation when we forget old posns, by setting an arb offset then;
        # - might need to preserve it in mmp file??
        # - might need to draw it into PovRay file??
        # - might need to preserve it when we translate or rotate entire jig with its atoms (doing which is NIM for now)
        # - could improve and generalize alg, and/or have sim do it (see comments below for details).
        #
        posns = A(map( lambda a: a.posn(), self.atoms ))
        posns -= self.center
        if self._initial_posns is None:
            # (we did this after -= center, so no need to forget posns if we translate the entire jig)
            self._initial_posns = posns # note, we're storing *relative* positions, in spite of the name!
            self._initial_quats = None # compute these the first time they're needed (since maybe never needed)
            return 0.0 # returning this now (rather than computing it below) is just an optim, in theory
        assert len(self._initial_posns) == len(posns), "bug in invalidating self._initial_posns when rmotor atoms change"
        if not (self._initial_posns != posns): # have to use not(x!=y) rather than (x==y) due to Numeric semantics!
            # no (noticable) change in positions - return quickly
            # (but don't change stored posns, in case this misses tiny changes which could accumulate over time)
            # (we do this before the subsequent stuff, to not waste redraw time when posns don't change;
            #  just re correctness, we could do it at a later stage)
            return 0.0
        # now we know the posns are different, and we have the old ones to compare them to.
        posns = self.norm_project_posns( posns) # this might modify posns object, and might return same or different object
        quats = self._initial_quats
        if quats is None:
            # precompute a quat to rotate new posns into a standard coord system for comparison to old ones
            # (Q args must be orthonormal and right-handed)
            oldposns = + self._initial_posns # don't modify those stored initial posns
                # (though it probably wouldn't matter if we did -- from now on,
                #  they are only compared to None and checked for length, as of 050518)
            oldposns = self.norm_project_posns( oldposns)
            axis = self.axis
            quats = self._initial_quats = [ Q(axis,pos1,cross(axis,pos1)) for pos1 in oldposns ]
        angs = []
        for qq, pos2 in zip( self._initial_quats, posns):
            npos2 = qq.unrot(pos2)
            # now npos2 is in yz plane, and pos1 (if transformed) would just be the y axis in that plane;
            # just get its angle in that plane (defined so that if pos2 = pos1, ie npos2 = (0,1,0), then angle is 0)
            ang = angle(npos2[1], npos2[2]) # in degrees
            angs.append(ang)
        # now average these angles, paying attention to their being on a circle
        # (which means the average of 1 and 359 is 0, not 180!)
        angs.sort()
            # Warning: this sort is only correct since we know they're in the range [0,360] (inclusive range is ok).
            # It might be correct for any range that covers the circle exactly once, e.g. [-180,180]
            # (not fully analyzed for that), but it would definitely be wrong for e.g. [-0.001, 360.001]!
            # So be careful if you change how angle() works.
        angs = A(angs)
        gaps = angs[1:] - angs[:-1]
        gaps = [angs[0] - angs[-1] + 360] + list(gaps)
        i = argmax(gaps)
        ##e Someday we should check whether this largest gap is large enough for this to make sense (>>180);
        # we are treating the angles as "clustered together in the part of the circle other than this gap"
        # and averaging them within that cluster. It would also make sense to discard outliers,
        # but doing this without jittering the rotation angle (as individual points become closer
        # to being outliers) would be challenging. Maybe better to just give up unless gap is, say, >>340.
        ##e Before any of that, just get the sim to do this in a better way -- interpret the complete set of
        # atom motions as approximating some overall translation and rotation, and tell us this, so we can show
        # not only rotation, but axis wobble and misalignment, and so these can be plotted.
        angs = list(angs)
        angs = angs[i:] + angs[:i] # start with the one just after the largest gap
        relang0 = angs[0]
        angs = A(angs) - relang0 # be relative to that, when we average them
        # but let them all be in the range [0,360)!
        angs = (angs + 720) % 360
            # We need to add 720 since Numeric's mod produces negative outputs
            # for negative inputs (unlike Python's native mod, which is correct)!
            # How amazingly ridiculous.
        ang = (sum(angs) / len(angs)) + relang0
        ang = ang % 360 # this is Python mod, so it's safe
        return ang
        
    # Rotary Motor is drawn as a cylinder along the axis,
    #  with a spoke to each atom
    def _draw(self, win, dispdef):
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) 
        
        orig_center = V(0.0, 0.0, 0.0)        
        
        bCenter = orig_center - (self.length / 2.0) * self.axis
        tCenter = orig_center + (self.length / 2.0) * self.axis
        drawcylinder(self.color, bCenter, tCenter, self.radius, 1 )
        for a in self.atoms:
            drawcylinder(self.color, orig_center, a.posn()-self.center, self.sradius)
        rotby = self.getrotation() #bruce 050518
            # if exception in getrotation, just don't draw the rotation sign
            # (safest now that people might believe what it shows about amount of rotation)
        drawRotateSign((0,0,0), bCenter, tCenter, self.radius, rotation = rotby)
        
        glPopMatrix()
        return
    
    # Write "rmotor" and "spoke" records to POV-Ray file in the format:
    # rmotor(<cap-point>, <base-point>, cylinder-radius, <r, g, b>)
    # spoke(<cap-point>, <base-point>, scylinder-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        c = self.posn()
        a = self.axen()
        file.write("rmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + povpoint(c-(self.length / 2.0)*a)  + "," + str (self.radius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn()) + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
    
    # Returns the jig-specific mmp data for the current Rotary Motor as:
    #    torque speed (cx, cy, cz) (ax, ay, az) length radius sradius \n shaft
    mmp_record_name = "rmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        dataline = "%.2f %.2f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f" % \
           (self.torque, self.speed,
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.radius, self.sradius   )
        return " " + dataline + "\n" + "shaft"
    
    pass # end of class RotaryMotor

def angle(x,y): #bruce 050518; see also atan2 (noticed used in VQT.py) which might do roughly the same thing
    """Return the angle above the x axis of the line from 0,0 to x,y,
    in a numerically stable way, assuming vlen(V(x,y)) is very close to 1.0.
    """
    if y < 0: return 360 - angle(x,-y)
    if x < 0: return 180 - angle(-x,y)
    if y > x: return 90 - angle(y,x)
    #e here we could normalize length if we felt like it,
    # and/or repair any glitches in continuity at exactly 45 degrees
    res = asin(y)*180/pi
    #print "angle(%r,%r) -> %r" % (x,y,res) 
    if res < 0:
        return res + 360 # should never happen
    return res

# == LinearMotor

class LinearMotor(Motor):
    '''A Linear Motor has an axis, represented as a point and
       a direction vector, a force, a stiffness, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''

    sym = "Linear Motor"
    icon_names = ["lmotor.png", "lmotor-hide.png"]
    featurename = "Linear Motor" #bruce 051203

    copyable_attrs = Motor.copyable_attrs + ('force', 'stiffness', 'length', 'width', 'sradius', 'center', 'axis', 'enable_minimize')

    # create a blank Linear Motor not connected to anything
    def __init__(self, assy, atomlist = []): #bruce 050526 added optional atomlist arg
        assert atomlist == [] # whether from default arg value or from caller -- for now
        Motor.__init__(self, assy, atomlist)
        
        self.force = 0.0
        self.stiffness = 0.0
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        # set default color of new linear motor to gray
        self.color = gray # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = gray # This is the normal (unselected) color.
        self.length = 10.0 # default length of Linear Motor box
        self.width = 2.0 # default box width
        self.sradius = 0.5 #default spoke radius
        self.cancelled = True # We will assume the user will cancel

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        from LinearMotorProp import LinearMotorProp
        self.cntl = LinearMotorProp(self, self.assy.o)

    # set the properties for a Linear Motor read from a (MMP) file
    def setProps(self, name, color, force, stiffness, center, axis, length, width, sradius):
        self.name = name
        self.color = color
        self.force = force
        self.stiffness = stiffness
        self.center = center
        self.axis = norm(axis)
        self.length = length
        self.width = width
        self.sradius = sradius

    def _getinfo(self):
        return  "[Object: Linear Motor] [Name: " + str(self.name) + "] " + \
                    "[Force = " + str(self.force) + " pN] " + \
                    "[Stiffness = " + str(self.stiffness) + " N/m]"

    def getstatistics(self, stats):
        stats.nlmotors += 1
   
    # drawn as a gray box along the axis,
    # with a thin cylinder to each atom 
    def _draw(self, win, dispdef):
        glPushMatrix()

        glTranslatef( self.center[0], self.center[1], self.center[2])
        q = self.quat
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) 
        
        orig_center = V(0.0, 0.0, 0.0)
        drawbrick(self.color, orig_center, self.axis, self.length, self.width, self.width)
        drawLinearSign((0,0,0), orig_center, self.axis, self.length, self.width, self.width)
        for a in self.atoms[:]:
            drawcylinder(self.color, orig_center, a.posn()-self.center, self.sradius)
        
        glPopMatrix()
            
    # Write "lmotor" and "spoke" records to POV-Ray file in the format:
    # lmotor(<cap-point>, <base-point>, box-width, <r, g, b>)
    # spoke(<cap-point>, <base-point>, sbox-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        c = self.posn()
        a = self.axen()
        file.write("lmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + 
                    povpoint(c-(self.length / 2.0)*a)  + "," + str (self.width / 2.0) + 
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn())  + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
    
    # Returns the jig-specific mmp data for the current Linear Motor as:
    #    force stiffness (cx, cy, cz) (ax, ay, az) length width sradius \n shaft
    mmp_record_name = "lmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        dataline = "%.6f %.6f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f" % \
           (self.force, self.stiffness,
                #bruce 050705 swapped force & stiffness order here, to fix bug 746;
                # since linear motors have never worked in sim in a released version,
                # and since this doesn't change the meaning of existing mmp files
                # (only the way the setup dialog generates them, making it more correct),
                # I'm guessing it's ok that this changes the actual mmp file-writing format
                # (to agree with the documented format and the reading-format)
                # and I'm guessing that no change to the format's required-date is needed.
                #bruce 050706 increased precision of force & stiffness from 0.01 to 0.000001
                # after email discussion with josh.
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.width, self.sradius    )
        return " " + dataline + "\n" + "shaft"
    
    pass # end of class LinearMotor

# end of module jigs_motors.py
