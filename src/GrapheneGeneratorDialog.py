# -*- coding: utf-8 -*-

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'GrapheneGeneratorDialog.ui'
#
# Created: Wed Sep 27 14:00:19 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui
from Utility import geticon, getpixmap

class Ui_graphene_sheet_dialog(object):
    def setupUi(self, graphene_sheet_dialog):
        graphene_sheet_dialog.setObjectName("graphene_sheet_dialog")
        graphene_sheet_dialog.resize(QtCore.QSize(QtCore.QRect(0,0,200,294).size()).expandedTo(graphene_sheet_dialog.minimumSizeHint()))
        
        palette = graphene_sheet_dialog.getPropertyManagerPalette()
        graphene_sheet_dialog.setPalette(palette)
        
        self.vboxlayout = QtGui.QVBoxLayout(graphene_sheet_dialog)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.heading_frame = QtGui.QFrame(graphene_sheet_dialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        palette2 = QtGui.QPalette()
        palette2.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),QtGui.QColor(150,150,140)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),QtGui.QColor(150, 150,140)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),QtGui.QColor(150,150,140)) #bgrole(10) is 'Windows'
        self.heading_frame.setAutoFillBackground(True)
        self.heading_frame.setPalette(palette2)

        self.hboxlayout = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(3)
        self.hboxlayout.setObjectName("hboxlayout")

        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Tools/Build Structures/Graphene'))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setObjectName("heading_pixmap")
        self.hboxlayout.addWidget(self.heading_pixmap)

        self.heading_label = QtGui.QLabel(self.heading_frame)

        font = QtGui.QFont(self.heading_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.heading_label.setFont(font)
        self.heading_label.setObjectName("heading_label")
        self.hboxlayout.addWidget(self.heading_label)
        self.vboxlayout.addWidget(self.heading_frame)

        self.sponsor_frame = QtGui.QFrame(graphene_sheet_dialog)
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.sponsor_frame.setObjectName("sponsor_frame")

        self.gridlayout = QtGui.QGridLayout(self.sponsor_frame)
        self.gridlayout.setMargin(0)
        self.gridlayout.setSpacing(0)
        self.gridlayout.setObjectName("gridlayout")

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setMaximumSize(QtCore.QSize(32767,32767))
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.gridlayout.addWidget(self.sponsor_btn,0,0,1,1)
        self.vboxlayout.addWidget(self.sponsor_frame)

        self.body_frame = QtGui.QFrame(graphene_sheet_dialog)
        self.body_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.body_frame.setObjectName("body_frame")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.body_frame)
        self.vboxlayout1.setMargin(3)
        self.vboxlayout1.setSpacing(3)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(2)
        self.hboxlayout1.setObjectName("hboxlayout1")

        spacerItem = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.done_btn = QtGui.QPushButton(self.body_frame)
        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done"))
        self.done_btn.setObjectName("done_btn")
        self.hboxlayout1.addWidget(self.done_btn)

        self.abort_btn = QtGui.QPushButton(self.body_frame)
        self.abort_btn.setIcon(geticon("ui/actions/Properties Manager/Abort"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout1.addWidget(self.abort_btn)

        self.restore_defaults_btn = QtGui.QPushButton(self.body_frame)
        self.restore_defaults_btn.setIcon(geticon("ui/actions/Properties Manager/Restore"))
        self.restore_defaults_btn.setObjectName("restore_defaults_btn")
        self.hboxlayout1.addWidget(self.restore_defaults_btn)

        self.preview_btn = QtGui.QPushButton(self.body_frame)
        self.preview_btn.setIcon(geticon("ui/actions/Properties Manager/Preview"))
        self.preview_btn.setObjectName("preview_btn")
        self.hboxlayout1.addWidget(self.preview_btn)

        self.whatsthis_btn = QtGui.QPushButton(self.body_frame)
        self.whatsthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis"))
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout1.addWidget(self.whatsthis_btn)

        spacerItem1 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.parameters_grpbox = QtGui.QGroupBox(self.body_frame)
        self.parameters_grpbox.setObjectName("parameters_grpbox")
        
        self.parameters_grpbox.setAutoFillBackground(True) 
        palette_param_grpbx =  graphene_sheet_dialog.getGroupBoxPalette()
        self.parameters_grpbox.setPalette(palette_param_grpbx)
        
        styleSheet = graphene_sheet_dialog.getGroupBoxStyleSheet()        
        self.parameters_grpbox.setStyleSheet(styleSheet)

        self.vboxlayout2 = QtGui.QVBoxLayout(self.parameters_grpbox)
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(2)
        self.vboxlayout2.setObjectName("vboxlayout2")

        ###self.graphene_parameters_grpbtn = QtGui.QPushButton(self.parameters_grpbox)

        self.graphene_parameters_grpbtn = graphene_sheet_dialog.getGroupBoxTitleButton(
            "Parameters",
            self.parameters_grpbox)
        
        self.vboxlayout2.addWidget(self.graphene_parameters_grpbtn)

        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setMargin(2)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.height_label = QtGui.QLabel(self.parameters_grpbox)
        self.height_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.height_label.setObjectName("height_label")
        self.gridlayout1.addWidget(self.height_label,1,0,1,1)

        self.height_linedit = QtGui.QLineEdit(self.parameters_grpbox)
        self.height_linedit.setObjectName("height_linedit")
        self.gridlayout1.addWidget(self.height_linedit,1,1,1,1)

        self.width_label = QtGui.QLabel(self.parameters_grpbox)
        self.width_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.width_label.setObjectName("width_label")
        self.gridlayout1.addWidget(self.width_label,2,0,1,1)

        self.width_linedit = QtGui.QLineEdit(self.parameters_grpbox)
        self.width_linedit.setObjectName("width_linedit")
        self.gridlayout1.addWidget(self.width_linedit,2,1,1,1)

        self.bond_length_label = QtGui.QLabel(self.parameters_grpbox)
        self.bond_length_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bond_length_label.setObjectName("bond_length_label")
        self.gridlayout1.addWidget(self.bond_length_label,3,0,1,1)

        self.bond_length_linedit = QtGui.QLineEdit(self.parameters_grpbox)
        self.bond_length_linedit.setObjectName("bond_length_linedit")
        self.gridlayout1.addWidget(self.bond_length_linedit,3,1,1,1)

        self.endings_label = QtGui.QLabel(self.parameters_grpbox)
        self.endings_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endings_label.setObjectName("endings_label")
        self.gridlayout1.addWidget(self.endings_label,4,0,1,1)

        self.endings_combox = QtGui.QComboBox(self.parameters_grpbox)
        self.endings_combox.setObjectName("endings_combox")
        self.gridlayout1.addWidget(self.endings_combox,4,1,1,1)
        self.vboxlayout2.addLayout(self.gridlayout1)
        self.vboxlayout1.addWidget(self.parameters_grpbox)
        self.vboxlayout.addWidget(self.body_frame)

        spacerItem3 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem3)

        self.retranslateUi(graphene_sheet_dialog)
        QtCore.QMetaObject.connectSlotsByName(graphene_sheet_dialog)

    def retranslateUi(self, graphene_sheet_dialog):
        graphene_sheet_dialog.setWindowTitle(QtGui.QApplication.translate("graphene_sheet_dialog", "Graphene sheet", None, QtGui.QApplication.UnicodeUTF8))
        graphene_sheet_dialog.setWindowIcon(QtGui.QIcon("ui/border/Graphene"))
        self.heading_label.setText(QtGui.QApplication.translate("graphene_sheet_dialog", 
                                                                "<font color=\"#FFFFFF\">Graphene Sheet </font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setToolTip(QtGui.QApplication.translate("graphene_sheet_dialog", "Done", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_btn.setToolTip(QtGui.QApplication.translate("graphene_sheet_dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_defaults_btn.setToolTip(QtGui.QApplication.translate("graphene_sheet_dialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_btn.setToolTip(QtGui.QApplication.translate("graphene_sheet_dialog", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.whatsthis_btn.setToolTip(QtGui.QApplication.translate("graphene_sheet_dialog", "What\'s This Help", None, QtGui.QApplication.UnicodeUTF8))
        self.height_label.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "Height (A) :", None, QtGui.QApplication.UnicodeUTF8))
        self.height_linedit.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "20.0", None, QtGui.QApplication.UnicodeUTF8))
        self.width_label.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "Width (A) :", None, QtGui.QApplication.UnicodeUTF8))
        self.width_linedit.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "20.0", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_label.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "Bond Length (A):", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_linedit.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "1.40", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_label.setText(QtGui.QApplication.translate("graphene_sheet_dialog", "Endings :", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("graphene_sheet_dialog", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("graphene_sheet_dialog", "Hydrogen", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("graphene_sheet_dialog", "Nitrogen", None, QtGui.QApplication.UnicodeUTF8))
