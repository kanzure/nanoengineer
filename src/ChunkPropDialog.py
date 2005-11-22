# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\ChunkPropDialog.ui'
#
# Created: Tue Nov 22 17:56:19 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x01" \
    "\x00\x49\x44\x41\x54\x78\x9c\xcd\x94\x3d\x8e\x85" \
    "\x20\x14\x46\x3f\x9e\xb3\x03\x0a\x17\x61\x68\x4d" \
    "\x2c\xed\x5c\x8a\x8b\x72\x55\xda\xd9\xda\x99\x60" \
    "\x61\x4c\x8c\x82\xe1\x35\x0f\x22\x0f\xf0\x67\xcc" \
    "\x24\xf3\x55\x70\x21\x87\x03\x21\x17\xf8\xef\x21" \
    "\xa1\x05\xc6\x98\xba\x03\x6a\x9a\x86\x00\xc0\x4f" \
    "\x08\x56\x96\x25\xe2\x38\x3e\x05\x15\x45\x81\x2c" \
    "\xcb\xcc\xdc\x01\x32\xc6\x54\x55\x55\x97\xac\xd2" \
    "\x34\x45\x9e\xe7\x56\xed\xf5\x5b\x58\x92\x24\x0e" \
    "\xcc\x32\x7c\x6a\x66\x01\x19\x63\xaa\xae\xeb\x4b" \
    "\x30\x00\x41\x98\x65\xd8\x75\x5d\x70\xd3\xb6\x6d" \
    "\x66\xdc\xf7\x3d\x00\x80\x52\x0a\xce\xb9\xb3\xf7" \
    "\xe5\x54\x3c\x89\xa2\xc8\xa9\xf9\x60\x96\xa1\x10" \
    "\x02\x4a\x29\x10\x42\x40\x48\xf0\x7b\x9a\x84\x0c" \
    "\x0d\x50\x5b\xac\xeb\xea\x05\x28\x65\xff\xf3\x53" \
    "\x43\xfd\x4e\xfb\xf7\x7a\x64\x28\x84\x80\x94\xd2" \
    "\x31\xf9\x8e\xbe\xc1\xa9\xe1\x1e\x7c\x94\x79\x9e" \
    "\xaf\x19\xea\xd3\x97\x65\xb9\x65\xc8\x39\x37\x8d" \
    "\xc1\x02\x8e\xe3\x08\x00\x90\x52\x1e\x02\xf5\x3a" \
    "\xa5\x14\x6d\xdb\x5a\x30\x0b\x38\x4d\x13\x86\x61" \
    "\x38\x84\xed\xe3\x83\x01\x9f\x7e\x78\xb7\xf7\x01" \
    "\xf0\xc2\xfe\x24\x6f\x83\xef\x89\x50\x2f\xd0\xee" \
    "\x65\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"

class ChunkPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("ChunkPropDialog")

        self.setIcon(self.image0)

        ChunkPropDialogLayout = QVBoxLayout(self,11,6,"ChunkPropDialogLayout")

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
        ChunkPropDialogLayout.addLayout(layout16)

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout15.addWidget(self.colorTextLabel)

        layout8 = QHBoxLayout(None,0,6,"layout8")

        self.chunk_color_frame = QLabel(self,"chunk_color_frame")
        self.chunk_color_frame.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.chunk_color_frame.sizePolicy().hasHeightForWidth()))
        self.chunk_color_frame.setMinimumSize(QSize(40,0))
        self.chunk_color_frame.setFrameShape(QLabel.Box)
        self.chunk_color_frame.setFrameShadow(QLabel.Plain)
        self.chunk_color_frame.setScaledContents(1)
        layout8.addWidget(self.chunk_color_frame)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setAutoDefault(0)
        layout8.addWidget(self.choose_color_btn)
        spacer2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout8.addItem(spacer2)
        layout15.addLayout(layout8)
        ChunkPropDialogLayout.addLayout(layout15)

        self.reset_color_btn = QPushButton(self,"reset_color_btn")
        self.reset_color_btn.setEnabled(1)
        self.reset_color_btn.setAutoDefault(0)
        ChunkPropDialogLayout.addWidget(self.reset_color_btn)

        self.make_atoms_visible_btn = QPushButton(self,"make_atoms_visible_btn")
        self.make_atoms_visible_btn.setEnabled(1)
        self.make_atoms_visible_btn.setAutoDefault(0)
        ChunkPropDialogLayout.addWidget(self.make_atoms_visible_btn)
        spacer4 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        ChunkPropDialogLayout.addItem(spacer4)

        layout13 = QHBoxLayout(None,0,6,"layout13")
        spacer3 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addItem(spacer3)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,0))
        self.ok_btn.setDefault(1)
        layout13.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,0))
        self.cancel_btn.setDefault(0)
        layout13.addWidget(self.cancel_btn)
        ChunkPropDialogLayout.addLayout(layout13)

        self.languageChange()

        self.resize(QSize(243,354).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.reset_color_btn,SIGNAL("clicked()"),self.reset_chunk_color)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_chunk_color)
        self.connect(self.make_atoms_visible_btn,SIGNAL("clicked()"),self.make_atoms_visible)

        self.setTabOrder(self.nameLineEdit,self.atomsTextBrowser)
        self.setTabOrder(self.atomsTextBrowser,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.reset_color_btn)
        self.setTabOrder(self.reset_color_btn,self.make_atoms_visible_btn)
        self.setTabOrder(self.make_atoms_visible_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Chunk Properties"))
        self.textLabel2.setText(self.__tr("Atoms:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel1.setText(self.__tr("Name:"))
        self.colorTextLabel.setText(self.__tr("Chunk Color:"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_color_btn,self.__tr("Change chunk color"))
        self.reset_color_btn.setText(self.__tr("Reset Chunk Color to Default"))
        self.make_atoms_visible_btn.setText(self.__tr("Make Invisible Atoms Visible"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def reset_chunk_color(self):
        print "ChunkPropDialog.reset_chunk_color(): Not implemented yet"

    def change_chunk_color(self):
        print "ChunkPropDialog.change_chunk_color(): Not implemented yet"

    def make_atoms_visible(self):
        print "ChunkPropDialog.make_atoms_visible(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ChunkPropDialog",s,c)
