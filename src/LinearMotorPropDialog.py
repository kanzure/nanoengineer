# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LinearMotorPropDialog.ui'
#
# Created: Mon Sep 27 17:29:23 2004
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

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(204,70,50,20))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(260,70,40,22))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(23,10,41,21))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(70,10,191,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(211,41,42,21))
        self.atomsTextLabel.setMouseTracking(0)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(259,41,85,21))

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setGeometry(QRect(71,70,108,23))

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setGeometry(QRect(71,41,108,23))

        self.forceTextLabel = QLabel(self,"forceTextLabel")
        self.forceTextLabel.setGeometry(QRect(11,41,54,23))
        forceTextLabel_font = QFont(self.forceTextLabel.font())
        self.forceTextLabel.setFont(forceTextLabel_font)
        self.forceTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.stiffnessTextLabel = QLabel(self,"stiffnessTextLabel")
        self.stiffnessTextLabel.setGeometry(QRect(11,70,54,23))
        self.stiffnessTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.groupBox3_3 = QGroupBox(self,"groupBox3_3")
        self.groupBox3_3.setGeometry(QRect(13,99,164,119))

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

        self.czLineEdit = QLineEdit(self.groupBox3_3,"czLineEdit")
        self.czLineEdit.setGeometry(QRect(30,77,123,21))

        self.cxLineEdit = QLineEdit(self.groupBox3_3,"cxLineEdit")
        self.cxLineEdit.setGeometry(QRect(30,23,123,21))
        self.cxLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.cxLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.groupBox3_2_2 = QGroupBox(self,"groupBox3_2_2")
        self.groupBox3_2_2.setGeometry(QRect(183,99,164,119))

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

        self.moveCenterPushButton = QPushButton(self,"moveCenterPushButton")
        self.moveCenterPushButton.setEnabled(0)
        self.moveCenterPushButton.setGeometry(QRect(13,226,164,29))

        self.alignAxiPushButtons = QPushButton(self,"alignAxiPushButtons")
        self.alignAxiPushButtons.setEnabled(0)
        self.alignAxiPushButtons.setGeometry(QRect(183,226,164,29))

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(126,284,108,29))
        self.cancelPushButton.setAutoDefault(1)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(240,284,108,29))
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(310,70,30,22))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(12,284,108,29))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.languageChange()

        self.resize(QSize(359,332).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeLinearMotorColor)
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))

        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.atomsComboBox)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.forceTextLabel.setText(self.__tr("Force:"))
        self.stiffnessTextLabel.setText(self.__tr("Stiffness:"))
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
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("&Apply"))
        self.applyPushButton.setAccel(self.__tr("Alt+A"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))


    def applyButtonPressed(self):
        print "LinearMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def changeLinearMotorColor(self):
        print "LinearMotorPropDialog.changeLinearMotorColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
