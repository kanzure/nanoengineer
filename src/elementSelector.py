# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

from ElementSelectorDialog import *
from elementpixmaps import *

#########################################################################
# Declaring tuples

elementSymbol = { 1 : "H", 2 : "He", 
                            5 : "B", 6 : "C" , 7 : "N", 8 : "O", 9 : "F", 10 : "Ne",
                            13 : "Al", 14 : "Si", 15 : "P", 16 : "S", 17 : "Cl" , 18 : "Ar",
                            32 : "Ge", 33 : "As", 34 : "Se", 35 : "Br", 36 : "Kr",
                           51 : "Sb", 52 : "Te", 53 : "I", 54 : "Xe" }
                        
elementAMU = { 1 : "1.008", 2 : "4.003", 
                        5 : "10.811", 6 : "12.011" , 7 : "14.007", 8 : "15.999", 9 : "18.998", 10: "20.178",
                        13 : "26.982", 14 : "28.086", 15 : "30.974", 16 : "32.066", 17 : "35.453", 18 : "39.948",
                        32 : "72.610", 33 : "74.922", 34 : "78.960", 35 : "79.904", 36 : "83.800",
                        51 : "121.760", 52 : "127.600", 53 : "126.904", 54 : "131.290" }

r = { 1: 60, 2 : 210, 
        5 : 80, 6 : 35, 7 : 255, 8 : 190, 9 : 85, 10 : 210, 
        13 : 170, 14 : 155, 15 : 170, 16 : 255, 17 : 150, 18 : 210,
        32 : 206, 33 : 229, 34 : 230, 35 : 77, 36 : 210,
        51 : 170, 52 : 238, 53 : 0, 54 : 210 }
g = { 1: 215, 2 : 210, 
        5 : 135, 6 : 165, 7 : 170, 8 : 0, 9 : 255, 10 : 210, 
        13 : 170, 14 : 155, 15 : 85, 16 : 215, 17 : 225, 18 : 210,
        32 : 206, 33 : 62, 34 : 144, 35 : 202, 36 : 210,
        51 : 0, 52 : 183, 53 : 180, 54 : 210 }
b = { 1: 205, 2 : 255, 
        5 : 255, 6 : 75, 7 : 255, 8 : 0, 9 : 125, 10 : 255, 
        13 : 255, 14 : 155, 15 : 200, 16 : 75, 17 : 0, 18 : 255,
        32 : 0, 33 : 255, 34 : 23, 35 : 156, 36 : 255,
        51 : 255, 52 : 53, 53 : 135, 54 : 255 }

############################################################

class elementSelector(ElementSelectorDialog):
    def __init__(self, win):
        ElementSelectorDialog.__init__(self)
        self.w = win

# Create the pixmaps for each element        

        self.image1 = QPixmap(image1_data)
        self.image5 = QPixmap(image5_data)
        self.image6 = QPixmap(image6_data)
        self.image7 = QPixmap(image7_data)
        self.image8 = QPixmap(image8_data)
        self.image9 = QPixmap(image9_data)
        self.image13 = QPixmap(image13_data)
        self.image14 = QPixmap(image14_data)
        self.image15 = QPixmap(image15_data)
        self.image16 = QPixmap(image16_data)
        self.image17 = QPixmap(image17_data)

# Set the default element here (carbon)
        #self.setElementInfo(6)  # commet out by Huaicai

    # called as a slot from button push
    def setElementInfo(self,value):
        self.w.glpane.mode.elemSet(value)

    def setDisplay(self, value):

        print "set display value",value
        # Set element number
        self.elementNumberLabel.setText(str(value))
        # Set element symbol
        self.elementSymbolLabel.setText(elementSymbol[ value ])
        # Set element AMU
        self.amuLabel.setText(elementAMU[ value ])
        # Set element frame color
        self.elementFrame.setPaletteBackgroundColor(QColor(r[value],g[value],b[value])) 
 
 # Set element pixmap
        
        if value == 1 :
            self.pixmapLabel1.setPixmap(self.image1)  # Set pixmap to hydrogen
        elif value == 5 :
            self.pixmapLabel1.setPixmap(self.image5)  # Set pixmap to boron
        elif value == 6 :
            self.pixmapLabel1.setPixmap(self.image6)  # Set pixmap to carbon
        elif value == 7 :
            self.pixmapLabel1.setPixmap(self.image7)  # Set pixmap to nitrogen
        elif value == 8 :
            self.pixmapLabel1.setPixmap(self.image8)  # Set pixmap to oxygen
        elif value == 9 :
            self.pixmapLabel1.setPixmap(self.image9)  # Set pixmap to flourine
        elif value == 13 :
            self.pixmapLabel1.setPixmap(self.image13)  # Set pixmap to aluminum
        elif value == 14 :
            self.pixmapLabel1.setPixmap(self.image14)  # Set pixmap to silicon
        elif value == 15 :
            self.pixmapLabel1.setPixmap(self.image15)  # Set pixmap to phosphorus 
        elif value == 16 :
            self.pixmapLabel1.setPixmap(self.image16)  # Set pixmap to sulfur
        else :
            self.pixmapLabel1.setPixmap(self.image17)  # Set pixmap to chloriine (all elements without a pixmap get this)
            
    def transmutePressed(self):
        self.w.glpane.mode.elemSet(self.w.Element)