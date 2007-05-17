# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'AboutDialog.ui'
#
# Created: Wed Sep 20 09:55:12 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(QtCore.QSize(QtCore.QRect(0,0,322,261).size()).expandedTo(AboutDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(AboutDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.pixmapLabel2 = QtGui.QLabel(AboutDialog)
        self.pixmapLabel2.setScaledContents(True)
        self.pixmapLabel2.setObjectName("pixmapLabel2")
        self.vboxlayout.addWidget(self.pixmapLabel2)

        self.textLabel1 = QtGui.QLabel(AboutDialog)
        self.textLabel1.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout.addWidget(self.textLabel1)

        self.textLabel2 = QtGui.QLabel(AboutDialog)
        self.textLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel2.setObjectName("textLabel2")
        self.vboxlayout.addWidget(self.textLabel2)

        self.textLabel2_2 = QtGui.QLabel(AboutDialog)
        self.textLabel2_2.setAlignment(QtCore.Qt.AlignCenter)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.vboxlayout.addWidget(self.textLabel2_2)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.okPushButton = QtGui.QPushButton(AboutDialog)
        self.okPushButton.setObjectName("okPushButton")
        self.hboxlayout.addWidget(self.okPushButton)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(AboutDialog)
        QtCore.QObject.connect(self.okPushButton,QtCore.SIGNAL("clicked()"),AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QtGui.QApplication.translate("AboutDialog", "About NanoEngineer-1", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("AboutDialog", "NanoEngineer-1 Version 1.0 (Alpha)", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("AboutDialog", "Copyright 2004-2007, Nanorex, Inc.", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("AboutDialog", "www.nanorex.com", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setText(QtGui.QApplication.translate("AboutDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
