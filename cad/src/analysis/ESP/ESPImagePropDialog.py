# -*- coding: utf-8 -*-

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
# Form implementation generated from reading ui file 'ESPImagePropDialog.ui'
#
# Created: Wed Sep 27 14:24:14 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from utilities.icon_utilities import geticon

class Ui_ESPImagePropDialog(object):
    def setupUi(self, ESPImagePropDialog):
        ESPImagePropDialog.setObjectName("ESPImagePropDialog")
        ESPImagePropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,299,700).size()).expandedTo(ESPImagePropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(ESPImagePropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.groupBox1 = QtGui.QGroupBox(ESPImagePropDialog)
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

        self.ok_btn = QtGui.QPushButton(ESPImagePropDialog)
        self.ok_btn.setMinimumSize(QtCore.QSize(0,30))
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(ESPImagePropDialog)
        self.cancel_btn.setMinimumSize(QtCore.QSize(0,30))
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)
        self.gridlayout.addLayout(self.hboxlayout,4,0,1,1)

        spacerItem1 = QtGui.QSpacerItem(101,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        self.gridlayout.addItem(spacerItem1,3,0,1,1)

        self.groupBox5 = QtGui.QGroupBox(ESPImagePropDialog)
        self.groupBox5.setObjectName("groupBox5")

        self.gridlayout1 = QtGui.QGridLayout(self.groupBox5)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.calculate_esp_btn = QtGui.QPushButton(self.groupBox5)
        self.calculate_esp_btn.setAutoDefault(False)
        self.calculate_esp_btn.setObjectName("calculate_esp_btn")
        self.hboxlayout1.addWidget(self.calculate_esp_btn)

        self.textLabel1_6 = QtGui.QLabel(self.groupBox5)
        self.textLabel1_6.setObjectName("textLabel1_6")
        self.hboxlayout1.addWidget(self.textLabel1_6)

        self.xaxis_spinbox = QtGui.QSpinBox(self.groupBox5)
        self.xaxis_spinbox.setMaximum(1)
        self.xaxis_spinbox.setMinimum(-1)
        self.xaxis_spinbox.setObjectName("xaxis_spinbox")
        self.hboxlayout1.addWidget(self.xaxis_spinbox)
        self.gridlayout1.addLayout(self.hboxlayout1,0,0,1,1)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.load_btn = QtGui.QToolButton(self.groupBox5)
        self.load_btn.setObjectName("load_btn")
        self.hboxlayout2.addWidget(self.load_btn)

        self.clear_btn = QtGui.QToolButton(self.groupBox5)
        self.clear_btn.setObjectName("clear_btn")
        self.hboxlayout2.addWidget(self.clear_btn)

        self.textLabel1_6_2 = QtGui.QLabel(self.groupBox5)
        self.textLabel1_6_2.setObjectName("textLabel1_6_2")
        self.hboxlayout2.addWidget(self.textLabel1_6_2)

        self.yaxis_spinbox = QtGui.QSpinBox(self.groupBox5)
        self.yaxis_spinbox.setMaximum(1)
        self.yaxis_spinbox.setMinimum(-1)
        self.yaxis_spinbox.setProperty("value",QtCore.QVariant(0))
        self.yaxis_spinbox.setObjectName("yaxis_spinbox")
        self.hboxlayout2.addWidget(self.yaxis_spinbox)
        self.gridlayout1.addLayout(self.hboxlayout2,1,0,1,1)

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.png_fname_linedit = QtGui.QLineEdit(self.groupBox5)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(7),QtGui.QSizePolicy.Policy(7))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.png_fname_linedit.sizePolicy().hasHeightForWidth())
        self.png_fname_linedit.setSizePolicy(sizePolicy)
        self.png_fname_linedit.setReadOnly(False)
        self.png_fname_linedit.setObjectName("png_fname_linedit")
        self.hboxlayout3.addWidget(self.png_fname_linedit)

        self.choose_file_btn = QtGui.QToolButton(self.groupBox5)
        self.choose_file_btn.setIcon(
            geticon("ui/actions/Properties Manager/Open.png"))
        self.choose_file_btn.setObjectName("choose_file_btn")
        self.hboxlayout3.addWidget(self.choose_file_btn)
        self.gridlayout1.addLayout(self.hboxlayout3,2,0,1,1)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.rotate_ccw_btn = QtGui.QToolButton(self.groupBox5)
        self.rotate_ccw_btn.setObjectName("rotate_ccw_btn")
        self.hboxlayout4.addWidget(self.rotate_ccw_btn)

        self.rotate_cw_btn = QtGui.QToolButton(self.groupBox5)
        self.rotate_cw_btn.setObjectName("rotate_cw_btn")
        self.hboxlayout4.addWidget(self.rotate_cw_btn)

        self.flip_btn = QtGui.QToolButton(self.groupBox5)
        self.flip_btn.setObjectName("flip_btn")
        self.hboxlayout4.addWidget(self.flip_btn)

        self.mirror_btn = QtGui.QToolButton(self.groupBox5)
        self.mirror_btn.setObjectName("mirror_btn")
        self.hboxlayout4.addWidget(self.mirror_btn)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem2)
        self.gridlayout1.addLayout(self.hboxlayout4,3,0,1,1)
        self.gridlayout.addWidget(self.groupBox5,2,0,1,1)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel1_4 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout1.addWidget(self.textLabel1_4)

        self.colorTextLabel_3 = QtGui.QLabel(ESPImagePropDialog)
        self.colorTextLabel_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_3.setObjectName("colorTextLabel_3")
        self.vboxlayout1.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QtGui.QLabel(ESPImagePropDialog)
        self.colorTextLabel_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_4.setObjectName("colorTextLabel_4")
        self.vboxlayout1.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout1.addWidget(self.textLabel1)

        self.textLabel1_3 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout1.addWidget(self.textLabel1_3)

        self.textLabel1_5 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.vboxlayout1.addWidget(self.textLabel1_5)

        self.textLabel1_2 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.vboxlayout1.addWidget(self.textLabel1_2)

        self.textLabel1_2_2 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel1_2_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.vboxlayout1.addWidget(self.textLabel1_2_2)
        self.hboxlayout5.addLayout(self.vboxlayout1)

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.name_linedit = QtGui.QLineEdit(ESPImagePropDialog)
        self.name_linedit.setAlignment(QtCore.Qt.AlignLeading)
        self.name_linedit.setObjectName("name_linedit")
        self.vboxlayout2.addWidget(self.name_linedit)

        self.hboxlayout6 = QtGui.QHBoxLayout()
        self.hboxlayout6.setMargin(0)
        self.hboxlayout6.setSpacing(6)
        self.hboxlayout6.setObjectName("hboxlayout6")

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setMargin(0)
        self.hboxlayout7.setSpacing(6)
        self.hboxlayout7.setObjectName("hboxlayout7")

        self.fill_color_pixmap = QtGui.QLabel(ESPImagePropDialog)

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
        self.hboxlayout7.addWidget(self.fill_color_pixmap)

        self.choose_fill_color_btn = QtGui.QPushButton(ESPImagePropDialog)
        self.choose_fill_color_btn.setEnabled(True)
        self.choose_fill_color_btn.setAutoDefault(False)
        self.choose_fill_color_btn.setObjectName("choose_fill_color_btn")
        self.hboxlayout7.addWidget(self.choose_fill_color_btn)

        spacerItem3 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout7.addItem(spacerItem3)
        self.vboxlayout3.addLayout(self.hboxlayout7)

        self.hboxlayout8 = QtGui.QHBoxLayout()
        self.hboxlayout8.setMargin(0)
        self.hboxlayout8.setSpacing(6)
        self.hboxlayout8.setObjectName("hboxlayout8")

        self.border_color_pixmap = QtGui.QLabel(ESPImagePropDialog)

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
        self.hboxlayout8.addWidget(self.border_color_pixmap)

        self.choose_border_color_btn = QtGui.QPushButton(ESPImagePropDialog)
        self.choose_border_color_btn.setEnabled(True)
        self.choose_border_color_btn.setAutoDefault(False)
        self.choose_border_color_btn.setObjectName("choose_border_color_btn")
        self.hboxlayout8.addWidget(self.choose_border_color_btn)

        spacerItem4 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout8.addItem(spacerItem4)
        self.vboxlayout3.addLayout(self.hboxlayout8)

        self.hboxlayout9 = QtGui.QHBoxLayout()
        self.hboxlayout9.setMargin(0)
        self.hboxlayout9.setSpacing(6)
        self.hboxlayout9.setObjectName("hboxlayout9")

        self.width_linedit = QtGui.QLineEdit(ESPImagePropDialog)
        self.width_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.width_linedit.setObjectName("width_linedit")
        self.hboxlayout9.addWidget(self.width_linedit)

        self.textLabel2 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel2.setObjectName("textLabel2")
        self.hboxlayout9.addWidget(self.textLabel2)

        spacerItem5 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout9.addItem(spacerItem5)
        self.vboxlayout3.addLayout(self.hboxlayout9)

        self.hboxlayout10 = QtGui.QHBoxLayout()
        self.hboxlayout10.setMargin(0)
        self.hboxlayout10.setSpacing(6)
        self.hboxlayout10.setObjectName("hboxlayout10")

        self.image_offset_linedit = QtGui.QLineEdit(ESPImagePropDialog)
        self.image_offset_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.image_offset_linedit.setObjectName("image_offset_linedit")
        self.hboxlayout10.addWidget(self.image_offset_linedit)

        self.textLabel2_2 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.hboxlayout10.addWidget(self.textLabel2_2)

        spacerItem6 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout10.addItem(spacerItem6)
        self.vboxlayout3.addLayout(self.hboxlayout10)

        self.hboxlayout11 = QtGui.QHBoxLayout()
        self.hboxlayout11.setMargin(0)
        self.hboxlayout11.setSpacing(6)
        self.hboxlayout11.setObjectName("hboxlayout11")

        self.edge_offset_linedit = QtGui.QLineEdit(ESPImagePropDialog)
        self.edge_offset_linedit.setMaximumSize(QtCore.QSize(80,32767))
        self.edge_offset_linedit.setObjectName("edge_offset_linedit")
        self.hboxlayout11.addWidget(self.edge_offset_linedit)

        self.textLabel2_3 = QtGui.QLabel(ESPImagePropDialog)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.hboxlayout11.addWidget(self.textLabel2_3)

        spacerItem7 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout11.addItem(spacerItem7)
        self.vboxlayout3.addLayout(self.hboxlayout11)

        self.hboxlayout12 = QtGui.QHBoxLayout()
        self.hboxlayout12.setMargin(0)
        self.hboxlayout12.setSpacing(6)
        self.hboxlayout12.setObjectName("hboxlayout12")

        self.resolution_spinbox = QtGui.QSpinBox(ESPImagePropDialog)
        self.resolution_spinbox.setMaximum(512)
        self.resolution_spinbox.setMinimum(1)
        self.resolution_spinbox.setProperty("value",QtCore.QVariant(20))
        self.resolution_spinbox.setObjectName("resolution_spinbox")
        self.hboxlayout12.addWidget(self.resolution_spinbox)

        spacerItem8 = QtGui.QSpacerItem(95,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout12.addItem(spacerItem8)
        self.vboxlayout3.addLayout(self.hboxlayout12)

        self.hboxlayout13 = QtGui.QHBoxLayout()
        self.hboxlayout13.setMargin(0)
        self.hboxlayout13.setSpacing(6)
        self.hboxlayout13.setObjectName("hboxlayout13")

        self.opacity_linedit = QtGui.QLineEdit(ESPImagePropDialog)
        self.opacity_linedit.setMaximumSize(QtCore.QSize(40,32767))
        self.opacity_linedit.setMaxLength(5)
        self.opacity_linedit.setReadOnly(True)
        self.opacity_linedit.setObjectName("opacity_linedit")
        self.hboxlayout13.addWidget(self.opacity_linedit)

        self.opacity_slider = QtGui.QSlider(ESPImagePropDialog)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setObjectName("opacity_slider")
        self.hboxlayout13.addWidget(self.opacity_slider)
        self.vboxlayout3.addLayout(self.hboxlayout13)
        self.hboxlayout6.addLayout(self.vboxlayout3)

        spacerItem9 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout6.addItem(spacerItem9)
        self.vboxlayout2.addLayout(self.hboxlayout6)
        self.hboxlayout5.addLayout(self.vboxlayout2)
        self.gridlayout.addLayout(self.hboxlayout5,0,0,1,1)

        self.retranslateUi(ESPImagePropDialog)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),ESPImagePropDialog.accept)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),ESPImagePropDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ESPImagePropDialog)
        ESPImagePropDialog.setTabOrder(self.name_linedit,self.choose_fill_color_btn)
        ESPImagePropDialog.setTabOrder(self.choose_fill_color_btn,self.choose_border_color_btn)
        ESPImagePropDialog.setTabOrder(self.choose_border_color_btn,self.resolution_spinbox)
        ESPImagePropDialog.setTabOrder(self.resolution_spinbox,self.show_esp_bbox_checkbox)
        ESPImagePropDialog.setTabOrder(self.show_esp_bbox_checkbox,self.highlight_atoms_in_bbox_checkbox)
        ESPImagePropDialog.setTabOrder(self.highlight_atoms_in_bbox_checkbox,self.select_atoms_btn)
        ESPImagePropDialog.setTabOrder(self.select_atoms_btn,self.ok_btn)
        ESPImagePropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, ESPImagePropDialog):
        ESPImagePropDialog.setWindowTitle(QtGui.QApplication.translate("ESPImagePropDialog", "ESP Image Properties", None, QtGui.QApplication.UnicodeUTF8))
        ESPImagePropDialog.setWindowIcon(QtGui.QIcon("ui/border/EspImage"))
        self.groupBox1.setTitle(QtGui.QApplication.translate("ESPImagePropDialog", "ESP Image Bounding Box", None, QtGui.QApplication.UnicodeUTF8))
        self.show_esp_bbox_checkbox.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Show Bounding Box", None, QtGui.QApplication.UnicodeUTF8))
        self.highlight_atoms_in_bbox_checkbox.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Highlight Atoms Inside Bounding Box", None, QtGui.QApplication.UnicodeUTF8))
        self.select_atoms_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Select Atoms Inside Volume", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("ESPImagePropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("ESPImagePropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox5.setTitle(QtGui.QApplication.translate("ESPImagePropDialog", "ESP Results Image", None, QtGui.QApplication.UnicodeUTF8))
        self.calculate_esp_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Calculate ESP", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6.setText(QtGui.QApplication.translate("ESPImagePropDialog", "xaxisOrient :", None, QtGui.QApplication.UnicodeUTF8))
        self.load_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Load", None, QtGui.QApplication.UnicodeUTF8))
        self.clear_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_6_2.setText(QtGui.QApplication.translate("ESPImagePropDialog", "yaxisOrient :", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_ccw_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Rotate  90 degrees counter clock-wisely.", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_ccw_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "+90", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_cw_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Rotate  90 degrees clock-wisely.", None, QtGui.QApplication.UnicodeUTF8))
        self.rotate_cw_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "-90", None, QtGui.QApplication.UnicodeUTF8))
        self.flip_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Flip the image vertically (top to bottom).", None, QtGui.QApplication.UnicodeUTF8))
        self.flip_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Flip", None, QtGui.QApplication.UnicodeUTF8))
        self.mirror_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Flip image horizontally (left to right).", None, QtGui.QApplication.UnicodeUTF8))
        self.mirror_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Mirror", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_3.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Fill Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_4.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Border Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Width :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Height Offset :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Edge Offset :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Resolution :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Opacity:", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_fill_color_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_fill_color_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setToolTip(QtGui.QApplication.translate("ESPImagePropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("ESPImagePropDialog", "Angstroms", None, QtGui.QApplication.UnicodeUTF8))
