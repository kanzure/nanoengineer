# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MoleculePropDialog.ui'
#
# Created: Tue Dec 28 15:25:27 2004
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


        LayoutWidget = QWidget(self,"layout9")
        LayoutWidget.setGeometry(QRect(13,13,290,319))
        layout9 = QGridLayout(LayoutWidget,1,1,11,6,"layout9")

        layout8 = QVBoxLayout(None,0,6,"layout8")

        layout102 = QHBoxLayout(None,0,6,"layout102")

        self.colorTextLabel = QLabel(LayoutWidget,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout102.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(LayoutWidget,"colorPixmapLabel")
        self.colorPixmapLabel.setMinimumSize(QSize(30,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(230,231,230))
        self.colorPixmapLabel.setFrameShape(QLabel.Box)
        self.colorPixmapLabel.setFrameShadow(QLabel.Plain)
        self.colorPixmapLabel.setScaledContents(1)
        layout102.addWidget(self.colorPixmapLabel)

        self.colorSelectorPushButton = QPushButton(LayoutWidget,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout102.addWidget(self.colorSelectorPushButton)
        layout8.addLayout(layout102)

        self.resetChunkColor = QPushButton(LayoutWidget,"resetChunkColor")
        self.resetChunkColor.setEnabled(1)
        layout8.addWidget(self.resetChunkColor)

        self.makeAtomsVisiblePB = QPushButton(LayoutWidget,"makeAtomsVisiblePB")
        self.makeAtomsVisiblePB.setEnabled(1)
        layout8.addWidget(self.makeAtomsVisiblePB)

        layout9.addLayout(layout8,2,0)

        layout9_2 = QHBoxLayout(None,0,6,"layout9_2")

        layout100 = QVBoxLayout(None,0,6,"layout100")

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout100.addWidget(self.textLabel2)
        spacer1 = QSpacerItem(20,113,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout100.addItem(spacer1)
        layout9_2.addLayout(layout100)

        self.atomsTextBrowser = QTextBrowser(LayoutWidget,"atomsTextBrowser")
        layout9_2.addWidget(self.atomsTextBrowser)

        layout9.addLayout(layout9_2,1,0)

        layout8_2 = QHBoxLayout(None,0,6,"layout8_2")

        self.textLabel1 = QLabel(LayoutWidget,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout8_2.addWidget(self.textLabel1)

        self.nameLineEdit = QLineEdit(LayoutWidget,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout8_2.addWidget(self.nameLineEdit)

        layout9.addLayout(layout8_2,0,0)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.okPushButton = QPushButton(LayoutWidget,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,0))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout7.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(LayoutWidget,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,0))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout7.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(LayoutWidget,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setMinimumSize(QSize(0,0))
        layout7.addWidget(self.applyPushButton)

        layout9.addLayout(layout7,3,0)

        self.languageChange()

        self.resize(QSize(334,355).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonClicked)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)
        self.connect(self.resetChunkColor,SIGNAL("clicked()"),self.setMol2ElementColors)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeMolColor)
        self.connect(self.makeAtomsVisiblePB,SIGNAL("clicked()"),self.makeAtomsVisible)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.colorTextLabel.setText(self.__tr("Chunk Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.resetChunkColor.setText(self.__tr("Reset Chunk Color to Default"))
        self.makeAtomsVisiblePB.setText(self.__tr("Make Invisible Atoms Visible"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
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

    def makeAtomsVisible(self):
        print "MoleculePropDialog.makeAtomsVisible(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
