# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/LinearMotorPropDialog.ui'
#
# Created: Thu Dec 9 14:44:27 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xeb\x49\x44\x41\x54\x78\x9c\xcd\x94\x31\x0e\x83" \
    "\x30\x0c\x45\xbf\xab\xce\x1e\x39\x85\x4f\x90\x89" \
    "\x91\x91\xa3\x72\x0a\x9f\xc0\x3b\x0b\x13\x0b\x52" \
    "\x06\xc4\xe6\x0e\x6d\x69\xaa\x36\x15\x69\x41\xea" \
    "\x97\x32\x44\xb1\x5f\x7e\x12\x3b\xa4\xaa\x38\x42" \
    "\xa7\x43\xa8\x7f\x0f\x0e\x21\x38\x33\xfb\xee\x60" \
    "\x00\x10\x11\xa4\xf0\x73\xa9\xb3\xdc\x9a\xbb\x83" \
    "\x88\x70\x2f\x06\x2a\xa9\x8a\x71\x1c\xdf\x82\xdb" \
    "\xb6\x05\x00\x98\x19\x62\x8c\x04\x14\x3a\xae\xaa" \
    "\x8a\x72\x86\x53\x28\x50\xe8\xb8\x48\x37\xb0\xdf" \
    "\xc7\x1e\x73\x55\x7d\x80\xa7\x69\xf2\x34\xa0\x74" \
    "\xde\xf7\xfd\x13\x9c\x54\x15\x21\x04\x37\xb3\x97" \
    "\xd3\xcc\xf3\xbc\xe9\xd4\x69\x5c\x5d\xd7\x50\x55" \
    "\x5a\x1f\x6f\x18\x86\x6c\xe2\xb2\x2c\x9b\x36\x48" \
    "\xe3\x56\x70\xd3\x34\x9b\x92\xb7\xea\xb0\xaa\x58" \
    "\x5b\x9a\x99\xfd\x53\x67\x7d\x05\x66\x66\x17\x91" \
    "\xbd\x98\x00\x6e\x77\x2c\x22\x6b\xaf\xe7\x5c\xab" \
    "\x6a\xae\xeb\xf2\x60\x33\x03\xd1\x35\xaf\xeb\xba" \
    "\x1f\xbd\x26\xe0\x18\x23\x99\x99\x8b\xc8\xa7\xff" \
    "\xa0\x48\xc7\x57\xc5\xde\xba\x00\x34\x42\x9d\xc7" \
    "\x1b\xf2\x3c\xce\x00\x00\x00\x00\x49\x45\x4e\x44" \
    "\xae\x42\x60\x82"

class LinearMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("LinearMotorPropDialog")

        self.setSizePolicy(QSizePolicy(5,5,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        LinearMotorPropDialogLayout = QVBoxLayout(self,11,7,"LinearMotorPropDialogLayout")

        layout52 = QHBoxLayout(None,0,6,"layout52")

        layout50 = QHBoxLayout(None,0,6,"layout50")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout50.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)
        layout50.addWidget(self.nameLineEdit)
        layout52.addLayout(layout50)

        layout51 = QHBoxLayout(None,0,6,"layout51")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout51.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(30,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)
        layout51.addWidget(self.colorPixmapLabel)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout51.addWidget(self.colorSelectorPushButton)
        layout52.addLayout(layout51)
        LinearMotorPropDialogLayout.addLayout(layout52)

        layout55 = QHBoxLayout(None,0,6,"layout55")

        layout53 = QGridLayout(None,1,1,0,6,"layout53")

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout53.addMultiCellWidget(self.forceLineEdit,0,0,1,2)

        self.stiffnessTextLabel = QLabel(self,"stiffnessTextLabel")
        self.stiffnessTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout53.addWidget(self.stiffnessTextLabel,1,0)

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout53.addMultiCellWidget(self.stiffnessLineEdit,1,1,1,2)

        self.textLabel3_4_2 = QLabel(self,"textLabel3_4_2")

        layout53.addWidget(self.textLabel3_4_2,1,3)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")

        layout53.addWidget(self.atomsComboBox,2,1)

        self.textLabel3_4 = QLabel(self,"textLabel3_4")

        layout53.addWidget(self.textLabel3_4,0,3)

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        self.atomsTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout53.addWidget(self.atomsTextLabel,2,0)

        self.forceTextLabel = QLabel(self,"forceTextLabel")
        forceTextLabel_font = QFont(self.forceTextLabel.font())
        self.forceTextLabel.setFont(forceTextLabel_font)
        self.forceTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout53.addWidget(self.forceTextLabel,0,0)

        self.textLabel3_4_2_2 = QLabel(self,"textLabel3_4_2_2")

        layout53.addWidget(self.textLabel3_4_2_2,2,2)
        layout55.addLayout(layout53)

        layout54 = QGridLayout(None,1,1,0,6,"layout54")

        self.lengthLineEdit = QLineEdit(self,"lengthLineEdit")
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout54.addWidget(self.lengthLineEdit,0,1)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout54.addWidget(self.textLabel1,0,0)

        self.textLabel3_3 = QLabel(self,"textLabel3_3")

        layout54.addWidget(self.textLabel3_3,2,2)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")

        layout54.addWidget(self.textLabel3_2,1,2)

        self.widthLineEdit = QLineEdit(self,"widthLineEdit")
        self.widthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout54.addWidget(self.widthLineEdit,1,1)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout54.addWidget(self.textLabel1_2_2,2,0)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout54.addWidget(self.textLabel1_2,1,0)

        self.textLabel3 = QLabel(self,"textLabel3")

        layout54.addWidget(self.textLabel3,0,2)

        self.sradiusLineEdit = QLineEdit(self,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout54.addWidget(self.sradiusLineEdit,2,1)
        layout55.addLayout(layout54)
        LinearMotorPropDialogLayout.addLayout(layout55)

        layout52_2 = QHBoxLayout(None,0,14,"layout52_2")

        self.groupBox3_3 = QGroupBox(self,"groupBox3_3")
        self.groupBox3_3.setMinimumSize(QSize(0,115))
        self.groupBox3_3.setAlignment(QGroupBox.AlignVCenter)

        self.cxLineEdit = QLineEdit(self.groupBox3_3,"cxLineEdit")
        self.cxLineEdit.setGeometry(QRect(83,41,130,24))
        self.cxLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cxLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.cxLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.cyLineEdit = QLineEdit(self.groupBox3_3,"cyLineEdit")
        self.cyLineEdit.setGeometry(QRect(80,90,130,24))
        self.cyLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cyLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.cyLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.czLineEdit = QLineEdit(self.groupBox3_3,"czLineEdit")
        self.czLineEdit.setGeometry(QRect(80,140,130,24))
        self.czLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.textLabel1_4_5 = QLabel(self.groupBox3_3,"textLabel1_4_5")
        self.textLabel1_4_5.setGeometry(QRect(51,41,16,24))

        self.textLabel1_4_3_3 = QLabel(self.groupBox3_3,"textLabel1_4_3_3")
        self.textLabel1_4_3_3.setGeometry(QRect(51,141,16,24))

        self.textLabel1_4_2_3 = QLabel(self.groupBox3_3,"textLabel1_4_2_3")
        self.textLabel1_4_2_3.setGeometry(QRect(51,91,16,24))
        layout52_2.addWidget(self.groupBox3_3)

        self.groupBox3_2_2 = QGroupBox(self,"groupBox3_2_2")
        self.groupBox3_2_2.setMinimumSize(QSize(0,115))
        self.groupBox3_2_2.setAlignment(QGroupBox.AlignVCenter)

        self.axLineEdit = QLineEdit(self.groupBox3_2_2,"axLineEdit")
        self.axLineEdit.setGeometry(QRect(83,41,140,24))
        self.axLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.axLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.axLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.ayLineEdit = QLineEdit(self.groupBox3_2_2,"ayLineEdit")
        self.ayLineEdit.setGeometry(QRect(83,91,140,24))
        self.ayLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.azLineEdit = QLineEdit(self.groupBox3_2_2,"azLineEdit")
        self.azLineEdit.setGeometry(QRect(80,140,140,24))
        self.azLineEdit.setAlignment(QLineEdit.AlignLeft)

        self.textLabel1_4_2_2_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_2_2_2")
        self.textLabel1_4_2_2_2.setGeometry(QRect(51,91,16,24))

        self.textLabel1_4_3_2_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_3_2_2")
        self.textLabel1_4_3_2_2.setGeometry(QRect(51,141,16,24))

        self.textLabel1_4_4_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_4_2")
        self.textLabel1_4_4_2.setGeometry(QRect(51,41,16,24))
        layout52_2.addWidget(self.groupBox3_2_2)
        LinearMotorPropDialogLayout.addLayout(layout52_2)

        layout48 = QHBoxLayout(None,5,36,"layout48")

        self.moveCenterPushButton = QPushButton(self,"moveCenterPushButton")
        self.moveCenterPushButton.setEnabled(0)
        layout48.addWidget(self.moveCenterPushButton)

        self.alignAxiPushButtons = QPushButton(self,"alignAxiPushButtons")
        self.alignAxiPushButtons.setEnabled(0)
        layout48.addWidget(self.alignAxiPushButtons)
        LinearMotorPropDialogLayout.addLayout(layout48)
        spacer10 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        LinearMotorPropDialogLayout.addItem(spacer10)

        layout49 = QHBoxLayout(None,4,31,"layout49")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout49.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        layout49.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)
        layout49.addWidget(self.applyPushButton)
        LinearMotorPropDialogLayout.addLayout(layout49)

        self.languageChange()

        self.resize(QSize(599,541).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.forceLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.stiffnessLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.axLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.ayLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.azLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.cxLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.cyLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.czLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeLinearMotorColor)

        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.atomsComboBox)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.stiffnessTextLabel.setText(self.__tr("Stiffness:"))
        self.textLabel3_4_2.setText(self.__tr("N/m"))
        self.textLabel3_4.setText(self.__tr("pN"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.forceTextLabel.setText(self.__tr("Force:"))
        self.textLabel3_4_2_2.setText(QString.null)
        self.textLabel1.setText(self.__tr("Motor Length:"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel1_2_2.setText(self.__tr("Spoke Radius:"))
        self.textLabel1_2.setText(self.__tr("Motor Width:"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.groupBox3_3.setTitle(self.__tr("Center Coordinates"))
        self.textLabel1_4_5.setText(self.__tr("X:"))
        self.textLabel1_4_3_3.setText(self.__tr("Z:"))
        self.textLabel1_4_2_3.setText(self.__tr("Y:"))
        self.groupBox3_2_2.setTitle(self.__tr("Axis Vector"))
        self.textLabel1_4_2_2_2.setText(self.__tr("Y:"))
        self.textLabel1_4_3_2_2.setText(self.__tr("Z:"))
        self.textLabel1_4_4_2.setText(self.__tr("X:"))
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
        print "LinearMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def propertyChanged(self):
        print "LinearMotorPropDialog.propertyChanged(): Not implemented yet"

    def changeLinearMotorColor(self):
        print "LinearMotorPropDialog.changeLinearMotorColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
