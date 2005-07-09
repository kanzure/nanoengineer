# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\MoleculePropDialog.ui'
#
# Created: Sat Jul 9 11:25:08 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xf3\x49\x44\x41\x54\x78\x9c\xcd\x94\x31\x6e\x84" \
    "\x30\x10\x45\xff\x2e\x99\x13\xb8\xe0\x10\x68\x5a" \
    "\x24\x4a\x3a\x8e\xc2\xa1\x38\x15\x74\xb4\x74\x48" \
    "\xa6\x40\x48\x08\x30\x62\x9b\x80\x76\x64\x1c\x4c" \
    "\xa2\x28\xf9\x8d\xed\xb1\xf5\xfc\xec\x62\x80\xff" \
    "\x9e\x87\x6b\x83\x99\xb7\x3b\xa0\xaa\xaa\x1e\x00" \
    "\xf0\xe1\x82\xe5\x79\x8e\x30\x0c\x2f\x41\x59\x96" \
    "\x21\x49\x92\x63\x6d\x01\x99\x79\x2b\x8a\xc2\xcb" \
    "\x2a\x8e\x63\xa4\x69\x2a\x6a\xcf\xef\xc2\xa2\x28" \
    "\xb2\x60\xc2\xf0\xa7\x66\x02\xc8\xcc\x5b\x59\x96" \
    "\x5e\x30\x00\x4e\x98\x30\x6c\x9a\xc6\x79\x68\x5d" \
    "\xd7\x63\xde\xb6\x2d\x00\x40\x29\x05\xad\xb5\x75" \
    "\xf6\x69\x55\x4e\x12\x04\x81\x55\x3b\x83\x09\xc3" \
    "\x65\x59\x00\x00\xc6\x18\x9f\x3b\x9c\x86\x07\x90" \
    "\x88\xc4\xb8\xe7\xfd\xb9\x7f\x6b\xb8\x03\xf7\xd1" \
    "\x95\x79\x9e\xfd\x0d\x89\xe8\x12\x38\x8e\xa3\xbf" \
    "\x21\x11\x61\x9a\xa6\x5b\x86\x5a\xeb\xa3\x31\x08" \
    "\xa0\x31\x06\x7d\xdf\x5f\xfe\xe1\xbe\xaf\x94\x42" \
    "\x5d\xd7\x02\x26\x80\xc3\x30\xa0\xeb\xba\x2f\x61" \
    "\xef\x39\x83\x01\x9f\xfd\xf0\x6e\xef\x03\x70\x0a" \
    "\xfb\x95\xbc\x00\x26\x43\x89\x5f\xd0\xf4\xfb\xb7" \
    "\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class MoleculePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("MoleculePropDialog")

        self.setIcon(self.image0)

        MoleculePropDialogLayout = QVBoxLayout(self,11,6,"MoleculePropDialogLayout")

        layout16 = QGridLayout(None,1,1,0,6,"layout16")

        self.atomsTextBrowser = QTextBrowser(self,"atomsTextBrowser")

        layout16.addWidget(self.atomsTextBrowser,1,1)

        layout100 = QVBoxLayout(None,0,6,"layout100")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout100.addWidget(self.textLabel2)
        spacer1 = QSpacerItem(20,113,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout100.addItem(spacer1)

        layout16.addLayout(layout100,1,0)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout16.addWidget(self.nameLineEdit,0,1)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout16.addWidget(self.textLabel1,0,0)
        MoleculePropDialogLayout.addLayout(layout16)

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout15.addWidget(self.colorTextLabel)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(230,231,230))
        self.colorPixmapLabel.setFrameShape(QLabel.Box)
        self.colorPixmapLabel.setFrameShadow(QLabel.Plain)
        self.colorPixmapLabel.setScaledContents(1)
        layout8.addWidget(self.colorPixmapLabel)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        layout8.addWidget(self.choose_color_btn)
        spacer2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout8.addItem(spacer2)
        layout15.addLayout(layout8)
        MoleculePropDialogLayout.addLayout(layout15)

        self.reset_color_btn = QPushButton(self,"reset_color_btn")
        self.reset_color_btn.setEnabled(1)
        MoleculePropDialogLayout.addWidget(self.reset_color_btn)

        self.make_atoms_visible_btn = QPushButton(self,"make_atoms_visible_btn")
        self.make_atoms_visible_btn.setEnabled(1)
        MoleculePropDialogLayout.addWidget(self.make_atoms_visible_btn)
        spacer4 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        MoleculePropDialogLayout.addItem(spacer4)

        layout13 = QHBoxLayout(None,0,6,"layout13")
        spacer3 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addItem(spacer3)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,0))
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout13.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,0))
        self.cancel_btn.setAutoDefault(1)
        self.cancel_btn.setDefault(0)
        layout13.addWidget(self.cancel_btn)
        MoleculePropDialogLayout.addLayout(layout13)

        self.languageChange()

        self.resize(QSize(243,354).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.reset_color_btn,SIGNAL("clicked()"),self.reset_chunk_color)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.choose_color)
        self.connect(self.make_atoms_visible_btn,SIGNAL("clicked()"),self.make_atoms_visible)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel1.setText(self.__tr("Name:"))
        self.colorTextLabel.setText(self.__tr("Chunk Color:"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_color_btn,self.__tr("Change color"))
        self.reset_color_btn.setText(self.__tr("Reset Chunk Color to Default"))
        self.make_atoms_visible_btn.setText(self.__tr("Make Invisible Atoms Visible"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def reset_chunk_color(self):
        print "MoleculePropDialog.reset_chunk_color(): Not implemented yet"

    def choose_color(self):
        print "MoleculePropDialog.choose_color(): Not implemented yet"

    def make_atoms_visible(self):
        print "MoleculePropDialog.make_atoms_visible(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MoleculePropDialog",s,c)
