# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
from qt import *
from GroupPropDialog import *
from VQT import V

class GroupProp(GroupPropDialog):
    def __init__(self, group):

        GroupPropDialog.__init__(self)
        self.group = group
        
        self.nameLineEdit.setText(group.name)

    #################
    # OK Button
    #################
    def accept(self):
        QDialog.accept(self)

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)

    def nameChanged(self):
        self.group.name = str(self.nameLineEdit.text())