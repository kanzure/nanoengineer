# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Graphics mode intended to be used while in DnaStrand_EditCommand. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created 2008-02-14

"""
from dna.commands.BuildDna.BuildDna_GraphicsMode import BuildDna_GraphicsMode
from TemporaryCommand import ESC_to_exit_GraphicsMode_preMixin

_superclass = BuildDna_GraphicsMode

class DnaStrand_GraphicsMode(ESC_to_exit_GraphicsMode_preMixin,
                             BuildDna_GraphicsMode):
    
    _handleDrawingRequested = True
    
    def leftUp(self, event):
        """
        Method called during Left up event. 
        """
                
        _superclass.leftUp(self, event)  
        
        self.update_selobj(event)
        self.update_cursor()
        self.o.gl_update()
        
        #Reset the flag that decides whether to draw the handles. This flag is
        #set during left dragging, when no handle is 'grabbed'. See the 
        #class definition for more details about this flag.
        if self.command and self.command.handles:
            if not self._handleDrawingRequested:
                self._handleDrawingRequested = True
        
        #@see: comment in DnaSegment_GraphicsMode.leftUp on why the following 
        #doesn't call command.preview_finialize_structure before calling 
        #command.Done()
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.command.Done()
    
    def Draw(self):
        """
        """
        if self._handleDrawingRequested:
            self._drawHandles()     
        _superclass.Draw(self)
        
    def _drawHandles(self):
        """
        Draw the handles for the command.struct 
        """    
        if self.command and self.command.struct:            
            for handle in self.command.handles:
                handle.draw()
        handleType = ''
        if self.command.grabbedHandle is not None:
            #No handle is grabbed. But may be the structure changed 
            #(e.g. while dragging it ) and as a result, the endPoint positions 
            #are modified. So we must update the handle positions because 
            #during left drag (when handle is not dragged) we skip the 
            #handle drawing code and computation to update the handle positions
            self.command.updateHandlePositions()