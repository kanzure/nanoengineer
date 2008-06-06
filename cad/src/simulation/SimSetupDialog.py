# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SimSetupDialog.ui'
#
# Created: Fri Jun 06 12:02:42 2008
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SimSetupDialog(object):
    def setupUi(self, SimSetupDialog):
        SimSetupDialog.setObjectName("SimSetupDialog")
        SimSetupDialog.resize(QtCore.QSize(QtCore.QRect(0,0,250,350).size()).expandedTo(SimSetupDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SimSetupDialog.sizePolicy().hasHeightForWidth())
        SimSetupDialog.setSizePolicy(sizePolicy)
        SimSetupDialog.setMinimumSize(QtCore.QSize(0,350))
        SimSetupDialog.setModal(True)

        self.gridlayout = QtGui.QGridLayout(SimSetupDialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.whatsthis_btn = QtGui.QToolButton(SimSetupDialog)
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout.addWidget(self.whatsthis_btn)

        spacerItem = QtGui.QSpacerItem(21,25,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.cancel_btn = QtGui.QPushButton(SimSetupDialog)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)

        self.run_sim_btn = QtGui.QPushButton(SimSetupDialog)
        self.run_sim_btn.setDefault(True)
        self.run_sim_btn.setObjectName("run_sim_btn")
        self.hboxlayout.addWidget(self.run_sim_btn)
        self.gridlayout.addLayout(self.hboxlayout,4,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1,3,0,1,1)

        self.parms_grpbox = QtGui.QGroupBox(SimSetupDialog)
        self.parms_grpbox.setObjectName("parms_grpbox")

        self.vboxlayout = QtGui.QVBoxLayout(self.parms_grpbox)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(4)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(4)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel5 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel5.setObjectName("textLabel5")
        self.vboxlayout1.addWidget(self.textLabel5)

        self.textLabel2 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel2.setObjectName("textLabel2")
        self.vboxlayout1.addWidget(self.textLabel2)

        self.textLabel3 = QtGui.QLabel(self.parms_grpbox)
        self.textLabel3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel3.setObjectName("textLabel3")
        self.vboxlayout1.addWidget(self.textLabel3)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(4)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.totalFramesSpinBox = QtGui.QSpinBox(self.parms_grpbox)
        self.totalFramesSpinBox.setMaximum(1000000)
        self.totalFramesSpinBox.setMinimum(1)
        self.totalFramesSpinBox.setSingleStep(15)
        self.totalFramesSpinBox.setProperty("value",QtCore.QVariant(900))
        self.totalFramesSpinBox.setObjectName("totalFramesSpinBox")
        self.vboxlayout2.addWidget(self.totalFramesSpinBox)

        self.stepsPerFrameDoubleSpinBox = QtGui.QDoubleSpinBox(self.parms_grpbox)
        self.stepsPerFrameDoubleSpinBox.setDecimals(2)
        self.stepsPerFrameDoubleSpinBox.setSingleStep(0.1)
        self.stepsPerFrameDoubleSpinBox.setProperty("value",QtCore.QVariant(1.0))
        self.stepsPerFrameDoubleSpinBox.setObjectName("stepsPerFrameDoubleSpinBox")
        self.vboxlayout2.addWidget(self.stepsPerFrameDoubleSpinBox)

        self.temperatureSpinBox = QtGui.QSpinBox(self.parms_grpbox)
        self.temperatureSpinBox.setMaximum(99999)
        self.temperatureSpinBox.setProperty("value",QtCore.QVariant(300))
        self.temperatureSpinBox.setObjectName("temperatureSpinBox")
        self.vboxlayout2.addWidget(self.temperatureSpinBox)
        self.hboxlayout1.addLayout(self.vboxlayout2)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.potential_energy_checkbox = QtGui.QCheckBox(self.parms_grpbox)
        self.potential_energy_checkbox.setObjectName("potential_energy_checkbox")
        self.vboxlayout.addWidget(self.potential_energy_checkbox)
        self.gridlayout.addWidget(self.parms_grpbox,0,0,1,1)

        self.watch_motion_groupbox = QtGui.QGroupBox(SimSetupDialog)
        self.watch_motion_groupbox.setCheckable(True)
        self.watch_motion_groupbox.setChecked(True)
        self.watch_motion_groupbox.setObjectName("watch_motion_groupbox")

        self.gridlayout1 = QtGui.QGridLayout(self.watch_motion_groupbox)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(2)
        self.gridlayout1.setObjectName("gridlayout1")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(4)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.update_every_rbtn = QtGui.QRadioButton(self.watch_motion_groupbox)
        self.update_every_rbtn.setObjectName("update_every_rbtn")
        self.hboxlayout2.addWidget(self.update_every_rbtn)

        self.update_number_spinbox = QtGui.QSpinBox(self.watch_motion_groupbox)
        self.update_number_spinbox.setMaximum(9999)
        self.update_number_spinbox.setMinimum(1)
        self.update_number_spinbox.setProperty("value",QtCore.QVariant(1))
        self.update_number_spinbox.setObjectName("update_number_spinbox")
        self.hboxlayout2.addWidget(self.update_number_spinbox)

        self.update_units_combobox = QtGui.QComboBox(self.watch_motion_groupbox)
        self.update_units_combobox.setObjectName("update_units_combobox")
        self.hboxlayout2.addWidget(self.update_units_combobox)

        spacerItem3 = QtGui.QSpacerItem(71,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem3)
        self.gridlayout1.addLayout(self.hboxlayout2,1,0,1,1)

        self.update_asap_rbtn = QtGui.QRadioButton(self.watch_motion_groupbox)
        self.update_asap_rbtn.setChecked(True)
        self.update_asap_rbtn.setObjectName("update_asap_rbtn")
        self.gridlayout1.addWidget(self.update_asap_rbtn,0,0,1,1)
        self.gridlayout.addWidget(self.watch_motion_groupbox,1,0,1,1)

        self.md_engine_groupbox = QtGui.QGroupBox(SimSetupDialog)
        self.md_engine_groupbox.setObjectName("md_engine_groupbox")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.md_engine_groupbox)
        self.vboxlayout3.setMargin(4)
        self.vboxlayout3.setSpacing(4)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(4)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.simulation_engine_combobox = QtGui.QComboBox(self.md_engine_groupbox)
        self.simulation_engine_combobox.setObjectName("simulation_engine_combobox")
        self.hboxlayout3.addWidget(self.simulation_engine_combobox)

        spacerItem4 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem4)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.electrostaticsForDnaDuringDynamics_checkBox = QtGui.QCheckBox(self.md_engine_groupbox)
        self.electrostaticsForDnaDuringDynamics_checkBox.setChecked(True)
        self.electrostaticsForDnaDuringDynamics_checkBox.setObjectName("electrostaticsForDnaDuringDynamics_checkBox")
        self.vboxlayout3.addWidget(self.electrostaticsForDnaDuringDynamics_checkBox)
        self.gridlayout.addWidget(self.md_engine_groupbox,2,0,1,1)

        self.retranslateUi(SimSetupDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),SimSetupDialog.close)
        QtCore.QMetaObject.connectSlotsByName(SimSetupDialog)

    def retranslateUi(self, SimSetupDialog):
        SimSetupDialog.setWindowTitle(QtGui.QApplication.translate("SimSetupDialog", "Run Dynamics", None, QtGui.QApplication.UnicodeUTF8))
        SimSetupDialog.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Run Dynamics Setup Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("SimSetupDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.run_sim_btn.setText(QtGui.QApplication.translate("SimSetupDialog", "Run Simulation", None, QtGui.QApplication.UnicodeUTF8))
        self.parms_grpbox.setTitle(QtGui.QApplication.translate("SimSetupDialog", "Simulation parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel5.setText(QtGui.QApplication.translate("SimSetupDialog", "Total frames:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("SimSetupDialog", "Steps per frame:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("SimSetupDialog", "Temperature:", None, QtGui.QApplication.UnicodeUTF8))
        self.totalFramesSpinBox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Total Frames value", None, QtGui.QApplication.UnicodeUTF8))
        self.totalFramesSpinBox.setSuffix(QtGui.QApplication.translate("SimSetupDialog", " frames", None, QtGui.QApplication.UnicodeUTF8))
        self.stepsPerFrameDoubleSpinBox.setSuffix(QtGui.QApplication.translate("SimSetupDialog", " femtoseconds", None, QtGui.QApplication.UnicodeUTF8))
        self.temperatureSpinBox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Temperature", None, QtGui.QApplication.UnicodeUTF8))
        self.temperatureSpinBox.setSuffix(QtGui.QApplication.translate("SimSetupDialog", " K", None, QtGui.QApplication.UnicodeUTF8))
        self.potential_energy_checkbox.setText(QtGui.QApplication.translate("SimSetupDialog", "Plot energy in tracefile", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_motion_groupbox.setTitle(QtGui.QApplication.translate("SimSetupDialog", "Watch motion in real time", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setText(QtGui.QApplication.translate("SimSetupDialog", "Update every", None, QtGui.QApplication.UnicodeUTF8))
        self.update_number_spinbox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Specify how often to update the screen during the simulation.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "frames", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "hours", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Update every 2 seconds, or faster if it doesn\'t slow simulation by more than 20%", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setText(QtGui.QApplication.translate("SimSetupDialog", "Update as fast as possible", None, QtGui.QApplication.UnicodeUTF8))
        self.md_engine_groupbox.setTitle(QtGui.QApplication.translate("SimSetupDialog", "Molecular Dynamics Engine", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.setToolTip(QtGui.QApplication.translate("SimSetupDialog", "Choose the simulation engine with which to minimize energy.", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "NanoDynamics-1 (Default)", None, QtGui.QApplication.UnicodeUTF8))
        self.simulation_engine_combobox.addItem(QtGui.QApplication.translate("SimSetupDialog", "GROMACS", None, QtGui.QApplication.UnicodeUTF8))
        self.electrostaticsForDnaDuringDynamics_checkBox.setText(QtGui.QApplication.translate("SimSetupDialog", "Electrostatics for DNA reduced model", None, QtGui.QApplication.UnicodeUTF8))

