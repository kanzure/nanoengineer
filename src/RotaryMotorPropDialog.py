# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\RotaryMotorPropDialog.ui'
#
# Created: Thu Dec 9 13:19:52 2004
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

        RotaryMotorPropDialogLayout = QVBoxLayout(self,11,6,"RotaryMotorPropDialogLayout")

        layout37 = QGridLayout(None,1,1,0,6,"layout37")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout37.addWidget(self.nameTextLabel,0,0)

        self.speedLineEdit = QLineEdit(self,"speedLineEdit")
        self.speedLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout37.addWidget(self.speedLineEdit,2,1)

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

        self.torqueLineEdit = QLineEdit(self,"torqueLineEdit")
        self.torqueLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout37.addWidget(self.torqueLineEdit,1,1)

        self.textLabel4 = QLabel(self,"textLabel4")

        layout37.addWidget(self.textLabel4,0,2)
        RotaryMotorPropDialogLayout.addLayout(layout37)

        layout38 = QGridLayout(None,1,1,0,6,"layout38")

        self.sradiusLineEdit = QLineEdit(self,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout38.addWidget(self.sradiusLineEdit,2,1)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")

        layout38.addWidget(self.textLabel3_2,1,2)

        self.radiusLineEdit = QLineEdit(self,"radiusLineEdit")
        self.radiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout38.addWidget(self.radiusLineEdit,1,1)

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
        RotaryMotorPropDialogLayout.addLayout(layout38)

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
        RotaryMotorPropDialogLayout.addLayout(layout39)

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
        RotaryMotorPropDialogLayout.addLayout(layout11)

        self.languageChange()

        self.resize(QSize(338,318).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.torqueLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.speedLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeRotaryMotorColor)

        self.setTabOrder(self.torqueLineEdit,self.speedLineEdit)
        self.setTabOrder(self.speedLineEdit,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(self.__tr("gHz"))
        self.textLabel1_4.setText(self.__tr("nN*nm"))
        self.textLabel1.setText(self.__tr("Torque:"))
        self.textLabel1_2.setText(self.__tr("Speed:"))
        self.textLabel4.setText(QString.null)
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius:"))
        self.textLabel1_2_2.setText(self.__tr("Motor Radius:"))
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
        print "RotaryMotorPropDialog.applyButtonPressed(): Not implemented yet"

    def propertyChanged(self):
        print "RotaryMotorPropDialog.propertyChanged(): Not implemented yet"

    def changeRotaryMotorColor(self):
        print "RotaryMotorPropDialog.changeRotaryMotorColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("RotaryMotorPropDialog",s,c)
