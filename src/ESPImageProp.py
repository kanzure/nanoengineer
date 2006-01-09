# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ESPImagePropDialog

$Id$
"""

from qt import *
from ESPImagePropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf
import copy


class ESPImageProp(ESPImagePropDialog):
    def __init__(self, esp_image, glpane):

        ESPImagePropDialog.__init__(self)
        self.jig = esp_image
        self.glpane = glpane
    
    def setup(self):
        
        #Default state for atoms selection
        self.selected = False        
        
        self.jig_attrs = self.jig.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Jig color
        self.fill_QColor = RGBf_to_QColor(self.jig.fill_color) # Used as default color by Color Chooser
        self.border_QColor = RGBf_to_QColor(self.jig.normcolor) # Used as default color by Color Chooser
        self.fill_color_pixmap.setPaletteBackgroundColor(self.fill_QColor)
        self.border_color_pixmap.setPaletteBackgroundColor(self.border_QColor)
        
        self.name_linedit.setText(self.jig.name)
        self.width_linedit.setText(str(self.jig.width))
        self.image_offset_linedit.setText(str(self.jig.image_offset))
        self.edge_offset_linedit.setText(str(self.jig.edge_offset))
        self.resolution_spinbox.setValue(self.jig.resolution)
        
        self.show_esp_bbox_checkbox.setChecked(self.jig.show_esp_bbox)
        
        opacity = '%1.2f ' % self.jig.opacity
        self.opacity_linedit.setText(opacity)
        self.opacity_slider.setValue(int (self.jig.opacity * 100))
        
        self.highlight_atoms_in_bbox_checkbox.setChecked(self.jig.highlightChecked)
        self._updateSelectButtonText()
        
        self.xaxis_spinbox.setValue(self.jig.xaxis_orient)
        self.yaxis_spinbox.setValue(self.jig.yaxis_orient)
        
        self.png_fname_linedit.setText(self.jig.espimage_file)
        
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
    
    def change_jig_size(self, gl_update=True):
        '''Slot method to change the jig's length, radius and/or spoke radius.'''
        self.jig.width = float(str(self.width_linedit.text()))
        self.jig.image_offset = float(str(self.image_offset_linedit.text()))
        self.jig.edge_offset = float(str(self.edge_offset_linedit.text()))
        if gl_update:
            self.glpane.gl_update()
            
    def change_opacity(self, val):
        '''Slot for opacity slider '''
        self.jig.opacity = val/100.0
        opacity = '%1.2f ' % self.jig.opacity
        self.opacity_linedit.setText(opacity)
        self.glpane.gl_update()
        
    def show_esp_bbox(self, val):
        "Slot for Show ESP Image Volume checkbox"
        self.jig.show_esp_bbox = val
        self.glpane.gl_update()
    
    def highlight_atoms_in_bbox(self, val):
        "Slot for Highlight Atoms Inside Volume checkbox"
        self.jig.highlightChecked = val
        self.glpane.gl_update()
    
    def _updateSelectButtonText(self):
        if self.selected:
            self.select_atoms_btn.setText("Deselect Atoms Inside Volume")
        else:
            self.select_atoms_btn.setText("Select Atoms Inside Volume")
            
    def select_atoms_inside_esp_bbox(self):
        "Slot for Select Atoms Inside Volume button, which selects all the atoms inside the bbox"
        self.selected = not self.selected
        self._updateSelectButtonText()
        self.jig.pickSelected(self.selected)
        self.glpane.gl_update()
        
    def calculate_esp(self):
        self.jig.calculate_esp()
        
    def load_esp_image(self):
        self.jig.load_esp_image()
        self.png_fname_linedit.setText(self.jig.espimage_file)
        
    def change_esp_image(self):
        self.jig.load_esp_image(choose_new_image = True)
        self.png_fname_linedit.setText(self.jig.espimage_file)
        
    def clear_esp_image(self):
        self.jig.clear_esp_image()
        
    def change_xaxisOrient(self, val):
        self.jig.xaxis_orient = val
        
    def change_yaxisOrient(self, val):
        self.jig.yaxis_orient = val
    
    def rotate_90(self):
        '''CCW rotate 90 degrees. '''
        self.jig.rotate_esp_image(90)
        
        
    def rotate_neg_90(self):
        '''CW rotate 90 degrees. '''
        self.jig.rotate_esp_image(-90)
        
        
    def flip_esp_image(self):
        '''Flip esp image. '''
        self.jig.flip_esp_image()
      
        
    def mirror_esp_image(self):
        '''Mirror esp image. '''
        self.jig.mirror_esp_image()
    
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.jig.cancelled = False   
        self.jig.try_rename(self.name_linedit.text())
        self.change_jig_size(gl_update=False)
        self.jig.resolution = float(self.resolution_spinbox.value())
        
        # Before exit the dialog, turn off the highlighting and selection
        #self.jig.highlightChecked = False # Let's try leaving highlighted atoms on.  It's useful.  Mark 051004.
        self.jig.pickSelected(False)
                
        self.jig.assy.w.win_update() # Update model tree
        self.jig.assy.changed()
        
        QDialog.accept(self)
        

    def reject(self):
        '''Slot for the 'Cancel' button '''
        self.jig.attr_update(self.jig_attrs) # Restore attributes of the jig.
        # Before exit the dialog, turn off the highlighting and selection
        self.jig.highlightChecked = False
        self.jig.pickSelected(False)
        
        self.glpane.gl_update()
        
        QDialog.reject(self)