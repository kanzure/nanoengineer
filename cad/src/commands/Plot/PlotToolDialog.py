# -*- coding: utf-8 -*-

# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'PlotToolDialog.ui'
#
# Created: Wed Sep 20 07:07:09 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_PlotToolDialog(object):
    def setupUi(self, PlotToolDialog):
        PlotToolDialog.setObjectName("PlotToolDialog")
        PlotToolDialog.resize(QtCore.QSize(QtCore.QRect(0,0,264,150).size()).expandedTo(PlotToolDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(PlotToolDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.plot_btn = QtGui.QPushButton(PlotToolDialog)
        self.plot_btn.setObjectName("plot_btn")
        self.hboxlayout.addWidget(self.plot_btn)

        self.done_btn = QtGui.QPushButton(PlotToolDialog)
        self.done_btn.setObjectName("done_btn")
        self.hboxlayout.addWidget(self.done_btn)
        self.gridlayout1.addLayout(self.hboxlayout,2,0,1,1)

        self.plot_combox = QtGui.QComboBox(PlotToolDialog)
        self.plot_combox.setObjectName("plot_combox")
        self.gridlayout1.addWidget(self.plot_combox,1,0,1,1)

        self.textLabel1 = QtGui.QLabel(PlotToolDialog)
        self.textLabel1.setObjectName("textLabel1")
        self.gridlayout1.addWidget(self.textLabel1,0,0,1,1)
        self.vboxlayout.addLayout(self.gridlayout1)

        spacerItem = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.open_trace_file_btn = QtGui.QPushButton(PlotToolDialog)
        self.open_trace_file_btn.setObjectName("open_trace_file_btn")
        self.hboxlayout1.addWidget(self.open_trace_file_btn)

        self.open_gnuplot_btn = QtGui.QPushButton(PlotToolDialog)
        self.open_gnuplot_btn.setObjectName("open_gnuplot_btn")
        self.hboxlayout1.addWidget(self.open_gnuplot_btn)
        self.vboxlayout.addLayout(self.hboxlayout1)
        self.gridlayout.addLayout(self.vboxlayout,0,0,1,1)

        self.retranslateUi(PlotToolDialog)
        QtCore.QObject.connect(self.done_btn,QtCore.SIGNAL("clicked()"),PlotToolDialog.close)
        QtCore.QMetaObject.connectSlotsByName(PlotToolDialog)
        PlotToolDialog.setTabOrder(self.plot_combox,self.plot_btn)
        PlotToolDialog.setTabOrder(self.plot_btn,self.done_btn)
        PlotToolDialog.setTabOrder(self.done_btn,self.open_trace_file_btn)
        PlotToolDialog.setTabOrder(self.open_trace_file_btn,self.open_gnuplot_btn)

    def retranslateUi(self, PlotToolDialog):
        PlotToolDialog.setWindowTitle(QtGui.QApplication.translate("PlotToolDialog", "Make Graphs", None, QtGui.QApplication.UnicodeUTF8))
        self.plot_btn.setText(QtGui.QApplication.translate("PlotToolDialog", "Make Graph", None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setText(QtGui.QApplication.translate("PlotToolDialog", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("PlotToolDialog", "Select jig to graph:", None, QtGui.QApplication.UnicodeUTF8))
        self.open_trace_file_btn.setText(QtGui.QApplication.translate("PlotToolDialog", "Open Trace File", None, QtGui.QApplication.UnicodeUTF8))
        self.open_gnuplot_btn.setText(QtGui.QApplication.translate("PlotToolDialog", "Open GNUplot File", None, QtGui.QApplication.UnicodeUTF8))
