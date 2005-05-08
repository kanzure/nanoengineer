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
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to stretch")) #bruce 050131
            return
        self.changed()
        for m in self.selmols:
            m.stretch(1.1)
        self.o.gl_update()
        
        # Added history message.  Mark 050413.
        info = fix_plurals( "stretched %d chunk(s)" % len(self.selmols))
        self.w.history.message( info)

    #invert a chunk
    def Invert(self):
        '''Invert the atoms of the selected chunk(s)'''
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to invert"))
            return
        self.changed()
        for m in self.selmols:
            m.stretch(-1.0)
        self.o.gl_update()
        
        from platform import fix_plurals
        info = fix_plurals( "inverted %d chunk(s)" % len(self.selmols))
        self.w.history.message( info)
    
    def align(self):
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("need two or more selected chunks to align")) #bruce 050131
            return
        self.changed() #bruce 050131 bugfix or precaution
        ax = V(0,0,0)
        for m in self.selmols:
            ax += m.getaxis()
        ax = norm(ax)
        for m in self.selmols:
            m.rot(Q(m.getaxis(),ax))
        self.o.gl_update()

    pass # end of class ops_motion_Mixin

# end
