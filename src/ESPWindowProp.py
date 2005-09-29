# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ESPWindowPropDialog

$Id$
"""

from qt import *
from ESPWindowPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf
import copy


class ESPWindowProp(ESPWindowPropDialog):
    def __init__(self, esp_window, glpane):

        ESPWindowPropDialog.__init__(self)
        self.jig = esp_window
        self.glpane = glpane

        self.jig.highlightChecked = False
        self.setup()
        
        self.selected = False        
        
    
    def setup(self):
        
        # Need to ask Bruce about the pros/cons of copying the jig here.  
        # It sure would be nice to use the copy of the jig in self.reject() like this:
        #     self.jig = self.original_jig
        # so I didn't have to copy each attr back when the user hit the Cancel button.  Mark 050929.
        self.original_jig = copy.copy(self.jig) 
        
        # Jig color
        # self.original_normcolor = self.jig.normcolor
        self.fill_QColor = RGBf_to_QColor(self.jig.fill_color) # Used as default color by Color Chooser
        self.border_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.fill_color_pixmap.setPaletteBackgroundColor(self.fill_QColor)
        self.border_color_pixmap.setPaletteBackgroundColor(self.border_QColor)
        
        self.name_linedit.setText(self.jig.name)
        self.width_spinbox.setValue(self.jig.width)
        self.window_offset_spinbox.setValue(self.jig.window_offset)
        self.edge_offset_spinbox.setValue(self.jig.edge_offset)
        self.resolution_spinbox.setValue(self.jig.resolution)
        
        self.show_esp_bbox_checkbox.setChecked(self.jig.show_esp_bbox)
        self.opacity_spinbox.setValue(int(self.jig.opacity*255))
        
        self.highlight_atoms_in_bbox_checkbox.setChecked(self.jig.highlightChecked)
        
        
    def change_fill_color(self):
        '''Slot method to change fill color.'''
        color = QColorDialog.getColor(self.fill_QColor, self, "ColorDialog")

        if color.isValid():
            self.fill_color_pixmap.setPaletteBackgroundColor(color)
            self.fill_QColor = color
            self.jig.fill_color = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_border_color(self):
        '''Slot method change border color.'''
        color = QColorDialog.getColor(self.border_QColor, self, "ColorDialog")

        if color.isValid():
            self.border_color_pixmap.setPaletteBackgroundColor(color)
            self.border_QColor = color
            self.jig.color = self.jig.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()
            
    def change_width(self, val):
        "Slot for Width spinbox"
        self.jig.width = float(val)
        self.glpane.gl_update()
        
    def change_window_offset(self, val):
        "Slot for Width spinbox"
        self.jig.window_offset = float(val)
        self.glpane.gl_update()
        
    def change_edge_offset(self, val):
        "Slot for Width spinbox"
        self.jig.edge_offset = float(val)
        self.glpane.gl_update()
        
    def show_esp_bbox(self, val):
        "Slot for Show ESP Window Volume checkbox"
        self.jig.show_esp_bbox = val
        self.glpane.gl_update()
    
    def opacityChanged(self, val):
        '''Slot for opacity spin box '''
        self.jig.opacity = val/255.0
        self.glpane.gl_update()
        
    def highlight_atoms_in_bbox(self, val):
        "Slot for Highlight Atoms Inside Volume checkbox"
        self.jig.highlightChecked = val
        self.glpane.gl_update()
        
    def select_atoms_inside_esp_bbox(self):
        "Slot for Select Atoms Inside Volume button, which selects all the atoms inside the bbox"
        self.selected = not self.selected
        if self.selected:
            self.select_atoms_btn.setText("Deselect Atoms Inside Volume")
        else:
            self.select_atoms_btn.setText("Select Atoms Inside Volume")
        self.jig.pickSelected(self.selected)
        self.glpane.gl_update()
        
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.cancelled = False   
        
        text =  QString(self.name_linedit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.jig.name = str(text) 
        
        self.jig.width = float(self.width_spinbox.value())
        self.jig.resolution = float(self.resolution_spinbox.value())
        
        #self.glpane.assy.selwhat = self.sel_what
        
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        
        QDialog.accept(self)
        

    def reject(self):
        '''Slot for the 'Cancel' button '''
        
        # Restore the original attribute values from the copied jig.
        self.jig.color = self.jig.normcolor = self.original_jig.normcolor # Border color
        self.jig.fill_color = self.original_jig.fill_color
        self.jig.name = self.original_jig.name
        self.jig.width = self.original_jig.width
        self.jig.window_offset = self.original_jig.window_offset
        self.jig.edge_offset = self.original_jig.edge_offset
        self.jig.resolution = self.original_jig.resolution
        self.jig.show_esp_bbox = self.original_jig.show_esp_bbox
        self.jig.opacity = self.original_jig.opacity

        #self.glpane.assy.selwhat = self.sel_what
        self.glpane.gl_update()
        
        QDialog.reject(self)