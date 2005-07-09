# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
GroundProp.py

$Id$
"""

from qt import *
from GroundPropDialog import *
from VQT import V

class GroundProp(GroundPropDialog):
    def __init__(self, ground, glpane):

        GroundPropDialog.__init__(self)
        self.ground = ground
        self.glpane = glpane
        self.setup()

    def setup(self):
        ground = self.ground
        
        self.originalColor = self.ground.normcolor

        self.nameLineEdit.setText(self.ground.name)

        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(ground.normcolor[0]*255), 
                         int(ground.normcolor[1]*255), 
                         int(ground.normcolor[2]*255)))

    def choose_color(self):

        color = QColorDialog.getColor(
            QColor(int(self.ground.normcolor[0]*255), 
                         int(self.ground.normcolor[1]*255), 
                         int(self.ground.normcolor[2]*255)),
                         self, "ColorDialog")
                        
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.ground.color = self.ground.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.gl_update()

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)
	    self.ground.color = self.ground.normcolor = self.originalColor
	    self.glpane.gl_update()

    #################
    # OK Button
    #################
    def accept(self):
        QDialog.accept(self)
        
        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.ground.name = str(text)
        
        self.ground.assy.w.win_update() # Update model tree
        self.ground.assy.changed()