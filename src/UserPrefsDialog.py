# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\UserPrefsDialog.ui'
#
# Created: Wed Jun 29 00:53:33 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class UserPrefsDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("UserPrefsDialog")


        UserPrefsDialogLayout = QVBoxLayout(self,11,6,"UserPrefsDialogLayout")

        self.general_tab = QTabWidget(self,"general_tab")

        self.tab = QWidget(self.general_tab,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

        self.file_locations_grp = QGroupBox(self.tab,"file_locations_grp")
        self.file_locations_grp.setColumnLayout(0,Qt.Vertical)
        self.file_locations_grp.layout().setSpacing(6)
        self.file_locations_grp.layout().setMargin(11)
        file_locations_grpLayout = QGridLayout(self.file_locations_grp.layout())
        file_locations_grpLayout.setAlignment(Qt.AlignTop)

        self.gamess_modify_btn = QPushButton(self.file_locations_grp,"gamess_modify_btn")

        file_locations_grpLayout.addWidget(self.gamess_modify_btn,1,2)

        self.gamess_lbl = QLabel(self.file_locations_grp,"gamess_lbl")
        self.gamess_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        file_locations_grpLayout.addWidget(self.gamess_lbl,1,0)

        self.gamess_path_linedit = QLineEdit(self.file_locations_grp,"gamess_path_linedit")
        self.gamess_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.gamess_path_linedit.setFrameShadow(QLineEdit.Sunken)

        file_locations_grpLayout.addWidget(self.gamess_path_linedit,1,1)

        tabLayout.addMultiCellWidget(self.file_locations_grp,1,1,0,1)

        self.groupBox7_2 = QGroupBox(self.tab,"groupBox7_2")
        self.groupBox7_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox7_2.layout().setSpacing(6)
        self.groupBox7_2.layout().setMargin(11)
        groupBox7_2Layout = QVBoxLayout(self.groupBox7_2.layout())
        groupBox7_2Layout.setAlignment(Qt.AlignTop)

        self.display_compass_checkbox = QCheckBox(self.groupBox7_2,"display_compass_checkbox")
        self.display_compass_checkbox.setChecked(1)
        groupBox7_2Layout.addWidget(self.display_compass_checkbox)

        self.display_origin_axis_checkbox = QCheckBox(self.groupBox7_2,"display_origin_axis_checkbox")
        self.display_origin_axis_checkbox.setChecked(1)
        groupBox7_2Layout.addWidget(self.display_origin_axis_checkbox)

        self.display_pov_axis_checkbox = QCheckBox(self.groupBox7_2,"display_pov_axis_checkbox")
        self.display_pov_axis_checkbox.setChecked(1)
        groupBox7_2Layout.addWidget(self.display_pov_axis_checkbox)

        tabLayout.addWidget(self.groupBox7_2,0,0)

        self.compass_position_btngrp = QButtonGroup(self.tab,"compass_position_btngrp")
        self.compass_position_btngrp.setExclusive(1)
        self.compass_position_btngrp.setColumnLayout(0,Qt.Vertical)
        self.compass_position_btngrp.layout().setSpacing(6)
        self.compass_position_btngrp.layout().setMargin(11)
        compass_position_btngrpLayout = QGridLayout(self.compass_position_btngrp.layout())
        compass_position_btngrpLayout.setAlignment(Qt.AlignTop)

        self.upper_right_btn = QRadioButton(self.compass_position_btngrp,"upper_right_btn")
        self.upper_right_btn.setChecked(1)

        compass_position_btngrpLayout.addWidget(self.upper_right_btn,0,1)

        self.upper_left_btn = QRadioButton(self.compass_position_btngrp,"upper_left_btn")

        compass_position_btngrpLayout.addWidget(self.upper_left_btn,0,0)

        self.lower_left_btn = QRadioButton(self.compass_position_btngrp,"lower_left_btn")

        compass_position_btngrpLayout.addWidget(self.lower_left_btn,2,0)

        self.lower_right_btn = QRadioButton(self.compass_position_btngrp,"lower_right_btn")

        compass_position_btngrpLayout.addWidget(self.lower_right_btn,2,1)
        spacer8 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        compass_position_btngrpLayout.addItem(spacer8,1,0)
        spacer8_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        compass_position_btngrpLayout.addItem(spacer8_2,1,1)

        tabLayout.addWidget(self.compass_position_btngrp,0,1)
        self.general_tab.insertTab(self.tab,QString(""))

        self.TabPage = QWidget(self.general_tab,"TabPage")
        TabPageLayout = QVBoxLayout(self.TabPage,11,6,"TabPageLayout")

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout25 = QHBoxLayout(None,0,6,"layout25")

        layout23 = QVBoxLayout(None,0,6,"layout23")

        self.textLabel2 = QLabel(self.TabPage,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout23.addWidget(self.textLabel2)

        self.textLabel3 = QLabel(self.TabPage,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout23.addWidget(self.textLabel3)

        self.textLabel4 = QLabel(self.TabPage,"textLabel4")
        self.textLabel4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout23.addWidget(self.textLabel4)
        layout25.addLayout(layout23)

        layout24 = QVBoxLayout(None,0,6,"layout24")

        self.comboBox2 = QComboBox(0,self.TabPage,"comboBox2")
        layout24.addWidget(self.comboBox2)

        self.comboBox3 = QComboBox(0,self.TabPage,"comboBox3")
        layout24.addWidget(self.comboBox3)

        layout37 = QHBoxLayout(None,0,6,"layout37")

        self.frame3 = QFrame(self.TabPage,"frame3")
        self.frame3.setPaletteBackgroundColor(QColor(0,0,127))
        self.frame3.setFrameShape(QFrame.StyledPanel)
        self.frame3.setFrameShadow(QFrame.Raised)
        layout37.addWidget(self.frame3)

        self.pushButton4 = QPushButton(self.TabPage,"pushButton4")
        layout37.addWidget(self.pushButton4)
        layout24.addLayout(layout37)
        layout25.addLayout(layout24)
        layout27.addLayout(layout25)
        spacer7_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout27.addItem(spacer7_2)
        TabPageLayout.addLayout(layout27)

        layout26 = QHBoxLayout(None,0,6,"layout26")
        spacer9 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout26.addItem(spacer9)

        self.default_bgcolor_btn = QPushButton(self.TabPage,"default_bgcolor_btn")
        layout26.addWidget(self.default_bgcolor_btn)
        TabPageLayout.addLayout(layout26)
        self.general_tab.insertTab(self.TabPage,QString(""))
        UserPrefsDialogLayout.addWidget(self.general_tab)

        layout28 = QHBoxLayout(None,0,6,"layout28")
        spacer7 = QSpacerItem(240,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout28.addItem(spacer7)

        self.ok_btn = QPushButton(self,"ok_btn")
        layout28.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        layout28.addWidget(self.cancel_btn)
        UserPrefsDialogLayout.addLayout(layout28)

        self.languageChange()

        self.resize(QSize(495,283).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.ok_btn,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.display_compass_checkbox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.display_origin_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_origin_axis)
        self.connect(self.display_pov_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_pov_axis)
        self.connect(self.compass_position_btngrp,SIGNAL("clicked(int)"),self.set_compass_position)
        self.connect(self.gamess_modify_btn,SIGNAL("clicked()"),self.set_gamess_path)


    def languageChange(self):
        self.setCaption(self.__tr("Preferences"))
        self.file_locations_grp.setTitle(self.__tr("File Locations"))
        self.gamess_modify_btn.setText(self.__tr("Modify..."))
        self.gamess_lbl.setText(self.__tr("GAMESS :"))
        self.groupBox7_2.setTitle(self.__tr("Compass and Axes"))
        self.display_compass_checkbox.setText(self.__tr("Display Compass"))
        self.display_origin_axis_checkbox.setText(self.__tr("Display Origin Axis"))
        self.display_pov_axis_checkbox.setText(self.__tr("Display Point of View Axis"))
        self.compass_position_btngrp.setTitle(self.__tr("Compass Position"))
        self.upper_right_btn.setText(self.__tr("Upper Right"))
        self.upper_left_btn.setText(self.__tr("Upper Left"))
        self.lower_left_btn.setText(self.__tr("Lower Left"))
        self.lower_right_btn.setText(self.__tr("Lower Right"))
        self.general_tab.changeTab(self.tab,self.__tr("General"))
        self.textLabel2.setText(self.__tr("Mode :"))
        self.textLabel3.setText(self.__tr("Fill Type :"))
        self.textLabel4.setText(self.__tr("Color :"))
        self.comboBox2.clear()
        self.comboBox2.insertItem(self.__tr("All Modes"))
        self.comboBox2.insertItem(self.__tr("Build Atoms"))
        self.comboBox2.insertItem(self.__tr("Cookie Cutter"))
        self.comboBox2.insertItem(self.__tr("Move Chunks"))
        self.comboBox2.insertItem(self.__tr("Select Chunks"))
        self.comboBox2.insertItem(self.__tr("Select Atoms"))
        self.comboBox3.clear()
        self.comboBox3.insertItem(self.__tr("Solid"))
        self.comboBox3.insertItem(self.__tr("Gradient"))
        self.comboBox3.insertItem(self.__tr("Image"))
        self.pushButton4.setText(self.__tr("Edit..."))
        self.default_bgcolor_btn.setText(self.__tr("Reset Defaults"))
        self.general_tab.changeTab(self.TabPage,self.__tr("Background"))
        self.ok_btn.setText(self.__tr("OK"))
        self.cancel_btn.setText(self.__tr("Cancel"))


    def display_compass(self):
        print "UserPrefsDialog.display_compass(): Not implemented yet"

    def display_origin_axis(self):
        print "UserPrefsDialog.display_origin_axis(): Not implemented yet"

    def display_pov_axis(self):
        print "UserPrefsDialog.display_pov_axis(): Not implemented yet"

    def set_compass_position(self):
        print "UserPrefsDialog.set_compass_position(): Not implemented yet"

    def set_gamess_path(self):
        print "UserPrefsDialog.set_gamess_path(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UserPrefsDialog",s,c)
