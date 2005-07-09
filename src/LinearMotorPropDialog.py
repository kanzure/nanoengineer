# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LinearMotorPropDialog.ui'
#
# Created: Sat Jul 9 00:00:28 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xda\x49\x44\x41\x54\x78\x9c\xcd\x95\x31\x0e\x83" \
    "\x30\x0c\x45\xbf\x2b\x4e\xe5\xc9\x23\x67\xf2\x01" \
    "\x38\x97\x27\x9f\x80\x9d\x85\x9d\x0d\xb1\xb9\x43" \
    "\x4b\x80\x16\x5a\x52\x05\xa9\x5f\x62\x30\x76\x1e" \
    "\x0e\x7c\x13\x72\x77\x5c\xa1\xdb\x25\xd4\xbf\x07" \
    "\x33\x73\xa8\x6a\x14\x07\x03\x80\x99\x61\x0d\xaf" \
    "\x72\x3b\x3b\xca\x45\x04\x88\x28\xc5\x59\x60\x11" \
    "\xd9\xbd\x6f\x66\x20\xa2\x4d\x9e\x4a\xd8\x8d\x99" \
    "\x43\x44\xd0\x34\x4d\x6a\xb9\x08\x78\x57\x4f\x70" \
    "\xcc\x57\x89\xd8\xdd\x17\xf0\x30\x0c\xb1\x2e\xc8" \
    "\x8d\xbb\xae\xdb\xc0\xc9\xdd\xc1\xcc\xd1\xb6\xed" \
    "\xdb\x6e\xc6\x71\x3c\xb5\xeb\x75\x9d\x88\xc0\xdd" \
    "\x29\xb9\xa2\xef\xfb\xc3\x85\xd3\x34\x9d\x7a\xc0" \
    "\xba\x2e\x81\xeb\xba\x3e\xb5\xf8\xac\x2e\x73\x45" \
    "\x1a\x69\x55\x8d\x4f\x93\xf5\x13\x58\x55\xc3\xcc" \
    "\x4a\x31\x01\x60\x71\xc5\xeb\xac\xbf\xca\xdd\x8f" \
    "\x93\x3b\xaa\x80\x87\x45\x66\xe8\xd1\xff\x20\x57" \
    "\xe9\xe3\xcd\xaf\x23\xb7\xb3\xaf\xe0\xd2\xba\xec" \
    "\x68\xba\x03\xf1\x15\x9c\x20\xb2\x0c\x57\xde\x00" \
    "\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class LinearMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("LinearMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        LinearMotorPropDialogLayout = QVBoxLayout(self,11,6,"LinearMotorPropDialogLayout")

        layout78 = QHBoxLayout(None,0,6,"layout78")

        layout40 = QVBoxLayout(None,0,6,"layout40")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.nameTextLabel)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.textLabel1)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.textLabel1_2)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.textLabel1_3)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.textLabel1_2_2)

        self.textLabel1_2_2_2 = QLabel(self,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.textLabel1_2_2_2)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.colorTextLabel)
        layout78.addLayout(layout40)

        layout77 = QVBoxLayout(None,0,6,"layout77")

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)
        layout77.addWidget(self.nameLineEdit)

        layout46 = QGridLayout(None,1,1,0,6,"layout46")

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout46.addWidget(self.forceLineEdit,0,0)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")

        layout46.addWidget(self.textLabel3_2,3,1)

        self.widthLineEdit = QLineEdit(self,"widthLineEdit")
        self.widthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout46.addWidget(self.widthLineEdit,3,0)

        self.lengthLineEdit = QLineEdit(self,"lengthLineEdit")
        self.lengthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.lengthLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout46.addWidget(self.lengthLineEdit,2,0)

        self.sradiusLineEdit = QLineEdit(self,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout46.addWidget(self.sradiusLineEdit,4,0)

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout46.addWidget(self.textLabel1_4,0,1)

        self.textLabel3_3 = QLabel(self,"textLabel3_3")

        layout46.addWidget(self.textLabel3_3,4,1)

        self.textLabel3 = QLabel(self,"textLabel3")

        layout46.addWidget(self.textLabel3,2,1)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout46.addWidget(self.textLabel2,1,1)

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.stiffnessLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.stiffnessLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout46.addWidget(self.stiffnessLineEdit,1,0)
        layout77.addLayout(layout46)

        layout76 = QHBoxLayout(None,0,6,"layout76")

        layout75 = QHBoxLayout(None,0,6,"layout75")

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)
        layout75.addWidget(self.colorPixmapLabel)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        layout75.addWidget(self.choose_color_btn)
        layout76.addLayout(layout75)
        spacer5 = QSpacerItem(46,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout76.addItem(spacer5)
        layout77.addLayout(layout76)
        layout78.addLayout(layout77)
        LinearMotorPropDialogLayout.addLayout(layout78)
        spacer6 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        LinearMotorPropDialogLayout.addItem(spacer6)

        layout45 = QHBoxLayout(None,0,6,"layout45")
        spacer7 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout45.addItem(spacer7)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout45.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setAutoDefault(1)
        layout45.addWidget(self.cancel_btn)
        LinearMotorPropDialogLayout.addLayout(layout45)

        self.languageChange()

        self.resize(QSize(306,285).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.ok_btn,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.choose_color)

        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.textLabel1.setText(self.__tr("Force:"))
        self.textLabel1_2.setText(self.__tr("Stiffness"))
        self.textLabel1_3.setText(self.__tr("Motor Length:"))
        self.textLabel1_2_2.setText(self.__tr("Motor Width:"))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel1_4.setText(self.__tr("pN"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.textLabel2.setText(self.__tr("N/m"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def choose_color(self):
        print "LinearMotorPropDialog.choose_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
