# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

__author__ = "Ninad"

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from Utility import geticon, getpixmap
from qt4transition import qt4todo



class Ui_MovePropertyManager(object):
    def setupUi(self, MovePropertyManager):
        
        self.w = MovePropertyManager.w
        
        MovePropertyManager.setObjectName("MovePropertyManager")
        
        palette = MovePropertyManager.getPropertyManagerPalette()
        MovePropertyManager.setPalette(palette)
        
        self.vboxlayout = QtGui.QVBoxLayout(MovePropertyManager)
        self.vboxlayout.setMargin(0) # was 1. Mark 2007-05-24.
        self.vboxlayout.setSpacing(0) # was 1. Mark 2007-05-24.
        self.vboxlayout.setSizeConstraint(QLayout.SetMinimumSize)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.heading_frame = QtGui.QFrame(MovePropertyManager)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        palette2 = QtGui.QPalette()
        palette2.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),
                          QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        self.heading_frame.setAutoFillBackground(True)
        self.heading_frame.setPalette(palette2)

        self.hboxlayout_heading = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout_heading.setMargin(2)
        self.hboxlayout_heading.setSpacing(5)
        self.hboxlayout_heading.setObjectName("hboxlayout")


        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Toolbars/Smart/Move.png'))
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        #self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setObjectName("heading_pixmap")
        
        self.hboxlayout_heading .addWidget(self.heading_pixmap)
        
        self.heading_label = QtGui.QLabel(self.heading_frame)

        font = QtGui.QFont(self.heading_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(100)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.heading_label.setFont(font)
        self.heading_label.setObjectName("heading_label")
        
        
        self.hboxlayout_heading .addWidget(self.heading_label)
        
        self.vboxlayout.addWidget(self.heading_frame)

        self.sponsor_frame = QtGui.QFrame(MovePropertyManager)
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.sponsor_frame.setObjectName("sponsor_frame")

        self.gridlayout_sponsor = QtGui.QGridLayout(self.sponsor_frame)
        self.gridlayout_sponsor.setMargin(0)
        self.gridlayout_sponsor.setSpacing(0)
        self.gridlayout_sponsor.setObjectName("gridlayout")

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.gridlayout_sponsor.addWidget(self.sponsor_btn,0,0,1,1)
        
        self.vboxlayout.addWidget(self.sponsor_frame)
        
        self.ui_doneCancelButtonRow(MovePropertyManager)
        
        self.ui_moveGroupBox(MovePropertyManager)
        
        self.ui_rotateGroupBox(MovePropertyManager)                            
            
                
        #ninad 0700202 its  important to add this spacerItem in the main vboxlayout to prevent the size adjustments in 
        #the property manager when the group items are hidden 
        bottom_spacer = QSpacerItem(10, 1,
                                    QSizePolicy.Minimum,
                                    QSizePolicy.MinimumExpanding)
	
        self.vboxlayout.addItem(bottom_spacer)
	        
        # This should be called last since it only works if all the widgets
	# for this Property Manager are added first. Mark 2007-05-29
        from PropMgrBaseClass import fitPropMgrToContents
	fitPropMgrToContents(MovePropertyManager)
        
    def ui_doneCancelButtonRow(self, MovePropertyManager):
        #Start Done , Abort, button row        
        hboxlayout_buttonrow = QtGui.QHBoxLayout()
        
        leftSpacer = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(leftSpacer)        
                        
        self.button_frame = QtGui.QFrame(MovePropertyManager)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.button_frame.sizePolicy().hasHeightForWidth())
        self.button_frame.setSizePolicy(sizePolicy)
        self.button_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.button_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.button_frame.setObjectName("button_frame")
        
        self.hboxlayout_buttonframe = QtGui.QHBoxLayout(self.button_frame)
        self.hboxlayout_buttonframe.setMargin(2)
        self.hboxlayout_buttonframe.setSpacing(2)
        self.hboxlayout_buttonframe.setObjectName("hboxlayout_buttonframe")
                
        self.done_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.done_btn.sizePolicy().hasHeightForWidth())
        self.done_btn.setSizePolicy(sizePolicy)

        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done.png"))
        self.done_btn.setObjectName("done_btn")        
        
        self.hboxlayout_buttonframe.addWidget(self.done_btn)        
                
        self.whatthis_btn = QtGui.QPushButton(self.button_frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.whatthis_btn.sizePolicy().hasHeightForWidth())
        self.whatthis_btn.setSizePolicy(sizePolicy)
        self.whatthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatthis_btn.setObjectName("whatthis_btn")
        self.hboxlayout_buttonframe.addWidget(self.whatthis_btn)
        
        hboxlayout_buttonrow.addWidget(self.button_frame)
        
        rightSpacer = QtGui.QSpacerItem(40, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(rightSpacer)
    
        self.vboxlayout.addLayout(hboxlayout_buttonrow)        
        #End Done , Abort button row
        
    def ui_moveGroupBox(self, MovePropertyManager):
        #Start Move Groupbox
        self.move_groupBox = QtGui.QGroupBox(MovePropertyManager)
        self.move_groupBox .setObjectName("move_groupBox")
               
        self.move_groupBox.setAutoFillBackground(True)
        palette = MovePropertyManager.getGroupBoxPalette()
        self.move_groupBox.setPalette(palette)
        
        styleSheet = MovePropertyManager.getGroupBoxStyleSheet()        
        self.move_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_move_grpbox = QtGui.QVBoxLayout(self.move_groupBox)
        self.vboxlayout_move_grpbox.setMargin(0)
        self.vboxlayout_move_grpbox.setSpacing(6)
        self.vboxlayout_move_grpbox.setObjectName("vboxlayout_move_grpbox") 
        
        if self.w.toolsMoveMoleculeAction.isChecked():
            self.move_groupBoxButton= MovePropertyManager.getGroupBoxTitleButton(
            "Translate", self.move_groupBox)
        else:
            self.move_groupBoxButton= MovePropertyManager.getGroupBoxTitleButton(
            "Translate", self.move_groupBox, bool_expand = False)
            
        
        self.move_groupBoxButton.setShortcut('T')
        self.vboxlayout_move_grpbox.addWidget(self.move_groupBoxButton) 
        
        
        self.moveGroupBox_widgetHolder = QtGui.QWidget(self.move_groupBox)
        self.vboxlayout_move_grpbox.addWidget(self.moveGroupBox_widgetHolder)
        
        if self.w.toolsMoveMoleculeAction.isChecked():
            self.w.moveFreeAction.setChecked(True)
            self.moveGroupBox_widgetHolder.show()
        else:
            self.moveGroupBox_widgetHolder.hide()
        
        self.vboxlo_moveWidgetHolder = QtGui.QVBoxLayout(self.moveGroupBox_widgetHolder)
        self.vboxlo_moveWidgetHolder.setMargin(4)
        self.vboxlo_moveWidgetHolder.setSpacing(6)
               
        self.movetype_combox = QtGui.QComboBox(self.moveGroupBox_widgetHolder)
        self.movetype_combox.addItem("Free Drag")
        self.movetype_combox.addItem("By Delta XYZ")
        self.movetype_combox.addItem("To XYZ Position")
        self.vboxlo_moveWidgetHolder.addWidget(self.movetype_combox)
        
        #Widget to show when 'Free Drag Combobox item is selected
        self.ui_freeDrag_comboItem(MovePropertyManager)
        
        #Widget to show when "By Delta XYZ combobox item is selected
        self.ui_byDeltaXYZ_comboItem(MovePropertyManager)
        
        #Widget to show when "To XYZ combobox item is selected
        self.ui_toXYZPosition_comboItem(MovePropertyManager)
        
        #End Move Options
        self.vboxlayout.addWidget(self.move_groupBox)
        spacer_move_grpbx = QtGui.QSpacerItem(10,10,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.vboxlayout.addItem(spacer_move_grpbx)
	
	# Height is fixed. Mark 2007-05-29.
	self.move_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_rotateGroupBox(self, MovePropertyManager):
        #Start Rotate Options        
        self.rotate_groupBox = QtGui.QGroupBox(MovePropertyManager)
        self.rotate_groupBox .setObjectName("rotate_groupBox")    
        
        self.rotate_groupBox.setAutoFillBackground(True)
        palette = MovePropertyManager.getGroupBoxPalette()
        self.rotate_groupBox.setPalette(palette)
        
        styleSheet = MovePropertyManager.getGroupBoxStyleSheet()        
        self.rotate_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_rotate_groupBox = QtGui.QVBoxLayout(self.rotate_groupBox)
        self.vboxlayout_rotate_groupBox.setMargin(0)
        self.vboxlayout_rotate_groupBox.setSpacing(6)
        self.vboxlayout_rotate_groupBox.setObjectName("vboxlayout_rotate_groupBox") 
        
        if self.w.rotateComponentsAction.isChecked():
            self.rotate_groupBoxButton =MovePropertyManager.getGroupBoxTitleButton(
            "Rotate", self.rotate_groupBox)
        else:
            self.rotate_groupBoxButton =MovePropertyManager.getGroupBoxTitleButton(
                "Rotate", self.rotate_groupBox,bool_expand = False)
        
        self.rotate_groupBoxButton.setShortcut('R')
        self.vboxlayout_rotate_groupBox.addWidget(self.rotate_groupBoxButton) 
        
        self.rotateGroupBox_widgetHolder = QtGui.QWidget(self.rotate_groupBox)
        self.vboxlayout_rotate_groupBox.addWidget(self.rotateGroupBox_widgetHolder)
        
        if self.w.rotateComponentsAction.isChecked():
            self.w.rotateFreeAction.setChecked(True)
            self.rotateGroupBox_widgetHolder.show()
        else:
            self.rotateGroupBox_widgetHolder.hide() 
                    
        self.vboxlo_rotateWidgetHolder = QtGui.QVBoxLayout(self.rotateGroupBox_widgetHolder)
     
        self.vboxlo_rotateWidgetHolder.setMargin(4)
        self.vboxlo_rotateWidgetHolder.setSpacing(6)
               
        self.rotatetype_combox = QtGui.QComboBox(self.rotateGroupBox_widgetHolder)
        self.rotatetype_combox.addItem("Free Drag")
        self.rotatetype_combox.addItem("By Specified Angle")
        self.vboxlo_rotateWidgetHolder.addWidget(self.rotatetype_combox)
        
        #Widget to show when 'Free Drag Combobox item is selected
        self.ui_freeDragRotate_comboItem(MovePropertyManager)
        
        #Widget to show when "By Specified Angle" combobox item is selected
        self.ui_rotateBySpecifiedAngle_comboItem(MovePropertyManager)
           
        #End Rotate Options Groupbox
        self.vboxlayout.addWidget(self.rotate_groupBox)
        
	# Height is fixed. Mark 2007-05-29.
	self.rotate_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_freeDrag_comboItem(self, MovePropertyManager):
        
        self.freeDragWidget = QtGui.QWidget(self.moveGroupBox_widgetHolder)
        
        hlo = QtGui.QHBoxLayout(self.freeDragWidget)
        hlo.setSpacing(2)
        
        left_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlo.addItem(left_spacer)
        
        self.moveFreeButton = QtGui.QToolButton(self.freeDragWidget)
        self.moveFreeButton.setDefaultAction(self.w.moveFreeAction)
        self.moveFreeButton.setIcon(geticon("ui/actions/Properties Manager/Move_Free"))
                
        self.transXButton = QtGui.QToolButton(self.freeDragWidget)
        self.transXButton.setDefaultAction(self.w.transXAction)
        self.transXButton.setIcon(geticon("ui/actions/Properties Manager/TranslateX"))
        
        self.transYButton = QtGui.QToolButton(self.freeDragWidget)
        self.transYButton.setDefaultAction(self.w.transYAction)
        self.transYButton.setIcon(geticon("ui/actions/Properties Manager/TranslateY"))

        self.transZButton = QtGui.QToolButton(self.freeDragWidget)
        self.transZButton.setDefaultAction(self.w.transZAction)
        self.transZButton.setIcon(geticon("ui/actions/Properties Manager/TranslateZ"))

        for btn in self.moveFreeButton, self.transXButton, self.transYButton, self.transZButton:
            btn.setMinimumSize(QtCore.QSize(24,24))        
            btn.setMinimumSize(QtCore.QSize(24,24))        
            btn.setIconSize(QtCore.QSize(24,24))  
            btn.setAutoRaise(True)
            hlo.addWidget(btn)
        
        right_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlo.addItem(right_spacer)
        
        self.vboxlo_moveWidgetHolder.addWidget(self.freeDragWidget)
        
    
    def ui_byDeltaXYZ_comboItem(self, MovePropertyManager):
        """Widget to show when 'By Delta XYZ Position' item  in the combobox is selected"""
        self.byDeltaXYZWidget = QtGui.QWidget(self.moveGroupBox_widgetHolder)
        lo = QtGui.QVBoxLayout(self.byDeltaXYZWidget)
        lo.setSpacing(2)
        
        self.dx_label = QtGui.QLabel(self.byDeltaXYZWidget)
        self.dx_label.setText("Delta X: ")        
        self.dy_label = QtGui.QLabel(self.byDeltaXYZWidget)
        self.dy_label.setText("Delta Y: ")        
        self.dz_label = QtGui.QLabel(self.byDeltaXYZWidget)
        self.dz_label.setText("Delta Z: ")
        
        hlayout_x = QtGui.QHBoxLayout()
        hlayout_x.setSpacing(4)
        hlayout_y = QtGui.QHBoxLayout()
        hlayout_y.setSpacing(4)
        hlayout_z = QtGui.QHBoxLayout()
        hlayout_z.setSpacing(4)
        
        hlayout_x.addWidget(self.dx_label)        
        hlayout_y.addWidget(self.dy_label)
        hlayout_z.addWidget(self.dz_label)
        
        self.moveDeltaXSpinBox = QtGui.QDoubleSpinBox(self.byDeltaXYZWidget)
        self.moveDeltaXSpinBox.setSuffix(" A")
        hlayout_x.addWidget(self.moveDeltaXSpinBox)
        spacer_x = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_x.addItem(spacer_x)
        self.moveDeltaYSpinBox = QtGui.QDoubleSpinBox(self.byDeltaXYZWidget)
        self.moveDeltaYSpinBox.setSuffix(" A")
        hlayout_y.addWidget(self.moveDeltaYSpinBox)
        spacer_y = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_y.addItem(spacer_y)
        self.moveDeltaZSpinBox = QtGui.QDoubleSpinBox(self.byDeltaXYZWidget)
        self.moveDeltaZSpinBox.setSuffix(" A")
        hlayout_z.addWidget(self.moveDeltaZSpinBox)
        spacer_z = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_z.addItem(spacer_z)
        
        for spinbox in self.moveDeltaXSpinBox, self.moveDeltaYSpinBox, self.moveDeltaZSpinBox:           
            spinbox.setDecimals(1)
            spinbox.setRange(0, 2000)              
        
        lo.addLayout(hlayout_x)
        lo.addLayout(hlayout_y)
        lo.addLayout(hlayout_z)
        
        hlayout_delta_btns = QtGui.QHBoxLayout()
        hlayout_delta_btns.setSpacing(2)
        
        self.moveDeltaPlusButton = QtGui.QToolButton(self.byDeltaXYZWidget)
        self.moveDeltaPlusButton.setMinimumSize(QtCore.QSize(24,24))
        self.moveDeltaPlusButton.setDefaultAction(self.w.moveDeltaPlusAction)
        self.moveDeltaPlusButton.setMinimumSize(QtCore.QSize(24,24))
        self.moveDeltaPlusButton.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Plus"))
        self.moveDeltaPlusButton.setIconSize(QtCore.QSize(24,24))  
        self.moveDeltaPlusButton.setAutoRaise(True)
        
        hlayout_delta_btns.addWidget(self.moveDeltaPlusButton)
        
        self.moveDeltaMinusButton = QtGui.QToolButton(self.byDeltaXYZWidget)
        self.moveDeltaMinusButton.setMinimumSize(QtCore.QSize(24,24))
        self.moveDeltaMinusButton.setDefaultAction(self.w.moveDeltaMinusAction)
        self.moveDeltaMinusButton.setMinimumSize(QtCore.QSize(24,24))
        self.moveDeltaMinusButton.setIcon(geticon("ui/actions/Properties Manager/Move_Delta_Minus"))
        self.moveDeltaMinusButton.setIconSize(QtCore.QSize(24,24))  
        self.moveDeltaMinusButton.setAutoRaise(True)
        
        hlayout_delta_btns.addWidget(self.moveDeltaMinusButton)
        
        spacer_delta_btns = QtGui.QSpacerItem(40, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout_delta_btns.addItem(spacer_delta_btns)
        
        lo.addLayout(hlayout_delta_btns)           
        
        self.byDeltaXYZWidget.hide()
        self.vboxlo_moveWidgetHolder.addWidget(self.byDeltaXYZWidget)
        
    
    def ui_toXYZPosition_comboItem(self, MovePropertyManager):
        """Widget to show when 'To XYZ Position' item in the combobox is selected."""
        self.toXYZPositionWidget = QtGui.QWidget(self.moveGroupBox_widgetHolder)
        lo = QtGui.QVBoxLayout(self.toXYZPositionWidget)
        lo.setSpacing(2)
        
        self.x_label = QtGui.QLabel(self.toXYZPositionWidget)
        self.x_label.setText("X: ")        
        self.y_label = QtGui.QLabel(self.toXYZPositionWidget)
        self.y_label.setText("Y: ")        
        self.z_label = QtGui.QLabel(self.toXYZPositionWidget)
        self.z_label.setText("Z: ")
        
        hlayout_x = QtGui.QHBoxLayout()
        hlayout_x.setSpacing(4)
        hlayout_y = QtGui.QHBoxLayout()
        hlayout_y.setSpacing(4)
        hlayout_z = QtGui.QHBoxLayout()
        hlayout_z.setSpacing(4)
        
        hlayout_x.addWidget(self.x_label)        
        hlayout_y.addWidget(self.y_label)
        hlayout_z.addWidget(self.z_label)
        
        self.moveXSpinBox = QtGui.QDoubleSpinBox(self.toXYZPositionWidget)
        self.moveXSpinBox.setSuffix(" A")
        hlayout_x.addWidget(self.moveXSpinBox)
        spacer_x = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_x.addItem(spacer_x)
        self.moveYSpinBox = QtGui.QDoubleSpinBox(self.toXYZPositionWidget)
        self.moveYSpinBox.setSuffix(" A")
        hlayout_y.addWidget(self.moveYSpinBox)
        spacer_y = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_y.addItem(spacer_y)
        self.moveZSpinBox = QtGui.QDoubleSpinBox(self.toXYZPositionWidget)
        self.moveZSpinBox.setSuffix(" A")
        hlayout_z.addWidget(self.moveZSpinBox)
        spacer_z = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlayout_z.addItem(spacer_z)
        
        for spinbox in self.moveXSpinBox, self.moveYSpinBox, self.moveZSpinBox:           
            spinbox.setDecimals(1)
            spinbox.setRange(0, 2000)              
        
        lo.addLayout(hlayout_x)
        lo.addLayout(hlayout_y)
        lo.addLayout(hlayout_z)
        
        self.moveAbsoluteButton = QtGui.QToolButton(self.toXYZPositionWidget)
        #Add Action to button
        self.moveAbsoluteButton.setDefaultAction(self.w.moveAbsoluteAction)
        self.moveAbsoluteButton.setMinimumSize(QtCore.QSize(24,24))
        self.moveAbsoluteButton.setIcon(geticon("ui/actions/Properties Manager/Move_Absolute"))
        self.moveAbsoluteButton.setIconSize(QtCore.QSize(24,24))       
        self.moveAbsoluteButton.setAutoRaise(True)
        
        lo.addWidget(self.moveAbsoluteButton)           
        self.toXYZPositionWidget.hide()
        self.vboxlo_moveWidgetHolder.addWidget(self.toXYZPositionWidget) 
        
    #Rotate Goupbox widgets 
    def ui_freeDragRotate_comboItem(self, MovePropertyManager):
    
        self.freeDragRotateWidget = QtGui.QWidget(self.rotateGroupBox_widgetHolder)
        
        vlo = QtGui.QVBoxLayout(self.freeDragRotateWidget)
        vlo.setSpacing(2)
        vlo.setMargin(2)
          
        hlo = QtGui.QHBoxLayout()
        hlo.setSpacing(2)
        
        left_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlo.addItem(left_spacer)
             
        self.rotateFreeButton = QtGui.QToolButton(self.freeDragRotateWidget)
        self.rotateFreeButton.setDefaultAction(self.w.rotateFreeAction)
        self.rotateFreeButton.setIcon(geticon("ui/actions/Properties Manager/Rotate_Free"))
                
        self.rotateXButton = QtGui.QToolButton(self.freeDragRotateWidget)
        self.rotateXButton.setDefaultAction(self.w.rotXAction)
        self.rotateXButton.setIcon(geticon("ui/actions/Properties Manager/RotateX"))
        
        self.rotateYButton = QtGui.QToolButton(self.freeDragRotateWidget)
        self.rotateYButton.setDefaultAction(self.w.rotYAction)
        self.rotateYButton.setIcon(geticon("ui/actions/Properties Manager/RotateY"))

        self.rotateZButton = QtGui.QToolButton(self.freeDragRotateWidget)
        self.rotateZButton.setDefaultAction(self.w.rotZAction)
        self.rotateZButton.setIcon(geticon("ui/actions/Properties Manager/RotateZ"))

        for btn in self.rotateFreeButton, self.rotateXButton, self.rotateYButton, self.rotateZButton:
            btn.setMinimumSize(QtCore.QSize(24,24))            
            btn.setIconSize(QtCore.QSize(24,24))  
            btn.setAutoRaise(True)
            hlo.addWidget(btn)
        
        right_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlo.addItem(right_spacer)
        
        vlo.addLayout(hlo)
        
         #Rotate as a unit checkbox-- Show when Rotate Free drag action is checked
        
        self.rotateAsUnitCB = QCheckBox("Rotate as unit", self.rotateGroupBox_widgetHolder)
        self.rotateAsUnitCB.setChecked(1)
        self.rotateAsUnitCB.setToolTip('Rotate selection as a unit')
        
        if self.w.rotateFreeAction.isChecked():
            self.rotateAsUnitCB.show()
        else:
            self.rotateAsUnitCB.hide()
        
        vlo.addWidget(self.rotateAsUnitCB)               
             
        #Rotation Angle Deltas
        #ninad 070321 disabled self.rotationAngleDeltas_lbl as its crowding the groupbox and also
        #giving obvious/reduendent information. 
        ##self.rotationAngleDeltas_lbl = QtGui.QLabel("Rotation Angle Deltas in Degrees:", self.rotateGroupBox_widgetHolder)
        ##self.vboxlo_rotateWidgetHolder.addWidget(self.rotationAngleDeltas_lbl)
               
        rotdelta_x_lo = QtGui.QHBoxLayout()
        rotdelta_x_lo.setSpacing(2)        
                
        self.lbl_x = QtGui.QLabel("Delta Theta X: ", self.freeDragRotateWidget)
        rotdelta_x_lo.addWidget(self.lbl_x)              
        self.deltaThetaX_lbl = QtGui.QLabel("   0.00", self.freeDragRotateWidget)
        rotdelta_x_lo.addWidget(self.deltaThetaX_lbl)        
        self.degree_lbl_x = QtGui.QLabel("Degrees", self.freeDragRotateWidget)
        rotdelta_x_lo.addWidget(self.degree_lbl_x) 
                
        vlo.addLayout(rotdelta_x_lo)
                
        rotdelta_y_lo = QtGui.QHBoxLayout()
        rotdelta_y_lo.setSpacing(2)        
        
        self.lbl_y = QtGui.QLabel("Delta Theta Y: ", self.freeDragRotateWidget)   
        rotdelta_y_lo.addWidget(self.lbl_y)
        self.deltaThetaY_lbl = QtGui.QLabel("   0.00", self.freeDragRotateWidget)
        self.vboxlo_rotateWidgetHolder.addWidget(self.deltaThetaY_lbl)    
        rotdelta_y_lo.addWidget(self.deltaThetaY_lbl)   
        self.degree_lbl_y = QtGui.QLabel("Degrees", self.freeDragRotateWidget)               
        rotdelta_y_lo.addWidget(self.degree_lbl_y) 
        
        vlo.addLayout(rotdelta_y_lo)
        
        rotdelta_z_lo = QtGui.QHBoxLayout()
        rotdelta_z_lo.setSpacing(2)
        
        self.lbl_z = QtGui.QLabel("Delta Theta Z : ", self.freeDragRotateWidget) 
        rotdelta_z_lo.addWidget(self.lbl_z)        
        self.deltaThetaZ_lbl = QtGui.QLabel("  0.00", self.freeDragRotateWidget)
        rotdelta_z_lo.addWidget(self.deltaThetaZ_lbl)        
        self.degree_lbl_z = QtGui.QLabel("Degrees", self.freeDragRotateWidget)
        rotdelta_z_lo.addWidget(self.degree_lbl_z) 
        
        vlo.addLayout(rotdelta_z_lo)
        
        #hide the rotation delta labels. This will be modified later based on the rotate 
        #action checked
        lst = [ self.lbl_x, self.lbl_y, self.lbl_z,
                self.deltaThetaX_lbl, self.deltaThetaY_lbl, 
                self.deltaThetaZ_lbl,
                self.degree_lbl_x, self.degree_lbl_y,
                self.degree_lbl_z]
        for thing in lst:
            thing.hide()
        
        rotate_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        vlo.addItem(rotate_spacer)
        
        self.vboxlo_rotateWidgetHolder.addWidget(self.freeDragRotateWidget)
        
    def ui_rotateBySpecifiedAngle_comboItem(self, MovePropertyManager):
        """Widget to show when ''By Specified Angle'' item  in the Rotate combobox is selected"""
        self.rotateBySpecifiedAngleWidget = QtGui.QWidget(self.rotateGroupBox_widgetHolder)
        
        vlo = QtGui.QVBoxLayout(self.rotateBySpecifiedAngleWidget)
        vlo.setSpacing(2)
        vlo.setMargin(2)
        
        #horizontal layout for tool buttons. 
        hlo = QtGui.QHBoxLayout()     
        hlo.setSpacing(2)
        hlo.setMargin(0)
        
        self.rotateAroundAxis_label = QtGui.QLabel(self.rotateBySpecifiedAngleWidget)
        self.rotateAroundAxis_label.setText("Rotate Around: ")       
        hlo.addWidget(self.rotateAroundAxis_label)
        
        self.rotateAroundAxisButtonGroup = QtGui.QButtonGroup()
        self.rotateAroundAxisButtonGroup.setExclusive(True)
        
        self.rotateByThetaXButton = QtGui.QToolButton(self.rotateBySpecifiedAngleWidget)
        self.rotateByThetaXButton .setIcon(geticon("ui/actions/Properties Manager/RotateX"))
        self.rotateByThetaXButton.setObjectName('Rotate X')
        
        self.rotateByThetaYButton = QtGui.QToolButton(self.rotateBySpecifiedAngleWidget)
        self.rotateByThetaYButton .setIcon(geticon("ui/actions/Properties Manager/RotateY"))
        self.rotateByThetaYButton.setObjectName('Rotate Y')
        
        self.rotateByThetaZButton = QtGui.QToolButton( self.rotateBySpecifiedAngleWidget)
        self.rotateByThetaZButton .setIcon(geticon("ui/actions/Properties Manager/RotateZ"))
        self.rotateByThetaZButton.setObjectName('Rotate Z')
        
        lst = [self.rotateByThetaXButton, self.rotateByThetaYButton,
               self.rotateByThetaZButton]
        for btn in lst:
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.setMinimumSize(QtCore.QSize(24,24))           
            btn.setIconSize(QtCore.QSize(24,24))  
            btn.setAutoRaise(True)
            self.rotateAroundAxisButtonGroup.addButton(btn)            
            hlo.addWidget(btn)            
            
        vlo.addLayout(hlo)    
        
        hlo2 = QtGui.QHBoxLayout()
        hlo2.setSpacing(2)
        hlo2.setMargin(0)
        
        self.rotateBy_label = QtGui.QLabel(self.rotateBySpecifiedAngleWidget)
        self.rotateBy_label.setText("Rotate By: ")  
        hlo2.addWidget(self.rotateBy_label)
                    
        self.rotateThetaSpinBox = QtGui.QDoubleSpinBox(self.rotateBySpecifiedAngleWidget)
        self.rotateThetaSpinBox.setSuffix(" Degrees")
        self.rotateThetaSpinBox.setDecimals(2)
        self.rotateThetaSpinBox.setRange(0, 360)    
        hlo2.addWidget(self.rotateThetaSpinBox)
        
        vlo.addLayout(hlo2)
        
        hlo3 = QtGui.QHBoxLayout()
        hlo3.setSpacing(2)
        hlo3.setMargin(0)
        
        self.rotateDirection_label = QtGui.QLabel(self.rotateBySpecifiedAngleWidget)
        self.rotateDirection_label.setText("Direction: ")  
        hlo3.addWidget(self.rotateDirection_label)        
        
        self.rotateThetaPlusButton = QtGui.QToolButton(self.rotateBySpecifiedAngleWidget)
        self.rotateThetaPlusButton.setDefaultAction(self.w.rotateThetaPlusAction)
        self.rotateThetaPlusButton.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Plus"))
        
        self.rotateThetaMinusButton = QtGui.QToolButton(self.freeDragWidget)
        self.rotateThetaMinusButton.setDefaultAction(self.w.rotateThetaMinusAction)
        self.rotateThetaMinusButton.setIcon(geticon("ui/actions/Properties Manager/Move_Theta_Minus"))
        
        for btn in self.rotateThetaPlusButton, self.rotateThetaMinusButton:
            btn.setMinimumSize(QtCore.QSize(24,24))        
            btn.setMinimumSize(QtCore.QSize(24,24))        
            btn.setIconSize(QtCore.QSize(24,24))  
            btn.setCheckable(False)
            btn.setAutoRaise(True)
            hlo3.addWidget(btn)
            
        right_spacer = QtGui.QSpacerItem(20,5,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        hlo3.addItem(right_spacer)
        
        vlo.addLayout(hlo3)                
        self.rotateBySpecifiedAngleWidget.hide()
        self.vboxlo_rotateWidgetHolder.addWidget(self.rotateBySpecifiedAngleWidget)        
        
        
    def retranslateUi(self, MovePropertyManager):
        MovePropertyManager.setWindowTitle(QtGui.QApplication.translate("MovePropertyManager", 
                                                                        "MovePropertyManager",
                                                                        None, QtGui.QApplication.UnicodeUTF8))
        self.heading_label.setText(QtGui.QApplication.translate("MovePropertyManager", 
                                                                "<font color=\"#FFFFFF\">Translate </font>", 
                                                                None, QtGui.QApplication.UnicodeUTF8))        