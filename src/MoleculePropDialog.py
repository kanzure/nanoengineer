# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/MoleculePropDialog.ui'
#
# Created: Thu Jan 13 19:36:34 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\xa4\x49\x44\x41\x54\x18\x95\xb5\x95\xc1\x6a\x1a" \
    "\x51\x14\x86\x3f\x1b\xa9\xad\xf3\x08\x2e\xb2\x4e" \
    "\x32\x08\xe2\x05\xa5\x34\x0f\x70\xc9\xd2\x07\x90" \
    "\x99\xe0\x46\x92\xe2\x26\xef\xe1\xa2\x8b\x94\x99" \
    "\xce\xc5\x65\x57\x3e\x83\xdc\x20\x5d\x5c\xe8\x42" \
    "\x28\x42\x53\xbb\x32\x79\x84\x66\x71\xe5\x76\x51" \
    "\x14\x53\x6f\x46\x0b\xfa\x2f\xe7\xe7\x7c\x1c\xce" \
    "\xf9\xef\x99\xc2\x78\x3c\xe6\x10\x7a\x75\x10\xea" \
    "\x21\xc1\x45\xdf\x47\xbb\xb0\x4e\x65\x0a\x63\x0c" \
    "\x42\x08\xa2\x38\xa2\x78\x54\x2c\x6c\xf3\xb6\x76" \
    "\xac\x32\xc5\xf1\xe5\x05\x1f\xbe\x7e\xe1\xf8\xf2" \
    "\x02\x95\x29\x82\x20\x70\x41\x10\x38\x9f\xe7\x93" \
    "\x17\x6c\x8c\xa1\x52\x3b\x05\x40\xd4\x05\xc6\x18" \
    "\xa4\x94\x48\x29\xbd\xde\xce\xa3\x10\x42\xf0\xf8" \
    "\xf3\x17\xaf\xdf\xbe\xe1\xf1\xf7\x13\x42\x08\x7a" \
    "\xbd\x1e\x00\xfd\x7e\x7f\xc3\xf3\xa9\xe0\x8b\x9b" \
    "\x6f\x8e\xe7\xef\xcf\x01\xd0\x77\x9a\x7f\xbd\xf0" \
    "\x2c\x64\x3a\x9d\x16\x72\xc1\xf5\x7a\xdd\x45\x51" \
    "\x84\xb5\x16\xa5\x14\xe5\x72\xd9\xdb\x11\xc0\x6c" \
    "\x36\xa3\xd5\x6a\xd1\x6e\xb7\x69\x34\x1a\xcf\xc0" \
    "\xab\x19\xdb\x85\x75\x49\x92\x38\x21\x04\xa5\x52" \
    "\x89\xab\xeb\xab\x5c\x28\xc0\xfc\x61\x4e\xad\x56" \
    "\x23\xcb\x32\x92\x24\x71\x76\x61\xdd\x06\x78\xd7" \
    "\x6d\xaf\x2b\xaf\x66\x05\xde\x75\xdb\xeb\xca\xab" \
    "\x59\xa5\xc2\x97\x84\x6d\xca\xab\x59\x2d\x2f\x2f" \
    "\x09\x2f\xc9\x97\x90\xe5\x2b\xf4\xc6\x6d\x32\x99" \
    "\xb8\x34\x4d\x19\x0e\x87\x54\x2a\x95\x17\xc1\xa3" \
    "\xd1\x88\x6e\xb7\x4b\x9a\xa6\x00\xfe\x54\xac\xeb" \
    "\xe4\xf4\x84\x30\x0c\x91\x52\x12\xc7\x31\xfa\x4e" \
    "\x3f\xeb\x32\x8e\x63\xaa\xd5\x2a\x83\xc1\x80\xdb" \
    "\x4f\xb7\x34\x9b\xcd\x0d\x86\xf7\xe5\x2d\xb7\xfd" \
    "\xee\xe3\x0d\xf3\x6f\xdf\x51\x9f\x15\xf7\x3f\xee" \
    "\xff\x82\xb5\xde\xf0\x76\x3e\x42\xbe\x6d\x6b\xad" \
    "\xd1\x5a\xef\xff\x56\x74\x3a\x9d\x65\x57\x6e\xaf" \
    "\xb7\xe2\x7f\xef\xb1\x17\xbc\x0f\x1d\xec\xd7\xf4" \
    "\x07\xc9\x62\x26\x86\xe6\x78\x0f\x76\x00\x00\x00" \
    "\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class MoleculePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MoleculePropDialog")

        self.setIcon(self.image0)

        MoleculePropDialogLayout = QGridLayout(self,1,1,11,6,"MoleculePropDialogLayout")

        layout9 = QHBoxLayout(None,0,6,"layout9")

        layout100 = QVBoxLayout(None,0,6,"layout100")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout100.addWidget(self.textLabel2)
        spacer1 = QSpacerItem(20,113,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout100.addItem(spacer1)
        layout9.addLayout(layout100)

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")
        layout9.addWidget(self.atomsTextBrowser)

        MoleculePropDialogLayout.addLayout(layout9,1,0)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout8.addWidget(self.textLabel1)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout8.addWidget(self.nameLineEdit)

        MoleculePropDialogLayout.addLayout(layout8,0,0)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,0))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout7.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,0))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout7.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setMinimumSize(QSize(0,0))
        layout7.addWidget(self.applyPushButton)

        MoleculePropDialogLayout.addLayout(layout7,3,0)

        layout10 = QVBoxLayout(None,0,6,"layout10")

        layout9_2 = QHBoxLayout(None,0,6,"layout9_2")

        layout8_2 = QHBoxLayout(None,0,6,"layout8_2")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout8_2.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(30,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(230,231,230))
        self.colorPixmapLabel.setFrameShape(QLabel.Box)
        self.colorPixmapLabel.setFrameShadow(QLabel.Plain)
        self.colorPixmapLabel.setScaledContents(1)
        layout8_2.addWidget(self.colorPixmapLabel)
        layout9_2.addLayout(layout8_2)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        layout9_2.addWidget(self.colorSelectorPushButton)
        layout10.addLayout(layout9_2)

        self.resetChunkColor = QPushButton(self,"resetChunkColor")
        self.resetChunkColor.setEnabled(1)
        layout10.addWidget(self.resetChunkColor)

        self.makeAtomsVisiblePB = QPushButton(self,"makeAtomsVisiblePB")
        self.makeAtomsVisiblePB.setEnabled(1)
        layout10.addWidget(self.makeAtomsVisiblePB)

        MoleculePropDialogLayout.addLayout(layout10,2,0)

        self.languageChange()

        self.resize(QSize(360,348).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonClicked)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.nameChanged)
        self.connect(self.resetChunkColor,SIGNAL("clicked()"),self.setMol2ElementColors)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeMolColor)
        self.connect(self.makeAtomsVisiblePB,SIGNAL("clicked()"),self.makeAtomsVisible)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.textLabel1.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.applyPushButton.setAccel(QString.null)
        self.colorTextLabel.setText(self.__tr("Chunk Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.resetChunkColor.setText(self.__tr("Reset Chunk Color to Default"))
        self.makeAtomsVisiblePB.setText(self.__tr("Make Invisible Atoms Visible"))


    def applyButtonClicked(self):
        print "MoleculePropDialog.applyButtonClicked(): Not implemented yet"

    def nameChanged(self):
        print "MoleculePropDialog.nameChanged(): Not implemented yet"

    def setMol2ElementColors(self):
        print "MoleculePropDialog.setMol2ElementColors(): Not implemented yet"

    def changeMolColor(self):
        print "MoleculePropDialog.changeMolColor(): Not implemented yet"

    def makeAtomsVisible(self):
        print "MoleculePropDialog.makeAtomsVisible(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
