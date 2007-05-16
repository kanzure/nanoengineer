# -*- coding: utf-8 -*-

# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'ProgressBarDialog.ui'
#
# Created: Wed Sep 20 07:51:54 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ProgressBarDialog(object):
    def setupUi(self, ProgressBarDialog):
        ProgressBarDialog.setObjectName("ProgressBarDialog")
        ProgressBarDialog.resize(QtCore.QSize(QtCore.QRect(0,0,348,186).size()).expandedTo(ProgressBarDialog.minimumSizeHint()))
        ProgressBarDialog.setFocusPolicy(QtCore.Qt.NoFocus)

        self.vboxlayout = QtGui.QVBoxLayout(ProgressBarDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.msgLabel = QtGui.QLabel(ProgressBarDialog)
        self.msgLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.msgLabel.setObjectName("msgLabel")
        self.vboxlayout1.addWidget(self.msgLabel)

        self.progress = QtGui.QProgressBar(ProgressBarDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progress.sizePolicy().hasHeightForWidth())
        self.progress.setSizePolicy(sizePolicy)
        self.progress.setTotalSteps(0)
        self.progress.setObjectName("progress")
        self.vboxlayout1.addWidget(self.progress)
        self.vboxlayout.addLayout(self.vboxlayout1)

        self.msgLabel2 = QtGui.QLabel(ProgressBarDialog)
        self.msgLabel2.setAlignment(QtCore.Qt.AlignCenter)
        self.msgLabel2.setObjectName("msgLabel2")
        self.vboxlayout.addWidget(self.msgLabel2)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(91,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.abortPB = QtGui.QPushButton(ProgressBarDialog)
        self.abortPB.setFocusPolicy(QtCore.Qt.TabFocus)
        self.abortPB.setObjectName("abortPB")
        self.hboxlayout.addWidget(self.abortPB)

        spacerItem1 = QtGui.QSpacerItem(91,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(ProgressBarDialog)
        QtCore.QMetaObject.connectSlotsByName(ProgressBarDialog)

    def retranslateUi(self, ProgressBarDialog):
        ProgressBarDialog.setWindowTitle(QtGui.QApplication.translate("ProgressBarDialog", "Adjust", None, QtGui.QApplication.UnicodeUTF8))
        self.msgLabel.setText(QtGui.QApplication.translate("ProgressBarDialog", "Calculating.  Please wait...", None, QtGui.QApplication.UnicodeUTF8))
        self.abortPB.setText(QtGui.QApplication.translate("ProgressBarDialog", "Abort", None, QtGui.QApplication.UnicodeUTF8))
