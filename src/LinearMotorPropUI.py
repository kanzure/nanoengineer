# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LinearMotorPropUI.ui'
#
# Created: Mon Sep 20 18:32:19 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 10 1",
"# c #000000",
"h c #a8a8a8",
"b c #b0b0b0",
"g c #b8b8b8",
"f c #c0c0c0",
"e c #cacaca",
"a c #d4d4d4",
"d c #dfdfdf",
"c c #efefef",
". c #ffffff",
"......................",
"......................",
"......................",
".................#a...",
".................##a..",
"...........#######.#..",
"...........bbbbbb##a..",
".................#a...",
"......................",
".###.###.###.###.###..",
".#c###c###c###c###d##.",
".#aaaaaeeeeeeeeeefff#.",
".#gggggggbbbbbbbbbbh#.",
".####################.",
"......................",
"..a#..................",
".a##..................",
".#.#######............",
".a##bbbbbb............",
"..a#..................",
"......................",
"......................"
]

class LinearMotorPropForm(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("LinearMotorPropForm")

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
        print "LinearMotorPropForm.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropForm",s,c)
