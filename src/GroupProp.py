# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
GroupProp.py

$Id$
"""

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
        text =  QString(self.nameLineEdit.text())        
        text = text.stripWhiteSpace() # make sure name is not just whitespaces
        if text:
            self.group.name = str(text)
            self.group.assy.modified = 1
