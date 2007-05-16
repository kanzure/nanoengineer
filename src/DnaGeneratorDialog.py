# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$

Created by Will

Ninad (Nov2006 and later): Ported it to Property manager 
with further enhancements

Mark 2007-05-14: Organized code, added docstrings and renamed variables to make
 code more readable and understandable.

"""

import sys
from PyQt4 import Qt, QtCore, QtGui
from Utility import geticon, getpixmap
from PyQt4.Qt import *

class Ui_dna_dialog(object):
    def setupUi(self, dna_dialog):
        dna_dialog.setObjectName("dna_dialog")
        
        # NOTE: This establishes the width and height of the
        # Property Manager "container" (i.e. dna_dialog). 
        # Height of 600 needs to be tested on a 1024 x 768 monitor.
        # The height should auto-adjust to fit contents, but
        # doesn't as of now. Needs to be fixed. Mark 2007-05-14.
        # PropMgr width (230 pixels) should be set via global constant. 
	# The width is currently set in MWsemantics.py (PartWindow).
	# The width of dna_dialog is 230 - (4 x 2) = 222 pixels on Windows.
	# Need to test width on MacOS.
        # Mark 2007-05-15.
	
	layout = dna_dialog.layout() # Test.
	
	#print "layout =", layout.objectName()
	
        dna_dialog.resize(QtCore.QSize(
            QtCore.QRect(0,0,222,550).size()).expandedTo(
                dna_dialog.minimumSizeHint()))
        
        # Test code. Mark 2007-05-15.
        #dna_dialog.setMinimumWidth(230)
	#dna_dialog.setMaximumWidth(290)
	#dna_dialog.setMaximumHeight(600)
	
	#dna_dialog.setSizePolicy(
        #    QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(QSizePolicy.MinimumExpanding),
        #                      QtGui.QSizePolicy.Policy(QSizePolicy.MinimumExpanding)))
        
        # Main pallete for PropMgr.
        propmgr_palette = dna_dialog.getPropertyManagerPalette()
        dna_dialog.setPalette(propmgr_palette)

        # Main vertical layout for PropMgr.
        self.pmMainVboxLO = QtGui.QVBoxLayout(dna_dialog)
        self.pmMainVboxLO.setMargin(0)
        self.pmMainVboxLO.setSpacing(0)
        self.pmMainVboxLO.setObjectName("pmMainVboxLO")

        # PropMgr's Header.
        self.pmCreate_Header(dna_dialog)
        self.pmMainVboxLO.addWidget(self.heading_frame)

        # PropMgr's Sponsor button.
        self.pmCreate_SponsorButton(dna_dialog)
        self.pmMainVboxLO.addWidget(self.sponsor_frame)
        
        # PropMgr's top buttons row.
        self.pmCreate_TopBtnsRow(dna_dialog) # Create top buttons row
        self.pmMainVboxLO.addLayout(self.pmTopBtnsRow) # Add top buttons row to pmgr.
        
        # Spacer used between groupboxes
        pmGBSpacer = QtGui.QSpacerItem(10,5,
                            QtGui.QSizePolicy.Expanding,
                            QtGui.QSizePolicy.Minimum)
        
        # Message groupbox
        self.pmCreate_MsgGroupBox(dna_dialog) # Create groupbox
        self.pmMainVboxLO.addWidget(self.pmMsgGroupBox) # Add groupbox
        
        self.pmMainVboxLO.addItem(pmGBSpacer) # Add spacer
        
        # Groupbox1
        self.pmCreate_GroupBox1(dna_dialog) # Create groupbox
        self.pmMainVboxLO.addWidget(self.pmGroupBox1) # Add groupbox
        
        self.pmMainVboxLO.addItem(pmGBSpacer) # Add spacer
        
        # Groupbox2
        self.pmCreate_GroupBox2(dna_dialog) # Create groupbox
        self.pmMainVboxLO.addWidget(self.pmGroupBox2) # Add groupbox
        
        self.pmMainVboxLO.addItem(pmGBSpacer) # Add spacer
        
        # Groupbox3
        self.pmCreate_GroupBox3(dna_dialog) # Create groupbox
        self.pmMainVboxLO.addWidget(self.pmGroupBox3) # Add groupbox
        
        # Add spacer at the very bottom of the PropMgr. 
        # It is needed to assist proper collasping/expanding of groupboxes.
        pmBottomSpacer = QtGui.QSpacerItem(20,40,
                                           QtGui.QSizePolicy.Minimum,
                                           QtGui.QSizePolicy.Expanding)
        self.pmMainVboxLO.addItem(pmBottomSpacer) # Add spacer to bottom

        self.retranslateUi(dna_dialog) # ???
        QtCore.QMetaObject.connectSlotsByName(dna_dialog) # ???
        
    def pmCreate_Header(self, dna_dialog):
        """Creates the Property Manager header, which contains
        a pixmap and white text label.
        """
        
        # Heading frame (dark gray), which contains 
        # a pixmap and (white) heading text.
        self.heading_frame = QtGui.QFrame(dna_dialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")
        
        heading_palette = dna_dialog.getPropMgrHeadingPalette()
        self.heading_frame.setPalette(heading_palette)
        self.heading_frame.setAutoFillBackground(True)

        # HBox layout for heading frame, containing the pixmap
        # and label (title).
        self.pmHboxLO1 = QtGui.QHBoxLayout(self.heading_frame)
        self.pmHboxLO1.setMargin(2) # 2 pixels around edges.
        self.pmHboxLO1.setSpacing(5) # 5 pixel between pixmap and label.
        self.pmHboxLO1.setObjectName("pmHboxLO1")

        # PropMgr heading pixmap
        self.heading_pixmap = QtGui.QLabel(self.heading_frame)
        self.heading_pixmap.setObjectName("heading_pixmap")
        self.heading_pixmap.setPixmap(getpixmap(
            'ui/actions/Tools/Build Structures/DNA.png'))
        self.heading_pixmap.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(QSizePolicy.Fixed),
                              QtGui.QSizePolicy.Policy(QSizePolicy.Fixed)))
            
        self.heading_pixmap.setScaledContents(True)
        
        self.pmHboxLO1.addWidget(self.heading_pixmap)
        
        # PropMgr heading label (DNA)
        self.heading_label = QtGui.QLabel(self.heading_frame)
        self.heading_label.setObjectName("heading_label")

        # PropMgr heading font (for label). 
        # Color (white) and text string set in retranslateUi(). Why?
        font = QtGui.QFont(self.heading_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.heading_label.setFont(font)
        
        self.pmHboxLO1.addWidget(self.heading_label)
        
    def pmCreate_SponsorButton(self, dna_dialog):
        """Creates the Property Manager sponsor button, which contains
        a QPushButton inside of a QGridLayout inside of a QFrame.
        """
        
        # Sponsor button (inside a frame)
        self.sponsor_frame = QtGui.QFrame(dna_dialog)
        self.sponsor_frame.setObjectName("sponsor_frame")
        self.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)

        self.pmGridLO1 = QtGui.QGridLayout(self.sponsor_frame)
        self.pmGridLO1.setMargin(0)
        self.pmGridLO1.setSpacing(0)
        self.pmGridLO1.setObjectName("pmGridLO1")

        self.sponsor_btn = QtGui.QPushButton(self.sponsor_frame)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        
        self.pmGridLO1.addWidget(self.sponsor_btn,0,0,1,1)

    def pmCreate_TopBtnsRow(self, dna_dialog):
        """Creates the OK, Cancel, Preview, What's This 
        buttons row at the top of the Pmgr.
        """
        
        # The Top Buttons Row includes the following widgets:
        #
        # - self.pmTopBtnsRow (Hbox Layout containing everything:)
        #   - left spacer (10x10)
        #   - frame
        #     - hbox layout "frameHboxLO" (margin=2, spacing=2)
        #     - Done (OK) button
        #     - Abort (Cancel) button
        #     - Preview button
        #     - What's This button
        #   - right spacer (10x10)
        
        # This should be made into a class since all PropMgrs need it.
        # A method(s) should hide/show individual buttons. 
        
        # Main widget
        self.pmTopBtnsRow = QtGui.QHBoxLayout()
        
        # Left and right spacers
        leftSpacer = QtGui.QSpacerItem(10, 10, 
                                       QtGui.QSizePolicy.Expanding, 
                                       QSizePolicy.Minimum)
        rightSpacer = QtGui.QSpacerItem(10, 10, 
                                        QtGui.QSizePolicy.Expanding,
                                        QSizePolicy.Minimum)
        
        # Frame containing all the buttons.
        self.topBtnsRowFrame = QtGui.QFrame(dna_dialog)
        self.topBtnsRowFrame.setObjectName("topBtnsRowFrame")
                
        self.topBtnsRowFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.topBtnsRowFrame.setFrameShadow(QtGui.QFrame.Raised)
        
        # Create Hbox layout for main frame.
        self.frameHboxLO = QtGui.QHBoxLayout(self.topBtnsRowFrame)
        self.frameHboxLO.setMargin(2)
        self.frameHboxLO.setSpacing(2)
        self.frameHboxLO.setObjectName("frameHboxLO")
        
        # OK (Done) button.
        self.done_btn = QtGui.QPushButton(self.topBtnsRowFrame)
        self.done_btn.setObjectName("done_btn")
        self.done_btn.setIcon(geticon("ui/actions/Properties Manager/Done.png"))
        
        self.frameHboxLO.addWidget(self.done_btn)
        
        # Cancel (Abort) button.
        self.abort_btn = QtGui.QPushButton(self.topBtnsRowFrame)
        self.abort_btn.setObjectName("abort_btn")
        self.abort_btn.setIcon(geticon("ui/actions/Properties Manager/Abort.png"))
        
        self.frameHboxLO.addWidget(self.abort_btn)
        
        # Preview (glasses) button.
        self.preview_btn = QtGui.QPushButton(self.topBtnsRowFrame)
        self.preview_btn.setObjectName("preview_btn")
        self.preview_btn.setIcon(geticon("ui/actions/Properties Manager/Preview.png"))
        
        self.frameHboxLO.addWidget(self.preview_btn)        
        
        # What's This (?) button.
        self.whatsthis_btn = QtGui.QPushButton(self.topBtnsRowFrame)
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.whatsthis_btn.setIcon(geticon("ui/actions/Properties Manager/WhatsThis.png"))
        
        self.frameHboxLO.addWidget(self.whatsthis_btn)
        
        # Create Button Row
        self.pmTopBtnsRow.addItem(leftSpacer)
        self.pmTopBtnsRow.addWidget(self.topBtnsRowFrame)
        self.pmTopBtnsRow.addItem(rightSpacer)
            
    def pmCreate_MsgGroupBox(self, dna_dialog):
        """Creates layout and widgets for the "Message" groupbox.
        """
        self.pmMsgGroupBox = QtGui.QGroupBox(dna_dialog)
        self.pmMsgGroupBox.setObjectName("pmMsgGroupBox")
        
        self.pmMsgGroupBox.setAutoFillBackground(True) 
        palette =  dna_dialog.getGroupBoxPalette()
        self.pmMsgGroupBox.setPalette(palette)
        
        styleSheet = dna_dialog.getGroupBoxStyleSheet()        
        self.pmMsgGroupBox.setStyleSheet(styleSheet)

        self.pmMsgVboxLO = QtGui.QVBoxLayout(self.pmMsgGroupBox)
        self.pmMsgVboxLO.setMargin(0)
        self.pmMsgVboxLO.setSpacing(0)
        self.pmMsgVboxLO.setObjectName("pmMsgVboxLO")
        
        # "Message" title button for pmMsgGroupBox
        
        self.pmMsgGroupBoxBtn = dna_dialog.getGroupBoxTitleButton(
            "Message", self.pmMsgGroupBox)
        
        self.pmMsgVboxLO.addWidget(self.pmMsgGroupBoxBtn)
        
        # "Message" TextEdit

        self.pmMsgTextEdit = QtGui.QTextEdit(self.pmMsgGroupBox)
        self.pmMsgTextEdit.setObjectName("pmMsgTextEdit")
        self.pmMsgTextEdit.setMinimumSize(200,46)
	self.pmMsgTextEdit.setMaximumSize(300,60)
        self.pmMsgTextEdit.setSizePolicy(QSizePolicy.MinimumExpanding,
					 QSizePolicy.Minimum )
        self.pmMsgTextEdit.setReadOnly(True)
	msg = "Edit the DNA parameters and select <b>Preview</b> to preview the structure. \
	Click <b>Done</b> to insert it into the model."
	
	# Preview button image.
	# <img source=\"ui/actions/Properties Manager/Preview.png\"><br> \ 
	
        self.pmMsgTextEdit.insertHtml(msg)
        
        msg_palette =  dna_dialog.getMsgGroupBoxPalette()
        self.pmMsgTextEdit.setPalette(msg_palette)
        
        self.pmMsgVboxLO.addWidget(self.pmMsgTextEdit)
        
    def pmCreate_GroupBox1(self, dna_dialog):
        """Creates layout and widgets for the "DNA Parameters" groupbox.
        """
        
        self.pmGroupBox1 = QtGui.QGroupBox(dna_dialog)
        self.pmGroupBox1.setObjectName("pmGroupBox1")
        
        self.pmGroupBox1.setAutoFillBackground(True) 
        palette =  dna_dialog.getGroupBoxPalette()
        self.pmGroupBox1.setPalette(palette)
        
        styleSheet = dna_dialog.getGroupBoxStyleSheet()        
        self.pmGroupBox1.setStyleSheet(styleSheet)
        
        self.pmGB1MainVboxLO = QtGui.QVBoxLayout(self.pmGroupBox1)
        self.pmGB1MainVboxLO.setMargin(0)
        self.pmGB1MainVboxLO.setSpacing(6)
        self.pmGB1MainVboxLO.setObjectName("pmGB1MainVboxLO")

        # Title button for groupbox1
        
        self.pmGroupBoxBtn1 = dna_dialog.getGroupBoxTitleButton(
            "DNA Parameters", self.pmGroupBox1)
        
        self.pmGB1MainVboxLO.addWidget(self.pmGroupBoxBtn1)
   
        self.pmGB1GridLO1 = QtGui.QGridLayout()
        self.pmGB1GridLO1.setMargin(0)
        self.pmGB1GridLO1.setSpacing(6)
        self.pmGB1GridLO1.setObjectName("pmGB1GridLO1")
        
        # "Conformation" label and combobox.
        
        self.dnaConformation_lbl = QtGui.QLabel(self.pmGroupBox1)
        self.dnaConformation_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.dnaConformation_lbl.setObjectName("dnaConformation_lbl")
        self.pmGB1GridLO1.addWidget(self.dnaConformation_lbl,0,0,1,1)

        self.dnaConformation_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.dnaConformation_combox.setObjectName("dnaConformation_combox")
        self.pmGB1GridLO1.addWidget(self.dnaConformation_combox,0,1,1,1)
        
        # "Strand Type" label and combobox.

        self.strandType_lbl = QtGui.QLabel(self.pmGroupBox1)
        self.strandType_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.strandType_lbl.setObjectName("strandType_lbl")
        self.pmGB1GridLO1.addWidget(self.strandType_lbl,5,0,1,1)

        self.strandType_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.strandType_combox.setObjectName("strandType_combox")
        self.pmGB1GridLO1.addWidget(self.strandType_combox,5,1,1,1)
        
        # "Bases Per Turn" label and combobox.

        self.basesPerTurn_lbl = QLabel()
        self.basesPerTurn_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.pmGB1GridLO1.addWidget(self.basesPerTurn_lbl, 10,0,1,1,)
                
        self.basesPerTurn_combox = QtGui.QComboBox(self.pmGroupBox1)
        self.basesPerTurn_combox.insertItem(0, "10.0")
        self.basesPerTurn_combox.insertItem(1, "10.5")
        self.basesPerTurn_combox.insertItem(2, "10.67")
        self.pmGB1GridLO1.addWidget(self.basesPerTurn_combox, 10,1,1,1,)
        
        #10.5 is the default value for Bases per turn. 
        #So set the current index to 1
        self.basesPerTurn_combox.setCurrentIndex(1) 
        
        self.pmGB1MainVboxLO.addLayout(self.pmGB1GridLO1)
        
    
    def pmCreate_GroupBox2(self, dna_dialog):
        """Creates layout and widgets for the "Representation" groupbox.
        """
        
        self.pmGroupBox2 = QtGui.QGroupBox(dna_dialog)
        self.pmGroupBox2.setObjectName("pmGroupBox2")
        
        self.pmGroupBox2.setAutoFillBackground(True) 
        palette =  dna_dialog.getGroupBoxPalette()
        self.pmGroupBox2.setPalette(palette)
        
        styleSheet = dna_dialog.getGroupBoxStyleSheet()        
        self.pmGroupBox2.setStyleSheet(styleSheet)
        
        self.pmGB2MainVboxLO = QtGui.QVBoxLayout(self.pmGroupBox2)
        self.pmGB2MainVboxLO.setMargin(0)
        self.pmGB2MainVboxLO.setSpacing(6)  
        
        # "Representation" title button for groupbox3
        
        self.pmGroupBoxBtn2 = dna_dialog.getGroupBoxTitleButton(
            "Representation", self.pmGroupBox2)
        
        self.pmGB2MainVboxLO.addWidget(self.pmGroupBoxBtn2)
                
        pmGB2HboxLO1 = QtGui.QHBoxLayout()
        pmGB2HboxLO1.setMargin(0)
        pmGB2HboxLO1.setSpacing(6)
        
        # "Model" label and combobox.
        
        self.model_combox_lbl = QLabel() # "Model :" label, defined in another file. mark 2007-05-09.
        self.model_combox_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        pmGB2HboxLO1.addWidget(self.model_combox_lbl)
                
        self.model_combox = QtGui.QComboBox(self.pmGroupBox2)
        self.model_combox.insertItem(1, "Reduced")
        self.model_combox.insertItem(2, "Atomistic")
        
        pmGB2HboxLO1.addWidget(self.model_combox)
                
        self.pmGB2MainVboxLO.addLayout(pmGB2HboxLO1)
        
        hlo_chunkOp = QtGui.QHBoxLayout()
        hlo_chunkOp.setMargin(0)
        hlo_chunkOp.setSpacing(2)
        
        # "Create" label and combobox.
        
        self.dnaChunkOptions_lbl = QtGui.QLabel(self.pmGroupBox2)
        self.dnaChunkOptions_lbl.setText("Create :")
        self.dnaChunkOptions_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        hlo_chunkOp.addWidget(self.dnaChunkOptions_lbl)
        
        self.dnaChunkOptions_combox = QtGui.QComboBox(self.pmGroupBox2)
        self.dnaChunkOptions_combox.addItem("DNA Chunk")
        self.dnaChunkOptions_combox.addItem("Strand Chunks")  
        self.dnaChunkOptions_combox.addItem("Base-Pair Chunks")   
                
        hlo_chunkOp.addWidget(self.dnaChunkOptions_combox)
        
        self.pmGB2MainVboxLO.addLayout(hlo_chunkOp)
                
    
    def pmCreate_GroupBox3(self, dna_dialog):
        """Creates layout and widgets for the "Strand Sequence" groupbox.
        """
        
        self.pmGroupBox3 = QtGui.QGroupBox(dna_dialog)
        self.pmGroupBox3.setObjectName("pmGroupBox3")
        
        self.pmGroupBox3.setAutoFillBackground(True) 
        palette =  dna_dialog.getGroupBoxPalette()
        self.pmGroupBox3.setPalette(palette)
        
        styleSheet = dna_dialog.getGroupBoxStyleSheet()        
        self.pmGroupBox3.setStyleSheet(styleSheet)

        self.pmGB3MainVboxLO = QtGui.QVBoxLayout(self.pmGroupBox3)
        self.pmGB3MainVboxLO.setMargin(0)
        self.pmGB3MainVboxLO.setSpacing(4)
        self.pmGB3MainVboxLO.setObjectName("pmGB3MainVboxLO")
        
        # "Strand Sequence" title button for groupbox3
        
        self.pmGroupBoxBtn3 = dna_dialog.getGroupBoxTitleButton(
            "Strand Sequence", self.pmGroupBox3)
        
        self.pmGB3MainVboxLO.addWidget(self.pmGroupBoxBtn3)
        
        # "Total Length" Label and ComboBox
        
        self.pmGB3HboxLO1 = QtGui.QHBoxLayout()
        self.pmGB3HboxLO1.setMargin(0)
        self.pmGB3HboxLO1.setSpacing(6)
        self.pmGB3HboxLO1.setObjectName("pmGB3HboxLO1")
        
        self.length_lbl = QtGui.QLabel(self.pmGroupBox3)
        self.length_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.pmGB3HboxLO1.addWidget(self.length_lbl)
        
        self.length_spinbox = QtGui.QSpinBox(self.pmGroupBox3)
        self.length_spinbox.setMinimum(0)
        self.length_spinbox.setMaximum(10000)
        self.length_spinbox.setValue(0)
        self.length_spinbox.setSuffix(" bases")
        self.pmGB3HboxLO1.addWidget(self.length_spinbox)
        
        self.pmGB3MainVboxLO.addLayout(self.pmGB3HboxLO1)
        
        # "New Bases Are" Label and ComboBox
        
        self.pmGB3HboxLO2 = QtGui.QHBoxLayout()
        self.pmGB3HboxLO2.setMargin(0)
        self.pmGB3HboxLO2.setSpacing(6)
        self.pmGB3HboxLO2.setObjectName("pmGB3HboxLO2")
        
        self.newBaseOptions_lbl = QtGui.QLabel(self.pmGroupBox3)
        self.newBaseOptions_lbl.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.pmGB3HboxLO2.addWidget(self.newBaseOptions_lbl)
        
        self.newBaseOptions_combox = QtGui.QComboBox(self.pmGroupBox3)
        self.newBaseOptions_combox.addItem("N (undefined)")
        self.newBaseOptions_combox.addItem("A")
        self.newBaseOptions_combox.addItem("T")  
        self.newBaseOptions_combox.addItem("C")
        self.newBaseOptions_combox.addItem("G")
        self.pmGB3HboxLO2.addWidget(self.newBaseOptions_combox)
        
        self.pmGB3MainVboxLO.addLayout(self.pmGB3HboxLO2)
        
        # "Base sequence" TextEdit

        self.base_textedit = QtGui.QTextEdit(self.pmGroupBox3)
        self.base_textedit.setObjectName("base_textedit")
        self.base_textedit.setMinimumSize(200,70)
        self.base_textedit.setSizePolicy ( QSizePolicy.MinimumExpanding, QSizePolicy.Minimum )
        self.pmGB3MainVboxLO.addWidget(self.base_textedit)
        
        # "Complementary" and "Reverse" buttons

        self.pmGB3HboxLO3 = QtGui.QHBoxLayout()
        self.pmGB3HboxLO3.setMargin(0)
        self.pmGB3HboxLO3.setSpacing(6)
        self.pmGB3HboxLO3.setObjectName("pmGB3HboxLO3")

        self.complement_btn = QtGui.QPushButton(self.pmGroupBox3)
        self.complement_btn.setAutoDefault(False)
        self.complement_btn.setObjectName("complement_btn")
        self.pmGB3HboxLO3.addWidget(self.complement_btn)

        self.reverse_btn = QtGui.QPushButton(self.pmGroupBox3)
        self.reverse_btn.setAutoDefault(False)
        self.reverse_btn.setObjectName("reverse_btn")
        self.pmGB3HboxLO3.addWidget(self.reverse_btn)
        self.pmGB3MainVboxLO.addLayout(self.pmGB3HboxLO3)      
        

    def retranslateUi(self, dna_dialog):
        dna_dialog.setWindowTitle(
            QtGui.QApplication.translate("dna_dialog", 
                                         "DNA", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        dna_dialog.setWindowIcon(QtGui.QIcon("ui/border/Dna"))
                
        self.heading_label.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "<font color=\"#FFFFFF\">DNA </font>", 
                                         None,
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.done_btn.setToolTip(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Done", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.abort_btn.setToolTip(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Cancel", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.preview_btn.setToolTip(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Preview",
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.whatsthis_btn.setToolTip(
            QtGui.QApplication.translate("dna_dialog", 
                                         "What\'s This Help", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.dnaConformation_combox.addItem(
            QtGui.QApplication.translate("dna_dialog", 
                                         "B-DNA", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.strandType_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Strand Type :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.strandType_combox.addItem(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Double", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.dnaConformation_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Conformation :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.basesPerTurn_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Bases Per Turn :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.model_combox_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Model :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.length_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "Total Length :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.newBaseOptions_lbl.setText(
            QtGui.QApplication.translate("dna_dialog", 
                                         "New Bases Are :", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))
        
        self.complement_btn.setText(
            QtGui.QApplication.translate("dna_dialog",
                                         "Complement", 
                                         None,
                                         QtGui.QApplication.UnicodeUTF8))
        self.reverse_btn.setText(
            QtGui.QApplication.translate("dna_dialog",
                                         "Reverse", 
                                         None, 
                                         QtGui.QApplication.UnicodeUTF8))

