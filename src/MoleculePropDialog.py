# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\MoleculePropDialog.ui'
#
# Created: Thu Dec 9 13:19:42 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 28 1",
". c None",
"g c #1a1a1a",
"w c #2a2a2a",
"b c #2d2d2d",
"q c #303030",
"t c #353535",
"n c #565656",
"m c #5a5a5a",
"a c #616161",
"c c #80c4ac",
"h c #82d2b5",
"i c #88dbbd",
"r c #8f8f8f",
"s c #999999",
"d c #9bf5d6",
"z c #9e9e9e",
"f c #b4f7e0",
"v c #c0c0c0",
"# c #c2c3c2",
"x c #c6c6c6",
"e c #d1d1d1",
"p c #dddddd",
"u c #e4e4e4",
"k c #eeeeee",
"o c #f5f5f5",
"l c #f9f9f9",
"y c #fefefe",
"j c #ffffff",
"......................",
"......................",
"......................",
".....#aba#..#aba#.....",
".....acdcaeeacdca.....",
".....bddfbggbddfb.....",
".....ahihaeeahiha.....",
".....#aba#jj#aba#k....",
"....lmnojjjjjjjpqr....",
"..#aba#jjjjjjjj#aba#..",
"..acdcajjjjjjjjacdca..",
"..bddfbjjjjjjjjbddfb..",
"..ahihajjjjjjjjahiha..",
"..#aba#jjjjjjjj#aba#..",
".....stujjjjjjjvwx....",
".....#aba#jj#aba#y....",
".....acdcazzacdca.....",
".....bddfbaabddfb.....",
".....ahiha..ahiha.....",
".....#aba#..#aba#.....",
"......................",
"......................"
]

class MoleculePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("MoleculePropDialog")

        self.setIcon(self.image0)

        MoleculePropDialogLayout = QVBoxLayout(self,11,7,"MoleculePropDialogLayout")

        layout99 = QHBoxLayout(None,0,6,"layout99")

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout99.addWidget(self.textLabel1)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout99.addWidget(self.nameLineEdit)
        MoleculePropDialogLayout.addLayout(layout99)

        layout101 = QHBoxLayout(None,0,6,"layout101")

        layout100 = QVBoxLayout(None,0,6,"layout100")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout100.addWidget(self.textLabel2)
        spacer1 = QSpacerItem(20,113,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout100.addItem(spacer1)
        layout101.addLayout(layout100)

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")
        layout101.addWidget(self.atomsTextBrowser)
        MoleculePropDialogLayout.addLayout(layout101)

        layout103 = QHBoxLayout(None,0,6,"layout103")

        layout102 = QHBoxLayout(None,0,6,"layout102")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout102.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setMinimumSize(QSize(30,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(230,231,230))
        self.colorPixmapLabel.setFrameShape(QLabel.Box)
        self.colorPixmapLabel.setFrameShadow(QLabel.Plain)
        self.colorPixmapLabel.setScaledContents(1)
        layout102.addWidget(self.colorPixmapLabel)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout102.addWidget(self.colorSelectorPushButton)
        layout103.addLayout(layout102)

        self.elementColorsPushButton = QPushButton(self,"elementColorsPushButton")
        self.elementColorsPushButton.setEnabled(1)
        layout103.addWidget(self.elementColorsPushButton)
        MoleculePropDialogLayout.addLayout(layout103)
        spacer2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        MoleculePropDialogLayout.addItem(spacer2)

        layout104 = QHBoxLayout(None,7,7,"layout104")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,30))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout104.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,30))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout104.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setMinimumSize(QSize(0,30))
        layout104.addWidget(self.applyPushButton)
        MoleculePropDialogLayout.addLayout(layout104)

        self.languageChange()

        self.resize(QSize(393,354).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonClicked)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)
        self.connect(self.elementColorsPushButton,SIGNAL("clicked()"),self.setMol2ElementColors)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeMolColor)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.elementColorsPushButton.setText(self.__tr("Element Colors"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.applyPushButton.setAccel(QString.null)


    def applyButtonClicked(self):
        print "MoleculePropDialog.applyButtonClicked(): Not implemented yet"

    def nameChanged(self):
        print "MoleculePropDialog.nameChanged(): Not implemented yet"

    def setMol2ElementColors(self):
        print "MoleculePropDialog.setMol2ElementColors(): Not implemented yet"

    def changeMolColor(self):
        print "MoleculePropDialog.changeMolColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
