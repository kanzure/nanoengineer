# -*- coding: utf-8 -*-

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'C:\Atom\qt4\cad\src\MinimizeEnergyPropDialog.ui'
#
# Created: Wed May 09 14:31:28 2007
#      by: PyQt4 UI code generator 4.1.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui
from PropMgr_Constants import getHeaderFont
from PropMgr_Constants import pmLabelLeftAlignment

class Ui_MinimizeEnergyPropDialog(object):
    def setupUi(self, MinimizeEnergyPropDialog):
        MinimizeEnergyPropDialog.setObjectName("MinimizeEnergyPropDialog")
        MinimizeEnergyPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,245,554).size()).expandedTo(MinimizeEnergyPropDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(MinimizeEnergyPropDialog)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.heading_frame = QtGui.QFrame(MinimizeEnergyPropDialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")

        self.hboxlayout = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(3)
        self.hboxlayout.setObjectName("hboxlayout")

        self.heading_pixmap = QtGui.QLabel(self.heading_frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setAlignment(QtCore.Qt.AlignVCenter)
        self.heading_pixmap.setObjectName("heading_pixmap")
        self.hboxlayout.addWidget(self.heading_pixmap)

        self.heading_label = QtGui.QLabel(self.heading_frame)
        self.heading_label.setFont(getHeaderFont())
        self.heading_label.setAlignment(pmLabelLeftAlignment)
        self.hboxlayout.addWidget(self.heading_label)
        
        self.vboxlayout.addWidget(self.heading_frame)

        self.body_frame = QtGui.QFrame(MinimizeEnergyPropDialog)
        self.body_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.body_frame.setObjectName("body_frame")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.body_frame)
        self.vboxlayout1.setMargin(3)
        self.vboxlayout1.setSpacing(3)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.sponsor_btn = QtGui.QPushButton(self.body_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.vboxlayout1.addWidget(self.sponsor_btn)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        spacerItem = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.done_btn = QtGui.QToolButton(self.body_frame)
        self.done_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image2"))
        self.done_btn.setObjectName("done_btn")
        self.hboxlayout1.addWidget(self.done_btn)

        self.abort_btn = QtGui.QToolButton(self.body_frame)
        self.abort_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image3"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout1.addWidget(self.abort_btn)

        self.restore_btn = QtGui.QToolButton(self.body_frame)
        self.restore_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image4"))
        self.restore_btn.setObjectName("restore_btn")
        self.hboxlayout1.addWidget(self.restore_btn)

        self.whatsthis_btn = QtGui.QToolButton(self.body_frame)
        self.whatsthis_btn.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image5"))
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout1.addWidget(self.whatsthis_btn)

        spacerItem1 = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.buttonGroup8 = QtGui.QGroupBox(self.body_frame)
        self.buttonGroup8.setObjectName("buttonGroup8")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.buttonGroup8)
        self.vboxlayout2.setMargin(4)
        self.vboxlayout2.setSpacing(1)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.min_options_label = QtGui.QLabel(self.buttonGroup8)
        self.min_options_label.setObjectName("min_options_label")
        self.hboxlayout2.addWidget(self.min_options_label)

        spacerItem2 = QtGui.QSpacerItem(21,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem2)

        self.grpbtn_1 = QtGui.QPushButton(self.buttonGroup8)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_1.sizePolicy().hasHeightForWidth())
        self.grpbtn_1.setSizePolicy(sizePolicy)
        self.grpbtn_1.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_1.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image6"))
        self.grpbtn_1.setAutoDefault(False)
        self.grpbtn_1.setFlat(True)
        self.grpbtn_1.setObjectName("grpbtn_1")
        self.hboxlayout2.addWidget(self.grpbtn_1)
        self.vboxlayout2.addLayout(self.hboxlayout2)

        self.line1 = QtGui.QFrame(self.buttonGroup8)
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setMidLineWidth(0)
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.vboxlayout2.addWidget(self.line1)

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
        self.vboxlayout1.addWidget(self.buttonGroup8)

        self.groupBox2 = QtGui.QGroupBox(self.body_frame)
        self.groupBox2.setObjectName("groupBox2")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.groupBox2)
        self.vboxlayout3.setMargin(4)
        self.vboxlayout3.setSpacing(1)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.watch_min_options_label = QtGui.QLabel(self.groupBox2)
        self.watch_min_options_label.setObjectName("watch_min_options_label")
        self.hboxlayout3.addWidget(self.watch_min_options_label)

        spacerItem3 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem3)

        self.grpbtn_2 = QtGui.QPushButton(self.groupBox2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_2.sizePolicy().hasHeightForWidth())
        self.grpbtn_2.setSizePolicy(sizePolicy)
        self.grpbtn_2.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_2.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image6"))
        self.grpbtn_2.setAutoDefault(False)
        self.grpbtn_2.setFlat(True)
        self.grpbtn_2.setObjectName("grpbtn_2")
        self.hboxlayout3.addWidget(self.grpbtn_2)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.line2 = QtGui.QFrame(self.groupBox2)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setMidLineWidth(0)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.vboxlayout3.addWidget(self.line2)

        self.watch_minimization_checkbox = QtGui.QCheckBox(self.groupBox2)
        self.watch_minimization_checkbox.setChecked(True)
        self.watch_minimization_checkbox.setObjectName("watch_minimization_checkbox")
        self.vboxlayout3.addWidget(self.watch_minimization_checkbox)

        self.update_btngrp = QtGui.QGroupBox(self.groupBox2)
        self.update_btngrp.setObjectName("update_btngrp")

        self.vboxlayout4 = QtGui.QVBoxLayout(self.update_btngrp)
        self.vboxlayout4.setMargin(3)
        self.vboxlayout4.setSpacing(1)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.watch_min_options_label_2 = QtGui.QLabel(self.update_btngrp)
        self.watch_min_options_label_2.setObjectName("watch_min_options_label_2")
        self.vboxlayout4.addWidget(self.watch_min_options_label_2)

        self.line2_1 = QtGui.QFrame(self.update_btngrp)
        self.line2_1.setFrameShape(QtGui.QFrame.HLine)
        self.line2_1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_1.setMidLineWidth(0)
        self.line2_1.setFrameShape(QtGui.QFrame.HLine)
        self.line2_1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2_1.setObjectName("line2_1")
        self.vboxlayout4.addWidget(self.line2_1)

        self.update_asap_rbtn = QtGui.QRadioButton(self.update_btngrp)
        self.update_asap_rbtn.setChecked(True)
        self.update_asap_rbtn.setObjectName("update_asap_rbtn")
        self.vboxlayout4.addWidget(self.update_asap_rbtn)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(0)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.update_every_rbtn = QtGui.QRadioButton(self.update_btngrp)
        self.update_every_rbtn.setObjectName("update_every_rbtn")
        self.hboxlayout4.addWidget(self.update_every_rbtn)

        self.update_number_spinbox = QtGui.QSpinBox(self.update_btngrp)
        self.update_number_spinbox.setMaximum(9999)
        self.update_number_spinbox.setMinimum(1)
        self.update_number_spinbox.setProperty("value",QtCore.QVariant(1))
        self.update_number_spinbox.setObjectName("update_number_spinbox")
        self.hboxlayout4.addWidget(self.update_number_spinbox)

        self.update_units_combobox = QtGui.QComboBox(self.update_btngrp)
        self.update_units_combobox.setObjectName("update_units_combobox")
        self.hboxlayout4.addWidget(self.update_units_combobox)

        spacerItem4 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem4)
        self.vboxlayout4.addLayout(self.hboxlayout4)
        self.vboxlayout3.addWidget(self.update_btngrp)
        self.vboxlayout1.addWidget(self.groupBox2)

        self.parms_grpbox = QtGui.QGroupBox(self.body_frame)
        self.parms_grpbox.setObjectName("parms_grpbox")

        self.vboxlayout5 = QtGui.QVBoxLayout(self.parms_grpbox)
        self.vboxlayout5.setMargin(4)
        self.vboxlayout5.setSpacing(1)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.parameters_label = QtGui.QLabel(self.parms_grpbox)
        self.parameters_label.setObjectName("parameters_label")
        self.hboxlayout5.addWidget(self.parameters_label)

        spacerItem5 = QtGui.QSpacerItem(21,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem5)

        self.grpbtn_3 = QtGui.QPushButton(self.parms_grpbox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_3.sizePolicy().hasHeightForWidth())
        self.grpbtn_3.setSizePolicy(sizePolicy)
        self.grpbtn_3.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_3.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image6"))
        self.grpbtn_3.setAutoDefault(False)
        self.grpbtn_3.setFlat(True)
        self.grpbtn_3.setObjectName("grpbtn_3")
        self.hboxlayout5.addWidget(self.grpbtn_3)
        self.vboxlayout5.addLayout(self.hboxlayout5)

        self.line3 = QtGui.QFrame(self.parms_grpbox)
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setMidLineWidth(0)
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setObjectName("line3")
        self.vboxlayout5.addWidget(self.line3)

        self.hboxlayout6 = QtGui.QHBoxLayout()
        self.hboxlayout6.setMargin(0)
        self.hboxlayout6.setSpacing(6)
        self.hboxlayout6.setObjectName("hboxlayout6")

        self.vboxlayout6 = QtGui.QVBoxLayout()
        self.vboxlayout6.setMargin(0)
        self.vboxlayout6.setSpacing(6)
        self.vboxlayout6.setObjectName("vboxlayout6")

        self.endrms_lbl = QtGui.QLabel(self.parms_grpbox)
        self.endrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endrms_lbl.setObjectName("endrms_lbl")
        self.vboxlayout6.addWidget(self.endrms_lbl)

        self.endmax_lbl = QtGui.QLabel(self.parms_grpbox)
        self.endmax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endmax_lbl.setObjectName("endmax_lbl")
        self.vboxlayout6.addWidget(self.endmax_lbl)

        self.cutoverrms_lbl = QtGui.QLabel(self.parms_grpbox)
        self.cutoverrms_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutoverrms_lbl.setObjectName("cutoverrms_lbl")
        self.vboxlayout6.addWidget(self.cutoverrms_lbl)

        self.cutovermax_lbl = QtGui.QLabel(self.parms_grpbox)
        self.cutovermax_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.cutovermax_lbl.setObjectName("cutovermax_lbl")
        self.vboxlayout6.addWidget(self.cutovermax_lbl)
        self.hboxlayout6.addLayout(self.vboxlayout6)

        self.vboxlayout7 = QtGui.QVBoxLayout()
        self.vboxlayout7.setMargin(0)
        self.vboxlayout7.setSpacing(6)
        self.vboxlayout7.setObjectName("vboxlayout7")

        self.endrms_linedit = QtGui.QLineEdit(self.parms_grpbox)
        self.endrms_linedit.setObjectName("endrms_linedit")
        self.vboxlayout7.addWidget(self.endrms_linedit)

        self.endmax_linedit = QtGui.QLineEdit(self.parms_grpbox)
        self.endmax_linedit.setObjectName("endmax_linedit")
        self.vboxlayout7.addWidget(self.endmax_linedit)

        self.cutoverrms_linedit = QtGui.QLineEdit(self.parms_grpbox)
        self.cutoverrms_linedit.setObjectName("cutoverrms_linedit")
        self.vboxlayout7.addWidget(self.cutoverrms_linedit)

        self.cutovermax_linedit = QtGui.QLineEdit(self.parms_grpbox)
        self.cutovermax_linedit.setObjectName("cutovermax_linedit")
        self.vboxlayout7.addWidget(self.cutovermax_linedit)
        self.hboxlayout6.addLayout(self.vboxlayout7)

        spacerItem6 = QtGui.QSpacerItem(40,1,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout6.addItem(spacerItem6)
        self.vboxlayout5.addLayout(self.hboxlayout6)
        self.vboxlayout1.addWidget(self.parms_grpbox)

        self.buttonGroup8_2 = QtGui.QGroupBox(self.body_frame)
        self.buttonGroup8_2.setObjectName("buttonGroup8_2")

        self.vboxlayout8 = QtGui.QVBoxLayout(self.buttonGroup8_2)
        self.vboxlayout8.setMargin(4)
        self.vboxlayout8.setSpacing(1)
        self.vboxlayout8.setObjectName("vboxlayout8")

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setMargin(0)
        self.hboxlayout7.setSpacing(6)
        self.hboxlayout7.setObjectName("hboxlayout7")

        self.min_options_label_4 = QtGui.QLabel(self.buttonGroup8_2)
        self.min_options_label_4.setObjectName("min_options_label_4")
        self.hboxlayout7.addWidget(self.min_options_label_4)

        spacerItem7 = QtGui.QSpacerItem(21,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout7.addItem(spacerItem7)

        self.grpbtn_4 = QtGui.QPushButton(self.buttonGroup8_2)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_4.sizePolicy().hasHeightForWidth())
        self.grpbtn_4.setSizePolicy(sizePolicy)
        self.grpbtn_4.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_4.setIcon(QtGui.QIcon("../../../../:icons/MinimizeEnergyPropDialog_image6"))
        self.grpbtn_4.setAutoDefault(False)
        self.grpbtn_4.setDefault(False)
        self.grpbtn_4.setFlat(True)
        self.grpbtn_4.setObjectName("grpbtn_4")
        self.hboxlayout7.addWidget(self.grpbtn_4)
        self.vboxlayout8.addLayout(self.hboxlayout7)

        self.line4 = QtGui.QFrame(self.buttonGroup8_2)
        self.line4.setFrameShape(QtGui.QFrame.HLine)
        self.line4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line4.setMidLineWidth(0)
        self.line4.setFrameShape(QtGui.QFrame.HLine)
        self.line4.setFrameShadow(QtGui.QFrame.Sunken)
        self.line4.setObjectName("line4")
        self.vboxlayout8.addWidget(self.line4)

        self.minimize_engine_combobox = QtGui.QComboBox(self.buttonGroup8_2)
        self.minimize_engine_combobox.setObjectName("minimize_engine_combobox")
        self.vboxlayout8.addWidget(self.minimize_engine_combobox)
        self.vboxlayout1.addWidget(self.buttonGroup8_2)
        self.vboxlayout.addWidget(self.body_frame)

        spacerItem8 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem8)

        self.hboxlayout8 = QtGui.QHBoxLayout()
        self.hboxlayout8.setMargin(4)
        self.hboxlayout8.setSpacing(6)
        self.hboxlayout8.setObjectName("hboxlayout8")

        spacerItem9 = QtGui.QSpacerItem(59,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout8.addItem(spacerItem9)

        self.cancel_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout8.addWidget(self.cancel_btn)

        self.ok_btn = QtGui.QPushButton(MinimizeEnergyPropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout8.addWidget(self.ok_btn)
        self.vboxlayout.addLayout(self.hboxlayout8)

        self.retranslateUi(MinimizeEnergyPropDialog)
        QtCore.QObject.connect(self.watch_minimization_checkbox,QtCore.SIGNAL("toggled(bool)"),self.update_btngrp.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(MinimizeEnergyPropDialog)

    def retranslateUi(self, MinimizeEnergyPropDialog):
        MinimizeEnergyPropDialog.setWindowTitle(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.heading_label.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.whatsthis_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "What\'s This Help", None, QtGui.QApplication.UnicodeUTF8))
        self.min_options_label.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Options", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on all the atoms in the workspace", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_all_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize All", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Perform energy minimization on only the atoms that have been selected", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_sel_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Selection", None, QtGui.QApplication.UnicodeUTF8))
        self.electrostaticsForDnaDuringMinimize_checkBox.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Electrostatics for DNA Reduced Model", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_min_options_label.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Watch Minimization Options", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_minimization_checkbox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Enables real time graphical updates during minimization runs", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_minimization_checkbox.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Watch minimization in real time", None, QtGui.QApplication.UnicodeUTF8))
        self.watch_min_options_label_2.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Update Options", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Update every 2 seconds, or faster if it doesn\'t slow minimization by more than 20%", None, QtGui.QApplication.UnicodeUTF8))
        self.update_asap_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "As fast as possible", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during the minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_every_rbtn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Every", None, QtGui.QApplication.UnicodeUTF8))
        self.update_number_spinbox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during the minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Specify how often to update the screen during the minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "frames", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "minutes", None, QtGui.QApplication.UnicodeUTF8))
        self.update_units_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "hours", None, QtGui.QApplication.UnicodeUTF8))
        self.parameters_label.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Convergence Criteria", None, QtGui.QApplication.UnicodeUTF8))
        self.endrms_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "EndRMS (pN) :", None, QtGui.QApplication.UnicodeUTF8))
        self.endmax_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "EndMax (pN) :", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverrms_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "CutoverRMS (pN) :", None, QtGui.QApplication.UnicodeUTF8))
        self.cutovermax_lbl.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "CutoverMax (pN) :", None, QtGui.QApplication.UnicodeUTF8))
        self.endrms_linedit.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Target RMS force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.endrms_linedit.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "1.0", None, QtGui.QApplication.UnicodeUTF8))
        self.endmax_linedit.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Target max force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.cutoverrms_linedit.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cutover RMS foce (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.cutovermax_linedit.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cutover max force (pN)", None, QtGui.QApplication.UnicodeUTF8))
        self.min_options_label_4.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Engine", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Choose the simulation engine with which to minimize energy.", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "NanoDynamics-1 (Default)", None, QtGui.QApplication.UnicodeUTF8))
        self.minimize_engine_combobox.addItem(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "GROMACS - SDN p-atom force-field", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setToolTip(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("MinimizeEnergyPropDialog", "Minimize Energy", None, QtGui.QApplication.UnicodeUTF8))

