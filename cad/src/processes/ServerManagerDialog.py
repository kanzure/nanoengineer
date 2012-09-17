# -*- coding: utf-8 -*-

# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'ServerManagerDialog.ui'
#
# Created: Wed Sep 20 09:07:05 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ServerManagerDialog(object):
    def setupUi(self, ServerManagerDialog):
        ServerManagerDialog.setObjectName("ServerManagerDialog")
        ServerManagerDialog.resize(QtCore.QSize(QtCore.QRect(0,0,673,677).size()).expandedTo(ServerManagerDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(ServerManagerDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.server_listview = QtGui.QListWidget(ServerManagerDialog)
        self.server_listview.setObjectName("server_listview")
        self.hboxlayout.addWidget(self.server_listview)

        self.frame4 = QtGui.QFrame(ServerManagerDialog)
        self.frame4.setFrameShape(QtGui.QFrame.Box)
        self.frame4.setFrameShadow(QtGui.QFrame.Raised)
        self.frame4.setObjectName("frame4")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.frame4)
        self.vboxlayout1.setMargin(11)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel1 = QtGui.QLabel(self.frame4)
        self.textLabel1.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout1.addWidget(self.textLabel1)

        self.name_linedit = QtGui.QLineEdit(self.frame4)
        self.name_linedit.setObjectName("name_linedit")
        self.vboxlayout1.addWidget(self.name_linedit)

        self.textLabel1_3 = QtGui.QLabel(self.frame4)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout1.addWidget(self.textLabel1_3)

        self.ipaddress_linedit = QtGui.QLineEdit(self.frame4)
        self.ipaddress_linedit.setObjectName("ipaddress_linedit")
        self.vboxlayout1.addWidget(self.ipaddress_linedit)

        self.gridlayout = QtGui.QGridLayout()
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.textLabel1_2 = QtGui.QLabel(self.frame4)
        self.textLabel1_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.gridlayout.addWidget(self.textLabel1_2,0,0,1,1)

        self.method_combox = QtGui.QComboBox(self.frame4)
        self.method_combox.setObjectName("method_combox")
        self.gridlayout.addWidget(self.method_combox,1,1,1,1)

        self.textLabel1_6 = QtGui.QLabel(self.frame4)
        self.textLabel1_6.setObjectName("textLabel1_6")
        self.gridlayout.addWidget(self.textLabel1_6,0,1,1,1)

        self.platform_combox = QtGui.QComboBox(self.frame4)
        self.platform_combox.setObjectName("platform_combox")
        self.gridlayout.addWidget(self.platform_combox,1,0,1,1)
        self.vboxlayout1.addLayout(self.gridlayout)

        self.textLabel1_4 = QtGui.QLabel(self.frame4)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout1.addWidget(self.textLabel1_4)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.engine_combox = QtGui.QComboBox(self.frame4)
        self.engine_combox.setObjectName("engine_combox")
        self.hboxlayout1.addWidget(self.engine_combox)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.textLabel1_5 = QtGui.QLabel(self.frame4)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.vboxlayout1.addWidget(self.textLabel1_5)

        self.program_linedit = QtGui.QLineEdit(self.frame4)
        self.program_linedit.setObjectName("program_linedit")
        self.vboxlayout1.addWidget(self.program_linedit)

        self.textLabel1_2_2 = QtGui.QLabel(self.frame4)
        self.textLabel1_2_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.vboxlayout1.addWidget(self.textLabel1_2_2)

        self.username_linedit = QtGui.QLineEdit(self.frame4)
        self.username_linedit.setObjectName("username_linedit")
        self.vboxlayout1.addWidget(self.username_linedit)

        self.textLabel1_2_2_2 = QtGui.QLabel(self.frame4)
        self.textLabel1_2_2_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2_2.setObjectName("textLabel1_2_2_2")
        self.vboxlayout1.addWidget(self.textLabel1_2_2_2)

        self.password_linedit = QtGui.QLineEdit(self.frame4)
        self.password_linedit.setEchoMode(QtGui.QLineEdit.Password)
        self.password_linedit.setObjectName("password_linedit")
        self.vboxlayout1.addWidget(self.password_linedit)
        self.hboxlayout.addWidget(self.frame4)
        self.vboxlayout.addLayout(self.hboxlayout)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.new_btn = QtGui.QPushButton(ServerManagerDialog)
        self.new_btn.setEnabled(True)
        self.new_btn.setObjectName("new_btn")
        self.hboxlayout2.addWidget(self.new_btn)

        self.del_btn = QtGui.QPushButton(ServerManagerDialog)
        self.del_btn.setObjectName("del_btn")
        self.hboxlayout2.addWidget(self.del_btn)

        self.test_btn = QtGui.QPushButton(ServerManagerDialog)
        self.test_btn.setObjectName("test_btn")
        self.hboxlayout2.addWidget(self.test_btn)

        self.exit_btn = QtGui.QPushButton(ServerManagerDialog)
        self.exit_btn.setObjectName("exit_btn")
        self.hboxlayout2.addWidget(self.exit_btn)
        self.vboxlayout.addLayout(self.hboxlayout2)

        self.retranslateUi(ServerManagerDialog)
        QtCore.QObject.connect(self.exit_btn,QtCore.SIGNAL("clicked()"),ServerManagerDialog.close)
        QtCore.QMetaObject.connectSlotsByName(ServerManagerDialog)

    def retranslateUi(self, ServerManagerDialog):
        ServerManagerDialog.setWindowTitle(QtGui.QApplication.translate("ServerManagerDialog", "Server Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("ServerManagerDialog", "Server Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.name_linedit.setText(QtGui.QApplication.translate("ServerManagerDialog", "localhost", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("ServerManagerDialog", "IP Address :", None, QtGui.QApplication.UnicodeUTF8))
        self.ipaddress_linedit.setText(QtGui.QApplication.translate("ServerManagerDialog", "127.0.0.1", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("ServerManagerDialog", "Platform :", None, QtGui.QApplication.UnicodeUTF8))
        self.method_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Local access", None, QtGui.QApplication.UnicodeUTF8))
        self.method_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Ssh/scp", None, QtGui.QApplication.UnicodeUTF8))
        self.method_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Rsh/rcp", None, QtGui.QApplication.UnicodeUTF8))
        self.method_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Telnet/ftp", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6.setText(QtGui.QApplication.translate("ServerManagerDialog", "Method:", None, QtGui.QApplication.UnicodeUTF8))
        self.platform_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Linux", None, QtGui.QApplication.UnicodeUTF8))
        self.platform_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Mac OS", None, QtGui.QApplication.UnicodeUTF8))
        self.platform_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "Windows", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("ServerManagerDialog", "Engine :", None, QtGui.QApplication.UnicodeUTF8))
        self.engine_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "PC GAMESS", None, QtGui.QApplication.UnicodeUTF8))
        self.engine_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "nanoSIM-1", None, QtGui.QApplication.UnicodeUTF8))
        self.engine_combox.addItem(QtGui.QApplication.translate("ServerManagerDialog", "GAMESS", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("ServerManagerDialog", "Executing Program :", None, QtGui.QApplication.UnicodeUTF8))
        self.program_linedit.setText(QtGui.QApplication.translate("ServerManagerDialog", "C:\\PCGAMESS", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("ServerManagerDialog", "Username :", None, QtGui.QApplication.UnicodeUTF8))
        self.username_linedit.setText(QtGui.QApplication.translate("ServerManagerDialog", "nanorex", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2_2.setText(QtGui.QApplication.translate("ServerManagerDialog", "Password :", None, QtGui.QApplication.UnicodeUTF8))
        self.password_linedit.setText(QtGui.QApplication.translate("ServerManagerDialog", "nanorex", None, QtGui.QApplication.UnicodeUTF8))
        self.new_btn.setText(QtGui.QApplication.translate("ServerManagerDialog", "New", None, QtGui.QApplication.UnicodeUTF8))
        self.del_btn.setText(QtGui.QApplication.translate("ServerManagerDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.test_btn.setText(QtGui.QApplication.translate("ServerManagerDialog", "Test", None, QtGui.QApplication.UnicodeUTF8))
        self.exit_btn.setText(QtGui.QApplication.translate("ServerManagerDialog", "Exit", None, QtGui.QApplication.UnicodeUTF8))
