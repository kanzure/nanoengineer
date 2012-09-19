# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'RotaryMotorPropDialog.ui'
#
# Created: Wed Sep 20 10:35:36 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_RotaryMotorPropDialog(object):
    def setupUi(self, RotaryMotorPropDialog):
        RotaryMotorPropDialog.setObjectName("RotaryMotorPropDialog")
        RotaryMotorPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,298,424).size()).expandedTo(RotaryMotorPropDialog.minimumSizeHint()))
        #RotaryMotorPropDialog.setSizeGripEnabled(True)

        self.vboxlayout = QtGui.QVBoxLayout(RotaryMotorPropDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.nameTextLabel = QtGui.QLabel(RotaryMotorPropDialog)
        self.nameTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nameTextLabel.setObjectName("nameTextLabel")
        self.vboxlayout1.addWidget(self.nameTextLabel)

        self.textLabel1 = QtGui.QLabel(RotaryMotorPropDialog)

        font = QtGui.QFont(self.textLabel1.font())
        font.setFamily("Sans Serif")
        font.setPointSize(9)
        font.setWeight(50)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(False)
        self.textLabel1.setFont(font)
        self.textLabel1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout1.addWidget(self.textLabel1)

        self.textLabel1_2_3 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel1_2_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_3.setObjectName("textLabel1_2_3")
        self.vboxlayout1.addWidget(self.textLabel1_2_3)

        self.textLabel1_2 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel1_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.vboxlayout1.addWidget(self.textLabel1_2)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.nameLineEdit = QtGui.QLineEdit(RotaryMotorPropDialog)
        self.nameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.nameLineEdit.setReadOnly(False)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.gridlayout.addWidget(self.nameLineEdit,0,0,1,2)

        self.torqueLineEdit = QtGui.QLineEdit(RotaryMotorPropDialog)
        self.torqueLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.torqueLineEdit.setObjectName("torqueLineEdit")
        self.gridlayout.addWidget(self.torqueLineEdit,1,0,1,1)

        self.speedLineEdit = QtGui.QLineEdit(RotaryMotorPropDialog)
        self.speedLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.speedLineEdit.setObjectName("speedLineEdit")
        self.gridlayout.addWidget(self.speedLineEdit,3,0,1,1)

        self.textLabel1_4 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.gridlayout.addWidget(self.textLabel1_4,1,1,1,1)

        self.textLabel2 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel2.setObjectName("textLabel2")
        self.gridlayout.addWidget(self.textLabel2,3,1,1,1)

        self.textLabel2_2 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.gridlayout.addWidget(self.textLabel2_2,2,1,1,1)

        self.initialSpeedLineEdit = QtGui.QLineEdit(RotaryMotorPropDialog)
        self.initialSpeedLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.initialSpeedLineEdit.setObjectName("initialSpeedLineEdit")
        self.gridlayout.addWidget(self.initialSpeedLineEdit,2,0,1,1)
        self.hboxlayout1.addLayout(self.gridlayout)
        self.hboxlayout.addLayout(self.hboxlayout1)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.dampers_textlabel = QtGui.QLabel(RotaryMotorPropDialog)
        self.dampers_textlabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.dampers_textlabel.setObjectName("dampers_textlabel")
        self.vboxlayout2.addWidget(self.dampers_textlabel)

        self.textLabel1_5 = QtGui.QLabel(RotaryMotorPropDialog)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.vboxlayout2.addWidget(self.textLabel1_5)
        self.hboxlayout2.addLayout(self.vboxlayout2)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.dampers_checkbox = QtGui.QCheckBox(RotaryMotorPropDialog)
        self.dampers_checkbox.setObjectName("dampers_checkbox")
        self.vboxlayout3.addWidget(self.dampers_checkbox)

        self.enable_minimize_checkbox = QtGui.QCheckBox(RotaryMotorPropDialog)
        self.enable_minimize_checkbox.setObjectName("enable_minimize_checkbox")
        self.vboxlayout3.addWidget(self.enable_minimize_checkbox)
        self.hboxlayout2.addLayout(self.vboxlayout3)

        spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem1)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.groupBox1 = QtGui.QGroupBox(RotaryMotorPropDialog)
        self.groupBox1.setObjectName("groupBox1")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox1)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.jig_color_pixmap = QtGui.QLabel(self.groupBox1)
        self.jig_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.jig_color_pixmap.setScaledContents(True)
        self.jig_color_pixmap.setObjectName("jig_color_pixmap")
        self.hboxlayout4.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QtGui.QPushButton(self.groupBox1)
        self.choose_color_btn.setEnabled(True)
        self.choose_color_btn.setAutoDefault(False)
        self.choose_color_btn.setObjectName("choose_color_btn")
        self.hboxlayout4.addWidget(self.choose_color_btn)
        self.hboxlayout3.addLayout(self.hboxlayout4)

        spacerItem2 = QtGui.QSpacerItem(46,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem2)
        self.gridlayout1.addLayout(self.hboxlayout3,3,1,1,2)

        self.textLabel1_2_2_2 = QtGui.QLabel(self.groupBox1)
        self.textLabel1_2_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2_2.setObjectName("textLabel1_2_2_2")
        self.gridlayout1.addWidget(self.textLabel1_2_2_2,2,0,1,1)

        self.textLabel1_3 = QtGui.QLabel(self.groupBox1)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.gridlayout1.addWidget(self.textLabel1_3,0,0,1,1)

        self.textLabel1_2_2 = QtGui.QLabel(self.groupBox1)
        self.textLabel1_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.gridlayout1.addWidget(self.textLabel1_2_2,1,0,1,1)

        self.colorTextLabel = QtGui.QLabel(self.groupBox1)
        self.colorTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel.setObjectName("colorTextLabel")
        self.gridlayout1.addWidget(self.colorTextLabel,3,0,1,1)

        self.lengthLineEdit = QtGui.QLineEdit(self.groupBox1)
        self.lengthLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.lengthLineEdit.setObjectName("lengthLineEdit")
        self.gridlayout1.addWidget(self.lengthLineEdit,0,1,1,1)

        self.sradiusLineEdit = QtGui.QLineEdit(self.groupBox1)
        self.sradiusLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.sradiusLineEdit.setObjectName("sradiusLineEdit")
        self.gridlayout1.addWidget(self.sradiusLineEdit,2,1,1,1)

        self.radiusLineEdit = QtGui.QLineEdit(self.groupBox1)
        self.radiusLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.radiusLineEdit.setObjectName("radiusLineEdit")
        self.gridlayout1.addWidget(self.radiusLineEdit,1,1,1,1)

        self.textLabel3_2 = QtGui.QLabel(self.groupBox1)
        self.textLabel3_2.setObjectName("textLabel3_2")
        self.gridlayout1.addWidget(self.textLabel3_2,1,2,1,1)

        self.textLabel3 = QtGui.QLabel(self.groupBox1)
        self.textLabel3.setObjectName("textLabel3")
        self.gridlayout1.addWidget(self.textLabel3,0,2,1,1)

        self.textLabel3_3 = QtGui.QLabel(self.groupBox1)
        self.textLabel3_3.setObjectName("textLabel3_3")
        self.gridlayout1.addWidget(self.textLabel3_3,2,2,1,1)
        self.vboxlayout.addWidget(self.groupBox1)

        spacerItem3 = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem3)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        spacerItem4 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem4)

        self.ok_btn = QtGui.QPushButton(RotaryMotorPropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout5.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(RotaryMotorPropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout5.addWidget(self.cancel_btn)
        self.vboxlayout.addLayout(self.hboxlayout5)
        #self.textLabel1.setBuddy(RotaryMotorPropDialog.lineEdit9)
        #self.textLabel1_2_3.setBuddy(RotaryMotorPropDialog.lineEdit9_2)
        #self.textLabel1_2.setBuddy(RotaryMotorPropDialog.lineEdit9_2)

        self.retranslateUi(RotaryMotorPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),RotaryMotorPropDialog.reject)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),RotaryMotorPropDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(RotaryMotorPropDialog)
        RotaryMotorPropDialog.setTabOrder(self.nameLineEdit,self.torqueLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.torqueLineEdit,self.initialSpeedLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.initialSpeedLineEdit,self.speedLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.speedLineEdit,self.enable_minimize_checkbox)
        RotaryMotorPropDialog.setTabOrder(self.enable_minimize_checkbox,self.lengthLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.lengthLineEdit,self.radiusLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.radiusLineEdit,self.sradiusLineEdit)
        RotaryMotorPropDialog.setTabOrder(self.sradiusLineEdit,self.choose_color_btn)
        RotaryMotorPropDialog.setTabOrder(self.choose_color_btn,self.ok_btn)
        RotaryMotorPropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, RotaryMotorPropDialog):
        RotaryMotorPropDialog.setWindowTitle(QtGui.QApplication.translate("RotaryMotorPropDialog", "Rotary Motor Properties", None, QtGui.QApplication.UnicodeUTF8))
        RotaryMotorPropDialog.setWindowIcon(QtGui.QIcon("ui/border/RotaryMotor"))
        self.nameTextLabel.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Torque :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_3.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Initial Speed :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Final Speed :", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLineEdit.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "Name of rotary motor.", None, QtGui.QApplication.UnicodeUTF8))
        self.torqueLineEdit.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "Simulations will begin with the motor\'s torque set to this value.", None, QtGui.QApplication.UnicodeUTF8))
        self.speedLineEdit.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "The final velocity of the motor\'s flywheel.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "nN-nm", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "GHz", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "GHz", None, QtGui.QApplication.UnicodeUTF8))
        self.initialSpeedLineEdit.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "The beginning velocity of the motor\'s flywheel.", None, QtGui.QApplication.UnicodeUTF8))
        self.dampers_textlabel.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "If checked, dampers are enabled in the simulator.", None, QtGui.QApplication.UnicodeUTF8))
        self.dampers_textlabel.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Dampers :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "If checked, the torque value is applied to the motor\'s atoms during minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Enable in Minimize (experimental) :", None, QtGui.QApplication.UnicodeUTF8))
        self.dampers_checkbox.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "If checked, dampers are enabled in the simulator.", None, QtGui.QApplication.UnicodeUTF8))
        self.enable_minimize_checkbox.setToolTip(QtGui.QApplication.translate("RotaryMotorPropDialog", "If checked, the torque value is applied to the motor\'s atoms during minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox1.setTitle(QtGui.QApplication.translate("RotaryMotorPropDialog", "Size and Color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2_2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Spoke Radius :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Motor Length :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Motor Radius :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3_2.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3_3.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("RotaryMotorPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("RotaryMotorPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("RotaryMotorPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
