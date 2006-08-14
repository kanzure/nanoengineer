# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
ops_motion.py -- various ways of moving or spatially distorting
selected atoms or chunks (and someday, attached jigs).
These operations don't create or destroy atoms or bonds.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce 050913 used env.history in some places.
"""

from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from VQT import V, norm, Q, vlen, orthodist
import env
from math import pi


class ops_motion_Mixin:
    "Mixin class for providing these methods to class Part"
    
    ###@@@ move/rot should be extended to apply to jigs too (and fit into some naming convention)
    
    def movesel(self, offset):
        "move selected chunks and jigs in space"
        movables = self.getSelectedMovables()
        
        for m in movables:
            self.changed() #Not check if this can be combined into one call
            m.move(offset)
  
  
    def rotsel(self, quat):
        '''Rotate selected chunks/jigs in space. [Huaicai 8/30/05: Fixed the problem of each rotating
           around its own center, they will now rotate around their common center]'''
        # Find the common center of all selected chunks to fix bug 594 
        comCenter = V(0.0, 0.0, 0.0)
            
        movables = self.getSelectedMovables()
        numMovables = len(movables)
        
        if numMovables:
            for m in movables: comCenter += m.center
            
            comCenter /= numMovables
        
            # Move the selected chunks    
            for m in movables:
                self.changed() #Not sure if this can be combined into one call
                
                # Get the moving offset because of the rotation around each movable's own center
                rotOff = quat.rot(m.center - comCenter)    
                rotOff = comCenter - m.center + rotOff
                
                m.move(rotOff) 
                m.rot(quat) 
        
            
    #stretch a molecule
    def Stretch(self):

        mc = env.begin_op("Stretch")
        try:
            cmd = greenmsg("Stretch: ")
            
            if not self.selmols:
                msg =  redmsg("No selected chunks to stretch")
                env.history.message(cmd + msg)
            else:
                self.changed()
                for m in self.selmols:
                    m.stretch(1.1)
                self.o.gl_update()
                
                # Added history message.  Mark 050413.
                info = fix_plurals( "Stretched %d chunk(s)" % len(self.selmols))
                env.history.message( cmd + info)
        finally:
            env.end_op(mc)
        return
    
    #invert a chunk
    def Invert(self):
        '''Invert the atoms of the selected chunk(s)'''

        mc = env.begin_op("Invert")
        cmd = greenmsg("Invert: ")
        
        if not self.selmols:
            msg = redmsg("No selected chunks to invert")
            env.history.message(cmd + msg)
            return
        self.changed()
        for m in self.selmols:
            m.stretch(-1.0)
        self.o.gl_update()
        
        info = fix_plurals( "Inverted %d chunk(s)" % len(self.selmols))
        env.history.message( cmd + info)
        env.end_op(mc) #e try/finally?
        
    #Mirror the selected chunks 
    def Mirror(self):
        "Mirror the selected chunk(s) about a selected grid plane."
        #ninad060812--: As of 060812 (11 PM EST) it creates mirror chunks about a selected grid plane/(or jig with 0 atoms)
        #This has some known bugs. listed below ninad060812: 
        #What it does:
            #- Mirrors selected chunks about a selected Grid plane. (Moves the mirrored copies on the other side of the mirror).
        # Known Bugs and NIYs for which I(ninad) need help---
            #2. When the selected chunks have interchunk bonds, and you hit mirror, it breaks the interchunk bond while doing mirror 
            #operation. (Suggestion: It should treat connected chunks as a single entity while doing mirror op..but once the operation is
            # over, it should separate them like the original chunks)
            #6. Untested on very large objects. Hopefully  it will take the same amount of time as that of the copy op.
            
        mc = env.begin_op("Mirror")
        cmd = greenmsg("Mirror: ")
        
        if not self.selmols:
            msg = redmsg("No chunks selected to mirror")
            env.history.message(cmd + msg)
            return
        #self.changed() # well assembly is not changed here - ninad060814
        
        if self.topnode.picked:
            self.topnode.unpick_top() #ninad060814 this is necessary to fix a bug. Otherwise program will crash if you try to mirror
                                                    #when the top node of the part (main part of clipboard) is selected
        
        jigs = self.assy.getSelectedJigs()
        jigCounter = self.getQualifiedMirrorJigs(jigs) # ninad060814 - check if Grid Plane is selected. If it does , check how many!
                
        if jigCounter < 1:
            msg = redmsg("No mirror plane selected. Please select a Grid Plane first.")
            instruction = "  (If it doesn't exists, create it using <b>Jigs > Grid Plane</b> )"
            env.history.message(cmd + msg  + instruction)
            return 
        elif jigCounter >1:
            msg = redmsg("More than one Grid Plane selected. Please select only one Grid Plane and try again")
            env.history.message(cmd + msg ) 
            return 
        else:
            for m in self.selmols:
                mirrorChunk = m.copy(None) #ninad060812 make a copy of the selection first
                self.o.assy.addmol(mirrorChunk)
                mirrorChunk.stretch(-1.0)
                self.mirrorAxis = jigs[0].getaxis() # ninad060812 Get the axis vector of the Grid Plane. Then you need to 
                                                                   #rotate the inverted chunk by pi around this axis vector 
                mirrorChunk.rot(Q(self.mirrorAxis, pi)) 
    
                self.mirrorDistance, self.wid = orthodist(m.center, self.mirrorAxis, jigs[0].center) # ninad060813 This gives an orthogonal distance between the chunk center and mirror plane.
                mirrorChunk.move(2*(self.mirrorDistance)*self.mirrorAxis)# @@@@ ninad060813 This moves the mirrror chunk on the other side of the mirror plane. It surely moves the chunk along the axis of the mirror plane but I am still unsure if this *always* moves the chunk on the other side of the mirror. Probably the 'orthodist' function has helped me here??  Need to discuss this.
                                                                                                                        
            self.w.win_update()  # update GLPane as well as MT
            
            info = fix_plurals( "Mirrored  %d chunk(s)" % len(self.selmols))
            env.history.message( cmd + info)
            env.end_op(mc) 
        
    def getQualifiedMirrorJigs(self, jigs):
        "Returns the jig names which can be used a  reference plane in Mirror Feature. Also returns how many such jigs are selected"
        #I am planning to extend this method for ESP images also. - ninad060814
        jigCounter = 0
        for j in jigs:
            if j.mmp_record_name is "gridplane":
                jigCounter = jigCounter + 1
        return jigCounter # if its 0 then no grid plane is selected.  If its >1 more than 1 grid planes are selected
    
    def align(self):
        
        cmd = greenmsg("Align to Common Axis: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            env.history.message(cmd + msg)
            return
        self.changed() #bruce 050131 bugfix or precaution
        #ax = V(0,0,0)
        #for m in self.selmols:
        #    ax += m.getaxis()
        #ax = norm(ax)
        ax = self.selmols[0].getaxis() # Axis of first selected chunk
        for m in self.selmols[1:]:
            m.rot(Q(m.getaxis(),ax))
        self.o.gl_update()
        
        info = fix_plurals( "Aligned %d chunk(s)" % (len(self.selmols) - 1) ) \
            + " to chunk %s" % self.selmols[0].name
        env.history.message( cmd + info)
        
    def alignmove(self):
        
        cmd = greenmsg("Move to Axis: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            env.history.message(cmd + msg)
            return
        self.changed()
        #ax = V(0,0,0)
        #for m in self.selmols:
        #    ax += m.getaxis()
        #ax = norm(ax)
        ax = self.selmols[0].getaxis() # Axis of first selected chunk
        ctr = self.selmols[0].center # Center of first selected chunk
        for m in self.selmols[1:]:
            m.rot(Q(m.getaxis(),ax))
            m.move(ctr-m.center) # offset
        
        self.o.gl_update()
        
        info = fix_plurals( "Aligned %d chunk(s)" % (len(self.selmols) - 1) ) \
            + " to chunk %s" % self.selmols[0].name
        env.history.message( cmd + info)
        
    pass # end of class ops_motion_Mixin

# end