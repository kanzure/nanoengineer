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
        self.grid_plane = gridPlane
        self.glpane = glpane
       
        self.setup()
    
    
    def setup(self):
        
        self.oldGridColor = self.grid_plane.grid_color # Grid color
        self.oldBorderColor = self.grid_plane.normcolor # The normal border color, not the highlight color.
        self.x_spacing = 2
        
        self.name_linedit.setText(self.grid_plane.name)
        
        self.grid_color = QColor(int(self.grid_plane.grid_color[0]*255), 
                         int(self.grid_plane.grid_color[1]*255), 
                         int(self.grid_plane.grid_color[2]*255))
        
        self.border_color = QColor(int(self.grid_plane.normcolor[0]*255), 
                         int(self.grid_plane.normcolor[1]*255), 
                         int(self.grid_plane.normcolor[2]*255))
        
        self.width_spinbox.setValue(self.grid_plane.width)
        self.height_spinbox.setValue(self.grid_plane.height)
        self.x_spacing_spinbox.setValue(self.grid_plane.x_spacing)
        self.y_spacing_spinbox.setValue(self.grid_plane.y_spacing)

        self.border_color_pixmap.setPaletteBackgroundColor(self.border_color)
        self.grid_color_pixmap.setPaletteBackgroundColor(self.grid_color)

        
    def change_border_color(self):
        '''Slot for changing border color.'''
        color = QColorDialog.getColor(self.border_color, self, "ColorDialog")

        if color.isValid():
            self.border_color_pixmap.setPaletteBackgroundColor(color)
            self.grid_plane.color = self.grid_plane.normcolor = \
                    (color.red()/255.0, color.green()/255.0, color.blue()/255.0)

            
    def change_grid_color(self):
        '''Slot for changing grid color'''
        color = QColorDialog.getColor(self.grid_color, self, "ColorDialog")

        if color.isValid():
            self.grid_color_pixmap.setPaletteBackgroundColor(color)
            self.grid_plane.grid_color = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
            
    def change_width(self):
        "Slot for Width spinbox"
        self.grid_plane.width = float(self.width_spinbox.value())
        self.glpane.gl_update()
        
    def change_height(self):
        "Slot for Height spinbox"
        self.grid_plane.height = float(self.height_spinbox.value())
        self.glpane.gl_update()
        
    def change_x_spacing(self):
        "Slot for X Spacing spinbox"
        self.grid_plane.x_spacing = float(self.x_spacing_spinbox.value())
        self.glpane.gl_update()
        
    def change_y_spacing(self):
        "Slot for Y Spacing spinbox"
        self.grid_plane.y_spacing = float(self.y_spacing_spinbox.value())
        self.glpane.gl_update()
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.grid_plane.cancelled = False   
        
        text =  QString(self.name_linedit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.grid_plane.name = str(text) 
        
        self.grid_plane.width = float(self.width_spinbox.value())
        self.grid_plane.height = float(self.height_spinbox.value())
        self.grid_plane.x_spacing = float(self.x_spacing_spinbox.value())
        self.grid_plane.y_spacing = float(self.y_spacing_spinbox.value())
        
        self.grid_plane.assy.w.win_update() # Update model tree
        self.grid_plane.assy.changed()
        
        QDialog.accept(self)
        
        
            
#    def accept(self):
#        '''Slot method for the 'Ok' button '''
#        self.plane.cancelled = False    
        
#        self.plane.width = float(str(self.wdLineEdit.text()))
#        self.plane.height = float(str(self.htLineEdit.text()))
#        self.plane.gridW = float(str(self.uwLineEdit.text()))
#        self.plane.gridH = float(str(self.uhLineEdit.text()))
        
#        self.plane.assy.w.win_update() # Update model tree
#        self.plane.assy.changed()
        
#        QDialog.accept(self)
        
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        
        # Need to restore width, height, spacing, etc., too.
        
        self.grid_plane.grid_color = self.grid_plane.normcolor = self.oldGridColor 
        self.grid_plane.color = self.oldBorderColor  
 
        self.glpane.gl_update()
        
        QDialog.reject(self)
            
#    def reject(self):
#        self.plane.color = self.plane.normcolor = self.oldNormColor 
#        self.plane.gridColor = self.oldGridColor  
 
#        self.glpane.gl_update()
        
#        QDialog.reject(self)
        