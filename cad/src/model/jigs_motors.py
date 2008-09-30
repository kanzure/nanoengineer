# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
jigs_motors.py -- Classes for motors.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History: 

050927. Split off Motor jigs from jigs.py into this file. Mark

"""

# imports from math vs. Numeric as discovered from running code on 2007/06/25.
from math import asin, atan2

from Numeric import pi
from Numeric import sqrt
from Numeric import dot
from Numeric import argmax
from Numeric import reshape

from OpenGL.GL import glPushMatrix
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import glPopMatrix

import foundation.env as env
from geometry.VQT import V, Q, A, norm, cross, vlen
from graphics.drawing.CS_draw_primitives import drawcylinder
from graphics.drawing.drawers import drawRotateSign
from graphics.drawing.drawers import drawbrick
from graphics.drawing.drawers import drawLinearSign

from utilities.Log import orangemsg
from utilities.Log import redmsg, greenmsg
from graphics.rendering.povray.povheader import povpoint #bruce 050413
from utilities.debug import print_compact_stack, print_compact_traceback
from model.jigs import Jig

from utilities.constants import gray

# == Motors

class Motor(Jig):
    """
    superclass for Motor jigs
    """
    axis = V(0,0,0) #bruce 060120; redundant with some subclass inits; some code could handle None here, but I'm not sure it all could.
        # WARNING: this is added to copyable_attrs in subclasses, not here, and is not added to mutable_attrs (possible bug). ###@@@
        # Also, self.center is not in mutable_attrs, but is modified by += , which is a likely bug. ####@@@@
        # [bruce 060228 comment]
    is_movable = True #mark 060120

    def __init__(self, assy, atomlist = []): #bruce 050526 added optional atomlist arg
        assert atomlist == [] # whether from default arg value or from caller -- for now
        Jig.__init__(self, assy, atomlist)

        self.quat = Q(1, 0, 0, 0)
            # is self.quat ever set to other values? if not, remove it; if so, add it to mutable_attrs. [bruce 060228 comment]
        
        #The motor is usually drawn as an opaque object. However when it is
        #being previewed, it is drawn as a transparent object - Ninad 2007-10-09
        self.previewOpacity = 0.4
        self.defaultOpacity = 1.0
        self.opacity = self.defaultOpacity
        

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
        return

    def recompute_center_axis(self, glpane): #bruce 060120 replaced los arg with glpane re bug 1344
        # try to point in direction of prior axis, or along line of sight if no old axis (self.axis is V(0,0,0) then)
        nears = [self.axis, glpane.lineOfSight, glpane.down]
        pos = A( map( lambda a: a.posn(), self.atoms ) )
        self.center = sum(pos)/len(pos)
        relpos = pos - self.center
        from geometry.geometryUtilities import compute_heuristic_axis
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
        """
        Rotary or Linear Motor context menu command: "Recenter on atoms"
        """
        ##e it might be nice to dim this menu item if the atoms haven't moved since this motor was made or recentered;
        # first we'd need to extend the __CM_ API to make that possible. [bruce 050704]

        cmd = greenmsg("Recenter on Atoms: ")

        self.recenter_on_atoms()
        info = "Recentered motor [%s] for current atom positions" % self.name 
        env.history.message( cmd + info ) 
        self.assy.w.win_update() # (glpane might be enough, but the other updates are fast so don't bother figuring it out)
        return

    def __CM_Align_to_chunk(self):
        """
        Rotary or Linear Motor context menu command: "Align to chunk"
        This uses the chunk connected to the first atom of the motor.
        """
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
        """
        Rotary or Linear Motor context menu command: "Reverse direction"
        """
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

    def move(self, offset):
        ###k NEEDS REVIEW: does this conform to the new Node API method 'move',
        # or should it do more invalidations / change notifications / updates? [bruce 070501 question]
        self.center += offset

    def rot(self, q):
        self.axis = q.rot(self.axis) #mark 060120.

    def posn(self):
        return self.center

    def getaxis(self):
        return self.axis

    def axen(self):
        return self.axis

    def remove_atom(self, *args, **opts):
        self._initial_posns = None #bruce 050518; needed in RotaryMotor, harmless in others
        return Jig.remove_atom(self, *args, **opts)

    def make_selobj_cmenu_items(self, menu_spec):
        """
        Add Motor-specific context menu items to <menu_spec> list when self is the selobj.
        """
        Jig.make_selobj_cmenu_items(self, menu_spec)
            #bruce 060313 share this code (it is identical to the following commented out code)
##        item = ('Hide', self.Hide)
##        menu_spec.append(item)
##        if self.disabled_by_user_choice:
##            item = ('Disabled', self.toggleJigDisabled, 'checked')
##        else:
##            item = ('Disable', self.toggleJigDisabled, 'unchecked')
##        menu_spec.append(item)
##        menu_spec.append(None) # Separator
##        item = ('Properties...', self.edit)
##        menu_spec.append(item)
        item = ('Align to Chunk', self.__CM_Align_to_chunk)
        menu_spec.append(item)
        item = ('Recenter on Atoms', self.__CM_Recenter_on_atoms)
        menu_spec.append(item)
        item = ('Reverse Direction', self.__CM_Reverse_direction)
        menu_spec.append(item)
    
    def updateCosmeticProps(self, previewing = False):
        """
        Update the cosmetic properties of motor
        """
        if not previewing:
            try:
                self.opacity = self.defaultOpacity
            except:
                print_compact_traceback("Can't set properties for the Rotary"\
                                        "Motor object. Ignoring exception.")
        else:
            self.opacity =  self.previewOpacity

    pass # end of class Motor


# == RotaryMotor

class RotaryMotor(Motor):
    """
    A Rotary Motor has an axis, represented as a point and
    a direction vector, a stall torque, a no-load speed, and
    a set of atoms connected to it
    To Be Done -- selecting & manipulation
    """
    sym = "RotaryMotor" # Was "Rotary Motor" (removed space). Mark 2007-05-28
    icon_names = ["modeltree/Rotary_Motor.png", "modeltree/Rotary_Motor-hide.png"]
    featurename = "Rotary Motor" #bruce 051203

    _initial_posns = None #bruce 060310 added default values for _initial_* and added them to copyable_attrs, to fix bug 1656
    _initial_quats = None

    copyable_attrs = Motor.copyable_attrs + ('torque', 'initial_speed', 'speed', 'enable_minimize', 'dampers_enabled', \
                                             'length', 'radius', 'sradius', \
                                             'center', 'axis', \
                                             '_initial_posns', '_initial_quats' )

    def __init__(self, 
                 assy, 
                 editCommand = None,
                 atomlist = []):
        """
        create a blank Rotary Motor not connected to anything
        """
        # [note (bruce 071128): future copy-code cleanup will require either
        # that the atomlist argument comes before the editCommand argument,
        # or that _um_initargs is overridden.]
        assert atomlist == [] # whether from default arg value or from caller -- for now
        Motor.__init__(self, assy, atomlist)
        self.torque = 0.0 # in nN * nm
        self.initial_speed = 0.0 # in gHz
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
        self.radius = 1.0 # default cylinder radius
        self.sradius = 0.2 #default spoke radius
        # Should self.cancelled be in RotaryMotorProp.setup? - Mark 050109
        self.cancelled = True # We will assume the user will cancel

        self.editCommand = editCommand

    def edit(self):
        """
        Overrides jig.edit. 
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('ROTARY_MOTOR', always_update = True)
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'ROTARY_MOTOR'
        #When a Motor object read from an mmp file is edited, we need to assign 
        #it an editCommand. So, when it is resized, the propMgr spinboxes
        #are properly updated. See also Plane.resizeGeometry. 
        if self.editCommand is None:
            self.editCommand = currentCommand
            
        currentCommand.editStructure(self)
        
        if self is self.assy.o.selobj:
            self.assy.o.selobj = None ###e shouldn't we use set_selobj instead?? [bruce 060726 question]
            # If the Properties dialog was selected from the GLPane's context menu, set selobj = None
            # so that we can see the jig's real color, not the highlighted color.  This is very important
            # when changing the jig's color from the properties dialog since it will remain highlighted
            # if we don't do this. mark 060312.


    def setProps(self, props):
        """
        Set the Rotary Motor properties. It is called while reading a MMP 
        file record or to restore the old properties if user cancels 
        edit operation on an exsiting motor.

        @param props: The rotary motor properties to be set.
        @type  props: tuple
        """

        self.name, self.color, self.torque, \
            self.speed, self.center, self.axis,\
            self.length, self.radius, self.sradius = props

        self._initial_posns = None


    def getProps(self):
        """
        Return the current properties of the Rotary motor.

        @return: The current properties of the rotary motor
        @rtype:  tuple
        """
        return (self.name,
                self.color,
                self.torque,
                self.speed,
                self.center,
                self.axis,
                self.length,
                self.radius,
                self.sradius)

    def _getinfo(self):        
        return  "[Object: Rotary Motor] [Name: " + str(self.name) + "] " + \
                "[Torque = " + str(self.torque) + " nN-nm] " + \
                "[Speed = " + str(self.speed) + " GHz]"

    def _getToolTipInfo(self): #ninad060825
        "Return a string for display in Dynamic Tool tip "
        from platform_dependent.PlatformDependent import fix_plurals
        attachedAtomCount = fix_plurals("Attached to %d atom(s)"%(len(self.atoms)))
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Rotary Motor"\
               +  "<br>" + "<font color=\"#0000FF\">Torque: </font>" + str(self.torque) +  " nN-nm " \
               +  "<br>" + "<font color=\"#0000FF\">Speed:</font> " + str(self.speed) + " GHz" \
               + "<br>"  + str(attachedAtomCount)

    def getstatistics(self, stats):
        stats.nrmotors += 1

    def norm_project_posns(self, posns):
        """
        [Private helper for getrotation]
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
        """
        Return a rotation angle for the motor. This is arbitrary, but rotates smoothly
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
        if not (self._initial_posns != posns): # have to use not (x != y) rather than (x == y) due to Numeric semantics!
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

    def _draw_jig(self, glpane, color, highlighted=False):
        """
        Draw a Rotary Motor jig as a cylinder along the axis, with a thin cylinder (spoke) to each atom.
        If <highlighted> is True, the Rotary Motor is draw slightly larger.
        """
        ## print "RMotor _draw_jig",env.redraw_counter
            # This confirms that Jigs are drawn more times than they ought to need to be,
            # possibly due to badly organized Jig hit-testing code -- 4 times on mouseenter that highlights them in Build mode
            # (even after I fixed a bug today in which it redrew the entire model twice each frame);
            # but it's hard to find something to compare it to for an objective test of whether being a Jig matters,
            # since atoms, bonds, and chunks all have special behavior of their own. BTW, the suspected bad Jig code might redraw
            # everything (not only Jigs) this often, even though all it cares about is seeing Jigs in glRenderMode output.
            # BTW2, on opening a file containing one jig, it was drawn something like 20 times.
            # [bruce 060724 comments]
        if highlighted:
            inc = 0.01 # tested.  Fixes bug 1681. mark 060314.
        else:
            inc = 0.0

        glPushMatrix()
        try:
            glTranslatef( self.center[0], self.center[1], self.center[2])
            q = self.quat
            glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) 

            orig_center = V(0.0, 0.0, 0.0)

            bCenter = orig_center - (self.length / 2.0 + inc) * self.axis
            tCenter = orig_center + (self.length / 2.0 + inc) * self.axis

            drawcylinder(color, bCenter, tCenter, 
                         self.radius + inc, 
                         capped = 1, 
                         opacity = self.opacity )
            for a in self.atoms:
                drawcylinder(color, orig_center, 
                             a.posn()-self.center, 
                             self.sradius + inc,
                             opacity = self.opacity)
            rotby = self.getrotation() #bruce 050518
                # if exception in getrotation, just don't draw the rotation sign
                # (safest now that people might believe what it shows about amount of rotation)
            drawRotateSign((0,0,0), bCenter, tCenter, self.radius, rotation = rotby)
        except:
            #bruce 060208 protect OpenGL stack from exception seen in bug 1445
            print_compact_traceback("exception in RotaryMotor._draw, continuing: ")
            print "  some info that might be related to that exception: natoms = %d" % len(self.atoms) ###@@@ might not keep this 
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
            if vlen(c - a.posn()) > 0.001: #bruce 060808 add condition to see if this fixes bug 719 (two places in this file)
                file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn()) + "," + str (self.sradius) +
                           ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the jig-specific mmp data for the current Rotary Motor as:
    #    torque speed (cx, cy, cz) (ax, ay, az) length radius sradius \n shaft
    mmp_record_name = "rmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        #bruce 060307 %.2f -> %.6f for params used by sim, %.2f -> %.3f for graphics-only params
        # (Note that for backwards compatibility we are constrained by files_mmp regexps which require these fields
        # to be 1 or more digits, '.', 1 or more digits. I'm more sure this is true of %.6f than of %f, though
        # in my tests these seemed equivalent. When someone has time they should check out python docs on this. [bruce 060307])
        dataline = "%.6f %.6f (%d, %d, %d) (%d, %d, %d) %.3f %.3f %.3f" % \
                 (self.torque, self.speed,
                  int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
                  int(axyz[0]), int(axyz[1]), int(axyz[2]),
                  self.length, self.radius, self.sradius   )
        return " " + dataline + "\n" + "shaft"

    def writemmp_info_leaf(self, mapping): #mark 060307 [bruce revised Jig -> Motor same day, should have no effect]
        "[extends superclass method]"
        Motor.writemmp_info_leaf(self, mapping)
        if self.initial_speed:
            # Note: info record not written if initial_speed = 0.0 (default).
            mapping.write("info leaf initial_speed = " + str(self.initial_speed) + "\n")
                # Note: this assumes all Python float formats (from str) can be read by the sim C code using atof().
                # Whether this is true needs testing, by trying out lots of sizes of values of initial speed
                # (perhaps negative too, if cad UI permits that). Ints might also be possible here (not sure),
                # so the sim reading code should permit them too. [bruce 060307 comment]
        return

    def readmmp_info_leaf_setitem( self, key, val, interp ): #mark 060307 [bruce revised Jig -> Motor same day, should have no effect]
        "[extends superclass method]"
        if key == ['initial_speed']:
            self.initial_speed = float(val)
                #bruce 060307 added "float" (not sure if this really matters, since cad doesn't compute with it)
        else:
            Motor.readmmp_info_leaf_setitem( self, key, val, interp)
        return

    pass # end of class RotaryMotor

