# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\ElementColorsDialog.ui'
#
# Created: Wed Feb 15 18:03:10 2006
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

        ElementColorsDialogLayout = QGridLayout(self,1,1,2,4,"ElementColorsDialogLayout")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(0,150))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)

        ElementColorsDialogLayout.addWidget(self.elementFrame,0,0)

        layout12 = QGridLayout(None,1,1,0,6,"layout12")

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setMaximumSize(QSize(40,32767))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout10.addWidget(self.textLabel2)

        self.redSpinBox = QSpinBox(self,"redSpinBox")
        self.redSpinBox.setEnabled(1)
        self.redSpinBox.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.redSpinBox.sizePolicy().hasHeightForWidth()))
        self.redSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.redSpinBox.setMaxValue(255)
        layout10.addWidget(self.redSpinBox)

        layout12.addLayout(layout10,0,0)

        layout10_2 = QHBoxLayout(None,0,6,"layout10_2")

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        self.textLabel2_2.setMaximumSize(QSize(40,32767))
        self.textLabel2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout10_2.addWidget(self.textLabel2_2)

        self.greenSpinBox = QSpinBox(self,"greenSpinBox")
        self.greenSpinBox.setEnabled(1)
        self.greenSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.greenSpinBox.setMaxValue(255)
        layout10_2.addWidget(self.greenSpinBox)

        layout12.addLayout(layout10_2,1,0)

        layout10_3 = QHBoxLayout(None,0,6,"layout10_3")

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        self.textLabel2_3.setMaximumSize(QSize(40,32767))
        self.textLabel2_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout10_3.addWidget(self.textLabel2_3)

        self.blueSpinBox = QSpinBox(self,"blueSpinBox")
        self.blueSpinBox.setEnabled(1)
        self.blueSpinBox.setFocusPolicy(QSpinBox.ClickFocus)
        self.blueSpinBox.setMaxValue(255)
        layout10_3.addWidget(self.blueSpinBox)

        layout12.addLayout(layout10_3,2,0)

        self.blueSlider = QSlider(self,"blueSlider")
        self.blueSlider.setEnabled(1)
        self.blueSlider.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.blueSlider.sizePolicy().hasHeightForWidth()))
        self.blueSlider.setPaletteForegroundColor(QColor(0,0,255))
        self.blueSlider.setMaxValue(255)
        self.blueSlider.setOrientation(QSlider.Horizontal)
        self.blueSlider.setTickmarks(QSlider.Above)
        self.blueSlider.setTickInterval(25)

        layout12.addWidget(self.blueSlider,2,1)

        self.redSlider = QSlider(self,"redSlider")
        self.redSlider.setEnabled(1)
        self.redSlider.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.redSlider.sizePolicy().hasHeightForWidth()))
        self.redSlider.setPaletteForegroundColor(QColor(255,0,0))
        self.redSlider.setMaxValue(255)
        self.redSlider.setOrientation(QSlider.Horizontal)
        self.redSlider.setTickmarks(QSlider.Above)
        self.redSlider.setTickInterval(25)

        layout12.addWidget(self.redSlider,0,1)

        self.greenSlider = QSlider(self,"greenSlider")
        self.greenSlider.setEnabled(1)
        self.greenSlider.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,0,0,self.greenSlider.sizePolicy().hasHeightForWidth()))
        self.greenSlider.setPaletteForegroundColor(QColor(0,255,0))
        self.greenSlider.setMaxValue(255)
        self.greenSlider.setOrientation(QSlider.Horizontal)
        self.greenSlider.setTickmarks(QSlider.Above)
        self.greenSlider.setTickInterval(25)

        layout12.addWidget(self.greenSlider,1,1)

        ElementColorsDialogLayout.addLayout(layout12,1,0)
        spacer4_2_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        ElementColorsDialogLayout.addItem(spacer4_2_2,6,0)

        self.elementButtonGroup = QButtonGroup(self,"elementButtonGroup")
        self.elementButtonGroup.setMinimumSize(QSize(0,126))
        self.elementButtonGroup.setFrameShape(QButtonGroup.StyledPanel)
        self.elementButtonGroup.setFrameShadow(QButtonGroup.Plain)
        self.elementButtonGroup.setLineWidth(1)
        self.elementButtonGroup.setExclusive(1)
        self.elementButtonGroup.setColumnLayout(0,Qt.Vertical)
        self.elementButtonGroup.layout().setSpacing(0)
        self.elementButtonGroup.layout().setMargin(2)
        elementButtonGroupLayout = QGridLayout(self.elementButtonGroup.layout())
        elementButtonGroupLayout.setAlignment(Qt.AlignTop)

        self.toolButton6 = QToolButton(self.elementButtonGroup,"toolButton6")
        self.toolButton6.setMinimumSize(QSize(30,30))
        self.toolButton6.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton6,6)

        elementButtonGroupLayout.addWidget(self.toolButton6,1,1)

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

        self.toolButton7 = QToolButton(self.elementButtonGroup,"toolButton7")
        self.toolButton7.setMinimumSize(QSize(30,30))
        self.toolButton7.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton7,7)

        elementButtonGroupLayout.addWidget(self.toolButton7,1,2)

        self.toolButton2 = QToolButton(self.elementButtonGroup,"toolButton2")
        self.toolButton2.setMinimumSize(QSize(30,30))
        self.toolButton2.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton2,2)

        elementButtonGroupLayout.addWidget(self.toolButton2,0,5)

        self.toolButton1 = QToolButton(self.elementButtonGroup,"toolButton1")
        self.toolButton1.setMinimumSize(QSize(30,30))
        self.toolButton1.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton1,1)

        elementButtonGroupLayout.addWidget(self.toolButton1,0,4)

        self.toolButton0 = QToolButton(self.elementButtonGroup,"toolButton0")
        self.toolButton0.setMinimumSize(QSize(30,30))
        self.toolButton0.setToggleButton(1)
        self.elementButtonGroup.insert( self.toolButton0,0)

        elementButtonGroupLayout.addWidget(self.toolButton0,0,3)

        ElementColorsDialogLayout.addWidget(self.elementButtonGroup,3,0)

        layout12_2 = QGridLayout(None,1,1,0,6,"layout12_2")

        self.saveColorsPB = QPushButton(self,"saveColorsPB")
        self.saveColorsPB.setAutoDefault(0)

        layout12_2.addWidget(self.saveColorsPB,0,1)

        self.defaultButton = QPushButton(self,"defaultButton")
        self.defaultButton.setAutoDefault(0)

        layout12_2.addWidget(self.defaultButton,1,0)

        self.loadColorsPB = QPushButton(self,"loadColorsPB")
        self.loadColorsPB.setAutoDefault(0)

        layout12_2.addWidget(self.loadColorsPB,0,0)

        self.cancelButton = QPushButton(self,"cancelButton")
        self.cancelButton.setAutoDefault(0)

        layout12_2.addWidget(self.cancelButton,2,1)

        self.alterButton = QPushButton(self,"alterButton")
        self.alterButton.setAutoDefault(0)

        layout12_2.addWidget(self.alterButton,1,1)

        self.okButton = QPushButton(self,"okButton")
        self.okButton.setAutoDefault(0)
        self.okButton.setDefault(0)

        layout12_2.addWidget(self.okButton,2,0)

        ElementColorsDialogLayout.addLayout(layout12_2,5,0)
        spacer4_2_2_2 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Fixed)
        ElementColorsDialogLayout.addItem(spacer4_2_2_2,4,0)

        layout7 = QHBoxLayout(None,0,6,"layout7")
        spacer3 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout7.addItem(spacer3)

        self.previewPB = QPushButton(self,"previewPB")
        self.previewPB.setAutoDefault(0)
        layout7.addWidget(self.previewPB)

        self.restorePB = QPushButton(self,"restorePB")
        self.restorePB.setAutoDefault(0)
        layout7.addWidget(self.restorePB)

        ElementColorsDialogLayout.addLayout(layout7,2,0)

        self.languageChange()

        self.resize(QSize(230,548).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.ok)
        self.connect(self.loadColorsPB,SIGNAL("clicked()"),self.read_element_rgb_table)
        self.connect(self.saveColorsPB,SIGNAL("clicked()"),self.write_element_rgb_table)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.reject)
        self.connect(self.defaultButton,SIGNAL("clicked()"),self.loadDefaultProp)
        self.connect(self.alterButton,SIGNAL("clicked()"),self.loadAlterProp)
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)
        self.connect(self.previewPB,SIGNAL("clicked()"),self.preview_color_change)
        self.connect(self.restorePB,SIGNAL("clicked()"),self.restore_current_color)

        self.setTabOrder(self.loadColorsPB,self.saveColorsPB)
        self.setTabOrder(self.saveColorsPB,self.defaultButton)
        self.setTabOrder(self.defaultButton,self.alterButton)
        self.setTabOrder(self.alterButton,self.okButton)
        self.setTabOrder(self.okButton,self.cancelButton)


    def languageChange(self):
        self.setCaption(self.__tr("Element Color Settings"))
        self.textLabel2.setText(self.__tr("Red:"))
        self.textLabel2_2.setText(self.__tr("Green:"))
        self.textLabel2_3.setText(self.__tr("Blue:"))
        self.elementButtonGroup.setTitle(QString.null)
        self.toolButton6.setText(self.__tr("C"))
        QToolTip.add(self.toolButton6,self.__tr("Carbon"))
        self.toolButton8.setText(self.__tr("O"))
        QToolTip.add(self.toolButton8,self.__tr("Oxygen"))
        self.toolButton10.setText(self.__tr("Ne"))
        QToolTip.add(self.toolButton10,self.__tr("Neon"))
        self.toolButton9.setText(self.__tr("F"))
        QToolTip.add(self.toolButton9,self.__tr("Fluorine"))
        self.toolButton13.setText(self.__tr("Al"))
        QToolTip.add(self.toolButton13,self.__tr("Aluminum"))
        self.toolButton17.setText(self.__tr("Cl"))
        QToolTip.add(self.toolButton17,self.__tr("Chlorine"))
        self.toolButton5.setText(self.__tr("B"))
        QToolTip.add(self.toolButton5,self.__tr("Boron"))
        self.toolButton10_2.setText(self.__tr("Ar"))
        QToolTip.add(self.toolButton10_2,self.__tr("Argon"))
        self.toolButton15.setText(self.__tr("P"))
        QToolTip.add(self.toolButton15,self.__tr("Phosphorus"))
        self.toolButton16.setText(self.__tr("S"))
        QToolTip.add(self.toolButton16,self.__tr("Sulfur"))
        self.toolButton14.setText(self.__tr("Si"))
        QToolTip.add(self.toolButton14,self.__tr("Silicon"))
        self.toolButton33.setText(self.__tr("As"))
        QToolTip.add(self.toolButton33,self.__tr("Arsenic"))
        self.toolButton34.setText(self.__tr("Se"))
        QToolTip.add(self.toolButton34,self.__tr("Selenium"))
        self.toolButton35.setText(self.__tr("Br"))
        QToolTip.add(self.toolButton35,self.__tr("Bromine"))
        self.toolButton36.setText(self.__tr("Kr"))
        QToolTip.add(self.toolButton36,self.__tr("Krypton"))
        self.toolButton32.setText(self.__tr("Ge"))
        QToolTip.add(self.toolButton32,self.__tr("Germanium"))
        self.toolButton7.setText(self.__tr("N"))
        QToolTip.add(self.toolButton7,self.__tr("Nitrogen"))
        self.toolButton2.setText(self.__tr("He"))
        QToolTip.add(self.toolButton2,self.__tr("Helium"))
        self.toolButton1.setText(self.__tr("H"))
        QToolTip.add(self.toolButton1,self.__tr("Hydrogen"))
        self.toolButton0.setText(self.__tr("X"))
        QToolTip.add(self.toolButton0,self.__tr("Bondpoint"))
        self.saveColorsPB.setText(self.__tr("Save Colors ..."))
        QToolTip.add(self.saveColorsPB,self.__tr("Save the current element color settings to a file"))
        QWhatsThis.add(self.saveColorsPB,self.__tr("Save the current color settings for elements in a text file."))
        self.defaultButton.setText(self.__tr("Restore Defaults"))
        QToolTip.add(self.defaultButton,self.__tr("Restore current element colors to the default colors."))
        QWhatsThis.add(self.defaultButton,self.__tr("Restore current element colors to the default colors."))
        self.loadColorsPB.setText(self.__tr("Load Colors ..."))
        QToolTip.add(self.loadColorsPB,self.__tr("Load element colors from file"))
        QWhatsThis.add(self.loadColorsPB,self.__tr("Load element colors from an external text file."))
        self.cancelButton.setText(self.__tr("Cancel"))
        self.alterButton.setText(self.__tr("Set To Alternate"))
        QToolTip.add(self.alterButton,self.__tr("Set element colors to the alternate color set"))
        QWhatsThis.add(self.alterButton,self.__tr("Set element colors to the alternate color set."))
        self.okButton.setText(self.__tr("Ok"))
        self.previewPB.setText(self.__tr("Preview"))
        self.restorePB.setText(self.__tr("Restore"))


    def setElementInfo(self,a0):
        print "ElementColorsDialog.setElementInfo(int): Not implemented yet"

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

    def changeDisplayMode(self,a0):
        print "ElementColorsDialog.changeDisplayMode(int): Not implemented yet"

    def preview_color_change(self):
        print "ElementColorsDialog.preview_color_change(): Not implemented yet"

    def restore_current_color(self):
        print "ElementColorsDialog.restore_current_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ElementColorsDialog",s,c)
