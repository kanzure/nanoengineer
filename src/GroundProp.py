# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from GroundPropDialog import *
from VQT import V

class GroundProp(GroundPropDialog):
    def __init__(self, ground, glpane):

        GroundPropDialog.__init__(self)
        self.ground = ground
        self.glpane = glpane
        self.setup()

    def setup(self):
        ground = self.ground
        
        self.ground.originalColor = self.ground.normcolor
        
        self.nameLineEdit.setText(ground.name)

        self.colorPixmapLabel.setPaletteBackgroundColor(
            QColor(int(ground.normcolor[0]*255), 
                         int(ground.normcolor[1]*255), 
                         int(ground.normcolor[2]*255)))

        strList = map(lambda i: ground.atoms[i].element.symbol + str(i),
                                                range(0, len(ground.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)

        self.applyPushButton.setEnabled(False)
        

    #########################
    # Change linear ground color
    #########################
    def changeGroundColor(self):

        color = QColorDialog.getColor(
            QColor(int(self.ground.normcolor[0]*255), 
                         int(self.ground.normcolor[1]*255), 
                         int(self.ground.normcolor[2]*255)),
                         self, "ColorDialog")
                        
        if color.isValid():
            self.colorPixmapLabel.setPaletteBackgroundColor(color)
            self.ground.color = self.ground.normcolor = (color.red() / 255.0, color.green() / 255.0, color.blue() / 255.0)
            self.glpane.paintGL()


    #################
    # OK Button
    #################
    def accept(self):
        self.applyButtonPressed()
        QDialog.accept(self)

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)
	    self.ground.normcolor = self.ground.originalColor

    #################
    # Apply Button
    #################	
    def applyButtonPressed(self):
        
        self.ground.name = self.nameLineEdit.text()

        self.applyPushButton.setEnabled(False)
	
    def propertyChanged(self):
        self.applyPushButton.setEnabled(True)	