# -*- coding: utf-8 -*-

# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'JigPropDialog.ui'
#
# Created: Wed Sep 20 07:56:23 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_JigPropDialog(object):
    def setupUi(self, JigPropDialog):
        JigPropDialog.setObjectName("JigPropDialog")
        JigPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,245,145).size()).expandedTo(JigPropDialog.minimumSizeHint()))
        JigPropDialog.setSizeGripEnabled(True)

        self.vboxlayout = QtGui.QVBoxLayout(JigPropDialog)
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

        self.nameTextLabel = QtGui.QLabel(JigPropDialog)
        self.nameTextLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nameTextLabel.setObjectName("nameTextLabel")
        self.vboxlayout1.addWidget(self.nameTextLabel)

        self.colorTextLabel = QtGui.QLabel(JigPropDialog)
        self.colorTextLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.colorTextLabel.setObjectName("colorTextLabel")
        self.vboxlayout1.addWidget(self.colorTextLabel)
        self.hboxlayout.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.nameLineEdit = QtGui.QLineEdit(JigPropDialog)
        self.nameLineEdit.setEnabled(True)
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

        self.jig_color_pixmap = QtGui.QLabel(JigPropDialog)
        self.jig_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.jig_color_pixmap.setScaledContents(True)
        self.jig_color_pixmap.setObjectName("jig_color_pixmap")
        self.hboxlayout2.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QtGui.QPushButton(JigPropDialog)
        self.choose_color_btn.setEnabled(True)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.choose_color_btn.sizePolicy().hasHeightForWidth())
        self.choose_color_btn.setSizePolicy(sizePolicy)
        self.choose_color_btn.setObjectName("choose_color_btn")
        self.hboxlayout2.addWidget(self.choose_color_btn)
        self.hboxlayout1.addLayout(self.hboxlayout2)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout2.addLayout(self.hboxlayout1)
        self.hboxlayout.addLayout(self.vboxlayout2)
        self.vboxlayout.addLayout(self.hboxlayout)

        spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem1)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem2)

        self.ok_btn = QtGui.QPushButton(JigPropDialog)
        self.ok_btn.setAutoDefault(True)
        self.ok_btn.setDefault(True)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout3.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(JigPropDialog)
        self.cancel_btn.setAutoDefault(True)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout3.addWidget(self.cancel_btn)
        self.vboxlayout.addLayout(self.hboxlayout3)

        self.retranslateUi(JigPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),JigPropDialog.reject)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),JigPropDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(JigPropDialog)
        JigPropDialog.setTabOrder(self.nameLineEdit,self.choose_color_btn)
        JigPropDialog.setTabOrder(self.choose_color_btn,self.ok_btn)
        JigPropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, JigPropDialog):
        JigPropDialog.setWindowTitle(QtGui.QApplication.translate("JigPropDialog", "Jig Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.nameTextLabel.setText(QtGui.QApplication.translate("JigPropDialog", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel.setText(QtGui.QApplication.translate("JigPropDialog", "Color:", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setToolTip(QtGui.QApplication.translate("JigPropDialog", "Change Color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_color_btn.setText(QtGui.QApplication.translate("JigPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("JigPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("JigPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("JigPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("JigPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
