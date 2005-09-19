# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ESPWindowPropDialog

$Id$
"""

from qt import *
from ESPWindowPropDialog import *

class ESPWindowProp(ESPWindowPropDialog):
    def __init__(self, gridPlane, glpane):

        ESPWindowPropDialog.__init__(self)
        self.plane = gridPlane
        self.glpane = glpane
       
        self.setup()
    
    
    def setup(self):
        self.oldNormColor = self.plane.normcolor
        self.oldGridColor = self.plane.gridColor
                
        self.planeColor = QColor(int(self.plane.normcolor[0]*255), 
                         int(self.plane.normcolor[1]*255), 
                         int(self.plane.normcolor[2]*255))
        self.gridColor = QColor(int(self.plane.gridColor[0]*255), 
                         int(self.plane.gridColor[1]*255), 
                         int(self.plane.gridColor[2]*255))
        
        self.wdLineEdit.setText(str(self.plane.width))
        self.resolutionLineEdit.setText(str(self.plane.resolution))
        
        self.planeColorButton.setPaletteBackgroundColor(self.planeColor)
        self.gridColorButton.setPaletteBackgroundColor(self.gridColor)

        
    def changePlaneColor(self):
        '''Slot method for change plane color button.'''
        color = QColorDialog.getColor(self.planeColor, self, "ColorDialog")

        if color.isValid():
            self.planeColorButton.setPaletteBackgroundColor(color)
            self.plane.color = self.plane.normalcolor = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)

            
    def changeGridColor(self):
        '''Slot method for change plane color button.'''
        color = QColorDialog.getColor(self.gridColor, self, "ColorDialog")

        if color.isValid():
            self.gridColorButton.setPaletteBackgroundColor(color)
            self.plane.gridColor = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
            
    
    def accept(self):
        '''Slot method for the 'Ok' button '''
        self.plane.cancelled = False    
        
        self.plane.width = float(str(self.wdLineEdit.text()))
        self.plane.resolution = float(str(self.resolutionLineEdit.text()))
        
        self.plane.assy.w.win_update() # Update model tree
        self.plane.assy.changed()
        
        QDialog.accept(self)
        
        
        
    def reject(self):
        self.plane.color = self.plane.normcolor = self.oldNormColor 
        self.plane.gridColor = self.oldGridColor  
 
        self.glpane.gl_update()
        
        QDialog.reject(self)
        