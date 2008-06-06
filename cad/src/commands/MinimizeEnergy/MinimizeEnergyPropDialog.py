# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MinimizeEnergyPropDialog.ui'
#
# Created: Fri Jun 06 11:55:35 2008
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MinimizeEnergyPropDialog(object):
    def setupUi(self, MinimizeEnergyPropDialog):
        MinimizeEnergyPropDialog.setObjectName("MinimizeEnergyPropDialog")
        MinimizeEnergyPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,300,500).size()).expandedTo(MinimizeEnergyPropDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MinimizeEnergyPropDialog.sizePolicy().hasHeightForWidth())
        MinimizeEnergyPropDialog.setSizePolicy(sizePolicy)
        MinimizeEnergyPropDialog.setMinimumSize(QtCore.QSize(300,500))

        self.gridlayout = QtGui.QGridLayout(MinimizeEnergyPropDialog)
        self.gridlayout.setMargin(9)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        spacerItem = QtGui.QSpacerItem(221,21,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,5,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.whatsthis_btn = QtGui.QToolButton(MinimizeEnergyPropDialog)
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout.addWidget(self.whatsthis_btn)

        spacerItem1 = QtGui.QSpacerItem(41,23,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)

        self.cancel_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)

        self.ok_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout.addWidget(self.ok_btn)
        self.gridlayout.addLayout(self.hboxlayout,6,0,1,1)

        self.buttonGroup8_2 = QtGui.QGroupBox(MinimizeEnergyPropDialog)
        self.buttonGroup8_2.setObjectName("buttonGroup8_2")

        self.vboxlayout = QtGui.QVBoxLayout(self.buttonGroup8_2)
        self.vboxlayout.setMargin(4)
        self.vboxlayout.setSpacing(4)
        self.vboxlayout.setObjectName("vboxlayout")

        self.minimize_engine_combobox = QtGui.QComboBox(self.buttonGroup8_2)
        self.minimize_engine_combobox.setObjectName("minimize_engine_combobox")
        self.vboxlayout.addWidget(self.minimize_engine_combobox)
        self.gridlayout.addWidget(self.buttonGroup8_2,0,0,1,1)

        self.buttonGroup8 = QtGui.QGroupBox(MinimizeEnergyPropDialog)
        self.buttonGroup8.setObjectName("buttonGroup8")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.buttonGroup8)
        self.vboxlayout1.setMargin(4)
        self.vboxlayout1.setSpacing(2)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.minimize_all_rbtn = QtGui.QRadioButton(self.buttonGroup8)
        self.minimize_all_rbtn.setChecked(True)
        self.minimize_all_rbtn.setObjectName("minimize_all_rbtn")
        self.vboxlayout1.addWidget(self.minimize_all_rbtn)

        self.minimize_sel_rbtn = QtGui.QRadioButton(self.buttonGroup8)
        self.minimize_sel_rbtn.setObjectName("minimize_sel_rbtn")
        self.vboxlayout1.addWidget(self.minimize_sel_rbtn)

        self.electrostaticsForDnaDuringMinimize_checkBox = QtGui.QCheckBox(self.buttonGroup8)
        self.electrostaticsForDnaDuringMinimize_checkBox.setChecked(True)
        self.electrostaticsForDnaDuringMinimize_checkBox.setObjectName("electrostaticsForDnaDuringMinimize_checkBox")
        self.vboxlayout1.addWidget(self.electrostaticsForDnaDuringMinimize_checkBox)

        self.enableNeighborSearching_check_box = QtGui.QCheckBox(self.buttonGroup8)
        self.enableNeighborSearching_check_box.setChecked(True)
        self.enableNeighborSearching_check_box.setObjectName("enableNeighborSearching_check_box")
        self.vboxlayout1.addWidget(self.enableNeighborSearching_check_box)
        self.gridlayout.addWidget(self.buttonGroup8,1,0,1,1)

        self.watch_motion_groupbox = QtGui.QGroupBox(MinimizeEnergyPropDialog)
        self.watch_motion_groupbox.setCheckable(True)
        self.watch_motion_groupbox.setObjectName("watch_motion_groupbox")

        self.gridlayout1 = QtGui.QGridLayout(self.watch_motion_groupbox)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(2)
        self.gridlayout1.setObjectName("gridlayout1")

        self.update_asap_rbtn = QtGui.QRadioButton(self.watch_motion_groupbox)
        self.update_asap_rbtn.setChecked(True)
        self.update_asap_rbtn.setObjectName("update_asap_rbtn")
        self.gridlayout1.addWidget(self.update_asap_rbtn,0,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(2)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.update_every_rbtn = QtGui.QRadioButton(self.watch_motion_groupbox)
        self.update_every_rbtn.setObjectName("update_every_rbtn")
        self.hboxlayout1.addWidget(self.update_every_rbtn)

        self.update_number_spinbox = QtGui.QSpinBox(self.watch_motion_groupbox)
        self.update_number_spinbox.setMaximum(9999)
        self.update_number_spinbox.setMinimum(1)
        self.update_number_spinbox.setProperty("value",QtCore.QVariant(1))
        self.update_number_spinbox.setObjectName("update_number_spinbox")
        self.hboxlayout1.addWidget(self.update_number_spinbox)

        self.update_units_combobox = QtGui.QComboBox(self.watch_motion_groupbox)
        self.update_units_combobox.setObjectName("update_units_combobox")
        self.hboxlayout1.addWidget(self.update_units_combobox)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.gridlayout1.addLayout(self.hboxlayout1,1,0,1,1)
        self.gridlayout.addWidget(self.watch_motion_groupbox,2,0,1,1)

        self.groupBox20 = QtGui.QGroupBox(MinimizeEnergyPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox20.sizePolicy().hasHeightForWidth())
        self.groupBox20.setSizePolicy(sizePolicy)
        self.groupBox20.setObjectName("groupBox20")

        self.hboxlayout2 = QtGui.QHBoxLayout(self.groupBox20)
        self.hboxlayout2.setMargin(4)
        self.hboxlayout2.setSpacing(4)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.endrms_lbl = QtGui.QLabel(self.groupBox20)
        self.endrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endrms_lbl.setObjectName("endrms_lbl")
        self.vboxlayout2.addWidget(self.endrms_lbl)

        self.endmax_lbl = QtGui.QLabel(self.groupBox20)
        self.endmax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endmax_lbl.setObjectName("endmax_lbl")
        self.vboxlayout2.addWidget(self.endmax_lbl)

        self.cutoverrms_lbl = QtGui.QLabel(self.groupBox20)
        self.cutoverrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutoverrms_lbl.setObjectName("cutoverrms_lbl")
        self.vboxlayout2.addWidget(self.cutoverrms_lbl)

        self.cutovermax_lbl = QtGui.QLabel(self.groupBox20)
        self.cutovermax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutovermax_lbl.setObjectName("cutovermax_lbl")
        self.vboxlayout2.addWidget(self.cutovermax_lbl)
        self.hboxlayout2.addLayout(self.vboxlayout2)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(2)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.endRmsDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endRmsDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.endRmsDoubleSpinBox.setSizePolicy(sizePolicy)
        self.endRmsDoubleSpinBox.setDecimals(3)
        self.endRmsDoubleSpinBox.setMaximum(501.0)
        self.endRmsDoubleSpinBox.setProperty("value",QtCore.QVariant(1.0))
        self.endRmsDoubleSpinBox.setObjectName("endRmsDoubleSpinBox")
        self.vboxlayout3.addWidget(self.endRmsDoubleSpinBox)

        self.endMaxDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.endMaxDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.endMaxDoubleSpinBox.setSizePolicy(sizePolicy)
        self.endMaxDoubleSpinBox.setDecimals(2)
        self.endMaxDoubleSpinBox.setMaximum(2501.0)
        self.endMaxDoubleSpinBox.setProperty("value",QtCore.QVariant(0.0))
        self.endMaxDoubleSpinBox.setObjectName("endMaxDoubleSpinBox")
        self.vboxlayout3.addWidget(self.endMaxDoubleSpinBox)

        self.cutoverRmsDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cutoverRmsDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.cutoverRmsDoubleSpinBox.setSizePolicy(sizePolicy)
        self.cutoverRmsDoubleSpinBox.setDecimals(2)
        self.cutoverRmsDoubleSpinBox.setMaximum(12500.0)
        self.cutoverRmsDoubleSpinBox.setProperty("value",QtCore.QVariant(0.0))
        self.cutoverRmsDoubleSpinBox.setObjectName("cutoverRmsDoubleSpinBox")
        self.vboxlayout3.addWidget(self.cutoverRmsDoubleSpinBox)

        self.cutoverMaxDoubleSpinBox = QtGui.QDoubleSpinBox(self.groupBox20)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cutoverMaxDoubleSpinBox.sizePolicy().hasHeightForWidth())
        self.cutoverMaxDoubleSpinBox.setSizePolicy(sizePolicy)
        self.cutoverMaxDoubleSpinBox.setDecimals(2)
        self.cutoverMaxDoubleSpinBox.setMaximum(60001.0)
        self.cutoverMaxDoubleSpinBox.setProperty("value",QtCore.QVariant(0.0))
        self.cutoverMaxDoubleSpinBox.setObjectName("cutoverMaxDoubleSpinBox")
        self.vboxlayout3.addWidget(self.cutoverMaxDoubleSpinBox)
        self.hboxlayout2.addLayout(self.vboxlayout3)

        spacerItem3 = QtGui.QSpacerItem(80,20,QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem3)
        self.gridlayout.addWidget(self.groupBox20,3,0,1,1)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem4 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem4)

        self.restore_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.restore_btn.setObjectName("restore_btn")
        self.hboxlayout3.addWidget(self.restore_btn)
        self.gridlayout.addLayout(self.hboxlayout3,4,0,1,1)

        self.retranslateUi(MinimizeEnergyPropDialog)
        QtCore.QMetaObject.connectSlotsByName(MinimizeEnergyPropDialog)

    def retranslateUi(self, MinimizeEnergyPropDialog):
        MinimizeEnergyPropDialog.setWindowTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonGroup8_2.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize physics engine", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Choose the simulation engine with which to minimize energy.", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "NanoDynamics-1 (Default)", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "GROMACS with ND1 Force Field", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Background GROMACS with ND1 Force Field", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonGroup8.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Options", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on all the atoms in the workspace", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize all", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on only the atoms that have been selected", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize selection", None, QtGui.QApplication.UnicodeUTF8))
        self.electrostaticsForDnaDuringMinimize_checkBox.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Electrostatics for DNA reduced model", None, QtGui.QApplication.UnicodeUTF8))
        self.enableNeighborSearching_check_box.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Enable neighbor searching (slow but accurate)", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_motion_groupbox.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Watch motion in real time", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Update every 2 seconds, or faster if it doesn\'t slow adjustments by more than 20%", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Update as fast as possible", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during adjustments", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Update every", None, QtGui.QApplication.UnicodeUTF8))
        self.update_number_spinbox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during adjustments", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during adjustments", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "frames", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "hours", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox20.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Convergence criteria", None, QtGui.QApplication.UnicodeUTF8))
        self.endrms_lbl.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Target RMS force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.endrms_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "EndRMS:", None, QtGui.QApplication.UnicodeUTF8))
        self.endmax_lbl.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Target max force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.endmax_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "EndMax:", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverrms_lbl.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cutover RMS force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverrms_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "CutoverRMS:", None, QtGui.QApplication.UnicodeUTF8))
        self.cutovermax_lbl.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cutover max force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.cutovermax_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "CutoverMax:", None, QtGui.QApplication.UnicodeUTF8))
        self.endRmsDoubleSpinBox.setSuffix(QtGui.QApplication.translate("MinimizeEnergyPropDialog", " pN", None, QtGui.QApplication.UnicodeUTF8))
        self.endMaxDoubleSpinBox.setSuffix(QtGui.QApplication.translate("MinimizeEnergyPropDialog", " pN", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverRmsDoubleSpinBox.setSuffix(QtGui.QApplication.translate("MinimizeEnergyPropDialog", " pN", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverMaxDoubleSpinBox.setSuffix(QtGui.QApplication.translate("MinimizeEnergyPropDialog", " pN", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))

