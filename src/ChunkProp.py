# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
ChunkProp.py

$Id$

History: Original code from MoleculeProps.py and cleaned up by Mark.

"""

__author__ = "Mark"

from qt import *
from constants import *
from ChunkPropDialog import *
from widgets import RGBf_to_QColor, QColor_to_RGBf

class ChunkProp(ChunkPropDialog):
    def __init__(self, chunk):
        ChunkPropDialog.__init__(self)
        self.chunk = chunk
        self.glpane = chunk.glpane
        self.setup()

    def setup(self):
        
        # Chunk color
        self.original_color = self.chunk.color # Save original Chunk color in case of Cancel
        
        if self.chunk.color: # Set colortile to chunk color (without border)
            self.chunk_QColor = RGBf_to_QColor(self.chunk.color) # Used as default color by Color Chooser
        else: # Set the colortile to the dialog's bg color (no color)
            self.chunk_QColor = self.paletteBackgroundColor()
        self.chunk_color_frame.setPaletteBackgroundColor(self.chunk_QColor)

        self.nameLineEdit.setText(self.chunk.name)
        
        self.atomsTextBrowser.setText(self.get_chunk_props_info())
        
    def get_chunk_props_info(self):
        "Return chunk properties information."
        
        self.atomsTextBrowser.setReadOnly(True)
        chunkInfoText = ""
        natoms = len(self.chunk.atoms) # number of atoms in the chunk
        
        # Determining the number of element types in this Chunk.
        ele2Num = {}
        for a in self.chunk.atoms.itervalues():
             if not ele2Num.has_key(a.element.symbol): ele2Num[a.element.symbol] = 1 # New element found
             else: ele2Num[a.element.symbol] += 1 # Increment element
        
        # String construction for each element to be displayed.
        nsinglets = 0        
        for item in ele2Num.iteritems():
            if item[0] == "X":  # It is a Singlet
                nsinglets = int(item[1])
                continue
            else: eleStr = item[0] + ": " + str(item[1]) + "\n"
            chunkInfoText += eleStr
            
        if nsinglets:
            eleStr = "\nBondpoints: " + str(nsinglets) + "\n"
            chunkInfoText += eleStr
         
        natoms -= nsinglets   
        header = "Total Atoms: " + str(natoms) + "\n"
        
        return header + chunkInfoText
            
    def change_chunk_color(self):
        '''Slot method to change the chunk's color.'''
        color = QColorDialog.getColor(self.chunk_QColor, self, "ColorDialog")

        if color.isValid():
            self.chunk_color_frame.setPaletteBackgroundColor(color)
            self.chunk_QColor = color
            self.chunk.color = QColor_to_RGBf(color)
            self.chunk.setcolor(self.chunk.color)
            if self.chunk.hidden: # A hidden chunk has no glpane attr.
                return
            self.glpane.gl_update()

    def reset_chunk_color(self):
        '''Slot method to reset the chunk's color.'''
        if not self.chunk.color: return
        self.chunk_QColor = self.paletteBackgroundColor()
        self.chunk_color_frame.setPaletteBackgroundColor(self.chunk_QColor)
        self.chunk.color = None
        self.chunk.setcolor(self.chunk.color)
        if self.chunk.hidden: # A hidden chunk has no glpane attr.
                return
        self.glpane.gl_update()
    
    def make_atoms_visible(self):
        '''Makes any atoms in this chunk visible.
        '''
        self.chunk.show_invisible_atoms()
        if self.chunk.hidden: # A hidden chunk has no glpane attr.
                return
        self.glpane.gl_update()
        
    def accept(self):
        '''Slot for the 'OK' button '''
        self.chunk.try_rename(self.nameLineEdit.text())
        self.chunk.assy.w.win_update() # Update model tree
        self.chunk.assy.changed()
        
        QDialog.accept(self)
        
    def reject(self):
        '''Slot for the 'Cancel' button '''
        
        self.chunk.color = self.original_color
        self.chunk.setcolor(self.chunk.color)

        QDialog.reject(self)
        
        # A hidden chunk has no glpane attr.  This fixes bug 1137.  Mark 051126.
        if self.chunk.hidden:
            return
            
        self.glpane.gl_update()