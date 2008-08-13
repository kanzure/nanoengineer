# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'COmmentPropDialog.ui'
#
# Created: Thu Aug 07 18:04:11 2008
#      by: PyQt4 UI code generator 4.3.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_CommentPropDialog(object):
    def setupUi(self, CommentPropDialog):
        CommentPropDialog.setObjectName("CommentPropDialog")
        CommentPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,390,275).size()).expandedTo(CommentPropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(CommentPropDialog)

        # note: this change will be lost when this file is remade from the .ui file.
        # it's a short term workaround only. [bruce 080808]
        from utilities.GlobalPreferences import debug_pref_support_Qt_4point2
        if not debug_pref_support_Qt_4point2():
            self.gridlayout.setContentsMargins(0,0,0,2)
        
        self.gridlayout.setSpacing(2)
        self.gridlayout.setObjectName("gridlayout")

        self.comment_textedit = QtGui.QTextEdit(CommentPropDialog)
        self.comment_textedit.setObjectName("comment_textedit")
        self.gridlayout.addWidget(self.comment_textedit,0,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setSpacing(4)
        self.hboxlayout.setObjectName("hboxlayout")

        self.date_time_btn = QtGui.QPushButton(CommentPropDialog)
        self.date_time_btn.setObjectName("date_time_btn")
        self.hboxlayout.addWidget(self.date_time_btn)

        spacerItem = QtGui.QSpacerItem(81,25,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.cancel_btn = QtGui.QPushButton(CommentPropDialog)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)

        self.ok__btn = QtGui.QPushButton(CommentPropDialog)
        self.ok__btn.setObjectName("ok__btn")
        self.hboxlayout.addWidget(self.ok__btn)

        spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)
        self.gridlayout.addLayout(self.hboxlayout,1,0,1,1)

        self.retranslateUi(CommentPropDialog)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),CommentPropDialog.reject)
        QtCore.QObject.connect(self.ok__btn,QtCore.SIGNAL("clicked()"),CommentPropDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(CommentPropDialog)

    def retranslateUi(self, CommentPropDialog):
        CommentPropDialog.setWindowTitle(QtGui.QApplication.translate("CommentPropDialog", "Comment", None, QtGui.QApplication.UnicodeUTF8))
        self.date_time_btn.setText(QtGui.QApplication.translate("CommentPropDialog", "Date/Time Stamp", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("CommentPropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok__btn.setText(QtGui.QApplication.translate("CommentPropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))

