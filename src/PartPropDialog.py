# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PartPropDialog.ui'
#
# Created: Tue Sep 13 16:00:27 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x1a\x49\x44\x41\x54\x78\x9c\xd5\xd5\x31\xae\x45" \
    "\x40\x14\x06\xe0\xdf\x73\xd9\xc0\x14\x12\xb1\x03" \
    "\xbd\x44\xa9\x93\x4c\xab\xd7\xea\x2c\xc1\x3a\x24" \
    "\xd6\x63\x01\x4a\xad\x4e\x42\x25\x91\x98\x91\xf7" \
    "\x2a\xc2\x9d\x31\x43\xa1\x78\xa7\x92\x39\xf2\xf9" \
    "\x73\xe6\x24\x8c\xba\xae\xf1\x46\xfd\xbc\xa2\xbe" \
    "\x09\x7f\x54\x4d\xcf\xf3\x7e\x29\xa5\xb7\xb1\xb2" \
    "\x2c\x0d\x2d\xbc\xa1\x59\x96\xc1\x71\x1c\x25\x18" \
    "\xc7\x31\xc2\x30\x3c\x9d\x49\xe1\x0d\xad\xaa\x4a" \
    "\x9b\x32\x08\x02\x24\x49\x22\x9c\x0b\xf0\x13\xd4" \
    "\xf7\x7d\x44\x51\x24\xed\x9d\x2e\xef\x69\xd2\x34" \
    "\x4d\x01\x00\x84\x10\x75\x62\x4a\x29\x9a\xa6\xd1" \
    "\xa2\x00\xf6\xa4\x84\x10\x0c\xc3\xa0\x86\x01\xa0" \
    "\xeb\x3a\x29\xb4\xae\xeb\xfe\xdc\xf7\xfd\x09\x95" \
    "\xe1\xb7\xf7\xd8\x34\x4d\xe1\xec\x0a\x95\x26\x66" \
    "\x8c\x01\x00\x38\xe7\xda\x8f\xa9\x12\x0b\xb0\x65" \
    "\x59\x4a\xd8\xb6\xed\x5b\x89\x85\x51\x30\xc6\xf6" \
    "\xd4\xb2\x5a\x96\x45\x9a\xf8\xbb\x2e\x47\x71\x07" \
    "\x7f\x3c\x63\x15\x0a\x00\xf3\x3c\x0b\x89\xb5\x33" \
    "\x66\x8c\x81\x73\x7e\x5a\x2f\x5d\xe2\xb6\x6d\x51" \
    "\x14\x85\x1a\xde\x2e\x4d\xb5\x15\x5b\xef\x88\xba" \
    "\xae\x6b\x1c\xdf\x11\xe0\x69\x9a\x30\x8e\xe3\x25" \
    "\x7a\xac\x2b\x54\x0a\xe7\x79\x7e\x0b\x05\x70\x89" \
    "\x02\x80\xf1\xef\xfe\x79\x7f\x4c\x28\xa5\xde\x38" \
    "\x57\x30\x20\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"

class PartPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
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
        self.tabWidget3.insertTab(self.tab,QString.fromLatin1(""))

        PartPropDialogLayout.addWidget(self.tabWidget3,0,0)

        self.languageChange()

        self.resize(QSize(396,402).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self.reject)

        self.setTabOrder(self.nameLineEdit,self.statsView)
        self.setTabOrder(self.statsView,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)
        self.setTabOrder(self.cancelPushButton,self.tabWidget3)


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
