# -*- coding: utf-8 -*-

# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'JobManagerDialog.ui'
#
# Created: Wed Sep 20 08:10:41 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_JobManagerDialog(object):
    def setupUi(self, JobManagerDialog):
        JobManagerDialog.setObjectName("JobManagerDialog")
        JobManagerDialog.resize(QtCore.QSize(QtCore.QRect(0,0,1009,258).size()).expandedTo(JobManagerDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(JobManagerDialog)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.groupBox1 = QtGui.QGroupBox(JobManagerDialog)
        self.groupBox1.setObjectName("groupBox1")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.groupBox1)
        self.vboxlayout1.setMargin(11)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.job_table = QtGui.QTableWidget(self.groupBox1)
        self.job_table.setNumRows(1)
        self.job_table.setNumCols(8)
        self.job_table.setSorting(False)
        self.job_table.setSelectionMode(QtGui.QTable.SingleRow)
        self.job_table.setObjectName("job_table")
        self.vboxlayout1.addWidget(self.job_table)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.start_btn = QtGui.QPushButton(self.groupBox1)
        self.start_btn.setEnabled(False)
        self.start_btn.setObjectName("start_btn")
        self.hboxlayout.addWidget(self.start_btn)

        self.stop_btn = QtGui.QPushButton(self.groupBox1)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setObjectName("stop_btn")
        self.hboxlayout.addWidget(self.stop_btn)

        self.edit_btn = QtGui.QPushButton(self.groupBox1)
        self.edit_btn.setEnabled(False)
        self.edit_btn.setObjectName("edit_btn")
        self.hboxlayout.addWidget(self.edit_btn)

        self.view_btn = QtGui.QPushButton(self.groupBox1)
        self.view_btn.setEnabled(False)
        self.view_btn.setObjectName("view_btn")
        self.hboxlayout.addWidget(self.view_btn)

        self.delete_btn = QtGui.QPushButton(self.groupBox1)
        self.delete_btn.setEnabled(False)
        self.delete_btn.setObjectName("delete_btn")
        self.hboxlayout.addWidget(self.delete_btn)

        self.move_btn = QtGui.QPushButton(self.groupBox1)
        self.move_btn.setEnabled(False)
        self.move_btn.setObjectName("move_btn")
        self.hboxlayout.addWidget(self.move_btn)

        spacerItem = QtGui.QSpacerItem(280,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)
        self.vboxlayout1.addLayout(self.hboxlayout)
        self.vboxlayout.addWidget(self.groupBox1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.refresh_btn = QtGui.QPushButton(JobManagerDialog)
        self.refresh_btn.setObjectName("refresh_btn")
        self.hboxlayout1.addWidget(self.refresh_btn)

        self.filter_btn = QtGui.QPushButton(JobManagerDialog)
        self.filter_btn.setObjectName("filter_btn")
        self.hboxlayout1.addWidget(self.filter_btn)

        spacerItem1 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)

        self.close_btn = QtGui.QPushButton(JobManagerDialog)
        self.close_btn.setObjectName("close_btn")
        self.hboxlayout1.addWidget(self.close_btn)
        self.vboxlayout.addLayout(self.hboxlayout1)

        self.retranslateUi(JobManagerDialog)
        QtCore.QObject.connect(self.close_btn,QtCore.SIGNAL("clicked()"),JobManagerDialog.close)
        QtCore.QMetaObject.connectSlotsByName(JobManagerDialog)

    def retranslateUi(self, JobManagerDialog):
        JobManagerDialog.setWindowTitle(QtGui.QApplication.translate("JobManagerDialog", "NanoEngineer-1 Job Manager", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox1.setTitle(QtGui.QApplication.translate("JobManagerDialog", "Jobs", None, QtGui.QApplication.UnicodeUTF8))
        self.job_table.clear()
        self.job_table.setColumnCount(0)
        self.job_table.setRowCount(0)
        self.start_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Start", None, QtGui.QApplication.UnicodeUTF8))
        self.stop_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.edit_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.view_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "View", None, QtGui.QApplication.UnicodeUTF8))
        self.delete_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.move_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Move", None, QtGui.QApplication.UnicodeUTF8))
        self.refresh_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Refresh", None, QtGui.QApplication.UnicodeUTF8))
        self.filter_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Filter...", None, QtGui.QApplication.UnicodeUTF8))
        self.close_btn.setText(QtGui.QApplication.translate("JobManagerDialog", "Close", None, QtGui.QApplication.UnicodeUTF8))
