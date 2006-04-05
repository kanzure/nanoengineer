# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
GroupProp.py

$Id$
"""

from qt import *
from GroupPropDialog import *
from VQT import V

class Statistics:
    def __init__(self, group):
        
        # Get statistics of group.
        group.init_statistics(self)
        group.getstatistics(self)
        
    def display(self, statsView):
        '''Display the statistics in the listview widget 'statsView'
        '''
        
        # Subtract singlets from total number of atoms            
        self.num_atoms = self.natoms - self.nsinglets 
            
        # Display stats in listview
        statsView.setSorting( -1) # Turn off sorting
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Measure Dihedral:")
        item.setText(1, str(self.num_mdihedral))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Measure Angle:")
        item.setText(1, str(self.num_mangle))

        item = QListViewItem(statsView,None)
        item.setText(0,"Measure Distance:")
        item.setText(1, str(self.num_mdistance))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Grid Plane:")
        item.setText(1, str(self.num_gridplane))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"ESP Image:")
        item.setText(1, str(self.num_espimage))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Gamess:")
        item.setText(1, str(self.ngamess))
                
        item = QListViewItem(statsView,None)
        item.setText(0,"Thermometers:")
        item.setText(1, str(self.nthermos))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Thermostats:")
        item.setText(1, str(self.nstats))

        item = QListViewItem(statsView,None)
        item.setText(0,"Anchors:")
        item.setText(1, str(self.nanchors))

        item = QListViewItem(statsView,None)
        item.setText(0,"Linear Motors:")
        item.setText(1, str(self.nlmotors))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Rotary Motors:")
        item.setText(1, str(self.nrmotors))
        
        item = QListViewItem(statsView,None)
        item.setText(0,"Groups:")
        item.setText(1, str(self.ngroups))

        item = QListViewItem(statsView,None)
        item.setText(0,"Bondpoints:")
        item.setText(1, str(self.nsinglets))

        item = QListViewItem(statsView,None)
        item.setText(0,"Atoms:")
        item.setText(1, str(self.num_atoms))
                        
        item = QListViewItem(statsView,None)
        item.setText(0,"Chunks:")
        item.setText(1, str(self.nchunks))

class GroupProp(GroupPropDialog):
    def __init__(self, group):

        GroupPropDialog.__init__(self)
        self.group = group
        
        self.nameLineEdit.setText(group.name)
        
        # Get statistics of group and display them in the statView widget.
        stats = Statistics(group)
        stats.display(self.statsView)

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