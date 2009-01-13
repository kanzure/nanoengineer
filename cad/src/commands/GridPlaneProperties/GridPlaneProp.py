# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
GridPlaneProp.py

$Id$
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QColorDialog

from commands.GridPlaneProperties.GridPlanePropDialog import Ui_GridPlanePropDialog
from widgets.widget_helpers import RGBf_to_QColor, QColor_to_RGBf, get_widget_with_color_palette

class GridPlaneProp(QDialog, Ui_GridPlanePropDialog):
    def __init__(self, gridPlane, glpane):

        QWidget.__init__(self)
        self.setupUi(self)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.choose_border_color_btn,SIGNAL("clicked()"),self.change_border_color)
        self.connect(self.choose_grid_color_btn,SIGNAL("clicked()"),self.change_grid_color)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.connect(self.x_spacing_spinbox,SIGNAL("valueChanged(int)"),self.change_x_spacing)
        self.connect(self.y_spacing_spinbox,SIGNAL("valueChanged(int)"),self.change_y_spacing)
        self.connect(self.grid_type_combox,SIGNAL("activated(int)"),self.change_grid_type)
        self.connect(self.line_type_combox,SIGNAL("activated(int)"),self.change_line_type)
        self.grid_plane = gridPlane
        self.glpane = glpane

    def setup(self):
        
        self.jig_attrs = self.grid_plane.copyable_attrs_dict() # Save the jig's attributes in case of Cancel.
        
        # Border color
        self.border_color = RGBf_to_QColor(self.grid_plane.normcolor) # Used as default color by Color Chooser
                
        # Grid color
        self.grid_color = RGBf_to_QColor(self.grid_plane.grid_color) # Used as default color by Color Chooser
 
        self.grid_color_pixmap = get_widget_with_color_palette(
            self.grid_color_pixmap, self.grid_color)
        
        self.border_color_pixmap = get_widget_with_color_palette(
            self.border_color_pixmap,self.border_color)
        
        self.name_linedit.setText(self.grid_plane.name)
        
        self.width_spinbox.setValue(self.grid_plane.width)
        self.height_spinbox.setValue(self.grid_plane.height)
        self.x_spacing_spinbox.setValue(self.grid_plane.x_spacing)
        self.y_spacing_spinbox.setValue(self.grid_plane.y_spacing)
        
        self.grid_type_combox.setCurrentIndex(self.grid_plane.grid_type)
        self.line_type_combox.setCurrentIndex(self.grid_plane.line_type)
        
        self._set_xyspacing_enabled(self.grid_plane.grid_type)

        
    def _set_xyspacing_enabled(self, grid_type):
        """
        If <grid_type> == 1, which is SiC type, disable x, y spacing comboBox, otherwise, enable it. 
        """
        from utilities.prefs_constants import SiC_GRID, SQUARE_GRID
        
        if grid_type == SiC_GRID:
            self.x_spacing_spinbox.setEnabled(False)
            self.y_spacing_spinbox.setEnabled(False)
        else:
            self.x_spacing_spinbox.setEnabled(True)
            self.y_spacing_spinbox.setEnabled(True)
        

    def change_grid_type(self, grid_type):
        """
        Slot method to change grid type
        """
        self.grid_plane.grid_type = grid_type
        self._set_xyspacing_enabled(grid_type)
        self.glpane.gl_update()
    
        
    def change_line_type(self, line_type):
        """
        Slot method to change grid line type
        """
        self.grid_plane.line_type = line_type
        self.glpane.gl_update()

        
    def change_grid_color(self):
        """
        Slot method to change grid color.
        """
        color = QColorDialog.getColor(self.grid_color, self)

        if color.isValid():            
            self.grid_color = color
            self.grid_color_pixmap = get_widget_with_color_palette(
            self.grid_color_pixmap, self.grid_color)
            self.grid_plane.grid_color = QColor_to_RGBf(color)
            self.glpane.gl_update()

            
    def change_border_color(self):
        """
        Slot method change border color.
        """
        color = QColorDialog.getColor(self.border_color, self)

        if color.isValid():
            self.border_color = color
            self.border_color_pixmap = get_widget_with_color_palette(
                self.border_color_pixmap,self.border_color)
            self.grid_plane.color = self.grid_plane.normcolor = QColor_to_RGBf(color)
            self.glpane.gl_update()

    def change_width(self, newWidth):
        """
        Slot for Width spinbox
        """
        self.grid_plane.width = float(newWidth)
        self.glpane.gl_update()
        
    def change_height(self, newHeight):
        """
        Slot for Height spinbox
        """
        self.grid_plane.height = float(newHeight)
        self.glpane.gl_update()
        
    def change_x_spacing(self, newXValue):
        """
        Slot for X Spacing spinbox
        """
        self.grid_plane.x_spacing = float(newXValue)
        self.glpane.gl_update()
        
    def change_y_spacing(self, newYValue):
        """
        Slot for Y Spacing spinbox
        """
        self.grid_plane.y_spacing = float(newYValue)
        self.glpane.gl_update()
        
    def accept(self):
        """
        Slot for the 'OK' button 
        """
        self.grid_plane.cancelled = False
        self.grid_plane.try_rename(self.name_linedit.text())
        self.grid_plane.width = float(self.width_spinbox.value())
        self.grid_plane.height = float(self.height_spinbox.value())
        self.grid_plane.x_spacing = float(self.x_spacing_spinbox.value())
        self.grid_plane.y_spacing = float(self.y_spacing_spinbox.value())
        
        self.grid_plane.assy.w.win_update() # Update model tree
        self.grid_plane.assy.changed()
        
        QDialog.accept(self)
        
    def reject(self):
        """
        Slot for the 'Cancel' button 
        """
        self.grid_plane.attr_update(self.jig_attrs) # Restore attributes of the jig.
        self.glpane.gl_update()
        QDialog.reject(self)
