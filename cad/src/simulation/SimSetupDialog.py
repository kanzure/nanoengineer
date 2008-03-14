# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'C:\Atom\qt4\cad\src\SimSetupDialog.ui'
#
# Created: Wed May 09 14:32:17 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SimSetupDialog(object):
    def setupUi(self, SimSetupDialog):
        SimSetupDialog.setObjectName("SimSetupDialog")
        SimSetupDialog.resize(QtCore.QSize(QtCore.QRect(0,0,337,428).size()).expandedTo(SimSetupDialog.minimumSizeHint()))
        SimSetupDialog.setModal(True)

        self.layout20 = QtGui.QWidget(SimSetupDialog)
        self.layout20.setGeometry(QtCore.QRect(10,380,310,40))
        self.layout20.setObjectName("layout20")

        self.hboxlayout = QtGui.QHBoxLayout(self.layout20)
        self.hboxlayout.setMargin(4)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.cancel_btn = QtGui.QPushButton(self.layout20)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)

        self.run_sim_btn = QtGui.QPushButton(self.layout20)
        self.run_sim_btn.setDefault(True)
        self.run_sim_btn.setObjectName("run_sim_btn")
        self.hboxlayout.addWidget(self.run_sim_btn)

        self.base_frame = QtGui.QFrame(SimSetupDialog)
        self.base_frame.setGeometry(QtCore.QRect(0,0,336,372))
        self.base_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.base_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.base_frame.setObjectName("base_frame")

        self.parms_grpbox_2 = QtGui.QGroupBox(self.base_frame)
        self.parms_grpbox_2.setGeometry(QtCore.QRect(6,305,324,61))
        self.parms_grpbox_2.setObjectName("parms_grpbox_2")

        self.line2_4_3 = QtGui.QFrame(self.parms_grpbox_2)
        self.line2_4_3.setGeometry(QtCore.QRect(4,21,316,2))
        self.line2_4_3.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4_3.setMidLineWidth(0)
        self.line2_4_3.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4_3.setObjectName("line2_4_3")

        self.parameters_label_2 = QtGui.QLabel(self.parms_grpbox_2)
        self.parameters_label_2.setGeometry(QtCore.QRect(4,4,316,17))
        self.parameters_label_2.setObjectName("parameters_label_2")

        self.simulation_engine_combobox = QtGui.QComboBox(self.parms_grpbox_2)
        self.simulation_engine_combobox.setGeometry(QtCore.QRect(18,30,281,20))
        self.simulation_engine_combobox.setObjectName("simulation_engine_combobox")

        self.groupBox2 = QtGui.QGroupBox(self.base_frame)
        self.groupBox2.setGeometry(QtCore.QRect(6,165,324,133))
        self.groupBox2.setObjectName("groupBox2")

        self.gridlayout = QtGui.QGridLayout(self.groupBox2)
        self.gridlayout.setMargin(4)
        self.gridlayout.setSpacing(1)
        self.gridlayout.setObjectName("gridlayout")

        self.watch_motion_checkbox = QtGui.QCheckBox(self.groupBox2)
        self.watch_motion_checkbox.setChecked(True)
        self.watch_motion_checkbox.setObjectName("watch_motion_checkbox")
        self.gridlayout.addWidget(self.watch_motion_checkbox,2,0,1,1)

        self.sim_options_label = QtGui.QLabel(self.groupBox2)
        self.sim_options_label.setObjectName("sim_options_label")
        self.gridlayout.addWidget(self.sim_options_label,0,0,1,1)

        self.update_btngrp = QtGui.QGroupBox(self.groupBox2)
        self.update_btngrp.setObjectName("update_btngrp")

        self.gridlayout1 = QtGui.QGridLayout(self.update_btngrp)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.update_number_spinbox = QtGui.QSpinBox(self.update_btngrp)
        self.update_number_spinbox.setMaximum(9999)
        self.update_number_spinbox.setMinimum(1)
        self.update_number_spinbox.setProperty("value",QtCore.QVariant(1))
        self.update_number_spinbox.setObjectName("update_number_spinbox")
        self.gridlayout1.addWidget(self.update_number_spinbox,1,1,1,1)

        self.update_units_combobox = QtGui.QComboBox(self.update_btngrp)
        self.update_units_combobox.setObjectName("update_units_combobox")
        self.gridlayout1.addWidget(self.update_units_combobox,1,2,1,1)

        spacerItem1 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem1,1,3,1,1)

        self.update_every_rbtn = QtGui.QRadioButton(self.update_btngrp)
        self.update_every_rbtn.setObjectName("update_every_rbtn")
        self.gridlayout1.addWidget(self.update_every_rbtn,1,0,1,1)

        self.update_asap_rbtn = QtGui.QRadioButton(self.update_btngrp)
        self.update_asap_rbtn.setChecked(True)
        self.update_asap_rbtn.setObjectName("update_asap_rbtn")
        self.gridlayout1.addWidget(self.update_asap_rbtn,0,0,1,4)
        self.gridlayout.addWidget(self.update_btngrp,3,0,1,1)

        self.line2_4 = QtGui.QFrame(self.groupBox2)
        self.line2_4.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4.setMidLineWidth(0)
        self.line2_4.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4.setObjectName("line2_4")
        self.gridlayout.addWidget(self.line2_4,1,0,1,1)

        self.electrostaticsForDnaDuringDynamics_checkBox = QtGui.QCheckBox(self.groupBox2)
        self.electrostaticsForDnaDuringDynamics_checkBox.setChecked(True)
        self.electrostaticsForDnaDuringDynamics_checkBox.setObjectName("electrostaticsForDnaDuringDynamics_checkBox")
        self.gridlayout.addWidget(self.electrostaticsForDnaDuringDynamics_checkBox,4,0,1,1)

        self.parms_grpbox = QtGui.QGroupBox(self.base_frame)
        self.parms_grpbox.setGeometry(QtCore.QRect(6,8,324,150))
        self.parms_grpbox.setObjectName("parms_grpbox")

        self.line2_4_2 = QtGui.QFrame(self.parms_grpbox)
        self.line2_4_2.setGeometry(QtCore.QRect(4,21,316,2))
        self.line2_4_2.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4_2.setMidLineWidth(0)
        self.line2_4_2.setFrameShape(QtGui.QFrame.HLine)
        self.line2_4_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_4_2.setObjectName("line2_4_2")

        self.tempSB = QtGui.QSpinBox(self.parms_grpbox)
        self.tempSB.setGeometry(QtCore.QRect(131,89,62,23))
        self.tempSB.setMaximum(99999)
        self.tempSB.setProperty("value",QtCore.QVariant(300))
        self.tempSB.setObjectName("tempSB")

        self.nframesSB = QtGui.QSpinBox(self.parms_grpbox)
        self.nframesSB.setGeometry(QtCore.QRect(131,31,62,23))
        self.nframesSB.setMaximum(90000)
        self.nframesSB.setMinimum(1)
        self.nframesSB.setSingleStep(15)
        self.nframesSB.setProperty("value",QtCore.QVariant(900))
        self.nframesSB.setObjectName("nframesSB")

        self.textLabel2 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel2.setGeometry(QtCore.QRect(6,60,117,23))
        self.textLabel2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel2.setObjectName("textLabel2")

        self.textLabel3 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel3.setGeometry(QtCore.QRect(6,89,117,23))
        self.textLabel3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel3.setObjectName("textLabel3")

        self.stepsperSB = QtGui.QSpinBox(self.parms_grpbox)
        self.stepsperSB.setGeometry(QtCore.QRect(131,60,62,23))
        self.stepsperSB.setMaximum(99999)
        self.stepsperSB.setMinimum(1)
        self.stepsperSB.setProperty("value",QtCore.QVariant(10))
        self.stepsperSB.setObjectName("stepsperSB")

        self.textLabel2_2 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel2_2.setGeometry(QtCore.QRect(201,60,117,23))
        self.textLabel2_2.setObjectName("textLabel2_2")

        self.textLabel5 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel5.setGeometry(QtCore.QRect(6,31,117,23))
        self.textLabel5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel5.setObjectName("textLabel5")

        self.parameters_label = QtGui.QLabel(self.parms_grpbox)
        self.parameters_label.setGeometry(QtCore.QRect(4,4,316,17))
        self.parameters_label.setObjectName("parameters_label")

        self.potential_energy_checkbox = QtGui.QCheckBox(self.parms_grpbox)
        self.potential_energy_checkbox.setGeometry(QtCore.QRect(20,121,180,20))
        self.potential_energy_checkbox.setObjectName("potential_energy_checkbox")

        self.textLabel3_2 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel3_2.setGeometry(QtCore.QRect(201,89,117,23))
        self.textLabel3_2.setObjectName("textLabel3_2")

        self.retranslateUi(SimSetupDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),SimSetupDialog.close)
        QtCore.QObject.connect(self.watch_motion_checkbox,QtCore.SIGNAL("toggled(bool)"),self.update_btngrp.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(SimSetupDialog)

    def retranslateUi(self, SimSetupDialog):
        SimSetupDialog.setWindowTitle(QtGui.QApplication.translate("SimSetupDialog", "Run Dynamics", None, QtGui.QApplication.UnicodeUTF8))
        SimSetupDialog.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Run Dynamics Setup Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("SimSetupDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.run_sim_btn.setText(QtGui.QApplication.translate("SimSetupDialog", "Run Simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.parameters_label_2.setText(QtGui.QApplication.translate("SimSetupDialog", "Simulation Engine", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Choose the simulation engine with which to minimize energy.", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "NanoDynamics-1 (Default)", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "GROMACS", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_motion_checkbox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Enables real time graphical updates during simulation runs", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_motion_checkbox.setText(QtGui.QApplication.translate("SimSetupDialog", "Watch motion in real time", None, QtGui.QApplication.UnicodeUTF8))
        self.sim_options_label.setText(QtGui.QApplication.translate("SimSetupDialog", "Simulation Options", None, QtGui.QApplication.UnicodeUTF8))
        self.update_number_spinbox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "frames", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "hours", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setText(QtGui.QApplication.translate("SimSetupDialog", "Update every", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Update every 2 seconds, or faster if it doesn\'t slow simulation by more than 20%", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setText(QtGui.QApplication.translate("SimSetupDialog", "Update as fast as possible", None, QtGui.QApplication.UnicodeUTF8))
        self.electrostaticsForDnaDuringDynamics_checkBox.setText(QtGui.QApplication.translate("SimSetupDialog", "Electrostatics for DNA Reduced Model", None, QtGui.QApplication.UnicodeUTF8))
        self.tempSB.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Temperature", None, QtGui.QApplication.UnicodeUTF8))
        self.nframesSB.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Total Frames value", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("SimSetupDialog", "Steps per Frame :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("SimSetupDialog", "Temperature :", None, QtGui.QApplication.UnicodeUTF8))
        self.stepsperSB.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Steps per Frame", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("SimSetupDialog", "0.1 femtosecond", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("SimSetupDialog", "Total Frames:", None, QtGui.QApplication.UnicodeUTF8))
        self.parameters_label.setText(QtGui.QApplication.translate("SimSetupDialog", "Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.potential_energy_checkbox.setText(QtGui.QApplication.translate("SimSetupDialog", "Plot energy in tracefile", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3_2.setText(QtGui.QApplication.translate("SimSetupDialog", "Kelvin", None, QtGui.QApplication.UnicodeUTF8))

