# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'StatPropDialog.ui'
#
# Created: Wed Sep 20 09:07:17 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_StatPropDialog(object):
    def setupUi(self, StatPropDialog):
        StatPropDialog.setObjectName("StatPropDialog")
        StatPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,299,202).size()).expandedTo(StatPropDialog.minimumSizeHint()))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(StatPropDialog.sizePolicy().hasHeightForWidth())
        StatPropDialog.setSizePolicy(sizePolicy)
        StatPropDialog.setSizeGripEnabled(True)

        self.vboxlayout = QtGui.QVBoxLayout(StatPropDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.nameTextLabel = QtGui.QLabel(StatPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nameTextLabel.sizePolicy().hasHeightForWidth())
        self.nameTextLabel.setSizePolicy(sizePolicy)
        self.nameTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nameTextLabel.setObjectName("nameTextLabel")
        self.vboxlayout1.addWidget(self.nameTextLabel)

        self.temp_lbl = QtGui.QLabel(StatPropDialog)
        self.temp_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.temp_lbl.setObjectName("temp_lbl")
        self.vboxlayout1.addWidget(self.temp_lbl)

        self.molnameTextLabel = QtGui.QLabel(StatPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.molnameTextLabel.sizePolicy().hasHeightForWidth())
        self.molnameTextLabel.setSizePolicy(sizePolicy)
        self.molnameTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.molnameTextLabel.setObjectName("molnameTextLabel")
        self.vboxlayout1.addWidget(self.molnameTextLabel)

        self.colorTextLabel = QtGui.QLabel(StatPropDialog)
        self.colorTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel.setObjectName("colorTextLabel")
        self.vboxlayout1.addWidget(self.colorTextLabel)
        self.hboxlayout.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.nameLineEdit = QtGui.QLineEdit(StatPropDialog)
        self.nameLineEdit.setEnabled(True)
        self.nameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.vboxlayout2.addWidget(self.nameLineEdit)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.tempSpinBox = QtGui.QSpinBox(StatPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tempSpinBox.sizePolicy().hasHeightForWidth())
        self.tempSpinBox.setSizePolicy(sizePolicy)
        self.tempSpinBox.setMaximum(9999)
        self.tempSpinBox.setProperty("value",QtCore.QVariant(300))
        self.tempSpinBox.setObjectName("tempSpinBox")
        self.hboxlayout2.addWidget(self.tempSpinBox)

        self.K_lbl = QtGui.QLabel(StatPropDialog)
        self.K_lbl.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.K_lbl.setObjectName("K_lbl")
        self.hboxlayout2.addWidget(self.K_lbl)
        self.hboxlayout1.addLayout(self.hboxlayout2)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout2.addLayout(self.hboxlayout1)

        self.molnameLineEdit = QtGui.QLineEdit(StatPropDialog)
        self.molnameLineEdit.setEnabled(True)
        self.molnameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.molnameLineEdit.setReadOnly(True)
        self.molnameLineEdit.setObjectName("molnameLineEdit")
        self.vboxlayout2.addWidget(self.molnameLineEdit)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.jig_color_pixmap = QtGui.QLabel(StatPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.jig_color_pixmap.sizePolicy().hasHeightForWidth())
        self.jig_color_pixmap.setSizePolicy(sizePolicy)
        self.jig_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.jig_color_pixmap.setScaledContents(True)
        self.jig_color_pixmap.setObjectName("jig_color_pixmap")
        self.hboxlayout4.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QtGui.QPushButton(StatPropDialog)
        self.choose_color_btn.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(1),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_color_btn.sizePolicy().hasHeightForWidth())
        self.choose_color_btn.setSizePolicy(sizePolicy)
        self.choose_color_btn.setAutoDefault(False)
        self.choose_color_btn.setObjectName("choose_color_btn")
        self.hboxlayout4.addWidget(self.choose_color_btn)
        self.hboxlayout3.addLayout(self.hboxlayout4)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem1)
        self.vboxlayout2.addLayout(self.hboxlayout3)
        self.hboxlayout.addLayout(self.vboxlayout2)
        self.vboxlayout.addLayout(self.hboxlayout)

        spacerItem2 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem2)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        spacerItem3 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem3)

        self.ok_btn = QtGui.QPushButton(StatPropDialog)
        self.ok_btn.setMinimumSize(QtCore.QSize(0,0))
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout5.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(StatPropDialog)
        self.cancel_btn.setMinimumSize(QtCore.QSize(0,0))
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout5.addWidget(self.cancel_btn)
        self.vboxlayout.addLayout(self.hboxlayout5)

        self.retranslateUi(StatPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),StatPropDialog.reject)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),StatPropDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(StatPropDialog)
        StatPropDialog.setTabOrder(self.nameLineEdit,self.tempSpinBox)
        StatPropDialog.setTabOrder(self.tempSpinBox,self.molnameLineEdit)
        StatPropDialog.setTabOrder(self.molnameLineEdit,self.choose_color_btn)
        StatPropDialog.setTabOrder(self.choose_color_btn,self.ok_btn)
        StatPropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, StatPropDialog):
        StatPropDialog.setWindowTitle(QtGui.QApplication.translate("StatPropDialog", "Stat Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.nameTextLabel.setText(QtGui.QApplication.translate("StatPropDialog", "Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.temp_lbl.setText(QtGui.QApplication.translate("StatPropDialog", "Temperature :", None, QtGui.QApplication.UnicodeUTF8))
        self.molnameTextLabel.setText(QtGui.QApplication.translate("StatPropDialog", "Attached to :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel.setText(QtGui.QApplication.translate("StatPropDialog", "Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.K_lbl.setText(QtGui.QApplication.translate("StatPropDialog", "Kelvin", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setToolTip(QtGui.QApplication.translate("StatPropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setText(QtGui.QApplication.translate("StatPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("StatPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("StatPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("StatPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("StatPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
