# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\atom\cad\src\ElementSelectorDialog.ui'
#
# Created: Fri Feb 25 16:34:42 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 19 1",
". c None",
"a c #00f2d3",
"p c #02ba8d",
"d c #05ab11",
"# c #2d2d2d",
"g c #39fda3",
"c c #4090fc",
"i c #808080",
"h c #aa9bf5",
"j c #ad46fc",
"l c #adfa5a",
"q c #c0c0c0",
"f c #cb0c03",
"n c #cd00f2",
"b c #d1c7f5",
"m c #dfdc01",
"e c #f3b3f5",
"k c #fcd846",
"o c #ffa31f",
"......................",
"..............#######.",
"..............#aa#bb#.",
"..............#aa#bb#.",
"..............#aa#bb#.",
"..###################.",
"..#cc#dd#ee#ff#gg#bb#.",
"..#cc#dd#ee#ff#gg#bb#.",
"..#cc#dd#ee#ff#gg#bb#.",
"..###################.",
"..#hh#ii#jj#kk#ll#bb#.",
"..#hh#ii#jj#kk#ll#bb#.",
"..#hh#ii#jj#kk#ll#bb#.",
"..###################.",
".....#mm#nn#oo#pp#bb#.",
".....#mm#nn#oo#pp#bb#.",
".....#mm#nn#oo#pp#bb#.",
".....################.",
"........#qq#qq#qq#qq#.",
"........#qq#qq#qq#qq#.",
"........#qq#qq#qq#qq#.",
"........#############."
]

class ElementSelectorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("ElementSelectorDialog")

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

        ElementSelectorDialogLayout = QVBoxLayout(self,11,6,"ElementSelectorDialogLayout")

        layout18 = QHBoxLayout(None,0,3,"layout18")

        layout17 = QVBoxLayout(None,0,0,"layout17")

        self.elemInfoLabel = QLabel(self,"elemInfoLabel")
        self.elemInfoLabel.setSizePolicy(QSizePolicy(0,5,0,1,self.elemInfoLabel.sizePolicy().hasHeightForWidth()))
        self.elemInfoLabel.setMinimumSize(QSize(70,0))
        self.elemInfoLabel.setPaletteBackgroundColor(QColor(227,211,231))
        self.elemInfoLabel.setTextFormat(QLabel.RichText)
        self.elemInfoLabel.setAlignment(QLabel.AlignCenter)
        layout17.addWidget(self.elemInfoLabel)

        self.elemColorLabel = QLabel(self,"elemColorLabel")
        self.elemColorLabel.setSizePolicy(QSizePolicy(0,5,0,0,self.elemColorLabel.sizePolicy().hasHeightForWidth()))
        self.elemColorLabel.setMinimumSize(QSize(70,50))
        self.elemColorLabel.setTextFormat(QLabel.RichText)
        self.elemColorLabel.setAlignment(QLabel.AlignCenter)
        layout17.addWidget(self.elemColorLabel)
        layout18.addLayout(layout17)

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setEnabled(0)
        self.elementFrame.setSizePolicy(QSizePolicy(5,5,0,0,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(120,0))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        layout18.addWidget(self.elementFrame)

        layout16 = QVBoxLayout(None,0,6,"layout16")

        layout11 = QVBoxLayout(None,0,6,"layout11")

        self.redSlider = QSlider(self,"redSlider")
        self.redSlider.setEnabled(1)
        self.redSlider.setSizePolicy(QSizePolicy(3,0,0,0,self.redSlider.sizePolicy().hasHeightForWidth()))
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
        self.redSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.redSpinBox.setMaxValue(255)
        layout10.addWidget(self.redSpinBox)
        layout11.addLayout(layout10)
        layout16.addLayout(layout11)

        layout11_2 = QVBoxLayout(None,0,6,"layout11_2")

        self.greenSlider = QSlider(self,"greenSlider")
        self.greenSlider.setEnabled(1)
        self.greenSlider.setSizePolicy(QSizePolicy(3,0,0,0,self.greenSlider.sizePolicy().hasHeightForWidth()))
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
        self.blueSlider.setSizePolicy(QSizePolicy(3,0,0,0,self.blueSlider.sizePolicy().hasHeightForWidth()))
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
        layout18.addLayout(layout16)
        ElementSelectorDialogLayout.addLayout(layout18)
        
        self.elementGroupBox = QGroupBox(self,"elementGroupBox")
        self.elementGroupBox.setPaletteForegroundColor(QColor(0,0,0))
        self.elementGroupBox.setPaletteBackgroundColor(QColor(208,203,231))
        self.elementGroupBox.setFrameShadow(QGroupBox.Raised)
        self.elementGroupBox.setLineWidth(1)

        layout22 = QGridLayout(self.elementGroupBox,5,6,0,2,"layout22")

        self.pushButton1 = QPushButton(self.elementGroupBox,"pushButton1")
        self.pushButton1.setSizePolicy(QSizePolicy(1,0,0,0,self.pushButton1.sizePolicy().hasHeightForWidth()))
        pushButton1_font = QFont(self.pushButton1.font())
        pushButton1_font.setBold(1)
        self.pushButton1.setFont(pushButton1_font)
        self.pushButton1.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton1.setToggleButton(1)
        self.pushButton1.setOn(0)
        self.pushButton1.setAutoDefault(0)
        self.pushButton1.setDefault(0)

        layout22.addWidget(self.pushButton1,0,4)

        self.pushButton2 = QPushButton(self.elementGroupBox,"pushButton2")
        self.pushButton2.setEnabled(1)
        self.pushButton2.setSizePolicy(QSizePolicy(1,0,0,0,self.pushButton2.sizePolicy().hasHeightForWidth()))
        pushButton2_font = QFont(self.pushButton2.font())
        pushButton2_font.setBold(1)
        self.pushButton2.setFont(pushButton2_font)
        self.pushButton2.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton2.setToggleButton(1)
        self.pushButton2.setAutoDefault(0)

        layout22.addWidget(self.pushButton2,0,5)

        self.pushButton5 = QPushButton(self.elementGroupBox,"pushButton5")
        pushButton5_font = QFont(self.pushButton5.font())
        pushButton5_font.setBold(1)
        self.pushButton5.setFont(pushButton5_font)
        self.pushButton5.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton5.setToggleButton(1)
        self.pushButton5.setAutoDefault(0)

        layout22.addWidget(self.pushButton5,1,0)
        
        self.pushButton6 = QPushButton(self.elementGroupBox,"pushButton6")
        pushButton6_font = QFont(self.pushButton6.font())
        pushButton6_font.setBold(1)
        self.pushButton6.setFont(pushButton6_font)
        self.pushButton6.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton6.setToggleButton(1)
        self.pushButton6.setOn(1)
        self.pushButton6.setAutoDefault(0)

        layout22.addWidget(self.pushButton6,1,1)

        self.pushButton7 = QPushButton(self.elementGroupBox,"pushButton7")
        pushButton7_font = QFont(self.pushButton7.font())
        pushButton7_font.setBold(1)
        self.pushButton7.setFont(pushButton7_font)
        self.pushButton7.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton7.setToggleButton(1)
        self.pushButton7.setAutoDefault(0)

        layout22.addWidget(self.pushButton7,1,2)

        self.pushButton8 = QPushButton(self.elementGroupBox,"pushButton8")
        pushButton8_font = QFont(self.pushButton8.font())
        pushButton8_font.setBold(1)
        self.pushButton8.setFont(pushButton8_font)
        self.pushButton8.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton8.setToggleButton(1)
        self.pushButton8.setAutoDefault(0)

        layout22.addWidget(self.pushButton8,1,3)
        
        self.pushButton9 = QPushButton(self.elementGroupBox,"pushButton9")
        pushButton9_font = QFont(self.pushButton9.font())
        pushButton9_font.setBold(1)
        self.pushButton9.setFont(pushButton9_font)
        self.pushButton9.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton9.setToggleButton(1)
        self.pushButton9.setAutoDefault(0)

        layout22.addWidget(self.pushButton9,1,4)
        
        self.pushButton10 = QPushButton(self.elementGroupBox,"pushButton10")
        self.pushButton10.setEnabled(1)
        pushButton10_font = QFont(self.pushButton10.font())
        pushButton10_font.setBold(1)
        self.pushButton10.setFont(pushButton10_font)
        self.pushButton10.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton10.setToggleButton(1)
        self.pushButton10.setAutoDefault(0)

        layout22.addWidget(self.pushButton10,1,5)
        
        self.pushButton13 = QPushButton(self.elementGroupBox,"pushButton13")
        pushButton13_font = QFont(self.pushButton13.font())
        pushButton13_font.setPointSize(9)
        pushButton13_font.setBold(1)
        self.pushButton13.setFont(pushButton13_font)
        self.pushButton13.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton13.setToggleButton(1)
        self.pushButton13.setAutoDefault(0)

        layout22.addWidget(self.pushButton13,2,0)
        
        self.pushButton14 = QPushButton(self.elementGroupBox,"pushButton14")
        pushButton14_font = QFont(self.pushButton14.font())
        pushButton14_font.setBold(1)
        self.pushButton14.setFont(pushButton14_font)
        self.pushButton14.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton14.setToggleButton(1)
        self.pushButton14.setAutoDefault(0)

        layout22.addWidget(self.pushButton14,2,1)
        
        self.pushButton15 = QPushButton(self.elementGroupBox,"pushButton15")
        pushButton15_font = QFont(self.pushButton15.font())
        pushButton15_font.setBold(1)
        self.pushButton15.setFont(pushButton15_font)
        self.pushButton15.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton15.setToggleButton(1)
        self.pushButton15.setAutoDefault(0)

        layout22.addWidget(self.pushButton15,2,2)

        self.pushButton16 = QPushButton(self.elementGroupBox,"pushButton16")
        pushButton16_font = QFont(self.pushButton16.font())
        pushButton16_font.setBold(1)
        self.pushButton16.setFont(pushButton16_font)
        self.pushButton16.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton16.setToggleButton(1)
        self.pushButton16.setAutoDefault(0)

        layout22.addWidget(self.pushButton16,2,3)

        self.pushButton17 = QPushButton(self.elementGroupBox,"pushButton17")
        self.pushButton17.setBackgroundOrigin(QPushButton.WindowOrigin)
        pushButton17_font = QFont(self.pushButton17.font())
        pushButton17_font.setBold(1)
        self.pushButton17.setFont(pushButton17_font)
        self.pushButton17.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton17.setToggleButton(1)
        self.pushButton17.setAutoDefault(0)

        layout22.addWidget(self.pushButton17,2,4)
        
        self.pushButton18 = QPushButton(self.elementGroupBox,"pushButton18")
        self.pushButton18.setEnabled(1)
        pushButton18_font = QFont(self.pushButton18.font())
        pushButton18_font.setBold(1)
        self.pushButton18.setFont(pushButton18_font)
        self.pushButton18.setToggleButton(1)
        self.pushButton18.setAutoDefault(0)

        layout22.addWidget(self.pushButton18,2,5)

        self.pushButton32 = QPushButton(self.elementGroupBox,"pushButton32")
        self.pushButton32.setEnabled(1)
        pushButton32_font = QFont(self.pushButton32.font())
        pushButton32_font.setBold(1)
        self.pushButton32.setFont(pushButton32_font)
        self.pushButton32.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton32.setToggleButton(1)
        self.pushButton32.setOn(0)
        self.pushButton32.setAutoDefault(0)

        layout22.addWidget(self.pushButton32,3,1)
        
        self.pushButton33 = QPushButton(self.elementGroupBox,"pushButton33")
        self.pushButton33.setEnabled(1)
        pushButton33_font = QFont(self.pushButton33.font())
        pushButton33_font.setBold(1)
        self.pushButton33.setFont(pushButton33_font)
        self.pushButton33.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton33.setToggleButton(1)
        self.pushButton33.setAutoDefault(0)

        layout22.addWidget(self.pushButton33,3,2)

        self.pushButton34 = QPushButton(self.elementGroupBox,"pushButton34")
        self.pushButton34.setEnabled(1)
        pushButton34_font = QFont(self.pushButton34.font())
        pushButton34_font.setBold(1)
        self.pushButton34.setFont(pushButton34_font)
        self.pushButton34.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton34.setToggleButton(1)
        self.pushButton34.setAutoDefault(0)

        layout22.addWidget(self.pushButton34,3,3)
        
        self.pushButton35 = QPushButton(self.elementGroupBox,"pushButton35")
        self.pushButton35.setEnabled(1)
        pushButton35_font = QFont(self.pushButton35.font())
        pushButton35_font.setBold(1)
        self.pushButton35.setFont(pushButton35_font)
        self.pushButton35.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton35.setToggleButton(1)
        self.pushButton35.setAutoDefault(0)

        layout22.addWidget(self.pushButton35,3,4)
        
        self.pushButton36 = QPushButton(self.elementGroupBox,"pushButton36")
        self.pushButton36.setEnabled(1)
        pushButton36_font = QFont(self.pushButton36.font())
        pushButton36_font.setBold(1)
        self.pushButton36.setFont(pushButton36_font)
        self.pushButton36.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton36.setToggleButton(1)
        self.pushButton36.setAutoDefault(0)

        layout22.addWidget(self.pushButton36,3,5)

        self.pushButton51 = QPushButton(self.elementGroupBox,"pushButton51")
        self.pushButton51.setEnabled(0)
        pushButton51_font = QFont(self.pushButton51.font())
        pushButton51_font.setBold(1)
        self.pushButton51.setFont(pushButton51_font)
        self.pushButton51.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton51.setToggleButton(1)
        self.pushButton51.setAutoDefault(0)

        layout22.addWidget(self.pushButton51,4,2)

        self.pushButton52 = QPushButton(self.elementGroupBox,"pushButton52")
        self.pushButton52.setEnabled(0)
        pushButton52_font = QFont(self.pushButton52.font())
        pushButton52_font.setBold(1)
        self.pushButton52.setFont(pushButton52_font)
        self.pushButton52.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton52.setToggleButton(1)
        self.pushButton52.setAutoDefault(0)

        layout22.addWidget(self.pushButton52,4,3)

        self.pushButton53 = QPushButton(self.elementGroupBox,"pushButton53")
        self.pushButton53.setEnabled(0)
        pushButton53_font = QFont(self.pushButton53.font())
        pushButton53_font.setBold(1)
        self.pushButton53.setFont(pushButton53_font)
        self.pushButton53.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton53.setToggleButton(1)
        self.pushButton53.setAutoDefault(0)

        layout22.addWidget(self.pushButton53,4,4)

        self.pushButton54 = QPushButton(self.elementGroupBox,"pushButton54")
        self.pushButton54.setEnabled(0)
        pushButton54_font = QFont(self.pushButton54.font())
        pushButton54_font.setBold(1)
        self.pushButton54.setFont(pushButton54_font)
        self.pushButton54.setFocusPolicy(QPushButton.NoFocus)
        self.pushButton54.setToggleButton(1)
        self.pushButton54.setAutoDefault(0)

        layout22.addWidget(self.pushButton54,4,5)

        #ElementSelectorDialogLayout.addLayout(layout22)
        ElementSelectorDialogLayout.addWidget(self.elementGroupBox)

        layout21 = QVBoxLayout(None,0,13,"layout21")

        layout19 = QGridLayout(None,1,1,0,27,"layout19")

        self.loadColorsPB = QPushButton(self,"loadColorsPB")
        self.loadColorsPB.setAutoDefault(0)

        layout19.addWidget(self.loadColorsPB,1,0)

        self.transmuteCheckBox = QCheckBox(self,"transmuteCheckBox")

        layout19.addWidget(self.transmuteCheckBox,0,1)

        self.saveColorsPB = QPushButton(self,"saveColorsPB")
        self.saveColorsPB.setAutoDefault(0)

        layout19.addWidget(self.saveColorsPB,1,1)

        self.TransmuteButton = QPushButton(self,"TransmuteButton")
        self.TransmuteButton.setAutoDefault(0)

        layout19.addWidget(self.TransmuteButton,0,0)
        layout21.addLayout(layout19)

        layout20 = QHBoxLayout(None,1,27,"layout20")

        self.okButton = QPushButton(self,"okButton")
        self.okButton.setAutoDefault(0)
        self.okButton.setDefault(0)
        layout20.addWidget(self.okButton)

        self.cancelButton = QPushButton(self,"cancelButton")
        self.cancelButton.setAutoDefault(0)
        layout20.addWidget(self.cancelButton)
        layout21.addLayout(layout20)
        ElementSelectorDialogLayout.addLayout(layout21)

        self.languageChange()

        self.resize(QSize(150,200).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.ok)
        self.connect(self.TransmuteButton,SIGNAL("clicked()"),self.transmutePressed)
        self.connect(self.loadColorsPB,SIGNAL("clicked()"),self.read_element_rgb_table)
        self.connect(self.saveColorsPB,SIGNAL("clicked()"),self.write_element_rgb_table)
        self.connect(self.redSlider,SIGNAL("valueChanged(int)"),self.changeSpinRed)
        self.connect(self.redSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderRed)
        self.connect(self.blueSlider,SIGNAL("valueChanged(int)"),self.changeSpinBlue)
        self.connect(self.blueSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderBlue)
        self.connect(self.greenSlider,SIGNAL("valueChanged(int)"),self.changeSpinGreen)
        self.connect(self.greenSpinBox,SIGNAL("valueChanged(int)"),self.changeSliderGreen)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.reject)

        self.setTabOrder(self.redSlider,self.redSpinBox)
        self.setTabOrder(self.redSpinBox,self.greenSlider)
        self.setTabOrder(self.greenSlider,self.greenSpinBox)
        self.setTabOrder(self.greenSpinBox,self.blueSlider)
        self.setTabOrder(self.blueSlider,self.blueSpinBox)
        self.setTabOrder(self.blueSpinBox,self.TransmuteButton)
        self.setTabOrder(self.TransmuteButton,self.transmuteCheckBox)
        self.setTabOrder(self.transmuteCheckBox,self.loadColorsPB)
        self.setTabOrder(self.loadColorsPB,self.saveColorsPB)
        self.setTabOrder(self.saveColorsPB,self.okButton)
        self.setTabOrder(self.okButton,self.cancelButton)


    def languageChange(self):
        self.setCaption(self.__tr("Element Selector"))
        self.elemInfoLabel.setText(QString.null)
        self.elemColorLabel.setText(QString.null)
        self.textLabel2.setText(QString.null)
        self.textLabel2_2.setText(QString.null)
        self.textLabel2_3.setText(QString.null)
        self.pushButton52.setText(self.__tr("Te"))
        self.pushButton35.setText(self.__tr("Br"))
        self.pushButton5.setText(self.__tr("B"))
        self.pushButton17.setText(self.__tr("Cl"))
        self.pushButton32.setText(self.__tr("Ge"))
        self.pushButton51.setText(self.__tr("Sb"))
        self.pushButton2.setText(self.__tr("He"))
        self.pushButton10.setText(self.__tr("Ne"))
        self.pushButton14.setText(self.__tr("Si"))
        self.pushButton33.setText(self.__tr("As"))
        self.pushButton34.setText(self.__tr("Se"))
        self.pushButton36.setText(self.__tr("Kr"))
        self.pushButton1.setText(self.__tr("H"))
        self.pushButton53.setText(self.__tr("I"))
        self.pushButton54.setText(self.__tr("Xe"))
        self.pushButton9.setText(self.__tr("F"))
        self.pushButton16.setText(self.__tr("S"))
        self.pushButton18.setText(self.__tr("Ar"))
        self.pushButton6.setText(self.__tr("C"))
        self.pushButton15.setText(self.__tr("P"))
        self.pushButton7.setText(self.__tr("N"))
        self.pushButton8.setText(self.__tr("O"))
        self.pushButton13.setText(self.__tr("Al"))
        self.loadColorsPB.setText(self.__tr("Load Colors ..."))
        QToolTip.add(self.loadColorsPB,self.__tr("Load element colors from an external text file."))
        self.transmuteCheckBox.setText(self.__tr("Keep Bonds"))
        QToolTip.add(self.transmuteCheckBox,self.__tr("Check if transmuted atoms should keep all existing bonds, even if chemistry is wrong."))
        self.saveColorsPB.setText(self.__tr("Save Colors ..."))
        QToolTip.add(self.saveColorsPB,self.__tr("Save the current color setting for elements in a text file."))
        self.TransmuteButton.setText(self.__tr("Transmute"))
        self.okButton.setText(self.__tr("Ok"))
        self.cancelButton.setText(self.__tr("Cancel"))


    def setElementInfo(self):
        print "ElementSelectorDialog.setElementInfo(): Not implemented yet"

    def transmutePressed(self):
        print "ElementSelectorDialog.transmutePressed(): Not implemented yet"

    def read_element_rgb_table(self):
        print "ElementSelectorDialog.read_element_rgb_table(): Not implemented yet"

    def write_element_rgb_table(self):
        print "ElementSelectorDialog.write_element_rgb_table(): Not implemented yet"

    def changeSliderBlue(self,a0):
        print "ElementSelectorDialog.changeSliderBlue(int): Not implemented yet"

    def ok(self):
        print "ElementSelectorDialog.ok(): Not implemented yet"

    def changeSpinRed(self,a0):
        print "ElementSelectorDialog.changeSpinRed(int): Not implemented yet"

    def changeSliderRed(self,a0):
        print "ElementSelectorDialog.changeSliderRed(int): Not implemented yet"

    def changeSpinBlue(self,a0):
        print "ElementSelectorDialog.changeSpinBlue(int): Not implemented yet"

    def changeSpinGreen(self,a0):
        print "ElementSelectorDialog.changeSpinGreen(int): Not implemented yet"

    def changeSliderGreen(self,a0):
        print "ElementSelectorDialog.changeSliderGreen(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ElementSelectorDialog",s,c)