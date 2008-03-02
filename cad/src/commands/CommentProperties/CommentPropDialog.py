# -*- coding: utf-8 -*-

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'CommentPropDialog.ui'
#
# Created: Wed Sep 20 06:42:18 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CommentPropDialog(object):
    def setupUi(self, CommentPropDialog):
        CommentPropDialog.setObjectName("CommentPropDialog")
        CommentPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,390,275).size()).expandedTo(CommentPropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(CommentPropDialog)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")

        self.comment_textedit = QtGui.QTextEdit(CommentPropDialog)
        self.comment_textedit.setObjectName("comment_textedit")
        self.gridlayout.addWidget(self.comment_textedit,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(3)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.date_time_btn = QtGui.QPushButton(CommentPropDialog)
        self.date_time_btn.setObjectName("date_time_btn")
        self.hboxlayout.addWidget(self.date_time_btn)

        spacerItem = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.cancel_btn = QtGui.QPushButton(CommentPropDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)

        self.ok__btn = QtGui.QPushButton(CommentPropDialog)
        self.ok__btn.setObjectName("ok__btn")
        self.hboxlayout.addWidget(self.ok__btn)
        self.gridlayout.addLayout(self.hboxlayout,1,0,1,1)

        self.retranslateUi(CommentPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),CommentPropDialog.reject)
        QtCore.QObject.connect(self.ok__btn,QtCore.SIGNAL("clicked()"),CommentPropDialog.accept)
        QtCore.QObject.connect(self.date_time_btn,QtCore.SIGNAL("clicked()"),CommentPropDialog.insert_date_time_stamp)
        QtCore.QMetaObject.connectSlotsByName(CommentPropDialog)

    def retranslateUi(self, CommentPropDialog):
        CommentPropDialog.setWindowTitle(QtGui.QApplication.translate("CommentPropDialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        CommentPropDialog.setWindowIcon(QtGui.QIcon("ui/border/Comment"))
        self.date_time_btn.setText(QtGui.QApplication.translate("CommentPropDialog", "Date/Time Stamp", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("CommentPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok__btn.setText(QtGui.QApplication.translate("CommentPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
