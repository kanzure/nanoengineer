# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\RotaryMotorPropDialog.ui'
#
# Created: Tue Mar 7 20:18:13 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x02" \
    "\xd5\x49\x44\x41\x54\x78\x9c\x95\x93\xbd\x4b\xec" \
    "\x40\x14\xc5\x4f\xe4\x15\x51\xd4\x26\x8d\x85\x0a" \
    "\xca\x04\x83\x4e\x10\x2d\x14\x4b\x21\xb3\x8b\x42" \
    "\x44\x45\x16\x65\xc5\xd6\xca\x4a\x41\x04\xad\x46" \
    "\x59\xbf\x30\xa6\x77\x6d\xd6\xca\xb0\x8d\x6c\xe3" \
    "\xc2\x6e\x1b\x3b\x85\x48\x0a\xf3\x27\x88\x58\xd8" \
    "\x04\x96\xe5\xbe\x6a\xf3\x0c\x6f\x7d\xfa\x2e\x0c" \
    "\x4c\x98\x33\xbf\xcc\x9d\x33\x47\x21\x22\xfc\xab" \
    "\x46\x47\x47\x13\x41\x18\x86\xca\x3f\xc5\x00\x3a" \
    "\xbe\x13\x00\xc0\xce\xce\xce\x4f\x64\x69\x60\x36" \
    "\x9b\x95\xa6\x69\x92\x10\x42\x02\x40\xa9\x54\x92" \
    "\xb6\x6d\xcb\xd6\xba\xa2\x28\xd8\xd8\xd8\x90\xd5" \
    "\x6a\x55\x02\x80\x10\x42\xea\xba\x4e\xd9\x6c\x56" \
    "\xa6\x88\x44\x04\x22\x02\xe7\x9c\x3c\xcf\x23\xce" \
    "\x39\xe5\xf3\x79\x39\x3e\x3e\x4e\xeb\xeb\xeb\x24" \
    "\x84\x20\xcf\xf3\x48\x08\x41\xb6\x6d\x13\xe7\x9c" \
    "\xe6\xe7\xe7\x25\x63\x8c\xea\xf5\x3a\x31\xc6\xa8" \
    "\xc5\x20\xa2\x3f\x40\xcb\xb2\x24\xe7\x9c\xea\xf5" \
    "\x3a\x09\x21\x28\x0c\xc3\x2f\x87\x10\x22\x81\x59" \
    "\x96\x25\xdb\x02\x89\x08\xf9\x7c\x5e\xb6\x60\x9e" \
    "\xe7\x51\x2e\x97\xa3\xa1\xa1\x21\x32\x0c\xa3\x2d" \
    "\xd4\xf3\xbc\x14\x8c\x88\xa0\xb4\x5c\x2e\x95\x4a" \
    "\xf2\xec\xec\x6c\xff\xe4\xe4\x04\x1f\x1f\x1f\x38" \
    "\x3f\x3f\x87\xa6\x69\xb0\x6d\x1b\xb3\xb3\xb3\xc9" \
    "\x15\xbd\xbd\xbd\x41\xd3\x34\x00\xc0\xc2\xc2\x02" \
    "\xa2\x28\x4a\x39\x9f\x98\x72\x7b\x7b\x0b\xd3\x34" \
    "\xa1\xaa\x2a\x2a\x95\x0a\xba\xba\xba\x70\x71\x71" \
    "\x91\x82\xf9\xbe\x0f\xcb\xb2\xe0\xfb\x3e\x00\xa0" \
    "\xb7\xb7\x17\x6b\x6b\x6b\x29\x53\x3a\x4c\xd3\x24" \
    "\xd3\x34\x29\x8a\xa2\xfd\xd7\xd7\x57\xf4\xf5\xf5" \
    "\xe1\xfe\xfe\x1e\x8b\x8b\x8b\x29\xf3\x7c\xdf\x47" \
    "\xa1\x50\x40\x77\x77\x37\xb6\xb6\xb6\xe0\xfb\x3e" \
    "\x6e\x6e\x6e\xf0\xfe\xfe\xbe\xaf\xeb\x3a\xe9\xba" \
    "\x4e\x00\xf0\x2b\x8e\x63\xec\xed\xed\x01\x00\x66" \
    "\x66\x66\x00\x00\x9d\x9d\x9d\xe8\xef\xef\x4f\x01" \
    "\x0b\x85\x42\x32\x6f\x36\x9b\x38\x3a\x3a\x42\xa5" \
    "\x52\x41\x2e\x97\x4b\xad\xff\x52\x55\x15\x8e\xe3" \
    "\xa0\xd1\x68\x60\x70\x70\x10\xae\xeb\xa2\xa7\xa7" \
    "\x07\xcf\xcf\xcf\x18\x1b\x1b\x4b\x20\x77\x77\x77" \
    "\xa8\xd5\x6a\x38\x38\x38\xc0\xe3\xe3\x23\x00\xe0" \
    "\xe1\xe1\x01\xe5\x72\x19\x2f\x2f\x2f\x7f\x5a\x0e" \
    "\x82\x40\x09\x82\x40\x99\x9a\x9a\x3a\x54\x55\x15" \
    "\x00\x30\x31\x31\x81\x72\xb9\x8c\xa7\xa7\xa7\xd4" \
    "\x29\x1b\x8d\x06\x86\x87\x87\x93\xef\xd3\xd3\x53" \
    "\x68\x9a\x76\x18\x45\x91\x92\x98\xf3\xd9\xf2\x91" \
    "\x91\x91\xe4\x59\x2c\x2d\x2d\x91\xae\xeb\xb4\xb9" \
    "\xb9\x49\xae\xeb\xd2\xca\xca\x0a\x0d\x0c\x0c\xd0" \
    "\xf6\xf6\x36\x85\x61\x48\x8e\xe3\x90\x61\x18\xf4" \
    "\xe5\xb3\x01\x80\xb9\xb9\x39\xd9\x6c\x36\xf7\x5d" \
    "\xd7\x05\x00\x54\xab\x55\xd4\x6a\x35\xc4\x71\x0c" \
    "\x55\x55\x31\x3d\x3d\x8d\xe5\xe5\x65\x04\x41\x80" \
    "\xab\xab\x2b\x4c\x4e\x4e\x1e\x1e\x1f\x1f\x1f\xa4" \
    "\xda\xf8\x2a\x29\xc5\x62\xb1\x6d\x4a\x1c\xc7\xf9" \
    "\x59\x52\x5a\x30\xce\x39\xad\xae\xae\x4a\xc6\x18" \
    "\x31\xc6\x92\xcd\x42\x08\x32\x0c\x83\x0c\xc3\xa0" \
    "\xdd\xdd\xdd\xef\xb3\x9c\xc9\x64\x24\xe7\x3c\xf5" \
    "\xc7\xcb\xcb\x4b\xc9\x18\xa3\x62\xb1\x48\x8c\x31" \
    "\xba\xbe\xbe\x96\x9f\x3b\x62\x8c\x51\x26\x93\xf9" \
    "\x3a\xcb\xed\xc6\x67\xe0\x77\xda\xbf\x4c\x69\x57" \
    "\xba\xae\x93\xaa\xaa\x88\xe3\xf8\xaf\xdc\xb6\xab" \
    "\x6f\x81\xff\x5b\xbf\x01\xcc\x4b\x51\xfe\x29\x59" \
    "\xb9\x97\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"

class RotaryMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("RotaryMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        RotaryMotorPropDialogLayout = QGridLayout(self,1,1,11,6,"RotaryMotorPropDialogLayout")

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QGridLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        layout76 = QHBoxLayout(None,0,6,"layout76")

        layout75 = QHBoxLayout(None,0,6,"layout75")

        self.jig_color_pixmap = QLabel(self.groupBox1,"jig_color_pixmap")
        self.jig_color_pixmap.setMinimumSize(QSize(40,0))
        self.jig_color_pixmap.setPaletteBackgroundColor(QColor(175,175,175))
        self.jig_color_pixmap.setScaledContents(1)
        layout75.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QPushButton(self.groupBox1,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setAutoDefault(0)
        layout75.addWidget(self.choose_color_btn)
        layout76.addLayout(layout75)
        spacer5 = QSpacerItem(46,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout76.addItem(spacer5)

        groupBox1Layout.addMultiCellLayout(layout76,3,3,1,2)

        self.textLabel1_2_2_2 = QLabel(self.groupBox1,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox1Layout.addWidget(self.textLabel1_2_2_2,2,0)

        self.textLabel1_3 = QLabel(self.groupBox1,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox1Layout.addWidget(self.textLabel1_3,0,0)

        self.textLabel1_2_2 = QLabel(self.groupBox1,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox1Layout.addWidget(self.textLabel1_2_2,1,0)

        self.colorTextLabel = QLabel(self.groupBox1,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox1Layout.addWidget(self.colorTextLabel,3,0)

        self.lengthLineEdit = QLineEdit(self.groupBox1,"lengthLineEdit")
        self.lengthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.lengthLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox1Layout.addWidget(self.lengthLineEdit,0,1)

        self.sradiusLineEdit = QLineEdit(self.groupBox1,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox1Layout.addWidget(self.sradiusLineEdit,2,1)

        self.radiusLineEdit = QLineEdit(self.groupBox1,"radiusLineEdit")
        self.radiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox1Layout.addWidget(self.radiusLineEdit,1,1)

        self.textLabel3_2 = QLabel(self.groupBox1,"textLabel3_2")

        groupBox1Layout.addWidget(self.textLabel3_2,1,2)

        self.textLabel3 = QLabel(self.groupBox1,"textLabel3")

        groupBox1Layout.addWidget(self.textLabel3,0,2)

        self.textLabel3_3 = QLabel(self.groupBox1,"textLabel3_3")

        groupBox1Layout.addWidget(self.textLabel3_3,2,2)

        RotaryMotorPropDialogLayout.addWidget(self.groupBox1,1,0)
        spacer6 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        RotaryMotorPropDialogLayout.addItem(spacer6,2,0)

        layout45 = QHBoxLayout(None,0,6,"layout45")
        spacer7 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout45.addItem(spacer7)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setAutoDefault(0)
        self.ok_btn.setDefault(0)
        layout45.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setAutoDefault(0)
        layout45.addWidget(self.cancel_btn)

        RotaryMotorPropDialogLayout.addLayout(layout45,3,0)

        layout14 = QGridLayout(None,1,1,0,6,"layout14")

        layout11 = QVBoxLayout(None,0,6,"layout11")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.nameTextLabel)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.textLabel1)

        self.textLabel1_2_3 = QLabel(self,"textLabel1_2_3")
        self.textLabel1_2_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.textLabel1_2_3)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.textLabel1_2)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.textLabel1_5)

        layout14.addLayout(layout11,0,0)

        layout13 = QGridLayout(None,1,1,0,6,"layout13")

        self.enable_minimize_checkbox = QCheckBox(self,"enable_minimize_checkbox")

        layout13.addWidget(self.enable_minimize_checkbox,4,0)

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout13.addWidget(self.textLabel1_4,1,2)

        self.initialSpeedLineEdit = QLineEdit(self,"initialSpeedLineEdit")
        self.initialSpeedLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.initialSpeedLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.initialSpeedLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout13.addMultiCellWidget(self.initialSpeedLineEdit,2,2,0,1)

        self.textLabel2_2 = QLabel(self,"textLabel2_2")

        layout13.addWidget(self.textLabel2_2,2,2)
        spacer16 = QSpacerItem(111,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addMultiCell(spacer16,4,4,1,2)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)

        layout13.addMultiCellWidget(self.nameLineEdit,0,0,0,2)

        self.speedLineEdit = QLineEdit(self,"speedLineEdit")
        self.speedLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.speedLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.speedLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout13.addMultiCellWidget(self.speedLineEdit,3,3,0,1)

        self.torqueLineEdit = QLineEdit(self,"torqueLineEdit")
        self.torqueLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout13.addMultiCellWidget(self.torqueLineEdit,1,1,0,1)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout13.addWidget(self.textLabel2,3,2)

        layout14.addLayout(layout13,0,1)

        RotaryMotorPropDialogLayout.addLayout(layout14,0,0)

        self.languageChange()

        self.resize(QSize(280,340).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_jig_color)
        self.connect(self.lengthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.radiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.sradiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)

        self.setTabOrder(self.nameLineEdit,self.torqueLineEdit)
        self.setTabOrder(self.torqueLineEdit,self.initialSpeedLineEdit)
        self.setTabOrder(self.initialSpeedLineEdit,self.speedLineEdit)
        self.setTabOrder(self.speedLineEdit,self.enable_minimize_checkbox)
        self.setTabOrder(self.enable_minimize_checkbox,self.lengthLineEdit)
        self.setTabOrder(self.lengthLineEdit,self.radiusLineEdit)
        self.setTabOrder(self.radiusLineEdit,self.sradiusLineEdit)
        self.setTabOrder(self.sradiusLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.groupBox1.setTitle(self.__tr("Size and Color"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius :"))
        self.textLabel1_3.setText(self.__tr("Motor Length :"))
        self.textLabel1_2_2.setText(self.__tr("Motor Radius :"))
        self.colorTextLabel.setText(self.__tr("Color :"))
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))
        self.nameTextLabel.setText(self.__tr("Name :"))
        self.textLabel1.setText(self.__tr("Torque :"))
        self.textLabel1_2_3.setText(self.__tr("Initial Speed :"))
        self.textLabel1_2.setText(self.__tr("Final Speed :"))
        self.textLabel1_5.setText(self.__tr("Enable in Minimize :"))
        self.enable_minimize_checkbox.setText(QString.null)
        self.textLabel1_4.setText(self.__tr("nN-nm"))
        self.textLabel2_2.setText(self.__tr("GHz"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(self.__tr("GHz"))


    def change_jig_color(self):
        print "RotaryMotorPropDialog.change_jig_color(): Not implemented yet"

    def change_motor_size(self):
        print "RotaryMotorPropDialog.change_motor_size(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("RotaryMotorPropDialog",s,c)
