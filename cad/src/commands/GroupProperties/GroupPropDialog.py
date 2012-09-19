# -*- coding: utf-8 -*-

# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'GroupPropDialog.ui'
#
# Created: Wed Sep 20 07:22:13 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_GroupPropDialog(object):
    def setupUi(self, GroupPropDialog):
        GroupPropDialog.setObjectName("GroupPropDialog")
        GroupPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,258,357).size()).expandedTo(GroupPropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(GroupPropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.nameLabel = QtGui.QLabel(GroupPropDialog)
        self.nameLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.nameLabel.setObjectName("nameLabel")
        self.hboxlayout.addWidget(self.nameLabel)

        self.nameLineEdit = QtGui.QLineEdit(GroupPropDialog)
        self.nameLineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.nameLineEdit.setAlignment(QtCore.Qt.AlignLeading)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.hboxlayout.addWidget(self.nameLineEdit)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.mmpformatLabel = QtGui.QLabel(GroupPropDialog)
        self.mmpformatLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.mmpformatLabel.setObjectName("mmpformatLabel")
        self.vboxlayout.addWidget(self.mmpformatLabel)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.statsView = QtGui.QListWidget(GroupPropDialog)
        self.statsView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.statsView.setObjectName("statsView")
        self.hboxlayout1.addWidget(self.statsView)
        self.vboxlayout.addLayout(self.hboxlayout1)
        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)

        spacerItem = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.gridlayout.addItem(spacerItem,1,0,1,1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.okPushButton = QtGui.QPushButton(GroupPropDialog)
        self.okPushButton.setAutoDefault(True)
        self.okPushButton.setDefault(True)
        self.okPushButton.setObjectName("okPushButton")
        self.hboxlayout2.addWidget(self.okPushButton)

        self.cancelPushButton = QtGui.QPushButton(GroupPropDialog)
        self.cancelPushButton.setAutoDefault(True)
        self.cancelPushButton.setDefault(False)
        self.cancelPushButton.setObjectName("cancelPushButton")
        self.hboxlayout2.addWidget(self.cancelPushButton)
        self.gridlayout.addLayout(self.hboxlayout2,2,0,1,1)

        self.retranslateUi(GroupPropDialog)
        QtCore.QObject.connect(self.okPushButton,QtCore.SIGNAL("clicked()"),GroupPropDialog.accept)
        QtCore.QObject.connect(self.cancelPushButton,QtCore.SIGNAL("clicked()"),GroupPropDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GroupPropDialog)
        GroupPropDialog.setTabOrder(self.nameLineEdit,self.okPushButton)
        GroupPropDialog.setTabOrder(self.okPushButton,self.cancelPushButton)
        GroupPropDialog.setTabOrder(self.cancelPushButton,self.statsView)

    def retranslateUi(self, GroupPropDialog):
        GroupPropDialog.setWindowTitle(QtGui.QApplication.translate("GroupPropDialog", "Group Properties", None, QtGui.QApplication.UnicodeUTF8))
        GroupPropDialog.setWindowIcon(QtGui.QIcon("ui/border/GroupProp"))
        self.nameLabel.setText(QtGui.QApplication.translate("GroupPropDialog", "Name:", None, QtGui.QApplication.UnicodeUTF8))
        self.mmpformatLabel.setText(QtGui.QApplication.translate("GroupPropDialog", "Group Statistics:", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setText(QtGui.QApplication.translate("GroupPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.okPushButton.setShortcut(QtGui.QApplication.translate("GroupPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setText(QtGui.QApplication.translate("GroupPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPushButton.setShortcut(QtGui.QApplication.translate("GroupPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
