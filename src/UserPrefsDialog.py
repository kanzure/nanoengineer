# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\UserPrefsDialog.ui'
#
# Created: Thu Aug 11 17:42:27 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class UserPrefsDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("UserPrefsDialog")


        UserPrefsDialogLayout = QGridLayout(self,1,1,11,6,"UserPrefsDialogLayout")

        layout28 = QHBoxLayout(None,0,6,"layout28")
        spacer7 = QSpacerItem(240,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout28.addItem(spacer7)

        self.ok_btn = QPushButton(self,"ok_btn")
        layout28.addWidget(self.ok_btn)

        UserPrefsDialogLayout.addLayout(layout28,1,0)

        self.prefs_tab = QTabWidget(self,"prefs_tab")

        self.tab = QWidget(self.prefs_tab,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")

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

        self.file_locations_grp = QGroupBox(self.tab,"file_locations_grp")
        self.file_locations_grp.setColumnLayout(0,Qt.Vertical)
        self.file_locations_grp.layout().setSpacing(6)
        self.file_locations_grp.layout().setMargin(11)
        file_locations_grpLayout = QGridLayout(self.file_locations_grp.layout())
        file_locations_grpLayout.setAlignment(Qt.AlignTop)

        self.gamess_choose_btn = QPushButton(self.file_locations_grp,"gamess_choose_btn")

        file_locations_grpLayout.addWidget(self.gamess_choose_btn,1,2)

        self.gamess_lbl = QLabel(self.file_locations_grp,"gamess_lbl")
        self.gamess_lbl.setSizePolicy(QSizePolicy(1,5,0,0,self.gamess_lbl.sizePolicy().hasHeightForWidth()))
        self.gamess_lbl.setMinimumSize(QSize(60,0))
        self.gamess_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        file_locations_grpLayout.addWidget(self.gamess_lbl,1,0)

        self.gamess_path_linedit = QLineEdit(self.file_locations_grp,"gamess_path_linedit")
        self.gamess_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.gamess_path_linedit.setFrameShadow(QLineEdit.Sunken)

        file_locations_grpLayout.addWidget(self.gamess_path_linedit,1,1)

        tabLayout.addMultiCellWidget(self.file_locations_grp,1,1,0,1)
        spacer23 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer23,2,0)
        self.prefs_tab.insertTab(self.tab,QString(""))

        self.TabPage = QWidget(self.prefs_tab,"TabPage")
        TabPageLayout = QHBoxLayout(self.TabPage,11,6,"TabPageLayout")

        layout59 = QVBoxLayout(None,0,6,"layout59")

        self.atom_colors_grpbox = QGroupBox(self.TabPage,"atom_colors_grpbox")
        self.atom_colors_grpbox.setColumnLayout(0,Qt.Vertical)
        self.atom_colors_grpbox.layout().setSpacing(6)
        self.atom_colors_grpbox.layout().setMargin(11)
        atom_colors_grpboxLayout = QVBoxLayout(self.atom_colors_grpbox.layout())
        atom_colors_grpboxLayout.setAlignment(Qt.AlignTop)

        layout58 = QGridLayout(None,1,1,0,6,"layout58")

        self.textLabel3_2_3 = QLabel(self.atom_colors_grpbox,"textLabel3_2_3")
        self.textLabel3_2_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout58.addWidget(self.textLabel3_2_3,0,0)

        layout37_2_2_2_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2_2_2_2")

        self.hotspot_color_frame = QFrame(self.atom_colors_grpbox,"hotspot_color_frame")
        self.hotspot_color_frame.setMinimumSize(QSize(25,0))
        self.hotspot_color_frame.setPaletteBackgroundColor(QColor(0,255,0))
        self.hotspot_color_frame.setFrameShape(QFrame.Box)
        self.hotspot_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_2_2.addWidget(self.hotspot_color_frame)

        self.hotspot_color_btn = QPushButton(self.atom_colors_grpbox,"hotspot_color_btn")
        layout37_2_2_2_2_2_2.addWidget(self.hotspot_color_btn)

        layout58.addLayout(layout37_2_2_2_2_2_2,3,1)

        layout37_2_2_2_3 = QHBoxLayout(None,0,6,"layout37_2_2_2_3")

        self.atom_hilite_color_frame = QFrame(self.atom_colors_grpbox,"atom_hilite_color_frame")
        self.atom_hilite_color_frame.setMinimumSize(QSize(25,0))
        self.atom_hilite_color_frame.setPaletteBackgroundColor(QColor(0,170,0))
        self.atom_hilite_color_frame.setFrameShape(QFrame.Box)
        self.atom_hilite_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_3.addWidget(self.atom_hilite_color_frame)

        self.atom_hilite_color_btn = QPushButton(self.atom_colors_grpbox,"atom_hilite_color_btn")
        layout37_2_2_2_3.addWidget(self.atom_hilite_color_btn)

        layout58.addLayout(layout37_2_2_2_3,0,1)

        self.hotspot_lbl = QLabel(self.atom_colors_grpbox,"hotspot_lbl")
        self.hotspot_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout58.addWidget(self.hotspot_lbl,3,0)
        atom_colors_grpboxLayout.addLayout(layout58)

        layout25_2 = QHBoxLayout(None,0,6,"layout25_2")
        spacer20_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25_2.addItem(spacer20_2)

        self.reset_atom_colors_btn = QPushButton(self.atom_colors_grpbox,"reset_atom_colors_btn")
        layout25_2.addWidget(self.reset_atom_colors_btn)
        atom_colors_grpboxLayout.addLayout(layout25_2)
        layout59.addWidget(self.atom_colors_grpbox)
        spacer11_4 = QSpacerItem(20,3,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout59.addItem(spacer11_4)
        TabPageLayout.addLayout(layout59)

        layout22 = QVBoxLayout(None,0,6,"layout22")

        self.default_display_btngrp = QButtonGroup(self.TabPage,"default_display_btngrp")
        self.default_display_btngrp.setColumnLayout(0,Qt.Vertical)
        self.default_display_btngrp.layout().setSpacing(6)
        self.default_display_btngrp.layout().setMargin(11)
        default_display_btngrpLayout = QGridLayout(self.default_display_btngrp.layout())
        default_display_btngrpLayout.setAlignment(Qt.AlignTop)

        self.vwd_rbtn = QRadioButton(self.default_display_btngrp,"vwd_rbtn")
        self.default_display_btngrp.insert( self.vwd_rbtn,2)

        default_display_btngrpLayout.addWidget(self.vwd_rbtn,0,0)

        self.cpk_rbtn = QRadioButton(self.default_display_btngrp,"cpk_rbtn")
        self.default_display_btngrp.insert( self.cpk_rbtn,4)

        default_display_btngrpLayout.addWidget(self.cpk_rbtn,1,0)

        self.lines_rbtn = QRadioButton(self.default_display_btngrp,"lines_rbtn")
        self.default_display_btngrp.insert( self.lines_rbtn,3)

        default_display_btngrpLayout.addWidget(self.lines_rbtn,3,0)

        self.tubes_rbtn = QRadioButton(self.default_display_btngrp,"tubes_rbtn")
        self.default_display_btngrp.insert( self.tubes_rbtn,5)

        default_display_btngrpLayout.addWidget(self.tubes_rbtn,2,0)
        layout22.addWidget(self.default_display_btngrp)
        spacer11 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout22.addItem(spacer11)
        TabPageLayout.addLayout(layout22)
        spacer9 = QSpacerItem(3,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout.addItem(spacer9)
        self.prefs_tab.insertTab(self.TabPage,QString(""))

        self.TabPage_2 = QWidget(self.prefs_tab,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")

        layout63 = QVBoxLayout(None,0,6,"layout63")

        self.groupBox4 = QGroupBox(self.TabPage_2,"groupBox4")
        self.groupBox4.setColumnLayout(0,Qt.Vertical)
        self.groupBox4.layout().setSpacing(6)
        self.groupBox4.layout().setMargin(11)
        groupBox4Layout = QVBoxLayout(self.groupBox4.layout())
        groupBox4Layout.setAlignment(Qt.AlignTop)

        layout61 = QGridLayout(None,1,1,0,6,"layout61")

        layout37_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2")

        self.bond_hilite_color_frame = QFrame(self.groupBox4,"bond_hilite_color_frame")
        self.bond_hilite_color_frame.setMinimumSize(QSize(25,0))
        self.bond_hilite_color_frame.setPaletteBackgroundColor(QColor(0,0,159))
        self.bond_hilite_color_frame.setFrameShape(QFrame.Box)
        self.bond_hilite_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2.addWidget(self.bond_hilite_color_frame)

        self.bond_hilite_color_btn = QPushButton(self.groupBox4,"bond_hilite_color_btn")
        layout37_2_2_2.addWidget(self.bond_hilite_color_btn)

        layout61.addLayout(layout37_2_2_2,0,1)

        layout37_2_2 = QHBoxLayout(None,0,6,"layout37_2_2")

        self.bond_cpk_color_frame = QFrame(self.groupBox4,"bond_cpk_color_frame")
        self.bond_cpk_color_frame.setMinimumSize(QSize(25,0))
        self.bond_cpk_color_frame.setPaletteBackgroundColor(QColor(158,158,158))
        self.bond_cpk_color_frame.setFrameShape(QFrame.Box)
        self.bond_cpk_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2.addWidget(self.bond_cpk_color_frame)

        self.bond_cpk_color_btn = QPushButton(self.groupBox4,"bond_cpk_color_btn")
        layout37_2_2.addWidget(self.bond_cpk_color_btn)

        layout61.addLayout(layout37_2_2,1,1)

        layout37_2_2_2_2_3 = QHBoxLayout(None,0,6,"layout37_2_2_2_2_3")

        self.bond_vane_color_frame = QFrame(self.groupBox4,"bond_vane_color_frame")
        self.bond_vane_color_frame.setMinimumSize(QSize(25,0))
        self.bond_vane_color_frame.setPaletteBackgroundColor(QColor(255,0,0))
        self.bond_vane_color_frame.setFrameShape(QFrame.Box)
        self.bond_vane_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_frame)

        self.bond_vane_color_btn = QPushButton(self.groupBox4,"bond_vane_color_btn")
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_btn)

        layout61.addLayout(layout37_2_2_2_2_3,4,1)

        self.textLabel3_2_2 = QLabel(self.groupBox4,"textLabel3_2_2")
        self.textLabel3_2_2.setSizePolicy(QSizePolicy(5,5,0,0,self.textLabel3_2_2.sizePolicy().hasHeightForWidth()))
        self.textLabel3_2_2.setMinimumSize(QSize(0,0))
        self.textLabel3_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout61.addWidget(self.textLabel3_2_2,2,0)

        self.textLabel3_2 = QLabel(self.groupBox4,"textLabel3_2")
        self.textLabel3_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout61.addWidget(self.textLabel3_2,0,0)

        self.textLabel3_3 = QLabel(self.groupBox4,"textLabel3_3")
        self.textLabel3_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout61.addWidget(self.textLabel3_3,4,0)

        layout37_2_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2_2")

        self.bond_stretch_color_frame = QFrame(self.groupBox4,"bond_stretch_color_frame")
        self.bond_stretch_color_frame.setMinimumSize(QSize(25,0))
        self.bond_stretch_color_frame.setPaletteBackgroundColor(QColor(255,0,0))
        self.bond_stretch_color_frame.setFrameShape(QFrame.Box)
        self.bond_stretch_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2.addWidget(self.bond_stretch_color_frame)

        self.bond_stretch_color_btn = QPushButton(self.groupBox4,"bond_stretch_color_btn")
        layout37_2_2_2_2.addWidget(self.bond_stretch_color_btn)

        layout61.addLayout(layout37_2_2_2_2,2,1)

        self.textLabel3 = QLabel(self.groupBox4,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout61.addWidget(self.textLabel3,1,0)
        groupBox4Layout.addLayout(layout61)

        layout25 = QHBoxLayout(None,0,6,"layout25")
        spacer20 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25.addItem(spacer20)

        self.reset_bond_colors_btn = QPushButton(self.groupBox4,"reset_bond_colors_btn")
        layout25.addWidget(self.reset_bond_colors_btn)
        groupBox4Layout.addLayout(layout25)
        layout63.addWidget(self.groupBox4)
        spacer22 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout63.addItem(spacer22)

        TabPageLayout_2.addLayout(layout63,0,0)
        spacer19 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_2.addItem(spacer19,0,2)

        layout64 = QVBoxLayout(None,0,6,"layout64")

        self.high_order_bond_display_btngrp = QButtonGroup(self.TabPage_2,"high_order_bond_display_btngrp")
        self.high_order_bond_display_btngrp.setExclusive(1)
        self.high_order_bond_display_btngrp.setColumnLayout(0,Qt.Vertical)
        self.high_order_bond_display_btngrp.layout().setSpacing(6)
        self.high_order_bond_display_btngrp.layout().setMargin(11)
        high_order_bond_display_btngrpLayout = QVBoxLayout(self.high_order_bond_display_btngrp.layout())
        high_order_bond_display_btngrpLayout.setAlignment(Qt.AlignTop)

        self.radioButton11 = QRadioButton(self.high_order_bond_display_btngrp,"radioButton11")
        self.radioButton11.setChecked(1)
        self.high_order_bond_display_btngrp.insert( self.radioButton11,0)
        high_order_bond_display_btngrpLayout.addWidget(self.radioButton11)

        self.radioButton11_2 = QRadioButton(self.high_order_bond_display_btngrp,"radioButton11_2")
        self.high_order_bond_display_btngrp.insert( self.radioButton11_2,1)
        high_order_bond_display_btngrpLayout.addWidget(self.radioButton11_2)

        self.radioButton11_2_2 = QRadioButton(self.high_order_bond_display_btngrp,"radioButton11_2_2")
        high_order_bond_display_btngrpLayout.addWidget(self.radioButton11_2_2)
        layout64.addWidget(self.high_order_bond_display_btngrp)

        self.show_bond_labels_checkbox = QCheckBox(self.TabPage_2,"show_bond_labels_checkbox")
        layout64.addWidget(self.show_bond_labels_checkbox)

        self.show_valence_errors_checkbox = QCheckBox(self.TabPage_2,"show_valence_errors_checkbox")
        layout64.addWidget(self.show_valence_errors_checkbox)
        spacer18 = QSpacerItem(20,30,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout64.addItem(spacer18)

        TabPageLayout_2.addLayout(layout64,0,1)
        self.prefs_tab.insertTab(self.TabPage_2,QString(""))

        self.TabPage_3 = QWidget(self.prefs_tab,"TabPage_3")
        TabPageLayout_3 = QGridLayout(self.TabPage_3,1,1,11,6,"TabPageLayout_3")
        spacer8_4 = QSpacerItem(60,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_3.addItem(spacer8_4,0,1)

        layout65 = QVBoxLayout(None,0,6,"layout65")

        self.groupBox11 = QGroupBox(self.TabPage_3,"groupBox11")
        self.groupBox11.setColumnLayout(0,Qt.Vertical)
        self.groupBox11.layout().setSpacing(6)
        self.groupBox11.layout().setMargin(11)
        groupBox11Layout = QGridLayout(self.groupBox11.layout())
        groupBox11Layout.setAlignment(Qt.AlignTop)

        layout62 = QGridLayout(None,1,1,0,6,"layout62")

        self.mode_lbl = QLabel(self.groupBox11,"mode_lbl")
        self.mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout62.addWidget(self.mode_lbl,0,0)

        self.mode_combox = QComboBox(0,self.groupBox11,"mode_combox")

        layout62.addWidget(self.mode_combox,0,1)

        layout37 = QHBoxLayout(None,0,6,"layout37")

        self.bg1_color_frame = QFrame(self.groupBox11,"bg1_color_frame")
        self.bg1_color_frame.setMinimumSize(QSize(25,0))
        self.bg1_color_frame.setPaletteBackgroundColor(QColor(170,255,255))
        self.bg1_color_frame.setFrameShape(QFrame.Box)
        self.bg1_color_frame.setFrameShadow(QFrame.Plain)
        layout37.addWidget(self.bg1_color_frame)

        self.choose_bg1_color_btn = QPushButton(self.groupBox11,"choose_bg1_color_btn")
        layout37.addWidget(self.choose_bg1_color_btn)

        layout62.addLayout(layout37,2,1)

        self.bg1_color_lbl = QLabel(self.groupBox11,"bg1_color_lbl")
        self.bg1_color_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout62.addWidget(self.bg1_color_lbl,2,0)

        self.fill_type_lbl = QLabel(self.groupBox11,"fill_type_lbl")
        self.fill_type_lbl.setEnabled(1)
        self.fill_type_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout62.addWidget(self.fill_type_lbl,1,0)

        self.fill_type_combox = QComboBox(0,self.groupBox11,"fill_type_combox")
        self.fill_type_combox.setEnabled(1)

        layout62.addWidget(self.fill_type_combox,1,1)

        groupBox11Layout.addMultiCellLayout(layout62,0,0,0,1)

        self.restore_bgcolor_btn = QPushButton(self.groupBox11,"restore_bgcolor_btn")

        groupBox11Layout.addWidget(self.restore_bgcolor_btn,1,1)
        spacer7_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox11Layout.addItem(spacer7_2,1,0)
        layout65.addWidget(self.groupBox11)
        spacer8_3 = QSpacerItem(20,30,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout65.addItem(spacer8_3)

        TabPageLayout_3.addLayout(layout65,0,0)
        self.prefs_tab.insertTab(self.TabPage_3,QString(""))

        self.TabPage_4 = QWidget(self.prefs_tab,"TabPage_4")
        TabPageLayout_4 = QVBoxLayout(self.TabPage_4,11,6,"TabPageLayout_4")

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.history_height_lbl = QLabel(self.TabPage_4,"history_height_lbl")
        self.history_height_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout9.addWidget(self.history_height_lbl)

        self.history_height_spinbox = QSpinBox(self.TabPage_4,"history_height_spinbox")
        self.history_height_spinbox.setMaxValue(20)
        self.history_height_spinbox.setValue(4)
        layout9.addWidget(self.history_height_spinbox)

        self.history_lines_lbl = QLabel(self.TabPage_4,"history_lines_lbl")
        layout9.addWidget(self.history_lines_lbl)
        spacer11_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout9.addItem(spacer11_2)
        TabPageLayout_4.addLayout(layout9)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.msg_serial_number_checkbox = QCheckBox(self.TabPage_4,"msg_serial_number_checkbox")
        layout11.addWidget(self.msg_serial_number_checkbox)
        spacer12 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout11.addItem(spacer12)
        TabPageLayout_4.addLayout(layout11)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.msg_timestamp_checkbox = QCheckBox(self.TabPage_4,"msg_timestamp_checkbox")
        layout10.addWidget(self.msg_timestamp_checkbox)
        spacer13 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout10.addItem(spacer13)
        TabPageLayout_4.addLayout(layout10)
        spacer10 = QSpacerItem(20,80,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_4.addItem(spacer10)
        self.prefs_tab.insertTab(self.TabPage_4,QString(""))

        self.TabPage_5 = QWidget(self.prefs_tab,"TabPage_5")
        TabPageLayout_5 = QGridLayout(self.TabPage_5,1,1,11,6,"TabPageLayout_5")

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.groupBox3 = QGroupBox(self.TabPage_5,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QVBoxLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.textLabel2 = QLabel(self.groupBox3,"textLabel2")
        groupBox3Layout.addWidget(self.textLabel2)

        self.caption_prefix_linedit = QLineEdit(self.groupBox3,"caption_prefix_linedit")
        self.caption_prefix_linedit.setMinimumSize(QSize(0,0))
        self.caption_prefix_linedit.setPaletteBackgroundColor(QColor(255,255,255))
        self.caption_prefix_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.caption_prefix_linedit.setFrameShadow(QLineEdit.Sunken)
        groupBox3Layout.addWidget(self.caption_prefix_linedit)

        self.textLabel2_2 = QLabel(self.groupBox3,"textLabel2_2")
        groupBox3Layout.addWidget(self.textLabel2_2)

        self.caption_suffix_linedit = QLineEdit(self.groupBox3,"caption_suffix_linedit")
        self.caption_suffix_linedit.setMinimumSize(QSize(0,0))
        self.caption_suffix_linedit.setPaletteBackgroundColor(QColor(255,255,255))
        self.caption_suffix_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.caption_suffix_linedit.setFrameShadow(QLineEdit.Sunken)
        groupBox3Layout.addWidget(self.caption_suffix_linedit)

        self.caption_fullpath_checkbox = QCheckBox(self.groupBox3,"caption_fullpath_checkbox")
        groupBox3Layout.addWidget(self.caption_fullpath_checkbox)
        layout15.addWidget(self.groupBox3)
        spacer9_2 = QSpacerItem(210,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout15.addItem(spacer9_2)

        TabPageLayout_5.addLayout(layout15,0,0)
        spacer11_3 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_5.addItem(spacer11_3,1,0)
        self.prefs_tab.insertTab(self.TabPage_5,QString(""))

        UserPrefsDialogLayout.addWidget(self.prefs_tab,0,0)

        self.languageChange()

        self.resize(QSize(495,318).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.atom_hilite_color_btn,SIGNAL("clicked()"),self.change_atom_hilite_color)
        self.connect(self.bond_cpk_color_btn,SIGNAL("clicked()"),self.change_bond_cpk_color)
        self.connect(self.bond_hilite_color_btn,SIGNAL("clicked()"),self.change_bond_hilite_color)
        self.connect(self.bond_stretch_color_btn,SIGNAL("clicked()"),self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn,SIGNAL("clicked()"),self.change_bond_vane_color)
        self.connect(self.choose_bg1_color_btn,SIGNAL("clicked()"),self.change_bg1_color)
        self.connect(self.compass_position_btngrp,SIGNAL("clicked(int)"),self.set_compass_position)
        self.connect(self.default_display_btngrp,SIGNAL("clicked(int)"),self.set_default_display_mode)
        self.connect(self.display_compass_checkbox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.display_origin_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_origin_axis)
        self.connect(self.display_pov_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_pov_axis)
        self.connect(self.fill_type_combox,SIGNAL("activated(const QString&)"),self.fill_type_changed)
        self.connect(self.gamess_choose_btn,SIGNAL("clicked()"),self.set_gamess_path)
        self.connect(self.high_order_bond_display_btngrp,SIGNAL("clicked(int)"),self.change_high_order_bond_display)
        self.connect(self.history_height_spinbox,SIGNAL("valueChanged(int)"),self.set_history_height)
        self.connect(self.mode_combox,SIGNAL("activated(int)"),self.mode_changed)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.prefs_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.reset_atom_colors_btn,SIGNAL("clicked()"),self.reset_atom_colors)
        self.connect(self.reset_bond_colors_btn,SIGNAL("clicked()"),self.reset_bond_colors)
        self.connect(self.restore_bgcolor_btn,SIGNAL("clicked()"),self.restore_default_bgcolor)
        self.connect(self.show_bond_labels_checkbox,SIGNAL("toggled(bool)"),self.change_bond_labels)
        self.connect(self.caption_fullpath_checkbox,SIGNAL("stateChanged(int)"),self.set_caption_fullpath)
        self.connect(self.hotspot_color_btn,SIGNAL("clicked()"),self.change_hotspot_color)
        self.connect(self.show_valence_errors_checkbox,SIGNAL("toggled(bool)"),self.change_show_valence_errors)


    def languageChange(self):
        self.setCaption(self.__tr("Preferences"))
        self.ok_btn.setText(self.__tr("OK"))
        self.groupBox7_2.setTitle(self.__tr("Compass and Axes"))
        self.display_compass_checkbox.setText(self.__tr("Display Compass"))
        self.display_origin_axis_checkbox.setText(self.__tr("Display Origin Axis"))
        self.display_pov_axis_checkbox.setText(self.__tr("Display Point of View Axis"))
        self.compass_position_btngrp.setTitle(self.__tr("Compass Position"))
        self.upper_right_btn.setText(self.__tr("Upper Right"))
        self.upper_left_btn.setText(self.__tr("Upper Left"))
        self.lower_left_btn.setText(self.__tr("Lower Left"))
        self.lower_right_btn.setText(self.__tr("Lower Right"))
        self.file_locations_grp.setTitle(self.__tr("File Locations"))
        self.gamess_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_lbl.setText(self.__tr("GAMESS Executable :"))
        QToolTip.add(self.gamess_lbl,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.gamess_path_linedit.setText(QString.null)
        self.prefs_tab.changeTab(self.tab,self.__tr("General"))
        self.atom_colors_grpbox.setTitle(self.__tr("Colors"))
        self.textLabel3_2_3.setText(self.__tr("Atom Highlighting :"))
        self.hotspot_color_btn.setText(self.__tr("Choose..."))
        self.atom_hilite_color_btn.setText(self.__tr("Choose..."))
        self.hotspot_lbl.setText(self.__tr("Open Bonds Hotspot  :"))
        self.reset_atom_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.default_display_btngrp.setTitle(self.__tr("Default Display"))
        self.vwd_rbtn.setText(self.__tr("VdW"))
        self.cpk_rbtn.setText(self.__tr("CPK"))
        self.lines_rbtn.setText(self.__tr("Lines"))
        self.tubes_rbtn.setText(self.__tr("Tubes"))
        self.prefs_tab.changeTab(self.TabPage,self.__tr("Atoms"))
        self.groupBox4.setTitle(self.__tr("Colors"))
        self.bond_hilite_color_btn.setText(self.__tr("Choose..."))
        self.bond_cpk_color_btn.setText(self.__tr("Choose..."))
        self.bond_vane_color_btn.setText(self.__tr("Choose..."))
        self.textLabel3_2_2.setText(self.__tr("Bond Stretch :"))
        QToolTip.add(self.textLabel3_2_2,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.textLabel3_2.setText(self.__tr("Bond Highlighting :"))
        self.textLabel3_3.setText(self.__tr("Vane/Ribbon :"))
        self.bond_stretch_color_btn.setText(self.__tr("Choose..."))
        self.textLabel3.setText(self.__tr("CPK Cylinder :"))
        self.reset_bond_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.high_order_bond_display_btngrp.setTitle(self.__tr("High Order Bonds"))
        self.radioButton11.setText(self.__tr("Multiple Cylinders"))
        self.radioButton11_2.setText(self.__tr("Vanes"))
        self.radioButton11_2_2.setText(self.__tr("Ribbons"))
        self.show_bond_labels_checkbox.setText(self.__tr("Show Bond Type Letters"))
        self.show_valence_errors_checkbox.setText(self.__tr("Show Valence Errors"))
        self.prefs_tab.changeTab(self.TabPage_2,self.__tr("Bonds"))
        self.groupBox11.setTitle(self.__tr("Mode Colors"))
        self.mode_lbl.setText(self.__tr("Mode :"))
        self.mode_combox.clear()
        self.mode_combox.insertItem(self.__tr("Select Chunks"))
        self.mode_combox.insertItem(self.__tr("Select Atoms"))
        self.mode_combox.insertItem(self.__tr("Move Chunks"))
        self.mode_combox.insertItem(self.__tr("Build"))
        self.mode_combox.insertItem(self.__tr("Cookie Cutter"))
        self.mode_combox.insertItem(self.__tr("Extrude"))
        self.mode_combox.insertItem(self.__tr("Fuse Chunks"))
        self.mode_combox.insertItem(self.__tr("Movie Player"))
        self.choose_bg1_color_btn.setText(self.__tr("Choose..."))
        self.bg1_color_lbl.setText(self.__tr("Color :"))
        self.fill_type_lbl.setText(self.__tr("Fill Type :"))
        self.fill_type_combox.clear()
        self.fill_type_combox.insertItem(self.__tr("Solid"))
        self.fill_type_combox.insertItem(self.__tr("Blue Sky"))
        self.restore_bgcolor_btn.setText(self.__tr("Restore Default Color"))
        self.prefs_tab.changeTab(self.TabPage_3,self.__tr("Background"))
        self.history_height_lbl.setText(self.__tr("Height :"))
        QToolTip.add(self.history_height_spinbox,self.__tr("Number of lines displayed in the history area."))
        self.history_lines_lbl.setText(self.__tr("lines"))
        self.msg_serial_number_checkbox.setText(self.__tr("Include message serial number"))
        self.msg_timestamp_checkbox.setText(self.__tr("Include message timestamp"))
        self.prefs_tab.changeTab(self.TabPage_4,self.__tr("History"))
        self.groupBox3.setTitle(self.__tr("Window Caption Format"))
        QToolTip.add(self.groupBox3,self.__tr("Window Border Caption Format"))
        QWhatsThis.add(self.groupBox3,self.__tr("Format Prefix and Suffix text the delimits the part name in the caption in window border."))
        self.textLabel2.setText(self.__tr("Caption Prefix for Modified File :"))
        self.textLabel2_2.setText(self.__tr("Caption Suffix for Modified File :"))
        self.caption_suffix_linedit.setText(QString.null)
        self.caption_fullpath_checkbox.setText(self.__tr("Display full path of part"))
        self.prefs_tab.changeTab(self.TabPage_5,self.__tr("Caption"))


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

    def setup_current_page(self):
        print "UserPrefsDialog.setup_current_page(): Not implemented yet"

    def mode_changed(self):
        print "UserPrefsDialog.mode_changed(): Not implemented yet"

    def change_bg1_color(self):
        print "UserPrefsDialog.change_bg1_color(): Not implemented yet"

    def fill_type_changed(self):
        print "UserPrefsDialog.fill_type_changed(): Not implemented yet"

    def restore_default_bgcolor(self):
        print "UserPrefsDialog.restore_default_bgcolor(): Not implemented yet"

    def set_default_display_mode(self):
        print "UserPrefsDialog.set_default_display_mode(): Not implemented yet"

    def set_caption_fullpath(self):
        print "UserPrefsDialog.set_caption_fullpath(): Not implemented yet"

    def set_history_height(self,a0):
        print "UserPrefsDialog.set_history_height(int): Not implemented yet"

    def change_atom_hilite_color(self):
        print "UserPrefsDialog.change_atom_hilite_color(): Not implemented yet"

    def change_bond_hilite_color(self):
        print "UserPrefsDialog.change_bond_hilite_color(): Not implemented yet"

    def change_bond_stretch_color(self):
        print "UserPrefsDialog.change_bond_stretch_color(): Not implemented yet"

    def change_bond_cpk_color(self):
        print "UserPrefsDialog.change_bond_cpk_color(): Not implemented yet"

    def change_bond_vane_color(self):
        print "UserPrefsDialog.change_bond_vane_color(): Not implemented yet"

    def change_high_order_bond_display(self):
        print "UserPrefsDialog.change_high_order_bond_display(): Not implemented yet"

    def change_bond_labels(self,a0):
        print "UserPrefsDialog.change_bond_labels(bool): Not implemented yet"

    def reset_bond_colors(self):
        print "UserPrefsDialog.reset_bond_colors(): Not implemented yet"

    def reset_atom_colors(self):
        print "UserPrefsDialog.reset_atom_colors(): Not implemented yet"

    def change_hotspot_color(self):
        print "UserPrefsDialog.change_hotspot_color(): Not implemented yet"

    def change_show_valence_errors(self):
        print "UserPrefsDialog.change_show_valence_errors(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UserPrefsDialog",s,c)
