# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'PartPropDialog.ui'
#
# Created: Wed Sep 20 08:20:23 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PartPropDialog(object):
    def setupUi(self, PartPropDialog):
        PartPropDialog.setObjectName("PartPropDialog")
        PartPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,396,402).size()).expandedTo(PartPropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(PartPropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(4)
        self.hboxlayout.setSpacing(72)
        self.hboxlayout.setObjectName("hboxlayout")

        self.okPushButton = QtGui.QPushButton(PartPropDialog)
        self.okPushButton.setMinimumSize(QtCore.QSize(0,0))
        self.okPushButton.setAutoDefault(True)
        self.okPushButton.setDefault(True)
        self.okPushButton.setObjectName("okPushButton")
        self.hboxlayout.addWidget(self.okPushButton)

        self.cancelPushButton = QtGui.QPushButton(PartPropDialog)
        self.cancelPushButton.setMinimumSize(QtCore.QSize(0,0))
        self.cancelPushButton.setAutoDefault(True)
        self.cancelPushButton.setDefault(False)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.hboxlayout.addWidget(self.cancelPushButton)
        self.gridlayout.addLayout(self.hboxlayout,1,0,1,1)

        self.tabWidget3 = QtGui.QTabWidget(PartPropDialog)
        self.tabWidget3.setObjectName("tabWidget3")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout1 = QtGui.QGridLayout(self.tab)
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.nameLabel = QtGui.QLabel(self.tab)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.nameLabel.setObjectName("nameLabel")
        self.hboxlayout1.addWidget(self.nameLabel)

        self.nameLineEdit = QtGui.QLineEdit(self.tab)
        self.nameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.nameLineEdit.setReadOnly(True)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.hboxlayout1.addWidget(self.nameLineEdit)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.mmpformatLabel = QtGui.QLabel(self.tab)
        self.mmpformatLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.mmpformatLabel.setObjectName("mmpformatLabel")
        self.vboxlayout.addWidget(self.mmpformatLabel)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.statsLabel = QtGui.QLabel(self.tab)
        self.statsLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.statsLabel.setObjectName("statsLabel")
        self.vboxlayout1.addWidget(self.statsLabel)

        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout1.addItem(spacerItem)
        self.hboxlayout2.addLayout(self.vboxlayout1)

        self.statsView = QtGui.QListWidget(self.tab)
        self.statsView.setObjectName("statsView")
        self.hboxlayout2.addWidget(self.statsView)
        self.vboxlayout.addLayout(self.hboxlayout2)
        self.gridlayout1.addLayout(self.vboxlayout,0,0,1,1)
        self.tabWidget3.addTab(self.tab, "")
        self.gridlayout.addWidget(self.tabWidget3,0,0,1,1)

        self.retranslateUi(PartPropDialog)
        QtCore.QObject.connect(self.okPushButton,QtCore.SIGNAL("clicked()"),PartPropDialog.accept)
        QtCore.QObject.connect(self.cancelPushButton,QtCore.SIGNAL("clicked()"),PartPropDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PartPropDialog)
        PartPropDialog.setTabOrder(self.nameLineEdit,self.statsView)
        PartPropDialog.setTabOrder(self.statsView,self.okPushButton)
        PartPropDialog.setTabOrder(self.okPushButton,self.cancelPushButton)
        PartPropDialog.setTabOrder(self.cancelPushButton,self.tabWidget3)

    def retranslateUi(self, PartPropDialog):
        PartPropDialog.setWindowTitle(QtGui.QApplication.translate("PartPropDialog", "Part Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setText(QtGui.QApplication.translate("PartPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setShortcut(QtGui.QApplication.translate("PartPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("PartPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setShortcut(QtGui.QApplication.translate("PartPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.nameLabel.setText(QtGui.QApplication.translate("PartPropDialog", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.mmpformatLabel.setText(QtGui.QApplication.translate("PartPropDialog", "MMP File Format:", None, QtGui.QApplication.UnicodeUTF8))
        self.statsLabel.setText(QtGui.QApplication.translate("PartPropDialog", "Statistics:", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget3.setTabText(self.tabWidget3.indexOf(self.tab), QtGui.QApplication.translate("PartPropDialog", "General", None, QtGui.QApplication.UnicodeUTF8))
