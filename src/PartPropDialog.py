# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\PartPropDialog.ui'
#
# Created: Tue Nov 9 09:38:36 2004
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


        self.nameLineEdit_2 = QLineEdit(self,"nameLineEdit_2")
        self.nameLineEdit_2.setGeometry(QRect(80,53,270,23))
        self.nameLineEdit_2.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit_2.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit_2.setReadOnly(1)

        self.nameLabel_2 = QLabel(self,"nameLabel_2")
        self.nameLabel_2.setGeometry(QRect(11,53,60,21))
        self.nameLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(190,430,82,29))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(102,430,82,29))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.tabWidget3 = QTabWidget(self,"tabWidget3")
        self.tabWidget3.setGeometry(QRect(0,10,370,410))

        self.tab = QWidget(self.tabWidget3,"tab")

        self.authorLineEdit = QLineEdit(self.tab,"authorLineEdit")
        self.authorLineEdit.setGeometry(QRect(80,61,270,23))
        self.authorLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.authorLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.mdateLabel = QLabel(self.tab,"mdateLabel")
        self.mdateLabel.setGeometry(QRect(80,121,270,20))
        self.mdateLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.adateLabel = QLabel(self.tab,"adateLabel")
        self.adateLabel.setGeometry(QRect(81,143,270,20))
        self.adateLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.nameLineEdit = QLineEdit(self.tab,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(80,23,270,23))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setReadOnly(1)

        self.cdateLabel = QLabel(self.tab,"cdateLabel")
        self.cdateLabel.setGeometry(QRect(81,98,270,20))
        self.cdateLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.createdLabel = QLabel(self.tab,"createdLabel")
        self.createdLabel.setGeometry(QRect(9,98,70,20))
        self.createdLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.modifiedLabel = QLabel(self.tab,"modifiedLabel")
        self.modifiedLabel.setGeometry(QRect(8,121,70,20))
        self.modifiedLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.accessedLabel = QLabel(self.tab,"accessedLabel")
        self.accessedLabel.setGeometry(QRect(9,143,70,20))
        self.accessedLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.statsLabel = QLabel(self.tab,"statsLabel")
        self.statsLabel.setGeometry(QRect(10,191,60,20))
        self.statsLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.authorLabel = QLabel(self.tab,"authorLabel")
        self.authorLabel.setGeometry(QRect(11,61,60,21))
        self.authorLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.nameLabel = QLabel(self.tab,"nameLabel")
        self.nameLabel.setGeometry(QRect(11,23,60,21))
        self.nameLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.statsView = QListView(self.tab,"statsView")
        self.statsView.addColumn(self.__tr("Statistic Name"))
        self.statsView.addColumn(self.__tr("Value"))
        self.statsView.setGeometry(QRect(80,180,270,180))
        self.tabWidget3.insertTab(self.tab,QString(""))

        self.tab_2 = QWidget(self.tabWidget3,"tab_2")

        self.nameCsysLineEdit = QLineEdit(self.tab_2,"nameCsysLineEdit")
        self.nameCsysLineEdit.setGeometry(QRect(80,22,270,23))
        self.nameCsysLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameCsysLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameCsysLineEdit.setReadOnly(1)

        self.tempLineEdit = QLineEdit(self.tab_2,"tempLineEdit")
        self.tempLineEdit.setGeometry(QRect(80,60,270,23))
        self.tempLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.tempLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.nameLabel2 = QLabel(self.tab_2,"nameLabel2")
        self.nameLabel2.setGeometry(QRect(11,22,60,21))
        self.nameLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        self.tempLabel = QLabel(self.tab_2,"tempLabel")
        self.tempLabel.setGeometry(QRect(11,60,60,21))
        self.tempLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        self.tabWidget3.insertTab(self.tab_2,QString(""))

        self.languageChange()

        self.resize(QSize(378,489).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))


    def languageChange(self):
        self.setCaption(self.__tr("Part Properties"))
        self.nameLineEdit_2.setText(QString.null)
        self.nameLabel_2.setText(self.__tr("Name:"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.authorLineEdit.setText(QString.null)
        self.mdateLabel.setText(self.__tr("Modified Date"))
        self.adateLabel.setText(self.__tr("Accessed Date"))
        self.nameLineEdit.setText(QString.null)
        self.cdateLabel.setText(self.__tr("Created Date"))
        self.createdLabel.setText(self.__tr("Created:"))
        self.modifiedLabel.setText(self.__tr("Modified:"))
        self.accessedLabel.setText(self.__tr("Accessed:"))
        self.statsLabel.setText(self.__tr("Statistics:"))
        self.authorLabel.setText(self.__tr("Author:"))
        self.nameLabel.setText(self.__tr("Name:"))
        self.statsView.header().setLabel(0,self.__tr("Statistic Name"))
        self.statsView.header().setLabel(1,self.__tr("Value"))
        self.tabWidget3.changeTab(self.tab,self.__tr("General"))
        self.nameCsysLineEdit.setText(QString.null)
        self.tempLineEdit.setText(QString.null)
        self.nameLabel2.setText(self.__tr("Name:"))
        self.tempLabel.setText(self.__tr("Temp:"))
        self.tabWidget3.changeTab(self.tab_2,self.__tr("CSys"))


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
