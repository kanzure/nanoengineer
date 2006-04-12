# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LinearMotorPropDialog.ui'
#
# Created: Wed Apr 12 10:35:27 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xbe\x49\x44\x41\x54\x38\x8d\xad\x53\x3b\x0e\x85" \
    "\x30\x0c\xb3\x11\x07\x4b\x4f\x46\xb9\x19\x87\x60" \
    "\x67\x61\x67\x43\x6c\x66\xa1\xbc\xea\x3d\xfa\xd4" \
    "\x8a\x58\x8a\xd4\x7c\xea\xc6\x89\x4a\x49\xf0\x44" \
    "\xe7\xca\xe6\x41\x48\x52\x21\x84\x78\x07\x24\xbd" \
    "\x32\x00\x02\x20\x33\x8b\x92\xc0\xda\x19\x92\x2c" \
    "\x16\x4a\x02\x49\x48\x62\x5f\x2b\xcd\xcc\xc6\xa7" \
    "\xf8\x34\x4d\x03\xc9\x4f\xde\x43\x72\x92\xdb\x24" \
    "\xb9\x05\x4a\x96\x0f\xf9\x85\x0f\x6d\xdb\xa6\x3c" \
    "\xd1\xea\x2f\xcb\x72\x9f\x09\x40\xf3\x3c\xff\xb4" \
    "\xbd\xef\x7b\x95\xbc\xbc\xce\xcc\xd0\x03\xc0\xba" \
    "\xae\xc5\x0b\xc7\x71\x54\x11\xa7\x3a\x5e\xad\xba" \
    "\xc1\x7d\xcb\x1d\x00\x84\x10\xe2\xbf\x9f\xd0\x04" \
    "\x33\x8b\xc8\xd6\xfe\xd6\x98\x88\x48\x16\x1f\x95" \
    "\x54\x4e\x7e\xa1\x37\xb3\x91\xe4\x70\x75\xfb\xf8" \
    "\x5f\x9b\x20\xe9\x96\xed\x22\xd9\x7b\xcb\x27\xb7" \
    "\xf9\x59\x2b\x13\x5a\x1e\x3e\x00\x00\x00\x00\x49" \
    "\x45\x4e\x44\xae\x42\x60\x82"

class LinearMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("LinearMotorPropDialog")

        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        LinearMotorPropDialogLayout = QGridLayout(self,1,1,11,6,"LinearMotorPropDialogLayout")

        layout30 = QHBoxLayout(None,0,6,"layout30")

        layout29 = QVBoxLayout(None,0,6,"layout29")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.nameTextLabel)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_2)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_5)
        layout30.addLayout(layout29)

        layout28 = QGridLayout(None,1,1,0,6,"layout28")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout28.addWidget(self.textLabel1_4,1,1)

        layout29_2 = QHBoxLayout(None,0,6,"layout29_2")

        self.enable_minimize_checkbox = QCheckBox(self,"enable_minimize_checkbox")
        layout29_2.addWidget(self.enable_minimize_checkbox)
        spacer16 = QSpacerItem(80,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout29_2.addItem(spacer16)

        layout28.addMultiCellLayout(layout29_2,3,3,0,1)

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.stiffnessLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.stiffnessLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout28.addWidget(self.stiffnessLineEdit,2,0)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)

        layout28.addMultiCellWidget(self.nameLineEdit,0,0,0,1)

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout28.addWidget(self.forceLineEdit,1,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout28.addWidget(self.textLabel2,2,1)
        layout30.addLayout(layout28)

        LinearMotorPropDialogLayout.addLayout(layout30,0,0)

        self.groupBox3 = QGroupBox(self,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.widthLineEdit = QLineEdit(self.groupBox3,"widthLineEdit")
        self.widthLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox3Layout.addWidget(self.widthLineEdit,1,1)

        self.textLabel3 = QLabel(self.groupBox3,"textLabel3")

        groupBox3Layout.addWidget(self.textLabel3,0,2)

        self.sradiusLineEdit = QLineEdit(self.groupBox3,"sradiusLineEdit")
        self.sradiusLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox3Layout.addWidget(self.sradiusLineEdit,2,1)

        self.lengthLineEdit = QLineEdit(self.groupBox3,"lengthLineEdit")
        self.lengthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.lengthLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.lengthLineEdit.setAlignment(QLineEdit.AlignLeft)

        groupBox3Layout.addWidget(self.lengthLineEdit,0,1)

        self.textLabel3_3 = QLabel(self.groupBox3,"textLabel3_3")

        groupBox3Layout.addWidget(self.textLabel3_3,2,2)

        self.textLabel3_2 = QLabel(self.groupBox3,"textLabel3_2")

        groupBox3Layout.addWidget(self.textLabel3_2,1,2)

        layout76 = QHBoxLayout(None,0,6,"layout76")

        layout75 = QHBoxLayout(None,0,6,"layout75")

        self.jig_color_pixmap = QLabel(self.groupBox3,"jig_color_pixmap")
        self.jig_color_pixmap.setMinimumSize(QSize(40,0))
        self.jig_color_pixmap.setPaletteBackgroundColor(QColor(175,175,175))
        self.jig_color_pixmap.setScaledContents(1)
        layout75.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QPushButton(self.groupBox3,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setAutoDefault(0)
        layout75.addWidget(self.choose_color_btn)
        layout76.addLayout(layout75)
        spacer5 = QSpacerItem(46,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout76.addItem(spacer5)

        groupBox3Layout.addMultiCellLayout(layout76,3,3,1,2)

        self.textLabel1_3 = QLabel(self.groupBox3,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox3Layout.addWidget(self.textLabel1_3,0,0)

        self.textLabel1_2_2 = QLabel(self.groupBox3,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox3Layout.addWidget(self.textLabel1_2_2,1,0)

        self.textLabel1_2_2_2 = QLabel(self.groupBox3,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox3Layout.addWidget(self.textLabel1_2_2_2,2,0)

        self.colorTextLabel = QLabel(self.groupBox3,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        groupBox3Layout.addWidget(self.colorTextLabel,3,0)

        LinearMotorPropDialogLayout.addWidget(self.groupBox3,1,0)
        spacer6 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        LinearMotorPropDialogLayout.addItem(spacer6,2,0)

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

        LinearMotorPropDialogLayout.addLayout(layout45,3,0)

        self.languageChange()

        self.resize(QSize(352,347).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_jig_color)
        self.connect(self.lengthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.widthLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)
        self.connect(self.sradiusLineEdit,SIGNAL("returnPressed()"),self.change_motor_size)

        self.setTabOrder(self.nameLineEdit,self.forceLineEdit)
        self.setTabOrder(self.forceLineEdit,self.stiffnessLineEdit)
        self.setTabOrder(self.stiffnessLineEdit,self.enable_minimize_checkbox)
        self.setTabOrder(self.enable_minimize_checkbox,self.lengthLineEdit)
        self.setTabOrder(self.lengthLineEdit,self.widthLineEdit)
        self.setTabOrder(self.widthLineEdit,self.sradiusLineEdit)
        self.setTabOrder(self.sradiusLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Linear Motor Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.textLabel1.setText(self.__tr("Force:"))
        self.textLabel1_2.setText(self.__tr("Stiffness:"))
        self.textLabel1_5.setText(self.__tr("Enable in Minimize (experimental)"))
        self.textLabel1_4.setText(self.__tr("pN"))
        self.enable_minimize_checkbox.setText(QString.null)
        self.nameLineEdit.setText(QString.null)
        self.textLabel2.setText(self.__tr("N/m"))
        self.groupBox3.setTitle(self.__tr("Size and Color"))
        self.textLabel3.setText(self.__tr("Angstroms"))
        self.textLabel3_3.setText(self.__tr("Angstroms"))
        self.textLabel3_2.setText(self.__tr("Angstroms"))
        self.choose_color_btn.setText(self.__tr("Choose..."))
        self.textLabel1_3.setText(self.__tr("Motor Length:"))
        self.textLabel1_2_2.setText(self.__tr("Motor Width:"))
        self.textLabel1_2_2_2.setText(self.__tr("Spoke Radius:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def change_jig_color(self):
        print "LinearMotorPropDialog.change_jig_color(): Not implemented yet"

    def change_motor_size(self):
        print "LinearMotorPropDialog.change_motor_size(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
