# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from Utility import geticon, getpixmap

class Ui_nanotube_dialog(object):
    def setupUi(self, nanotube_dialog):
        nanotube_dialog.setObjectName("nanotube_dialog")
        nanotube_dialog.resize(QtCore.QSize(
            QtCore.QRect(0,0,200,591).size()).expandedTo(
                nanotube_dialog.minimumSizeHint()))
        
        palette = nanotube_dialog.getPropertyManagerPalette()
        nanotube_dialog.setPalette(palette)

        self.vboxlayout = QtGui.QVBoxLayout(nanotube_dialog)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.heading_frame = QtGui.QFrame(nanotube_dialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        palette2 = QtGui.QPalette()
        palette2.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(150,150,140)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(150, 150,140)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(150,150,140)) #bgrole(10) is 'Windows'
        self.heading_frame.setAutoFillBackground(True)
        self.heading_frame.setPalette(palette2)

        self.hboxlayout = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(3)
        self.hboxlayout.setObjectName("hboxlayout")

        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setPixmap(getpixmap(
            'ui/actions/Tools/Build Structures/Nanotube'))  

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),
                                       QtGui.QSizePolicy.Policy(0))
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

        self.sponsor_frame = QtGui.QFrame(nanotube_dialog)
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


        self.ui_doneCancelButtonRow(nanotube_dialog)
        self.ui_parametersGroupBox(nanotube_dialog)
        self.ui_tubeDistortionsGroupBox(nanotube_dialog)        
        self.ui_mwcntGroupBox(nanotube_dialog)
        
        
        spacerItem5 = QtGui.QSpacerItem(20,20,QtGui.QSizePolicy.Minimum,
                                        QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem5)


        self.retranslateUi(nanotube_dialog)
        QtCore.QMetaObject.connectSlotsByName(nanotube_dialog)
        nanotube_dialog.setTabOrder(self.sponsor_btn,self.nt_parameters_grpbtn)
        nanotube_dialog.setTabOrder(self.nt_parameters_grpbtn,self.members_combox)
        nanotube_dialog.setTabOrder(self.members_combox,self.length_linedit)
        nanotube_dialog.setTabOrder(self.length_linedit,self.chirality_n_spinbox)
        nanotube_dialog.setTabOrder(self.chirality_n_spinbox,
                                    self.chirality_m_spinbox)
        nanotube_dialog.setTabOrder(self.chirality_m_spinbox,
                                    self.bond_length_linedit)
        nanotube_dialog.setTabOrder(self.bond_length_linedit,
                                    self.endings_combox)
        nanotube_dialog.setTabOrder(self.endings_combox,
                                    self.nt_distortion_grpbtn)
        nanotube_dialog.setTabOrder(self.nt_distortion_grpbtn,
                                    self.z_distortion_linedit)
        nanotube_dialog.setTabOrder(self.z_distortion_linedit,
                                    self.xy_distortion_linedit)
        nanotube_dialog.setTabOrder(self.xy_distortion_linedit,
                                    self.twist_spinbox)
        nanotube_dialog.setTabOrder(self.twist_spinbox,self.bend_spinbox)
        nanotube_dialog.setTabOrder(self.bend_spinbox,self.mwcnt_grpbtn)
        nanotube_dialog.setTabOrder(self.mwcnt_grpbtn,self.mwcnt_count_spinbox)
        nanotube_dialog.setTabOrder(self.mwcnt_count_spinbox,
                                    self.mwcnt_spacing_linedit)

    def ui_doneCancelButtonRow(self, nanotube_dialog):
        
        #Start Done , Abort, button row
        
        hboxlayout_buttonrow = QtGui.QHBoxLayout()
        
        leftSpacer = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, 
                                       QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(leftSpacer)
        self.button_frame = QtGui.QFrame(nanotube_dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),
                                       QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.button_frame.sizePolicy().hasHeightForWidth())
        self.button_frame.setSizePolicy(sizePolicy)
        self.button_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.button_frame.setObjectName("button_frame")
        
        self.hboxlayout_buttonframe = QtGui.QHBoxLayout(self.button_frame)
        self.hboxlayout_buttonframe.setMargin(2)
        self.hboxlayout_buttonframe.setSpacing(2)
        self.hboxlayout_buttonframe.setObjectName("hboxlayout_buttonframe")
                
        self.done_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),
                                       QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.done_btn.sizePolicy().hasHeightForWidth())
        self.done_btn.setSizePolicy(sizePolicy)

        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done.png"))
        self.done_btn.setObjectName("done_btn")
        
        self.hboxlayout_buttonframe.addWidget(self.done_btn)
        
        self.abort_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abort_btn.sizePolicy().hasHeightForWidth())
        self.abort_btn.setSizePolicy(sizePolicy)
        self.abort_btn.setIcon(geticon("ui/actions/Properties Manager/Abort.png"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout_buttonframe.addWidget(self.abort_btn)
        
        self.restore_defaults_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abort_btn.sizePolicy().hasHeightForWidth())
        self.restore_defaults_btn.setSizePolicy(sizePolicy)
        self.restore_defaults_btn.setIcon(geticon("ui/actions/Properties Manager/Restore"))
        self.restore_defaults_btn.setObjectName("restore_defaults_btn")
        self.hboxlayout_buttonframe.addWidget(self.restore_defaults_btn)
        
        self.preview_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.abort_btn.sizePolicy().hasHeightForWidth())
        self.preview_btn.setSizePolicy(sizePolicy)
        self.preview_btn.setIcon(geticon("ui/actions/Properties Manager/Preview"))
        self.preview_btn.setObjectName("preview_btn")
        self.hboxlayout_buttonframe.addWidget(self.preview_btn)        
        
        self.whatsthis_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.whatsthis_btn.sizePolicy().hasHeightForWidth())
        self.whatsthis_btn.setSizePolicy(sizePolicy)
        self.whatsthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout_buttonframe.addWidget(self.whatsthis_btn)
        
        hboxlayout_buttonrow.addWidget(self.button_frame)
        
        rightSpacer = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(rightSpacer)
    
        #self.vboxlayout.addWidget(self.button_frame)
        self.vboxlayout.addLayout(hboxlayout_buttonrow)
        #End Done , Abort button row
        
    def ui_parametersGroupBox(self, nanotube_dialog):        
        self.parameters_grpbox = QtGui.QGroupBox(nanotube_dialog)
        self.parameters_grpbox.setObjectName("parameters_grpbox")
        
        self.parameters_grpbox.setAutoFillBackground(True) 
        palette =  nanotube_dialog.getGroupBoxPalette()
        self.parameters_grpbox.setPalette(palette)
        
        styleSheet = nanotube_dialog.getGroupBoxStyleSheet()        
        self.parameters_grpbox.setStyleSheet(styleSheet)

        self.vboxlayout2 = QtGui.QVBoxLayout(self.parameters_grpbox)
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")
    
        self.nt_parameters_grpbtn = nanotube_dialog.getGroupBoxTitleButton(
        "Nanotube Parameters", self.parameters_grpbox)    
        self.vboxlayout2.addWidget(self.nt_parameters_grpbtn)    
            
        self.gridlayout1 = QtGui.QGridLayout()
        self.gridlayout1.setMargin(0)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.chirality_n_label = QtGui.QLabel(self.parameters_grpbox)
        self.chirality_n_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.chirality_n_label.setObjectName("chirality_n_label")
        self.gridlayout1.addWidget(self.chirality_n_label,2,0,1,1)

        self.chirality_m_spinbox = QtGui.QSpinBox(self.parameters_grpbox)
        self.chirality_m_spinbox.setMinimum(0)
        self.chirality_m_spinbox.setProperty("value",QtCore.QVariant(5))
        self.chirality_m_spinbox.setObjectName("chirality_m_spinbox")
        self.gridlayout1.addWidget(self.chirality_m_spinbox,3,1,1,1)

        self.chirality_m_label = QtGui.QLabel(self.parameters_grpbox)
        self.chirality_m_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.chirality_m_label.setObjectName("chirality_m_label")
        self.gridlayout1.addWidget(self.chirality_m_label,3,0,1,1)

        self.length_label = QtGui.QLabel(self.parameters_grpbox)
        self.length_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.length_label.setObjectName("length_label")
        self.gridlayout1.addWidget(self.length_label,1,0,1,1)

        self.chirality_n_spinbox = QtGui.QSpinBox(self.parameters_grpbox)
        self.chirality_n_spinbox.setMinimum(0)
        self.chirality_n_spinbox.setProperty("value",QtCore.QVariant(5))
        self.chirality_n_spinbox.setObjectName("chirality_n_spinbox")
        self.gridlayout1.addWidget(self.chirality_n_spinbox,2,1,1,1)

        self.members_combox = QtGui.QComboBox(self.parameters_grpbox)
        self.members_combox.setObjectName("members_combox")
        self.gridlayout1.addWidget(self.members_combox,0,1,1,1)

        self.endings_label = QtGui.QLabel(self.parameters_grpbox)
        self.endings_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.endings_label.setObjectName("endings_label")
        self.gridlayout1.addWidget(self.endings_label,5,0,1,1)

        self.bond_length_label = QtGui.QLabel(self.parameters_grpbox)
        self.bond_length_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bond_length_label.setObjectName("bond_length_label")
        self.gridlayout1.addWidget(self.bond_length_label,4,0,1,1)

        self.endings_combox = QtGui.QComboBox(self.parameters_grpbox)
        self.endings_combox.setObjectName("endings_combox")
        self.gridlayout1.addWidget(self.endings_combox,5,1,1,1)

        self.length_linedit = QtGui.QLineEdit(self.parameters_grpbox)
        self.length_linedit.setObjectName("length_linedit")
        self.gridlayout1.addWidget(self.length_linedit,1,1,1,1)

        self.type_label = QtGui.QLabel(self.parameters_grpbox)
        self.type_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.type_label.setObjectName("type_label")
        self.gridlayout1.addWidget(self.type_label,0,0,1,1)

        self.bond_length_linedit = QtGui.QLineEdit(self.parameters_grpbox)
        self.bond_length_linedit.setObjectName("bond_length_linedit")
        self.gridlayout1.addWidget(self.bond_length_linedit,4,1,1,1)
        self.vboxlayout2.addLayout(self.gridlayout1)
        #End Parameters Groupbox
        
        self.vboxlayout.addWidget(self.parameters_grpbox)
        spacer_param_grpbx = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.vboxlayout.addItem(spacer_param_grpbx)
        
    def ui_tubeDistortionsGroupBox(self, nanotube_dialog):        
        self.tube_distortions_grpbox = QtGui.QGroupBox(nanotube_dialog)
        self.tube_distortions_grpbox.setObjectName("tube_distortions_grpbox")
        
        self.vboxlayout3 = QtGui.QVBoxLayout(self.tube_distortions_grpbox)
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")     
        
        self.tube_distortions_grpbox.setAutoFillBackground(True)         
        palette =  nanotube_dialog.getGroupBoxPalette()
        self.tube_distortions_grpbox.setPalette(palette)
    
        styleSheet = nanotube_dialog.getGroupBoxStyleSheet()        
        self.tube_distortions_grpbox.setStyleSheet(styleSheet)   

        self.nt_distortion_grpbtn = nanotube_dialog.getGroupBoxTitleButton(
            "Nanotube Distortion", self.tube_distortions_grpbox)    
        self.vboxlayout3.addWidget(self.nt_distortion_grpbtn)

        self.gridlayout2 = QtGui.QGridLayout()
        self.gridlayout2.setMargin(0)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.z_distortion_label = QtGui.QLabel(self.tube_distortions_grpbox)
        self.z_distortion_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.z_distortion_label.setObjectName("z_distortion_label")
        self.gridlayout2.addWidget(self.z_distortion_label,0,0,1,1)

        self.xy_distortion_label = QtGui.QLabel(self.tube_distortions_grpbox)
        self.xy_distortion_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.xy_distortion_label.setObjectName("xy_distortion_label")
        self.gridlayout2.addWidget(self.xy_distortion_label,1,0,1,1)

        self.twist_spinbox = QtGui.QSpinBox(self.tube_distortions_grpbox)
        self.twist_spinbox.setMinimum(0)
        self.twist_spinbox.setProperty("value",QtCore.QVariant(0))
        self.twist_spinbox.setObjectName("twist_spinbox")
        self.gridlayout2.addWidget(self.twist_spinbox,2,1,1,1)

        self.z_distortion_linedit = QtGui.QLineEdit(self.tube_distortions_grpbox)
        self.z_distortion_linedit.setObjectName("z_distortion_linedit")
        self.gridlayout2.addWidget(self.z_distortion_linedit,0,1,1,1)

        self.bend_label = QtGui.QLabel(self.tube_distortions_grpbox)
        self.bend_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.bend_label.setObjectName("bend_label")
        self.gridlayout2.addWidget(self.bend_label,3,0,1,1)

        self.bend_spinbox = QtGui.QSpinBox(self.tube_distortions_grpbox)
        self.bend_spinbox.setMaximum(360)
        self.bend_spinbox.setMinimum(0)
        self.bend_spinbox.setProperty("value",QtCore.QVariant(0))
        self.bend_spinbox.setObjectName("bend_spinbox")
        self.gridlayout2.addWidget(self.bend_spinbox,3,1,1,1)

        self.xy_distortion_linedit = QtGui.QLineEdit(self.tube_distortions_grpbox)
        self.xy_distortion_linedit.setObjectName("xy_distortion_linedit")
        self.gridlayout2.addWidget(self.xy_distortion_linedit,1,1,1,1)

        self.twist_label = QtGui.QLabel(self.tube_distortions_grpbox)
        self.twist_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.twist_label.setObjectName("twist_label")
        self.gridlayout2.addWidget(self.twist_label,2,0,1,1)
        self.vboxlayout3.addLayout(self.gridlayout2)
        self.vboxlayout.addWidget(self.tube_distortions_grpbox)
        
        spacer_tubedist_grpbx = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.vboxlayout.addItem(spacer_tubedist_grpbx)
        
    def ui_mwcntGroupBox(self, nanotube_dialog):
        self.mwcnt_grpbox = QtGui.QGroupBox(nanotube_dialog)
        self.mwcnt_grpbox.setObjectName("mwcnt_grpbox")
        
        self.mwcnt_grpbox.setAutoFillBackground(True) 
        
        palette =  nanotube_dialog.getGroupBoxPalette()
        self.mwcnt_grpbox.setPalette(palette)
    
        styleSheet = nanotube_dialog.getGroupBoxStyleSheet()        
        self.mwcnt_grpbox.setStyleSheet(styleSheet)

        self.vboxlayout4 = QtGui.QVBoxLayout(self.mwcnt_grpbox)
        self.vboxlayout4.setMargin(0)
        self.vboxlayout4.setSpacing(6)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.mwcnt_grpbtn = nanotube_dialog.getGroupBoxTitleButton(
            "Multi-Walled Nanotubes", self.mwcnt_grpbox)
        self.vboxlayout4.addWidget(self.mwcnt_grpbtn)

        self.gridlayout3 = QtGui.QGridLayout()
        self.gridlayout3.setMargin(0)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.mwcnt_spacing_label = QtGui.QLabel(self.mwcnt_grpbox)
        self.mwcnt_spacing_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mwcnt_spacing_label.setObjectName("mwcnt_spacing_label")
        self.gridlayout3.addWidget(self.mwcnt_spacing_label,1,0,1,1)

        self.mwcnt_count_label = QtGui.QLabel(self.mwcnt_grpbox)
        self.mwcnt_count_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mwcnt_count_label.setObjectName("mwcnt_count_label")
        self.gridlayout3.addWidget(self.mwcnt_count_label,0,0,1,1)

        self.mwcnt_count_spinbox = QtGui.QSpinBox(self.mwcnt_grpbox)
        self.mwcnt_count_spinbox.setMinimum(0)
        self.mwcnt_count_spinbox.setProperty("value",QtCore.QVariant(1))
        self.mwcnt_count_spinbox.setObjectName("mwcnt_count_spinbox")
        self.gridlayout3.addWidget(self.mwcnt_count_spinbox,0,1,1,1)

        self.mwcnt_spacing_linedit = QtGui.QLineEdit(self.mwcnt_grpbox)
        self.mwcnt_spacing_linedit.setObjectName("mwcnt_spacing_linedit")
        self.gridlayout3.addWidget(self.mwcnt_spacing_linedit,1,1,1,1)
        self.vboxlayout4.addLayout(self.gridlayout3)
        self.vboxlayout.addWidget(self.mwcnt_grpbox)
        spacer_mwcnt_grpbx = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.vboxlayout.addItem(spacer_mwcnt_grpbx)
        

    def retranslateUi(self, nanotube_dialog):
        nanotube_dialog.setWindowTitle(QtGui.QApplication.translate("nanotube_dialog", "Nanotube", None, QtGui.QApplication.UnicodeUTF8))
        nanotube_dialog.setWindowIcon(QtGui.QIcon("ui/border/Nanotube"))
        self.heading_label.setText(QtGui.QApplication.translate("nanotube_dialog", 
                                                                "<font color=\"#FFFFFF\">Nanotube </font>",  
                                                                None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_btn.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_defaults_btn.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_btn.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.whatsthis_btn.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "What\'s This Help", None, QtGui.QApplication.UnicodeUTF8))
      
        self.chirality_n_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Chirality (n) :", None, QtGui.QApplication.UnicodeUTF8))
        self.chirality_m_spinbox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Chirality (m)", None, QtGui.QApplication.UnicodeUTF8))
        self.chirality_m_label.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Chirality (m)", None, QtGui.QApplication.UnicodeUTF8))
        self.chirality_m_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Chirality (m) :", None, QtGui.QApplication.UnicodeUTF8))
        self.length_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Length (A) :", None, QtGui.QApplication.UnicodeUTF8))
        self.chirality_n_spinbox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Chirality (n)", None, QtGui.QApplication.UnicodeUTF8))
        self.members_combox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Members", None, QtGui.QApplication.UnicodeUTF8))
        self.members_combox.addItem(QtGui.QApplication.translate("nanotube_dialog", "Carbon", None, QtGui.QApplication.UnicodeUTF8))
        self.members_combox.addItem(QtGui.QApplication.translate("nanotube_dialog", "Boron Nitride", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Endings :", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_label.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Bond length in angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Bond Length (A):", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Endings", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("nanotube_dialog", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("nanotube_dialog", "Hydrogen", None, QtGui.QApplication.UnicodeUTF8))
        self.endings_combox.addItem(QtGui.QApplication.translate("nanotube_dialog", "Nitrogen", None, QtGui.QApplication.UnicodeUTF8))
        self.length_linedit.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Length of nanotube in angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.length_linedit.setText(QtGui.QApplication.translate("nanotube_dialog", "20.0", None, QtGui.QApplication.UnicodeUTF8))
        self.type_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Type :", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_linedit.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Bond length in angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.bond_length_linedit.setText(QtGui.QApplication.translate("nanotube_dialog", "1.40", None, QtGui.QApplication.UnicodeUTF8))
        
        self.z_distortion_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Z-distortion (A):", None, QtGui.QApplication.UnicodeUTF8))
        self.xy_distortion_label.setText(QtGui.QApplication.translate("nanotube_dialog", "XY-distortion (A):", None, QtGui.QApplication.UnicodeUTF8))
        self.twist_spinbox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Twist in degrees/angstrom", None, QtGui.QApplication.UnicodeUTF8))
        self.twist_spinbox.setSuffix(QtGui.QApplication.translate("nanotube_dialog", " deg/A", None, QtGui.QApplication.UnicodeUTF8))
        self.z_distortion_linedit.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Z-distortion in angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.z_distortion_linedit.setText(QtGui.QApplication.translate("nanotube_dialog", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.bend_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Bend :", None, QtGui.QApplication.UnicodeUTF8))
        self.bend_spinbox.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "Bend in degrees", None, QtGui.QApplication.UnicodeUTF8))
        self.bend_spinbox.setSuffix(QtGui.QApplication.translate("nanotube_dialog", " deg", None, QtGui.QApplication.UnicodeUTF8))
        self.xy_distortion_linedit.setToolTip(QtGui.QApplication.translate("nanotube_dialog", "XY-distortion", None, QtGui.QApplication.UnicodeUTF8))
        self.xy_distortion_linedit.setText(QtGui.QApplication.translate("nanotube_dialog", "0.0", None, QtGui.QApplication.UnicodeUTF8))
        self.twist_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Twist :", None, QtGui.QApplication.UnicodeUTF8))

        self.mwcnt_spacing_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Spacing (A):", None, QtGui.QApplication.UnicodeUTF8))
        self.mwcnt_count_label.setText(QtGui.QApplication.translate("nanotube_dialog", "Number of Nanotubes :", None, QtGui.QApplication.UnicodeUTF8))
        self.mwcnt_count_spinbox.setToolTip(QtGui.QApplication.translate("nanotube_dialog",
                                                                         "Number of nanotubes", 
                                                                         None, 
                                                                         QtGui.QApplication.UnicodeUTF8))
        self.mwcnt_spacing_linedit.setToolTip(QtGui.QApplication.translate("nanotube_dialog", 
                                                                           "Spacing between nanotubes", 
                                                                           None, QtGui.QApplication.UnicodeUTF8))
        self.mwcnt_spacing_linedit.setText(QtGui.QApplication.translate("nanotube_dialog", "2.46", None, QtGui.QApplication.UnicodeUTF8))

      
