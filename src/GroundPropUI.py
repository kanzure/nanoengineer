# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GroundPropUI.ui'
#
# Created: Mon Sep 20 18:32:19 2004
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

class GroundPropForm(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("GroundPropForm")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        LayoutWidget = QWidget(self,"layout31")
        LayoutWidget.setGeometry(QRect(10,10,260,23))
        layout31 = QHBoxLayout(LayoutWidget,11,6,"layout31")

        self.nameTextLabel = QLabel(LayoutWidget,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout31.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(LayoutWidget,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout31.addWidget(self.nameLineEdit)

        LayoutWidget_2 = QWidget(self,"layout30")
        LayoutWidget_2.setGeometry(QRect(10,80,260,29))
        layout30 = QHBoxLayout(LayoutWidget_2,11,6,"layout30")

        self.okPushButton = QPushButton(LayoutWidget_2,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout30.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(LayoutWidget_2,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout30.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(LayoutWidget_2,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        layout30.addWidget(self.applyPushButton)

        LayoutWidget_3 = QWidget(self,"layout32")
        LayoutWidget_3.setGeometry(QRect(10,40,133,23))
        layout32 = QHBoxLayout(LayoutWidget_3,11,6,"layout32")

        self.atomsTextLabel = QLabel(LayoutWidget_3,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        layout32.addWidget(self.atomsTextLabel)

        self.atomsComboBox = QComboBox(0,LayoutWidget_3,"atomsComboBox")
        layout32.addWidget(self.atomsComboBox)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(151,41,36,27))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(193,41,40,27))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setGeometry(QRect(242,41,30,27))

        self.languageChange()

        self.resize(QSize(285,118).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))



    def languageChange(self):
        self.setCaption(self.__tr("Ground Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))


    def applyButtonPressed(self):
        print "GroundPropForm.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroundPropForm",s,c)
