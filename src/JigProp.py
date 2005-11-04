# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
JigProp.py

$Id$

History: Original code from GroundProps.py and cleaned up by Mark.

"""

__author__ = "Mark"

from qt import *
from JigPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf

# This Jig Property dialog and its slot methods can be used for any simple jig
# that has only a name and a color attribute changable by the user.  It is currently
# used by both the Anchor and AtomSet jig.  Mark 050928.
        
class JigProp(JigPropDialog):
    def __init__(self, jig, glpane):

        JigPropDialog.__init__(self)
        
        # Set Dialog caption based on the jig type.
        self.setCaption( jig.__class__.__name__ + " Properties")
            
        self.jig = jig
        self.glpane = glpane

    def setup(self):
        '''Initializes the dialog and it's widgets '''
        
        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Jig color
        self.jig_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.jig_color_pixmap.setPaletteBackgroundColor(self.jig_QColor)

        # Jig name
        self.nameLineEdit.setText(self.jig.name)

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
        self.jig.try_rename(self.nameLineEdit.text())
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)