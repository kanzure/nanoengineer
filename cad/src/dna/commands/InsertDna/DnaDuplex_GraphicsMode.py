# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplex_GraphicsMode.py

Graphics mode class for creating a dna duplex by specifying two line end 
points. The duplex can be created on a specified plane or parallel to screen
    
@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created on 2008-06-24

TODO:
- 2008-06-24: See  DnaOrCntPropertyManager class for a detailed to do comment regarding 
the tool that allows user to specify a drawing plane. 
"""
from PyQt4.Qt import Qt

from dna.temporary_commands.DnaLineMode import DnaLine_GM
from graphics.drawing.drawDnaLabels import draw_dnaBaseNumberLabels

_superclass = DnaLine_GM
class DnaDuplex_GraphicsMode(DnaLine_GM):
    """
    Graphics mode class for creating a dna duplex by specifying two line end 
    points. The duplex can be created on a specified plane or parallel to screen
    @see: Line_GraphicsMode.bareMotion()
    @see: Line_GraphicsMode.leftDown()
    @see: DnaLine_GM.leftUp()
    """  
    
    def _drawLabels(self):
        """
        Overrides suoerclass method.
        @see: GraphicsMode._drawLabels()
        """
        _superclass._drawLabels(self)
        draw_dnaBaseNumberLabels(self.glpane)
        
        
    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """         
        
        _superclass.update_cursor_for_no_MB(self)
        
        if self.isSpecifyPlaneToolActive():
            self.o.setCursor(self.win.specifyPlaneCursor)
                       
    
    def keyPressEvent(self, event):
        """
        Handles keyPressEvent. Overrides superclass method. If delete key 
        is pressed while the focus is inside the PM list widget, it deletes
        that list widget item.
        @see: ListWidgetItems_PM_Mixing.listWidgetHasFocus()
        @see: DnaDuplexPropertyManager.listWidgetHasFocus()
        """
        if event.key() == Qt.Key_Delete:
            if self.command.listWidgetHasFocus():
                self.command.removeListWidgetItems()
                return            

        _superclass.keyPressEvent(self, event)
                
    def jigLeftUp(self, j, event):
        """
        Overrides superclass method See that method for more details. 
        
        Additional things it does: If the jig is a Plane and if Specify reference 
        plane tool is enabled (from the Property manager), this method updates 
        the 'drawing plane' on which the dna duplex will be created. 
        
        @see: Select_graphicsmode_MouseHelpers_preMixin.jigLeftUp()
        @see: self.self.isSpecifyPlaneToolActive() 
        """
        if self.isSpecifyPlaneToolActive() and self.glpane.modkeys is None:
            if isinstance(j, self.win.assy.Plane):
                self.command.updateDrawingPlane(j)                
            return 
        
        _superclass.jigLeftUp(self, j, event)
                
        
    def isSpecifyPlaneToolActive(self):
        """
        Overrides superclass method. Delegates this job to self.command. 
        @see: DnaDuplex_EditCommand.isSpecifyPlaneToolActive()
        @see: DnaDuplexPropertyManager.isSpecifyPlaneToolActive()
        @see: self.jigLeftUp()
        """
        if self.command:
            return self.command.isSpecifyPlaneToolActive()
        
        return False
    
        
    def getDrawingPlane(self):
        """
        Overridden in subclasses. 
        
        Returns the reference plane on which the line will be drawn.
        The default immplementation returns None.
        @see: DnaDuplex_EditCommand.useSpecifiedDrawingPlane()
        @see: Line_GraphicsMode.bareMotion()
        @see: Line_GraphicsMode.leftDown()
        """
        if self.command.useSpecifiedDrawingPlane():
            return self.plane 
        else:
            return None
          
    
            
    
