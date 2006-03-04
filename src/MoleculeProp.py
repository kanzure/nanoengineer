# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
MoleculeProp.py

$Id$
"""

from qt import *
from constants import *
from MoleculePropDialog import *

nocolor = QColor(230,231,230) # needed by colortile and colorchooser

class MoleculeProp(MoleculePropDialog):
    def __init__(self, mol):
        MoleculePropDialog.__init__(self)
        self.mol = mol
        self.setup()

    def setup(self):
        mol = self.mol
        
        self.originalColor = mol.color # Save original molecule color in case of cancel
        
        self.nameLineEdit.setText(mol.name)
        
        if mol.color: # Set colortile to mol color (without border)
            self.colorPixmapLabel.setPaletteBackgroundColor(
                QColor(int(mol.color[0]*255), 
                             int(mol.color[1]*255), 
                             int(mol.color[2]*255)))
            self.colorPixmapLabel.setFrameShape(QFrame.NoFrame)
        else: # Set the colortile to the dialog's bg color (no color), with a box (border)
            self.colorPixmapLabel.setPaletteBackgroundColor(self.paletteBackgroundColor())
            self.colorPixmapLabel.setFrameShape(QFrame.Box)
        
        # Create text for chunk info.
        self.atomsTextBrowser.setReadOnly(True)
        chunkInfoText = ""
        natoms = len(mol.atoms) # number of atoms in the chunk
        
        # Determining the number of element types in this molecule.
        ele2Num = {}
        for a in mol.atoms.itervalues():
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
        header = "Total Atoms: " + str(natoms) + "\n\n"
        
        # Display chunk info in a textbrowser in the dialog window.      
        self.atomsTextBrowser.setText(header + chunkInfoText)

    #########################
    # Change molecule color
    #########################
    def choose_color(self):
        
        if self.mol.color: 
            color = QColorDialog.getColor(
                QColor(int(self.mol.color[0]*255), 
                            int(self.mol.color[1]*255), 
                            int(self.mol.color[2]*255)),
                            self, "ColorDialog")
        else:
            color = QColorDialog.getColor(self.paletteBackgroundColor(), self, "ColorDialog")

        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.colorPixmapLabel.setFrameShape(QFrame.NoFrame)
            self.mol.color = color.red()/255.0, color.green()/255.0, color.blue()/255.0
            self.mol.setcolor(self.mol.color)
            self.mol.glpane.gl_update()

    def reset_chunk_color(self):
        if not self.mol.color: return
        self.colorPixmapLabel.setPaletteBackgroundColor(nocolor)
        self.colorPixmapLabel.setFrameShape(QFrame.Box)
        self.mol.color = None
        self.mol.setcolor(self.mol.color)
        self.mol.glpane.gl_update()
        
    def make_atoms_visible(self):
        '''Makes any atoms in this chunk visible.
        '''
        self.mol.show_invisible_atoms()
        self.mol.glpane.gl_update()
        
    def reject(self):
        QDialog.reject(self)
        
        self.mol.color = self.originalColor
        self.mol.setcolor(self.mol.color)
        self.mol.glpane.gl_update()
        
    def accept(self):
        QDialog.accept(self)
        
        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text: self.mol.name = str(text)
        
        self.mol.assy.w.win_update() # Update model tree
        self.mol.assy.changed()