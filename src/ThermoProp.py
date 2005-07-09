# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ThermoProp.py

$Id$
"""

from qt import *
from ThermoPropDialog import *
from VQT import V

class ThermoProp(ThermoPropDialog):
    def __init__(self, thermo, glpane):

        ThermoPropDialog.__init__(self)
        self.thermo = thermo
        self.glpane = glpane
        self.setup()

    def setup(self):
        thermo = self.thermo
        
        self.originalColor = self.thermo.normcolor
        
        self.nameLineEdit.setText(thermo.name)
        self.molnameLineEdit.setText(thermo.atoms[0].molecule.name) #bruce 050210 replaced obs .mol attr

        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(thermo.normcolor[0]*255), 
                         int(thermo.normcolor[1]*255), 
                         int(thermo.normcolor[2]*255)))

    def choose_color(self):

        color = QColorDialog.getColor(
            QColor(int(self.thermo.normcolor[0]*255), 
                         int(self.thermo.normcolor[1]*255), 
                         int(self.thermo.normcolor[2]*255)),
                         self, "ColorDialog")
                        
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.thermo.color = self.thermo.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.gl_update()

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)
	    self.thermo.color = self.thermo.normcolor = self.originalColor
	    self.glpane.gl_update()

    #################
    # OK Button
    #################
    def accept(self):
        QDialog.accept(self)

        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.thermo.name = str(text)
        
        self.thermo.assy.w.win_update() # Update model tree
        self.thermo.assy.changed()