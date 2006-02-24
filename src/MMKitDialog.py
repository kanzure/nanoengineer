# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MMKitDialog.ui'
#
# Created: Fri Feb 24 03:27:28 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xd7\x49\x44\x41\x54\x78\x9c\xe5\x93\x31\x8a\x02" \
    "\x41\x10\x45\xdf\x18\x9b\x19\x4d\xe4\x09\xfe\x69" \
    "\xfa\x08\xe6\x86\x66\xca\x44\x66\x5e\xc0\xc0\x44" \
    "\x33\x6f\xe0\x01\xb4\x93\xa1\x15\x41\x0c\x84\x49" \
    "\x3c\xc1\x80\xf1\x37\x18\x58\x56\xcc\x96\x16\x76" \
    "\xd9\x17\x16\xd4\xaf\xcf\x83\x82\xcc\x14\x3f\x59" \
    "\x92\xe4\xac\x2d\x24\x99\xf6\x6c\xda\xb3\x25\xf9" \
    "\x74\x78\xf8\x74\x78\x58\x92\x7b\x59\x2f\x01\xd9" \
    "\x03\x0b\xc8\xeb\xe4\xab\xe1\x60\x94\x18\x8c\x12" \
    "\x00\xd7\xd9\x9d\xeb\xec\x0e\xc0\x7e\x1e\xd9\xcf" \
    "\x23\x00\xab\xe6\xc2\xaa\xb9\x00\xd0\x3f\x4e\xe8" \
    "\x1f\x27\x00\x6c\x96\x91\xcd\x32\xbe\x06\x66\x6f" \
    "\x98\x8b\xcf\x39\x9c\x8e\x23\xd3\x71\xe7\x21\x84" \
    "\x40\x08\x01\x80\xaa\x4c\x54\x65\xe7\x36\x6d\x4b" \
    "\xd2\xb6\xec\xe6\xb5\xa8\x6a\x01\xff\xde\xe1\x1b" \
    "\x92\xdc\xdc\x0a\x37\xb7\xc2\x92\x5c\xd3\xba\xa6" \
    "\xb5\x24\x7b\x3d\xb4\xd7\xc3\xee\x67\x77\x0b\xf7" \
    "\x76\x8b\xbf\xfa\xcb\xdf\xf9\xa8\xcf\x5f\xc1\x13" \
    "\xdd\x30\x66\xf2\xaf\x98\x1f\x6d\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"

class MMKitDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MMKitDialog")

        self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setMinimumSize(QSize(180,400))
        pal = QPalette()
        cg = QColorGroup()
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,QColor(242,243,242))
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,Qt.black)
        cg.setColor(QColorGroup.LinkVisited,Qt.black)
        pal.setActive(cg)
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,Qt.white)
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setInactive(cg)
        cg.setColor(QColorGroup.Foreground,QColor(128,128,128))
        cg.setColor(QColorGroup.Button,QColor(230,231,230))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,Qt.white)
        cg.setColor(QColorGroup.Dark,QColor(115,115,115))
        cg.setColor(QColorGroup.Mid,QColor(153,154,153))
        cg.setColor(QColorGroup.Text,QColor(128,128,128))
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,QColor(128,128,128))
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(230,231,230))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setDisabled(cg)
        self.setPalette(pal)
        self.setIcon(self.image0)

        MMKitDialogLayout = QVBoxLayout(self,2,2,"MMKitDialogLayout")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,1,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(150,150))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        MMKitDialogLayout.addWidget(self.elementFrame)
        spacer4_2_3_2 = QSpacerItem(20,5,QSizePolicy.Minimum,QSizePolicy.Fixed)
        MMKitDialogLayout.addItem(spacer4_2_3_2)

        self.mmkit_tab = QTabWidget(self,"mmkit_tab")
        self.mmkit_tab.setEnabled(1)
        self.mmkit_tab.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.mmkit_tab.sizePolicy().hasHeightForWidth()))

        self.atomsPage = QWidget(self.mmkit_tab,"atomsPage")
        atomsPageLayout = QGridLayout(self.atomsPage,1,1,4,2,"atomsPageLayout")

        self.frame5 = QFrame(self.atomsPage,"frame5")
        self.frame5.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum,0,0,self.frame5.sizePolicy().hasHeightForWidth()))
        self.frame5.setFrameShape(QFrame.NoFrame)
        self.frame5.setFrameShadow(QFrame.Plain)
        frame5Layout = QGridLayout(self.frame5,1,1,2,2,"frame5Layout")

        self.elementButtonGroup = QButtonGroup(self.frame5,"elementButtonGroup")
        self.elementButtonGroup.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum,0,0,self.elementButtonGroup.sizePolicy().hasHeightForWidth()))
        self.elementButtonGroup.setMinimumSize(QSize(0,95))
        self.elementButtonGroup.setBackgroundOrigin(QButtonGroup.AncestorOrigin)
        self.elementButtonGroup.setFrameShape(QButtonGroup.NoFrame)
        self.elementButtonGroup.setFrameShadow(QButtonGroup.Plain)
        self.elementButtonGroup.setLineWidth(0)
        self.elementButtonGroup.setExclusive(1)
        self.elementButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.elementButtonGroup.layout().setSpacing(0)
        self.elementButtonGroup.layout().setMargin(0)
        elementButtonGroupLayout = QGridLayout(self.elementButtonGroup.layout())
        elementButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.toolButton1 = QToolButton(self.elementButtonGroup,"toolButton1")
        self.toolButton1.setMinimumSize(QSize(26,26))
        self.toolButton1.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton1,1)

        elementButtonGroupLayout.addWidget(self.toolButton1,0,4)

        self.toolButton2 = QToolButton(self.elementButtonGroup,"toolButton2")
        self.toolButton2.setMinimumSize(QSize(26,26))
        self.toolButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton2,2)

        elementButtonGroupLayout.addWidget(self.toolButton2,0,5)

        self.toolButton6 = QToolButton(self.elementButtonGroup,"toolButton6")
        self.toolButton6.setMinimumSize(QSize(26,26))
        self.toolButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton6,6)

        elementButtonGroupLayout.addWidget(self.toolButton6,1,1)

        self.toolButton7 = QToolButton(self.elementButtonGroup,"toolButton7")
        self.toolButton7.setMinimumSize(QSize(26,26))
        self.toolButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton7,7)

        elementButtonGroupLayout.addWidget(self.toolButton7,1,2)

        self.toolButton8 = QToolButton(self.elementButtonGroup,"toolButton8")
        self.toolButton8.setMinimumSize(QSize(26,26))
        self.toolButton8.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton8,8)

        elementButtonGroupLayout.addWidget(self.toolButton8,1,3)

        self.toolButton10 = QToolButton(self.elementButtonGroup,"toolButton10")
        self.toolButton10.setMinimumSize(QSize(26,26))
        self.toolButton10.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton10,10)

        elementButtonGroupLayout.addWidget(self.toolButton10,1,5)

        self.toolButton9 = QToolButton(self.elementButtonGroup,"toolButton9")
        self.toolButton9.setMinimumSize(QSize(26,26))
        self.toolButton9.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton9,9)

        elementButtonGroupLayout.addWidget(self.toolButton9,1,4)

        self.toolButton13 = QToolButton(self.elementButtonGroup,"toolButton13")
        self.toolButton13.setMinimumSize(QSize(26,26))
        self.toolButton13.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton13,13)

        elementButtonGroupLayout.addWidget(self.toolButton13,2,0)

        self.toolButton17 = QToolButton(self.elementButtonGroup,"toolButton17")
        self.toolButton17.setMinimumSize(QSize(26,26))
        self.toolButton17.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton17,17)

        elementButtonGroupLayout.addWidget(self.toolButton17,2,4)

        self.toolButton5 = QToolButton(self.elementButtonGroup,"toolButton5")
        self.toolButton5.setMinimumSize(QSize(26,26))
        self.toolButton5.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton5,5)

        elementButtonGroupLayout.addWidget(self.toolButton5,1,0)

        self.toolButton10_2 = QToolButton(self.elementButtonGroup,"toolButton10_2")
        self.toolButton10_2.setMinimumSize(QSize(26,26))
        self.toolButton10_2.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton10_2,18)

        elementButtonGroupLayout.addWidget(self.toolButton10_2,2,5)

        self.toolButton15 = QToolButton(self.elementButtonGroup,"toolButton15")
        self.toolButton15.setMinimumSize(QSize(26,26))
        self.toolButton15.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton15,15)

        elementButtonGroupLayout.addWidget(self.toolButton15,2,2)

        self.toolButton16 = QToolButton(self.elementButtonGroup,"toolButton16")
        self.toolButton16.setMinimumSize(QSize(26,26))
        self.toolButton16.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton16,16)

        elementButtonGroupLayout.addWidget(self.toolButton16,2,3)

        self.toolButton14 = QToolButton(self.elementButtonGroup,"toolButton14")
        self.toolButton14.setMinimumSize(QSize(26,26))
        self.toolButton14.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton14,14)

        elementButtonGroupLayout.addWidget(self.toolButton14,2,1)

        self.toolButton33 = QToolButton(self.elementButtonGroup,"toolButton33")
        self.toolButton33.setMinimumSize(QSize(26,26))
        self.toolButton33.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton33,33)

        elementButtonGroupLayout.addWidget(self.toolButton33,3,2)

        self.toolButton34 = QToolButton(self.elementButtonGroup,"toolButton34")
        self.toolButton34.setMinimumSize(QSize(26,26))
        self.toolButton34.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton34,34)

        elementButtonGroupLayout.addWidget(self.toolButton34,3,3)

        self.toolButton35 = QToolButton(self.elementButtonGroup,"toolButton35")
        self.toolButton35.setMinimumSize(QSize(26,26))
        self.toolButton35.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton35,35)

        elementButtonGroupLayout.addWidget(self.toolButton35,3,4)

        self.toolButton32 = QToolButton(self.elementButtonGroup,"toolButton32")
        self.toolButton32.setMinimumSize(QSize(26,26))
        self.toolButton32.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton32,32)

        elementButtonGroupLayout.addWidget(self.toolButton32,3,1)

        self.toolButton36 = QToolButton(self.elementButtonGroup,"toolButton36")
        self.toolButton36.setMinimumSize(QSize(26,26))
        self.toolButton36.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton36,36)

        elementButtonGroupLayout.addWidget(self.toolButton36,3,5)

        frame5Layout.addWidget(self.elementButtonGroup,0,0)

        atomsPageLayout.addWidget(self.frame5,0,0)
        spacer8 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        atomsPageLayout.addItem(spacer8,2,0)

        layout14 = QHBoxLayout(None,0,6,"layout14")

        self.hybrid_btngrp = QButtonGroup(self.atomsPage,"hybrid_btngrp")
        self.hybrid_btngrp.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Fixed,0,0,self.hybrid_btngrp.sizePolicy().hasHeightForWidth()))
        self.hybrid_btngrp.setFrameShape(QButtonGroup.NoFrame)
        self.hybrid_btngrp.setFrameShadow(QButtonGroup.Plain)
        self.hybrid_btngrp.setLineWidth(0)
        self.hybrid_btngrp.setExclusive(1)
        self.hybrid_btngrp.setColumnLayout(0,Qt.Vertical)
        self.hybrid_btngrp.layout().setSpacing(0)
        self.hybrid_btngrp.layout().setMargin(2)
        hybrid_btngrpLayout = QHBoxLayout(self.hybrid_btngrp.layout())
        hybrid_btngrpLayout.setAlignment(Qt.AlignTop)

        self.sp3_btn = QToolButton(self.hybrid_btngrp,"sp3_btn")
        self.sp3_btn.setMinimumSize(QSize(30,30))
        self.sp3_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.sp3_btn,0)
        hybrid_btngrpLayout.addWidget(self.sp3_btn)

        self.sp2_btn = QToolButton(self.hybrid_btngrp,"sp2_btn")
        self.sp2_btn.setMinimumSize(QSize(30,30))
        self.sp2_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.sp2_btn,1)
        hybrid_btngrpLayout.addWidget(self.sp2_btn)

        self.sp_btn = QToolButton(self.hybrid_btngrp,"sp_btn")
        self.sp_btn.setMinimumSize(QSize(30,30))
        self.sp_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.sp_btn,2)
        hybrid_btngrpLayout.addWidget(self.sp_btn)

        self.graphitic_btn = QToolButton(self.hybrid_btngrp,"graphitic_btn")
        self.graphitic_btn.setMinimumSize(QSize(30,30))
        self.graphitic_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.graphitic_btn,3)
        hybrid_btngrpLayout.addWidget(self.graphitic_btn)
        spacer19 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        hybrid_btngrpLayout.addItem(spacer19)
        layout14.addWidget(self.hybrid_btngrp)
        spacer18 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout14.addItem(spacer18)

        atomsPageLayout.addLayout(layout14,1,0)
        self.mmkit_tab.insertTab(self.atomsPage,QString.fromLatin1(""))

        self.clipboardPage = QWidget(self.mmkit_tab,"clipboardPage")
        clipboardPageLayout = QGridLayout(self.clipboardPage,1,1,4,2,"clipboardPageLayout")

        self.chunkListBox = QListBox(self.clipboardPage,"chunkListBox")
        self.chunkListBox.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.Minimum,0,2,self.chunkListBox.sizePolicy().hasHeightForWidth()))
        self.chunkListBox.setMinimumSize(QSize(100,100))
        self.chunkListBox.setVariableWidth(1)

        clipboardPageLayout.addWidget(self.chunkListBox,0,0)
        self.mmkit_tab.insertTab(self.clipboardPage,QString.fromLatin1(""))

        self.libraryPage = QWidget(self.mmkit_tab,"libraryPage")
        self.mmkit_tab.insertTab(self.libraryPage,QString.fromLatin1(""))
        MMKitDialogLayout.addWidget(self.mmkit_tab)
        spacer10 = QSpacerItem(20,5,QSizePolicy.Minimum,QSizePolicy.Expanding)
        MMKitDialogLayout.addItem(spacer10)

        layout4 = QHBoxLayout(None,0,0,"layout4")
        spacer4_2_3_3 = QSpacerItem(5,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
        layout4.addItem(spacer4_2_3_3)

        self.browseButton = QPushButton(self,"browseButton")
        self.browseButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.browseButton.sizePolicy().hasHeightForWidth()))
        self.browseButton.setDefault(1)
        layout4.addWidget(self.browseButton)

        self.closePTableButton = QPushButton(self,"closePTableButton")
        self.closePTableButton.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.closePTableButton.sizePolicy().hasHeightForWidth()))
        self.closePTableButton.setDefault(1)
        layout4.addWidget(self.closePTableButton)
        spacer4_2_3 = QSpacerItem(5,20,QSizePolicy.Fixed,QSizePolicy.Minimum)
        layout4.addItem(spacer4_2_3)
        MMKitDialogLayout.addLayout(layout4)

        self.languageChange()

        self.resize(QSize(180,400).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closePTableButton,SIGNAL("clicked()"),self.close)
        self.connect(self.hybrid_btngrp,SIGNAL("clicked(int)"),self.set_hybrid_type)
        self.connect(self.mmkit_tab,SIGNAL("currentChanged(QWidget*)"),self.setup_current_page)
        self.connect(self.chunkListBox,SIGNAL("selectionChanged(QListBoxItem*)"),self.chunkChanged)
        self.connect(self.browseButton,SIGNAL("clicked()"),self.browseDirectories)
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)



    def languageChange(self):
        self.setCaption(self.__tr("Modeling Kit"))
        QToolTip.add(self.elementFrame,self.__tr("3D thumbnail view"))
        QWhatsThis.add(self.elementFrame,self.__tr("3D thumbnail view"))
        self.elementButtonGroup.setTitle(QString.null)
        self.toolButton1.setText(self.__tr("H"))
        self.toolButton1.setAccel(self.__tr("H"))
        QToolTip.add(self.toolButton1,self.__tr("Hydrogen"))
        QWhatsThis.add(self.toolButton1,QString.null)
        self.toolButton2.setText(self.__tr("He"))
        self.toolButton2.setAccel(QString.null)
        QToolTip.add(self.toolButton2,self.__tr("Helium"))
        self.toolButton6.setText(self.__tr("C"))
        self.toolButton6.setAccel(self.__tr("C"))
        QToolTip.add(self.toolButton6,self.__tr("Carbon"))
        self.toolButton7.setText(self.__tr("N"))
        self.toolButton7.setAccel(self.__tr("N"))
        QToolTip.add(self.toolButton7,self.__tr("Nitrogen"))
        self.toolButton8.setText(self.__tr("O"))
        self.toolButton8.setAccel(self.__tr("O"))
        QToolTip.add(self.toolButton8,self.__tr("Oxygen"))
        self.toolButton10.setText(self.__tr("Ne"))
        self.toolButton10.setAccel(QString.null)
        QToolTip.add(self.toolButton10,self.__tr("Neon"))
        self.toolButton9.setText(self.__tr("F"))
        self.toolButton9.setAccel(self.__tr("F"))
        QToolTip.add(self.toolButton9,self.__tr("Fluorine"))
        self.toolButton13.setText(self.__tr("Al"))
        self.toolButton13.setAccel(self.__tr("A"))
        QToolTip.add(self.toolButton13,self.__tr("Aluminum"))
        self.toolButton17.setText(self.__tr("Cl"))
        self.toolButton17.setAccel(self.__tr("L"))
        QToolTip.add(self.toolButton17,self.__tr("Chlorine"))
        self.toolButton5.setText(self.__tr("B"))
        self.toolButton5.setAccel(self.__tr("B"))
        QToolTip.add(self.toolButton5,self.__tr("Boron"))
        self.toolButton10_2.setText(self.__tr("Ar"))
        self.toolButton10_2.setAccel(QString.null)
        QToolTip.add(self.toolButton10_2,self.__tr("Argon"))
        self.toolButton15.setText(self.__tr("P"))
        self.toolButton15.setAccel(self.__tr("P"))
        QToolTip.add(self.toolButton15,self.__tr("Phosphorus"))
        self.toolButton16.setText(self.__tr("S"))
        self.toolButton16.setAccel(self.__tr("S"))
        QToolTip.add(self.toolButton16,self.__tr("Sulfur"))
        self.toolButton14.setText(self.__tr("Si"))
        self.toolButton14.setAccel(self.__tr("Q"))
        QToolTip.add(self.toolButton14,self.__tr("Silicon"))
        self.toolButton33.setText(self.__tr("As"))
        QToolTip.add(self.toolButton33,self.__tr("Arsenic"))
        self.toolButton34.setText(self.__tr("Se"))
        QToolTip.add(self.toolButton34,self.__tr("Selenium"))
        self.toolButton35.setText(self.__tr("Br"))
        QToolTip.add(self.toolButton35,self.__tr("Bromine"))
        self.toolButton32.setText(self.__tr("Ge"))
        QToolTip.add(self.toolButton32,self.__tr("Germanium"))
        self.toolButton36.setText(self.__tr("Kr"))
        QToolTip.add(self.toolButton36,self.__tr("Krypton"))
        self.hybrid_btngrp.setTitle(QString.null)
        self.sp3_btn.setText(QString.null)
        self.sp3_btn.setAccel(self.__tr("3"))
        QToolTip.add(self.sp3_btn,self.__tr("sp3"))
        self.sp2_btn.setText(QString.null)
        self.sp2_btn.setAccel(self.__tr("2"))
        QToolTip.add(self.sp2_btn,self.__tr("sp2"))
        self.sp_btn.setText(QString.null)
        self.sp_btn.setAccel(self.__tr("1"))
        QToolTip.add(self.sp_btn,self.__tr("sp"))
        self.graphitic_btn.setText(QString.null)
        self.graphitic_btn.setAccel(self.__tr("4"))
        QToolTip.add(self.graphitic_btn,self.__tr("Graphitic"))
        self.mmkit_tab.changeTab(self.atomsPage,QString.null)
        self.mmkit_tab.changeTab(self.clipboardPage,QString.null)
        self.mmkit_tab.changeTab(self.libraryPage,QString.null)
        self.browseButton.setText(self.__tr("Browse..."))
        QToolTip.add(self.browseButton,self.__tr("Open file chooser dialog to select a new directory."))
        self.closePTableButton.setText(self.__tr("Close"))


    def setElementInfo(self,a0):
        print "MMKitDialog.setElementInfo(int): Not implemented yet"

    def set_hybrid_type(self,a0):
        print "MMKitDialog.set_hybrid_type(int): Not implemented yet"

    def setup_current_page(self):
        print "MMKitDialog.setup_current_page(): Not implemented yet"

    def chunkChanged(self,a0):
        print "MMKitDialog.chunkChanged(QListBoxItem*): Not implemented yet"

    def updatePastableItems(self):
        print "MMKitDialog.updatePastableItems(): Not implemented yet"

    def browseDirectories(self):
        print "MMKitDialog.browseDirectories(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MMKitDialog",s,c)
