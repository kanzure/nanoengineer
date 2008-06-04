# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MinimizeEnergyPropDialog.ui'
#
# Created: Wed Jun 04 18:56:48 2008
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
        self.gridlayout.setMargin(2)
        self.gridlayout.setSpacing(4)
        self.gridlayout.setObjectName("gridlayout")

        spacerItem = QtGui.QSpacerItem(270,5,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,2,0,1,1)

        self.body_frame = QtGui.QFrame(MinimizeEnergyPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(3))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.body_frame.sizePolicy().hasHeightForWidth())
        self.body_frame.setSizePolicy(sizePolicy)
        self.body_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.body_frame.setObjectName("body_frame")

        self.gridlayout1 = QtGui.QGridLayout(self.body_frame)
        self.gridlayout1.setMargin(4)
        self.gridlayout1.setSpacing(4)
        self.gridlayout1.setObjectName("gridlayout1")

        self.watch_minimize_groupbox = QtGui.QGroupBox(self.body_frame)
        self.watch_minimize_groupbox.setCheckable(True)
        self.watch_minimize_groupbox.setObjectName("watch_minimize_groupbox")

        self.gridlayout2 = QtGui.QGridLayout(self.watch_minimize_groupbox)
        self.gridlayout2.setMargin(4)
        self.gridlayout2.setSpacing(2)
        self.gridlayout2.setObjectName("gridlayout2")

        self.update_asap_rbtn = QtGui.QRadioButton(self.watch_minimize_groupbox)
        self.update_asap_rbtn.setChecked(True)
        self.update_asap_rbtn.setObjectName("update_asap_rbtn")
        self.gridlayout2.addWidget(self.update_asap_rbtn,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(2)
        self.hboxlayout.setObjectName("hboxlayout")

        self.update_every_rbtn = QtGui.QRadioButton(self.watch_minimize_groupbox)
        self.update_every_rbtn.setObjectName("update_every_rbtn")
        self.hboxlayout.addWidget(self.update_every_rbtn)

        self.update_number_spinbox = QtGui.QSpinBox(self.watch_minimize_groupbox)
        self.update_number_spinbox.setMaximum(9999)
        self.update_number_spinbox.setMinimum(1)
        self.update_number_spinbox.setProperty("value",QtCore.QVariant(1))
        self.update_number_spinbox.setObjectName("update_number_spinbox")
        self.hboxlayout.addWidget(self.update_number_spinbox)

        self.update_units_combobox = QtGui.QComboBox(self.watch_minimize_groupbox)
        self.update_units_combobox.setObjectName("update_units_combobox")
        self.hboxlayout.addWidget(self.update_units_combobox)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.gridlayout2.addLayout(self.hboxlayout,1,0,1,1)
        self.gridlayout1.addWidget(self.watch_minimize_groupbox,4,0,1,1)

        self.groupBox20 = QtGui.QGroupBox(self.body_frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox20.sizePolicy().hasHeightForWidth())
        self.groupBox20.setSizePolicy(sizePolicy)
        self.groupBox20.setObjectName("groupBox20")

        self.hboxlayout1 = QtGui.QHBoxLayout(self.groupBox20)
        self.hboxlayout1.setMargin(4)
        self.hboxlayout1.setSpacing(4)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(2)
        self.vboxlayout.setObjectName("vboxlayout")

        self.endrms_lbl = QtGui.QLabel(self.groupBox20)
        self.endrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endrms_lbl.setObjectName("endrms_lbl")
        self.vboxlayout.addWidget(self.endrms_lbl)

        self.endmax_lbl = QtGui.QLabel(self.groupBox20)
        self.endmax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endmax_lbl.setObjectName("endmax_lbl")
        self.vboxlayout.addWidget(self.endmax_lbl)

        self.cutoverrms_lbl = QtGui.QLabel(self.groupBox20)
        self.cutoverrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutoverrms_lbl.setObjectName("cutoverrms_lbl")
        self.vboxlayout.addWidget(self.cutoverrms_lbl)

        self.cutovermax_lbl = QtGui.QLabel(self.groupBox20)
        self.cutovermax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutovermax_lbl.setObjectName("cutovermax_lbl")
        self.vboxlayout.addWidget(self.cutovermax_lbl)
        self.hboxlayout1.addLayout(self.vboxlayout)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(2)
        self.vboxlayout1.setObjectName("vboxlayout1")

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
        self.vboxlayout1.addWidget(self.endRmsDoubleSpinBox)

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
        self.vboxlayout1.addWidget(self.endMaxDoubleSpinBox)

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
        self.vboxlayout1.addWidget(self.cutoverRmsDoubleSpinBox)

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
        self.vboxlayout1.addWidget(self.cutoverMaxDoubleSpinBox)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        spacerItem2 = QtGui.QSpacerItem(80,20,QtGui.QSizePolicy.MinimumExpanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem2)
        self.gridlayout1.addWidget(self.groupBox20,5,0,1,1)

        self.buttonGroup8 = QtGui.QGroupBox(self.body_frame)
        self.buttonGroup8.setObjectName("buttonGroup8")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.buttonGroup8)
        self.vboxlayout2.setMargin(4)
        self.vboxlayout2.setSpacing(2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.minimize_all_rbtn = QtGui.QRadioButton(self.buttonGroup8)
        self.minimize_all_rbtn.setChecked(True)
        self.minimize_all_rbtn.setObjectName("minimize_all_rbtn")
        self.vboxlayout2.addWidget(self.minimize_all_rbtn)

        self.minimize_sel_rbtn = QtGui.QRadioButton(self.buttonGroup8)
        self.minimize_sel_rbtn.setObjectName("minimize_sel_rbtn")
        self.vboxlayout2.addWidget(self.minimize_sel_rbtn)

        self.electrostaticsForDnaDuringMinimize_checkBox = QtGui.QCheckBox(self.buttonGroup8)
        self.electrostaticsForDnaDuringMinimize_checkBox.setChecked(True)
        self.electrostaticsForDnaDuringMinimize_checkBox.setObjectName("electrostaticsForDnaDuringMinimize_checkBox")
        self.vboxlayout2.addWidget(self.electrostaticsForDnaDuringMinimize_checkBox)

        self.enableNeighborSearching_check_box = QtGui.QCheckBox(self.buttonGroup8)
        self.enableNeighborSearching_check_box.setChecked(True)
        self.enableNeighborSearching_check_box.setObjectName("enableNeighborSearching_check_box")
        self.vboxlayout2.addWidget(self.enableNeighborSearching_check_box)
        self.gridlayout1.addWidget(self.buttonGroup8,3,0,1,1)

        self.buttonGroup8_2 = QtGui.QGroupBox(self.body_frame)
        self.buttonGroup8_2.setObjectName("buttonGroup8_2")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.buttonGroup8_2)
        self.vboxlayout3.setMargin(4)
        self.vboxlayout3.setSpacing(4)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.minimize_engine_combobox = QtGui.QComboBox(self.buttonGroup8_2)
        self.minimize_engine_combobox.setObjectName("minimize_engine_combobox")
        self.vboxlayout3.addWidget(self.minimize_engine_combobox)
        self.gridlayout1.addWidget(self.buttonGroup8_2,2,0,1,1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        spacerItem3 = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem3)

        self.done_btn = QtGui.QToolButton(self.body_frame)
        self.done_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image2"))
        self.done_btn.setObjectName("done_btn")
        self.hboxlayout2.addWidget(self.done_btn)

        self.abort_btn = QtGui.QToolButton(self.body_frame)
        self.abort_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image3"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout2.addWidget(self.abort_btn)

        self.restore_btn = QtGui.QToolButton(self.body_frame)
        self.restore_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image4"))
        self.restore_btn.setObjectName("restore_btn")
        self.hboxlayout2.addWidget(self.restore_btn)

        self.whatsthis_btn = QtGui.QToolButton(self.body_frame)
        self.whatsthis_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image5"))
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout2.addWidget(self.whatsthis_btn)

        spacerItem4 = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem4)
        self.gridlayout1.addLayout(self.hboxlayout2,1,0,1,1)

        self.sponsor_btn = QtGui.QPushButton(self.body_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.gridlayout1.addWidget(self.sponsor_btn,0,0,1,1)
        self.gridlayout.addWidget(self.body_frame,1,0,1,1)

        self.heading_frame = QtGui.QFrame(MinimizeEnergyPropDialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")

        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setGeometry(QtCore.QRect(0,8,16,16))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setAlignment(QtCore.Qt.AlignVCenter)
        self.heading_pixmap.setObjectName("heading_pixmap")

        self.heading_label = QtGui.QLabel(self.heading_frame)
        self.heading_label.setGeometry(QtCore.QRect(3,0,267,21))

        font = QtGui.QFont()
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.heading_label.setFont(font)
        self.heading_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.heading_label.setObjectName("heading_label")
        self.gridlayout.addWidget(self.heading_frame,0,0,1,1)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(4)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem5 = QtGui.QSpacerItem(59,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem5)

        self.cancel_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout3.addWidget(self.cancel_btn)

        self.ok_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout3.addWidget(self.ok_btn)
        self.gridlayout.addLayout(self.hboxlayout3,3,0,1,1)

        self.retranslateUi(MinimizeEnergyPropDialog)
        QtCore.QMetaObject.connectSlotsByName(MinimizeEnergyPropDialog)

    def retranslateUi(self, MinimizeEnergyPropDialog):
        MinimizeEnergyPropDialog.setWindowTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_minimize_groupbox.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Watch minimize in real time", None, QtGui.QApplication.UnicodeUTF8))
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
        self.buttonGroup8.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Options", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on all the atoms in the workspace", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize all", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on only the atoms that have been selected", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize selection", None, QtGui.QApplication.UnicodeUTF8))
        self.electrostaticsForDnaDuringMinimize_checkBox.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Electrostatics for DNA reduced model", None, QtGui.QApplication.UnicodeUTF8))
        self.enableNeighborSearching_check_box.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Enable neighbor searching (slow but accurate)", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonGroup8_2.setTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize physics engine", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Choose the simulation engine with which to minimize energy.", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "NanoDynamics-1 (Default)", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "GROMACS with ND1 Force Field", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Background GROMACS with ND1 Force Field", None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.whatsthis_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "What\'s This Help", None, QtGui.QApplication.UnicodeUTF8))
        self.heading_label.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))

