# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MMKit.py 

$Id$

History: 

Originally created by Mark and Huaicai using Qt3 designer
Till Alpha8,  MMKit existed  as a Dialog. 

In October 2006 Will ported MMKitDialog to NE1 on Qt4 

October 2006 onwards Ninad integrated Build Dashboard and MMKitDialog 
and converted it into a 'Property Manager' 

ninad070207 made enhancements to this Build Property Manager

As of 070207 it is still refered as MMKitDialog. Should really be called
'Build Property Manager' as it also implements old dashboard functionality
-- ninad 070207

mark 2007-05-29: Fixed sizePolicy for all widgets so everything behaves itself
                 in a fixed width Property Manager (for Alpha 9).
"""

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import *
from Utility import geticon, getpixmap
import env
from prefs_constants import *
from PropMgr_Constants import *
from PropMgrBaseClass import getPalette
        
class Ui_MMKitDialog(object):
    def setupUi(self, MMKitDialog):
        MMKitDialog.setObjectName("MMKitDialog")

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(0),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(1),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(3),QtGui.QColor(242,243,242))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(4),QtGui.QColor(115,115,115))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(5),QtGui.QColor(153,154,153))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(6),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(8),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(9),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(12),QtGui.QColor(0,0,128))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(15),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(0),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(1),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(3),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(4),QtGui.QColor(115,115,115))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(5),QtGui.QColor(153,154,153))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(6),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(8),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(9),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(12),QtGui.QColor(0,0,128))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(15),QtGui.QColor(255,0,255))
        palette.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(0),QtGui.QColor(128,128,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(1),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(2),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(3),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(4),QtGui.QColor(115,115,115))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(5),QtGui.QColor(153,154,153))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(6),QtGui.QColor(128,128,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(7),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(8),QtGui.QColor(128,128,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(9),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),QtGui.QColor(230,231,230))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(11),QtGui.QColor(0,0,0))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(12),QtGui.QColor(0,0,128))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(13),QtGui.QColor(255,255,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(14),QtGui.QColor(0,0,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(15),QtGui.QColor(255,0,255))
        palette.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(16),QtGui.QColor(232,232,232))
        MMKitDialog.setPalette(palette)

        self.vboxlayout = QtGui.QVBoxLayout(MMKitDialog)
        self.vboxlayout.setMargin(pmMainVboxLayoutMargin)
        self.vboxlayout.setSpacing(pmMainVboxLayoutSpacing)
        self.vboxlayout.setObjectName("vboxlayout")
        
        self.heading_frame = QtGui.QFrame(MMKitDialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        palette2 = QtGui.QPalette()
        palette2.setColor(QtGui.QPalette.Active,QtGui.QPalette.ColorRole(10),QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Inactive,QtGui.QPalette.ColorRole(10),QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        palette2.setColor(QtGui.QPalette.Disabled,QtGui.QPalette.ColorRole(10),QtGui.QColor(120,120,120)) #bgrole(10) is 'Windows'
        self.heading_frame.setAutoFillBackground(True)
        self.heading_frame.setPalette(palette2)

        self.hboxlayout_heading = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout_heading.setMargin(pmHeaderFrameMargin)
        self.hboxlayout_heading.setSpacing(pmHeaderFrameSpacing)
        self.hboxlayout_heading.setObjectName("hboxlayout")
        
        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setPixmap(getpixmap('ui/actions/Tools/Build Structures/Atoms.png'))     
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        #self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setObjectName("heading_pixmap")
        self.hboxlayout_heading .addWidget(self.heading_pixmap)
        
        self.heading_label = QtGui.QLabel(self.heading_frame)
        self.heading_label.setFont(getHeaderFont())
        self.hboxlayout_heading .addWidget(self.heading_label)
        
        self.vboxlayout.addWidget(self.heading_frame)

        self.sponsor_frame = QtGui.QFrame(MMKitDialog)
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.sponsor_frame.setObjectName("sponsor_frame")

        self.gridlayout_sponsor = QtGui.QGridLayout(self.sponsor_frame)
        self.gridlayout_sponsor.setMargin(pmSponsorFrameMargin)
        self.gridlayout_sponsor.setSpacing(pmSponsorFrameSpacing)
        self.gridlayout_sponsor.setObjectName("gridlayout")

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.gridlayout_sponsor.addWidget(self.sponsor_btn,0,0,1,1)
        
        self.vboxlayout.addWidget(self.sponsor_frame)
        
        # ninad 070221 Call methods that define different groupboxes and 
        #done cancel rows (groupbox  methods also define spacer items 
        #after the groupbox)
        self.ui_doneCancelButtonRow(MMKitDialog)
	
	self.ui_message_GroupBox(MMKitDialog)
	
        self.ui_bondTools_grpBox(MMKitDialog)
        
        self.ui_preview_GroupBox(MMKitDialog)
        
        self.ui_MMKit_GroupBox(MMKitDialog)
        
        self.ui_selectionFilter_GroupBox(MMKitDialog)
        
        self.ui_advancedOps_GroupBox(MMKitDialog)
                                
        ######################################################.
        
        #ninad 070120 Following spacerItem is important to add in the main vboxlayout to prevent the size adjustments in 
        #the property manager when the group items are hidden 
        bottom_spacer = QtGui.QSpacerItem(20,1,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(bottom_spacer)

        self.retranslateUi(MMKitDialog)
        
        QtCore.QMetaObject.connectSlotsByName(MMKitDialog)

	# This should be called last since it only works if all the widgets
	# for this Property Manager are added first. Mark 2007-05-29
        from PropMgrBaseClass import fitPropMgrToContents
	fitPropMgrToContents(MMKitDialog)
	
	# End of MMKitDialog ####################################
    
    def ui_doneCancelButtonRow(self, MMKitDialog):
        #Start Done , Abort, button row
        
        hboxlayout_buttonrow = QtGui.QHBoxLayout()
        
        hSpacer = QtGui.QSpacerItem(10, 10, QtGui.QSizePolicy.Expanding, QSizePolicy.Minimum)
        hboxlayout_buttonrow.addItem(hSpacer)
              
        self.button_frame = QtGui.QFrame(MMKitDialog)

        self.button_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.button_frame.setFrameShadow(QtGui.QFrame.Plain)
        
        self.hboxlayout_buttonframe = QtGui.QHBoxLayout(self.button_frame)
        self.hboxlayout_buttonframe.setMargin(pmTopRowBtnsMargin)
        self.hboxlayout_buttonframe.setSpacing(pmTopRowBtnsSpacing)
                
        self.done_btn = QtGui.QToolButton(self.button_frame)
        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done.png"))
	self.done_btn.setIconSize(QSize(22,22))
        self.hboxlayout_buttonframe.addWidget(self.done_btn)
                
        self.whatsthis_btn = QtGui.QToolButton(self.button_frame)
        self.whatsthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis.png"))
	self.whatsthis_btn.setIconSize(QSize(22,22))
        self.hboxlayout_buttonframe.addWidget(self.whatsthis_btn)

        hboxlayout_buttonrow.addWidget(self.button_frame)
        
        hboxlayout_buttonrow.addItem(hSpacer)
    
        self.vboxlayout.addLayout(hboxlayout_buttonrow)
        
        #End Done , Abort button row
    
    def ui_message_GroupBox(self, MMKitDialog):
        #Start Advanced Options GroupBox
        self.message_groupBox = QtGui.QGroupBox(MMKitDialog)        
        
        self.message_groupBox.setAutoFillBackground(True) 
        palette = MMKitDialog.getGroupBoxPalette()
        self.message_groupBox.setPalette(palette)
        
        styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
        self.message_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_msgbox = QtGui.QVBoxLayout(self.message_groupBox)
        self.vboxlayout_msgbox.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_msgbox.setSpacing(pmGrpBoxVboxLayoutSpacing)

        self.message_groupBoxButton = \
	    MMKitDialog.getGroupBoxTitleButton("Message", self.message_groupBox)
        
        self.vboxlayout_msgbox.addWidget(self.message_groupBoxButton)

        # Yellow TextEdit here
	
	self.MsgTextEdit = QtGui.QTextEdit(self.message_groupBox)
        self.MsgTextEdit.setMaximumHeight(80) # 80 pixels height
        self.MsgTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
	
	msg_palette = getPalette(None,
                          QPalette.Base,
                          pmMessageTextEditColor)
	
	self.MsgTextEdit.setPalette(msg_palette)
	self.MsgTextEdit.setReadOnly(True)
	
	self.vboxlayout_msgbox.addWidget(self.MsgTextEdit)
	        
        # End Message GroupBox
        self.vboxlayout.addWidget(self.message_groupBox)
	
	# Height is fixed. Mark 2007-05-29.
	self.message_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_bondTools_grpBox(self, MMKitDialog):
        #Start Atom Bond tools Groupbox
    
	self.bondTools_grpBox = QtGui.QGroupBox(MMKitDialog)
	self.bondTools_grpBox.setObjectName("bondTools_grpBox")
	
	self.bondTools_grpBox.setAutoFillBackground(True) 
	palette = MMKitDialog.getGroupBoxPalette()
	self.bondTools_grpBox.setPalette(palette)
	
	styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
	self.bondTools_grpBox.setStyleSheet(styleSheet)

	self.vboxlayout_grpbox1 = QtGui.QVBoxLayout(self.bondTools_grpBox)
	self.vboxlayout_grpbox1.setMargin(pmGrpBoxVboxLayoutMargin)
	self.vboxlayout_grpbox1.setSpacing(pmGrpBoxVboxLayoutSpacing)
	self.vboxlayout_grpbox1.setObjectName("vboxlayout_grpbox1")
	
	self.bondTool_groupBoxButton = MMKitDialog.getGroupBoxTitleButton(
	    "Bonds Tool", 
	    self.bondTools_grpBox)      
	
	self.vboxlayout_grpbox1.addWidget(self.bondTool_groupBoxButton)
	
	#Atom and bond Tools action
	#Following Actions are added in the Flyout toolbar. 
	#Defining them outside that method as those are being used
	#by the subclasses of deposit mode (testmode.py as of 070410) -- ninad
	
	self.depositAtomsAction = QtGui.QWidgetAction(self.w)
	self.depositAtomsAction.setText("Atoms Tool")
	self.depositAtomsAction.setIcon(geticon(
	    'ui/actions/Toolbars/Smart/Deposit_Atoms'))
	self.depositAtomsAction.setCheckable(True)
	self.depositAtomsAction.setChecked(True)
	
		
	self.transmuteBondsAction = QtGui.QWidgetAction(self.w)
	self.transmuteBondsAction.setText("Bonds Tool")
	self.transmuteBondsAction.setIcon(geticon(
	    'ui/actions/Toolbars/Smart/Transmute_Bonds'))
	self.transmuteBondsAction.setCheckable(True)
		
	self.bondToolWidget = QtGui.QWidget(self.bondTools_grpBox)	
	
	hlo_bondtool = QtGui.QHBoxLayout(self.bondToolWidget)
	hlo_bondtool.setMargin(2)
	hlo_bondtool.setSpacing(2)
    
	self.bondToolsActionGroup = QtGui.QActionGroup(MMKitDialog.w)
	self.bondToolsActionGroup.setExclusive(True)
		
	self.bond1Action = QtGui.QWidgetAction(MMKitDialog.w)  
	self.bond1Action.setText("Single")
	self.bond1Action.setIcon(geticon("ui/dashboard/bond1.png"))
    
	self.bond2Action = QtGui.QWidgetAction(MMKitDialog.w)  
	self.bond2Action.setText("Double")
	self.bond2Action.setIcon(geticon("ui/dashboard/bond2.png"))
	
	self.bond3Action = QtGui.QWidgetAction(MMKitDialog.w)  
	self.bond3Action.setText("Triple")
	self.bond3Action.setIcon(geticon("ui/dashboard/bond3.png"))
	
	self.bondaAction = QtGui.QWidgetAction(MMKitDialog.w)  
	self.bondaAction.setText("Aromatic")
	self.bondaAction.setIcon(geticon("ui/dashboard/bonda.png"))
	
	self.bondgAction = QtGui.QWidgetAction(MMKitDialog.w)  
	self.bondgAction.setText("Graphitic")
	self.bondgAction.setIcon(geticon("ui/dashboard/bondg.png"))

	for action in self.bond1Action, self.bond2Action, self.bond3Action,self.bondaAction, self.bondgAction:
	    
	    btn = QtGui.QToolButton()
	    btn.setDefaultAction(action)       
	    btn.setIconSize(QtCore.QSize(22,22))
	    btn.setAutoRaise(1)        
	    action.setCheckable(True)	
	    self.bondToolsActionGroup.addAction(action)
	    hlo_bondtool.addWidget(btn)
       
	self.vboxlayout_grpbox1.addWidget(self.bondToolWidget)
	
	# End Atom Bond Tools Groupbox
	self.vboxlayout.addWidget(self.bondTools_grpBox)
	
	spacer_BondTools_grpbx = QtGui.QSpacerItem(10, pmGroupBoxSpacing, 
						   QtGui.QSizePolicy.Fixed,
						   QtGui.QSizePolicy.Fixed)
	
	self.vboxlayout.addItem(spacer_BondTools_grpbx)
	
	# Height is fixed. Mark 2007-05-29.
	self.bondTools_grpBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_preview_GroupBox(self, MMKitDialog):
        # Start MMKit ThumbView  (Preview) GroupBox        
        
        self.thumbView_groupBox = QtGui.QGroupBox(MMKitDialog)
        self.thumbView_groupBox.setObjectName("thumbView_groupBox")
        
        self.thumbView_groupBox.setAutoFillBackground(True) 
        palette = MMKitDialog.getGroupBoxPalette()
        self.thumbView_groupBox.setPalette(palette)
        
        styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
        self.thumbView_groupBox.setStyleSheet(styleSheet)
        
        
        self.vboxlayout_grpbox2 = QtGui.QVBoxLayout(self.thumbView_groupBox)
        self.vboxlayout_grpbox2.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox2.setSpacing(pmGrpBoxVboxLayoutSpacing)
        self.vboxlayout_grpbox2.setObjectName("vboxlayout_grpbox2")

        self.thumbView_groupBoxButton = MMKitDialog.getGroupBoxTitleButton("Preview", self.thumbView_groupBox)
        
        self.vboxlayout_grpbox2.addWidget(self.thumbView_groupBoxButton)
      
               
        self.elementFrame = QtGui.QFrame(self.thumbView_groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.elementFrame.sizePolicy().hasHeightForWidth())
        self.elementFrame.setSizePolicy(sizePolicy)
        self.elementFrame.setMinimumSize(QtCore.QSize(150,150))
        self.elementFrame.setFrameShape(QtGui.QFrame.Box)
        self.elementFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.elementFrame.setObjectName("elementFrame")
        
        self.vboxlayout_grpbox2.addWidget(self.elementFrame)   
    
        #End  MMKit ThumbView  (Preview) GroupBox 
        self.vboxlayout.addWidget(self.thumbView_groupBox)        
        spacer_thumbview_grpbx = QtGui.QSpacerItem(10, pmGroupBoxSpacing, 
						   QtGui.QSizePolicy.Fixed,
						   QtGui.QSizePolicy.Fixed)
        self.vboxlayout.addItem(spacer_thumbview_grpbx)
	
	# Height is fixed. Mark 2007-05-29.
	self.thumbView_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_MMKit_GroupBox(self, MMKitDialog):        
        #Start MMKit groupbox (includes atom, clipboard and library tabs)
        self.MMKit_groupBox = QtGui.QGroupBox(MMKitDialog)
        self.MMKit_groupBox.setObjectName("MMKit_groupBox")
        
        self.MMKit_groupBox.setAutoFillBackground(True) 
        palette = MMKitDialog.getGroupBoxPalette()
        self.MMKit_groupBox.setPalette(palette)
        
        styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
        self.MMKit_groupBox.setStyleSheet(styleSheet)

        self.vboxlayout_grpbox3 = QtGui.QVBoxLayout(self.MMKit_groupBox)
        self.vboxlayout_grpbox3.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox3.setSpacing(pmGrpBoxVboxLayoutSpacing)
        self.vboxlayout_grpbox3.setObjectName("vboxlayout_grpbox3")

        self.MMKit_groupBoxButton = MMKitDialog.getGroupBoxTitleButton("MMKit", self.MMKit_groupBox)
       
        self.vboxlayout_grpbox3.addWidget(self.MMKit_groupBoxButton)

        self.mmkit_tab = QtGui.QTabWidget(self.MMKit_groupBox)
        self.mmkit_tab.setEnabled(True)
	
	# Height is fixed. Mark 2007-05-29.
	self.mmkit_tab.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
	
        self.mmkit_tab.setObjectName("mmkit_tab")

        self.atomsPage = QtGui.QWidget()
        self.atomsPage.setObjectName("atomsPage")
        
        self.mmkit_tab.addTab(self.atomsPage, "")    

        self.frame5 = QtGui.QFrame(self.atomsPage)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame5.sizePolicy().hasHeightForWidth())
        self.frame5.setSizePolicy(sizePolicy)
        self.frame5.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame5.setFrameShadow(QtGui.QFrame.Plain)
        self.frame5.setMinimumSize(QtCore.QSize(100,100))
        self.frame5.setObjectName("frame5")
        
        self.vboxlayout_atomsPage = QtGui.QVBoxLayout(self.frame5)
        self.vboxlayout_atomsPage.setMargin(pmMMKitPageMargin) # Was 4. Mark 2007-05-30
        self.vboxlayout_atomsPage.setSpacing(2)

	# Element Button GroupBox begins here. #####################
	
        self.elementButtonGroup = QtGui.QGroupBox(self.frame5)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(3),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.elementButtonGroup.sizePolicy().hasHeightForWidth())
        self.elementButtonGroup.setSizePolicy(sizePolicy)
        self.elementButtonGroup.setMinimumSize(QtCore.QSize(0,95))
        self.elementButtonGroup.setObjectName("elementButtonGroup")

        self.gridlayout2 = QtGui.QGridLayout(self.elementButtonGroup)
        self.gridlayout2.setMargin(1) # Was 0. Mark 2007-05-30
        self.gridlayout2.setSpacing(0)
        self.gridlayout2.setObjectName("gridlayout2")
	
	# Font for toolbuttons.
        font = QFont(self.frame5.font())
	font.setFamily(pmMMKitButtonFont)
	font.setPointSize(pmMMKitButtonFontPointSize)
	font.setBold(pmMMKitButtonFontBold)
        #font.setWeight(75)
        #font.setItalic(False)
        #font.setUnderline(False)
        #font.setStrikeOut(False)
        
        # All this would be much nicer in a for loop. 
	# Later, when time permits. Mark 2007-05-30.

        self.toolButton1 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton1.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton1.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton1.setCheckable(True)
	self.toolButton1.setFont(font)
        self.toolButton1.setObjectName("toolButton1")
        self.gridlayout2.addWidget(self.toolButton1,0,4,1,1)

        self.toolButton2 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton2.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton2.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton2.setCheckable(True)
	self.toolButton2.setFont(font)
        self.toolButton2.setObjectName("toolButton2")
        self.gridlayout2.addWidget(self.toolButton2,0,5,1,1)

        self.toolButton6 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton6.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton6.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton6.setCheckable(True)
	self.toolButton6.setFont(font)
        self.toolButton6.setObjectName("toolButton6")
        self.gridlayout2.addWidget(self.toolButton6,1,1,1,1)

        self.toolButton7 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton7.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton7.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton7.setCheckable(True)
	self.toolButton7.setFont(font)
        self.toolButton7.setObjectName("toolButton7")
        self.gridlayout2.addWidget(self.toolButton7,1,2,1,1)

        self.toolButton8 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton8.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton8.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton8.setCheckable(True)
	self.toolButton8.setFont(font)
        self.toolButton8.setObjectName("toolButton8")
        self.gridlayout2.addWidget(self.toolButton8,1,3,1,1)

        self.toolButton10 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton10.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton10.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton10.setCheckable(True)
	self.toolButton10.setFont(font)
        self.toolButton10.setObjectName("toolButton10")
        self.gridlayout2.addWidget(self.toolButton10,1,5,1,1)

        self.toolButton9 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton9.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton9.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton9.setCheckable(True)
	self.toolButton9.setFont(font)
        self.toolButton9.setObjectName("toolButton9")
        self.gridlayout2.addWidget(self.toolButton9,1,4,1,1)

        self.toolButton13 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton13.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton13.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton13.setCheckable(True)
	self.toolButton13.setFont(font)
        self.toolButton13.setObjectName("toolButton13")
        self.gridlayout2.addWidget(self.toolButton13,2,0,1,1)

        self.toolButton17 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton17.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton17.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton17.setCheckable(True)
	self.toolButton17.setFont(font)
        self.toolButton17.setObjectName("toolButton17")
        self.gridlayout2.addWidget(self.toolButton17,2,4,1,1)

        self.toolButton5 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton5.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton5.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton5.setCheckable(True)
	self.toolButton5.setFont(font)
        self.toolButton5.setObjectName("toolButton5")
        self.gridlayout2.addWidget(self.toolButton5,1,0,1,1)

        self.toolButton10_2 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton10_2.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton10_2.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton10_2.setCheckable(True)
	self.toolButton10_2.setFont(font)
        self.toolButton10_2.setObjectName("toolButton10_2")
        self.gridlayout2.addWidget(self.toolButton10_2,2,5,1,1)

        self.toolButton15 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton15.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton15.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton15.setCheckable(True)
	self.toolButton15.setFont(font)
        self.toolButton15.setObjectName("toolButton15")
        self.gridlayout2.addWidget(self.toolButton15,2,2,1,1)

        self.toolButton16 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton16.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton16.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton16.setCheckable(True)
	self.toolButton16.setFont(font)
        self.toolButton16.setObjectName("toolButton16")
        self.gridlayout2.addWidget(self.toolButton16,2,3,1,1)

        self.toolButton14 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton14.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton14.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton14.setCheckable(True)
	self.toolButton14.setFont(font)
        self.toolButton14.setObjectName("toolButton14")
        self.gridlayout2.addWidget(self.toolButton14,2,1,1,1)

        self.toolButton33 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton33.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton33.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton33.setCheckable(True)
	self.toolButton33.setFont(font)
        self.toolButton33.setObjectName("toolButton33")
        self.gridlayout2.addWidget(self.toolButton33,3,2,1,1)

        self.toolButton34 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton34.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton34.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton34.setCheckable(True)
	self.toolButton34.setFont(font)
        self.toolButton34.setObjectName("toolButton34")
        self.gridlayout2.addWidget(self.toolButton34,3,3,1,1)

        self.toolButton35 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton35.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton35.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton35.setCheckable(True)
	self.toolButton35.setFont(font)
        self.toolButton35.setObjectName("toolButton35")
        self.gridlayout2.addWidget(self.toolButton35,3,4,1,1)

        self.toolButton32 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton32.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton32.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton32.setCheckable(True)
	self.toolButton32.setFont(font)
        self.toolButton32.setObjectName("toolButton32")
        self.gridlayout2.addWidget(self.toolButton32,3,1,1,1)

        self.toolButton36 = QtGui.QToolButton(self.elementButtonGroup)
        self.toolButton36.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.toolButton36.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.toolButton36.setCheckable(True)
	self.toolButton36.setFont(font)
        self.toolButton36.setObjectName("toolButton36")
        self.gridlayout2.addWidget(self.toolButton36,3,5,1,1)
        
        self.vboxlayout_atomsPage.addWidget(self.elementButtonGroup)
	
	# Height is fixed. Mark 2007-05-29.
	self.elementButtonGroup.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
	
	# Atomic Hybrid label
	self.atomic_hybrids_label = QtGui.QLabel(self.frame5)
	self.atomic_hybrids_label.setText("Atomic Hybrids :")
	self.vboxlayout_atomsPage.addWidget(self.atomic_hybrids_label)
	    
	# Elements Button GroupBox ends here. #######################
        
        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

	# Hybrid GroupBox begins here ###############################
	
        self.hybrid_btngrp = QtGui.QGroupBox(self.frame5)
        self.hybrid_btngrp.setObjectName("hybrid_btngrp")
        self.hboxlayout.addWidget(self.hybrid_btngrp)
        
        self.hboxlayout1 = QtGui.QHBoxLayout(self.hybrid_btngrp)
        self.hboxlayout1.setMargin(2)
        self.hboxlayout1.setSpacing(0)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.sp3_btn = QtGui.QToolButton(self.hybrid_btngrp)
        self.sp3_btn.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.sp3_btn.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.sp3_btn.setCheckable(True)
        self.sp3_btn.setObjectName("sp3_btn")
        self.hboxlayout1.addWidget(self.sp3_btn)

        self.sp2_btn = QtGui.QToolButton(self.hybrid_btngrp)
        self.sp2_btn.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.sp2_btn.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.sp2_btn.setCheckable(True)
        self.sp2_btn.setObjectName("sp2_btn")
        self.hboxlayout1.addWidget(self.sp2_btn)

        self.sp_btn = QtGui.QToolButton(self.hybrid_btngrp)
        self.sp_btn.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.sp_btn.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.sp_btn.setCheckable(True)
        self.sp_btn.setObjectName("sp_btn")
        self.hboxlayout1.addWidget(self.sp_btn)

        self.graphitic_btn = QtGui.QToolButton(self.hybrid_btngrp)
        self.graphitic_btn.setMinimumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
	self.graphitic_btn.setMaximumSize(QtCore.QSize(pmMMKitButtonWidth,pmMMKitButtonHeight))
        self.graphitic_btn.setCheckable(True)
        self.graphitic_btn.setObjectName("graphitic_btn")
        self.hboxlayout1.addWidget(self.graphitic_btn)
	
	self.hboxlayout1.addStretch(0)
	
	# Height is fixed. Mark 2007-05-29.
	self.hybrid_btngrp.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
	
        spacerItem2 = QtGui.QSpacerItem(10, 20, 
					QtGui.QSizePolicy.Fixed,
					QtGui.QSizePolicy.Fixed)
        self.hboxlayout1.addItem(spacerItem2)       
         
        self.vboxlayout_atomsPage.addLayout(self.hboxlayout)
	
	# Mark. 2007-05-30
	bottom_vspacer = QtGui.QSpacerItem(10,1,QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Expanding)
	
	self.vboxlayout_atomsPage.addItem(bottom_vspacer)

	# Clipboard page begins here ############################################
	
        self.clipboardPage = QtGui.QWidget()
        self.clipboardPage.setObjectName("clipboardPage")

        self.gridlayout3 = QtGui.QGridLayout(self.clipboardPage)
        self.gridlayout3.setMargin(pmMMKitPageMargin) # Was 4. Mark 2007-05-30
        self.gridlayout3.setSpacing(2)
        self.gridlayout3.setObjectName("gridlayout3")

        self.chunkListBox = QtGui.QListWidget(self.clipboardPage)

        self.chunkListBox.setMinimumSize(QtCore.QSize(100,100))
	
	# Height is fixed. Mark 2007-05-29.
	self.chunkListBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.MinimumExpanding),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
	
        self.chunkListBox.setObjectName("chunkListBox")
        self.gridlayout3.addWidget(self.chunkListBox,0,0,1,1)
        self.mmkit_tab.addTab(self.clipboardPage, "")
        
        self.libraryPage = QtGui.QWidget()
        #self.libraryPage = QtGui.QScrollArea()
        #self.libraryPageWidget = QtGui.QWidget()
        #self.libraryPage.setWidget(self.libraryPageWidget)
        self.libraryPage.setObjectName("libraryPage")
        self.mmkit_tab.addTab(self.libraryPage, "")

        self.vboxlayout_grpbox3.addWidget(self.mmkit_tab)
        
        self.transmuteAtomsAction = QtGui.QWidgetAction(self.w)
	self.transmuteAtomsAction.setText("Transmute")
	self.transmuteAtomsAction.setIcon(geticon(
	    'ui/actions/Toolbars/Smart/Transmute_Atoms'))	
	self.transmuteAtomsAction.setCheckable(False)
	
        hlo_1 = QtGui.QHBoxLayout()
	
        self.transmuteBtn = QtGui.QToolButton(self.MMKit_groupBox)
	self.transmuteBtn.setDefaultAction(self.transmuteAtomsAction)
        self.transmuteBtn.setFixedSize(QtCore.QSize(36, 36))
	self.transmuteBtn.setIconSize(QtCore.QSize(22,22))
        hlo_1.addWidget(self.transmuteBtn)
	
	self.browseButton = QtGui.QPushButton(MMKitDialog)
	self.browseButton.setMaximumSize(QtCore.QSize(80,60))
	hlo_1.addWidget(self.browseButton)
	
	self.defaultPartLibButton = QtGui.QPushButton(MMKitDialog)
	self.defaultPartLibButton.setMaximumSize(QtCore.QSize(80,60))
	hlo_1.addWidget(self.defaultPartLibButton)
	
	spacer_browsebtn = QtGui.QSpacerItem(5,5,
					     QtGui.QSizePolicy.Expanding,
					     QtGui.QSizePolicy.Minimum)
	
	hlo_1.addItem(spacer_browsebtn)
	
	self.vboxlayout_grpbox3.addLayout(hlo_1)
        
        self.transmuteCB = QtGui.QCheckBox(" Force to Keep Bonds", self.MMKit_groupBox)
        
        self.vboxlayout_grpbox3.addWidget(self.transmuteCB)
	
        #End MMKit groupbox
        self.vboxlayout.addWidget(self.MMKit_groupBox)
        
        spacer_mmkit_grpbx = QtGui.QSpacerItem(10, pmGroupBoxSpacing, 
						QtGui.QSizePolicy.Fixed,
						QtGui.QSizePolicy.Fixed)
	
        self.vboxlayout.addItem(spacer_mmkit_grpbx)
	
	# This line is important. Without it, the MMKit groupbox is
	# too wide by default and causes a horizontal scrollbar 
	# to be displayed at the bottom of the PropMgr. Mark 2007-05-30
	self.MMKit_groupBox.setMinimumWidth(200)

	# Height is fixed. Mark 2007-05-29.
	self.MMKit_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.MinimumExpanding),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
    
    def ui_selectionFilter_GroupBox(self, MMKitDialog):
        #Start Selection Filter GroupBox
        self.selectionFilter_groupBox = QtGui.QGroupBox(MMKitDialog)
        self.selectionFilter_groupBox.setObjectName("selectionFilter_groupBox")
        
        self.selectionFilter_groupBox.setAutoFillBackground(True) 
        palette = MMKitDialog.getGroupBoxPalette()
        self.selectionFilter_groupBox.setPalette(palette)
        
        styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
        self.selectionFilter_groupBox.setStyleSheet(styleSheet)
        
        self.hboxlayout_selfilter = QtGui.QHBoxLayout()
        self.hboxlayout_selfilter.setMargin(pmGrpBoxVboxLayoutMargin)
        self.hboxlayout_selfilter.setSpacing(6)
        self.hboxlayout_selfilter.setObjectName("hboxlayout_selfilter")
        
        self.vboxlayout_selfilter = QtGui.QVBoxLayout(self.selectionFilter_groupBox)
        self.vboxlayout_selfilter.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_selfilter.setSpacing(6)
        self.vboxlayout_selfilter.setObjectName("vboxlayout_selfilter")

        self.filterCB = MMKitDialog.getGroupBoxTitleCheckBox("Selection Filter ", self.selectionFilter_groupBox )
        
        self.vboxlayout_selfilter.addWidget(self.filterCB)
        
        self.selectionFilter_label = QtGui.QLabel(self.selectionFilter_groupBox)
        self.vboxlayout_selfilter.addWidget(self.selectionFilter_label)
        
        self.filterlistLE = QLineEdit(self.selectionFilter_groupBox)
        self.filterlistLE.setReadOnly(1)
        self.filterlistLE.setEnabled(0)
        
        if self.filterCB.isChecked():
            self.filterlistLE.show()
            self.selectionFilter_label.show()
        else:
            self.filterlistLE.hide()
            self.selectionFilter_label.hide()  
            
        self.vboxlayout_selfilter.addWidget(self.filterlistLE)        
        #End Selection filter GroupBox
        self.vboxlayout.addWidget(self.selectionFilter_groupBox)
        
        spacer_selfilter_grpbx = QtGui.QSpacerItem(10, pmGroupBoxSpacing, 
						   QtGui.QSizePolicy.Fixed,
						   QtGui.QSizePolicy.Fixed)
	
        self.vboxlayout.addItem(spacer_selfilter_grpbx)
	
	# Height is fixed. Mark 2007-05-29.
	self.selectionFilter_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
        
    def ui_advancedOps_GroupBox(self, MMKitDialog):
        #Start Advanced Options GroupBox
        self.advancedOptions_groupBox = QtGui.QGroupBox(MMKitDialog)        
        self.advancedOptions_groupBox.setObjectName("advancedOptions_groupBox")
        
        self.advancedOptions_groupBox.setAutoFillBackground(True) 
        palette = MMKitDialog.getGroupBoxPalette()
        self.advancedOptions_groupBox.setPalette(palette)
        
        styleSheet = MMKitDialog.getGroupBoxStyleSheet()        
        self.advancedOptions_groupBox.setStyleSheet(styleSheet)
        
        self.vboxlayout_grpbox4 = QtGui.QVBoxLayout(self.advancedOptions_groupBox)
        self.vboxlayout_grpbox4.setMargin(pmGrpBoxVboxLayoutMargin)
        self.vboxlayout_grpbox4.setSpacing(pmGrpBoxVboxLayoutSpacing)
        self.vboxlayout_grpbox4.setObjectName("vboxlayout_grpbox4")

        self.advancedOptions_groupBoxButton = MMKitDialog.getGroupBoxTitleButton("Advanced Options", 
                                                                                 self.advancedOptions_groupBox)
        
        self.vboxlayout_grpbox4.addWidget(self.advancedOptions_groupBoxButton)

        self.autobondCB = QtGui.QCheckBox("Autobond", self.advancedOptions_groupBox )
        self.autobondCB.setChecked(env.prefs[buildModeAutobondEnabled_prefs_key])
        self.vboxlayout_grpbox4.addWidget(self.autobondCB)
        
        self.highlightingCB = QtGui.QCheckBox("Highlighting", self.advancedOptions_groupBox )
        self.highlightingCB.setChecked(env.prefs[buildModeHighlightingEnabled_prefs_key])
        self.vboxlayout_grpbox4.addWidget(self.highlightingCB)
        
        self.waterCB = QtGui.QCheckBox("Water", self.advancedOptions_groupBox )
        self.waterCB.setChecked(env.prefs[buildModeWaterEnabled_prefs_key])
        self.vboxlayout_grpbox4.addWidget(self.waterCB)
        
        #End Advanced Options GroupBox
        self.vboxlayout.addWidget(self.advancedOptions_groupBox)
	
	# Height is fixed. Mark 2007-05-29.
	self.advancedOptions_groupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))

    def retranslateUi(self, MMKitDialog):
        MMKitDialog.setWindowTitle(QtGui.QApplication.translate("MMKitDialog", 
                                                                "MMKit", None, QtGui.QApplication.UnicodeUTF8))
        MMKitDialog.setWindowIcon(QtGui.QIcon("ui/border/MMKit"))
	
        MMKitDialog.setToolTip(QtGui.QApplication.translate(
	    "MMKitDialog","Molecular Modeling Kit", 
	    None, QtGui.QApplication.UnicodeUTF8))
	
        self.heading_label.setText(QtGui.QApplication.translate(
	    "MMKitDialog", "<font color=\"#FFFFFF\">Build Atoms </font>",
	    None, QtGui.QApplication.UnicodeUTF8))
	
        self.elementFrame.setToolTip(QtGui.QApplication.translate("MMKitDialog", "3D thumbnail view", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton1.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Hydrogen", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton1.setText(QtGui.QApplication.translate("MMKitDialog", "H", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton1.setShortcut(QtGui.QApplication.translate("MMKitDialog", "H", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton2.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Helium", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton2.setText(QtGui.QApplication.translate("MMKitDialog", "He", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton6.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Carbon", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton6.setText(QtGui.QApplication.translate("MMKitDialog", "C", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton6.setShortcut(QtGui.QApplication.translate("MMKitDialog", "C", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton7.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Nitrogen", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton7.setText(QtGui.QApplication.translate("MMKitDialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton7.setShortcut(QtGui.QApplication.translate("MMKitDialog", "N", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton8.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Oxygen", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton8.setText(QtGui.QApplication.translate("MMKitDialog", "O", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton8.setShortcut(QtGui.QApplication.translate("MMKitDialog", "O", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton10.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Neon", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton10.setText(QtGui.QApplication.translate("MMKitDialog", "Ne", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton9.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Fluorine", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton9.setText(QtGui.QApplication.translate("MMKitDialog", "F", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton9.setShortcut(QtGui.QApplication.translate("MMKitDialog", "F", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton13.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Aluminum", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton13.setText(QtGui.QApplication.translate("MMKitDialog", "Al", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton13.setShortcut(QtGui.QApplication.translate("MMKitDialog", "A", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton17.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Chlorine", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton17.setText(QtGui.QApplication.translate("MMKitDialog", "Cl", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton17.setShortcut(QtGui.QApplication.translate("MMKitDialog", "L", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton5.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Boron", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton5.setText(QtGui.QApplication.translate("MMKitDialog", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton5.setShortcut(QtGui.QApplication.translate("MMKitDialog", "B", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton10_2.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Argon", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton10_2.setText(QtGui.QApplication.translate("MMKitDialog", "Ar", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton15.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Phosphorus", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton15.setText(QtGui.QApplication.translate("MMKitDialog", "P", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton15.setShortcut(QtGui.QApplication.translate("MMKitDialog", "P", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton16.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Sulfur", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton16.setText(QtGui.QApplication.translate("MMKitDialog", "S", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton16.setShortcut(QtGui.QApplication.translate("MMKitDialog", "S", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton14.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Silicon", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton14.setText(QtGui.QApplication.translate("MMKitDialog", "Si", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton14.setShortcut(QtGui.QApplication.translate("MMKitDialog", "Q", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton33.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Arsenic", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton33.setText(QtGui.QApplication.translate("MMKitDialog", "As", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton34.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Selenium", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton34.setText(QtGui.QApplication.translate("MMKitDialog", "Se", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton35.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Bromine", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton35.setText(QtGui.QApplication.translate("MMKitDialog", "Br", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton32.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Germanium", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton32.setText(QtGui.QApplication.translate("MMKitDialog", "Ge", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton36.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Krypton", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton36.setText(QtGui.QApplication.translate("MMKitDialog", "Kr", None, QtGui.QApplication.UnicodeUTF8))
        self.sp3_btn.setToolTip(QtGui.QApplication.translate("MMKitDialog", "sp3", None, QtGui.QApplication.UnicodeUTF8))
        self.sp3_btn.setShortcut(QtGui.QApplication.translate("MMKitDialog", "3", None, QtGui.QApplication.UnicodeUTF8))
        self.sp2_btn.setToolTip(QtGui.QApplication.translate("MMKitDialog", "sp2", None, QtGui.QApplication.UnicodeUTF8))
        self.sp2_btn.setShortcut(QtGui.QApplication.translate("MMKitDialog", "2", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_btn.setToolTip(QtGui.QApplication.translate("MMKitDialog", "sp", None, QtGui.QApplication.UnicodeUTF8))
        self.sp_btn.setShortcut(QtGui.QApplication.translate("MMKitDialog", "1", None, QtGui.QApplication.UnicodeUTF8))
        self.graphitic_btn.setToolTip(QtGui.QApplication.translate("MMKitDialog", "Graphitic", None, QtGui.QApplication.UnicodeUTF8))
        self.graphitic_btn.setShortcut(QtGui.QApplication.translate("MMKitDialog", "4", None, QtGui.QApplication.UnicodeUTF8))
        self.mmkit_tab.setTabText(self.mmkit_tab.indexOf(self.atomsPage), QtGui.QApplication.translate("MMKitDialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.mmkit_tab.setTabText(self.mmkit_tab.indexOf(self.clipboardPage), QtGui.QApplication.translate("MMKitDialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.mmkit_tab.setTabText(self.mmkit_tab.indexOf(self.libraryPage), QtGui.QApplication.translate("MMKitDialog", "", None, QtGui.QApplication.UnicodeUTF8))
        self.selectionFilter_label.setText(QtGui.QApplication.translate("selectionFilter_groupBox", 
                                                                        "Apply Filter To:", 
                                                                        None, QtGui.QApplication.UnicodeUTF8))
       
        self.browseButton.setToolTip(QtGui.QApplication.translate(
	    "MMKitDialog",
	    "Open file chooser dialog to select a new directory.",
	    None, QtGui.QApplication.UnicodeUTF8))
	
        self.browseButton.setText(QtGui.QApplication.translate(
	    "MMKitDialog", "Browse...",None, QtGui.QApplication.UnicodeUTF8))
	
	self.defaultPartLibButton.setText(QtGui.QApplication.translate(
	    "MMKitDialog", "Default Dir", None, QtGui.QApplication.UnicodeUTF8))
	
	self.defaultPartLibButton.setToolTip(QtGui.QApplication.translate(
	    "MMKitDialog", "Reset the partlib directory path to program default", 
	    None, QtGui.QApplication.UnicodeUTF8))
  
