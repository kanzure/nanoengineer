# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\GroundPropDialog.ui'
#
# Created: Thu Dec 9 13:19:20 2004
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

        GroundPropDialogLayout = QVBoxLayout(self,11,28,"GroundPropDialogLayout")

        layout70 = QHBoxLayout(None,0,6,"layout70")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout70.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout70.addWidget(self.nameLineEdit)
        GroundPropDialogLayout.addLayout(layout70)

        layout73 = QHBoxLayout(None,0,16,"layout73")

        layout67 = QHBoxLayout(None,0,6,"layout67")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout67.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setMinimumSize(QSize(30,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout67.addWidget(self.colorPixmapLabel)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout67.addWidget(self.colorSelectorPushButton)
        layout73.addLayout(layout67)

        layout72 = QHBoxLayout(None,0,0,"layout72")

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        layout72.addWidget(self.atomsTextLabel)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        layout72.addWidget(self.atomsComboBox)
        layout73.addLayout(layout72)
        GroundPropDialogLayout.addLayout(layout73)
        spacer9 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        GroundPropDialogLayout.addItem(spacer9)

        layout66 = QHBoxLayout(None,0,16,"layout66")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout66.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout66.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        layout66.addWidget(self.applyPushButton)
        GroundPropDialogLayout.addLayout(layout66)

        self.languageChange()

        self.resize(QSize(331,202).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeGroundColor)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)



    def languageChange(self):
        self.setCaption(self.__tr("Ground Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))


    def applyButtonPressed(self):
        print "GroundPropDialog.applyButtonPressed(): Not implemented yet"

    def changeGroundColor(self):
        print "GroundPropDialog.changeGroundColor(): Not implemented yet"

    def propertyChanged(self):
        print "GroundPropDialog.propertyChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroundPropDialog",s,c)
