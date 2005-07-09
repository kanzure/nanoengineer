# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
StatProp.py

$Id$
"""

from qt import *
from StatPropDialog import *
from VQT import V

class StatProp(StatPropDialog):
    def __init__(self, stat, glpane):

        StatPropDialog.__init__(self)
        self.stat = stat
        self.glpane = glpane
        self.setup()

    def setup(self):
        stat = self.stat
        
        self.originalColor = self.stat.normcolor
        
        self.nameLineEdit.setText(stat.name)
        self.molnameLineEdit.setText(stat.atoms[0].molecule.name) #bruce 050210 replaced obs .mol attr
        self.tempSpinBox.setValue(int(stat.temp))

        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(stat.normcolor[0]*255), 
                         int(stat.normcolor[1]*255), 
                         int(stat.normcolor[2]*255)))
        
    def choose_color(self):

        color = QColorDialog.getColor(
            QColor(int(self.stat.normcolor[0]*255), 
                         int(self.stat.normcolor[1]*255), 
                         int(self.stat.normcolor[2]*255)),
                         self, "ColorDialog")
                        
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.stat.color = self.stat.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.gl_update()

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)
	    self.stat.color = self.stat.normcolor = self.originalColor
	    self.glpane.gl_update()

    #################
    # OK Button
    #################
    def accept(self):
        QDialog.accept(self)
        
        self.stat.temp = self.tempSpinBox.value()
        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.stat.name = str(text)
        
        self.stat.assy.w.win_update() # Update model tree
        self.stat.assy.changed()