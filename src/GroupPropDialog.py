# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/GroupPropDialog.ui'
#
# Created: Thu Dec 9 14:04:25 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 46 1",
"H c #656565",
"w c #717171",
"q c #898989",
"v c #9b7b19",
"h c #9d7b1a",
"p c #a17e19",
"D c #a5730d",
"k c #b18919",
"N c #b9b9b9",
"Q c #bf9929",
"d c #c5c5c5",
"c c #c69a19",
"I c #c69a1a",
"O c #c79c1c",
"y c #c9a021",
"# c #cea222",
"C c #cebc5c",
"E c #cfa226",
"R c #d1d1d1",
"F c #d7b840",
"m c #dabf6c",
"a c #dddddd",
"M c #deb243",
"x c #e2b343",
"j c #e2c150",
"B c #e7be53",
"G c #efba43",
"J c #f0e47a",
"b c #f5f5f5",
"s c #f7f089",
"u c #fbf996",
"r c #fdd570",
"t c #ffc75b",
"P c #ffd76c",
"l c #ffd784",
"L c #ffdf7c",
"K c #ffe37c",
"o c #ffe784",
"i c #ffeb84",
"g c #fff38c",
"f c #fff39c",
"A c #fff794",
"n c #fffbf7",
"e c #ffff9c",
"z c #ffffa5",
". c #ffffff",
"......................",
"......................",
"......................",
"......................",
".....####ab...........",
"....#....cdb..........",
"...c.eeee.ccccccab....",
"...cfggggg.....chdb...",
"...cijccccccccccckd...",
"...clcm..n.....o.pq...",
"...crcseeeeeeeetuvw...",
"...cxyzAAAAAAAABCDw...",
"...cEFeiiiiiiioGcHq...",
"...cIJeKKKKKKKLMhHN...",
"...cOePPPPPPPPPQDwR...",
"...aDDDDDDDDDDDDHqa...",
"...bdqwwwwwwwwwwqdb...",
"....baRRRRRRRRRRab....",
"......................",
"......................",
"......................",
"......................"
]

class GroupPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("GroupPropDialog")

        self.setIcon(self.image0)

        GroupPropDialogLayout = QVBoxLayout(self,11,6,"GroupPropDialogLayout")

        layout98 = QHBoxLayout(None,0,6,"layout98")

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout98.addWidget(self.textLabel1)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout98.addWidget(self.nameLineEdit)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setMinimumSize(QSize(30,0))
        layout98.addWidget(self.textLabel2)
        GroupPropDialogLayout.addLayout(layout98)
        spacer11 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        GroupPropDialogLayout.addItem(spacer11)

        layout96 = QHBoxLayout(None,10,65,"layout96")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout96.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout96.addWidget(self.cancelPushButton)
        GroupPropDialogLayout.addLayout(layout96)

        self.languageChange()

        self.resize(QSize(314,136).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)


    def languageChange(self):
        self.setCaption(self.__tr("Group Properties"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))


    def nameChanged(self):
        print "GroupPropDialog.nameChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroupPropDialog",s,c)
