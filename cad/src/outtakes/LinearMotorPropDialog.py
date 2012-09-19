# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'LinearMotorPropDialog.ui'
#
# Created: Wed Sep 20 10:14:34 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LinearMotorPropDialog(object):
    def setupUi(self, LinearMotorPropDialog):
        LinearMotorPropDialog.setObjectName("LinearMotorPropDialog")
        LinearMotorPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,295,372).size()).expandedTo(LinearMotorPropDialog.minimumSizeHint()))
        LinearMotorPropDialog.setSizeGripEnabled(True)

        self.gridlayout = QtGui.QGridLayout(LinearMotorPropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox3 = QtGui.QGroupBox(LinearMotorPropDialog)
        self.groupBox3.setObjectName("groupBox3")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox3)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.widthLineEdit = QtGui.QLineEdit(self.groupBox3)
        self.widthLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.widthLineEdit.setObjectName("widthLineEdit")
        self.gridlayout1.addWidget(self.widthLineEdit,1,1,1,1)

        self.textLabel3 = QtGui.QLabel(self.groupBox3)
        self.textLabel3.setObjectName("textLabel3")
        self.gridlayout1.addWidget(self.textLabel3,0,2,1,1)

        self.sradiusLineEdit = QtGui.QLineEdit(self.groupBox3)
        self.sradiusLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.sradiusLineEdit.setObjectName("sradiusLineEdit")
        self.gridlayout1.addWidget(self.sradiusLineEdit,2,1,1,1)

        self.lengthLineEdit = QtGui.QLineEdit(self.groupBox3)
        self.lengthLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.lengthLineEdit.setObjectName("lengthLineEdit")
        self.gridlayout1.addWidget(self.lengthLineEdit,0,1,1,1)

        self.textLabel3_3 = QtGui.QLabel(self.groupBox3)
        self.textLabel3_3.setObjectName("textLabel3_3")
        self.gridlayout1.addWidget(self.textLabel3_3,2,2,1,1)

        self.textLabel3_2 = QtGui.QLabel(self.groupBox3)
        self.textLabel3_2.setObjectName("textLabel3_2")
        self.gridlayout1.addWidget(self.textLabel3_2,1,2,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.jig_color_pixmap = QtGui.QLabel(self.groupBox3)
        self.jig_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.jig_color_pixmap.setScaledContents(True)
        self.jig_color_pixmap.setObjectName("jig_color_pixmap")
        self.hboxlayout1.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QtGui.QPushButton(self.groupBox3)
        self.choose_color_btn.setEnabled(True)
        self.choose_color_btn.setAutoDefault(False)
        self.choose_color_btn.setObjectName("choose_color_btn")
        self.hboxlayout1.addWidget(self.choose_color_btn)
        self.hboxlayout.addLayout(self.hboxlayout1)

        spacerItem = QtGui.QSpacerItem(46,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.gridlayout1.addLayout(self.hboxlayout,3,1,1,2)

        self.textLabel1_3 = QtGui.QLabel(self.groupBox3)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.gridlayout1.addWidget(self.textLabel1_3,0,0,1,1)

        self.textLabel1_2_2 = QtGui.QLabel(self.groupBox3)
        self.textLabel1_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.gridlayout1.addWidget(self.textLabel1_2_2,1,0,1,1)

        self.textLabel1_2_2_2 = QtGui.QLabel(self.groupBox3)
        self.textLabel1_2_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2_2.setObjectName("textLabel1_2_2_2")
        self.gridlayout1.addWidget(self.textLabel1_2_2_2,2,0,1,1)

        self.colorTextLabel = QtGui.QLabel(self.groupBox3)
        self.colorTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel.setObjectName("colorTextLabel")
        self.gridlayout1.addWidget(self.colorTextLabel,3,0,1,1)
        self.gridlayout.addWidget(self.groupBox3,2,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem1,3,0,1,1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem2)

        self.ok_btn = QtGui.QPushButton(LinearMotorPropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout2.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(LinearMotorPropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout2.addWidget(self.cancel_btn)
        self.gridlayout.addLayout(self.hboxlayout2,4,0,1,1)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.nameTextLabel = QtGui.QLabel(LinearMotorPropDialog)
        self.nameTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nameTextLabel.setObjectName("nameTextLabel")
        self.vboxlayout.addWidget(self.nameTextLabel)

        self.textLabel1 = QtGui.QLabel(LinearMotorPropDialog)

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
        self.vboxlayout.addWidget(self.textLabel1)

        self.textLabel1_2 = QtGui.QLabel(LinearMotorPropDialog)
        self.textLabel1_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.vboxlayout.addWidget(self.textLabel1_2)
        self.hboxlayout3.addLayout(self.vboxlayout)

        self.gridlayout2 = QtGui.QGridLayout()
        self.gridlayout2.setMargin(0)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.forceLineEdit = QtGui.QLineEdit(LinearMotorPropDialog)
        self.forceLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.forceLineEdit.setObjectName("forceLineEdit")
        self.gridlayout2.addWidget(self.forceLineEdit,1,0,1,1)

        self.textLabel2 = QtGui.QLabel(LinearMotorPropDialog)
        self.textLabel2.setObjectName("textLabel2")
        self.gridlayout2.addWidget(self.textLabel2,2,1,1,1)

        self.textLabel1_4 = QtGui.QLabel(LinearMotorPropDialog)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.gridlayout2.addWidget(self.textLabel1_4,1,1,1,1)

        self.nameLineEdit = QtGui.QLineEdit(LinearMotorPropDialog)
        self.nameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.nameLineEdit.setReadOnly(False)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.gridlayout2.addWidget(self.nameLineEdit,0,0,1,2)

        self.stiffnessLineEdit = QtGui.QLineEdit(LinearMotorPropDialog)
        self.stiffnessLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.stiffnessLineEdit.setObjectName("stiffnessLineEdit")
        self.gridlayout2.addWidget(self.stiffnessLineEdit,2,0,1,1)
        self.hboxlayout3.addLayout(self.gridlayout2)

        spacerItem3 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem3)
        self.gridlayout.addLayout(self.hboxlayout3,0,0,1,1)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.textLabel1_5 = QtGui.QLabel(LinearMotorPropDialog)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.hboxlayout4.addWidget(self.textLabel1_5)

        self.enable_minimize_checkbox = QtGui.QCheckBox(LinearMotorPropDialog)
        self.enable_minimize_checkbox.setObjectName("enable_minimize_checkbox")
        self.hboxlayout4.addWidget(self.enable_minimize_checkbox)

        spacerItem4 = QtGui.QSpacerItem(92,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem4)
        self.gridlayout.addLayout(self.hboxlayout4,1,0,1,1)
        #self.textLabel1.setBuddy(LinearMotorPropDialog.lineEdit9)
        #self.textLabel1_2.setBuddy(LinearMotorPropDialog.lineEdit9_2)

        self.retranslateUi(LinearMotorPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),LinearMotorPropDialog.reject)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),LinearMotorPropDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(LinearMotorPropDialog)
        LinearMotorPropDialog.setTabOrder(self.nameLineEdit,self.forceLineEdit)
        LinearMotorPropDialog.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        LinearMotorPropDialog.setTabOrder(self.stiffnessLineEdit,self.enable_minimize_checkbox)
        LinearMotorPropDialog.setTabOrder(self.enable_minimize_checkbox,self.lengthLineEdit)
        LinearMotorPropDialog.setTabOrder(self.lengthLineEdit,self.widthLineEdit)
        LinearMotorPropDialog.setTabOrder(self.widthLineEdit,self.sradiusLineEdit)
        LinearMotorPropDialog.setTabOrder(self.sradiusLineEdit,self.choose_color_btn)
        LinearMotorPropDialog.setTabOrder(self.choose_color_btn,self.ok_btn)
        LinearMotorPropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, LinearMotorPropDialog):
        LinearMotorPropDialog.setWindowTitle(QtGui.QApplication.translate("LinearMotorPropDialog", "Linear Motor Properties", None, QtGui.QApplication.UnicodeUTF8))
        LinearMotorPropDialog.setWindowIcon(QtGui.QIcon("ui/border/LinearMotor"))
        self.groupBox3.setTitle(QtGui.QApplication.translate("LinearMotorPropDialog", "Size and Color", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3_3.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel3_2.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Motor Length:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Motor Width:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2_2.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Spoke Radius:", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Color:", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("LinearMotorPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("LinearMotorPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.nameTextLabel.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Force:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Stiffness:", None, QtGui.QApplication.UnicodeUTF8))
        self.forceLineEdit.setToolTip(QtGui.QApplication.translate("LinearMotorPropDialog", "Simulations will begin with the motor\'s force set to this value.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "N/m", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "pN", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLineEdit.setToolTip(QtGui.QApplication.translate("LinearMotorPropDialog", "Name of Linear Motor", None, QtGui.QApplication.UnicodeUTF8))
        self.stiffnessLineEdit.setToolTip(QtGui.QApplication.translate("LinearMotorPropDialog", "Simulations will begin with the motor\'s stiffness set to this value.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setToolTip(QtGui.QApplication.translate("LinearMotorPropDialog", "If checked, the force value is applied to the motor\'s atoms during minimization.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("LinearMotorPropDialog", "Enable in Minimize (experimental) :", None, QtGui.QApplication.UnicodeUTF8))
        self.enable_minimize_checkbox.setToolTip(QtGui.QApplication.translate("LinearMotorPropDialog", "If checked, the force value is applied to the motor\'s atoms during minimization.", None, QtGui.QApplication.UnicodeUTF8))
