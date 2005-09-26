# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ESPWindowPropDialog

$Id$
"""

from qt import *
from ESPWindowPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf

class ESPWindowProp(ESPWindowPropDialog):
    def __init__(self, esp_window, glpane):

        ESPWindowPropDialog.__init__(self)
        self.esp_window = esp_window
        self.glpane = glpane
        self.setup()
    
    def setup(self):
        self.oldNormColor = self.esp_window.normcolor # Border color
        self.oldFillColor = self.esp_window.fill_color
        
        self.name_linedit.setText(self.esp_window.name)
        
        self.fill_color = RGBf_to_QColor(self.esp_window.fill_color)
        self.border_color = RGBf_to_QColor(self.esp_window.normcolor)
        
        self.width_spinbox.setValue(self.esp_window.width)
        self.window_offset_spinbox.setValue(self.esp_window.window_offset)
        self.edge_offset_spinbox.setValue(self.esp_window.edge_offset)
        self.resolution_spinbox.setValue(self.esp_window.resolution)
        
        self.fill_color_pixmap.setPaletteBackgroundColor(self.fill_color)
        self.border_color_pixmap.setPaletteBackgroundColor(self.border_color)
        
    def change_fill_color(self):
        '''Slot method to change fill color.'''
        color = QColorDialog.getColor(self.fill_color, self, "ColorDialog")

        if color.isValid():
            self.fill_color_pixmap.setPaletteBackgroundColor(color)
            self.esp_window.fill_color = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_border_color(self):
        '''Slot method change border color.'''
        color = QColorDialog.getColor(self.border_color, self, "ColorDialog")

        if color.isValid():
            self.border_color_pixmap.setPaletteBackgroundColor(color)
            self.esp_window.color = self.esp_window.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_width(self, val):
        "Slot for Width spinbox"
        self.esp_window.width = float(val)
        self.glpane.gl_update()
        
    def change_window_offset(self, val):
        "Slot for Width spinbox"
        self.esp_window.window_offset = float(val)
        self.glpane.gl_update()
        
    def change_edge_offset(self, val):
        "Slot for Width spinbox"
        self.esp_window.edge_offset = float(val)
        self.glpane.gl_update()
        
    def show_esp_bbox(self, val):
        "Slot for Show ESP Window Volume"
        self.esp_window.show_esp_bbox = val
        self.glpane.gl_update()
        
    def select_atoms_inside_esp_bbox(self):
        "Slot for Select Atoms Inside Volume button, which selects all the atoms inside the bbox"
        print "ESPWindowProp.select_atoms_inside_esp_bbox(): Not implemented yet."
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.esp_window.cancelled = False   
        
        text =  QString(self.name_linedit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.esp_window.name = str(text) 
        
        self.esp_window.width = float(self.width_spinbox.value())
        self.esp_window.resolution = float(self.resolution_spinbox.value())
        
        self.esp_window.assy.w.win_update() # Update model tree
        self.esp_window.assy.changed()
        
        QDialog.accept(self)

    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.esp_window.fill_color = self.oldFillColor 
        self.esp_window.color = self.esp_window.normcolor = self.oldNormColor   # Border color
 
        self.glpane.gl_update()
        
        QDialog.reject(self)