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
    #def Invertorig(self):
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
    #def Invert(self):
        "Mirror the selected chunk(s) about a selected grid plane."
        #ninad060812--: As of 060812 (11 PM EST) it creates mirror chunks about a selected grid plane/(or jig with 0 atoms)
        #This has some known bugs. listed below ninad060812: 
        #What it does:
            #- Mirrors selected chunks about a selected Grid plane. (Moves the mirrored copies on the other side of the mirror).
        # Known Bugs and NIYs for which I(ninad) need help---
            #1. (major bug) If the whole part is selected (either main part or any clipboard part) and then you try to mirror, it  
            # crashes  the program. For that, we need a check to see that the whole part is not selected. (probably similar to the one
            # implemented in TreeWidget.py lines 1125-1132)
            #2. When the selected chunks have interchunk bonds, and you hit mirror, it breaks the interchunk bond while doing mirror 
            #operation. (Suggestion: It should treat connected chunks as a single entity while doing mirror op..but once the operation is
            # over, it should separate them like the original chunks)
            #3. UI for this feature is NIY.
            #4. If I mirror a clipboard chunk, the history says "Mirrored 0 chunks"
            #5. Untested (and most likely it will break if multiple grid planes are selected) 
            #6. Untested on very large objects. Hopefully  it will take the same amount of time as that of the copy op.
        mc = env.begin_op("Mirror")
        cmd = greenmsg("Mirror: ")
        
        if not self.selmols:
            msg = redmsg("No selected chunks to mirror")
            env.history.message(cmd + msg)
            return
        self.changed()
        
        jigs = self.assy.getSelectedJigs()
        
        for m in self.selmols:
            mirrorChunk = m.copy(None) #ninad060812 make a copy of the selection first
            self.o.assy.addmol(mirrorChunk)
            mirrorChunk.stretch(-1.0)
            self.mirrorAxis = jigs[0].getaxis() # ninad060812 Get the axis vector of the Grid Plane. Then you need to 
                                                               #rotate the inverted chunk by pi around this axis vector 
            mirrorChunk.rot(Q(self.mirrorAxis, pi)) 

            self.mirrorDistance, self.wid = orthodist(m.center, self.mirrorAxis, jigs[0].center) # ninad060813 This gives an orthogonal distance between 
                                                                                                                        #the chunk center and mirror plane. 
            
            mirrorChunk.move(2*(self.mirrorDistance)*self.mirrorAxis)# @@@@ ninad060813 This moves the mirrror chunk on the other side of the mirror plane. It surely moves the chunk along the axis of the mirror plane but I am still unsure if this *always* moves the chunk on the other side of the mirror. Probably the 'orthodist' function has helped me here??  Need to discuss this.
                                                                                                    
            #older implementation (if it is to be mirrored about YZ axis)
            #mirrorChunk.rot(Q(V(1,0,0), pi)) #ninad060812 rotate the inverted chunk by 180 degrees about X axis 
            
        self.w.win_update()  # update GLPane as well as MT
        
        info = fix_plurals( "Mirrored  %d chunk(s)" % len(self.selmols)) # see item 5 in known bugs ninad060812
        env.history.message( cmd + info)
        env.end_op(mc) 
        
    
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