# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MoleculePropDialog.ui'
#
# Created: Wed Sep 22 10:19:35 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 27 1",
"g c #1a1a1a",
"v c #2a2a2a",
"b c #2d2d2d",
"p c #303030",
"s c #353535",
"m c #565656",
"l c #5a5a5a",
"a c #616161",
"c c #80c4ac",
"h c #82d2b5",
"i c #88dbbd",
"q c #8f8f8f",
"r c #999999",
"d c #9bf5d6",
"y c #9e9e9e",
"f c #b4f7e0",
"u c #c0c0c0",
"# c #c2c3c2",
"w c #c6c6c6",
"e c #d1d1d1",
"o c #dddddd",
"t c #e4e4e4",
"j c #eeeeee",
"n c #f5f5f5",
"k c #f9f9f9",
"x c #fefefe",
". c #ffffff",
"......................",
"......................",
"......................",
".....#aba#..#aba#.....",
".....acdcaeeacdca.....",
".....bddfbggbddfb.....",
".....ahihaeeahiha.....",
".....#aba#..#aba#j....",
"....klmn.......opq....",
"..#aba#........#aba#..",
"..acdca........acdca..",
"..bddfb........bddfb..",
"..ahiha........ahiha..",
"..#aba#........#aba#..",
".....rst.......uvw....",
".....#aba#..#aba#x....",
".....acdcayyacdca.....",
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


        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(12,12,42,21))
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(12,39,42,17))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(12,181,42,27))
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(60,12,210,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")
        self.atomsTextBrowser.setGeometry(QRect(60,39,210,136))

        self.jigsComboBox = QComboBox(0,self,"jigsComboBox")
        self.jigsComboBox.setGeometry(QRect(60,184,122,21))
        self.jigsComboBox.setSizePolicy(QSizePolicy(7,0,0,0,self.jigsComboBox.sizePolicy().hasHeightForWidth()))

        self.propPushButton = QPushButton(self,"propPushButton")
        self.propPushButton.setGeometry(QRect(188,181,82,27))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(12,238,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(100,238,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(188,238,82,27))

        self.languageChange()

        self.resize(QSize(282,280).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)


    def languageChange(self):
        self.setCaption(self.__tr("Molecule Properties"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.textLabel3.setText(self.__tr("Jigs:"))
        self.nameLineEdit.setText(QString.null)
        self.propPushButton.setText(self.__tr("Properties..."))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))


    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
