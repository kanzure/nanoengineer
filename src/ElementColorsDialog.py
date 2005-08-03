# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ElementColorsDialog.ui'
#
# Created: Wed Aug 3 17:42:17 2005
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

        ElementColorsDialogLayout = QVBoxLayout(self,2,4,"ElementColorsDialogLayout")

        self.elementFrame = QFrame(self,"elementFrame")
        self.elementFrame.setSizePolicy(QSizePolicy(5,1,0,0,self.elementFrame.sizePolicy().hasHeightForWidth()))
        self.elementFrame.setMinimumSize(QSize(0,150))
        self.elementFrame.setFrameShape(QFrame.Box)
        self.elementFrame.setFrameShadow(QFrame.Raised)
        ElementColorsDialogLayout.addWidget(self.elementFrame)

        layout12 = QGridLayout(None,1,1,0,6,"layout12")

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setMaximumSize(QSize(40,32767))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout10.addWidget(self.textLabel2)

        self.redSpinBox = QSpinBox(self,"redSpinBox")
        self.redSpinBox.setEnabled(1)
        self.redSpinBox.setSizePolicy(QSizePolicy(1,0,0,0,self.redSpinBox.sizePolicy().hasHeightForWidth()))
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
        self.blueSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.blueSlider.sizePolicy().hasHeightForWidth()))
        self.blueSlider.setPaletteForegroundColor(QColor(0,0,255))
        self.blueSlider.setMaxValue(255)
        self.blueSlider.setOrientation(QSlider.Horizontal)
        self.blueSlider.setTickmarks(QSlider.Above)
        self.blueSlider.setTickInterval(25)

        layout12.addWidget(self.blueSlider,2,1)

        self.redSlider = QSlider(self,"redSlider")
        self.redSlider.setEnabled(1)
        self.redSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.redSlider.sizePolicy().hasHeightForWidth()))
        self.redSlider.setPaletteForegroundColor(QColor(255,0,0))
        self.redSlider.setMaxValue(255)
        self.redSlider.setOrientation(QSlider.Horizontal)
        self.redSlider.setTickmarks(QSlider.Above)
        self.redSlider.setTickInterval(25)

        layout12.addWidget(self.redSlider,0,1)

        self.greenSlider = QSlider(self,"greenSlider")
        self.greenSlider.setEnabled(1)
        self.greenSlider.setSizePolicy(QSizePolicy(5,0,0,0,self.greenSlider.sizePolicy().hasHeightForWidth()))
        self.greenSlider.setPaletteForegroundColor(QColor(0,255,0))
        self.greenSlider.setMaxValue(255)
        self.greenSlider.setOrientation(QSlider.Horizontal)
        self.greenSlider.setTickmarks(QSlider.Above)
        self.greenSlider.setTickInterval(25)

        layout12.addWidget(self.greenSlider,1,1)
        ElementColorsDialogLayout.addLayout(layout12)

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
        ElementColorsDialogLayout.addWidget(self.elementButtonGroup)
        spacer4_2_2_2 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Fixed)
        ElementColorsDialogLayout.addItem(spacer4_2_2_2)

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
        ElementColorsDialogLayout.addLayout(layout12_2)
        spacer4_2_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        ElementColorsDialogLayout.addItem(spacer4_2_2)

        self.languageChange()

        self.resize(QSize(211,513).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.ok)
        self.connect(self.loadColorsPB,SIGNAL("clicked()"),self.read_element_rgb_table)
        self.connect(self.saveColorsPB,SIGNAL("clicked()"),self.write_element_rgb_table)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.defaultButton,SIGNAL("clicked()"),self.loadDefaultProp)
        self.connect(self.alterButton,SIGNAL("clicked()"),self.loadAlterProp)
        self.connect(self.elementButtonGroup,SIGNAL("clicked(int)"),self.setElementInfo)

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

    def __tr(self,s,c = None):
        return qApp.translate("ElementColorsDialog",s,c)
