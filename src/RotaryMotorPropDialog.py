# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RotaryMotorPropDialog.ui'
#
# Created: Tue Sep 21 10:13:08 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\xe6\x49\x44\x41\x54\x78\x9c\xb5\x95\xbf\x4b\xf3" \
    "\x40\x1c\xc6\x9f\xbc\x38\x44\x51\x97\x2c\x0e\x2a" \
    "\x28\x17\x0c\x7a\x41\x74\x50\x1c\x85\x5c\x8b\x42" \
    "\x44\x45\x8a\x52\x71\x75\x72\x52\x10\x41\xa7\x53" \
    "\xea\x2f\x8c\xd9\xad\x4b\x9d\x0c\x5d\xa4\x8b\x85" \
    "\x76\x8d\x9b\x42\x24\x83\xf9\x13\x44\x1c\x5c\x02" \
    "\xa5\x7c\xdf\xc9\x60\x6d\xdf\xf7\xed\xfb\xc2\xfb" \
    "\xc0\x41\xc2\x3d\xf7\xc9\x5d\xbe\x3f\x4e\x21\x22" \
    "\xfc\x0f\x75\xb4\x63\x1a\x1d\x1d\x4d\xbe\x1e\x86" \
    "\xa1\xd2\xce\x9a\x1f\xed\xee\x60\x67\x67\xa7\x5d" \
    "\x6b\x33\x38\x9d\x4e\x4b\xd3\x34\x49\x08\x21\x01" \
    "\xa0\x50\x28\x48\xdb\xb6\xe5\xe7\xbc\xa2\x28\xd8" \
    "\xd8\xd8\x90\xe5\x72\x59\x02\x80\x10\x42\xea\xba" \
    "\x4e\xe9\x74\x5a\xe2\xbb\x88\x28\x19\x9c\x73\xf2" \
    "\x3c\x8f\x38\xe7\x94\xcd\x66\xe5\xf8\xf8\x38\xad" \
    "\xaf\xaf\x93\x10\x82\x3c\xcf\x23\x21\x04\xd9\xb6" \
    "\x4d\x9c\x73\x9a\x9f\x9f\x97\x8c\x31\xaa\x56\xab" \
    "\xc4\x18\xa3\xaf\x1c\x22\x6a\x04\x5b\x96\x25\x39" \
    "\xe7\x54\xad\x56\x49\x08\x41\x61\x18\xfe\x72\x08" \
    "\x21\x12\xa8\x65\x59\xf2\xb7\x60\x22\x42\x36\x9b" \
    "\x95\x9f\x50\xcf\xf3\x28\x93\xc9\xd0\xd0\xd0\x10" \
    "\x19\x86\xd1\x12\xee\x79\x5e\x13\x94\x88\xa0\x7c" \
    "\x4d\xb7\x42\xa1\x20\xcf\xce\xce\xf6\x4f\x4e\x4e" \
    "\xf0\xf1\xf1\x81\xf3\xf3\x73\x68\x9a\x06\xdb\xb6" \
    "\x31\x3b\x3b\x9b\xf8\xde\xde\xde\xa0\x69\x1a\x00" \
    "\x60\x61\x61\x01\x51\x14\x35\x65\x4a\x43\xf0\x6e" \
    "\x6f\x6f\x61\x9a\x26\x54\x55\x45\xa9\x54\x42\x57" \
    "\x57\x17\x2e\x2e\x2e\x1a\xa0\xbe\xef\xc3\xb2\x2c" \
    "\xf8\xbe\x0f\x00\xe8\xed\xed\xc5\xda\xda\x5a\x53" \
    "\xf0\x7e\x00\x80\x69\x9a\x64\x9a\x26\x45\x51\xb4" \
    "\xff\xfa\xfa\x8a\xbe\xbe\x3e\xdc\xdf\xdf\x63\x71" \
    "\x71\xb1\xc1\xec\xfb\x3e\x72\xb9\x1c\xba\xbb\xbb" \
    "\xb1\xb5\xb5\x05\xdf\xf7\x71\x73\x73\x83\xf7\xf7" \
    "\xf7\x7d\x5d\xd7\x49\xd7\xf5\xe4\xf8\x1d\x00\x10" \
    "\xc7\x31\xf6\xf6\xf6\x00\x00\x33\x33\x33\x00\x80" \
    "\xce\xce\x4e\xf4\xf7\xf7\x37\x80\x73\xb9\x5c\xf2" \
    "\x5c\xaf\xd7\x71\x74\x74\x84\x52\xa9\x84\x4c\x26" \
    "\xd3\x34\xdf\x01\x00\xaa\xaa\xc2\x71\x1c\xd4\x6a" \
    "\x35\x0c\x0e\x0e\xc2\x75\x5d\xf4\xf4\xf4\xe0\xf9" \
    "\xf9\x19\x63\x63\x63\x89\xf9\xee\xee\x0e\x95\x4a" \
    "\x05\x07\x07\x07\x78\x7c\x7c\x04\x00\x3c\x3c\x3c" \
    "\xa0\x58\x2c\xe2\xe5\xe5\xa5\xf9\x57\x04\x41\xa0" \
    "\x04\x41\xa0\x4c\x4d\x4d\x1d\xaa\xaa\x0a\x00\x98" \
    "\x98\x98\x40\xb1\x58\xc4\xd3\xd3\x53\xc3\x82\x5a" \
    "\xad\x86\xe1\xe1\xe1\xe4\xfd\xf4\xf4\x14\x9a\xa6" \
    "\x1d\x46\x51\xa4\x34\x04\xf1\x7b\x9a\x8c\x8c\x8c" \
    "\x24\xe9\xb4\xb4\xb4\x44\xba\xae\xd3\xe6\xe6\x26" \
    "\xb9\xae\x4b\x2b\x2b\x2b\x34\x30\x30\x40\xdb\xdb" \
    "\xdb\x14\x86\x21\x39\x8e\x43\x86\x61\x34\x15\x47" \
    "\x53\xba\x01\xc0\xdc\xdc\x9c\xac\xd7\xeb\xfb\xae" \
    "\xeb\x02\x00\xca\xe5\x32\x2a\x95\x0a\xe2\x38\x86" \
    "\xaa\xaa\x98\x9e\x9e\xc6\xf2\xf2\x32\x82\x20\xc0" \
    "\xd5\xd5\x15\x26\x27\x27\x0f\x8f\x8f\x8f\x0f\xf0" \
    "\x5d\xbf\xab\xbc\x7c\x3e\xdf\xb2\xea\x1c\xc7\xf9" \
    "\xbb\xca\xfb\x84\x72\xce\x69\x75\x75\x55\x32\xc6" \
    "\x88\x31\x96\x40\x84\x10\x64\x18\x06\x19\x86\x41" \
    "\xbb\xbb\xbb\xed\xf7\x8a\x54\x2a\x25\x39\xe7\x0d" \
    "\x3b\xb8\xbc\xbc\x94\x8c\x31\xca\xe7\xf3\xc4\x18" \
    "\xa3\xeb\xeb\x6b\xf9\xf5\x84\x8c\x31\x4a\xa5\x52" \
    "\x7f\xee\x15\xad\xc6\x57\x70\x3b\xfe\x96\xc1\x6b" \
    "\x25\x5d\xd7\x49\x55\x55\xc4\x71\xdc\xb2\x2f\xb4" \
    "\x52\x5b\xe0\x7f\x51\xdb\x57\xd3\xdf\xea\x27\xa0" \
    "\x80\x81\xd4\x4f\xfd\xdb\x64\x00\x00\x00\x00\x49" \
    "\x45\x4e\x44\xae\x42\x60\x82"

class RotaryMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("RotaryMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        LayoutWidget = QWidget(self,"layout20")
        LayoutWidget.setGeometry(QRect(17,10,210,23))
        layout20 = QHBoxLayout(LayoutWidget,11,6,"layout20")

        self.nameTextLabel = QLabel(LayoutWidget,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout20.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(LayoutWidget,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout20.addWidget(self.nameLineEdit)

        LayoutWidget_2 = QWidget(self,"layout21")
        LayoutWidget_2.setGeometry(QRect(210,40,133,23))
        layout21 = QHBoxLayout(LayoutWidget_2,11,6,"layout21")

        self.atomsTextLabel = QLabel(LayoutWidget_2,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        self.atomsTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout21.addWidget(self.atomsTextLabel)

        self.atomsComboBox = QComboBox(0,LayoutWidget_2,"atomsComboBox")
        layout21.addWidget(self.atomsComboBox)

        LayoutWidget_3 = QWidget(self,"layout25")
        LayoutWidget_3.setGeometry(QRect(10,40,170,50))
        layout25 = QGridLayout(LayoutWidget_3,1,1,11,6,"layout25")

        self.speedLineEdit = QLineEdit(LayoutWidget_3,"speedLineEdit")

        layout25.addWidget(self.speedLineEdit,1,1)

        self.textLabel1_2 = QLabel(LayoutWidget_3,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout25.addWidget(self.textLabel1_2,1,0)

        self.textLabel1 = QLabel(LayoutWidget_3,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout25.addWidget(self.textLabel1,0,0)

        self.torqueLineEdit = QLineEdit(LayoutWidget_3,"torqueLineEdit")

        layout25.addWidget(self.torqueLineEdit,0,1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(204,70,50,20))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(260,70,40,22))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(310,70,30,22))

        LayoutWidget_4 = QWidget(self,"layout45")
        LayoutWidget_4.setGeometry(QRect(10,100,340,219))
        layout45 = QVBoxLayout(LayoutWidget_4,11,6,"layout45")

        layout42 = QGridLayout(None,1,1,0,6,"layout42")

        layout40 = QHBoxLayout(None,0,6,"layout40")

        self.groupBox3 = QGroupBox(LayoutWidget_4,"groupBox3")

        self.textLabel1_4_3 = QLabel(self.groupBox3,"textLabel1_4_3")
        self.textLabel1_4_3.setGeometry(QRect(11,77,16,21))

        self.textLabel1_4_2 = QLabel(self.groupBox3,"textLabel1_4_2")
        self.textLabel1_4_2.setGeometry(QRect(11,50,16,21))

        self.textLabel1_4 = QLabel(self.groupBox3,"textLabel1_4")
        self.textLabel1_4.setGeometry(QRect(11,23,16,21))

        self.cxLineEdit = QLineEdit(self.groupBox3,"cxLineEdit")
        self.cxLineEdit.setGeometry(QRect(30,23,123,21))

        self.cyLineEdit = QLineEdit(self.groupBox3,"cyLineEdit")
        self.cyLineEdit.setGeometry(QRect(30,50,123,21))
        self.cyLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cyLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.czLineEdit = QLineEdit(self.groupBox3,"czLineEdit")
        self.czLineEdit.setGeometry(QRect(30,77,123,21))
        layout40.addWidget(self.groupBox3)

        self.groupBox3_2 = QGroupBox(LayoutWidget_4,"groupBox3_2")

        self.textLabel1_4_3_2 = QLabel(self.groupBox3_2,"textLabel1_4_3_2")
        self.textLabel1_4_3_2.setGeometry(QRect(11,77,16,22))

        self.textLabel1_4_4 = QLabel(self.groupBox3_2,"textLabel1_4_4")
        self.textLabel1_4_4.setGeometry(QRect(11,21,16,22))

        self.textLabel1_4_2_2 = QLabel(self.groupBox3_2,"textLabel1_4_2_2")
        self.textLabel1_4_2_2.setGeometry(QRect(11,49,16,22))

        self.axLineEdit = QLineEdit(self.groupBox3_2,"axLineEdit")
        self.axLineEdit.setGeometry(QRect(30,21,123,22))
        self.axLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.axLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.ayLineEdit = QLineEdit(self.groupBox3_2,"ayLineEdit")
        self.ayLineEdit.setGeometry(QRect(30,49,123,22))

        self.azLineEdit = QLineEdit(self.groupBox3_2,"azLineEdit")
        self.azLineEdit.setGeometry(QRect(30,77,123,22))
        layout40.addWidget(self.groupBox3_2)

        layout42.addLayout(layout40,0,0)

        layout41 = QHBoxLayout(None,0,6,"layout41")

        self.moveCenterPushButton = QPushButton(LayoutWidget_4,"moveCenterPushButton")
        self.moveCenterPushButton.setEnabled(0)
        layout41.addWidget(self.moveCenterPushButton)

        self.alignAxiPushButtons = QPushButton(LayoutWidget_4,"alignAxiPushButtons")
        self.alignAxiPushButtons.setEnabled(0)
        layout41.addWidget(self.alignAxiPushButtons)

        layout42.addLayout(layout41,1,0)
        layout45.addLayout(layout42)
        spacer2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout45.addItem(spacer2)

        layout16 = QHBoxLayout(None,0,6,"layout16")

        self.okPushButton = QPushButton(LayoutWidget_4,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout16.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(LayoutWidget_4,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        layout16.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(LayoutWidget_4,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)
        layout16.addWidget(self.applyPushButton)
        layout45.addLayout(layout16)

        self.languageChange()

        self.resize(QSize(357,329).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))

        self.setTabOrder(self.torqueLineEdit,self.speedLineEdit)
        self.setTabOrder(self.speedLineEdit,self.atomsComboBox)
        self.setTabOrder(self.atomsComboBox,self.alignAxiPushButtons)
        self.setTabOrder(self.alignAxiPushButtons,self.moveCenterPushButton)
        self.setTabOrder(self.moveCenterPushButton,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.textLabel1_2.setText(self.__tr("Speed:"))
        self.textLabel1.setText(self.__tr("Torque:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.groupBox3.setTitle(self.__tr("Center Coordinates"))
        self.textLabel1_4_3.setText(self.__tr("Z:"))
        self.textLabel1_4_2.setText(self.__tr("Y:"))
        self.textLabel1_4.setText(self.__tr("X:"))
        self.groupBox3_2.setTitle(self.__tr("Axis Vector"))
        self.textLabel1_4_3_2.setText(self.__tr("Z:"))
        self.textLabel1_4_4.setText(self.__tr("X:"))
        self.textLabel1_4_2_2.setText(self.__tr("Y:"))
        self.moveCenterPushButton.setText(self.__tr("Move Center"))
        self.moveCenterPushButton.setAccel(QString.null)
        self.alignAxiPushButtons.setText(self.__tr("Align Axis"))
        self.alignAxiPushButtons.setAccel(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("&Apply"))
        self.applyPushButton.setAccel(self.__tr("Alt+A"))


    def applyButtonPressed(self):
        print "RotaryMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("RotaryMotorPropDialog",s,c)
