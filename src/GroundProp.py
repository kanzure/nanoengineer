# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from GroundPropDialog import *


class GroundProp(GroundPropDialog):
    def __init__(self, ground):
        GroundPropDialog.__init__(self)
        self.ground = ground
     
        self.nameLineEdit.setText("Ground1")   
        
        
        strList = map(lambda i: ground.atoms[i].element.symbol + str(i), 
                                                 range(0, len(ground.atoms)))
        self.atomsComboBox.insertStrList(strList, 0)
        

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

         