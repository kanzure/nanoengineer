# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\GroundPropDialog.ui'
#
# Created: Wed Sep 22 10:09:08 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 35 1",
"q c #000000",
"v c #171717",
"w c #191919",
"c c #1d1d1d",
"n c #2b2b2b",
"x c #2e2e2e",
"F c #303030",
"m c #353535",
"h c #3c3c3c",
"t c #3d3d3d",
"D c #444444",
"b c #454545",
"f c #5d5d5d",
"d c #636463",
"i c #6d6e6d",
"z c #707070",
"y c #737373",
"E c #737473",
"p c #767776",
"l c #7e7f7e",
"o c #818181",
"r c #838483",
"A c #8d8d8d",
"B c #8f8f8f",
"u c #9b9c9b",
"s c #acadac",
"g c #adaead",
"C c #b4b5b4",
"e c #c5c6c5",
"a c #c7c8c7",
"# c #cacbca",
"j c #cdcecd",
"G c #cecfce",
"k c #e6e7e6",
". c #ffffff",
"......................",
"...........#..........",
".........abcde........",
".........bfghi........",
"........jcgklm........",
".........dhlno........",
".........epqrj........",
"..........sqs.........",
"..........sqs.........",
"..........sqs.........",
"..........sqs.........",
"..........sqs.........",
"..qqqn....sqs....tqqq.",
"..qqu.....sqs.....uvq.",
"..quws....sqs....sxuq.",
"..n.yws...sqs...swy.t.",
".....ywzAsBqBCAywy....",
"......ywwDDqDDwwy.....",
".......syqqqqqys......",
"........CEFqFEC.......",
".........GsysG........",
"......................"
]

class GroundPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("GroundPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(151,41,36,27))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(193,41,40,27))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(242,41,30,27))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(11,81,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(99,81,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(187,81,82,27))

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(11,41,42,21))
        self.atomsTextLabel.setMouseTracking(0)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(59,41,85,21))

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(11,11,41,21))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(58,11,211,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.languageChange()

        self.resize(QSize(285,121).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))



    def languageChange(self):
        self.setCaption(self.__tr("Ground Properties"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)


    def applyButtonPressed(self):
        print "GroundPropDialog.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroundPropDialog",s,c)
