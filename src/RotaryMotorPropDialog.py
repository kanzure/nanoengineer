# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RotaryMotorPropDialog.ui'
#
# Created: Tue Sep 13 16:00:27 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x03" \
    "\x1e\x49\x44\x41\x54\x78\x9c\xb5\x94\x4f\x48\x2a" \
    "\x6d\x14\xc6\x7f\x73\x09\xb2\x48\x69\x29\x29\x51" \
    "\x6e\x8a\xfe\x40\x05\x15\x77\x59\xb4\x37\x5a\x44" \
    "\x8b\x10\x22\x18\x68\x91\x12\xb9\x99\x22\x35\x29" \
    "\x06\x84\x12\x25\x11\xa4\x36\x11\x04\x86\x2d\x42" \
    "\x02\x03\x57\x41\xd3\x1f\x22\xc8\xda\x94\xa4\x10" \
    "\x88\x14\x91\xb4\x12\x44\xe6\x5b\x35\x5c\xf5\xde" \
    "\x8b\x1f\x7c\xdf\xb3\x3a\xc3\xfb\x9c\x67\x9e\xf3" \
    "\x9e\x73\x5e\xe1\xe2\xe2\x82\xff\x03\x0d\xf5\x90" \
    "\xe6\xe7\xe7\xd5\xef\x78\x6f\x6f\x4f\xa8\x27\xe7" \
    "\x47\xbd\x0e\x9c\x4e\x67\xbd\x54\xa0\xca\xb1\xc7" \
    "\xe3\x51\x73\xb9\x1c\x46\xa3\x11\xaf\xd7\x2b\xa4" \
    "\xd3\x69\x35\x1a\x8d\x6a\xe7\x82\x20\x10\x0e\x87" \
    "\xd5\xd9\xd9\x59\xf4\x7a\xbd\xe0\x72\xb9\xd4\x6c" \
    "\x36\x8b\xc5\x62\xc1\xe3\xf1\x54\x54\x52\xe1\x38" \
    "\x97\xcb\xe1\x76\xbb\xc9\xe7\xf3\x84\x42\x21\x75" \
    "\x6b\x6b\x8b\xd6\xd6\x56\xcc\x66\x33\x06\x83\x01" \
    "\x93\xc9\x44\xa1\x50\x60\x79\x79\x99\x8d\x8d\x0d" \
    "\x35\x9b\xcd\x12\x89\x44\x78\x79\x79\xf9\xbb\x63" \
    "\xa3\xd1\xc8\xfa\xfa\x3a\xc1\x60\x10\x59\x96\x39" \
    "\x3c\x3c\xac\x20\x07\x02\x01\x2d\x76\x38\x1c\x44" \
    "\x22\x11\x44\x51\xa4\xa3\xa3\xa3\x46\x58\xa8\x9e" \
    "\x8a\x50\x28\xa4\xbe\xbd\xbd\x11\x08\x04\x78\x7c" \
    "\x7c\xe4\xe8\xe8\x88\x9b\x9b\x1b\x1a\x1b\x1b\x39" \
    "\x3e\x3e\xae\xe0\x3a\x1c\x0e\x44\x51\xc4\x64\x32" \
    "\xd5\x34\xb4\xe2\x2a\xd2\xe9\xb4\x7a\x7f\x7f\xcf" \
    "\xd2\xd2\x12\xa9\x54\x0a\x9f\xcf\xc7\xd7\xd7\x17" \
    "\x4e\xa7\xb3\x42\xf4\xe3\xe3\x43\xab\x40\x92\xa4" \
    "\x1a\xb7\x35\xc2\xd1\x68\x94\xfe\xfe\x7e\x74\x3a" \
    "\x1d\xf1\x78\x9c\xe6\xe6\x66\xb6\xb7\xb7\x19\x1b" \
    "\x1b\xd3\x38\x8a\xa2\x30\x31\x31\x81\xa2\x28\x00" \
    "\x18\x0c\x06\x82\xc1\xa0\x4a\x15\x7e\x00\x88\xa2" \
    "\xa8\x8a\xa2\xa8\x3e\x3f\x3f\xf3\xfe\xfe\x8e\xd1" \
    "\x68\x24\x91\x48\x30\x39\x39\x59\x41\x56\x14\x05" \
    "\x59\x96\x69\x69\x69\x61\x71\x71\x11\x45\x51\x38" \
    "\x38\x38\xe0\xf3\xf3\x13\x9b\xcd\xa6\xda\x6c\x36" \
    "\xed\x07\x0d\x00\xc5\x62\x51\x2b\xe9\xe7\xcf\x9f" \
    "\x00\x34\x35\x35\x61\x36\x9b\x2b\x84\x65\x59\xd6" \
    "\xe2\x72\xb9\xcc\xe6\xe6\x26\xf1\x78\x9c\xe9\xe9" \
    "\xe9\x9a\xf3\x06\x00\x9d\x4e\x87\xdf\xef\xa7\x54" \
    "\x2a\xd1\xde\xde\x4e\x20\x10\x40\xaf\xd7\xf3\xf0" \
    "\xf0\x40\x6f\x6f\xaf\x46\x3e\x39\x39\x21\x99\x4c" \
    "\xb2\xb6\xb6\xc6\xdd\xdd\x1d\x00\x97\x97\x97\xc4" \
    "\x62\x31\x9e\x9e\x9e\x2a\x4c\x34\x00\x44\x22\x11" \
    "\x01\x20\x1c\x0e\xab\x85\x42\x01\x80\xc1\xc1\x41" \
    "\x62\xb1\x18\x5d\x5d\x5d\x0c\x0c\x0c\x68\x09\xa5" \
    "\x52\x09\x8b\xc5\xa2\x7d\xfb\x7c\x3e\x86\x87\x87" \
    "\xd9\xdf\xdf\x17\x6a\x84\xbf\xb1\xb0\xb0\x20\xcc" \
    "\xcd\xcd\xa9\x00\x92\x24\xb1\xba\xba\x8a\xdb\xed" \
    "\x66\x7c\x7c\x9c\x9e\x9e\x1e\xce\xcf\xcf\xb9\xba" \
    "\xba\xd2\x4a\x4f\x24\x12\x5a\x1e\x55\xa8\x99\x63" \
    "\xaf\xd7\xab\x96\xcb\x65\x6d\x19\xce\xce\xce\x48" \
    "\x26\x93\x14\x8b\x45\x74\x3a\x1d\xa3\xa3\xa3\x4c" \
    "\x4d\x4d\x91\x4a\xa5\xd8\xdd\xdd\x65\x68\x68\x08" \
    "\xab\xd5\xfa\x77\x61\x97\xcb\xa5\xe6\xf3\x79\x6d" \
    "\xf3\x66\x66\x66\xb4\x66\xfe\x8a\x44\x22\xc1\xe9" \
    "\xe9\x29\x92\x24\x69\x9b\xe7\xf5\x7a\xff\x7c\x15" \
    "\xdf\xa2\x76\xbb\x9d\xbe\xbe\x3e\xad\xcb\x9d\x9d" \
    "\x9d\x48\x92\x84\x2c\xcb\xbc\xbe\xbe\x02\x60\xb5" \
    "\x5a\x11\x45\x51\x5b\xeb\x6a\x54\x08\xb7\xb5\xb5" \
    "\x61\xb7\xdb\x31\x1a\x8d\xd8\xed\x76\x01\xe0\xfa" \
    "\xfa\x5a\xdd\xd9\xd9\x21\x93\xc9\x90\xc9\x64\x58" \
    "\x59\x59\xa1\xbb\xbb\x5b\x00\xb8\xbd\xbd\x55\x45" \
    "\x51\xac\x68\xe6\x6f\x85\xab\x9f\x3e\x80\x91\x91" \
    "\x11\x01\xd0\x06\xff\x5b\x14\xa8\x29\xff\x57\xd4" \
    "\xfd\xd0\xfb\xfd\xfe\x7a\xa9\xc0\x6f\xa6\xe2\xbf" \
    "\x42\xdd\x8e\xff\x2d\xfe\x01\xd6\x23\x4d\x14\xd1" \
    "\x7e\x8f\x6b\x00\x00\x00\x00\x49\x45\x4e\x44\xae" \
    "\x42\x60\x82"

class RotaryMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("RotaryMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        RotaryMotorPropDialogLayout = QVBoxLayout(self,11,6,"RotaryMotorPropDialogLayout")

        layout82 = QHBoxLayout(None,0,6,"layout82")

        layout27 = QVBoxLayout(None,0,6,"layout27")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.nameTextLabel)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.textLabel1)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.textLabel1_2)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.textLabel1_3)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.textLabel1_2_2)

        self.textLabel1_2_2_2 = QLabel(self,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.textLabel1_2_2_2)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout27.addWidget(self.colorTextLabel)
        layout82.addLayout(layout27)

        layout81 = QVBoxLayout(None,0,6,"layout81")

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)
        layout81.addWidget(self.nameLineEdit)

        layout33 = QGridLayout(None,1,1,0,6,"layout33")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout33.addWidget(self.textLabel1_4,0,1)

        self.torqueLineEdit = QLineEdit(self,"torqueLineEdit")
        self.torqueLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout33.addWidget(self.torqueLineEdit,0,0)

        self.textLabel3 = QLabel(self,"textLabel3")

        layout33.addWidget(self.textLabel3,2,1)

        self.radiusLineEdit = QLineEdit(self,"radiusLineEdit")
        self.radiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout33.addWidget(self.radiusLineEdit,3,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout33.addWidget(self.textLabel2,1,1)

        self.lengthLineEdit = QLineEdit(self,"lengthLineEdit")
        self.lengthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.lengthLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout33.addWidget(self.lengthLineEdit,2,0)

        self.textLabel3_2 = QLabel(self,"textLabel3_2")

        layout33.addWidget(self.textLabel3_2,3,1)

        self.speedLineEdit = QLineEdit(self,"speedLineEdit")
        self.speedLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.speedLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.speedLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout33.addWidget(self.speedLineEdit,1,0)

        self.textLabel3_3 = QLabel(self,"textLabel3_3")

        layout33.addWidget(self.textLabel3_3,4,1)

        self.sradiusLineEdit = QLineEdit(self,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout33.addWidget(self.sradiusLineEdit,4,0)
        layout81.addLayout(layout33)

        layout80 = QHBoxLayout(None,0,6,"layout80")

        layout79 = QHBoxLayout(None,0,6,"layout79")

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(175,175,175))
        self.colorPixmapLabel.setScaledContents(1)
        layout79.addWidget(self.colorPixmapLabel)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        layout79.addWidget(self.choose_color_btn)
        layout80.addLayout(layout79)
        spacer3 = QSpacerItem(49,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout80.addItem(spacer3)
        layout81.addLayout(layout80)
        layout82.addLayout(layout81)
        RotaryMotorPropDialogLayout.addLayout(layout82)
        spacer4 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        RotaryMotorPropDialogLayout.addItem(spacer4)

        layout23 = QHBoxLayout(None,0,6,"layout23")
        spacer1 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout23.addItem(spacer1)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout23.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setAutoDefault(1)
        layout23.addWidget(self.cancel_btn)
        RotaryMotorPropDialogLayout.addLayout(layout23)

        self.languageChange()

        self.resize(QSize(309,281).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.choose_color)

        self.setTabOrder(self.nameLineEdit,self.torqueLineEdit)
        self.setTabOrder(self.torqueLineEdit,self.speedLineEdit)
        self.setTabOrder(self.speedLineEdit,self.lengthLineEdit)
        self.setTabOrder(self.lengthLineEdit,self.radiusLineEdit)
        self.setTabOrder(self.radiusLineEdit,self.sradiusLineEdit)
        self.setTabOrder(self.sradiusLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.textLabel1.setText(self.__tr("Torque:"))
        self.textLabel1_2.setText(self.__tr("Speed:"))
        self.textLabel1_3.setText(self.__tr("Motor Length:"))
        self.textLabel1_2_2.setText(self.__tr("Motor Radius:"))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel1_4.setText(self.__tr("nN-nm"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.textLabel2.setText(self.__tr("GHz"))
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def choose_color(self):
        print "RotaryMotorPropDialog.choose_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("RotaryMotorPropDialog",s,c)
