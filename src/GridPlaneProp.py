# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
GridPlaneProp.py

$Id$
"""

from qt import *
from GridPlanePropDialog import *

class GridPlaneProp(GridPlanePropDialog):
    def __init__(self, gridPlane, glpane):

        GridPlanePropDialog.__init__(self)
        self.plane = gridPlane
        self.glpane = glpane
        
        self.setup()
    
    
    def setup(self):
        self.planeColor = QColor(int(self.plane.normcolor[0]*255), 
                         int(self.plane.normcolor[1]*255), 
                         int(self.plane.normcolor[2]*255))
        self.gridColor = QColor(int(self.plane.gridColor[0]*255), 
                         int(self.plane.gridColor[1]*255), 
                         int(self.plane.gridColor[2]*255))
        
        self.wdLineEdit.setText(str(self.plane.width))
        self.htLineEdit.setText(str(self.plane.height))
        self.uwLineEdit.setText(str(self.plane.gridW))
        self.uhLineEdit.setText(str(self.plane.gridH))
        
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
        QDialog.accept(self)
        
        self.plane.cancelled = False    
        
        self.plane.width = float(str(self.wdLineEdit.text()))
        self.plane.height = float(str(self.htLineEdit.text()))
        self.plane.gridW = float(str(self.uwLineEdit.text()))
        self.plane.gridH = float(str(self.uhLineEdit.text()))
        
        self.glpane.gl_update()
        