# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from GroundPropDialog import *
from VQT import V

class GroundProp(GroundPropDialog):
    def __init__(self, ground, glpane):
        GroundPropDialog.__init__(self)
        self.ground = ground
        self.glpane = glpane

        self.colorPixmapLabel.setPaletteBackgroundColor(ground.color)
        
        self.nameLineEdit.setText(ground.name)
        self.applyPushButton.setEnabled(False)

        strList = map(lambda i: ground.atoms[i].element.symbol + str(i),
                                                range(0, len(ground.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)

    #########################
    # Change ground color
    #########################
    def changeGroundColor(self):
        color = QColorDialog.getColor(QColor(self.ground.color), self, "ColorDialog")
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.ground.color = color
            self.ground.molecule.havelist = 0
            self.glpane.paintGL()

    #################
    # OK Button
    #################
    def accept(self):
        self.ground.name = self.nameLineEdit.text()
        QDialog.accept(self)

    #################
    # Cancel Button
    #################
    def reject(self):
        QDialog.reject(self)
        
    
    ########################
    # Properties change slot function
    ########################
    def propertiesChanged(self):
         self.applyPushButton.setEnabled(True)
          
    ########################
    # Properties change slot function
    ########################
    def applyButtonPressed(self):
         self.ground.name = self.nameLineEdit.text()   
         self.applyPushButton.setEnabled(False)