def angle(x,y): #bruce 050518; see also atan2 (noticed used in VQT.py) which might do roughly the same thing
    """
    Return the angle above the x axis of the line from 0,0 to x,y,
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
    """
    A Linear Motor has an axis, represented as a point and
    a direction vector, a force, a stiffness, and
    a set of atoms connected to it
    To Be Done -- selecting & manipulation
    """
    sym = "LinearMotor" # Was "Linear Motor" (removed space). Mark 2007-05-28
    icon_names = ["modeltree/Linear_Motor.png", "modeltree/Linear_Motor-hide.png"]
    featurename = "Linear Motor" #bruce 051203

    copyable_attrs = Motor.copyable_attrs + ('force', 'stiffness', 'length', 'width', 'sradius', 'center', 'axis', \
                                             'enable_minimize', 'dampers_enabled')

    def __init__(self, 
                 assy, 
                 command = None,
                 atomlist = []):
        """
        create a blank Linear Motor not connected to anything
        """
        # [note (bruce 071128): future copy-code cleanup will require either
        # that the atomlist argument comes before the command argument,
        # or that _um_initargs is overridden.]
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
        self.sradius = 0.2 #default spoke radius
        self.cancelled = True # We will assume the user will cancel
        self.command = command

    def edit(self):
        """
        Overrides jig.edit. 
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('LINEAR_MOTOR', always_update = True)
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'LINEAR_MOTOR'
        #When a Motor object read from an mmp file is edited, we need to assign 
        #it an command. So, when it is resized, the propMgr spinboxes
        #are properly updated. See also Plane.resizeGeometry. 
        if self.command is None:
            self.command = currentCommand
            
        currentCommand.editStructure(self)
        
        if self is self.assy.o.selobj:
            self.assy.o.selobj = None ###e shouldn't we use set_selobj instead?? [bruce 060726 question]
            # If the Properties dialog was selected from the GLPane's context menu, set selobj = None
            # so that we can see the jig's real color, not the highlighted color.  This is very important
            # when changing the jig's color from the properties dialog since it will remain highlighted
            # if we don't do this. mark 060312.
    
    def getProps(self):
        """
        Return the current properties of the Rotary motor.

        @return: The current properties of the rotary motor
        @rtype:  tuple
        """
        return (self.name,
                self.color,
                self.force,
                self.stiffness,
                self.center,
                self.axis,
                self.length,
                self.width,
                self.sradius)
            
    # set the properties for a Linear Motor read from a (MMP) file
    def setProps(self, props):
        """
        Set the Linear Motor properties. It is called while reading a MMP 
        file record or to restore the old properties if user cancels 
        edit operation on an exsiting motor.

        @param props: The linear motor properties to be set.
        @type  props: tuple
        """
        self.name, self.color, self.force, \
            self.stiffness, self.center, \
            self.axis, self.length, \
            self.width, self.sradius = props

    def _getinfo_TEST(self): # please leave in for debugging POV-Ray lmotor macro. mark 060324
        a = self.axen()
        xrot = -atan2(a[1], sqrt(1-a[1]*a[1]))*180/pi
        yrot = atan2(a[0], sqrt(1-a[0]*a[0]))*180/pi

        return  "[Object: Linear Motor] [Name: " + str(self.name) + "] " + \
                "[Force = " + str(self.force) + " pN] " + \
                "[Stiffness = " + str(self.stiffness) + " N/m] " + \
                "[Axis = " + str(self.axis[0]) + ", " +  str(self.axis[1]) + ", " +  str(self.axis[2]) + "]" + \
                "[xRotation = " + str(xrot) + ", yRotation = " + str(yrot) + "]"

    def _getinfo(self):
        return  "[Object: Linear Motor] [Name: " + str(self.name) + "] " + \
                "[Force = " + str(self.force) + " pN] " + \
                "[Stiffness = " + str(self.stiffness) + " N/m]"

    def _getToolTipInfo(self): #ninad060825
        "Return a string for display in Dynamic Tool tip "
        from platform_dependent.PlatformDependent import fix_plurals
        attachedAtomCount = fix_plurals("Attached to %d atom(s)"%(len(self.atoms)))
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Linear Motor"\
               +  "<br>" + "<font color=\"#0000FF\">Force: </font>" + str(self.force) +  " pN " \
               +  "<br>" + "<font color=\"#0000FF\">Stiffness:</font> " + str(self.stiffness) + " N/m" \
               + "<br>"  + str(attachedAtomCount)

    def getstatistics(self, stats):
        stats.nlmotors += 1

    def _draw_jig(self, glpane, color, highlighted=False):
        """
        Draw a linear motor as a long box along the axis, with a thin cylinder (spoke) to each atom.
        """
        glPushMatrix()
        try:
            glTranslatef( self.center[0], self.center[1], self.center[2])
            q = self.quat
            glRotatef( q.angle*180.0/pi, q.x, q.y, q.z)

            orig_center = V(0.0, 0.0, 0.0)
            drawbrick(color, orig_center, self.axis, 
                      self.length, self.width, self.width, 
                      opacity = self.opacity)
            
            drawLinearSign((0,0,0), orig_center, self.axis, self.length, self.width, self.width)
                # (note: drawLinearSign uses a small depth offset so that arrows are slightly in front of brick)
                # [bruce comment 060302, a guess from skimming drawLinearSign's code]
            for a in self.atoms[:]:
                drawcylinder(color, orig_center, 
                             a.posn()-self.center, 
                             self.sradius, 
                             opacity = self.opacity)
        except:
            #bruce 060208 protect OpenGL stack from exception analogous to that seen for RotaryMotor in bug 1445
            print_compact_traceback("exception in LinearMotor._draw, continuing: ")
        glPopMatrix()

    # Write "lmotor" and "spoke" records to POV-Ray file in the format:
    # lmotor(<corner-point1>, <corner-point2>, <yrotate>, <yrotate>, <translate>, <r, g, b>)
    # spoke(<cap-point>, <base-point>, sbox-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        c = self.posn()
        a = self.axen()

        xrot = -atan2(a[1], sqrt(1-a[1]*a[1]))*180/pi
        yrot =  atan2(a[0], sqrt(1-a[0]*a[0]))*180/pi

        file.write("lmotor(" \
                   + povpoint([self.width *  0.5, self.width *  0.5, self.length *  0.5]) + "," \
                   + povpoint([self.width * -0.5, self.width * -0.5, self.length * -0.5]) + "," \
                   + "<0.0, " + str(yrot) + ", 0.0>," \
                   + "<" + str(xrot) + ", 0.0, 0.0>," \
                   + povpoint(c) + "," \
                   + "<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

        for a in self.atoms:
            if vlen(c - a.posn()) > 0.001: #bruce 060808 add condition to see if this fixes bug 719 (two places in this file)
                file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn())  + "," + str (self.sradius) +
                           ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")

    # Returns the jig-specific mmp data for the current Linear Motor as:
    #    force stiffness (cx, cy, cz) (ax, ay, az) length width sradius \n shaft
    mmp_record_name = "lmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        #bruce 060307 %.6f left as is for params used by sim, %.2f -> %.3f for graphics-only params
        # (see further comments in RotaryMotor method)
        dataline = "%.6f %.6f (%d, %d, %d) (%d, %d, %d) %.3f %.3f %.3f" % \
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
