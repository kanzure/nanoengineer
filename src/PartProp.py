# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from PartPropDialog import *

class PartProp(PartPropDialog):
    def __init__(self, assy):
        PartPropDialog.__init__(self)
        self.assy = assy
        
        self.nameLineEdit.setText(self.assy.name)
                
    def applyButtonClicked(self):
        self.applyPushButton.setEnabled(False)            

    def accept(self):
        self.applyButtonClicked()    
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)