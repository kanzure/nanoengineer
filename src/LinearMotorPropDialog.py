# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LinearMotorPropDialog.ui'
#
# Created: Tue Sep 21 10:13:08 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xcc\x49\x44\x41\x54\x78\x9c\xcd\x95\x3b\x0e\x84" \
    "\x30\x0c\x44\xc7\x2b\x0e\xc6\x11\x38\x2a\x87\x71" \
    "\x6a\x1a\x7a\x3a\x44\xf7\xb6\x58\x12\x88\x16\x56" \
    "\x44\x10\x69\x47\x4a\xe1\x7c\xec\xc9\x78\x02\x06" \
    "\xa8\x06\x5e\x55\xb2\xfe\x7d\x62\x33\x23\x84\x90" \
    "\x6b\x0a\xdc\x1e\x92\x90\x84\xbb\x13\xe7\x9a\x52" \
    "\x66\x67\x6b\x80\xcc\x2c\x16\x2a\x4b\xdc\xf7\xfd" \
    "\xe1\x7c\xd7\x75\x32\x33\xb9\x7b\x5e\xe9\x09\x29" \
    "\xf6\x32\x00\xb2\x5a\x3e\xce\xc4\xff\x84\xf7\x63" \
    "\x60\xb3\xdb\x34\x4d\x92\xb6\x06\x95\xc6\xc3\x30" \
    "\x64\xb1\xad\xdd\x24\x13\x7e\xc5\x3c\xcf\x97\x6e" \
    "\xbd\xdf\xd7\xb6\xad\x00\x4b\xae\x18\xc7\xf1\xf4" \
    "\xe0\xb2\x2c\x97\x0a\xec\xf7\x25\xc6\x97\x4e\x5e" \
    "\x04\x60\xd5\x5c\x91\x9a\x17\x42\xe0\x51\xe6\x80" \
    "\xdc\xfd\xcb\x2e\x77\x47\xd2\x38\xbe\xf5\x1f\x04" \
    "\xce\x17\x0f\xd0\x48\x92\xbb\xa7\xa4\x67\xdf\x83" \
    "\x62\x44\xea\x51\x8e\x47\xa5\xa8\x81\x6a\xbf\xa6" \
    "\x37\x5d\x04\x83\x5a\x0e\x5d\x6a\x62\x00\x00\x00" \
    "\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class LinearMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("LinearMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        LayoutWidget = QWidget(self,"layout45")
        LayoutWidget.setGeometry(QRect(10,96,340,219))
        layout45 = QVBoxLayout(LayoutWidget,11,6,"layout45")

        layout42 = QGridLayout(None,1,1,0,6,"layout42")

        layout40 = QHBoxLayout(None,0,6,"layout40")

        self.groupBox3_3 = QGroupBox(LayoutWidget,"groupBox3_3")

        self.textLabel1_4_3_3 = QLabel(self.groupBox3_3,"textLabel1_4_3_3")
        self.textLabel1_4_3_3.setGeometry(QRect(11,77,16,21))

        self.textLabel1_4_2_3 = QLabel(self.groupBox3_3,"textLabel1_4_2_3")
        self.textLabel1_4_2_3.setGeometry(QRect(11,50,16,21))

        self.textLabel1_4_5 = QLabel(self.groupBox3_3,"textLabel1_4_5")
        self.textLabel1_4_5.setGeometry(QRect(11,23,16,21))

        self.cyLineEdit = QLineEdit(self.groupBox3_3,"cyLineEdit")
        self.cyLineEdit.setGeometry(QRect(30,50,123,21))
        self.cyLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cyLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.cxLineEdit = QLineEdit(self.groupBox3_3,"cxLineEdit")
        self.cxLineEdit.setGeometry(QRect(30,23,123,21))
        self.cxLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cxLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.czLineEdit = QLineEdit(self.groupBox3_3,"czLineEdit")
        self.czLineEdit.setGeometry(QRect(30,77,123,21))
        layout40.addWidget(self.groupBox3_3)

        self.groupBox3_2_2 = QGroupBox(LayoutWidget,"groupBox3_2_2")

        self.textLabel1_4_3_2_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_3_2_2")
        self.textLabel1_4_3_2_2.setGeometry(QRect(11,77,16,22))

        self.textLabel1_4_4_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_4_2")
        self.textLabel1_4_4_2.setGeometry(QRect(11,21,16,22))

        self.textLabel1_4_2_2_2 = QLabel(self.groupBox3_2_2,"textLabel1_4_2_2_2")
        self.textLabel1_4_2_2_2.setGeometry(QRect(11,49,16,22))

        self.ayLineEdit = QLineEdit(self.groupBox3_2_2,"ayLineEdit")
        self.ayLineEdit.setGeometry(QRect(30,49,123,22))

        self.azLineEdit = QLineEdit(self.groupBox3_2_2,"azLineEdit")
        self.azLineEdit.setGeometry(QRect(30,77,123,22))

        self.axLineEdit = QLineEdit(self.groupBox3_2_2,"axLineEdit")
        self.axLineEdit.setGeometry(QRect(30,21,123,22))
        self.axLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.axLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout40.addWidget(self.groupBox3_2_2)

        layout42.addLayout(layout40,0,0)

        layout41 = QHBoxLayout(None,0,6,"layout41")

        self.moveCenterPushButton = QPushButton(LayoutWidget,"moveCenterPushButton")
        self.moveCenterPushButton.setEnabled(0)
        layout41.addWidget(self.moveCenterPushButton)

        self.alignAxiPushButtons = QPushButton(LayoutWidget,"alignAxiPushButtons")
        self.alignAxiPushButtons.setEnabled(0)
        layout41.addWidget(self.alignAxiPushButtons)

        layout42.addLayout(layout41,1,0)
        layout45.addLayout(layout42)
        spacer2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout45.addItem(spacer2)

        layout16 = QHBoxLayout(None,0,6,"layout16")

        self.okPushButton = QPushButton(LayoutWidget,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout16.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(LayoutWidget,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        layout16.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(LayoutWidget,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)
        layout16.addWidget(self.applyPushButton)
        layout45.addLayout(layout16)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(204,70,50,20))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(260,70,40,22))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(310,70,30,22))

        LayoutWidget_2 = QWidget(self,"layout37")
        LayoutWidget_2.setGeometry(QRect(210,40,133,23))
        layout37 = QHBoxLayout(LayoutWidget_2,11,6,"layout37")

        self.atomsTextLabel = QLabel(LayoutWidget_2,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        layout37.addWidget(self.atomsTextLabel)

        self.atomsComboBox = QComboBox(0,LayoutWidget_2,"atomsComboBox")
        layout37.addWidget(self.atomsComboBox)

        LayoutWidget_3 = QWidget(self,"layout34")
        LayoutWidget_3.setGeometry(QRect(10,40,170,50))
        layout34 = QGridLayout(LayoutWidget_3,1,1,11,6,"layout34")

        self.stiffnessLineEdit = QLineEdit(LayoutWidget_3,"stiffnessLineEdit")

        layout34.addWidget(self.stiffnessLineEdit,1,1)

        self.forceLineEdit = QLineEdit(LayoutWidget_3,"forceLineEdit")

        layout34.addWidget(self.forceLineEdit,0,1)

        self.forceTextLabel = QLabel(LayoutWidget_3,"forceTextLabel")
        forceTextLabel_font = QFont(self.forceTextLabel.font())
        self.forceTextLabel.setFont(forceTextLabel_font)
        self.forceTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout34.addWidget(self.forceTextLabel,0,0)

        self.stiffnessTextLabel = QLabel(LayoutWidget_3,"stiffnessTextLabel")
        self.stiffnessTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout34.addWidget(self.stiffnessTextLabel,1,0)

        LayoutWidget_4 = QWidget(self,"layout36")
        LayoutWidget_4.setGeometry(QRect(22,9,240,23))
        layout36 = QHBoxLayout(LayoutWidget_4,11,6,"layout36")

        self.nameTextLabel = QLabel(LayoutWidget_4,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout36.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(LayoutWidget_4,"nameLineEdit")
        layout36.addWidget(self.nameLineEdit)

        self.languageChange()

        self.resize(QSize(359,326).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.atomsComboBox)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.groupBox3_3.setTitle(self.__tr("Center Coordinates"))
        self.textLabel1_4_3_3.setText(self.__tr("Z:"))
        self.textLabel1_4_2_3.setText(self.__tr("Y:"))
        self.textLabel1_4_5.setText(self.__tr("X:"))
        self.groupBox3_2_2.setTitle(self.__tr("Axis Vector"))
        self.textLabel1_4_3_2_2.setText(self.__tr("Z:"))
        self.textLabel1_4_4_2.setText(self.__tr("X:"))
        self.textLabel1_4_2_2_2.setText(self.__tr("Y:"))
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
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.forceTextLabel.setText(self.__tr("Force:"))
        self.stiffnessTextLabel.setText(self.__tr("Stiffness:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)


    def applyButtonPressed(self):
        print "LinearMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
