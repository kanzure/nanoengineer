# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LinearMotorPropDialog.ui'
#
# Created: Mon Apr 24 11:08:45 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xc4\x49\x44\x41\x54\x78\x9c\xed\x94\x31\x0e\x83" \
    "\x30\x0c\x45\x3f\x15\x5b\xb7\x1c\xa3\xca\x19\xb8" \
    "\x47\xd8\x7b\x81\x5c\x27\x37\x61\x64\x44\x8c\x88" \
    "\x2d\xea\x12\xa9\x1b\x03\x51\x66\x77\x29\x11\x91" \
    "\x5a\x30\x34\x63\xdf\x92\x58\xb1\xbf\x23\x5b\x36" \
    "\xc0\x40\xd5\x8a\x00\xd0\xfb\xfc\x0d\x55\x2b\x22" \
    "\x22\x32\x61\x24\x13\xc6\x5d\xd1\x82\xa1\x49\x26" \
    "\x8c\xd1\xb8\x5f\x6f\x9b\x71\x17\xc6\x0f\xe3\xfd" \
    "\x69\x1f\x89\x7d\x9a\xac\x35\x5c\xc1\x12\x2b\xb8" \
    "\x8e\x5c\x4a\x00\x18\x86\x21\x8b\x98\x94\x32\x6d" \
    "\xca\x34\x4d\x68\x9a\x06\x52\xca\xcd\x40\xef\x3d" \
    "\x9c\x73\x1f\x7d\xcb\xb5\x58\x55\x55\x49\xb6\x33" \
    "\x44\x41\x21\x04\xda\xb6\x45\xdf\xf7\xd0\x5a\xa3" \
    "\xeb\xba\xaf\x41\x21\x04\xcc\xf3\x0c\x6b\x2d\xb4" \
    "\xd6\xc9\x5b\x01\x80\x72\xd6\x30\x7b\x97\x8f\xc0" \
    "\x4a\xbc\x3b\x7a\x47\x61\x09\x2e\x23\xf7\x5f\x5f" \
    "\xe7\x39\xb2\xbe\x5e\xa3\x7c\x71\x8b\xd8\x9f\x60" \
    "\x3f\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"

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

        self.groupBox3 = QGroupBox(self,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QGridLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.widthLineEdit = QLineEdit(self.groupBox3,"widthLineEdit")
        self.widthLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.widthLineEdit.setFrameShadow(QLineEdit.Sunken)
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

        LinearMotorPropDialogLayout.addWidget(self.groupBox3,2,0)
        spacer6 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        LinearMotorPropDialogLayout.addItem(spacer6,3,0)

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

        LinearMotorPropDialogLayout.addLayout(layout45,4,0)

        layout21 = QHBoxLayout(None,0,6,"layout21")

        layout19 = QVBoxLayout(None,0,6,"layout19")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout19.addWidget(self.nameTextLabel)

        self.textLabel1 = QLabel(self,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout19.addWidget(self.textLabel1)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout19.addWidget(self.textLabel1_2)
        layout21.addLayout(layout19)

        layout20 = QGridLayout(None,1,1,0,6,"layout20")

        self.forceLineEdit = QLineEdit(self,"forceLineEdit")
        self.forceLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout20.addWidget(self.forceLineEdit,1,0)

        self.textLabel2 = QLabel(self,"textLabel2")

        layout20.addWidget(self.textLabel2,2,1)

        self.textLabel1_4 = QLabel(self,"textLabel1_4")

        layout20.addWidget(self.textLabel1_4,1,1)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.nameLineEdit.setReadOnly(0)

        layout20.addMultiCellWidget(self.nameLineEdit,0,0,0,1)

        self.stiffnessLineEdit = QLineEdit(self,"stiffnessLineEdit")
        self.stiffnessLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.stiffnessLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.stiffnessLineEdit.setAlignment(QLineEdit.AlignLeft)

        layout20.addWidget(self.stiffnessLineEdit,2,0)
        layout21.addLayout(layout20)
        spacer10 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout21.addItem(spacer10)

        LinearMotorPropDialogLayout.addLayout(layout21,0,0)

        layout22 = QHBoxLayout(None,0,6,"layout22")

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout22.addWidget(self.textLabel1_5)

        self.enable_minimize_checkbox = QCheckBox(self,"enable_minimize_checkbox")
        layout22.addWidget(self.enable_minimize_checkbox)
        spacer16 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout22.addItem(spacer16)

        LinearMotorPropDialogLayout.addLayout(layout22,1,0)

        self.languageChange()

        self.resize(QSize(277,315).expandedTo(self.minimumSizeHint()))
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
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.textLabel1.setText(self.__tr("Force:"))
        self.textLabel1_2.setText(self.__tr("Stiffness:"))
        QToolTip.add(self.forceLineEdit,self.__tr("Simulations will begin with the motor's force set to this value."))
        QWhatsThis.add(self.forceLineEdit,self.__tr("<b>Force </b><p>Simulations will begin with the motor's force set to this\n"
"value. The integral displacement of the linear motor's atoms is computed\n"
"using Hooke's Law where:</p>\n"
"<p><b>displacement = - Force  / Stiffness</b>.</p>\n"
"<p>The negative sign indicates that the force exerted by the spring is in\n"
"direct opposition to the direction of displacement. It is called a\n"
"\"restoring force\", as it tends to restore the system to equilibrium.</p>\n"
"<p>When stiffness = 0, the restoring force is 0 and the displacement will\n"
"continue in one direction.</p>"))
        self.textLabel2.setText(self.__tr("N/m"))
        self.textLabel1_4.setText(self.__tr("pN"))
        self.nameLineEdit.setText(QString.null)
        QToolTip.add(self.nameLineEdit,self.__tr("Name of Linear Motor"))
        QWhatsThis.add(self.nameLineEdit,self.__tr("<b>Name</b><p>Name of Linear Motor that appears in the Model Tree</p>"))
        QToolTip.add(self.stiffnessLineEdit,self.__tr("Simulation will begin with the motor's stiffness set to this value."))
        QWhatsThis.add(self.stiffnessLineEdit,self.__tr("<b>Stiffness </b><p>Simulations will begin with the motor's stiffness set to this\n"
"value. The integral displacement of the linear motor's atoms is computed\n"
"using Hooke's Law where:</p>\n"
"<p><b>displacement = - Force  / Stiffness</b>.</p>\n"
"<p>The negative sign indicates that the force exerted by the spring is in\n"
"direct opposition to the direction of displacement. It is called a\n"
"\"restoring force\", as it tends to restore the system to equilibrium.</p>\n"
"<p>When stiffness = 0, the restoring force is 0 and the displacement will\n"
"continue in one direction.</p>"))
        self.textLabel1_5.setText(self.__tr("Enable in Minimize (experimental) :"))
        QToolTip.add(self.textLabel1_5,self.__tr("If checked, the force value is applied to the motor's atoms during minimization."))
        QWhatsThis.add(self.textLabel1_5,self.__tr("<b>Enable in Minimize <i>(experimental)</i></b><p>If checked, the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>"))
        self.enable_minimize_checkbox.setText(QString.null)
        QToolTip.add(self.enable_minimize_checkbox,self.__tr("If checked, the force value is applied to the motor's atoms during minimization."))
        QWhatsThis.add(self.enable_minimize_checkbox,self.__tr("<b>Enable in Minimize <i>(experimental)</i></b><p>If checked, the force specified above will be applied to the motor's atoms during a structure minimization.  While intended to allow simulations to begin with linear motors running at speed, this feature requires more work to be useful.</p>"))


    def change_jig_color(self):
        print "LinearMotorPropDialog.change_jig_color(): Not implemented yet"

    def change_motor_size(self):
        print "LinearMotorPropDialog.change_motor_size(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LinearMotorPropDialog",s,c)
