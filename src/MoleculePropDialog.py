# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MoleculePropDialog.ui'
#
# Created: Sat Oct 9 08:13:38 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x80\x49\x44\x41\x54\x78\x9c\xbd\x95\xb1\x4f\xc2" \
    "\x40\x18\xc5\x1f\xc4\x88\x76\x65\x32\x0c\xee\x4d" \
    "\x68\x68\x3c\xdc\xf8\x0b\x8c\x2b\x03\x5b\xcf\x15" \
    "\x0d\xab\x7f\x05\xac\x0c\xde\xee\x1f\xe0\x4e\x7a" \
    "\x84\x38\x34\x31\x61\x70\x6b\x8c\x09\xc8\x04\x1b" \
    "\x51\x16\x9e\x83\xd2\x68\x7b\xb4\x8d\x01\x5f\x72" \
    "\xd3\xcb\xf7\xcb\x77\xf7\xbd\x7c\x57\x20\x89\x7d" \
    "\xa8\xb8\x17\xea\xbf\x83\xf5\x50\x53\x4a\x49\xc7" \
    "\x71\x28\xa5\xa4\x1e\x6a\xe6\xf1\x7e\xaa\x60\x7a" \
    "\x63\x29\x25\x4f\xaf\x2e\x50\x71\x6d\x4c\x9f\x9e" \
    "\xf1\x7a\xf7\x80\x4e\xa7\x03\x00\xe8\xf5\x7a\x88" \
    "\x7b\x4a\xa9\x42\x2e\xb0\xe3\x38\xbc\x79\xbc\x07" \
    "\x00\x9c\x14\x2d\xdc\x9e\x5f\x62\x3e\x9f\x03\x00" \
    "\xca\xe5\x32\xe2\xde\x78\x3c\x4e\x80\x0f\x4c\xd7" \
    "\x10\x42\x60\x16\xbe\xe0\xf0\xf8\x08\xb3\xf7\x0f" \
    "\x08\x21\x7e\x75\x1c\xf7\x8c\x22\x99\x38\xbe\xf6" \
    "\xe9\x79\x1e\xab\xd5\x2a\x3d\xcf\xa3\xaf\x7d\x6e" \
    "\x64\xf2\x16\x8b\x05\xe3\x8c\x04\x74\xb5\x5a\xb1" \
    "\xd5\x6a\xb1\xd9\x6c\x72\xb9\x5c\x32\x4d\x61\x18" \
    "\xb2\x56\xab\xb1\xdb\xed\x26\xc0\x51\x2a\x36\xd3" \
    "\x16\x42\xa0\x54\x2a\xa1\x7d\xdd\x86\x65\x59\xe6" \
    "\x6b\x7e\x6b\xfa\x36\x85\xeb\xba\x50\x4a\x21\x9e" \
    "\x90\x68\x78\xa6\x24\x28\xa5\x52\xc1\x52\xca\xad" \
    "\x09\x89\x3a\x0e\x82\x00\x15\xd7\xfe\x1a\xde\x99" \
    "\x40\x10\x04\xa9\xd0\xac\x9a\x28\x15\xa6\x24\x64" \
    "\x29\xb5\x26\x4f\x12\xb6\x69\x4b\x8d\x39\x15\x24" \
    "\xd1\xef\xf7\x59\xaf\xd7\x39\x99\x4c\x52\xc1\x83" \
    "\xc1\x80\xb6\x6d\x73\x34\x1a\x65\xc7\xed\x2f\x39" \
    "\x5e\xaf\xd7\x09\x70\xee\x5d\xd1\x68\x34\x00\x00" \
    "\x5a\xeb\x5c\xbb\xc2\xb8\xdd\x4c\xd3\xd6\x5a\x43" \
    "\x6b\x9d\x3b\x3d\xb9\x77\xc5\xa6\x2b\x29\x25\x77" \
    "\xbd\x2b\x32\xbd\xcc\x37\xde\x85\xf6\xf6\x35\x7d" \
    "\x02\xd3\x48\x5b\xaa\x5b\x91\x0a\x0a\x00\x00\x00" \
    "\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class MoleculePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MoleculePropDialog")

        self.setIcon(self.image0)


        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(12,49,52,20))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(14,22,50,21))
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(14,191,50,27))
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(130,248,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(218,248,82,27))

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")
        self.atomsTextBrowser.setGeometry(QRect(70,49,220,136))

        self.jigsComboBox = QComboBox(0,self,"jigsComboBox")
        self.jigsComboBox.setGeometry(QRect(70,194,122,21))
        self.jigsComboBox.setSizePolicy(QSizePolicy(7,0,0,0,self.jigsComboBox.sizePolicy().hasHeightForWidth()))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(42,248,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.propPushButton = QPushButton(self,"propPushButton")
        self.propPushButton.setEnabled(0)
        self.propPushButton.setGeometry(QRect(198,191,100,27))

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setGeometry(QRect(70,22,220,23))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.languageChange()

        self.resize(QSize(318,301).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonClicked)
        self.connect(self.propPushButton,SIGNAL("clicked()"),self.propClickedButton)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)


    def languageChange(self):
        self.setCaption(self.__tr("Molecule Properties"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.textLabel3.setText(self.__tr("Jigs:"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.propPushButton.setText(self.__tr("Properties..."))
        self.nameLineEdit.setText(QString.null)


    def applyButtonClicked(self):
        print "MoleculePropDialog.applyButtonClicked(): Not implemented yet"

    def propClickedButton(self):
        print "MoleculePropDialog.propClickedButton(): Not implemented yet"

    def nameChanged(self):
        print "MoleculePropDialog.nameChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
