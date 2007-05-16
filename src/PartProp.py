# Copyright 2004-2006 Nanorex, Inc.  See LICENSE file for details. 
"""
PartProp.py

$Id$
"""

from PyQt4.Qt import *
from PartPropDialog import *

class PartProp(QDialog, Ui_PartPropDialog):
    def __init__(self, assy):
        QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.okPushButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self.reject)

        self.nameLineEdit.setText(assy.name)
        
        self.mmpformatLabel.setText("MMP File Format: " + assy.mmpformat)
        
        # Get statistics of part and display them in the statView widget.
        from GroupProp import Statistics
        stats = Statistics(assy.tree)
        stats.display(self.statsView)

    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)
