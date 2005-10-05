# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
        
        # Get statistics of group.
        self.group.init_statistics(self)
        self.group.getstatistics(self)

        # Subtract singlets from total number of atoms            
        self.natoms = self.natoms - self.nsinglets 
            
        # Display stats in listview
        self.statsView.setSorting( -1) # Turn off sorting

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Groups:")
        item.setText(1, str(self.ngroups))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Gamess:")
        item.setText(1, str(self.ngamess))
                
        item = QListViewItem(self.statsView,None)
        item.setText(0,"Thermometers:")
        item.setText(1, str(self.nthermos))
        
        item = QListViewItem(self.statsView,None)
        item.setText(0,"Thermostats:")
        item.setText(1, str(self.nstats))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Grounds:")
        item.setText(1, str(self.ngrounds))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Linear Motors:")
        item.setText(1, str(self.nlmotors))
        
        item = QListViewItem(self.statsView,None)
        item.setText(0,"Rotary Motors:")
        item.setText(1, str(self.nrmotors))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Open Bonds:")
        item.setText(1, str(self.nsinglets))

        item = QListViewItem(self.statsView,None)
        item.setText(0,"Atoms:")
        item.setText(1, str(self.natoms))
                        
        item = QListViewItem(self.statsView,None)
        item.setText(0,"Chunks:")
        item.setText(1, str(self.nchunks))

    #################
    # Cancel Button
    #################
    def reject(self):
	    QDialog.reject(self)

    #################
    # OK Button
    #################
    def accept(self):
        self.group.try_rename(self.nameLineEdit.text())
        QDialog.accept(self)