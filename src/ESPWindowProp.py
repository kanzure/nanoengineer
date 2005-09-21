# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ESPWindowPropDialog

$Id$
"""

from qt import *
from ESPWindowPropDialog import *

class ESPWindowProp(ESPWindowPropDialog):
    def __init__(self, esp_window, glpane):

        ESPWindowPropDialog.__init__(self)
        self.esp_window = esp_window
        self.glpane = glpane
        self.setup()
    
    def setup(self):
        self.oldNormColor = self.esp_window.normcolor
        self.oldBorderColor = self.esp_window.border_color
        
        self.name_linedit.setText(self.esp_window.name)
        
        self.fill_color = QColor(int(self.esp_window.normcolor[0]*255), 
                         int(self.esp_window.normcolor[1]*255), 
                         int(self.esp_window.normcolor[2]*255))
        
        self.border_color = QColor(int(self.esp_window.border_color[0]*255), 
                         int(self.esp_window.border_color[1]*255), 
                         int(self.esp_window.border_color[2]*255))
        
        self.width_spinbox.setValue(self.esp_window.width)
        self.resolution_spinbox.setValue(self.esp_window.resolution)
        
        self.fill_color_pixmap.setPaletteBackgroundColor(self.fill_color)
        self.border_color_pixmap.setPaletteBackgroundColor(self.border_color)
        
    def change_fill_color(self):
        '''Slot method to change fill color.'''
        color = QColorDialog.getColor(self.fill_color, self, "ColorDialog")

        if color.isValid():
            self.fill_color_pixmap.setPaletteBackgroundColor(color)
            self.esp_window.color = self.esp_window.normcolor = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
            
    def change_border_color(self):
        '''Slot method change border color.'''
        color = QColorDialog.getColor(self.border_color, self, "ColorDialog")

        if color.isValid():
            self.border_color_pixmap.setPaletteBackgroundColor(color)
            self.esp_window.border_color = (color.red()/255.0, color.green()/255.0, color.blue()/255.0)
            
    def change_width(self):
        "Slot for Width spinbox"
        self.esp_window.width = float(self.width_spinbox.value())
        self.glpane.gl_update()
        
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
        self.esp_window.color = self.esp_window.normcolor = self.oldNormColor 
        self.esp_window.border_color = self.oldBorderColor  
 
        self.glpane.gl_update()
        
        QDialog.reject(self)