# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MoleculePropDialog.ui'
#
# Created: Fri Nov 5 09:10:26 2004
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


        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(121,259,82,29))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.elementColorsPushButton = QPushButton(self,"elementColorsPushButton")
        self.elementColorsPushButton.setEnabled(1)
        self.elementColorsPushButton.setGeometry(QRect(150,200,130,30))

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")
        self.atomsTextBrowser.setGeometry(QRect(60,49,220,136))

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(2,49,52,20))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(4,22,50,21))
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(60,22,220,23))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(209,259,82,29))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(33,259,82,29))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(0,205,50,20))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(60,200,40,28))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(230,231,230))
        self.colorPixmapLabel.setFrameShape(QLabel.Box)
        self.colorPixmapLabel.setFrameShadow(QLabel.Plain)
        self.colorPixmapLabel.setScaledContents(1)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setGeometry(QRect(110,200,30,30))

        self.languageChange()

        self.resize(QSize(314,313).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonClicked)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)
        self.connect(self.elementColorsPushButton,SIGNAL("clicked()"),self.setMol2ElementColors)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeMolColor)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.elementColorsPushButton.setText(self.__tr("Element Colors"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.applyPushButton.setText(self.__tr("Apply"))
        self.applyPushButton.setAccel(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))


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
