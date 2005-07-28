# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MMKitDialog.ui'
#
# Created: Thu Jul 28 14:43:03 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x1c\x49\x44\x41\x54\x78\x9c\xed\x93\xb1\x6a\xc2" \
    "\x40\x18\xc7\x7f\x57\x1c\xa5\x8b\x53\x9e\xa1\x4d" \
    "\xe7\x82\xef\x50\x28\xb7\x95\x0e\x82\xd0\x9b\xe2" \
    "\x52\xc8\xa6\x64\x72\x28\x74\xca\x74\x0e\xe2\x20" \
    "\x2e\x0e\x85\xbe\x43\x8e\x2c\x72\xd2\xb4\xe2\xe6" \
    "\xe2\x13\xf4\x05\xec\x10\x12\x92\x96\x48\x89\x38" \
    "\x54\xfa\x9b\xbe\xbb\x3f\xf7\xdd\xf1\xe3\x3e\x61" \
    "\x8c\xe1\x18\x34\xea\x1e\x54\x4a\xed\xaa\x32\xad" \
    "\xb5\x38\xab\xdb\x18\x20\x89\x66\x24\xd1\x0c\x80" \
    "\xe9\x28\x66\x3a\x8a\xf3\xec\xa0\xc6\xfb\x38\x5a" \
    "\xe3\xdc\xf1\x3e\x67\x55\xb8\xed\xbb\xbc\xbe\x7f" \
    "\xb8\x2e\x65\xa5\x17\xb7\xba\x96\x56\xd7\x02\xb0" \
    "\x1e\x6c\x59\x0f\xb6\x00\x98\x61\x8c\x19\xa6\xfe" \
    "\xc6\x9b\x15\xe3\xcd\x0a\x80\xe6\xd2\xa7\xb9\xf4" \
    "\x81\x53\x70\x2c\xb2\x01\xa9\xe3\xb8\x8a\x1f\xff" \
    "\xb8\xdf\x8b\xe9\xf7\x52\x4f\x52\x4a\xa4\x94\x00" \
    "\x04\x8e\x25\x70\x52\xf7\x76\xee\x60\xe7\x4e\xba" \
    "\xbf\x70\x09\x16\x2e\xf0\xef\xb8\x02\xad\xb5\x68" \
    "\x14\x17\x59\xad\x94\xda\xbd\xbe\xbc\x03\x70\x73" \
    "\x7b\xc9\x24\x89\x00\xe8\xb8\x6d\xde\xfc\x4f\x00" \
    "\xae\x9e\xce\xf9\x78\xee\x00\x70\xf1\x38\xc9\xfd" \
    "\x66\x83\xf2\x87\x1d\x17\x39\xd4\x77\xc9\xf1\xf7" \
    "\xa0\x78\x49\x18\x86\x00\x78\x9e\xc7\x6f\x6a\x38" \
    "\x19\xc7\x45\xea\xf8\xd6\x5a\x8b\x2f\x29\x94\x78" \
    "\x0c\x77\x48\xb1\xfb\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"

class MMKitDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MMKitDialog")

        self.setSizePolicy(QSizePolicy(5,1,0,0,self.sizePolicy().hasHeightForWidth()))
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

        MMKitDialogLayout = QVBoxLayout(self,11,6,"MMKitDialogLayout")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(5,5,0,1,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(200,150))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        MMKitDialogLayout.addWidget(self.elementFrame)

        self.tabWidget2 = QTabWidget(self,"tabWidget2")

        self.tab = QWidget(self.tabWidget2,"tab")
        tabLayout = QGridLayout(self.tab,1,1,0,0,"tabLayout")

        self.elementButtonGroup = QButtonGroup(self.tab,"elementButtonGroup")
        self.elementButtonGroup.setMinimumSize(QSize(0,126))
        self.elementButtonGroup.setFrameShape(QButtonGroup.NoFrame)
        self.elementButtonGroup.setFrameShadow(QButtonGroup.Plain)
        self.elementButtonGroup.setLineWidth(0)
        self.elementButtonGroup.setExclusive(1)
        self.elementButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.elementButtonGroup.layout().setSpacing(0)
        self.elementButtonGroup.layout().setMargin(2)
        elementButtonGroupLayout = QGridLayout(self.elementButtonGroup.layout())
        elementButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.toolButton1 = QToolButton(self.elementButtonGroup,"toolButton1")
        self.toolButton1.setMinimumSize(QSize(30,30))
        self.toolButton1.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton1,1)

        elementButtonGroupLayout.addWidget(self.toolButton1,0,4)

        self.toolButton2 = QToolButton(self.elementButtonGroup,"toolButton2")
        self.toolButton2.setMinimumSize(QSize(30,30))
        self.toolButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton2,2)

        elementButtonGroupLayout.addWidget(self.toolButton2,0,5)

        self.toolButton6 = QToolButton(self.elementButtonGroup,"toolButton6")
        self.toolButton6.setMinimumSize(QSize(30,30))
        self.toolButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton6,6)

        elementButtonGroupLayout.addWidget(self.toolButton6,1,1)

        self.toolButton7 = QToolButton(self.elementButtonGroup,"toolButton7")
        self.toolButton7.setMinimumSize(QSize(30,30))
        self.toolButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton7,7)

        elementButtonGroupLayout.addWidget(self.toolButton7,1,2)

        self.toolButton8 = QToolButton(self.elementButtonGroup,"toolButton8")
        self.toolButton8.setMinimumSize(QSize(30,30))
        self.toolButton8.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton8,8)

        elementButtonGroupLayout.addWidget(self.toolButton8,1,3)

        self.toolButton10 = QToolButton(self.elementButtonGroup,"toolButton10")
        self.toolButton10.setMinimumSize(QSize(30,30))
        self.toolButton10.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton10,10)

        elementButtonGroupLayout.addWidget(self.toolButton10,1,5)

        self.toolButton9 = QToolButton(self.elementButtonGroup,"toolButton9")
        self.toolButton9.setMinimumSize(QSize(30,30))
        self.toolButton9.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton9,9)

        elementButtonGroupLayout.addWidget(self.toolButton9,1,4)

        self.toolButton13 = QToolButton(self.elementButtonGroup,"toolButton13")
        self.toolButton13.setMinimumSize(QSize(30,30))
        self.toolButton13.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton13,13)

        elementButtonGroupLayout.addWidget(self.toolButton13,2,0)

        self.toolButton17 = QToolButton(self.elementButtonGroup,"toolButton17")
        self.toolButton17.setMinimumSize(QSize(30,30))
        self.toolButton17.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton17,17)

        elementButtonGroupLayout.addWidget(self.toolButton17,2,4)

        self.toolButton5 = QToolButton(self.elementButtonGroup,"toolButton5")
        self.toolButton5.setMinimumSize(QSize(30,30))
        self.toolButton5.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton5,5)

        elementButtonGroupLayout.addWidget(self.toolButton5,1,0)

        self.toolButton10_2 = QToolButton(self.elementButtonGroup,"toolButton10_2")
        self.toolButton10_2.setMinimumSize(QSize(30,30))
        self.toolButton10_2.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton10_2,18)

        elementButtonGroupLayout.addWidget(self.toolButton10_2,2,5)

        self.toolButton15 = QToolButton(self.elementButtonGroup,"toolButton15")
        self.toolButton15.setMinimumSize(QSize(30,30))
        self.toolButton15.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton15,15)

        elementButtonGroupLayout.addWidget(self.toolButton15,2,2)

        self.toolButton16 = QToolButton(self.elementButtonGroup,"toolButton16")
        self.toolButton16.setMinimumSize(QSize(30,30))
        self.toolButton16.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton16,16)

        elementButtonGroupLayout.addWidget(self.toolButton16,2,3)

        self.toolButton14 = QToolButton(self.elementButtonGroup,"toolButton14")
        self.toolButton14.setMinimumSize(QSize(30,30))
        self.toolButton14.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton14,14)

        elementButtonGroupLayout.addWidget(self.toolButton14,2,1)

        self.toolButton33 = QToolButton(self.elementButtonGroup,"toolButton33")
        self.toolButton33.setMinimumSize(QSize(30,30))
        self.toolButton33.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton33,33)

        elementButtonGroupLayout.addWidget(self.toolButton33,3,2)

        self.toolButton34 = QToolButton(self.elementButtonGroup,"toolButton34")
        self.toolButton34.setMinimumSize(QSize(30,30))
        self.toolButton34.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton34,34)

        elementButtonGroupLayout.addWidget(self.toolButton34,3,3)

        self.toolButton35 = QToolButton(self.elementButtonGroup,"toolButton35")
        self.toolButton35.setMinimumSize(QSize(30,30))
        self.toolButton35.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton35,35)

        elementButtonGroupLayout.addWidget(self.toolButton35,3,4)

        self.toolButton36 = QToolButton(self.elementButtonGroup,"toolButton36")
        self.toolButton36.setMinimumSize(QSize(30,30))
        self.toolButton36.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton36,36)

        elementButtonGroupLayout.addWidget(self.toolButton36,3,5)

        self.toolButton32 = QToolButton(self.elementButtonGroup,"toolButton32")
        self.toolButton32.setMinimumSize(QSize(30,30))
        self.toolButton32.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton32,32)

        elementButtonGroupLayout.addWidget(self.toolButton32,3,1)

        tabLayout.addMultiCellWidget(self.elementButtonGroup,0,0,0,1)

        self.hybrid_btngrp = QButtonGroup(self.tab,"hybrid_btngrp")
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
        self.hybrid_btngrp.insert( self.sp_btn,3)
        hybrid_btngrpLayout.addWidget(self.sp_btn)

        self.aromatic_btn = QToolButton(self.hybrid_btngrp,"aromatic_btn")
        self.aromatic_btn.setMinimumSize(QSize(30,30))
        self.aromatic_btn.setToggleButton(1)
        self.hybrid_btngrp.insert( self.aromatic_btn,3)
        hybrid_btngrpLayout.addWidget(self.aromatic_btn)
        spacer4 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        hybrid_btngrpLayout.addItem(spacer4)

        tabLayout.addWidget(self.hybrid_btngrp,1,0)
        spacer36 = QSpacerItem(20,34,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer36,1,1)
        self.tabWidget2.insertTab(self.tab,QString(""))

        self.tab_2 = QWidget(self.tabWidget2,"tab_2")
        tabLayout_2 = QVBoxLayout(self.tab_2,11,6,"tabLayout_2")

        self.textLabel1 = QLabel(self.tab_2,"textLabel1")
        tabLayout_2.addWidget(self.textLabel1)

        self.chunkListBox = QListBox(self.tab_2,"chunkListBox")
        self.chunkListBox.setSizePolicy(QSizePolicy(7,7,0,2,self.chunkListBox.sizePolicy().hasHeightForWidth()))
        tabLayout_2.addWidget(self.chunkListBox)
        self.tabWidget2.insertTab(self.tab_2,QString(""))
        MMKitDialogLayout.addWidget(self.tabWidget2)
        spacer4_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        MMKitDialogLayout.addItem(spacer4_2)

        layout10 = QHBoxLayout(None,0,6,"layout10")
        spacer8 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout10.addItem(spacer8)

        self.closePTableButton = QPushButton(self,"closePTableButton")
        self.closePTableButton.setSizePolicy(QSizePolicy(1,0,0,0,self.closePTableButton.sizePolicy().hasHeightForWidth()))
        self.closePTableButton.setDefault(1)
        layout10.addWidget(self.closePTableButton)
        MMKitDialogLayout.addLayout(layout10)

        self.languageChange()

        self.resize(QSize(230,448).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.closePTableButton,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.connect(self.hybrid_btngrp,SIGNAL("clicked(int)"),self.set_hybrid_type)
        self.connect(self.tabWidget2,SIGNAL("currentChanged(QWidget*)"),self.tabpageChanged)
        self.connect(self.chunkListBox,SIGNAL("selectionChanged(QListBoxItem*)"),self.chunkChanged)



    def languageChange(self):
        self.setCaption(self.__tr("Modeling Kit"))
        self.elementButtonGroup.setTitle(QString.null)
        self.toolButton1.setText(self.__tr("H"))
        self.toolButton2.setText(self.__tr("He"))
        self.toolButton6.setText(self.__tr("C"))
        self.toolButton7.setText(self.__tr("N"))
        self.toolButton8.setText(self.__tr("O"))
        self.toolButton10.setText(self.__tr("Ne"))
        self.toolButton9.setText(self.__tr("F"))
        self.toolButton13.setText(self.__tr("Al"))
        self.toolButton17.setText(self.__tr("Cl"))
        self.toolButton5.setText(self.__tr("B"))
        self.toolButton10_2.setText(self.__tr("Ar"))
        self.toolButton15.setText(self.__tr("P"))
        self.toolButton16.setText(self.__tr("S"))
        self.toolButton14.setText(self.__tr("Si"))
        self.toolButton33.setText(self.__tr("As"))
        self.toolButton34.setText(self.__tr("Se"))
        self.toolButton35.setText(self.__tr("Br"))
        self.toolButton36.setText(self.__tr("Kr"))
        self.toolButton32.setText(self.__tr("Ge"))
        self.hybrid_btngrp.setTitle(QString.null)
        self.sp3_btn.setText(QString.null)
        self.sp2_btn.setText(QString.null)
        self.sp_btn.setText(QString.null)
        self.aromatic_btn.setText(QString.null)
        self.tabWidget2.changeTab(self.tab,self.__tr("Atoms"))
        self.textLabel1.setText(self.__tr("Pastable Chunks:"))
        self.tabWidget2.changeTab(self.tab_2,self.__tr("Clipboard"))
        self.closePTableButton.setText(self.__tr("Close"))


    def setElementInfo(self,a0):
        print "MMKitDialog.setElementInfo(int): Not implemented yet"

    def set_hybrid_type(self,a0):
        print "MMKitDialog.set_hybrid_type(int): Not implemented yet"

    def tabpageChanged(self,a0):
        print "MMKitDialog.tabpageChanged(QWidget*): Not implemented yet"

    def chunkChanged(self,a0):
        print "MMKitDialog.chunkChanged(QListBoxItem*): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MMKitDialog",s,c)
