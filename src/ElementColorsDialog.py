# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\atom\cad\src\ElementColorsDialog.ui'
#
# Created: Wed Mar 9 17:57:29 2005
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

class ElementColorsDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("ElementColorsDialog")

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

        ElementColorsDialogLayout = QVBoxLayout(self,11,6,"ElementColorsDialogLayout")

        layout33 = QHBoxLayout(None,0,6,"layout33")

        layout32 = QVBoxLayout(None,0,6,"layout32")

        self.elemInfoLabel = QLabel(self,"elemInfoLabel")
        self.elemInfoLabel.setSizePolicy(QSizePolicy(5,5,0,1,self.elemInfoLabel.sizePolicy().hasHeightForWidth()))
        self.elemInfoLabel.setMinimumSize(QSize(0,0))
        self.elemInfoLabel.setPaletteBackgroundColor(QColor(227,211,231))
        self.elemInfoLabel.setTextFormat(QLabel.RichText)
        self.elemInfoLabel.setAlignment(QLabel.AlignCenter)
        layout32.addWidget(self.elemInfoLabel)

        self.elemColorLabel = QLabel(self,"elemColorLabel")
        self.elemColorLabel.setSizePolicy(QSizePolicy(5,5,0,0,self.elemColorLabel.sizePolicy().hasHeightForWidth()))
        self.elemColorLabel.setMinimumSize(QSize(0,50))
        self.elemColorLabel.setTextFormat(QLabel.RichText)
        self.elemColorLabel.setAlignment(QLabel.AlignCenter)
        layout32.addWidget(self.elemColorLabel)
        layout33.addLayout(layout32)

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(5,5,0,0,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(0,0))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        layout33.addWidget(self.elementFrame)

        layout16 = QVBoxLayout(None,0,6,"layout16")

        layout11 = QVBoxLayout(None,0,6,"layout11")

        self.redSlider = QSlider(self,"redSlider")
        self.redSlider.setEnabled(1)
        self.redSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.redSlider.sizePolicy().hasHeightForWidth()))
        self.redSlider.setPaletteForegroundColor(QColor(255,0,0))
        self.redSlider.setMaxValue(255)
        self.redSlider.setOrientation(QSlider.Horizontal)
        self.redSlider.setTickmarks(QSlider.Above)
        layout11.addWidget(self.redSlider)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setMaximumSize(QSize(40,32767))
        self.textLabel2.setPaletteBackgroundColor(QColor(255,0,0))
        layout10.addWidget(self.textLabel2)

        self.redSpinBox = QSpinBox(self,"redSpinBox")
        self.redSpinBox.setEnabled(1)
        self.redSpinBox.setSizePolicy(QSizePolicy(1,0,0,0,self.redSpinBox.sizePolicy().hasHeightForWidth()))
        self.redSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.redSpinBox.setMaxValue(255)
        layout10.addWidget(self.redSpinBox)
        layout11.addLayout(layout10)
        layout16.addLayout(layout11)

        layout11_2 = QVBoxLayout(None,0,6,"layout11_2")

        self.greenSlider = QSlider(self,"greenSlider")
        self.greenSlider.setEnabled(1)
        self.greenSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.greenSlider.sizePolicy().hasHeightForWidth()))
        self.greenSlider.setPaletteForegroundColor(QColor(0,255,0))
        self.greenSlider.setMaxValue(255)
        self.greenSlider.setOrientation(QSlider.Horizontal)
        self.greenSlider.setTickmarks(QSlider.Above)
        layout11_2.addWidget(self.greenSlider)

        layout10_2 = QHBoxLayout(None,0,6,"layout10_2")

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        self.textLabel2_2.setMaximumSize(QSize(40,32767))
        self.textLabel2_2.setPaletteBackgroundColor(QColor(0,255,0))
        layout10_2.addWidget(self.textLabel2_2)

        self.greenSpinBox = QSpinBox(self,"greenSpinBox")
        self.greenSpinBox.setEnabled(1)
        self.greenSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.greenSpinBox.setMaxValue(255)
        layout10_2.addWidget(self.greenSpinBox)
        layout11_2.addLayout(layout10_2)
        layout16.addLayout(layout11_2)

        layout11_3 = QVBoxLayout(None,0,6,"layout11_3")

        self.blueSlider = QSlider(self,"blueSlider")
        self.blueSlider.setEnabled(1)
        self.blueSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.blueSlider.sizePolicy().hasHeightForWidth()))
        self.blueSlider.setPaletteForegroundColor(QColor(0,0,255))
        self.blueSlider.setMaxValue(255)
        self.blueSlider.setOrientation(QSlider.Horizontal)
        self.blueSlider.setTickmarks(QSlider.Above)
        layout11_3.addWidget(self.blueSlider)

        layout10_3 = QHBoxLayout(None,0,6,"layout10_3")

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        self.textLabel2_3.setMaximumSize(QSize(40,32767))
        self.textLabel2_3.setPaletteBackgroundColor(QColor(0,0,255))
        layout10_3.addWidget(self.textLabel2_3)

        self.blueSpinBox = QSpinBox(self,"blueSpinBox")
        self.blueSpinBox.setEnabled(1)
        self.blueSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.blueSpinBox.setMaxValue(255)
        layout10_3.addWidget(self.blueSpinBox)
        layout11_3.addLayout(layout10_3)
        layout16.addLayout(layout11_3)
        layout33.addLayout(layout16)
        ElementColorsDialogLayout.addLayout(layout33)

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setPaletteBackgroundColor(QColor(213,229,231))
        self.groupBox1.setFrameShadow(QGroupBox.Raised)
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QGridLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.pushButton5 = QPushButton(self.groupBox1,"pushButton5")
        self.pushButton5.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton5.sizePolicy().hasHeightForWidth()))
        pushButton5_font = QFont(self.pushButton5.font())
        pushButton5_font.setBold(1)
        self.pushButton5.setFont(pushButton5_font)
        self.pushButton5.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton5.setToggleButton(1)
        self.pushButton5.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton5,1,0)

        self.pushButton54 = QPushButton(self.groupBox1,"pushButton54")
        self.pushButton54.setEnabled(0)
        pushButton54_font = QFont(self.pushButton54.font())
        pushButton54_font.setBold(1)
        self.pushButton54.setFont(pushButton54_font)
        self.pushButton54.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton54.setToggleButton(1)
        self.pushButton54.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton54,4,5)

        self.pushButton34 = QPushButton(self.groupBox1,"pushButton34")
        self.pushButton34.setEnabled(1)
        pushButton34_font = QFont(self.pushButton34.font())
        pushButton34_font.setBold(1)
        self.pushButton34.setFont(pushButton34_font)
        self.pushButton34.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton34.setToggleButton(1)
        self.pushButton34.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton34,3,3)

        self.pushButton32 = QPushButton(self.groupBox1,"pushButton32")
        self.pushButton32.setEnabled(1)
        pushButton32_font = QFont(self.pushButton32.font())
        pushButton32_font.setBold(1)
        self.pushButton32.setFont(pushButton32_font)
        self.pushButton32.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton32.setToggleButton(1)
        self.pushButton32.setOn(0)
        self.pushButton32.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton32,3,1)

        self.pushButton14 = QPushButton(self.groupBox1,"pushButton14")
        pushButton14_font = QFont(self.pushButton14.font())
        pushButton14_font.setBold(1)
        self.pushButton14.setFont(pushButton14_font)
        self.pushButton14.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton14.setToggleButton(1)
        self.pushButton14.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton14,2,1)

        self.pushButton10 = QPushButton(self.groupBox1,"pushButton10")
        self.pushButton10.setEnabled(1)
        pushButton10_font = QFont(self.pushButton10.font())
        pushButton10_font.setBold(1)
        self.pushButton10.setFont(pushButton10_font)
        self.pushButton10.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton10.setToggleButton(1)
        self.pushButton10.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton10,1,5)

        self.pushButton15 = QPushButton(self.groupBox1,"pushButton15")
        pushButton15_font = QFont(self.pushButton15.font())
        pushButton15_font.setBold(1)
        self.pushButton15.setFont(pushButton15_font)
        self.pushButton15.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton15.setToggleButton(1)
        self.pushButton15.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton15,2,2)

        self.pushButton7 = QPushButton(self.groupBox1,"pushButton7")
        pushButton7_font = QFont(self.pushButton7.font())
        pushButton7_font.setBold(1)
        self.pushButton7.setFont(pushButton7_font)
        self.pushButton7.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton7.setToggleButton(1)
        self.pushButton7.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton7,1,2)

        self.pushButton51 = QPushButton(self.groupBox1,"pushButton51")
        self.pushButton51.setEnabled(0)
        pushButton51_font = QFont(self.pushButton51.font())
        pushButton51_font.setBold(1)
        self.pushButton51.setFont(pushButton51_font)
        self.pushButton51.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton51.setToggleButton(1)
        self.pushButton51.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton51,4,2)

        self.pushButton16 = QPushButton(self.groupBox1,"pushButton16")
        pushButton16_font = QFont(self.pushButton16.font())
        pushButton16_font.setBold(1)
        self.pushButton16.setFont(pushButton16_font)
        self.pushButton16.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton16.setToggleButton(1)
        self.pushButton16.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton16,2,3)

        self.pushButton2 = QPushButton(self.groupBox1,"pushButton2")
        self.pushButton2.setEnabled(1)
        self.pushButton2.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton2.sizePolicy().hasHeightForWidth()))
        pushButton2_font = QFont(self.pushButton2.font())
        pushButton2_font.setBold(1)
        self.pushButton2.setFont(pushButton2_font)
        self.pushButton2.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton2.setToggleButton(1)
        self.pushButton2.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton2,0,5)

        self.pushButton36 = QPushButton(self.groupBox1,"pushButton36")
        self.pushButton36.setEnabled(1)
        pushButton36_font = QFont(self.pushButton36.font())
        pushButton36_font.setBold(1)
        self.pushButton36.setFont(pushButton36_font)
        self.pushButton36.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton36.setToggleButton(1)
        self.pushButton36.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton36,3,5)

        self.pushButton53 = QPushButton(self.groupBox1,"pushButton53")
        self.pushButton53.setEnabled(0)
        pushButton53_font = QFont(self.pushButton53.font())
        pushButton53_font.setBold(1)
        self.pushButton53.setFont(pushButton53_font)
        self.pushButton53.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton53.setToggleButton(1)
        self.pushButton53.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton53,4,4)

        self.pushButton52 = QPushButton(self.groupBox1,"pushButton52")
        self.pushButton52.setEnabled(0)
        pushButton52_font = QFont(self.pushButton52.font())
        pushButton52_font.setBold(1)
        self.pushButton52.setFont(pushButton52_font)
        self.pushButton52.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton52.setToggleButton(1)
        self.pushButton52.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton52,4,3)

        self.pushButton8 = QPushButton(self.groupBox1,"pushButton8")
        pushButton8_font = QFont(self.pushButton8.font())
        pushButton8_font.setBold(1)
        self.pushButton8.setFont(pushButton8_font)
        self.pushButton8.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton8.setToggleButton(1)
        self.pushButton8.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton8,1,3)

        self.pushButton6 = QPushButton(self.groupBox1,"pushButton6")
        pushButton6_font = QFont(self.pushButton6.font())
        pushButton6_font.setBold(1)
        self.pushButton6.setFont(pushButton6_font)
        self.pushButton6.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton6.setToggleButton(1)
        self.pushButton6.setOn(1)
        self.pushButton6.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton6,1,1)

        self.pushButton35 = QPushButton(self.groupBox1,"pushButton35")
        self.pushButton35.setEnabled(1)
        pushButton35_font = QFont(self.pushButton35.font())
        pushButton35_font.setBold(1)
        self.pushButton35.setFont(pushButton35_font)
        self.pushButton35.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton35.setToggleButton(1)
        self.pushButton35.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton35,3,4)

        self.pushButton18 = QPushButton(self.groupBox1,"pushButton18")
        self.pushButton18.setEnabled(1)
        pushButton18_font = QFont(self.pushButton18.font())
        pushButton18_font.setBold(1)
        self.pushButton18.setFont(pushButton18_font)
        self.pushButton18.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton18.setToggleButton(1)
        self.pushButton18.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton18,2,5)

        self.pushButton13 = QPushButton(self.groupBox1,"pushButton13")
        pushButton13_font = QFont(self.pushButton13.font())
        pushButton13_font.setBold(1)
        self.pushButton13.setFont(pushButton13_font)
        self.pushButton13.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton13.setToggleButton(1)
        self.pushButton13.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton13,2,0)

        self.pushButton1 = QPushButton(self.groupBox1,"pushButton1")
        self.pushButton1.setSizePolicy(QSizePolicy(5,0,0,0,self.pushButton1.sizePolicy().hasHeightForWidth()))
        pushButton1_font = QFont(self.pushButton1.font())
        pushButton1_font.setBold(1)
        self.pushButton1.setFont(pushButton1_font)
        self.pushButton1.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton1.setToggleButton(1)
        self.pushButton1.setOn(0)
        self.pushButton1.setAutoDefault(0)
        self.pushButton1.setDefault(0)

        groupBox1Layout.addWidget(self.pushButton1,0,4)

        self.pushButton33 = QPushButton(self.groupBox1,"pushButton33")
        self.pushButton33.setEnabled(1)
        pushButton33_font = QFont(self.pushButton33.font())
        pushButton33_font.setBold(1)
        self.pushButton33.setFont(pushButton33_font)
        self.pushButton33.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton33.setToggleButton(1)
        self.pushButton33.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton33,3,2)

        self.pushButton17 = QPushButton(self.groupBox1,"pushButton17")
        self.pushButton17.setBackgroundOrigin(QPushButton.ParentOrigin)
        pushButton17_font = QFont(self.pushButton17.font())
        pushButton17_font.setBold(1)
        self.pushButton17.setFont(pushButton17_font)
        self.pushButton17.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton17.setToggleButton(1)
        self.pushButton17.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton17,2,4)

        self.pushButton9 = QPushButton(self.groupBox1,"pushButton9")
        pushButton9_font = QFont(self.pushButton9.font())
        pushButton9_font.setBold(1)
        self.pushButton9.setFont(pushButton9_font)
        self.pushButton9.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton9.setToggleButton(1)
        self.pushButton9.setAutoDefault(0)

        groupBox1Layout.addWidget(self.pushButton9,1,4)
        ElementColorsDialogLayout.addWidget(self.groupBox1)

        layout12 = QGridLayout(None,1,1,0,6,"layout12")

        self.saveColorsPB = QPushButton(self,"saveColorsPB")
        self.saveColorsPB.setAutoDefault(0)

        layout12.addWidget(self.saveColorsPB,0,1)

        self.defaultButton = QPushButton(self,"defaultButton")
        self.defaultButton.setAutoDefault(0)

        layout12.addWidget(self.defaultButton,1,0)

        self.loadColorsPB = QPushButton(self,"loadColorsPB")
        self.loadColorsPB.setAutoDefault(0)

        layout12.addWidget(self.loadColorsPB,0,0)

        self.cancelButton = QPushButton(self,"cancelButton")
        self.cancelButton.setAutoDefault(0)

        layout12.addWidget(self.cancelButton,2,1)

        self.alterButton = QPushButton(self,"alterButton")
        self.alterButton.setAutoDefault(0)

        layout12.addWidget(self.alterButton,1,1)

        self.okButton = QPushButton(self,"okButton")
        self.okButton.setAutoDefault(0)
        self.okButton.setDefault(0)

        layout12.addWidget(self.okButton,2,0)
        ElementColorsDialogLayout.addLayout(layout12)

        self.languageChange()

        self.resize(QSize(554,527).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.ok)
        self.connect(self.loadColorsPB,SIGNAL("clicked()"),self.read_element_rgb_table)
        self.connect(self.saveColorsPB,SIGNAL("clicked()"),self.write_element_rgb_table)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.connect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.connect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.connect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
        self.connect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.connect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.connect(self.defaultButton,SIGNAL("clicked()"),self.loadDefaultProp)
        self.connect(self.alterButton,SIGNAL("clicked()"),self.loadAlterProp)

        self.setTabOrder(self.redSlider,self.redSpinBox)
        self.setTabOrder(self.redSpinBox,self.greenSlider)
        self.setTabOrder(self.greenSlider,self.greenSpinBox)
        self.setTabOrder(self.greenSpinBox,self.blueSlider)
        self.setTabOrder(self.blueSlider,self.blueSpinBox)
        self.setTabOrder(self.blueSpinBox,self.loadColorsPB)
        self.setTabOrder(self.loadColorsPB,self.saveColorsPB)
        self.setTabOrder(self.saveColorsPB,self.defaultButton)
        self.setTabOrder(self.defaultButton,self.alterButton)
        self.setTabOrder(self.alterButton,self.okButton)
        self.setTabOrder(self.okButton,self.cancelButton)
        self.setTabOrder(self.cancelButton,self.pushButton18)


    def languageChange(self):
        self.setCaption(self.__tr("Element Color Settings"))
        self.elemInfoLabel.setText(QString.null)
        self.elemColorLabel.setText(QString.null)
        self.textLabel2.setText(QString.null)
        self.textLabel2_2.setText(QString.null)
        self.textLabel2_3.setText(QString.null)
        self.groupBox1.setTitle(QString.null)
        self.pushButton5.setText(self.__tr("B"))
        self.pushButton54.setText(self.__tr("Xe"))
        self.pushButton34.setText(self.__tr("Se"))
        self.pushButton32.setText(self.__tr("Ge"))
        self.pushButton14.setText(self.__tr("Si"))
        self.pushButton10.setText(self.__tr("Ne"))
        self.pushButton15.setText(self.__tr("P"))
        self.pushButton7.setText(self.__tr("N"))
        self.pushButton51.setText(self.__tr("Sb"))
        self.pushButton16.setText(self.__tr("S"))
        self.pushButton2.setText(self.__tr("He"))
        self.pushButton36.setText(self.__tr("Kr"))
        self.pushButton53.setText(self.__tr("I"))
        self.pushButton52.setText(self.__tr("Te"))
        self.pushButton8.setText(self.__tr("O"))
        self.pushButton6.setText(self.__tr("C"))
        self.pushButton35.setText(self.__tr("Br"))
        self.pushButton18.setText(self.__tr("Ar"))
        self.pushButton13.setText(self.__tr("Al"))
        self.pushButton1.setText(self.__tr("H"))
        self.pushButton33.setText(self.__tr("As"))
        self.pushButton17.setText(self.__tr("Cl"))
        self.pushButton9.setText(self.__tr("F"))
        self.saveColorsPB.setText(self.__tr("Save Colors ..."))
        QToolTip.add(self.saveColorsPB,self.__tr("Save the current color setting for elements in a text file."))
        self.defaultButton.setText(self.__tr("Set To Default"))
        QToolTip.add(self.defaultButton,self.__tr("Set element color to the default set."))
        self.loadColorsPB.setText(self.__tr("Load Colors ..."))
        QToolTip.add(self.loadColorsPB,self.__tr("Load element colors from an external text file."))
        self.cancelButton.setText(self.__tr("Cancel"))
        self.alterButton.setText(self.__tr("Set To Alternate"))
        QToolTip.add(self.alterButton,self.__tr("Set elements color to the alternate set."))
        self.okButton.setText(self.__tr("Ok"))


    def setElementInfo(self):
        print "ElementColorsDialog.setElementInfo(): Not implemented yet"

    def read_element_rgb_table(self):
        print "ElementColorsDialog.read_element_rgb_table(): Not implemented yet"

    def write_element_rgb_table(self):
        print "ElementColorsDialog.write_element_rgb_table(): Not implemented yet"

    def changeSliderBlue(self,a0):
        print "ElementColorsDialog.changeSliderBlue(int): Not implemented yet"

    def ok(self):
        print "ElementColorsDialog.ok(): Not implemented yet"

    def changeSpinRed(self,a0):
        print "ElementColorsDialog.changeSpinRed(int): Not implemented yet"

    def changeSliderRed(self,a0):
        print "ElementColorsDialog.changeSliderRed(int): Not implemented yet"

    def changeSpinBlue(self,a0):
        print "ElementColorsDialog.changeSpinBlue(int): Not implemented yet"

    def changeSpinGreen(self,a0):
        print "ElementColorsDialog.changeSpinGreen(int): Not implemented yet"

    def changeSliderGreen(self,a0):
        print "ElementColorsDialog.changeSliderGreen(int): Not implemented yet"

    def cancel(self):
        print "ElementColorsDialog.cancel(): Not implemented yet"

    def loadDefaultProp(self):
        print "ElementColorsDialog.loadDefaultProp(): Not implemented yet"

    def loadAlterProp(self):
        print "ElementColorsDialog.loadAlterProp(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ElementColorsDialog",s,c)
