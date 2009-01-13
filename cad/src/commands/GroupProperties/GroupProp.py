# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
GroupProp.py

$Id$
"""

import sys

from PyQt4.Qt import QDialog, QListWidgetItem, SIGNAL
from commands.GroupProperties.GroupPropDialog import Ui_GroupPropDialog
from geometry.VQT import V

class Statistics:
    def __init__(self, group):

        # Get statistics of group.
        group.init_statistics(self)
        group.getstatistics(self)

    def display(self, statsView):
        """
        Display the statistics in the listview widget 'statsView'
        """
        # Subtract singlets from total number of atoms
        self.num_atoms = self.natoms - self.nsinglets

        item = QListWidgetItem()
        item.setText("Measure Dihedral:" + str(self.num_mdihedral))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Measure Angle:" + str(self.num_mangle))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Measure Distance:" + str(self.num_mdistance))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Grid Plane:" + str(self.num_gridplane))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("ESP Image:" + str(self.num_espimage))
        statsView.addItem(item)

        item = QListWidgetItem()
        if sys.platform == "win32":
            item.setText("PC GAMESS:" + str(self.ngamess))
        else:
            item.setText("GAMESS:" + str(self.ngamess))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Thermometers:" + str(self.nthermos))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Thermostats:" + str(self.nstats))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Anchors:" + str(self.nanchors))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Linear Motors:" + str(self.nlmotors))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Rotary Motors:" + str(self.nrmotors))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Groups:" + str(self.ngroups))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Bondpoints:" + str(self.nsinglets))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Atoms:" + str(self.num_atoms))
        statsView.addItem(item)

        item = QListWidgetItem()
        item.setText("Chunks:" + str(self.nchunks))
        statsView.addItem(item)

class GroupProp(QDialog, Ui_GroupPropDialog):
    def __init__(self, group):

        QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.okPushButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self.reject)
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
