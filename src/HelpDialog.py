# -*- coding: utf-8 -*-

# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'HelpDialog.ui'
#
# Created: Tue Sep 19 21:01:19 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_HelpDialog(object):
    def setupUi(self, HelpDialog):
        HelpDialog.setObjectName("HelpDialog")
        HelpDialog.resize(QtCore.QSize(QtCore.QRect(0,0,600,480).size()).expandedTo(HelpDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(HelpDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.help_tab = QtGui.QTabWidget(HelpDialog)
        self.help_tab.setObjectName("help_tab")

        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")

        self.gridlayout = QtGui.QGridLayout(self.tab)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.mouse_controls_textbrowser = QtGui.QTextBrowser(self.tab)
        self.mouse_controls_textbrowser.setObjectName("mouse_controls_textbrowser")
        self.gridlayout.addWidget(self.mouse_controls_textbrowser,0,0,1,1)
        self.help_tab.addTab(self.tab, "")

        self.tab1 = QtGui.QWidget()
        self.tab1.setObjectName("tab1")

        self.gridlayout1 = QtGui.QGridLayout(self.tab1)
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.keyboard_shortcuts_textbrowser = QtGui.QTextBrowser(self.tab1)
        self.keyboard_shortcuts_textbrowser.setObjectName("keyboard_shortcuts_textbrowser")
        self.gridlayout1.addWidget(self.keyboard_shortcuts_textbrowser,0,0,1,1)
        self.help_tab.addTab(self.tab1, "")
        self.vboxlayout.addWidget(self.help_tab)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.close_btn = QtGui.QPushButton(HelpDialog)
        self.close_btn.setObjectName("close_btn")
        self.hboxlayout.addWidget(self.close_btn)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.retranslateUi(HelpDialog)
        QtCore.QObject.connect(self.close_btn,QtCore.SIGNAL("clicked()"),HelpDialog.close)
        QtCore.QMetaObject.connectSlotsByName(HelpDialog)

    def retranslateUi(self, HelpDialog):
        HelpDialog.setWindowTitle(QtGui.QApplication.translate("HelpDialog", "NanoEngineer-1 Help", None, QtGui.QApplication.UnicodeUTF8))
        self.help_tab.setTabText(self.help_tab.indexOf(self.tab), QtGui.QApplication.translate("HelpDialog", "Mouse Controls", None, QtGui.QApplication.UnicodeUTF8))
        self.help_tab.setTabText(self.help_tab.indexOf(self.tab1), QtGui.QApplication.translate("HelpDialog", "Keyboard Shortcuts", None, QtGui.QApplication.UnicodeUTF8))
        self.close_btn.setText(QtGui.QApplication.translate("HelpDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
