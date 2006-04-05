# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
PartProp.py

$Id$
"""

from qt import *
from PartPropDialog import *

class PartProp(PartPropDialog):
    def __init__(self, assy):
        PartPropDialog.__init__(self)

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