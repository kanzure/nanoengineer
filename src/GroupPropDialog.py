# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GroupPropDialog.ui'
#
# Created: Tue Sep 13 16:00:26 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x01" \
    "\x76\x49\x44\x41\x54\x78\x9c\xe5\x94\xbf\x2f\x43" \
    "\x51\x14\x80\xbf\xd7\x96\x34\x12\x3a\x09\x49\xb5" \
    "\x82\x34\x61\xe8\x60\x24\x91\x94\x45\x24\x16\x83" \
    "\x89\x4d\xc2\x54\x03\xa3\x88\xc9\xc6\xc2\x64\x78" \
    "\x8b\xc4\x7f\x20\x24\x96\x6e\x6d\x24\x22\xa4\x8d" \
    "\x54\x42\x15\x7d\xf5\x50\xfd\x91\x56\x3c\x52\x7d" \
    "\x86\xf2\x28\xf7\x51\x2b\xdf\x76\xce\x3d\xf7\xbb" \
    "\xf7\xdc\x9b\x7b\xe1\xdf\x21\x7d\x0c\x82\x6b\x6e" \
    "\x5d\x54\xd4\x3b\x75\x21\x89\xf2\xdf\x12\x5c\x73" \
    "\xeb\x66\x04\x56\x9a\x84\x0b\x89\xb0\x01\xec\x2c" \
    "\x35\xea\x3d\x93\xe7\x80\x2c\x2c\xf2\xf9\x55\x02" \
    "\x34\x9b\x4a\xfb\xa7\xaf\x8d\x0e\x6c\x46\xb6\x20" \
    "\x03\x59\x93\x29\xcb\xf8\xfc\xaa\x70\xe4\x78\xcb" \
    "\x87\x3c\x67\xd5\x27\x16\x93\x52\xa5\x10\x40\xd3" \
    "\xb8\x3c\xda\x23\x71\xbc\x2b\x94\x9a\xd1\xd5\x0a" \
    "\xe1\xed\x61\xdd\x3b\xb4\x29\x55\x0a\x53\x70\x7a" \
    "\x18\xc2\xe9\x1d\xc5\xe3\x5b\x2d\xe7\x8a\x1a\xd8" \
    "\xec\xa6\xb2\x32\x32\xeb\x0b\xf3\x7c\xd9\x61\xa9" \
    "\x94\x02\xc0\xd5\xed\xc2\x38\xcf\xca\x25\x85\x68" \
    "\xaa\xc2\xd3\xb3\xa0\x5c\x89\x85\xb1\xd6\xd4\x62" \
    "\x77\xb4\x80\x96\xf9\xd9\xf4\x4a\x3a\x73\x4b\x9d" \
    "\x56\xf8\x24\x4c\xa8\x28\xc9\x18\x8d\x6d\x1d\xc0" \
    "\x03\x14\xcc\x2e\xe8\x03\x45\x28\xde\xe7\x48\x45" \
    "\x43\xd4\x39\x5b\x81\xc8\xbb\xf0\xad\xdd\xf7\x3e" \
    "\xb4\xaa\x84\x85\x5c\x96\x58\xfc\x91\x91\x99\x88" \
    "\x04\x60\x79\x1b\xbb\x51\x4e\xb0\x35\x34\xd1\x39" \
    "\x38\x0e\x89\xf8\xcf\xb2\x57\x32\x4a\x8c\xf4\x5d" \
    "\xda\x88\x0d\xe1\x59\x7c\x1f\x4f\xdf\x40\xd5\x22" \
    "\x33\x8c\x96\x25\x8b\x05\x87\xb3\x1d\xa2\x07\xbf" \
    "\x12\x9c\x5f\x25\xb1\x6b\x79\x23\x36\x9e\xcc\xc6" \
    "\x6c\x7d\xd5\xef\xf5\x33\x63\xcb\xf9\xdf\x7f\x1e" \
    "\x7f\x87\x17\x97\x77\x90\xc4\xd6\x04\x1a\xd5\x00" \
    "\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class GroupPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("GroupPropDialog")

        self.setIcon(self.image0)

        GroupPropDialogLayout = QGridLayout(self,1,1,11,6,"GroupPropDialogLayout")

        layout8 = QVBoxLayout(None,0,6,"layout8")

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.nameLabel = QLabel(self,"nameLabel")
        self.nameLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout6.addWidget(self.nameLabel)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFocusPolicy(QLineEdit.StrongFocus)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout6.addWidget(self.nameLineEdit)
        layout8.addLayout(layout6)

        self.mmpformatLabel = QLabel(self,"mmpformatLabel")
        self.mmpformatLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout8.addWidget(self.mmpformatLabel)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.statsView = QListView(self,"statsView")
        self.statsView.addColumn(self.__tr("Object Name"))
        self.statsView.addColumn(self.__tr("Value"))
        self.statsView.setFocusPolicy(QListView.NoFocus)
        layout7.addWidget(self.statsView)
        layout8.addLayout(layout7)

        GroupPropDialogLayout.addLayout(layout8,0,0)
        spacer11 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        GroupPropDialogLayout.addItem(spacer11,1,0)

        layout96 = QHBoxLayout(None,0,6,"layout96")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout96.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout96.addWidget(self.cancelPushButton)

        GroupPropDialogLayout.addLayout(layout96,2,0)

        self.languageChange()

        self.resize(QSize(258,357).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self.reject)

        self.setTabOrder(self.nameLineEdit,self.okPushButton)
        self.setTabOrder(self.okPushButton,self.cancelPushButton)
        self.setTabOrder(self.cancelPushButton,self.statsView)


    def languageChange(self):
        self.setCaption(self.__tr("Group Properties"))
        self.nameLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.mmpformatLabel.setText(self.__tr("Group Statistics:"))
        self.statsView.header().setLabel(0,self.__tr("Object Name"))
        self.statsView.header().setLabel(1,self.__tr("Value"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))


    def __tr(self,s,c = None):
        return qApp.translate("GroupPropDialog",s,c)
