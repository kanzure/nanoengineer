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

        strList = map(lambda i: ground.atoms[i].element.symbol + str(i),
                                                range(0, len(ground.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)

    #########################
    # Change ground color
    #########################
    def changeGroundColor(self):
        color = QColorDialog.getColor(QColor("linen"), self, "ColorDialog")
        self.colorPixmapLabel.setPaletteBackgroundColor(color)
        
        self.ground.molecule.havelist = 0
        self.ground.color = color
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