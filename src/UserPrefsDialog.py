# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\UserPrefsDialog.ui'
#
# Created: Tue Mar 7 22:01:25 2006
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
        spacer22_2 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        UserPrefsDialogLayout.addItem(spacer22_2,0,0)

        self.prefs_tab = QTabWidget(self,"prefs_tab")

        self.tab = QWidget(self.prefs_tab,"tab")
        tabLayout = QGridLayout(self.tab,1,1,11,6,"tabLayout")
        spacer57_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        tabLayout.addItem(spacer57_2,0,3)

        layout77 = QHBoxLayout(None,0,6,"layout77")

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
        layout77.addWidget(self.groupBox7_2)

        self.groupBox15 = QGroupBox(self.tab,"groupBox15")
        self.groupBox15.setColumnLayout(0,Qt.Vertical)
        self.groupBox15.layout().setSpacing(6)
        self.groupBox15.layout().setMargin(11)
        groupBox15Layout = QGridLayout(self.groupBox15.layout())
        groupBox15Layout.setAlignment(Qt.AlignTop)

        self.compass_position_btngrp = QButtonGroup(self.groupBox15,"compass_position_btngrp")
        self.compass_position_btngrp.setPaletteBackgroundColor(QColor(178,231,229))
        self.compass_position_btngrp.setFrameShape(QButtonGroup.Box)
        self.compass_position_btngrp.setFrameShadow(QButtonGroup.Plain)
        self.compass_position_btngrp.setLineWidth(1)
        self.compass_position_btngrp.setExclusive(1)
        self.compass_position_btngrp.setRadioButtonExclusive(1)
        self.compass_position_btngrp.setColumnLayout(0,Qt.Vertical)
        self.compass_position_btngrp.layout().setSpacing(6)
        self.compass_position_btngrp.layout().setMargin(11)
        compass_position_btngrpLayout = QGridLayout(self.compass_position_btngrp.layout())
        compass_position_btngrpLayout.setAlignment(Qt.AlignTop)

        self.upper_left_btn = QRadioButton(self.compass_position_btngrp,"upper_left_btn")
        self.compass_position_btngrp.insert( self.upper_left_btn,1)

        compass_position_btngrpLayout.addWidget(self.upper_left_btn,0,0)
        spacer53 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        compass_position_btngrpLayout.addItem(spacer53,1,0)

        self.lower_left_btn = QRadioButton(self.compass_position_btngrp,"lower_left_btn")
        self.compass_position_btngrp.insert( self.lower_left_btn,2)

        compass_position_btngrpLayout.addWidget(self.lower_left_btn,2,0)
        spacer55 = QSpacerItem(30,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        compass_position_btngrpLayout.addItem(spacer55,1,1)

        self.upper_right_btn = QRadioButton(self.compass_position_btngrp,"upper_right_btn")
        self.upper_right_btn.setChecked(1)
        self.compass_position_btngrp.insert( self.upper_right_btn,0)

        compass_position_btngrpLayout.addWidget(self.upper_right_btn,0,2)
        spacer54_2 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        compass_position_btngrpLayout.addItem(spacer54_2,1,2)

        self.lower_right_btn = QRadioButton(self.compass_position_btngrp,"lower_right_btn")
        self.compass_position_btngrp.insert( self.lower_right_btn,3)

        compass_position_btngrpLayout.addWidget(self.lower_right_btn,2,2)

        groupBox15Layout.addWidget(self.compass_position_btngrp,0,0)
        layout77.addWidget(self.groupBox15)

        layout73 = QVBoxLayout(None,0,6,"layout73")

        self.groupBox14 = QGroupBox(self.tab,"groupBox14")
        self.groupBox14.setColumnLayout(0,Qt.Vertical)
        self.groupBox14.layout().setSpacing(6)
        self.groupBox14.layout().setMargin(11)
        groupBox14Layout = QVBoxLayout(self.groupBox14.layout())
        groupBox14Layout.setAlignment(Qt.AlignTop)

        self.watch_min_in_realtime_checkbox = QCheckBox(self.groupBox14,"watch_min_in_realtime_checkbox")
        groupBox14Layout.addWidget(self.watch_min_in_realtime_checkbox)
        layout73.addWidget(self.groupBox14)
        spacer56_2 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout73.addItem(spacer56_2)
        layout77.addLayout(layout73)

        tabLayout.addMultiCellLayout(layout77,0,0,0,2)

        layout129 = QVBoxLayout(None,0,6,"layout129")

        self.groupBox8 = QGroupBox(self.tab,"groupBox8")
        self.groupBox8.setColumnLayout(0,Qt.Vertical)
        self.groupBox8.layout().setSpacing(6)
        self.groupBox8.layout().setMargin(11)
        groupBox8Layout = QGridLayout(self.groupBox8.layout())
        groupBox8Layout.setAlignment(Qt.AlignTop)

        self.animate_views_checkbox = QCheckBox(self.groupBox8,"animate_views_checkbox")
        self.animate_views_checkbox.setChecked(1)

        groupBox8Layout.addWidget(self.animate_views_checkbox,1,0)

        layout128 = QHBoxLayout(None,0,6,"layout128")

        layout127 = QVBoxLayout(None,0,6,"layout127")
        spacer110 = QSpacerItem(40,20,QSizePolicy.Minimum,QSizePolicy.Minimum)
        layout127.addItem(spacer110)

        self.textLabel1_5 = QLabel(self.groupBox8,"textLabel1_5")
        self.textLabel1_5.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.textLabel1_5.sizePolicy().hasHeightForWidth()))
        self.textLabel1_5.setScaledContents(0)
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter)
        layout127.addWidget(self.textLabel1_5)
        layout128.addLayout(layout127)

        layout118 = QVBoxLayout(None,0,6,"layout118")

        layout117 = QHBoxLayout(None,0,6,"layout117")

        self.textLabel2_3 = QLabel(self.groupBox8,"textLabel2_3")
        layout117.addWidget(self.textLabel2_3)
        spacer107 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout117.addItem(spacer107)

        self.textLabel3_4 = QLabel(self.groupBox8,"textLabel3_4")
        layout117.addWidget(self.textLabel3_4)
        layout118.addLayout(layout117)

        self.animation_speed_slider = QSlider(self.groupBox8,"animation_speed_slider")
        self.animation_speed_slider.setMinValue(-300)
        self.animation_speed_slider.setMaxValue(-25)
        self.animation_speed_slider.setOrientation(QSlider.Horizontal)
        layout118.addWidget(self.animation_speed_slider)
        layout128.addLayout(layout118)

        groupBox8Layout.addLayout(layout128,2,0)

        self.high_quality_graphics_checkbox = QCheckBox(self.groupBox8,"high_quality_graphics_checkbox")
        self.high_quality_graphics_checkbox.setChecked(1)

        groupBox8Layout.addWidget(self.high_quality_graphics_checkbox,0,0)
        layout129.addWidget(self.groupBox8)
        spacer109 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout129.addItem(spacer109)

        tabLayout.addLayout(layout129,1,1)
        spacer25 = QSpacerItem(170,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        tabLayout.addItem(spacer25,1,2)

        layout67 = QVBoxLayout(None,0,6,"layout67")

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
        layout67.addWidget(self.default_projection_btngrp)
        spacer53_2 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout67.addItem(spacer53_2)

        tabLayout.addLayout(layout67,1,0)
        self.prefs_tab.insertTab(self.tab,QString.fromLatin1(""))

        self.TabPage = QWidget(self.prefs_tab,"TabPage")
        TabPageLayout = QGridLayout(self.TabPage,1,1,11,6,"TabPageLayout")

        layout101 = QVBoxLayout(None,0,6,"layout101")

        layout100 = QHBoxLayout(None,0,6,"layout100")

        self.textLabel1_7 = QLabel(self.TabPage,"textLabel1_7")
        self.textLabel1_7.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout100.addWidget(self.textLabel1_7)

        self.level_of_detail_combox = QComboBox(0,self.TabPage,"level_of_detail_combox")
        layout100.addWidget(self.level_of_detail_combox)
        spacer54 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout100.addItem(spacer54)
        layout101.addLayout(layout100)
        spacer76 = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout101.addItem(spacer76)

        TabPageLayout.addLayout(layout101,0,1)

        layout104 = QVBoxLayout(None,0,6,"layout104")

        self.atom_colors_grpbox = QGroupBox(self.TabPage,"atom_colors_grpbox")
        self.atom_colors_grpbox.setColumnLayout(0,Qt.Vertical)
        self.atom_colors_grpbox.layout().setSpacing(6)
        self.atom_colors_grpbox.layout().setMargin(11)
        atom_colors_grpboxLayout = QGridLayout(self.atom_colors_grpbox.layout())
        atom_colors_grpboxLayout.setAlignment(Qt.AlignTop)

        layout79 = QHBoxLayout(None,0,6,"layout79")
        spacer56 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout79.addItem(spacer56)

        self.change_element_colors_btn = QPushButton(self.atom_colors_grpbox,"change_element_colors_btn")
        layout79.addWidget(self.change_element_colors_btn)

        atom_colors_grpboxLayout.addLayout(layout79,0,0)

        self.groupBox13 = QGroupBox(self.atom_colors_grpbox,"groupBox13")
        self.groupBox13.setColumnLayout(0,Qt.Vertical)
        self.groupBox13.layout().setSpacing(6)
        self.groupBox13.layout().setMargin(11)
        groupBox13Layout = QVBoxLayout(self.groupBox13.layout())
        groupBox13Layout.setAlignment(Qt.AlignTop)

        layout80 = QGridLayout(None,1,1,0,6,"layout80")

        self.textLabel3_2_3 = QLabel(self.groupBox13,"textLabel3_2_3")
        self.textLabel3_2_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout80.addWidget(self.textLabel3_2_3,0,0)

        self.hotspot_lbl_2 = QLabel(self.groupBox13,"hotspot_lbl_2")
        self.hotspot_lbl_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout80.addWidget(self.hotspot_lbl_2,2,0)

        self.hotspot_lbl = QLabel(self.groupBox13,"hotspot_lbl")
        self.hotspot_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout80.addWidget(self.hotspot_lbl,3,0)

        layout37_2_2_2_2_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2_2_2_2_2")

        self.bondpoint_hilite_color_frame = QFrame(self.groupBox13,"bondpoint_hilite_color_frame")
        self.bondpoint_hilite_color_frame.setMinimumSize(QSize(25,0))
        self.bondpoint_hilite_color_frame.setPaletteBackgroundColor(QColor(255,203,203))
        self.bondpoint_hilite_color_frame.setFrameShape(QFrame.Box)
        self.bondpoint_hilite_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_2_2_2.addWidget(self.bondpoint_hilite_color_frame)

        self.bondpoint_hilite_color_btn = QPushButton(self.groupBox13,"bondpoint_hilite_color_btn")
        layout37_2_2_2_2_2_2_2.addWidget(self.bondpoint_hilite_color_btn)

        layout80.addLayout(layout37_2_2_2_2_2_2_2,2,1)

        layout37_2_2_2_3 = QHBoxLayout(None,0,6,"layout37_2_2_2_3")

        self.atom_hilite_color_frame = QFrame(self.groupBox13,"atom_hilite_color_frame")
        self.atom_hilite_color_frame.setMinimumSize(QSize(25,0))
        self.atom_hilite_color_frame.setPaletteBackgroundColor(QColor(255,255,0))
        self.atom_hilite_color_frame.setFrameShape(QFrame.Box)
        self.atom_hilite_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_3.addWidget(self.atom_hilite_color_frame)

        self.atom_hilite_color_btn = QPushButton(self.groupBox13,"atom_hilite_color_btn")
        layout37_2_2_2_3.addWidget(self.atom_hilite_color_btn)

        layout80.addLayout(layout37_2_2_2_3,0,1)

        layout37_2_2_2_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2_2_2_2")

        self.hotspot_color_frame = QFrame(self.groupBox13,"hotspot_color_frame")
        self.hotspot_color_frame.setMinimumSize(QSize(25,0))
        self.hotspot_color_frame.setPaletteBackgroundColor(QColor(0,255,0))
        self.hotspot_color_frame.setFrameShape(QFrame.Box)
        self.hotspot_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_2_2.addWidget(self.hotspot_color_frame)

        self.hotspot_color_btn = QPushButton(self.groupBox13,"hotspot_color_btn")
        layout37_2_2_2_2_2_2.addWidget(self.hotspot_color_btn)

        layout80.addLayout(layout37_2_2_2_2_2_2,3,1)
        groupBox13Layout.addLayout(layout80)

        layout25_2 = QHBoxLayout(None,0,6,"layout25_2")
        spacer20_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25_2.addItem(spacer20_2)

        self.reset_atom_colors_btn = QPushButton(self.groupBox13,"reset_atom_colors_btn")
        layout25_2.addWidget(self.reset_atom_colors_btn)
        groupBox13Layout.addLayout(layout25_2)

        atom_colors_grpboxLayout.addWidget(self.groupBox13,1,0)
        layout104.addWidget(self.atom_colors_grpbox)

        layout103 = QGridLayout(None,1,1,0,6,"layout103")

        self.textLabel1_3_2 = QLabel(self.TabPage,"textLabel1_3_2")
        self.textLabel1_3_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout103.addWidget(self.textLabel1_3_2,0,0)

        self.textLabel1_3_2_2 = QLabel(self.TabPage,"textLabel1_3_2_2")
        self.textLabel1_3_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout103.addWidget(self.textLabel1_3_2_2,1,0)

        layout67_2 = QHBoxLayout(None,0,6,"layout67_2")

        self.cpk_atom_rad_spinbox = QSpinBox(self.TabPage,"cpk_atom_rad_spinbox")
        self.cpk_atom_rad_spinbox.setMaxValue(125)
        self.cpk_atom_rad_spinbox.setMinValue(50)
        self.cpk_atom_rad_spinbox.setValue(100)
        layout67_2.addWidget(self.cpk_atom_rad_spinbox)

        self.textLabel1_4 = QLabel(self.TabPage,"textLabel1_4")
        layout67_2.addWidget(self.textLabel1_4)
        spacer38 = QSpacerItem(19,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout67_2.addItem(spacer38)

        layout103.addLayout(layout67_2,0,1)

        layout67_2_2 = QHBoxLayout(None,0,6,"layout67_2_2")

        self.cpk_scale_factor_spinbox = QSpinBox(self.TabPage,"cpk_scale_factor_spinbox")
        self.cpk_scale_factor_spinbox.setMaxValue(100)
        self.cpk_scale_factor_spinbox.setMinValue(50)
        self.cpk_scale_factor_spinbox.setValue(100)
        layout67_2_2.addWidget(self.cpk_scale_factor_spinbox)

        self.textLabel1_4_2 = QLabel(self.TabPage,"textLabel1_4_2")
        layout67_2_2.addWidget(self.textLabel1_4_2)
        spacer38_3 = QSpacerItem(19,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout67_2_2.addItem(spacer38_3)

        layout103.addLayout(layout67_2_2,1,1)
        layout104.addLayout(layout103)
        spacer11 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout104.addItem(spacer11)

        TabPageLayout.addLayout(layout104,0,0)
        self.prefs_tab.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.prefs_tab,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")

        layout111 = QVBoxLayout(None,0,6,"layout111")

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
        layout111.addWidget(self.groupBox4)

        layout110 = QHBoxLayout(None,0,6,"layout110")

        layout109 = QVBoxLayout(None,0,6,"layout109")

        self.textLabel1_3 = QLabel(self.TabPage_2,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout109.addWidget(self.textLabel1_3)

        self.textLabel1 = QLabel(self.TabPage_2,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout109.addWidget(self.textLabel1)
        layout110.addLayout(layout109)

        layout106 = QVBoxLayout(None,0,6,"layout106")

        self.cpk_cylinder_rad_spinbox = QSpinBox(self.TabPage_2,"cpk_cylinder_rad_spinbox")
        self.cpk_cylinder_rad_spinbox.setMaxValue(125)
        self.cpk_cylinder_rad_spinbox.setMinValue(50)
        self.cpk_cylinder_rad_spinbox.setValue(100)
        layout106.addWidget(self.cpk_cylinder_rad_spinbox)

        self.bond_line_thickness_spinbox = QSpinBox(self.TabPage_2,"bond_line_thickness_spinbox")
        self.bond_line_thickness_spinbox.setMaxValue(3)
        self.bond_line_thickness_spinbox.setMinValue(1)
        layout106.addWidget(self.bond_line_thickness_spinbox)
        layout110.addLayout(layout106)

        layout108 = QVBoxLayout(None,0,6,"layout108")

        self.textLabel1_2_2 = QLabel(self.TabPage_2,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout108.addWidget(self.textLabel1_2_2)

        self.textLabel1_2 = QLabel(self.TabPage_2,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout108.addWidget(self.textLabel1_2)
        layout110.addLayout(layout108)
        layout111.addLayout(layout110)
        spacer22 = QSpacerItem(20,51,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout111.addItem(spacer22)

        TabPageLayout_2.addLayout(layout111,0,0)

        layout98 = QVBoxLayout(None,0,6,"layout98")

        layout76 = QHBoxLayout(None,0,6,"layout76")

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
        layout76.addWidget(self.high_order_bond_display_btngrp)
        spacer19 = QSpacerItem(72,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout76.addItem(spacer19)
        layout98.addLayout(layout76)

        self.show_bond_labels_checkbox = QCheckBox(self.TabPage_2,"show_bond_labels_checkbox")
        layout98.addWidget(self.show_bond_labels_checkbox)

        self.show_valence_errors_checkbox = QCheckBox(self.TabPage_2,"show_valence_errors_checkbox")
        layout98.addWidget(self.show_valence_errors_checkbox)
        spacer18 = QSpacerItem(20,144,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout98.addItem(spacer18)

        TabPageLayout_2.addLayout(layout98,0,1)
        self.prefs_tab.insertTab(self.TabPage_2,QString.fromLatin1(""))

        self.TabPage_3 = QWidget(self.prefs_tab,"TabPage_3")
        TabPageLayout_3 = QGridLayout(self.TabPage_3,1,1,11,6,"TabPageLayout_3")
        spacer8_3_2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Fixed)
        TabPageLayout_3.addItem(spacer8_3_2,0,0)

        layout69 = QGridLayout(None,1,1,0,6,"layout69")

        layout68 = QGridLayout(None,1,1,0,6,"layout68")

        self.startup_mode_lbl = QLabel(self.TabPage_3,"startup_mode_lbl")
        self.startup_mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout68.addWidget(self.startup_mode_lbl,0,0)

        self.startup_mode_combox = QComboBox(0,self.TabPage_3,"startup_mode_combox")

        layout68.addWidget(self.startup_mode_combox,0,1)

        self.default_mode_lbl = QLabel(self.TabPage_3,"default_mode_lbl")
        self.default_mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout68.addWidget(self.default_mode_lbl,1,0)

        self.default_mode_combox = QComboBox(0,self.TabPage_3,"default_mode_combox")

        layout68.addWidget(self.default_mode_combox,1,1)

        layout69.addLayout(layout68,0,0)
        spacer8_3 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout69.addItem(spacer8_3,2,0)

        self.mode_groupbox = QGroupBox(self.TabPage_3,"mode_groupbox")
        self.mode_groupbox.setColumnLayout(0,Qt.Vertical)
        self.mode_groupbox.layout().setSpacing(6)
        self.mode_groupbox.layout().setMargin(11)
        mode_groupboxLayout = QGridLayout(self.mode_groupbox.layout())
        mode_groupboxLayout.setAlignment(Qt.AlignTop)

        layout66 = QHBoxLayout(None,0,6,"layout66")

        layout65 = QVBoxLayout(None,0,6,"layout65")

        self.mode_lbl = QLabel(self.mode_groupbox,"mode_lbl")
        self.mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout65.addWidget(self.mode_lbl)

        self.display_mode_lbl = QLabel(self.mode_groupbox,"display_mode_lbl")
        self.display_mode_lbl.setEnabled(1)
        self.display_mode_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout65.addWidget(self.display_mode_lbl)
        layout66.addLayout(layout65)

        layout64 = QVBoxLayout(None,0,6,"layout64")

        self.mode_combox = QComboBox(0,self.mode_groupbox,"mode_combox")
        layout64.addWidget(self.mode_combox)

        self.display_mode_combox = QComboBox(0,self.mode_groupbox,"display_mode_combox")
        self.display_mode_combox.setEnabled(1)
        layout64.addWidget(self.display_mode_combox)
        layout66.addLayout(layout64)

        mode_groupboxLayout.addLayout(layout66,0,0)

        self.bg_groupbox = QGroupBox(self.mode_groupbox,"bg_groupbox")
        self.bg_groupbox.setColumnLayout(0,Qt.Vertical)
        self.bg_groupbox.layout().setSpacing(6)
        self.bg_groupbox.layout().setMargin(11)
        bg_groupboxLayout = QGridLayout(self.bg_groupbox.layout())
        bg_groupboxLayout.setAlignment(Qt.AlignTop)

        layout69_2 = QHBoxLayout(None,0,6,"layout69_2")

        layout68_2 = QVBoxLayout(None,0,6,"layout68_2")

        self.fill_type_lbl = QLabel(self.bg_groupbox,"fill_type_lbl")
        self.fill_type_lbl.setEnabled(1)
        self.fill_type_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout68_2.addWidget(self.fill_type_lbl)

        self.bg1_color_lbl = QLabel(self.bg_groupbox,"bg1_color_lbl")
        self.bg1_color_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout68_2.addWidget(self.bg1_color_lbl)
        layout69_2.addLayout(layout68_2)

        layout67_3 = QVBoxLayout(None,0,6,"layout67_3")

        self.fill_type_combox = QComboBox(0,self.bg_groupbox,"fill_type_combox")
        self.fill_type_combox.setEnabled(1)
        layout67_3.addWidget(self.fill_type_combox)

        layout37 = QHBoxLayout(None,0,6,"layout37")

        self.bg1_color_frame = QFrame(self.bg_groupbox,"bg1_color_frame")
        self.bg1_color_frame.setMinimumSize(QSize(25,0))
        self.bg1_color_frame.setPaletteBackgroundColor(QColor(170,255,255))
        self.bg1_color_frame.setFrameShape(QFrame.Box)
        self.bg1_color_frame.setFrameShadow(QFrame.Plain)
        layout37.addWidget(self.bg1_color_frame)

        self.choose_bg1_color_btn = QPushButton(self.bg_groupbox,"choose_bg1_color_btn")
        layout37.addWidget(self.choose_bg1_color_btn)
        layout67_3.addLayout(layout37)
        layout69_2.addLayout(layout67_3)

        bg_groupboxLayout.addMultiCellLayout(layout69_2,0,0,0,1)

        self.restore_bgcolor_btn = QPushButton(self.bg_groupbox,"restore_bgcolor_btn")

        bg_groupboxLayout.addWidget(self.restore_bgcolor_btn,1,1)
        spacer7_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        bg_groupboxLayout.addItem(spacer7_2,1,0)

        mode_groupboxLayout.addWidget(self.bg_groupbox,1,0)

        layout69.addWidget(self.mode_groupbox,1,0)

        TabPageLayout_3.addLayout(layout69,0,0)

        layout67_4 = QVBoxLayout(None,0,6,"layout67_4")

        self.default_display_btngrp = QButtonGroup(self.TabPage_3,"default_display_btngrp")
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
        layout67_4.addWidget(self.default_display_btngrp)

        self.buildmode_groupbox = QGroupBox(self.TabPage_3,"buildmode_groupbox")
        self.buildmode_groupbox.setColumnLayout(0,Qt.Vertical)
        self.buildmode_groupbox.layout().setSpacing(6)
        self.buildmode_groupbox.layout().setMargin(11)
        buildmode_groupboxLayout = QGridLayout(self.buildmode_groupbox.layout())
        buildmode_groupboxLayout.setAlignment(Qt.AlignTop)

        self.autobond_checkbox = QCheckBox(self.buildmode_groupbox,"autobond_checkbox")

        buildmode_groupboxLayout.addWidget(self.autobond_checkbox,0,0)

        self.water_checkbox = QCheckBox(self.buildmode_groupbox,"water_checkbox")

        buildmode_groupboxLayout.addWidget(self.water_checkbox,0,1)

        self.buildmode_select_atoms_checkbox = QCheckBox(self.buildmode_groupbox,"buildmode_select_atoms_checkbox")

        buildmode_groupboxLayout.addMultiCellWidget(self.buildmode_select_atoms_checkbox,2,2,0,1)

        self.buildmode_highlighting_checkbox = QCheckBox(self.buildmode_groupbox,"buildmode_highlighting_checkbox")

        buildmode_groupboxLayout.addMultiCellWidget(self.buildmode_highlighting_checkbox,1,1,0,1)
        layout67_4.addWidget(self.buildmode_groupbox)

        self.groupBox16 = QGroupBox(self.TabPage_3,"groupBox16")
        self.groupBox16.setColumnLayout(0,Qt.Vertical)
        self.groupBox16.layout().setSpacing(6)
        self.groupBox16.layout().setMargin(11)
        groupBox16Layout = QGridLayout(self.groupBox16.layout())
        groupBox16Layout.setAlignment(Qt.AlignTop)

        self.selatomsmode_highlighting_checkbox = QCheckBox(self.groupBox16,"selatomsmode_highlighting_checkbox")

        groupBox16Layout.addWidget(self.selatomsmode_highlighting_checkbox,0,0)
        layout67_4.addWidget(self.groupBox16)

        TabPageLayout_3.addLayout(layout67_4,0,1)
        spacer8_4 = QSpacerItem(60,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_3.addItem(spacer8_4,0,2)
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

        layout69_3 = QHBoxLayout(None,0,6,"layout69_3")

        self.light_checkbox = QCheckBox(self.groupBox8_2,"light_checkbox")
        layout69_3.addWidget(self.light_checkbox)
        spacer45 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout69_3.addItem(spacer45)
        layout559.addLayout(layout69_3)

        layout82 = QHBoxLayout(None,0,6,"layout82")

        layout37_2_2_2_4 = QHBoxLayout(None,0,6,"layout37_2_2_2_4")

        self.light_color_frame = QFrame(self.groupBox8_2,"light_color_frame")
        self.light_color_frame.setMinimumSize(QSize(25,0))
        self.light_color_frame.setPaletteBackgroundColor(QColor(255,255,255))
        self.light_color_frame.setFrameShape(QFrame.Box)
        self.light_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_4.addWidget(self.light_color_frame)

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

        layout63 = QHBoxLayout(None,0,6,"layout63")

        self.light_x_linedit = QLineEdit(self.groupBox8_2,"light_x_linedit")
        layout63.addWidget(self.light_x_linedit)
        spacer42 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout63.addItem(spacer42)
        layout559.addLayout(layout63)

        layout62 = QHBoxLayout(None,0,6,"layout62")

        self.light_y_linedit = QLineEdit(self.groupBox8_2,"light_y_linedit")
        layout62.addWidget(self.light_y_linedit)
        spacer43 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout62.addItem(spacer43)
        layout559.addLayout(layout62)

        layout61_2 = QHBoxLayout(None,0,6,"layout61_2")

        self.light_z_linedit = QLineEdit(self.groupBox8_2,"light_z_linedit")
        self.light_z_linedit.setMaxLength(32767)
        layout61_2.addWidget(self.light_z_linedit)
        spacer44 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout61_2.addItem(spacer44)
        layout559.addLayout(layout61_2)

        groupBox8_2Layout.addLayout(layout559,0,1)

        TabPageLayout_4.addMultiCellWidget(self.groupBox8_2,0,2,0,0)

        layout505 = QHBoxLayout(None,0,6,"layout505")
        spacer57 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout505.addItem(spacer57)

        self.lighting_restore_defaults_btn = QPushButton(self.TabPage_4,"lighting_restore_defaults_btn")
        layout505.addWidget(self.lighting_restore_defaults_btn)

        TabPageLayout_4.addLayout(layout505,2,1)
        spacer345 = QSpacerItem(20,30,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_4.addItem(spacer345,1,1)

        self.groupBox9_2 = QGroupBox(self.TabPage_4,"groupBox9_2")
        self.groupBox9_2.setEnabled(1)
        self.groupBox9_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox9_2.layout().setSpacing(6)
        self.groupBox9_2.layout().setMargin(11)
        groupBox9_2Layout = QGridLayout(self.groupBox9_2.layout())
        groupBox9_2Layout.setAlignment(Qt.AlignTop)

        layout49 = QVBoxLayout(None,0,6,"layout49")

        self.ms_on_label = QLabel(self.groupBox9_2,"ms_on_label")
        self.ms_on_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout49.addWidget(self.ms_on_label)
        spacer38_2 = QSpacerItem(70,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout49.addItem(spacer38_2)

        self.ms_finish_label = QLabel(self.groupBox9_2,"ms_finish_label")
        self.ms_finish_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout49.addWidget(self.ms_finish_label)
        spacer40_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout49.addItem(spacer40_2)

        self.ms_shininess_label = QLabel(self.groupBox9_2,"ms_shininess_label")
        self.ms_shininess_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout49.addWidget(self.ms_shininess_label)
        spacer40 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout49.addItem(spacer40)

        self.ms_brightness__label = QLabel(self.groupBox9_2,"ms_brightness__label")
        self.ms_brightness__label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout49.addWidget(self.ms_brightness__label)

        groupBox9_2Layout.addLayout(layout49,0,0)

        layout50 = QVBoxLayout(None,0,6,"layout50")

        self.ms_on_checkbox = QCheckBox(self.groupBox9_2,"ms_on_checkbox")
        layout50.addWidget(self.ms_on_checkbox)
        spacer39 = QSpacerItem(46,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout50.addItem(spacer39)

        self.ms_finish_linedit = QLineEdit(self.groupBox9_2,"ms_finish_linedit")
        self.ms_finish_linedit.setMaximumSize(QSize(50,32767))
        self.ms_finish_linedit.setMaxLength(5)
        self.ms_finish_linedit.setReadOnly(1)
        layout50.addWidget(self.ms_finish_linedit)
        spacer41_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout50.addItem(spacer41_2)

        self.ms_shininess_linedit = QLineEdit(self.groupBox9_2,"ms_shininess_linedit")
        self.ms_shininess_linedit.setMaximumSize(QSize(50,32767))
        self.ms_shininess_linedit.setMaxLength(5)
        self.ms_shininess_linedit.setReadOnly(1)
        layout50.addWidget(self.ms_shininess_linedit)
        spacer41 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout50.addItem(spacer41)

        self.ms_brightness_linedit = QLineEdit(self.groupBox9_2,"ms_brightness_linedit")
        self.ms_brightness_linedit.setMaximumSize(QSize(50,32767))
        self.ms_brightness_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.ms_brightness_linedit.setFrameShadow(QLineEdit.Sunken)
        self.ms_brightness_linedit.setMaxLength(5)
        self.ms_brightness_linedit.setReadOnly(1)
        layout50.addWidget(self.ms_brightness_linedit)

        groupBox9_2Layout.addLayout(layout50,0,1)

        layout54 = QVBoxLayout(None,0,6,"layout54")
        spacer36 = QSpacerItem(100,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout54.addItem(spacer36)

        layout46 = QHBoxLayout(None,0,6,"layout46")

        self.textLabel1_6 = QLabel(self.groupBox9_2,"textLabel1_6")
        layout46.addWidget(self.textLabel1_6)
        spacer37 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46.addItem(spacer37)

        self.textLabel2_4 = QLabel(self.groupBox9_2,"textLabel2_4")
        layout46.addWidget(self.textLabel2_4)
        layout54.addLayout(layout46)

        self.ms_finish_slider = QSlider(self.groupBox9_2,"ms_finish_slider")
        self.ms_finish_slider.setMinValue(0)
        self.ms_finish_slider.setMaxValue(100)
        self.ms_finish_slider.setValue(50)
        self.ms_finish_slider.setOrientation(QSlider.Horizontal)
        self.ms_finish_slider.setTickmarks(QSlider.NoMarks)
        self.ms_finish_slider.setTickInterval(5)
        layout54.addWidget(self.ms_finish_slider)

        layout46_2 = QHBoxLayout(None,0,6,"layout46_2")

        self.textLabel1_6_2 = QLabel(self.groupBox9_2,"textLabel1_6_2")
        layout46_2.addWidget(self.textLabel1_6_2)
        spacer37_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_2.addItem(spacer37_2)

        self.textLabel2_4_2 = QLabel(self.groupBox9_2,"textLabel2_4_2")
        layout46_2.addWidget(self.textLabel2_4_2)
        layout54.addLayout(layout46_2)

        self.ms_shininess_slider = QSlider(self.groupBox9_2,"ms_shininess_slider")
        self.ms_shininess_slider.setMinValue(15)
        self.ms_shininess_slider.setMaxValue(60)
        self.ms_shininess_slider.setValue(15)
        self.ms_shininess_slider.setOrientation(QSlider.Horizontal)
        self.ms_shininess_slider.setTickmarks(QSlider.NoMarks)
        self.ms_shininess_slider.setTickInterval(5)
        layout54.addWidget(self.ms_shininess_slider)

        layout46_3 = QHBoxLayout(None,0,6,"layout46_3")

        self.textLabel1_6_3 = QLabel(self.groupBox9_2,"textLabel1_6_3")
        layout46_3.addWidget(self.textLabel1_6_3)
        spacer37_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_3.addItem(spacer37_3)

        self.textLabel2_4_3 = QLabel(self.groupBox9_2,"textLabel2_4_3")
        layout46_3.addWidget(self.textLabel2_4_3)
        layout54.addLayout(layout46_3)

        self.ms_brightness_slider = QSlider(self.groupBox9_2,"ms_brightness_slider")
        self.ms_brightness_slider.setMinValue(0)
        self.ms_brightness_slider.setMaxValue(100)
        self.ms_brightness_slider.setValue(50)
        self.ms_brightness_slider.setOrientation(QSlider.Horizontal)
        self.ms_brightness_slider.setTickmarks(QSlider.NoMarks)
        self.ms_brightness_slider.setTickInterval(5)
        layout54.addWidget(self.ms_brightness_slider)

        groupBox9_2Layout.addLayout(layout54,0,2)

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

        layout80_2 = QGridLayout(None,1,1,0,6,"layout80_2")

        self.nanohive_path_linedit = QLineEdit(self.file_locations_grp,"nanohive_path_linedit")
        self.nanohive_path_linedit.setEnabled(0)
        self.nanohive_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.nanohive_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.nanohive_path_linedit.setReadOnly(1)

        layout80_2.addWidget(self.nanohive_path_linedit,1,0)

        self.gamess_path_linedit = QLineEdit(self.file_locations_grp,"gamess_path_linedit")
        self.gamess_path_linedit.setEnabled(0)
        self.gamess_path_linedit.setMaximumSize(QSize(32767,32767))
        self.gamess_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.gamess_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.gamess_path_linedit.setMaxLength(32767)
        self.gamess_path_linedit.setReadOnly(1)

        layout80_2.addWidget(self.gamess_path_linedit,0,0)

        self.nanohive_choose_btn = QPushButton(self.file_locations_grp,"nanohive_choose_btn")
        self.nanohive_choose_btn.setEnabled(0)

        layout80_2.addWidget(self.nanohive_choose_btn,1,1)

        self.gamess_choose_btn = QPushButton(self.file_locations_grp,"gamess_choose_btn")
        self.gamess_choose_btn.setEnabled(0)

        layout80_2.addWidget(self.gamess_choose_btn,0,1)

        file_locations_grpLayout.addLayout(layout80_2,0,1)

        layout63_2 = QGridLayout(None,1,1,0,6,"layout63_2")

        self.gamess_lbl = QLabel(self.file_locations_grp,"gamess_lbl")
        self.gamess_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.gamess_lbl.sizePolicy().hasHeightForWidth()))
        self.gamess_lbl.setMinimumSize(QSize(60,0))
        self.gamess_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout63_2.addWidget(self.gamess_lbl,0,1)

        self.nanohive_lbl = QLabel(self.file_locations_grp,"nanohive_lbl")
        self.nanohive_lbl.setEnabled(1)
        self.nanohive_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.nanohive_lbl.sizePolicy().hasHeightForWidth()))
        self.nanohive_lbl.setMinimumSize(QSize(60,0))
        self.nanohive_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout63_2.addWidget(self.nanohive_lbl,1,1)

        self.gamess_checkbox = QCheckBox(self.file_locations_grp,"gamess_checkbox")

        layout63_2.addWidget(self.gamess_checkbox,0,0)

        self.nanohive_checkbox = QCheckBox(self.file_locations_grp,"nanohive_checkbox")
        self.nanohive_checkbox.setEnabled(1)

        layout63_2.addWidget(self.nanohive_checkbox,1,0)

        file_locations_grpLayout.addLayout(layout63_2,0,0)

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
        spacer11_3 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_7.addItem(spacer11_3,2,0)

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

        TabPageLayout_7.addLayout(layout15,1,0)

        layout51 = QHBoxLayout(None,0,6,"layout51")

        self.groupBox10 = QGroupBox(self.TabPage_7,"groupBox10")
        self.groupBox10.setColumnLayout(0,Qt.Vertical)
        self.groupBox10.layout().setSpacing(6)
        self.groupBox10.layout().setMargin(11)
        groupBox10Layout = QGridLayout(self.groupBox10.layout())
        groupBox10Layout.setAlignment(Qt.AlignTop)

        self.always_save_win_pos_and_size_checkbox = QCheckBox(self.groupBox10,"always_save_win_pos_and_size_checkbox")

        groupBox10Layout.addMultiCellWidget(self.always_save_win_pos_and_size_checkbox,0,0,0,1)

        self.save_current_btn = QPushButton(self.groupBox10,"save_current_btn")

        groupBox10Layout.addWidget(self.save_current_btn,1,0)
        spacer46 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox10Layout.addItem(spacer46,1,1)
        layout51.addWidget(self.groupBox10)
        spacer47 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout51.addItem(spacer47)

        TabPageLayout_7.addLayout(layout51,0,0)
        self.prefs_tab.insertTab(self.TabPage_7,QString.fromLatin1(""))

        UserPrefsDialogLayout.addWidget(self.prefs_tab,0,0)

        self.languageChange()

        self.resize(QSize(565,424).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.always_save_win_pos_and_size_checkbox,SIGNAL("toggled(bool)"),self.change_always_save_win_pos_and_size)
        self.connect(self.animate_views_checkbox,SIGNAL("stateChanged(int)"),self.change_animate_standard_views)
        self.connect(self.animation_speed_slider,SIGNAL("sliderReleased()"),self.change_view_animation_speed)
        self.connect(self.atom_hilite_color_btn,SIGNAL("clicked()"),self.change_atom_hilite_color)
        self.connect(self.autobond_checkbox,SIGNAL("clicked()"),self.set_buildmode_autobond)
        self.connect(self.bond_cpk_color_btn,SIGNAL("clicked()"),self.change_bond_cpk_color)
        self.connect(self.bond_hilite_color_btn,SIGNAL("clicked()"),self.change_bond_hilite_color)
        self.connect(self.bond_line_thickness_spinbox,SIGNAL("valueChanged(int)"),self.change_bond_line_thickness)
        self.connect(self.bond_stretch_color_btn,SIGNAL("clicked()"),self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn,SIGNAL("clicked()"),self.change_bond_vane_color)
        self.connect(self.bondpoint_hilite_color_btn,SIGNAL("clicked()"),self.change_bondpoint_hilite_color)
        self.connect(self.buildmode_highlighting_checkbox,SIGNAL("clicked()"),self.set_buildmode_highlighting)
        self.connect(self.caption_fullpath_checkbox,SIGNAL("stateChanged(int)"),self.set_caption_fullpath)
        self.connect(self.change_element_colors_btn,SIGNAL("clicked()"),self.change_element_colors)
        self.connect(self.choose_bg1_color_btn,SIGNAL("clicked()"),self.change_bg1_color)
        self.connect(self.compass_position_btngrp,SIGNAL("clicked(int)"),self.set_compass_position)
        self.connect(self.cpk_atom_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_cpk_atom_radius)
        self.connect(self.cpk_cylinder_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_cpk_cylinder_radius)
        self.connect(self.default_display_btngrp,SIGNAL("clicked(int)"),self.set_default_display_mode)
        self.connect(self.default_mode_combox,SIGNAL("activated(int)"),self.change_default_mode)
        self.connect(self.display_compass_checkbox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.display_mode_combox,SIGNAL("activated(int)"),self.change_display_mode)
        self.connect(self.display_origin_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_origin_axis)
        self.connect(self.display_pov_axis_checkbox,SIGNAL("stateChanged(int)"),self.display_pov_axis)
        self.connect(self.fill_type_combox,SIGNAL("activated(const QString&)"),self.fill_type_changed)
        self.connect(self.gamess_checkbox,SIGNAL("toggled(bool)"),self.enable_gamess)
        self.connect(self.gamess_choose_btn,SIGNAL("clicked()"),self.set_gamess_path)
        self.connect(self.high_order_bond_display_btngrp,SIGNAL("clicked(int)"),self.change_high_order_bond_display)
        self.connect(self.high_quality_graphics_checkbox,SIGNAL("toggled(bool)"),self.change_high_quality_graphics)
        self.connect(self.history_height_spinbox,SIGNAL("valueChanged(int)"),self.set_history_height)
        self.connect(self.hotspot_color_btn,SIGNAL("clicked()"),self.change_hotspot_color)
        self.connect(self.level_of_detail_combox,SIGNAL("activated(int)"),self.change_level_of_detail)
        self.connect(self.light_ambient_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_ambient_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_checkbox,SIGNAL("toggled(bool)"),self.toggle_light)
        self.connect(self.light_color_btn,SIGNAL("clicked()"),self.change_light_color)
        self.connect(self.light_combobox,SIGNAL("activated(int)"),self.change_active_light)
        self.connect(self.light_diffuse_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_diffuse_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("valueChanged(int)"),self.change_lighting)
        self.connect(self.light_specularity_slider,SIGNAL("sliderReleased()"),self.save_lighting)
        self.connect(self.light_x_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.light_y_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.light_z_linedit,SIGNAL("returnPressed()"),self.save_lighting)
        self.connect(self.lighting_restore_defaults_btn,SIGNAL("clicked()"),self.restore_default_lighting)
        self.connect(self.mode_combox,SIGNAL("activated(int)"),self.mode_changed)
        self.connect(self.ms_brightness_slider,SIGNAL("sliderReleased()"),self.change_material_brightness_stop)
        self.connect(self.ms_brightness_slider,SIGNAL("sliderPressed()"),self.change_material_brightness_start)
        self.connect(self.ms_brightness_slider,SIGNAL("valueChanged(int)"),self.change_material_brightness)
        self.connect(self.ms_finish_slider,SIGNAL("sliderReleased()"),self.change_material_finish_stop)
        self.connect(self.ms_finish_slider,SIGNAL("sliderPressed()"),self.change_material_finish_start)
        self.connect(self.ms_finish_slider,SIGNAL("valueChanged(int)"),self.change_material_finish)
        self.connect(self.ms_on_checkbox,SIGNAL("toggled(bool)"),self.toggle_material_specularity)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderPressed()"),self.change_material_shininess_start)
        self.connect(self.ms_shininess_slider,SIGNAL("valueChanged(int)"),self.change_material_shininess)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderReleased()"),self.change_material_shininess_stop)
        self.connect(self.nanohive_checkbox,SIGNAL("toggled(bool)"),self.enable_nanohive)
        self.connect(self.nanohive_choose_btn,SIGNAL("clicked()"),self.set_nanohive_path)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.prefs_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.reset_atom_colors_btn,SIGNAL("clicked()"),self.reset_atom_colors)
        self.connect(self.reset_bond_colors_btn,SIGNAL("clicked()"),self.reset_bond_colors)
        self.connect(self.restore_bgcolor_btn,SIGNAL("clicked()"),self.restore_default_bgcolor)
        self.connect(self.save_current_btn,SIGNAL("clicked()"),self.save_current_win_pos_and_size)
        self.connect(self.show_bond_labels_checkbox,SIGNAL("toggled(bool)"),self.change_bond_labels)
        self.connect(self.show_valence_errors_checkbox,SIGNAL("toggled(bool)"),self.change_show_valence_errors)
        self.connect(self.startup_mode_combox,SIGNAL("activated(const QString&)"),self.change_startup_mode)
        self.connect(self.watch_min_in_realtime_checkbox,SIGNAL("clicked()"),self.set_realtime_minimization)
        self.connect(self.water_checkbox,SIGNAL("clicked()"),self.set_buildmode_water)
        self.connect(self.selatomsmode_highlighting_checkbox,SIGNAL("clicked()"),self.set_selatomsmode_highlighting)
        self.connect(self.default_projection_btngrp,SIGNAL("clicked(int)"),self.set_default_projection)
        self.connect(self.buildmode_select_atoms_checkbox,SIGNAL("clicked()"),self.set_buildmode_select_atoms_of_deposited_obj)
        self.connect(self.cpk_scale_factor_spinbox,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)

        self.setTabOrder(self.prefs_tab,self.display_compass_checkbox)
        self.setTabOrder(self.display_compass_checkbox,self.display_origin_axis_checkbox)
        self.setTabOrder(self.display_origin_axis_checkbox,self.display_pov_axis_checkbox)
        self.setTabOrder(self.display_pov_axis_checkbox,self.upper_right_btn)
        self.setTabOrder(self.upper_right_btn,self.radioButton12)
        self.setTabOrder(self.radioButton12,self.animate_views_checkbox)
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
        self.setTabOrder(self.light_z_linedit,self.lighting_restore_defaults_btn)
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
        self.groupBox15.setTitle(self.__tr("Compass Position"))
        self.compass_position_btngrp.setTitle(QString.null)
        self.upper_left_btn.setText(QString.null)
        self.lower_left_btn.setText(QString.null)
        self.upper_right_btn.setText(QString.null)
        self.lower_right_btn.setText(QString.null)
        self.groupBox14.setTitle(self.__tr("Minimization"))
        self.watch_min_in_realtime_checkbox.setText(self.__tr("Watch In Realtime"))
        self.groupBox8.setTitle(self.__tr("View Animation"))
        self.animate_views_checkbox.setText(self.__tr("Animate between views"))
        self.textLabel1_5.setText(self.__tr("Speed :"))
        self.textLabel2_3.setText(self.__tr("Slow"))
        self.textLabel3_4.setText(self.__tr("Fast"))
        self.high_quality_graphics_checkbox.setText(self.__tr("High quality graphics"))
        self.default_projection_btngrp.setTitle(self.__tr("Default Projection"))
        self.radioButton12.setText(self.__tr("Perspective"))
        self.radioButton13.setText(self.__tr("Orthographic"))
        self.prefs_tab.changeTab(self.tab,self.__tr("General"))
        self.textLabel1_7.setText(self.__tr("Level of Detail :"))
        self.level_of_detail_combox.clear()
        self.level_of_detail_combox.insertItem(self.__tr("Low"))
        self.level_of_detail_combox.insertItem(self.__tr("Medium"))
        self.level_of_detail_combox.insertItem(self.__tr("High"))
        self.level_of_detail_combox.insertItem(self.__tr("Variable"))
        self.level_of_detail_combox.setCurrentItem(2)
        self.atom_colors_grpbox.setTitle(self.__tr("Colors"))
        self.change_element_colors_btn.setText(self.__tr("Change Element Colors..."))
        self.groupBox13.setTitle(QString.null)
        self.textLabel3_2_3.setText(self.__tr("Atom Highlighting :"))
        self.hotspot_lbl_2.setText(self.__tr("Bondpoint Highlighting :"))
        self.hotspot_lbl.setText(self.__tr("Bondpoint Hotspot  :"))
        self.bondpoint_hilite_color_btn.setText(self.__tr("Choose..."))
        self.atom_hilite_color_btn.setText(self.__tr("Choose..."))
        self.hotspot_color_btn.setText(self.__tr("Choose..."))
        self.reset_atom_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.textLabel1_3_2.setText(self.__tr("Ball and Stick Atom Scale Factor :"))
        self.textLabel1_3_2_2.setText(self.__tr("CPK Scale Factor :"))
        self.textLabel1_4.setText(self.__tr("%"))
        self.textLabel1_4_2.setText(self.__tr("%"))
        self.prefs_tab.changeTab(self.TabPage,self.__tr("Atoms"))
        self.groupBox4.setTitle(self.__tr("Colors"))
        self.bond_hilite_color_btn.setText(self.__tr("Choose..."))
        self.bond_cpk_color_btn.setText(self.__tr("Choose..."))
        self.bond_vane_color_btn.setText(self.__tr("Choose..."))
        self.textLabel3_2_2.setText(self.__tr("Bond Stretch :"))
        self.textLabel3_2.setText(self.__tr("Bond Highlighting :"))
        self.textLabel3_3.setText(self.__tr("Vane/Ribbon :"))
        self.bond_stretch_color_btn.setText(self.__tr("Choose..."))
        self.textLabel3.setText(self.__tr("CPK Cylinder :"))
        self.reset_bond_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.textLabel1_3.setText(self.__tr("Ball and Stick Cylinder Scale Factor :"))
        self.textLabel1.setText(self.__tr("Bond Line Thickness :"))
        QToolTip.add(self.textLabel1,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.textLabel1,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QToolTip.add(self.bond_line_thickness_spinbox,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        QWhatsThis.add(self.bond_line_thickness_spinbox,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.textLabel1_2_2.setText(self.__tr("%"))
        self.textLabel1_2.setText(self.__tr("pixels"))
        self.high_order_bond_display_btngrp.setTitle(self.__tr("High Order Bonds"))
        self.radioButton11.setText(self.__tr("Multiple Cylinders"))
        self.radioButton11_2.setText(self.__tr("Vanes"))
        self.radioButton11_2_2.setText(self.__tr("Ribbons"))
        self.show_bond_labels_checkbox.setText(self.__tr("Show Bond Type Letters"))
        self.show_valence_errors_checkbox.setText(self.__tr("Show Valence Errors"))
        self.prefs_tab.changeTab(self.TabPage_2,self.__tr("Bonds"))
        self.startup_mode_lbl.setText(self.__tr("Startup Mode :"))
        self.startup_mode_combox.clear()
        self.startup_mode_combox.insertItem(self.__tr("Default Mode"))
        self.startup_mode_combox.insertItem(self.__tr("Build"))
        self.default_mode_lbl.setText(self.__tr("Default Mode :"))
        self.default_mode_combox.clear()
        self.default_mode_combox.insertItem(self.__tr("Select Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Select Atoms"))
        self.default_mode_combox.insertItem(self.__tr("Move Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Build"))
        self.mode_groupbox.setTitle(self.__tr("Mode Settings"))
        self.mode_lbl.setText(self.__tr("Mode :"))
        self.display_mode_lbl.setText(self.__tr("Display Mode :"))
        self.mode_combox.clear()
        self.mode_combox.insertItem(self.__tr("Select Chunks"))
        self.mode_combox.insertItem(self.__tr("Select Atoms"))
        self.mode_combox.insertItem(self.__tr("Move Chunks"))
        self.mode_combox.insertItem(self.__tr("Build"))
        self.mode_combox.insertItem(self.__tr("Cookie Cutter"))
        self.mode_combox.insertItem(self.__tr("Extrude"))
        self.mode_combox.insertItem(self.__tr("Fuse Chunks"))
        self.mode_combox.insertItem(self.__tr("Movie Player"))
        self.display_mode_combox.clear()
        self.display_mode_combox.insertItem(self.__tr("Default"))
        self.display_mode_combox.insertItem(self.__tr("Invisible"))
        self.display_mode_combox.insertItem(self.__tr("CPK"))
        self.display_mode_combox.insertItem(self.__tr("Lines"))
        self.display_mode_combox.insertItem(self.__tr("Ball and Stick"))
        self.display_mode_combox.insertItem(self.__tr("Tubes"))
        self.bg_groupbox.setTitle(self.__tr("Background Color"))
        self.fill_type_lbl.setText(self.__tr("Fill Type :"))
        self.bg1_color_lbl.setText(self.__tr("Color :"))
        self.fill_type_combox.clear()
        self.fill_type_combox.insertItem(self.__tr("Solid"))
        self.fill_type_combox.insertItem(self.__tr("Blue Sky"))
        self.choose_bg1_color_btn.setText(self.__tr("Choose..."))
        self.restore_bgcolor_btn.setText(self.__tr("Restore Default Color"))
        self.default_display_btngrp.setTitle(self.__tr("Default Display Mode"))
        self.vwd_rbtn.setText(self.__tr("CPK"))
        self.cpk_rbtn.setText(self.__tr("Ball and Stick"))
        self.lines_rbtn.setText(self.__tr("Lines"))
        self.tubes_rbtn.setText(self.__tr("Tubes"))
        self.buildmode_groupbox.setTitle(self.__tr("Build Mode Defaults"))
        self.autobond_checkbox.setText(self.__tr("Autobond"))
        self.water_checkbox.setText(self.__tr("Water"))
        self.buildmode_select_atoms_checkbox.setText(self.__tr("Select Atoms of Deposited Object"))
        self.buildmode_highlighting_checkbox.setText(self.__tr("Highligting"))
        self.groupBox16.setTitle(self.__tr("Select Atoms Mode Defaults"))
        self.selatomsmode_highlighting_checkbox.setText(self.__tr("Highligting"))
        self.prefs_tab.changeTab(self.TabPage_3,self.__tr("Modes"))
        self.groupBox8_2.setTitle(self.__tr("Directional Light Properties"))
        self.light_label.setText(self.__tr("Light :"))
        self.on_label.setText(self.__tr("On :"))
        self.color_label.setText(self.__tr("Color :"))
        self.ambient_label.setText(self.__tr("Ambient :"))
        self.diffuse_label.setText(self.__tr("Diffuse :"))
        self.specularity_label.setText(self.__tr("Specular :"))
        self.x_label.setText(self.__tr("X :"))
        self.y_label.setText(self.__tr("Y :"))
        self.z_label.setText(self.__tr("Z :"))
        self.light_combobox.clear()
        self.light_combobox.insertItem(self.__tr("1 (On)"))
        self.light_combobox.insertItem(self.__tr("2 (On)"))
        self.light_combobox.insertItem(self.__tr("3 (Off)"))
        self.light_checkbox.setText(QString.null)
        self.light_color_btn.setText(self.__tr("Choose..."))
        self.lighting_restore_defaults_btn.setText(self.__tr("Restore Defaults"))
        self.groupBox9_2.setTitle(self.__tr("Material Specular Properties"))
        self.ms_on_label.setText(self.__tr("On :"))
        self.ms_finish_label.setText(self.__tr("Finish :"))
        self.ms_shininess_label.setText(self.__tr("Shininess :"))
        self.ms_brightness__label.setText(self.__tr("Brightness :"))
        self.ms_on_checkbox.setText(QString.null)
        self.textLabel1_6.setText(self.__tr("Metal"))
        self.textLabel2_4.setText(self.__tr("Plastic"))
        self.textLabel1_6_2.setText(self.__tr("Flat"))
        self.textLabel2_4_2.setText(self.__tr("Glossy"))
        self.textLabel1_6_3.setText(self.__tr("Low"))
        self.textLabel2_4_3.setText(self.__tr("High"))
        self.prefs_tab.changeTab(self.TabPage_4,self.__tr("Lighting"))
        self.file_locations_grp.setTitle(self.__tr("Location of Executables"))
        self.nanohive_path_linedit.setText(QString.null)
        self.gamess_path_linedit.setText(QString.null)
        QToolTip.add(self.gamess_path_linedit,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        QWhatsThis.add(self.gamess_path_linedit,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.nanohive_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_lbl.setText(self.__tr("GAMESS :"))
        QToolTip.add(self.gamess_lbl,self.__tr("Enable GAMESS."))
        QWhatsThis.add(self.gamess_lbl,self.__tr("Enable GAMESS."))
        self.nanohive_lbl.setText(self.__tr("Nano-Hive :"))
        QToolTip.add(self.nanohive_lbl,self.__tr("Enable Nano-Hive."))
        QWhatsThis.add(self.nanohive_lbl,self.__tr("Enable Nano-Hive."))
        self.gamess_checkbox.setText(QString.null)
        QToolTip.add(self.gamess_checkbox,self.__tr("Enable GAMESS."))
        QWhatsThis.add(self.gamess_checkbox,self.__tr("Enable GAMESS."))
        self.nanohive_checkbox.setText(QString.null)
        QToolTip.add(self.nanohive_checkbox,self.__tr("Enable Nano-Hive."))
        QWhatsThis.add(self.nanohive_checkbox,self.__tr("Enable Nano-Hive."))
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
        self.groupBox10.setTitle(self.__tr("Window Position and Size"))
        self.always_save_win_pos_and_size_checkbox.setText(self.__tr("Always save window position and size"))
        self.save_current_btn.setText(self.__tr("Save Current"))
        self.prefs_tab.changeTab(self.TabPage_7,self.__tr("Window"))


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

    def change_light_color(self):
        print "UserPrefsDialog.change_light_color(): Not implemented yet"

    def change_material_finish_start(self):
        print "UserPrefsDialog.change_material_finish_start(): Not implemented yet"

    def change_material_finish_stop(self):
        print "UserPrefsDialog.change_material_finish_stop(): Not implemented yet"

    def change_material_shininess_start(self):
        print "UserPrefsDialog.change_material_shininess_start(): Not implemented yet"

    def change_material_shininess_stop(self):
        print "UserPrefsDialog.change_material_shininess_stop(): Not implemented yet"

    def change_material_brightness_start(self):
        print "UserPrefsDialog.change_material_brightness_start(): Not implemented yet"

    def change_material_brightness_stop(self):
        print "UserPrefsDialog.change_material_brightness_stop(): Not implemented yet"

    def change_high_quality_graphics(self):
        print "UserPrefsDialog.change_high_quality_graphics(): Not implemented yet"

    def change_always_save_win_pos_and_size(self):
        print "UserPrefsDialog.change_always_save_win_pos_and_size(): Not implemented yet"

    def save_current_win_pos_and_size(self):
        print "UserPrefsDialog.save_current_win_pos_and_size(): Not implemented yet"

    def change_view_animation_speed(self):
        print "UserPrefsDialog.change_view_animation_speed(): Not implemented yet"

    def set_buildmode_autobond(self):
        print "UserPrefsDialog.set_buildmode_autobond(): Not implemented yet"

    def set_buildmode_water(self):
        print "UserPrefsDialog.set_buildmode_water(): Not implemented yet"

    def set_buildmode_highlighting(self):
        print "UserPrefsDialog.set_buildmode_highlighting(): Not implemented yet"

    def change_element_colors(self):
        print "UserPrefsDialog.change_element_colors(): Not implemented yet"

    def change_bondpoint_hilite_color(self):
        print "UserPrefsDialog.change_bondpoint_hilite_color(): Not implemented yet"

    def change_level_of_detail(self):
        print "UserPrefsDialog.change_level_of_detail(): Not implemented yet"

    def change_display_mode(self):
        print "UserPrefsDialog.change_display_mode(): Not implemented yet"

    def set_realtime_minimization(self):
        print "UserPrefsDialog.set_realtime_minimization(): Not implemented yet"

    def set_selatomsmode_highlighting(self):
        print "UserPrefsDialog.set_selatomsmode_highlighting(): Not implemented yet"

    def set_buildmode_select_atoms_of_deposited_obj(self):
        print "UserPrefsDialog.set_buildmode_select_atoms_of_deposited_obj(): Not implemented yet"

    def change_cpk_scale_factor(self):
        print "UserPrefsDialog.change_cpk_scale_factor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UserPrefsDialog",s,c)
