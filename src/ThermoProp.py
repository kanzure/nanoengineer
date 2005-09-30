# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ThermoProp.py

$Id$
"""

from qt import *
from ThermoPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf

class ThermoProp(ThermoPropDialog):
    def __init__(self, thermo, glpane):

        ThermoPropDialog.__init__(self)
        self.jig = thermo
        self.glpane = glpane
        self.setup()

    def setup(self):
        
        # Jig color
        self.original_normcolor = self.jig.normcolor 
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        # Jig name
        self.nameLineEdit.setText(self.jig.name)
        
        self.molnameLineEdit.setText(self.jig.atoms[0].molecule.name)
        
    def change_jig_color(self):
        '''Slot method to change the jig's color.'''
        color = QColorDialog.getColor(self.jig_QColor, self, "ColorDialog")

        if color.isValid():
            self.jig_color_pixmap.setPaletteBackgroundColor(color)
            self.jig_QColor = color
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()

    def accept(self):
        '''Slot for the 'OK' button '''
        text =  QString(self.nameLineEdit.text())
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.jig.name = str(text)
        
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.color = self.jig.normcolor = self.original_normcolor
        self.glpane.gl_update()
        QDialog.reject(self)