# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LinearMotorPropDialog.ui'
#
# Created: Mon Jan 31 14:42:21 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 12 1",
". c None",
"a c #404040",
"# c #000000",
"j c #a8a8a8",
"i c #b0b0b0",
"h c #b8b8b8",
"g c #c0c0c0",
"f c #cacaca",
"e c #d4d4d4",
"d c #dfdfdf",
"c c #efefef",
"b c #ffffff",
"......................",
"......................",
"......................",
".................#a...",
".................##a..",
"...........#######b#..",
"...........aaaaaa##a..",
".................#a...",
"......................",
".###.###.###.###.###..",
".#c###c###c###c###d##.",
".#eeeeeffffffffffggg#.",
".#hhhhhhhiiiiiiiiiij#.",
".####################.",
"......................",
"..a#..................",
".a##..................",
".#b#######............",
".a##aaaaaa............",
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

        LinearMotorPropDialogLayout = QVBoxLayout(self,11,6,"LinearMotorPropDialogLayout")

        layout37 = QGridLayout(None,1,1,0,6,"layout37")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout37.addWidget(self.nameTextLabel,0,0)

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout37.addWidget(self.stiffnessLineEdit,2,1)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)

        layout37.addWidget(self.nameLineEdit,0,1)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout37.addWidget(self.textLabel2,2,2)

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout37.addWidget(self.textLabel1_4,1,2)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout37.addWidget(self.textLabel1,1,0)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout37.addWidget(self.textLabel1_2,2,0)

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout37.addWidget(self.forceLineEdit,1,1)

        self.textLabel4 = QLabel(self,"textLabel4")

        layout37.addWidget(self.textLabel4,0,2)
        LinearMotorPropDialogLayout.addLayout(layout37)

        layout38 = QGridLayout(None,1,1,0,6,"layout38")

        self.sradiusLineEdit = QLineEdit(self,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout38.addWidget(self.sradiusLineEdit,2,1)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")

        layout38.addWidget(self.textLabel3_2,1,2)

        self.widthLineEdit = QLineEdit(self,"widthLineEdit")
        self.widthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout38.addWidget(self.widthLineEdit,1,1)

        self.textLabel1_2_2_2 = QLabel(self,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout38.addWidget(self.textLabel1_2_2_2,2,0)

        self.lengthLineEdit = QLineEdit(self,"lengthLineEdit")
        self.lengthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.lengthLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout38.addWidget(self.lengthLineEdit,0,1)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout38.addWidget(self.textLabel1_2_2,1,0)

        self.textLabel3_3 = QLabel(self,"textLabel3_3")

        layout38.addWidget(self.textLabel3_3,2,2)

        self.textLabel3 = QLabel(self,"textLabel3")

        layout38.addWidget(self.textLabel3,0,2)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout38.addWidget(self.textLabel1_3,0,0)
        LinearMotorPropDialogLayout.addLayout(layout38)

        layout39 = QHBoxLayout(None,0,6,"layout39")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout39.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)
        layout39.addWidget(self.colorPixmapLabel)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout39.addWidget(self.colorSelectorPushButton)
        LinearMotorPropDialogLayout.addLayout(layout39)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout11.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        layout11.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)
        layout11.addWidget(self.applyPushButton)
        LinearMotorPropDialogLayout.addLayout(layout11)

        self.languageChange()

        self.resize(QSize(338,327).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.forceLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.stiffnessLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeColor)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)

        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(self.__tr("N/m"))
        self.textLabel1_4.setText(self.__tr("pN"))
        self.textLabel1.setText(self.__tr("Force:"))
        self.textLabel1_2.setText(self.__tr("Stiffness"))
        self.textLabel4.setText(QString.null)
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius:"))
        self.textLabel1_2_2.setText(self.__tr("Motor Width:"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.textLabel1_3.setText(self.__tr("Motor Length:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
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

    def changeColor(self):
        print "LinearMotorPropDialog.changeColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
