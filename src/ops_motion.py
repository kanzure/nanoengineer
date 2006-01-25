# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
from VQT import V, norm, Q
import env

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