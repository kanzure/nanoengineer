# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/PartPropDialog.ui'
#
# Created: Thu Dec 9 14:29:46 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x17\x49\x44\x41\x54\x78\x9c\xb5\xd5\x3d\x8a\x85" \
    "\x30\x14\x05\xe0\xe3\xf8\x74\x03\x29\x5c\x84\x60" \
    "\x29\x58\xda\x09\x29\xb5\xb7\x75\x17\x6e\xc4\x55" \
    "\xa5\xb4\xb5\x13\xb4\x12\x04\x13\x71\x9a\x51\xf4" \
    "\xe5\x4f\x61\xbc\x95\xe4\x86\xcf\xc3\x4d\x20\xce" \
    "\xb6\x6d\x78\xa3\x7e\x5e\x51\xdf\x84\x3f\xa6\x66" \
    "\xd7\x75\x1b\xa5\xf4\x36\xc6\x18\x73\xac\xf0\x8e" \
    "\x56\x55\x85\x20\x08\x8c\x60\x96\x65\x48\x92\xe4" \
    "\xb2\xa6\x84\x77\xb4\x69\x1a\x6b\xca\x38\x8e\x51" \
    "\x14\x85\xb4\x2e\xc1\x4f\xd0\x30\x0c\x91\xa6\xa9" \
    "\xb2\x77\x39\xbc\xa7\x49\xcb\xb2\x04\x00\x10\x42" \
    "\xcc\x89\x29\xa5\x60\x8c\x59\x51\x00\x47\x52\x42" \
    "\x08\x86\x61\x30\xc3\x7f\xa9\x95\xd0\xba\xae\xc7" \
    "\x77\xdf\xf7\x17\x54\x85\xdf\xbe\xc7\xae\xeb\x4a" \
    "\x6b\x3a\x54\x99\x98\x73\x0e\x00\x10\x42\x58\x7f" \
    "\x66\x4a\x2c\xc1\x9e\xe7\x19\x61\xdf\xf7\x6f\x25" \
    "\x96\x46\xc1\x39\x3f\x52\xab\x6a\x59\x16\x65\xe2" \
    "\xef\xd2\x8e\xe2\x0e\xfe\x78\xc6\x26\x14\x00\xe6" \
    "\x79\x96\x12\x5b\x67\xcc\x39\x87\x10\xe2\x72\xbd" \
    "\x6c\x89\xdb\xb6\x45\x5d\xd7\x66\x78\x3f\x34\xd3" \
    "\xad\xd8\x7b\x67\x34\xcf\x73\xe7\xbc\x47\x82\xa7" \
    "\x69\xc2\x38\x8e\x5a\xf4\x5c\x3a\x14\x00\x9c\xf3" \
    "\xd3\x14\x45\xd1\xa3\x77\x4a\x87\x4a\xf0\x7f\xd6" \
    "\x6b\x4f\xd3\x2f\x90\x3f\xb8\xbf\xe7\x51\xf3\x3f" \
    "\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class PartPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
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
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
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
        self.okPushButton.setMinimumSize(QSize(0,0))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout108.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,0))
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
