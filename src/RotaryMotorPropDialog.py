# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\RotaryMotorPropDialog.ui'
#
# Created: Mon Sep 27 12:36:54 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 60 1",
". c None",
"F c #070707",
"M c #0a0a0a",
"S c #101010",
"L c #131313",
"J c #161616",
"1 c #1d1d1d",
"O c #1f1f1f",
"u c #212121",
"P c #222222",
"j c #242424",
"X c #252525",
"I c #272727",
"v c #282828",
"# c #292929",
"g c #2a2a2a",
"c c #2c2c2c",
"w c #2d2d2d",
"m c #2f2f2f",
"G c #323232",
"z c #353535",
"E c #3f3f3f",
"d c #444444",
"o c #454545",
"b c #464646",
"N c #474747",
"A c #484848",
"q c #4a4a4a",
"f c #4c4c4c",
"p c #4d4d4d",
"W c #515151",
"0 c #545454",
"t c #565656",
"H c #585858",
"D c #5a5a5a",
"l c #5b5b5b",
"n c #5c5c5c",
"h c #5d5d5d",
"Y c #676767",
"2 c #737373",
"5 c #777777",
"Q c #7f7f7f",
"4 c #848484",
"V c #8e8e8e",
"K c #8f8f8f",
"3 c #909090",
"Z c #919191",
"R c #939393",
"B c #959595",
"a c #9d9d9d",
"T c #9e9e9e",
"e c #a2a2a2",
"U c #a6a6a6",
"y c #a9a9a9",
"k c #ababab",
"x c #b6b6b6",
"i c #b9b9b9",
"r c #bebebe",
"C c #c3c3c3",
"s c #d6d6d6",
"......................",
".........###..........",
".........#a#..........",
"...bcd.ef#aghi.djb....",
"...ckclmnokopcqjrj....",
"...dcrosssssssorjd....",
"....losktuvssssok.....",
"...ewxyzABsssCssj.....",
"...fDrhEssssaFasGH....",
".ccIosJKsssajLMasNjj..",
".jaassOksssjjLFPsaaj..",
".ccIoscQssssRSssTqjj..",
"...hpshcUsssVGssvh....",
"....IssWXYZ012sKv.....",
"....Aoss3pop4syo5.....",
"...dcroasssssKorjd....",
"...crcHjjorovv5jrj....",
"...bcd..3jajT..djb....",
".........jaj..........",
".........jcj..........",
"......................",
"......................"
]

class RotaryMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("RotaryMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(204,70,50,20))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(211,41,42,21))
        self.atomsTextLabel.setMouseTracking(0)
        self.atomsTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(259,41,83,21))

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(18,11,41,21))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(65,11,161,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.speedLineEdit = QLineEdit(self,"speedLineEdit")
        self.speedLineEdit.setGeometry(QRect(65,68,114,21))

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setGeometry(QRect(11,68,48,21))
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(11,41,48,21))
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.torqueLineEdit = QLineEdit(self,"torqueLineEdit")
        self.torqueLineEdit.setGeometry(QRect(65,41,114,21))

        self.groupBox3 = QGroupBox(self,"groupBox3")
        self.groupBox3.setGeometry(QRect(13,103,164,121))

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

        self.groupBox3_2 = QGroupBox(self,"groupBox3_2")
        self.groupBox3_2.setGeometry(QRect(183,103,164,121))

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

        self.moveCenterPushButton = QPushButton(self,"moveCenterPushButton")
        self.moveCenterPushButton.setEnabled(0)
        self.moveCenterPushButton.setGeometry(QRect(13,232,164,27))

        self.alignAxiPushButtons = QPushButton(self,"alignAxiPushButtons")
        self.alignAxiPushButtons.setEnabled(0)
        self.alignAxiPushButtons.setGeometry(QRect(183,232,164,27))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(12,290,108,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(126,290,108,27))
        self.cancelPushButton.setAutoDefault(1)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(240,290,108,27))
        self.applyPushButton.setAutoDefault(1)
        self.applyPushButton.setDefault(0)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(260,70,40,22))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(310,70,30,22))

        self.languageChange()

        self.resize(QSize(357,335).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeRotaryMotorColor)

        self.setTabOrder(self.torqueLineEdit,self.speedLineEdit)
        self.setTabOrder(self.speedLineEdit,self.atomsComboBox)
        self.setTabOrder(self.atomsComboBox,self.alignAxiPushButtons)
        self.setTabOrder(self.alignAxiPushButtons,self.moveCenterPushButton)
        self.setTabOrder(self.moveCenterPushButton,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel1_2.setText(self.__tr("Speed:"))
        self.textLabel1.setText(self.__tr("Torque:"))
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
        self.colorSelectorPushButton.setText(self.__tr("..."))


    def applyButtonPressed(self):
        print "RotaryMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def changeRotaryMotorColor(self):
        print "RotaryMotorPropDialog.changeRotaryMotorColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("RotaryMotorPropDialog",s,c)
