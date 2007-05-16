# -*- coding: utf-8 -*-

# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'ESPWindowPropDialog.ui'
#
# Created: Wed Sep 20 10:42:42 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui

class Ui_ESPWindowPropDialog(object):
    def setupUi(self, ESPWindowPropDialog):
        ESPWindowPropDialog.setObjectName("ESPWindowPropDialog")
        ESPWindowPropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,320,692).size()).expandedTo(ESPWindowPropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(ESPWindowPropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox1 = QtGui.QGroupBox(ESPWindowPropDialog)
        self.groupBox1.setObjectName("groupBox1")

        self.vboxlayout = QtGui.QVBoxLayout(self.groupBox1)
        self.vboxlayout.setMargin(11)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.show_esp_bbox_checkbox = QtGui.QCheckBox(self.groupBox1)
        self.show_esp_bbox_checkbox.setChecked(True)
        self.show_esp_bbox_checkbox.setObjectName("show_esp_bbox_checkbox")
        self.vboxlayout.addWidget(self.show_esp_bbox_checkbox)

        self.highlight_atoms_in_bbox_checkbox = QtGui.QCheckBox(self.groupBox1)
        self.highlight_atoms_in_bbox_checkbox.setChecked(False)
        self.highlight_atoms_in_bbox_checkbox.setObjectName("highlight_atoms_in_bbox_checkbox")
        self.vboxlayout.addWidget(self.highlight_atoms_in_bbox_checkbox)

        self.select_atoms_btn = QtGui.QPushButton(self.groupBox1)
        self.select_atoms_btn.setAutoDefault(False)
        self.select_atoms_btn.setObjectName("select_atoms_btn")
        self.vboxlayout.addWidget(self.select_atoms_btn)
        self.gridlayout.addWidget(self.groupBox1,1,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem = QtGui.QSpacerItem(92,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem)

        self.ok_btn = QtGui.QPushButton(ESPWindowPropDialog)
        self.ok_btn.setMinimumSize(QtCore.QSize(0,30))
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(ESPWindowPropDialog)
        self.cancel_btn.setMinimumSize(QtCore.QSize(0,30))
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)
        self.gridlayout.addLayout(self.hboxlayout,4,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(101,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        self.gridlayout.addItem(spacerItem1,3,0,1,1)

        self.groupBox5 = QtGui.QGroupBox(ESPWindowPropDialog)
        self.groupBox5.setObjectName("groupBox5")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox5)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.choose_file_btn = QtGui.QToolButton(self.groupBox5)
        self.choose_file_btn.setObjectName("choose_file_btn")
        self.gridlayout1.addWidget(self.choose_file_btn,2,6,1,1)

        self.mirror_btn = QtGui.QToolButton(self.groupBox5)
        self.mirror_btn.setObjectName("mirror_btn")
        self.gridlayout1.addWidget(self.mirror_btn,3,4,1,1)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.gridlayout1.addItem(spacerItem2,3,5,1,2)

        self.rotate_ccw_btn = QtGui.QToolButton(self.groupBox5)
        self.rotate_ccw_btn.setObjectName("rotate_ccw_btn")
        self.gridlayout1.addWidget(self.rotate_ccw_btn,3,0,1,1)

        self.png_fname_linedit = QtGui.QLineEdit(self.groupBox5)
        self.png_fname_linedit.setReadOnly(False)
        self.png_fname_linedit.setObjectName("png_fname_linedit")
        self.gridlayout1.addWidget(self.png_fname_linedit,2,0,1,6)

        self.rotate_cw_btn = QtGui.QToolButton(self.groupBox5)
        self.rotate_cw_btn.setObjectName("rotate_cw_btn")
        self.gridlayout1.addWidget(self.rotate_cw_btn,3,1,1,2)

        self.flip_btn = QtGui.QToolButton(self.groupBox5)
        self.flip_btn.setObjectName("flip_btn")
        self.gridlayout1.addWidget(self.flip_btn,3,3,1,1)

        self.calculate_esp_btn = QtGui.QPushButton(self.groupBox5)
        self.calculate_esp_btn.setAutoDefault(False)
        self.calculate_esp_btn.setObjectName("calculate_esp_btn")
        self.gridlayout1.addWidget(self.calculate_esp_btn,0,0,1,4)

        self.clear_btn = QtGui.QToolButton(self.groupBox5)
        self.clear_btn.setObjectName("clear_btn")
        self.gridlayout1.addWidget(self.clear_btn,1,2,1,2)

        self.load_btn = QtGui.QToolButton(self.groupBox5)
        self.load_btn.setObjectName("load_btn")
        self.gridlayout1.addWidget(self.load_btn,1,0,1,2)

        self.textLabel1_6 = QtGui.QLabel(self.groupBox5)
        self.textLabel1_6.setObjectName("textLabel1_6")
        self.gridlayout1.addWidget(self.textLabel1_6,0,4,1,2)

        self.textLabel1_6_2 = QtGui.QLabel(self.groupBox5)
        self.textLabel1_6_2.setObjectName("textLabel1_6_2")
        self.gridlayout1.addWidget(self.textLabel1_6_2,1,4,1,2)

        self.xaxis_spinbox = QtGui.QSpinBox(self.groupBox5)
        self.xaxis_spinbox.setMaximum(1)
        self.xaxis_spinbox.setMinimum(-1)
        self.xaxis_spinbox.setObjectName("xaxis_spinbox")
        self.gridlayout1.addWidget(self.xaxis_spinbox,0,6,1,1)

        self.yaxis_spinbox = QtGui.QSpinBox(self.groupBox5)
        self.yaxis_spinbox.setMaximum(1)
        self.yaxis_spinbox.setMinimum(-1)
        self.yaxis_spinbox.setProperty("value",QtCore.QVariant(0))
        self.yaxis_spinbox.setObjectName("yaxis_spinbox")
        self.gridlayout1.addWidget(self.yaxis_spinbox,1,6,1,1)
        self.gridlayout.addWidget(self.groupBox5,2,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel1_4 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout1.addWidget(self.textLabel1_4)

        self.colorTextLabel_3 = QtGui.QLabel(ESPWindowPropDialog)
        self.colorTextLabel_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_3.setObjectName("colorTextLabel_3")
        self.vboxlayout1.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QtGui.QLabel(ESPWindowPropDialog)
        self.colorTextLabel_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_4.setObjectName("colorTextLabel_4")
        self.vboxlayout1.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout1.addWidget(self.textLabel1)

        self.textLabel1_3 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout1.addWidget(self.textLabel1_3)

        self.textLabel1_5 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.vboxlayout1.addWidget(self.textLabel1_5)

        self.textLabel1_2 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.vboxlayout1.addWidget(self.textLabel1_2)

        self.textLabel1_2_2 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel1_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.vboxlayout1.addWidget(self.textLabel1_2_2)
        self.hboxlayout1.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.name_linedit = QtGui.QLineEdit(ESPWindowPropDialog)
        self.name_linedit.setAlignment(QtCore.Qt.AlignLeading)
        self.name_linedit.setObjectName("name_linedit")
        self.vboxlayout2.addWidget(self.name_linedit)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.fill_color_pixmap = QtGui.QLabel(ESPWindowPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fill_color_pixmap.sizePolicy().hasHeightForWidth())
        self.fill_color_pixmap.setSizePolicy(sizePolicy)
        self.fill_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.fill_color_pixmap.setFrameShape(QtGui.QFrame.Box)
        self.fill_color_pixmap.setFrameShadow(QtGui.QFrame.Plain)
        self.fill_color_pixmap.setScaledContents(True)
        self.fill_color_pixmap.setObjectName("fill_color_pixmap")
        self.hboxlayout3.addWidget(self.fill_color_pixmap)

        self.choose_fill_color_btn = QtGui.QPushButton(ESPWindowPropDialog)
        self.choose_fill_color_btn.setEnabled(True)
        self.choose_fill_color_btn.setAutoDefault(False)
        self.choose_fill_color_btn.setObjectName("choose_fill_color_btn")
        self.hboxlayout3.addWidget(self.choose_fill_color_btn)

        spacerItem3 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem3)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.border_color_pixmap = QtGui.QLabel(ESPWindowPropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.border_color_pixmap.sizePolicy().hasHeightForWidth())
        self.border_color_pixmap.setSizePolicy(sizePolicy)
        self.border_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.border_color_pixmap.setFrameShape(QtGui.QFrame.Box)
        self.border_color_pixmap.setFrameShadow(QtGui.QFrame.Plain)
        self.border_color_pixmap.setScaledContents(True)
        self.border_color_pixmap.setObjectName("border_color_pixmap")
        self.hboxlayout4.addWidget(self.border_color_pixmap)

        self.choose_border_color_btn = QtGui.QPushButton(ESPWindowPropDialog)
        self.choose_border_color_btn.setEnabled(True)
        self.choose_border_color_btn.setAutoDefault(False)
        self.choose_border_color_btn.setObjectName("choose_border_color_btn")
        self.hboxlayout4.addWidget(self.choose_border_color_btn)

        spacerItem4 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem4)
        self.vboxlayout3.addLayout(self.hboxlayout4)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.width_linedit = QtGui.QLineEdit(ESPWindowPropDialog)
        self.width_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.width_linedit.setObjectName("width_linedit")
        self.hboxlayout5.addWidget(self.width_linedit)

        self.textLabel2 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel2.setObjectName("textLabel2")
        self.hboxlayout5.addWidget(self.textLabel2)

        spacerItem5 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem5)
        self.vboxlayout3.addLayout(self.hboxlayout5)

        self.hboxlayout6 = QtGui.QHBoxLayout()
        self.hboxlayout6.setMargin(0)
        self.hboxlayout6.setSpacing(6)
        self.hboxlayout6.setObjectName("hboxlayout6")

        self.window_offset_linedit = QtGui.QLineEdit(ESPWindowPropDialog)
        self.window_offset_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.window_offset_linedit.setObjectName("window_offset_linedit")
        self.hboxlayout6.addWidget(self.window_offset_linedit)

        self.textLabel2_2 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.hboxlayout6.addWidget(self.textLabel2_2)

        spacerItem6 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout6.addItem(spacerItem6)
        self.vboxlayout3.addLayout(self.hboxlayout6)

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setMargin(0)
        self.hboxlayout7.setSpacing(6)
        self.hboxlayout7.setObjectName("hboxlayout7")

        self.edge_offset_linedit = QtGui.QLineEdit(ESPWindowPropDialog)
        self.edge_offset_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.edge_offset_linedit.setObjectName("edge_offset_linedit")
        self.hboxlayout7.addWidget(self.edge_offset_linedit)

        self.textLabel2_3 = QtGui.QLabel(ESPWindowPropDialog)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.hboxlayout7.addWidget(self.textLabel2_3)

        spacerItem7 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout7.addItem(spacerItem7)
        self.vboxlayout3.addLayout(self.hboxlayout7)

        self.hboxlayout8 = QtGui.QHBoxLayout()
        self.hboxlayout8.setMargin(0)
        self.hboxlayout8.setSpacing(6)
        self.hboxlayout8.setObjectName("hboxlayout8")

        self.resolution_spinbox = QtGui.QSpinBox(ESPWindowPropDialog)
        self.resolution_spinbox.setMaximum(512)
        self.resolution_spinbox.setMinimum(1)
        self.resolution_spinbox.setProperty("value",QtCore.QVariant(20))
        self.resolution_spinbox.setObjectName("resolution_spinbox")
        self.hboxlayout8.addWidget(self.resolution_spinbox)

        spacerItem8 = QtGui.QSpacerItem(95,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout8.addItem(spacerItem8)
        self.vboxlayout3.addLayout(self.hboxlayout8)

        self.hboxlayout9 = QtGui.QHBoxLayout()
        self.hboxlayout9.setMargin(0)
        self.hboxlayout9.setSpacing(6)
        self.hboxlayout9.setObjectName("hboxlayout9")

        self.opacity_linedit = QtGui.QLineEdit(ESPWindowPropDialog)
        self.opacity_linedit.setMaximumSize(QtCore.QSize(40,32767))
        self.opacity_linedit.setMaxLength(5)
        self.opacity_linedit.setReadOnly(True)
        self.opacity_linedit.setObjectName("opacity_linedit")
        self.hboxlayout9.addWidget(self.opacity_linedit)

        self.opacity_slider = QtGui.QSlider(ESPWindowPropDialog)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setObjectName("opacity_slider")
        self.hboxlayout9.addWidget(self.opacity_slider)
        self.vboxlayout3.addLayout(self.hboxlayout9)
        self.hboxlayout2.addLayout(self.vboxlayout3)

        spacerItem9 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem9)
        self.vboxlayout2.addLayout(self.hboxlayout2)
        self.hboxlayout1.addLayout(self.vboxlayout2)
        self.gridlayout.addLayout(self.hboxlayout1,0,0,1,1)

        self.retranslateUi(ESPWindowPropDialog)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),ESPWindowPropDialog.accept)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),ESPWindowPropDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ESPWindowPropDialog)
        ESPWindowPropDialog.setTabOrder(self.name_linedit,self.choose_fill_color_btn)
        ESPWindowPropDialog.setTabOrder(self.choose_fill_color_btn,self.choose_border_color_btn)
        ESPWindowPropDialog.setTabOrder(self.choose_border_color_btn,self.resolution_spinbox)
        ESPWindowPropDialog.setTabOrder(self.resolution_spinbox,self.show_esp_bbox_checkbox)
        ESPWindowPropDialog.setTabOrder(self.show_esp_bbox_checkbox,self.highlight_atoms_in_bbox_checkbox)
        ESPWindowPropDialog.setTabOrder(self.highlight_atoms_in_bbox_checkbox,self.select_atoms_btn)
        ESPWindowPropDialog.setTabOrder(self.select_atoms_btn,self.ok_btn)
        ESPWindowPropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, ESPWindowPropDialog):
        ESPWindowPropDialog.setWindowTitle(QtGui.QApplication.translate("ESPWindowPropDialog", "ESP Window Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox1.setTitle(QtGui.QApplication.translate("ESPWindowPropDialog", "ESP Window Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.show_esp_bbox_checkbox.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Show Bounding Box of Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.highlight_atoms_in_bbox_checkbox.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Highlight Atoms Inside Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.select_atoms_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Select Atoms Inside Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("ESPWindowPropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("ESPWindowPropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox5.setTitle(QtGui.QApplication.translate("ESPWindowPropDialog", "ESP Results Image", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_file_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.mirror_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Flip image horizontally (left to right).", None, QtGui.QApplication.UnicodeUTF8))
        self.mirror_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Mirror", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_ccw_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Rotate  90 degrees counter clock-wisely.", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_ccw_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "+90", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_cw_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Rotate  90 degrees clock-wisely.", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_cw_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "-90", None, QtGui.QApplication.UnicodeUTF8))
        self.flip_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Flip the image vertically (top to bottom).", None, QtGui.QApplication.UnicodeUTF8))
        self.flip_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Flip", None, QtGui.QApplication.UnicodeUTF8))
        self.calculate_esp_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Calculate ESP", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.load_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "xaxisOrient :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6_2.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "yaxisOrient :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_3.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Fill Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_4.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Border Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Width :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Window Offset :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Edge Offset :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Resolution :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Opacity:", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_fill_color_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_fill_color_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setToolTip(QtGui.QApplication.translate("ESPWindowPropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("ESPWindowPropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
