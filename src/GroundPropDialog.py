# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\GroundPropDialog.ui'
#
# Created: Fri Oct 8 11:47:17 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 35 1",
". c None",
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


        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(21,101,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(119,101,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(223,51,40,27))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(171,51,44,27))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(11,11,42,26))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setGeometry(QRect(58,11,211,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setGeometry(QRect(272,51,30,27))

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(11,51,42,23))
        self.atomsTextLabel.setMouseTracking(0)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(59,51,85,23))

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(217,101,82,27))

        self.languageChange()

        self.resize(QSize(339,164).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeGroundColor)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)



    def languageChange(self):
        self.setCaption(self.__tr("Ground Properties"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.applyPushButton.setText(self.__tr("Apply"))


    def applyButtonPressed(self):
        print "GroundPropDialog.applyButtonPressed(): Not implemented yet"

    def changeGroundColor(self):
        print "GroundPropDialog.changeGroundColor(): Not implemented yet"

    def propertyChanged(self):
        print "GroundPropDialog.propertyChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroundPropDialog",s,c)
