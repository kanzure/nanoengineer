# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\UserPrefsDialog.ui'
#
# Created: Sun Dec 4 14:42:31 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
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
        self.ok_btn.setAutoDefault(0)
        layout28.addWidget(self.ok_btn)

        UserPrefsDialogLayout.addLayout(layout28,1,0)

        self.prefs_tab = QTabWidget(self,"prefs_tab")

        self.tab = QWidget(self.prefs_tab,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")
        spacer23 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer23,2,0)

        layout31 = QHBoxLayout(None,0,6,"layout31")

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
        layout31.addWidget(self.groupBox7_2)

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
        layout31.addWidget(self.compass_position_btngrp)

        tabLayout.addLayout(layout31,0,0)

        layout32 = QHBoxLayout(None,0,6,"layout32")

        self.default_projection_btngrp = QButtonGroup(self.tab,"default_projection_btngrp")
        self.default_projection_btngrp.setExclusive(1)
        self.default_projection_btngrp.setColumnLayout(0,Qt.Vertical)
        self.default_projection_btngrp.layout().setSpacing(6)
        self.default_projection_btngrp.layout().setMargin(11)
        default_projection_btngrpLayout = QGridLayout(self.default_projection_btngrp.layout())
        default_projection_btngrpLayout.setAlignment(Qt.AlignTop)

        self.radioButton12 = QRadioButton(self.default_projection_btngrp,"radioButton12")
        self.radioButton12.setChecked(1)

        default_projection_btngrpLayout.addWidget(self.radioButton12,0,0)

        self.radioButton13 = QRadioButton(self.default_projection_btngrp,"radioButton13")

        default_projection_btngrpLayout.addWidget(self.radioButton13,1,0)
        layout32.addWidget(self.default_projection_btngrp)

        self.selection_behavior_btngrp = QButtonGroup(self.tab,"selection_behavior_btngrp")
        self.selection_behavior_btngrp.setProperty("selectedId",QVariant(-1))
        self.selection_behavior_btngrp.setColumnLayout(0,Qt.Vertical)
        self.selection_behavior_btngrp.layout().setSpacing(6)
        self.selection_behavior_btngrp.layout().setMargin(11)
        selection_behavior_btngrpLayout = QVBoxLayout(self.selection_behavior_btngrp.layout())
        selection_behavior_btngrpLayout.setAlignment(Qt.AlignTop)

        self.alpha7_behavior_rbtn = QRadioButton(self.selection_behavior_btngrp,"alpha7_behavior_rbtn")
        self.selection_behavior_btngrp.insert( self.alpha7_behavior_rbtn,0)
        selection_behavior_btngrpLayout.addWidget(self.alpha7_behavior_rbtn)

        self.alpha6_behavior_rbtn = QRadioButton(self.selection_behavior_btngrp,"alpha6_behavior_rbtn")
        self.alpha6_behavior_rbtn.setChecked(0)
        self.selection_behavior_btngrp.insert( self.alpha6_behavior_rbtn,1)
        selection_behavior_btngrpLayout.addWidget(self.alpha6_behavior_rbtn)
        layout32.addWidget(self.selection_behavior_btngrp)

        self.groupBox8 = QGroupBox(self.tab,"groupBox8")
        self.groupBox8.setColumnLayout(0,Qt.Vertical)
        self.groupBox8.layout().setSpacing(6)
        self.groupBox8.layout().setMargin(11)
        groupBox8Layout = QGridLayout(self.groupBox8.layout())
        groupBox8Layout.setAlignment(Qt.AlignTop)

        self.animate_views_checkbox = QCheckBox(self.groupBox8,"animate_views_checkbox")
        self.animate_views_checkbox.setChecked(1)

        groupBox8Layout.addWidget(self.animate_views_checkbox,0,0)
        layout32.addWidget(self.groupBox8)
        spacer25 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout32.addItem(spacer25)

        tabLayout.addLayout(layout32,1,0)
        self.prefs_tab.insertTab(self.tab,QString.fromLatin1(""))

        self.TabPage = QWidget(self.prefs_tab,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")
        spacer9 = QSpacerItem(3,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout.addItem(spacer9,0,2)

        layout24 = QVBoxLayout(None,0,6,"layout24")

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
        layout24.addWidget(self.default_display_btngrp)
        spacer11 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout24.addItem(spacer11)

        TabPageLayout.addLayout(layout24,0,1)

        layout60 = QVBoxLayout(None,0,6,"layout60")

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
        layout60.addWidget(self.atom_colors_grpbox)

        layout59 = QHBoxLayout(None,0,6,"layout59")

        self.textLabel1_3_2 = QLabel(self.TabPage,"textLabel1_3_2")
        layout59.addWidget(self.textLabel1_3_2)

        self.cpk_atom_rad_spinbox = QSpinBox(self.TabPage,"cpk_atom_rad_spinbox")
        self.cpk_atom_rad_spinbox.setMaxValue(125)
        self.cpk_atom_rad_spinbox.setMinValue(50)
        self.cpk_atom_rad_spinbox.setValue(100)
        layout59.addWidget(self.cpk_atom_rad_spinbox)

        self.textLabel1_4 = QLabel(self.TabPage,"textLabel1_4")
        layout59.addWidget(self.textLabel1_4)
        spacer38 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(spacer38)
        layout60.addLayout(layout59)
        spacer11_4 = QSpacerItem(20,102,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout60.addItem(spacer11_4)

        TabPageLayout.addLayout(layout60,0,0)
        self.prefs_tab.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.prefs_tab,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")
        spacer22 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_2.addItem(spacer22,3,0)
        spacer19 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_2.addItem(spacer19,0,2)

        layout26 = QVBoxLayout(None,0,6,"layout26")

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
        layout26.addWidget(self.high_order_bond_display_btngrp)

        self.show_bond_labels_checkbox = QCheckBox(self.TabPage_2,"show_bond_labels_checkbox")
        layout26.addWidget(self.show_bond_labels_checkbox)

        self.show_valence_errors_checkbox = QCheckBox(self.TabPage_2,"show_valence_errors_checkbox")
        layout26.addWidget(self.show_valence_errors_checkbox)
        spacer18 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout26.addItem(spacer18)

        TabPageLayout_2.addMultiCellLayout(layout26,0,2,1,1)

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
        self.bond_hilite_color_frame.setMaximumSize(QSize(32767,32767))
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
        self.bond_vane_color_frame.setMaximumSize(QSize(32767,32767))
        self.bond_vane_color_frame.setPaletteBackgroundColor(QColor(255,0,0))
        self.bond_vane_color_frame.setFrameShape(QFrame.Box)
        self.bond_vane_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_frame)

        self.bond_vane_color_btn = QPushButton(self.groupBox4,"bond_vane_color_btn")
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_btn)

        layout61.addLayout(layout37_2_2_2_2_3,4,1)

        self.textLabel3_2_2 = QLabel(self.groupBox4,"textLabel3_2_2")
        self.textLabel3_2_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.textLabel3_2_2.sizePolicy().hasHeightForWidth()))
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
        self.bond_stretch_color_frame.setMaximumSize(QSize(32767,32767))
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

        TabPageLayout_2.addWidget(self.groupBox4,0,0)

        layout29 = QHBoxLayout(None,0,6,"layout29")

        self.textLabel1 = QLabel(self.TabPage_2,"textLabel1")
        layout29.addWidget(self.textLabel1)

        self.bond_line_thickness_spinbox = QSpinBox(self.TabPage_2,"bond_line_thickness_spinbox")
        self.bond_line_thickness_spinbox.setMaxValue(3)
        self.bond_line_thickness_spinbox.setMinValue(1)
        layout29.addWidget(self.bond_line_thickness_spinbox)

        self.textLabel1_2 = QLabel(self.TabPage_2,"textLabel1_2")
        layout29.addWidget(self.textLabel1_2)
        spacer22_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout29.addItem(spacer22_2)

        TabPageLayout_2.addLayout(layout29,1,0)

        layout61_2 = QHBoxLayout(None,0,6,"layout61_2")

        self.textLabel1_3 = QLabel(self.TabPage_2,"textLabel1_3")
        layout61_2.addWidget(self.textLabel1_3)

        self.cpk_cylinder_rad_spinbox = QSpinBox(self.TabPage_2,"cpk_cylinder_rad_spinbox")
        self.cpk_cylinder_rad_spinbox.setMaxValue(125)
        self.cpk_cylinder_rad_spinbox.setMinValue(50)
        self.cpk_cylinder_rad_spinbox.setValue(100)
        layout61_2.addWidget(self.cpk_cylinder_rad_spinbox)

        self.textLabel1_2_2 = QLabel(self.TabPage_2,"textLabel1_2_2")
        layout61_2.addWidget(self.textLabel1_2_2)
        spacer22_2_2 = QSpacerItem(31,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout61_2.addItem(spacer22_2_2)

        TabPageLayout_2.addLayout(layout61_2,2,0)
        self.prefs_tab.insertTab(self.TabPage_2,QString.fromLatin1(""))

        self.TabPage_3 = QWidget(self.prefs_tab,"TabPage_3")
        TabPageLayout_3 = QGridLayout(self.TabPage_3,1,1,11,6,"TabPageLayout_3")
        spacer8_4 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_3.addItem(spacer8_4,0,1)

        layout66 = QVBoxLayout(None,0,6,"layout66")

        layout60_2 = QGridLayout(None,1,1,0,6,"layout60_2")

        self.default_mode_lbl = QLabel(self.TabPage_3,"default_mode_lbl")
        self.default_mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout60_2.addWidget(self.default_mode_lbl,0,0)

        self.default_mode_combox = QComboBox(0,self.TabPage_3,"default_mode_combox")

        layout60_2.addWidget(self.default_mode_combox,0,1)

        self.startup_mode_lbl = QLabel(self.TabPage_3,"startup_mode_lbl")
        self.startup_mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout60_2.addWidget(self.startup_mode_lbl,1,0)

        self.startup_mode_combox = QComboBox(0,self.TabPage_3,"startup_mode_combox")

        layout60_2.addWidget(self.startup_mode_combox,1,1)
        layout66.addLayout(layout60_2)
        spacer8_3_2 = QSpacerItem(20,10,QSizePolicy.Minimum,QSizePolicy.Fixed)
        layout66.addItem(spacer8_3_2)

        self.groupBox11 = QGroupBox(self.TabPage_3,"groupBox11")
        self.groupBox11.setColumnLayout(0,Qt.Vertical)
        self.groupBox11.layout().setSpacing(6)
        self.groupBox11.layout().setMargin(11)
        groupBox11Layout = QGridLayout(self.groupBox11.layout())
        groupBox11Layout.setAlignment(Qt.AlignTop)

        self.restore_bgcolor_btn = QPushButton(self.groupBox11,"restore_bgcolor_btn")

        groupBox11Layout.addWidget(self.restore_bgcolor_btn,1,1)
        spacer7_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox11Layout.addItem(spacer7_2,1,0)

        layout65 = QGridLayout(None,1,1,0,6,"layout65")

        layout64 = QVBoxLayout(None,0,6,"layout64")

        self.mode_lbl = QLabel(self.groupBox11,"mode_lbl")
        self.mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout64.addWidget(self.mode_lbl)

        self.fill_type_lbl = QLabel(self.groupBox11,"fill_type_lbl")
        self.fill_type_lbl.setEnabled(1)
        self.fill_type_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout64.addWidget(self.fill_type_lbl)

        self.bg1_color_lbl = QLabel(self.groupBox11,"bg1_color_lbl")
        self.bg1_color_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout64.addWidget(self.bg1_color_lbl)

        layout65.addLayout(layout64,0,0)

        layout63 = QVBoxLayout(None,0,6,"layout63")

        self.mode_combox = QComboBox(0,self.groupBox11,"mode_combox")
        layout63.addWidget(self.mode_combox)

        self.fill_type_combox = QComboBox(0,self.groupBox11,"fill_type_combox")
        self.fill_type_combox.setEnabled(1)
        layout63.addWidget(self.fill_type_combox)

        layout37 = QHBoxLayout(None,0,6,"layout37")

        self.bg1_color_frame = QFrame(self.groupBox11,"bg1_color_frame")
        self.bg1_color_frame.setMinimumSize(QSize(25,0))
        self.bg1_color_frame.setPaletteBackgroundColor(QColor(170,255,255))
        self.bg1_color_frame.setFrameShape(QFrame.Box)
        self.bg1_color_frame.setFrameShadow(QFrame.Plain)
        layout37.addWidget(self.bg1_color_frame)

        self.choose_bg1_color_btn = QPushButton(self.groupBox11,"choose_bg1_color_btn")
        layout37.addWidget(self.choose_bg1_color_btn)
        layout63.addLayout(layout37)

        layout65.addLayout(layout63,0,1)

        groupBox11Layout.addMultiCellLayout(layout65,0,0,0,1)
        layout66.addWidget(self.groupBox11)
        spacer8_3 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout66.addItem(spacer8_3)

        TabPageLayout_3.addLayout(layout66,0,0)
        self.prefs_tab.insertTab(self.TabPage_3,QString.fromLatin1(""))

        self.TabPage_4 = QWidget(self.prefs_tab,"TabPage_4")
        TabPageLayout_4 = QGridLayout(self.TabPage_4,1,1,11,6,"TabPageLayout_4")

        self.groupBox8_2 = QGroupBox(self.TabPage_4,"groupBox8_2")
        self.groupBox8_2.setEnabled(1)
        self.groupBox8_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox8_2.layout().setSpacing(6)
        self.groupBox8_2.layout().setMargin(11)
        groupBox8_2Layout = QGridLayout(self.groupBox8_2.layout())
        groupBox8_2Layout.setAlignment(Qt.AlignTop)

        layout494 = QVBoxLayout(None,0,6,"layout494")

        self.light_label = QLabel(self.groupBox8_2,"light_label")
        self.light_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.light_label)

        self.on_label = QLabel(self.groupBox8_2,"on_label")
        self.on_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.on_label)

        self.color_label = QLabel(self.groupBox8_2,"color_label")
        self.color_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.color_label)

        self.ambient_label = QLabel(self.groupBox8_2,"ambient_label")
        self.ambient_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.ambient_label)

        self.diffuse_label = QLabel(self.groupBox8_2,"diffuse_label")
        self.diffuse_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.diffuse_label)

        self.specularity_label = QLabel(self.groupBox8_2,"specularity_label")
        self.specularity_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.specularity_label)

        self.x_label = QLabel(self.groupBox8_2,"x_label")
        self.x_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.x_label)

        self.y_label = QLabel(self.groupBox8_2,"y_label")
        self.y_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.y_label)

        self.z_label = QLabel(self.groupBox8_2,"z_label")
        self.z_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout494.addWidget(self.z_label)

        groupBox8_2Layout.addLayout(layout494,0,0)

        layout559 = QVBoxLayout(None,0,6,"layout559")

        layout558 = QHBoxLayout(None,0,6,"layout558")

        self.light_combobox = QComboBox(0,self.groupBox8_2,"light_combobox")
        layout558.addWidget(self.light_combobox)
        spacer342 = QSpacerItem(60,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout558.addItem(spacer342)
        layout559.addLayout(layout558)

        layout69 = QHBoxLayout(None,0,6,"layout69")

        self.light_checkbox = QCheckBox(self.groupBox8_2,"light_checkbox")
        layout69.addWidget(self.light_checkbox)
        spacer45 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout69.addItem(spacer45)
        layout559.addLayout(layout69)

        layout82 = QHBoxLayout(None,0,6,"layout82")

        layout37_2_2_2_4 = QHBoxLayout(None,0,6,"layout37_2_2_2_4")

        self.light1_color_frame = QFrame(self.groupBox8_2,"light1_color_frame")
        self.light1_color_frame.setMinimumSize(QSize(25,0))
        self.light1_color_frame.setPaletteBackgroundColor(QColor(255,255,255))
        self.light1_color_frame.setFrameShape(QFrame.Box)
        self.light1_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_4.addWidget(self.light1_color_frame)

        self.light_color_btn = QPushButton(self.groupBox8_2,"light_color_btn")
        layout37_2_2_2_4.addWidget(self.light_color_btn)
        layout82.addLayout(layout37_2_2_2_4)
        spacer50 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout82.addItem(spacer50)
        layout559.addLayout(layout82)

        layout66_2 = QHBoxLayout(None,0,6,"layout66_2")

        self.light_ambient_linedit = QLineEdit(self.groupBox8_2,"light_ambient_linedit")
        self.light_ambient_linedit.setMaximumSize(QSize(40,32767))
        self.light_ambient_linedit.setReadOnly(1)
        layout66_2.addWidget(self.light_ambient_linedit)

        self.light_ambient_slider = QSlider(self.groupBox8_2,"light_ambient_slider")
        self.light_ambient_slider.setMaxValue(100)
        self.light_ambient_slider.setOrientation(QSlider.Horizontal)
        self.light_ambient_slider.setTickmarks(QSlider.NoMarks)
        self.light_ambient_slider.setTickInterval(10)
        layout66_2.addWidget(self.light_ambient_slider)
        layout559.addLayout(layout66_2)

        layout65_2 = QHBoxLayout(None,0,6,"layout65_2")

        self.light_diffuse_linedit = QLineEdit(self.groupBox8_2,"light_diffuse_linedit")
        self.light_diffuse_linedit.setMaximumSize(QSize(40,32767))
        self.light_diffuse_linedit.setReadOnly(1)
        layout65_2.addWidget(self.light_diffuse_linedit)

        self.light_diffuse_slider = QSlider(self.groupBox8_2,"light_diffuse_slider")
        self.light_diffuse_slider.setMaxValue(100)
        self.light_diffuse_slider.setOrientation(QSlider.Horizontal)
        self.light_diffuse_slider.setTickmarks(QSlider.NoMarks)
        self.light_diffuse_slider.setTickInterval(10)
        layout65_2.addWidget(self.light_diffuse_slider)
        layout559.addLayout(layout65_2)

        layout64_2 = QHBoxLayout(None,0,6,"layout64_2")

        self.light_specularity_linedit = QLineEdit(self.groupBox8_2,"light_specularity_linedit")
        self.light_specularity_linedit.setMaximumSize(QSize(40,32767))
        self.light_specularity_linedit.setReadOnly(1)
        layout64_2.addWidget(self.light_specularity_linedit)

        self.light_specularity_slider = QSlider(self.groupBox8_2,"light_specularity_slider")
        self.light_specularity_slider.setMaxValue(100)
        self.light_specularity_slider.setOrientation(QSlider.Horizontal)
        self.light_specularity_slider.setTickmarks(QSlider.NoMarks)
        self.light_specularity_slider.setTickInterval(10)
        layout64_2.addWidget(self.light_specularity_slider)
        layout559.addLayout(layout64_2)

        layout63_2 = QHBoxLayout(None,0,6,"layout63_2")

        self.light_x_linedit = QLineEdit(self.groupBox8_2,"light_x_linedit")
        layout63_2.addWidget(self.light_x_linedit)
        spacer42 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout63_2.addItem(spacer42)
        layout559.addLayout(layout63_2)

        layout62 = QHBoxLayout(None,0,6,"layout62")

        self.light_y_linedit = QLineEdit(self.groupBox8_2,"light_y_linedit")
        layout62.addWidget(self.light_y_linedit)
        spacer43 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout62.addItem(spacer43)
        layout559.addLayout(layout62)

        layout61_3 = QHBoxLayout(None,0,6,"layout61_3")

        self.light_z_linedit = QLineEdit(self.groupBox8_2,"light_z_linedit")
        self.light_z_linedit.setMaxLength(32767)
        layout61_3.addWidget(self.light_z_linedit)
        spacer44 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout61_3.addItem(spacer44)
        layout559.addLayout(layout61_3)

        groupBox8_2Layout.addLayout(layout559,0,1)

        TabPageLayout_4.addMultiCellWidget(self.groupBox8_2,0,2,0,0)

        layout505 = QHBoxLayout(None,0,6,"layout505")
        spacer57 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout505.addItem(spacer57)

        self.lighting_reset_btn = QPushButton(self.TabPage_4,"lighting_reset_btn")
        layout505.addWidget(self.lighting_reset_btn)

        self.lighting_restore_defaults_btn = QPushButton(self.TabPage_4,"lighting_restore_defaults_btn")
        layout505.addWidget(self.lighting_restore_defaults_btn)

        TabPageLayout_4.addLayout(layout505,2,1)
        spacer345 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_4.addItem(spacer345,1,1)

        self.groupBox9_2 = QGroupBox(self.TabPage_4,"groupBox9_2")
        self.groupBox9_2.setEnabled(1)
        self.groupBox9_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox9_2.layout().setSpacing(6)
        self.groupBox9_2.layout().setMargin(11)
        groupBox9_2Layout = QGridLayout(self.groupBox9_2.layout())
        groupBox9_2Layout.setAlignment(Qt.AlignTop)

        layout57 = QVBoxLayout(None,0,6,"layout57")

        self.ms_on_label = QLabel(self.groupBox9_2,"ms_on_label")
        self.ms_on_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout57.addWidget(self.ms_on_label)
        spacer38_2 = QSpacerItem(70,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout57.addItem(spacer38_2)

        self.ms_finish_label = QLabel(self.groupBox9_2,"ms_finish_label")
        self.ms_finish_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout57.addWidget(self.ms_finish_label)

        self.ms_shininess_label = QLabel(self.groupBox9_2,"ms_shininess_label")
        self.ms_shininess_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout57.addWidget(self.ms_shininess_label)

        self.ms_brightness__label = QLabel(self.groupBox9_2,"ms_brightness__label")
        self.ms_brightness__label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout57.addWidget(self.ms_brightness__label)

        groupBox9_2Layout.addLayout(layout57,0,0)

        layout58_2 = QVBoxLayout(None,0,6,"layout58_2")

        self.ms_on_checkbox = QCheckBox(self.groupBox9_2,"ms_on_checkbox")
        layout58_2.addWidget(self.ms_on_checkbox)
        spacer39 = QSpacerItem(38,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout58_2.addItem(spacer39)

        self.ms_finish_linedit = QLineEdit(self.groupBox9_2,"ms_finish_linedit")
        self.ms_finish_linedit.setMaximumSize(QSize(50,32767))
        self.ms_finish_linedit.setMaxLength(5)
        self.ms_finish_linedit.setReadOnly(1)
        layout58_2.addWidget(self.ms_finish_linedit)

        self.ms_shininess_linedit = QLineEdit(self.groupBox9_2,"ms_shininess_linedit")
        self.ms_shininess_linedit.setMaximumSize(QSize(50,32767))
        self.ms_shininess_linedit.setMaxLength(5)
        self.ms_shininess_linedit.setReadOnly(1)
        layout58_2.addWidget(self.ms_shininess_linedit)

        self.ms_brightness_linedit = QLineEdit(self.groupBox9_2,"ms_brightness_linedit")
        self.ms_brightness_linedit.setMaximumSize(QSize(50,32767))
        self.ms_brightness_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.ms_brightness_linedit.setFrameShadow(QLineEdit.Sunken)
        self.ms_brightness_linedit.setMaxLength(5)
        self.ms_brightness_linedit.setReadOnly(1)
        layout58_2.addWidget(self.ms_brightness_linedit)

        groupBox9_2Layout.addLayout(layout58_2,0,1)

        layout59_2 = QVBoxLayout(None,0,6,"layout59_2")
        spacer36 = QSpacerItem(30,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59_2.addItem(spacer36)

        layout46 = QHBoxLayout(None,0,6,"layout46")

        self.textLabel1_6 = QLabel(self.groupBox9_2,"textLabel1_6")
        layout46.addWidget(self.textLabel1_6)
        spacer37 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46.addItem(spacer37)

        self.textLabel2_4 = QLabel(self.groupBox9_2,"textLabel2_4")
        layout46.addWidget(self.textLabel2_4)
        layout59_2.addLayout(layout46)

        self.ms_finish_slider = QSlider(self.groupBox9_2,"ms_finish_slider")
        self.ms_finish_slider.setMinValue(0)
        self.ms_finish_slider.setMaxValue(100)
        self.ms_finish_slider.setValue(50)
        self.ms_finish_slider.setOrientation(QSlider.Horizontal)
        self.ms_finish_slider.setTickmarks(QSlider.NoMarks)
        self.ms_finish_slider.setTickInterval(5)
        layout59_2.addWidget(self.ms_finish_slider)

        self.ms_shininess_slider = QSlider(self.groupBox9_2,"ms_shininess_slider")
        self.ms_shininess_slider.setMinValue(15)
        self.ms_shininess_slider.setMaxValue(60)
        self.ms_shininess_slider.setValue(15)
        self.ms_shininess_slider.setOrientation(QSlider.Horizontal)
        self.ms_shininess_slider.setTickmarks(QSlider.NoMarks)
        self.ms_shininess_slider.setTickInterval(5)
        layout59_2.addWidget(self.ms_shininess_slider)

        self.ms_brightness_slider = QSlider(self.groupBox9_2,"ms_brightness_slider")
        self.ms_brightness_slider.setMinValue(0)
        self.ms_brightness_slider.setMaxValue(100)
        self.ms_brightness_slider.setValue(50)
        self.ms_brightness_slider.setOrientation(QSlider.Horizontal)
        self.ms_brightness_slider.setTickmarks(QSlider.NoMarks)
        self.ms_brightness_slider.setTickInterval(5)
        layout59_2.addWidget(self.ms_brightness_slider)

        groupBox9_2Layout.addLayout(layout59_2,0,2)

        TabPageLayout_4.addWidget(self.groupBox9_2,0,1)
        self.prefs_tab.insertTab(self.TabPage_4,QString.fromLatin1(""))

        self.TabPage_5 = QWidget(self.prefs_tab,"TabPage_5")
        TabPageLayout_5 = QGridLayout(self.TabPage_5,1,1,11,6,"TabPageLayout_5")
        spacer24 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_5.addItem(spacer24,1,0)

        self.file_locations_grp = QGroupBox(self.TabPage_5,"file_locations_grp")
        self.file_locations_grp.setColumnLayout(0,Qt.Vertical)
        self.file_locations_grp.layout().setSpacing(6)
        self.file_locations_grp.layout().setMargin(11)
        file_locations_grpLayout = QGridLayout(self.file_locations_grp.layout())
        file_locations_grpLayout.setAlignment(Qt.AlignTop)

        layout80 = QGridLayout(None,1,1,0,6,"layout80")

        self.nanohive_path_linedit = QLineEdit(self.file_locations_grp,"nanohive_path_linedit")
        self.nanohive_path_linedit.setEnabled(0)
        self.nanohive_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.nanohive_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.nanohive_path_linedit.setReadOnly(1)

        layout80.addWidget(self.nanohive_path_linedit,1,0)

        self.gamess_path_linedit = QLineEdit(self.file_locations_grp,"gamess_path_linedit")
        self.gamess_path_linedit.setEnabled(0)
        self.gamess_path_linedit.setMaximumSize(QSize(32767,32767))
        self.gamess_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.gamess_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.gamess_path_linedit.setMaxLength(32767)
        self.gamess_path_linedit.setReadOnly(1)

        layout80.addWidget(self.gamess_path_linedit,0,0)

        self.nanohive_choose_btn = QPushButton(self.file_locations_grp,"nanohive_choose_btn")
        self.nanohive_choose_btn.setEnabled(0)

        layout80.addWidget(self.nanohive_choose_btn,1,1)

        self.gamess_choose_btn = QPushButton(self.file_locations_grp,"gamess_choose_btn")
        self.gamess_choose_btn.setEnabled(0)

        layout80.addWidget(self.gamess_choose_btn,0,1)

        file_locations_grpLayout.addLayout(layout80,0,1)

        layout63_3 = QGridLayout(None,1,1,0,6,"layout63_3")

        self.gamess_lbl = QLabel(self.file_locations_grp,"gamess_lbl")
        self.gamess_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.gamess_lbl.sizePolicy().hasHeightForWidth()))
        self.gamess_lbl.setMinimumSize(QSize(60,0))
        self.gamess_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout63_3.addWidget(self.gamess_lbl,0,1)

        self.nanohive_lbl = QLabel(self.file_locations_grp,"nanohive_lbl")
        self.nanohive_lbl.setEnabled(0)
        self.nanohive_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.nanohive_lbl.sizePolicy().hasHeightForWidth()))
        self.nanohive_lbl.setMinimumSize(QSize(60,0))
        self.nanohive_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout63_3.addWidget(self.nanohive_lbl,1,1)

        self.gamess_checkbox = QCheckBox(self.file_locations_grp,"gamess_checkbox")

        layout63_3.addWidget(self.gamess_checkbox,0,0)

        self.nanohive_checkbox = QCheckBox(self.file_locations_grp,"nanohive_checkbox")
        self.nanohive_checkbox.setEnabled(0)

        layout63_3.addWidget(self.nanohive_checkbox,1,0)

        file_locations_grpLayout.addLayout(layout63_3,0,0)

        TabPageLayout_5.addWidget(self.file_locations_grp,0,0)
        self.prefs_tab.insertTab(self.TabPage_5,QString.fromLatin1(""))

        self.TabPage_6 = QWidget(self.prefs_tab,"TabPage_6")
        TabPageLayout_6 = QVBoxLayout(self.TabPage_6,11,6,"TabPageLayout_6")

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.history_height_lbl = QLabel(self.TabPage_6,"history_height_lbl")
        self.history_height_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout9.addWidget(self.history_height_lbl)

        self.history_height_spinbox = QSpinBox(self.TabPage_6,"history_height_spinbox")
        self.history_height_spinbox.setMaxValue(20)
        self.history_height_spinbox.setValue(4)
        layout9.addWidget(self.history_height_spinbox)

        self.history_lines_lbl = QLabel(self.TabPage_6,"history_lines_lbl")
        layout9.addWidget(self.history_lines_lbl)
        spacer11_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout9.addItem(spacer11_2)
        TabPageLayout_6.addLayout(layout9)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.msg_serial_number_checkbox = QCheckBox(self.TabPage_6,"msg_serial_number_checkbox")
        layout11.addWidget(self.msg_serial_number_checkbox)
        spacer12 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout11.addItem(spacer12)
        TabPageLayout_6.addLayout(layout11)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.msg_timestamp_checkbox = QCheckBox(self.TabPage_6,"msg_timestamp_checkbox")
        layout10.addWidget(self.msg_timestamp_checkbox)
        spacer13 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout10.addItem(spacer13)
        TabPageLayout_6.addLayout(layout10)
        spacer10 = QSpacerItem(20,80,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_6.addItem(spacer10)
        self.prefs_tab.insertTab(self.TabPage_6,QString.fromLatin1(""))

        self.TabPage_7 = QWidget(self.prefs_tab,"TabPage_7")
        TabPageLayout_7 = QGridLayout(self.TabPage_7,1,1,11,6,"TabPageLayout_7")

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.groupBox3 = QGroupBox(self.TabPage_7,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QVBoxLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        self.textLabel2 = QLabel(self.groupBox3,"textLabel2")
        groupBox3Layout.addWidget(self.textLabel2)

        self.caption_prefix_linedit = QLineEdit(self.groupBox3,"caption_prefix_linedit")
        self.caption_prefix_linedit.setMinimumSize(QSize(0,0))
        self.caption_prefix_linedit.setMaximumSize(QSize(32767,32767))
        self.caption_prefix_linedit.setPaletteBackgroundColor(QColor(255,255,255))
        self.caption_prefix_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.caption_prefix_linedit.setFrameShadow(QLineEdit.Sunken)
        groupBox3Layout.addWidget(self.caption_prefix_linedit)

        self.textLabel2_2 = QLabel(self.groupBox3,"textLabel2_2")
        groupBox3Layout.addWidget(self.textLabel2_2)

        self.caption_suffix_linedit = QLineEdit(self.groupBox3,"caption_suffix_linedit")
        self.caption_suffix_linedit.setMinimumSize(QSize(0,0))
        self.caption_suffix_linedit.setMaximumSize(QSize(32767,32767))
        self.caption_suffix_linedit.setPaletteBackgroundColor(QColor(255,255,255))
        self.caption_suffix_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.caption_suffix_linedit.setFrameShadow(QLineEdit.Sunken)
        groupBox3Layout.addWidget(self.caption_suffix_linedit)

        self.caption_fullpath_checkbox = QCheckBox(self.groupBox3,"caption_fullpath_checkbox")
        groupBox3Layout.addWidget(self.caption_fullpath_checkbox)
        layout15.addWidget(self.groupBox3)
        spacer9_2 = QSpacerItem(210,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout15.addItem(spacer9_2)

        TabPageLayout_7.addLayout(layout15,0,0)
        spacer11_3 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_7.addItem(spacer11_3,1,0)
        self.prefs_tab.insertTab(self.TabPage_7,QString.fromLatin1(""))

        UserPrefsDialogLayout.addWidget(self.prefs_tab,0,0)

        self.languageChange()

        self.resize(QSize(559,400).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.animate_views_checkbox,SIGNAL("stateChanged(int)"),self.change_animate_standard_views)
        self.connect(self.atom_hilite_color_btn,SIGNAL("clicked()"),self.change_atom_hilite_color)
        self.connect(self.bond_cpk_color_btn,SIGNAL("clicked()"),self.change_bond_cpk_color)
        self.connect(self.bond_hilite_color_btn,SIGNAL("clicked()"),self.change_bond_hilite_color)
        self.connect(self.bond_line_thickness_spinbox,SIGNAL("valueChanged(int)"),self.change_bond_line_thickness)
        self.connect(self.bond_stretch_color_btn,SIGNAL("clicked()"),self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn,SIGNAL("clicked()"),self.change_bond_vane_color)
        self.connect(self.ms_brightness_slider,SIGNAL("valueChanged(int)"),self.change_material_brightness)
        self.connect(self.caption_fullpath_checkbox,SIGNAL("stateChanged(int)"),self.set_caption_fullpath)
        self.connect(self.choose_bg1_color_btn,SIGNAL("clicked()"),self.change_bg1_color)
        self.connect(self.compass_position_btngrp,SIGNAL("clicked(int)"),self.set_compass_position)
        self.connect(self.cpk_atom_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_cpk_atom_radius)
        self.connect(self.cpk_cylinder_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_cpk_cylinder_radius)
        self.connect(self.default_display_btngrp,SIGNAL("clicked(int)"),self.set_default_display_mode)
        self.connect(self.default_mode_combox,SIGNAL("activated(int)"),self.change_default_mode)
        self.connect(self.default_projection_btngrp,SIGNAL("clicked(int)"),self.set_default_projection)
        self.connect(self.display_compass_checkbox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.display_origin_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_origin_axis)
        self.connect(self.display_pov_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_pov_axis)
        self.connect(self.fill_type_combox,SIGNAL("activated(const QString&)"),self.fill_type_changed)
        self.connect(self.ms_finish_slider,SIGNAL("valueChanged(int)"),self.change_material_finish)
        self.connect(self.gamess_checkbox,SIGNAL("toggled(bool)"),self.enable_gamess)
        self.connect(self.gamess_choose_btn,SIGNAL("clicked()"),self.set_gamess_path)
        self.connect(self.high_order_bond_display_btngrp,SIGNAL("clicked(int)"),self.change_high_order_bond_display)
        self.connect(self.history_height_spinbox,SIGNAL("valueChanged(int)"),self.set_history_height)
        self.connect(self.hotspot_color_btn,SIGNAL("clicked()"),self.change_hotspot_color)
        self.connect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_ambient_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_checkbox,SIGNAL("toggled(bool)"),self.toggle_light)
        self.connect(self.light_checkbox,SIGNAL("clicked()"),self.save_lighting)
        self.connect(self.light_combobox,SIGNAL("activated(int)"),self.change_active_light)
        self.connect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_diffuse_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_x_linedit,SIGNAL("returnPressed()"),self.change_lighting)
        self.connect(self.light_y_linedit,SIGNAL("returnPressed()"),self.change_lighting)
        self.connect(self.light_z_linedit,SIGNAL("returnPressed()"),self.change_lighting)
        self.connect(self.lighting_reset_btn,SIGNAL("clicked()"),self.reset_lighting)
        self.connect(self.lighting_restore_defaults_btn,SIGNAL("clicked()"),self.restore_default_lighting)
        self.connect(self.mode_combox,SIGNAL("activated(int)"),self.mode_changed)
        self.connect(self.nanohive_checkbox,SIGNAL("toggled(bool)"),self.enable_nanohive)
        self.connect(self.nanohive_choose_btn,SIGNAL("clicked()"),self.set_nanohive_path)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.prefs_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.reset_atom_colors_btn,SIGNAL("clicked()"),self.reset_atom_colors)
        self.connect(self.reset_bond_colors_btn,SIGNAL("clicked()"),self.reset_bond_colors)
        self.connect(self.restore_bgcolor_btn,SIGNAL("clicked()"),self.restore_default_bgcolor)
        self.connect(self.selection_behavior_btngrp,SIGNAL("clicked(int)"),self.set_selection_behavior)
        self.connect(self.ms_shininess_slider,SIGNAL("valueChanged(int)"),self.change_material_shininess)
        self.connect(self.show_bond_labels_checkbox,SIGNAL("toggled(bool)"),self.change_bond_labels)
        self.connect(self.show_valence_errors_checkbox,SIGNAL("toggled(bool)"),self.change_show_valence_errors)
        self.connect(self.startup_mode_combox,SIGNAL("activated(const QString&)"),self.change_startup_mode)
        self.connect(self.ms_on_checkbox,SIGNAL("toggled(bool)"),self.toggle_material_specularity)

        self.setTabOrder(self.prefs_tab,self.display_compass_checkbox)
        self.setTabOrder(self.display_compass_checkbox,self.display_origin_axis_checkbox)
        self.setTabOrder(self.display_origin_axis_checkbox,self.display_pov_axis_checkbox)
        self.setTabOrder(self.display_pov_axis_checkbox,self.upper_right_btn)
        self.setTabOrder(self.upper_right_btn,self.radioButton12)
        self.setTabOrder(self.radioButton12,self.alpha7_behavior_rbtn)
        self.setTabOrder(self.alpha7_behavior_rbtn,self.alpha6_behavior_rbtn)
        self.setTabOrder(self.alpha6_behavior_rbtn,self.animate_views_checkbox)
        self.setTabOrder(self.animate_views_checkbox,self.atom_hilite_color_btn)
        self.setTabOrder(self.atom_hilite_color_btn,self.hotspot_color_btn)
        self.setTabOrder(self.hotspot_color_btn,self.reset_atom_colors_btn)
        self.setTabOrder(self.reset_atom_colors_btn,self.cpk_atom_rad_spinbox)
        self.setTabOrder(self.cpk_atom_rad_spinbox,self.vwd_rbtn)
        self.setTabOrder(self.vwd_rbtn,self.cpk_rbtn)
        self.setTabOrder(self.cpk_rbtn,self.tubes_rbtn)
        self.setTabOrder(self.tubes_rbtn,self.lines_rbtn)
        self.setTabOrder(self.lines_rbtn,self.bond_hilite_color_btn)
        self.setTabOrder(self.bond_hilite_color_btn,self.bond_cpk_color_btn)
        self.setTabOrder(self.bond_cpk_color_btn,self.bond_stretch_color_btn)
        self.setTabOrder(self.bond_stretch_color_btn,self.bond_vane_color_btn)
        self.setTabOrder(self.bond_vane_color_btn,self.reset_bond_colors_btn)
        self.setTabOrder(self.reset_bond_colors_btn,self.bond_line_thickness_spinbox)
        self.setTabOrder(self.bond_line_thickness_spinbox,self.cpk_cylinder_rad_spinbox)
        self.setTabOrder(self.cpk_cylinder_rad_spinbox,self.radioButton11)
        self.setTabOrder(self.radioButton11,self.show_bond_labels_checkbox)
        self.setTabOrder(self.show_bond_labels_checkbox,self.show_valence_errors_checkbox)
        self.setTabOrder(self.show_valence_errors_checkbox,self.default_mode_combox)
        self.setTabOrder(self.default_mode_combox,self.startup_mode_combox)
        self.setTabOrder(self.startup_mode_combox,self.mode_combox)
        self.setTabOrder(self.mode_combox,self.fill_type_combox)
        self.setTabOrder(self.fill_type_combox,self.choose_bg1_color_btn)
        self.setTabOrder(self.choose_bg1_color_btn,self.restore_bgcolor_btn)
        self.setTabOrder(self.restore_bgcolor_btn,self.light_checkbox)
        self.setTabOrder(self.light_checkbox,self.light_color_btn)
        self.setTabOrder(self.light_color_btn,self.light_ambient_linedit)
        self.setTabOrder(self.light_ambient_linedit,self.light_ambient_slider)
        self.setTabOrder(self.light_ambient_slider,self.light_diffuse_linedit)
        self.setTabOrder(self.light_diffuse_linedit,self.light_diffuse_slider)
        self.setTabOrder(self.light_diffuse_slider,self.light_specularity_linedit)
        self.setTabOrder(self.light_specularity_linedit,self.light_specularity_slider)
        self.setTabOrder(self.light_specularity_slider,self.light_x_linedit)
        self.setTabOrder(self.light_x_linedit,self.light_y_linedit)
        self.setTabOrder(self.light_y_linedit,self.light_z_linedit)
        self.setTabOrder(self.light_z_linedit,self.lighting_reset_btn)
        self.setTabOrder(self.lighting_reset_btn,self.lighting_restore_defaults_btn)
        self.setTabOrder(self.lighting_restore_defaults_btn,self.gamess_checkbox)
        self.setTabOrder(self.gamess_checkbox,self.gamess_path_linedit)
        self.setTabOrder(self.gamess_path_linedit,self.gamess_choose_btn)
        self.setTabOrder(self.gamess_choose_btn,self.nanohive_checkbox)
        self.setTabOrder(self.nanohive_checkbox,self.nanohive_path_linedit)
        self.setTabOrder(self.nanohive_path_linedit,self.nanohive_choose_btn)
        self.setTabOrder(self.nanohive_choose_btn,self.history_height_spinbox)
        self.setTabOrder(self.history_height_spinbox,self.msg_serial_number_checkbox)
        self.setTabOrder(self.msg_serial_number_checkbox,self.msg_timestamp_checkbox)
        self.setTabOrder(self.msg_timestamp_checkbox,self.caption_prefix_linedit)
        self.setTabOrder(self.caption_prefix_linedit,self.caption_suffix_linedit)
        self.setTabOrder(self.caption_suffix_linedit,self.caption_fullpath_checkbox)
        self.setTabOrder(self.caption_fullpath_checkbox,self.ok_btn)


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
        self.default_projection_btngrp.setTitle(self.__tr("Default Projection"))
        self.radioButton12.setText(self.__tr("Perspective"))
        self.radioButton13.setText(self.__tr("Orthographic"))
        self.selection_behavior_btngrp.setTitle(self.__tr("Selection Behavior"))
        self.alpha7_behavior_rbtn.setText(self.__tr("Alpha 7"))
        self.alpha6_behavior_rbtn.setText(self.__tr("Alpha 6"))
        self.groupBox8.setTitle(self.__tr("Standard Views"))
        self.animate_views_checkbox.setText(self.__tr("Animate"))
        self.prefs_tab.changeTab(self.tab,self.__tr("General"))
        self.default_display_btngrp.setTitle(self.__tr("Default Display"))
        self.vwd_rbtn.setText(self.__tr("VdW"))
        self.cpk_rbtn.setText(self.__tr("CPK"))
        self.lines_rbtn.setText(self.__tr("Lines"))
        self.tubes_rbtn.setText(self.__tr("Tubes"))
        self.atom_colors_grpbox.setTitle(self.__tr("Colors"))
        self.textLabel3_2_3.setText(self.__tr("Atom Highlighting :"))
        self.hotspot_color_btn.setText(self.__tr("Choose..."))
        self.atom_hilite_color_btn.setText(self.__tr("Choose..."))
        self.hotspot_lbl.setText(self.__tr("Open Bonds Hotspot  :"))
        self.reset_atom_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.textLabel1_3_2.setText(self.__tr("CPK Atom Radius :"))
        QToolTip.add(self.textLabel1_3_2,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.textLabel1_3_2,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.textLabel1_4.setText(self.__tr("%"))
        self.prefs_tab.changeTab(self.TabPage,self.__tr("Atoms"))
        self.high_order_bond_display_btngrp.setTitle(self.__tr("High Order Bonds"))
        self.radioButton11.setText(self.__tr("Multiple Cylinders"))
        self.radioButton11_2.setText(self.__tr("Vanes"))
        self.radioButton11_2_2.setText(self.__tr("Ribbons"))
        self.show_bond_labels_checkbox.setText(self.__tr("Show Bond Type Letters"))
        self.show_valence_errors_checkbox.setText(self.__tr("Show Valence Errors"))
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
        self.textLabel1.setText(self.__tr("Bond Line Thickness :"))
        QToolTip.add(self.textLabel1,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.textLabel1,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QToolTip.add(self.bond_line_thickness_spinbox,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.bond_line_thickness_spinbox,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.textLabel1_2.setText(self.__tr("pixels"))
        self.textLabel1_3.setText(self.__tr("CPK Cylinder Radius :"))
        QToolTip.add(self.textLabel1_3,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.textLabel1_3,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.textLabel1_2_2.setText(self.__tr("%"))
        self.prefs_tab.changeTab(self.TabPage_2,self.__tr("Bonds"))
        self.default_mode_lbl.setText(self.__tr("Default Mode :"))
        self.default_mode_combox.clear()
        self.default_mode_combox.insertItem(self.__tr("Select Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Select Atoms"))
        self.default_mode_combox.insertItem(self.__tr("Move Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Build"))
        self.startup_mode_lbl.setText(self.__tr("Startup Mode :"))
        self.startup_mode_combox.clear()
        self.startup_mode_combox.insertItem(self.__tr("Default Mode"))
        self.startup_mode_combox.insertItem(self.__tr("Build"))
        self.groupBox11.setTitle(self.__tr("Background"))
        self.restore_bgcolor_btn.setText(self.__tr("Restore Default Color"))
        self.mode_lbl.setText(self.__tr("Mode :"))
        self.fill_type_lbl.setText(self.__tr("Fill Type :"))
        self.bg1_color_lbl.setText(self.__tr("Color :"))
        self.mode_combox.clear()
        self.mode_combox.insertItem(self.__tr("Select Chunks"))
        self.mode_combox.insertItem(self.__tr("Select Atoms"))
        self.mode_combox.insertItem(self.__tr("Move Chunks"))
        self.mode_combox.insertItem(self.__tr("Build"))
        self.mode_combox.insertItem(self.__tr("Cookie Cutter"))
        self.mode_combox.insertItem(self.__tr("Extrude"))
        self.mode_combox.insertItem(self.__tr("Fuse Chunks"))
        self.mode_combox.insertItem(self.__tr("Movie Player"))
        self.fill_type_combox.clear()
        self.fill_type_combox.insertItem(self.__tr("Solid"))
        self.fill_type_combox.insertItem(self.__tr("Blue Sky"))
        self.choose_bg1_color_btn.setText(self.__tr("Choose..."))
        self.prefs_tab.changeTab(self.TabPage_3,self.__tr("Modes"))
        self.groupBox8_2.setTitle(self.__tr("Directional Light Properties"))
        self.light_label.setText(self.__tr("Light :"))
        self.on_label.setText(self.__tr("On :"))
        self.color_label.setText(self.__tr("Color :"))
        self.ambient_label.setText(self.__tr("Ambient :"))
        self.diffuse_label.setText(self.__tr("Diffuse :"))
        self.specularity_label.setText(self.__tr("Specularity :"))
        self.x_label.setText(self.__tr("X :"))
        self.y_label.setText(self.__tr("Y :"))
        self.z_label.setText(self.__tr("Z :"))
        self.light_combobox.clear()
        self.light_combobox.insertItem(self.__tr("1 (On)"))
        self.light_combobox.insertItem(self.__tr("2 (On)"))
        self.light_combobox.insertItem(self.__tr("3 (Off)"))
        self.light_checkbox.setText(QString.null)
        self.light_color_btn.setText(self.__tr("Choose..."))
        self.lighting_reset_btn.setText(self.__tr("Reset"))
        self.lighting_restore_defaults_btn.setText(self.__tr("Restore Defaults"))
        self.groupBox9_2.setTitle(self.__tr("Material Specularity Properties"))
        self.ms_on_label.setText(self.__tr("On :"))
        self.ms_finish_label.setText(self.__tr("Finish :"))
        self.ms_shininess_label.setText(self.__tr("Shininess :"))
        self.ms_brightness__label.setText(self.__tr("Brightness :"))
        self.ms_on_checkbox.setText(QString.null)
        self.textLabel1_6.setText(self.__tr("Metal"))
        self.textLabel2_4.setText(self.__tr("Plastic"))
        self.prefs_tab.changeTab(self.TabPage_4,self.__tr("Lighting"))
        self.file_locations_grp.setTitle(self.__tr("Location of Executables"))
        self.nanohive_path_linedit.setText(QString.null)
        self.gamess_path_linedit.setText(QString.null)
        self.nanohive_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_lbl.setText(self.__tr("GAMESS :"))
        QToolTip.add(self.gamess_lbl,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.nanohive_lbl.setText(self.__tr("Nano-Hive :"))
        QToolTip.add(self.nanohive_lbl,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.gamess_checkbox.setText(QString.null)
        self.nanohive_checkbox.setText(QString.null)
        self.prefs_tab.changeTab(self.TabPage_5,self.__tr("Plug-ins"))
        self.history_height_lbl.setText(self.__tr("Height :"))
        QToolTip.add(self.history_height_spinbox,self.__tr("Number of lines displayed in the history area."))
        self.history_lines_lbl.setText(self.__tr("lines"))
        self.msg_serial_number_checkbox.setText(self.__tr("Include message serial number"))
        self.msg_timestamp_checkbox.setText(self.__tr("Include message timestamp"))
        self.prefs_tab.changeTab(self.TabPage_6,self.__tr("History"))
        self.groupBox3.setTitle(self.__tr("Window Caption Format"))
        QToolTip.add(self.groupBox3,self.__tr("Window Border Caption Format"))
        QWhatsThis.add(self.groupBox3,self.__tr("Format Prefix and Suffix text the delimits the part name in the caption in window border."))
        self.textLabel2.setText(self.__tr("Caption Prefix for Modified File :"))
        self.textLabel2_2.setText(self.__tr("Caption Suffix for Modified File :"))
        self.caption_suffix_linedit.setText(QString.null)
        self.caption_fullpath_checkbox.setText(self.__tr("Display full path of part"))
        self.prefs_tab.changeTab(self.TabPage_7,self.__tr("Caption"))


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

    def change_bond_line_thickness(self):
        print "UserPrefsDialog.change_bond_line_thickness(): Not implemented yet"

    def change_startup_mode(self):
        print "UserPrefsDialog.change_startup_mode(): Not implemented yet"

    def change_default_mode(self):
        print "UserPrefsDialog.change_default_mode(): Not implemented yet"

    def set_nanohive_path(self):
        print "UserPrefsDialog.set_nanohive_path(): Not implemented yet"

    def set_default_projection(self):
        print "UserPrefsDialog.set_default_projection(): Not implemented yet"

    def enable_gamess(self):
        print "UserPrefsDialog.enable_gamess(): Not implemented yet"

    def enable_nanohive(self):
        print "UserPrefsDialog.enable_nanohive(): Not implemented yet"

    def set_selection_behavior(self):
        print "UserPrefsDialog.set_selection_behavior(): Not implemented yet"

    def change_cpk_atom_radius(self):
        print "UserPrefsDialog.change_cpk_atom_radius(): Not implemented yet"

    def change_cpk_cylinder_radius(self):
        print "UserPrefsDialog.change_cpk_cylinder_radius(): Not implemented yet"

    def change_animate_standard_views(self):
        print "UserPrefsDialog.change_animate_standard_views(): Not implemented yet"

    def reset_lighting(self):
        print "UserPrefsDialog.reset_lighting(): Not implemented yet"

    def restore_default_lighting(self):
        print "UserPrefsDialog.restore_default_lighting(): Not implemented yet"

    def change_lighting(self):
        print "UserPrefsDialog.change_lighting(): Not implemented yet"

    def save_lighting(self):
        print "UserPrefsDialog.save_lighting(): Not implemented yet"

    def toggle_material_specularity(self):
        print "UserPrefsDialog.toggle_material_specularity(): Not implemented yet"

    def change_material_shininess(self):
        print "UserPrefsDialog.change_material_shininess(): Not implemented yet"

    def change_material_finish(self):
        print "UserPrefsDialog.change_material_finish(): Not implemented yet"

    def change_active_light(self):
        print "UserPrefsDialog.change_active_light(): Not implemented yet"

    def change_material_brightness(self):
        print "UserPrefsDialog.change_material_brightness(): Not implemented yet"

    def toggle_light(self):
        print "UserPrefsDialog.toggle_light(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UserPrefsDialog",s,c)
