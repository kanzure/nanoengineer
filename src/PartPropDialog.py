# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\PartPropDialog.ui'
#
# Created: Sun Jan 30 22:33:45 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 23 1",
". c None",
"a c #2d2d2d",
"h c #404040",
"g c #535353",
"b c #959595",
"c c #acacac",
"t c #b0b0b0",
"s c #b4b4b4",
"p c #bababa",
"u c #bebebe",
"n c #c3c3c3",
"r c #c7c7c7",
"e c #c9c9c9",
"q c #cacaca",
"o c #cecece",
"m c #d3d3d3",
"l c #d8d8d8",
"k c #d9d9d9",
"j c #dddddd",
"i c #dfdfdf",
"# c #e2e2e2",
"d c #f4f4f4",
"f c #ffffff",
"......................",
"......................",
"......................",
".......#aaaaaaaaaaa...",
"......#abccccccccda...",
".....#aeeeeeeeeefga...",
"....#aeeeeeeeeedhha...",
"...#aeeeeeeeeefghga...",
"...affffffffffhhgha...",
"...a######iiiehghga...",
"...a#######iiehhgha...",
"...ajjkkkkkkkehghga...",
"...a##kkkkkkiehhgha...",
"...ajjkkkkkkkehghga...",
"...allmmmmmmmnhhgha...",
"...amoooooooophghga...",
"...aoqrrrrrrrshhgac...",
"...aqqnnnnnnnthgac....",
"...auccccccccchac.....",
"...aaaaaaaaaaaac......",
"......................",
"......................"
]

class PartPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("PartPropDialog")

        self.setIcon(self.image0)

        PartPropDialogLayout = QGridLayout(self,1,1,11,6,"PartPropDialogLayout")

        layout108 = QHBoxLayout(None,4,72,"layout108")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,0))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout108.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,0))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout108.addWidget(self.cancelPushButton)

        PartPropDialogLayout.addLayout(layout108,1,0)

        self.tabWidget3 = QTabWidget(self,"tabWidget3")

        self.tab = QWidget(self.tabWidget3,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        layout8 = QVBoxLayout(None,0,6,"layout8")

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.nameLabel = QLabel(self.tab,"nameLabel")
        self.nameLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout6.addWidget(self.nameLabel)

        self.nameLineEdit = QLineEdit(self.tab,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(1)
        layout6.addWidget(self.nameLineEdit)
        layout8.addLayout(layout6)

        self.mmpformatLabel = QLabel(self.tab,"mmpformatLabel")
        self.mmpformatLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout8.addWidget(self.mmpformatLabel)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        layout105 = QVBoxLayout(None,0,6,"layout105")

        self.statsLabel = QLabel(self.tab,"statsLabel")
        self.statsLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout105.addWidget(self.statsLabel)
        spacer14 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout105.addItem(spacer14)
        layout7.addLayout(layout105)

        self.statsView = QListView(self.tab,"statsView")
        self.statsView.addColumn(self.__tr("Statistic Name"))
        self.statsView.addColumn(self.__tr("Value"))
        layout7.addWidget(self.statsView)
        layout8.addLayout(layout7)

        tabLayout.addLayout(layout8,0,0)
        self.tabWidget3.insertTab(self.tab,QString(""))

        PartPropDialogLayout.addWidget(self.tabWidget3,0,0)

        self.languageChange()

        self.resize(QSize(396,402).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))


    def languageChange(self):
        self.setCaption(self.__tr("Part Properties"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.nameLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.mmpformatLabel.setText(self.__tr("MMP File Format:"))
        self.statsLabel.setText(self.__tr("Statistics:"))
        self.statsView.header().setLabel(0,self.__tr("Statistic Name"))
        self.statsView.header().setLabel(1,self.__tr("Value"))
        self.tabWidget3.changeTab(self.tab,self.__tr("General"))


    def applyButtonClicked(self):
        print "PartPropDialog.applyButtonClicked(): Not implemented yet"

    def nameChanged(self):
        print "PartPropDialog.nameChanged(): Not implemented yet"

    def setMol2ElementColors(self):
        print "PartPropDialog.setMol2ElementColors(): Not implemented yet"

    def changeMolColor(self):
        print "PartPropDialog.changeMolColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PartPropDialog",s,c)
