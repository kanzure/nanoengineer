# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/GroundPropDialog.ui'
#
# Created: Wed Sep 22 15:55:42 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\xdb\x49\x44\x41\x54\x78\x9c\xed\x95\xb1\x6f\xda" \
    "\x40\x14\xc6\xbf\xab\x3a\xf0\x1f\x80\x07\x2b\x15" \
    "\x1b\x32\x42\xc0\x66\x24\x90\x08\x25\x95\x9a\x25" \
    "\x6d\x24\x06\xd6\x74\x6c\xa6\x93\xd2\xa9\x59\xd2" \
    "\x11\x35\xe9\x6c\x66\x8b\xc1\x1e\xdd\xa9\x59\x9c" \
    "\x80\x91\xd2\x00\x91\x40\x32\x0b\x43\x90\xe0\xcf" \
    "\xf8\x3a\x54\x6e\x82\x08\x39\x53\xa9\x5b\x3f\xe9" \
    "\x2d\x77\xf7\xfd\xf4\xfc\xfc\xee\x9d\x20\x89\x7f" \
    "\xa1\x17\xdb\x1c\xbe\xf9\x79\x13\x3f\x0b\x92\xca" \
    "\x08\xfa\x01\xeb\xf5\x3a\x75\x5d\xe7\xd1\x87\x23" \
    "\x76\x7b\x5d\xaa\x3c\xb1\x32\x3e\xfd\x7c\x8a\x54" \
    "\x2a\x85\x8b\x6f\x17\x98\x86\x53\x74\x3a\x1d\xa5" \
    "\x47\x09\x1e\x0c\x07\x0c\xc3\x10\x07\xef\x0e\x60" \
    "\x9a\x26\x76\x6b\xbb\xe8\x07\x7d\x25\xf8\xa5\xea" \
    "\x40\xb1\x50\x14\x7b\x6f\xf6\x78\xfe\xf5\x1c\x77" \
    "\xb5\x3b\xb8\x8e\x8b\x46\xa3\xa1\x04\xc7\xaa\x71" \
    "\xb7\xd7\xe5\xc9\xa7\x13\x02\xe0\xd9\x97\x33\xde" \
    "\x0e\x6e\x95\x35\x56\x66\x0c\x00\x25\xb3\x24\x96" \
    "\xcb\x25\x01\x20\x93\xc9\xa0\x58\x28\x0a\x95\x67" \
    "\xab\x76\xdb\x46\xff\xc1\xeb\x60\x21\x04\xa3\xc8" \
    "\x66\xb3\x5b\x0d\x90\x4a\xa5\xc2\xc7\xfe\x15\x70" \
    "\x24\xab\x6d\x61\x3c\x1e\x2b\xff\xfa\x63\xf9\xbe" \
    "\x2f\xac\xb6\x85\x64\x32\xf9\xb0\x18\xf5\x1d\x00" \
    "\x5a\x6d\x8b\x9a\xa6\xd1\x71\x9d\xb5\x3e\x75\x5c" \
    "\x87\x00\x36\xee\xe5\x72\x39\x5a\x6d\x8b\xbf\x91" \
    "\x7c\x00\x1b\x86\x41\x92\x90\x52\x3e\x09\xdf\x04" \
    "\x76\x5c\x87\x9a\xa6\x51\x4a\x49\x92\x28\x97\xcb" \
    "\x5c\xb9\x20\xd1\xe7\xb7\x5a\x2d\x01\x80\xc7\x1f" \
    "\x8f\x71\x7d\x75\x4d\x5d\xd7\xb1\xf3\x6a\x07\xf3" \
    "\xfb\x39\x00\x60\x7e\x3f\x87\xf7\xdd\xe3\x34\x9c" \
    "\x62\xb1\x58\xc0\xb6\x6d\x34\x9b\xcd\xc8\x07\xdf" \
    "\xf7\x05\xb0\x61\x56\x44\x70\xdb\xb6\x01\x00\x86" \
    "\x61\xfc\xd9\xf3\x3c\x0f\xf0\x80\xc9\x64\x02\x00" \
    "\x2b\xd0\x15\x3d\x77\xdf\x1d\xd7\xa1\x94\x92\x00" \
    "\xd6\x42\x4a\xf9\x64\xbd\x63\xcd\x8a\xc3\xf7\x87" \
    "\x22\x91\x48\x10\x02\xb8\xfc\x71\x89\xd1\x68\x84" \
    "\x7c\x3e\x8f\xda\xeb\x1a\xaa\xd5\x2a\xf6\xdf\xee" \
    "\x6f\xec\x1e\x11\xe7\xcd\x1b\x8e\x86\x9c\xcd\x66" \
    "\x08\x7a\x01\xcc\x92\x89\x74\x3a\x8d\x42\xbe\xf0" \
    "\x6c\x4b\xc6\x02\xff\x8d\x7e\x01\x94\x53\xa4\xe9" \
    "\x34\x3a\x15\xa3\x00\x00\x00\x00\x49\x45\x4e\x44" \
    "\xae\x42\x60\x82"

class GroundPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("GroundPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(21,101,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(119,101,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(217,101,82,27))

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(223,51,40,27))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(171,51,44,27))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(20,10,50,21))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(11,51,52,21))
        self.atomsTextLabel.setMouseTracking(0)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(70,50,90,20))

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(0)
        self.colorSelectorPushButton.setGeometry(QRect(272,51,30,27))

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(0)
        self.nameLineEdit.setGeometry(QRect(78,11,211,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.languageChange()

        self.resize(QSize(339,152).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))



    def languageChange(self):
        self.setCaption(self.__tr("Ground Properties"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.nameLineEdit.setText(QString.null)


    def applyButtonPressed(self):
        print "GroundPropDialog.applyButtonPressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GroundPropDialog",s,c)
