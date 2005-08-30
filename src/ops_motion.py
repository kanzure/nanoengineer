# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_motion.py -- various ways of moving or spatially distorting
selected atoms or chunks (and someday, attached jigs).
These operations don't create or destroy atoms or bonds.

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.
"""

from HistoryWidget import greenmsg, redmsg
from platform import fix_plurals
from VQT import V, norm, Q

class ops_motion_Mixin:
    "Mixin class for providing these methods to class Part"
    
    ###@@@ move/rot should be extended to apply to jigs too (and fit into some naming convention)
    
    def movesel(self, offset):
        "move selected chunks in space"
        for mol in self.selmols:
            self.changed()
            mol.move(offset)
 
    def rotsel(self, quat):
        "rotate selected chunks in space"
        for mol in self.selmols:
            self.changed()
            mol.rot(quat)

    #stretch a molecule
    def Stretch(self):
        
        cmd = greenmsg("Stretch: ")
        
        if not self.selmols:
            msg =  redmsg("No selected chunks to stretch")
            self.w.history.message(cmd + msg)
            return
        self.changed()
        for m in self.selmols:
            m.stretch(1.1)
        self.o.gl_update()
        
        # Added history message.  Mark 050413.
        info = fix_plurals( "Stretched %d chunk(s)" % len(self.selmols))
        self.w.history.message( cmd + info)

    #invert a chunk
    def Invert(self):
        '''Invert the atoms of the selected chunk(s)'''
        
        cmd = greenmsg("Invert: ")
        
        if not self.selmols:
            msg = redmsg("No selected chunks to invert")
            self.w.history.message(cmd + msg)
            return
        self.changed()
        for m in self.selmols:
            m.stretch(-1.0)
        self.o.gl_update()
        
        info = fix_plurals( "Inverted %d chunk(s)" % len(self.selmols))
        self.w.history.message( cmd + info)
    
    def align(self):
        
        cmd = greenmsg("Align to Common Axis: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            self.w.history.message(cmd + msg)
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
        self.w.history.message( cmd + info)
        
    def alignmove(self):
        
        cmd = greenmsg("Move to Axis: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            self.w.history.message(cmd + msg)
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
        self.w.history.message( cmd + info)
        
    pass # end of class ops_motion_Mixin

# end