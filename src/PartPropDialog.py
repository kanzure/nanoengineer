# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\PartPropDialog.ui'
#
# Created: Thu Dec 9 13:19:47 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 22 1",
"a c #2d2d2d",
"g c #404040",
"f c #535353",
"b c #959595",
"c c #acacac",
"s c #b0b0b0",
"r c #b4b4b4",
"o c #bababa",
"t c #bebebe",
"m c #c3c3c3",
"q c #c7c7c7",
"e c #c9c9c9",
"p c #cacaca",
"n c #cecece",
"l c #d3d3d3",
"k c #d8d8d8",
"j c #d9d9d9",
"i c #dddddd",
"h c #dfdfdf",
"# c #e2e2e2",
"d c #f4f4f4",
". c #ffffff",
"......................",
"......................",
"......................",
".......#aaaaaaaaaaa...",
"......#abccccccccda...",
".....#aeeeeeeeee.fa...",
"....#aeeeeeeeeedgga...",
"...#aeeeeeeeee.fgfa...",
"...a..........ggfga...",
"...a######hhhegfgfa...",
"...a#######hheggfga...",
"...aiijjjjjjjegfgfa...",
"...a##jjjjjjheggfga...",
"...aiijjjjjjjegfgfa...",
"...akklllllllmggfga...",
"...alnnnnnnnnogfgfa...",
"...anpqqqqqqqrggfac...",
"...appmmmmmmmsgfac....",
"...atcccccccccgac.....",
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

        PartPropDialogLayout = QVBoxLayout(self,11,6,"PartPropDialogLayout")

        self.tabWidget3 = QTabWidget(self,"tabWidget3")

        self.tab = QWidget(self.tabWidget3,"tab")
        tabLayout = QVBoxLayout(self.tab,11,6,"tabLayout")

        layout109 = QVBoxLayout(None,0,6,"layout109")

        layout107 = QHBoxLayout(None,0,6,"layout107")

        self.nameLabel = QLabel(self.tab,"nameLabel")
        self.nameLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout107.addWidget(self.nameLabel)

        self.nameLineEdit = QLineEdit(self.tab,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setReadOnly(1)
        layout107.addWidget(self.nameLineEdit)
        layout109.addLayout(layout107)

        layout106 = QHBoxLayout(None,0,6,"layout106")

        layout105 = QVBoxLayout(None,0,6,"layout105")

        self.statsLabel = QLabel(self.tab,"statsLabel")
        self.statsLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout105.addWidget(self.statsLabel)
        spacer14 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout105.addItem(spacer14)
        layout106.addLayout(layout105)

        self.statsView = QListView(self.tab,"statsView")
        self.statsView.addColumn(self.__tr("Statistic Name"))
        self.statsView.addColumn(self.__tr("Value"))
        layout106.addWidget(self.statsView)
        layout109.addLayout(layout106)
        tabLayout.addLayout(layout109)
        self.tabWidget3.insertTab(self.tab,QString(""))
        PartPropDialogLayout.addWidget(self.tabWidget3)

        layout108 = QHBoxLayout(None,4,72,"layout108")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,30))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout108.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,30))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout108.addWidget(self.cancelPushButton)
        PartPropDialogLayout.addLayout(layout108)

        self.languageChange()

        self.resize(QSize(393,381).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))


    def languageChange(self):
        self.setCaption(self.__tr("Part Properties"))
        self.nameLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.statsLabel.setText(self.__tr("Statistics:"))
        self.statsView.header().setLabel(0,self.__tr("Statistic Name"))
        self.statsView.header().setLabel(1,self.__tr("Value"))
        self.tabWidget3.changeTab(self.tab,self.__tr("General"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))


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
