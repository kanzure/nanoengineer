# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LinearMotorPropDialog.ui'
#
# Created: Fri Dec 24 03:16:43 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 11 1",
". c None",
"# c #000000",
"i c #a8a8a8",
"c c #b0b0b0",
"h c #b8b8b8",
"g c #c0c0c0",
"f c #cacaca",
"a c #d4d4d4",
"e c #dfdfdf",
"d c #efefef",
"b c #ffffff",
"......................",
"......................",
"......................",
".................#a...",
".................##a..",
"...........#######b#..",
"...........cccccc##a..",
".................#a...",
"......................",
".###.###.###.###.###..",
".#d###d###d###d###e##.",
".#aaaaaffffffffffggg#.",
".#hhhhhhhcccccccccci#.",
".####################.",
"......................",
"..a#..................",
".a##..................",
".#b#######............",
".a##cccccc............",
"..a#..................",
"......................",
"......................"
]

class LinearMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

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

        self.resize(QSize(599,544).expandedTo(self.minimumSizeHint()))
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
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)

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
