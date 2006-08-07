# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Documents and Settings\Mark\My Documents\ne1 sandbox\cad\src\UserPrefsDialog.ui'
#
# Created: Mon Aug 7 11:28:24 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\x6d\x49\x44\x41\x54\x78\x9c\xed\xd4\x41\x0e\x80" \
    "\x20\x0c\x44\xd1\xaf\x17\xf6\x2c\x9e\x58\xb7\x86" \
    "\x74\x68\x61\x42\x62\x8c\x5d\x97\x47\xd3\x16\xe0" \
    "\x73\x71\xc2\x35\x73\x6e\x5f\x81\x76\x61\x07\x95" \
    "\xb0\x8b\x02\x6c\x2e\x7a\x04\x06\x24\x3d\xae\x84" \
    "\x2a\x24\xbc\xad\x4d\x56\x55\x3d\xf3\xda\x9c\xb0" \
    "\x62\x05\x8d\xe4\xc9\x56\x54\xf1\x61\xd8\xc5\xd3" \
    "\xe1\xcd\xe2\xf6\x56\xfc\xf0\x5a\xb8\xf7\xfc\x4b" \
    "\x13\xcf\xfe\x8f\x68\x73\xec\x56\xb8\x0f\xe9\x3d" \
    "\x71\x03\x2f\xef\x14\x20\x18\x3f\xe3\xe2\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

class UserPrefsDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
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
        tabLayout = QVBoxLayout(self.tab,11,6,"tabLayout")

        layout71 = QHBoxLayout(None,0,6,"layout71")

        self.groupBox7_2 = QGroupBox(self.tab,"groupBox7_2")
        self.groupBox7_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox7_2.layout().setSpacing(6)
        self.groupBox7_2.layout().setMargin(11)
        groupBox7_2Layout = QVBoxLayout(self.groupBox7_2.layout())
        groupBox7_2Layout.setAlignment(Qt.AlignTop)

        self.display_origin_axis_checkbox = QCheckBox(self.groupBox7_2,"display_origin_axis_checkbox")
        self.display_origin_axis_checkbox.setChecked(1)
        groupBox7_2Layout.addWidget(self.display_origin_axis_checkbox)

        self.display_pov_axis_checkbox = QCheckBox(self.groupBox7_2,"display_pov_axis_checkbox")
        self.display_pov_axis_checkbox.setChecked(1)
        groupBox7_2Layout.addWidget(self.display_pov_axis_checkbox)
        layout71.addWidget(self.groupBox7_2)

        self.groupBox17_2 = QGroupBox(self.tab,"groupBox17_2")
        self.groupBox17_2.setColumnLayout(0,Qt.Vertical)
        self.groupBox17_2.layout().setSpacing(6)
        self.groupBox17_2.layout().setMargin(11)
        groupBox17_2Layout = QVBoxLayout(self.groupBox17_2.layout())
        groupBox17_2Layout.setAlignment(Qt.AlignTop)

        self.display_compass_checkbox = QCheckBox(self.groupBox17_2,"display_compass_checkbox")
        self.display_compass_checkbox.setChecked(1)
        groupBox17_2Layout.addWidget(self.display_compass_checkbox)

        self.display_compass_labels_checkbox = QCheckBox(self.groupBox17_2,"display_compass_labels_checkbox")
        self.display_compass_labels_checkbox.setChecked(1)
        groupBox17_2Layout.addWidget(self.display_compass_labels_checkbox)

        layout70 = QHBoxLayout(None,0,6,"layout70")

        self.textLabel1_4 = QLabel(self.groupBox17_2,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout70.addWidget(self.textLabel1_4)

        self.compass_position_combox = QComboBox(0,self.groupBox17_2,"compass_position_combox")
        layout70.addWidget(self.compass_position_combox)
        groupBox17_2Layout.addLayout(layout70)
        layout71.addWidget(self.groupBox17_2)

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
        layout71.addWidget(self.default_projection_btngrp)
        tabLayout.addLayout(layout71)

        layout86 = QHBoxLayout(None,0,6,"layout86")

        self.groupBox14 = QGroupBox(self.tab,"groupBox14")
        self.groupBox14.setColumnLayout(0,Qt.Vertical)
        self.groupBox14.layout().setSpacing(6)
        self.groupBox14.layout().setMargin(11)
        groupBox14Layout = QVBoxLayout(self.groupBox14.layout())
        groupBox14Layout.setAlignment(Qt.AlignTop)

        self.watch_min_in_realtime_checkbox = QCheckBox(self.groupBox14,"watch_min_in_realtime_checkbox")
        groupBox14Layout.addWidget(self.watch_min_in_realtime_checkbox)

        self.update_btngrp = QButtonGroup(self.groupBox14,"update_btngrp")
        self.update_btngrp.setFrameShape(QButtonGroup.StyledPanel)
        self.update_btngrp.setFrameShadow(QButtonGroup.Sunken)
        self.update_btngrp.setColumnLayout(0,Qt.Vertical)
        self.update_btngrp.layout().setSpacing(6)
        self.update_btngrp.layout().setMargin(11)
        update_btngrpLayout = QGridLayout(self.update_btngrp.layout())
        update_btngrpLayout.setAlignment(Qt.AlignTop)

        self.update_number_spinbox = QSpinBox(self.update_btngrp,"update_number_spinbox")
        self.update_number_spinbox.setMaxValue(9999)
        self.update_number_spinbox.setMinValue(1)
        self.update_number_spinbox.setValue(1)

        update_btngrpLayout.addWidget(self.update_number_spinbox,1,1)

        self.update_units_combobox = QComboBox(0,self.update_btngrp,"update_units_combobox")

        update_btngrpLayout.addWidget(self.update_units_combobox,1,2)

        self.update_every_rbtn = QRadioButton(self.update_btngrp,"update_every_rbtn")
        self.update_btngrp.insert( self.update_every_rbtn,1)

        update_btngrpLayout.addWidget(self.update_every_rbtn,1,0)
        spacer2 = QSpacerItem(12,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        update_btngrpLayout.addItem(spacer2,1,3)

        self.update_asap_rbtn = QRadioButton(self.update_btngrp,"update_asap_rbtn")
        self.update_asap_rbtn.setChecked(1)
        self.update_btngrp.insert( self.update_asap_rbtn,0)

        update_btngrpLayout.addMultiCellWidget(self.update_asap_rbtn,0,0,0,2)
        groupBox14Layout.addWidget(self.update_btngrp)

        self.groupBox20 = QGroupBox(self.groupBox14,"groupBox20")
        self.groupBox20.setColumnLayout(0,Qt.Vertical)
        self.groupBox20.layout().setSpacing(6)
        self.groupBox20.layout().setMargin(11)
        groupBox20Layout = QVBoxLayout(self.groupBox20.layout())
        groupBox20Layout.setAlignment(Qt.AlignTop)

        layout79 = QHBoxLayout(None,0,6,"layout79")

        layout73 = QGridLayout(None,1,1,0,6,"layout73")

        self.endrms_lbl = QLabel(self.groupBox20,"endrms_lbl")
        self.endrms_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout73.addWidget(self.endrms_lbl,0,0)

        self.endmax_lbl = QLabel(self.groupBox20,"endmax_lbl")
        self.endmax_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout73.addWidget(self.endmax_lbl,1,0)

        self.endmax_linedit = QLineEdit(self.groupBox20,"endmax_linedit")

        layout73.addWidget(self.endmax_linedit,1,1)

        self.endrms_linedit = QLineEdit(self.groupBox20,"endrms_linedit")
        self.endrms_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.endrms_linedit.setFrameShadow(QLineEdit.Sunken)

        layout73.addWidget(self.endrms_linedit,0,1)
        layout79.addLayout(layout73)

        layout72 = QGridLayout(None,1,1,0,6,"layout72")

        self.cutovermax_lbl = QLabel(self.groupBox20,"cutovermax_lbl")
        self.cutovermax_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout72.addWidget(self.cutovermax_lbl,1,0)

        self.cutovermax_linedit = QLineEdit(self.groupBox20,"cutovermax_linedit")

        layout72.addWidget(self.cutovermax_linedit,1,1)

        self.cutoverrms_linedit = QLineEdit(self.groupBox20,"cutoverrms_linedit")

        layout72.addWidget(self.cutoverrms_linedit,0,1)

        self.cutoverrms_lbl = QLabel(self.groupBox20,"cutoverrms_lbl")
        self.cutoverrms_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout72.addWidget(self.cutoverrms_lbl,0,0)
        layout79.addLayout(layout72)
        groupBox20Layout.addLayout(layout79)

        self.minimize_warning_lbl = QLabel(self.groupBox20,"minimize_warning_lbl")
        self.minimize_warning_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Expanding,0,0,self.minimize_warning_lbl.sizePolicy().hasHeightForWidth()))
        groupBox20Layout.addWidget(self.minimize_warning_lbl)
        groupBox14Layout.addWidget(self.groupBox20)
        layout86.addWidget(self.groupBox14)

        self.groupBox8 = QGroupBox(self.tab,"groupBox8")
        self.groupBox8.setColumnLayout(0,Qt.Vertical)
        self.groupBox8.layout().setSpacing(6)
        self.groupBox8.layout().setMargin(11)
        groupBox8Layout = QVBoxLayout(self.groupBox8.layout())
        groupBox8Layout.setAlignment(Qt.AlignTop)

        self.animate_views_checkbox = QCheckBox(self.groupBox8,"animate_views_checkbox")
        self.animate_views_checkbox.setChecked(1)
        groupBox8Layout.addWidget(self.animate_views_checkbox)

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
        groupBox8Layout.addLayout(layout128)

        self.high_quality_graphics_checkbox = QCheckBox(self.groupBox8,"high_quality_graphics_checkbox")
        self.high_quality_graphics_checkbox.setChecked(1)
        groupBox8Layout.addWidget(self.high_quality_graphics_checkbox)
        layout86.addWidget(self.groupBox8)
        spacer58_4 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout86.addItem(spacer58_4)
        tabLayout.addLayout(layout86)
        spacer109 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        tabLayout.addItem(spacer109)
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

        TabPageLayout.addMultiCellLayout(layout101,0,3,1,1)

        self.atom_colors_grpbox = QGroupBox(self.TabPage,"atom_colors_grpbox")
        self.atom_colors_grpbox.setColumnLayout(0,Qt.Vertical)
        self.atom_colors_grpbox.layout().setSpacing(6)
        self.atom_colors_grpbox.layout().setMargin(11)
        atom_colors_grpboxLayout = QGridLayout(self.atom_colors_grpbox.layout())
        atom_colors_grpboxLayout.setAlignment(Qt.AlignTop)

        layout79_2 = QHBoxLayout(None,0,6,"layout79_2")
        spacer56 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout79_2.addItem(spacer56)

        self.change_element_colors_btn = QPushButton(self.atom_colors_grpbox,"change_element_colors_btn")
        self.change_element_colors_btn.setAutoDefault(0)
        layout79_2.addWidget(self.change_element_colors_btn)

        atom_colors_grpboxLayout.addLayout(layout79_2,0,0)

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
        self.bondpoint_hilite_color_btn.setAutoDefault(0)
        self.bondpoint_hilite_color_btn.setDefault(0)
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
        self.atom_hilite_color_btn.setAutoDefault(0)
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
        self.hotspot_color_btn.setAutoDefault(0)
        layout37_2_2_2_2_2_2.addWidget(self.hotspot_color_btn)

        layout80.addLayout(layout37_2_2_2_2_2_2,3,1)
        groupBox13Layout.addLayout(layout80)

        layout25_2 = QHBoxLayout(None,0,6,"layout25_2")
        spacer20_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25_2.addItem(spacer20_2)

        self.reset_atom_colors_btn = QPushButton(self.groupBox13,"reset_atom_colors_btn")
        self.reset_atom_colors_btn.setAutoDefault(0)
        layout25_2.addWidget(self.reset_atom_colors_btn)
        groupBox13Layout.addLayout(layout25_2)

        atom_colors_grpboxLayout.addWidget(self.groupBox13,1,0)

        TabPageLayout.addWidget(self.atom_colors_grpbox,0,0)
        spacer11 = QSpacerItem(20,27,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout.addItem(spacer11,3,0)

        layout74 = QHBoxLayout(None,0,6,"layout74")

        self.textLabel1_3_2 = QLabel(self.TabPage,"textLabel1_3_2")
        self.textLabel1_3_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout74.addWidget(self.textLabel1_3_2)

        self.cpk_atom_rad_spinbox = QSpinBox(self.TabPage,"cpk_atom_rad_spinbox")
        self.cpk_atom_rad_spinbox.setMaxValue(125)
        self.cpk_atom_rad_spinbox.setMinValue(50)
        self.cpk_atom_rad_spinbox.setValue(100)
        layout74.addWidget(self.cpk_atom_rad_spinbox)
        spacer38 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout74.addItem(spacer38)

        TabPageLayout.addLayout(layout74,1,0)

        layout75 = QHBoxLayout(None,0,6,"layout75")

        self.textLabel1_3_2_2 = QLabel(self.TabPage,"textLabel1_3_2_2")
        self.textLabel1_3_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout75.addWidget(self.textLabel1_3_2_2)

        self.cpk_scale_factor_linedit = QLineEdit(self.TabPage,"cpk_scale_factor_linedit")
        self.cpk_scale_factor_linedit.setMaximumSize(QSize(40,32767))
        self.cpk_scale_factor_linedit.setReadOnly(1)
        layout75.addWidget(self.cpk_scale_factor_linedit)

        self.cpk_scale_factor_slider = QSlider(self.TabPage,"cpk_scale_factor_slider")
        self.cpk_scale_factor_slider.setMinValue(100)
        self.cpk_scale_factor_slider.setMaxValue(200)
        self.cpk_scale_factor_slider.setValue(155)
        self.cpk_scale_factor_slider.setOrientation(QSlider.Horizontal)
        self.cpk_scale_factor_slider.setTickmarks(QSlider.NoMarks)
        self.cpk_scale_factor_slider.setTickInterval(10)
        layout75.addWidget(self.cpk_scale_factor_slider)

        self.reset_cpk_scale_factor_btn = QToolButton(self.TabPage,"reset_cpk_scale_factor_btn")
        self.reset_cpk_scale_factor_btn.setIconSet(QIconSet(self.image0))
        layout75.addWidget(self.reset_cpk_scale_factor_btn)

        TabPageLayout.addLayout(layout75,2,0)
        self.prefs_tab.insertTab(self.TabPage,QString.fromLatin1(""))

        self.TabPage_2 = QWidget(self.prefs_tab,"TabPage_2")
        TabPageLayout_2 = QGridLayout(self.TabPage_2,1,1,11,6,"TabPageLayout_2")

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

        TabPageLayout_2.addMultiCellLayout(layout98,0,2,1,1)
        spacer56_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_2.addItem(spacer56_3,0,2)

        self.groupBox4 = QGroupBox(self.TabPage_2,"groupBox4")
        self.groupBox4.setColumnLayout(0,Qt.Vertical)
        self.groupBox4.layout().setSpacing(6)
        self.groupBox4.layout().setMargin(11)
        groupBox4Layout = QGridLayout(self.groupBox4.layout())
        groupBox4Layout.setAlignment(Qt.AlignTop)

        layout25 = QHBoxLayout(None,0,6,"layout25")
        spacer20 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout25.addItem(spacer20)

        self.reset_bond_colors_btn = QPushButton(self.groupBox4,"reset_bond_colors_btn")
        self.reset_bond_colors_btn.setAutoDefault(0)
        layout25.addWidget(self.reset_bond_colors_btn)

        groupBox4Layout.addMultiCellLayout(layout25,1,1,0,1)

        layout79_3 = QGridLayout(None,1,1,0,6,"layout79_3")

        self.textLabel3_2 = QLabel(self.groupBox4,"textLabel3_2")
        self.textLabel3_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.textLabel3_2.sizePolicy().hasHeightForWidth()))
        self.textLabel3_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout79_3.addWidget(self.textLabel3_2,0,0)

        layout37_2_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2_2")

        self.bond_stretch_color_frame = QFrame(self.groupBox4,"bond_stretch_color_frame")
        self.bond_stretch_color_frame.setMinimumSize(QSize(25,0))
        self.bond_stretch_color_frame.setMaximumSize(QSize(32767,32767))
        self.bond_stretch_color_frame.setPaletteBackgroundColor(QColor(255,0,0))
        self.bond_stretch_color_frame.setFrameShape(QFrame.Box)
        self.bond_stretch_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2.addWidget(self.bond_stretch_color_frame)

        self.bond_stretch_color_btn = QPushButton(self.groupBox4,"bond_stretch_color_btn")
        self.bond_stretch_color_btn.setAutoDefault(0)
        self.bond_stretch_color_btn.setDefault(0)
        layout37_2_2_2_2.addWidget(self.bond_stretch_color_btn)

        layout79_3.addLayout(layout37_2_2_2_2,2,1)

        layout37_2_2_2 = QHBoxLayout(None,0,6,"layout37_2_2_2")

        self.bond_hilite_color_frame = QFrame(self.groupBox4,"bond_hilite_color_frame")
        self.bond_hilite_color_frame.setMinimumSize(QSize(25,0))
        self.bond_hilite_color_frame.setMaximumSize(QSize(32767,32767))
        self.bond_hilite_color_frame.setPaletteBackgroundColor(QColor(255,255,0))
        self.bond_hilite_color_frame.setFrameShape(QFrame.Box)
        self.bond_hilite_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2.addWidget(self.bond_hilite_color_frame)

        self.bond_hilite_color_btn = QPushButton(self.groupBox4,"bond_hilite_color_btn")
        self.bond_hilite_color_btn.setAutoDefault(0)
        layout37_2_2_2.addWidget(self.bond_hilite_color_btn)

        layout79_3.addLayout(layout37_2_2_2,0,1)

        self.textLabel3_3 = QLabel(self.groupBox4,"textLabel3_3")
        self.textLabel3_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout79_3.addWidget(self.textLabel3_3,3,0)

        layout37_2_2 = QHBoxLayout(None,0,6,"layout37_2_2")

        self.ballstick_bondcolor_frame = QFrame(self.groupBox4,"ballstick_bondcolor_frame")
        self.ballstick_bondcolor_frame.setMinimumSize(QSize(25,0))
        self.ballstick_bondcolor_frame.setPaletteBackgroundColor(QColor(158,158,158))
        self.ballstick_bondcolor_frame.setFrameShape(QFrame.Box)
        self.ballstick_bondcolor_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2.addWidget(self.ballstick_bondcolor_frame)

        self.ballstick_bondcolor_btn = QPushButton(self.groupBox4,"ballstick_bondcolor_btn")
        self.ballstick_bondcolor_btn.setAutoDefault(0)
        layout37_2_2.addWidget(self.ballstick_bondcolor_btn)

        layout79_3.addLayout(layout37_2_2,1,1)

        self.textLabel3 = QLabel(self.groupBox4,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout79_3.addWidget(self.textLabel3,1,0)

        self.textLabel3_2_2 = QLabel(self.groupBox4,"textLabel3_2_2")
        self.textLabel3_2_2.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.textLabel3_2_2.sizePolicy().hasHeightForWidth()))
        self.textLabel3_2_2.setMinimumSize(QSize(0,0))
        self.textLabel3_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout79_3.addWidget(self.textLabel3_2_2,2,0)

        layout37_2_2_2_2_3 = QHBoxLayout(None,0,6,"layout37_2_2_2_2_3")

        self.bond_vane_color_frame = QFrame(self.groupBox4,"bond_vane_color_frame")
        self.bond_vane_color_frame.setMinimumSize(QSize(25,0))
        self.bond_vane_color_frame.setMaximumSize(QSize(32767,32767))
        self.bond_vane_color_frame.setPaletteBackgroundColor(QColor(119,0,179))
        self.bond_vane_color_frame.setFrameShape(QFrame.Box)
        self.bond_vane_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_frame)

        self.bond_vane_color_btn = QPushButton(self.groupBox4,"bond_vane_color_btn")
        self.bond_vane_color_btn.setAutoDefault(0)
        layout37_2_2_2_2_3.addWidget(self.bond_vane_color_btn)

        layout79_3.addLayout(layout37_2_2_2_2_3,3,1)

        groupBox4Layout.addLayout(layout79_3,0,1)

        TabPageLayout_2.addWidget(self.groupBox4,0,0)
        spacer22 = QSpacerItem(20,51,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_2.addItem(spacer22,2,0)

        layout84 = QHBoxLayout(None,0,6,"layout84")

        layout83 = QVBoxLayout(None,0,6,"layout83")

        self.textLabel1_3 = QLabel(self.TabPage_2,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout83.addWidget(self.textLabel1_3)

        self.textLabel1 = QLabel(self.TabPage_2,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout83.addWidget(self.textLabel1)
        layout84.addLayout(layout83)

        layout82 = QVBoxLayout(None,0,6,"layout82")

        self.cpk_cylinder_rad_spinbox = QSpinBox(self.TabPage_2,"cpk_cylinder_rad_spinbox")
        self.cpk_cylinder_rad_spinbox.setMaxValue(125)
        self.cpk_cylinder_rad_spinbox.setMinValue(50)
        self.cpk_cylinder_rad_spinbox.setValue(100)
        layout82.addWidget(self.cpk_cylinder_rad_spinbox)

        self.bond_line_thickness_spinbox = QSpinBox(self.TabPage_2,"bond_line_thickness_spinbox")
        self.bond_line_thickness_spinbox.setMaxValue(4)
        self.bond_line_thickness_spinbox.setMinValue(1)
        layout82.addWidget(self.bond_line_thickness_spinbox)
        layout84.addLayout(layout82)
        spacer58 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout84.addItem(spacer58)

        TabPageLayout_2.addLayout(layout84,1,0)
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
        self.default_mode_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.default_mode_lbl.sizePolicy().hasHeightForWidth()))
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

        layout67 = QVBoxLayout(None,0,6,"layout67")

        self.fill_type_combox = QComboBox(0,self.bg_groupbox,"fill_type_combox")
        self.fill_type_combox.setEnabled(1)
        layout67.addWidget(self.fill_type_combox)

        layout37 = QHBoxLayout(None,0,6,"layout37")

        self.bg1_color_frame = QFrame(self.bg_groupbox,"bg1_color_frame")
        self.bg1_color_frame.setMinimumSize(QSize(25,0))
        self.bg1_color_frame.setPaletteBackgroundColor(QColor(170,255,255))
        self.bg1_color_frame.setFrameShape(QFrame.Box)
        self.bg1_color_frame.setFrameShadow(QFrame.Plain)
        layout37.addWidget(self.bg1_color_frame)

        self.choose_bg1_color_btn = QPushButton(self.bg_groupbox,"choose_bg1_color_btn")
        self.choose_bg1_color_btn.setAutoDefault(0)
        layout37.addWidget(self.choose_bg1_color_btn)
        layout67.addLayout(layout37)
        layout69_2.addLayout(layout67)

        bg_groupboxLayout.addMultiCellLayout(layout69_2,0,0,0,1)

        self.restore_bgcolor_btn = QPushButton(self.bg_groupbox,"restore_bgcolor_btn")
        self.restore_bgcolor_btn.setAutoDefault(0)

        bg_groupboxLayout.addWidget(self.restore_bgcolor_btn,1,1)
        spacer7_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        bg_groupboxLayout.addItem(spacer7_2,1,0)

        mode_groupboxLayout.addWidget(self.bg_groupbox,1,0)

        layout69.addWidget(self.mode_groupbox,1,0)

        TabPageLayout_3.addLayout(layout69,0,0)
        spacer8_4 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_3.addItem(spacer8_4,0,2)

        layout66_2 = QVBoxLayout(None,0,6,"layout66_2")

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
        layout66_2.addWidget(self.default_display_btngrp)

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
        layout66_2.addWidget(self.buildmode_groupbox)
        spacer58_3 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout66_2.addItem(spacer58_3)

        TabPageLayout_3.addLayout(layout66_2,0,1)
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

        layout82_2 = QHBoxLayout(None,0,6,"layout82_2")

        layout37_2_2_2_4 = QHBoxLayout(None,0,6,"layout37_2_2_2_4")

        self.light_color_frame = QFrame(self.groupBox8_2,"light_color_frame")
        self.light_color_frame.setMinimumSize(QSize(25,0))
        self.light_color_frame.setPaletteBackgroundColor(QColor(255,255,255))
        self.light_color_frame.setFrameShape(QFrame.Box)
        self.light_color_frame.setFrameShadow(QFrame.Plain)
        layout37_2_2_2_4.addWidget(self.light_color_frame)

        self.light_color_btn = QPushButton(self.groupBox8_2,"light_color_btn")
        self.light_color_btn.setAutoDefault(0)
        layout37_2_2_2_4.addWidget(self.light_color_btn)
        layout82_2.addLayout(layout37_2_2_2_4)
        spacer50 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout82_2.addItem(spacer50)
        layout559.addLayout(layout82_2)

        layout66_3 = QHBoxLayout(None,0,6,"layout66_3")

        self.light_ambient_linedit = QLineEdit(self.groupBox8_2,"light_ambient_linedit")
        self.light_ambient_linedit.setMaximumSize(QSize(40,32767))
        self.light_ambient_linedit.setReadOnly(1)
        layout66_3.addWidget(self.light_ambient_linedit)

        self.light_ambient_slider = QSlider(self.groupBox8_2,"light_ambient_slider")
        self.light_ambient_slider.setMaxValue(100)
        self.light_ambient_slider.setOrientation(QSlider.Horizontal)
        self.light_ambient_slider.setTickmarks(QSlider.NoMarks)
        self.light_ambient_slider.setTickInterval(10)
        layout66_3.addWidget(self.light_ambient_slider)
        layout559.addLayout(layout66_3)

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

        layout61 = QHBoxLayout(None,0,6,"layout61")

        self.light_z_linedit = QLineEdit(self.groupBox8_2,"light_z_linedit")
        self.light_z_linedit.setMaxLength(32767)
        layout61.addWidget(self.light_z_linedit)
        spacer44 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout61.addItem(spacer44)
        layout559.addLayout(layout61)

        groupBox8_2Layout.addLayout(layout559,0,1)

        TabPageLayout_4.addMultiCellWidget(self.groupBox8_2,0,2,0,0)

        layout505 = QHBoxLayout(None,0,6,"layout505")
        spacer57 = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout505.addItem(spacer57)

        self.lighting_restore_defaults_btn = QPushButton(self.TabPage_4,"lighting_restore_defaults_btn")
        self.lighting_restore_defaults_btn.setAutoDefault(0)
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
        spacer49 = QSpacerItem(20,218,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_5.addItem(spacer49,1,0)

        self.file_locations_grp = QGroupBox(self.TabPage_5,"file_locations_grp")
        self.file_locations_grp.setColumnLayout(0,Qt.Vertical)
        self.file_locations_grp.layout().setSpacing(6)
        self.file_locations_grp.layout().setMargin(11)
        file_locations_grpLayout = QGridLayout(self.file_locations_grp.layout())
        file_locations_grpLayout.setAlignment(Qt.AlignTop)

        self.povray_path_linedit = QLineEdit(self.file_locations_grp,"povray_path_linedit")
        self.povray_path_linedit.setEnabled(0)
        self.povray_path_linedit.setMaximumSize(QSize(32767,32767))
        self.povray_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.povray_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.povray_path_linedit.setMaxLength(32767)
        self.povray_path_linedit.setReadOnly(1)

        file_locations_grpLayout.addMultiCellWidget(self.povray_path_linedit,1,1,1,2)

        self.nanohive_path_linedit = QLineEdit(self.file_locations_grp,"nanohive_path_linedit")
        self.nanohive_path_linedit.setEnabled(0)
        self.nanohive_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.nanohive_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.nanohive_path_linedit.setReadOnly(1)

        file_locations_grpLayout.addMultiCellWidget(self.nanohive_path_linedit,0,0,1,2)

        self.megapov_path_linedit = QLineEdit(self.file_locations_grp,"megapov_path_linedit")
        self.megapov_path_linedit.setEnabled(0)
        self.megapov_path_linedit.setMaximumSize(QSize(32767,32767))
        self.megapov_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.megapov_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.megapov_path_linedit.setMaxLength(32767)
        self.megapov_path_linedit.setReadOnly(1)

        file_locations_grpLayout.addMultiCellWidget(self.megapov_path_linedit,2,2,1,2)

        self.gamess_path_linedit = QLineEdit(self.file_locations_grp,"gamess_path_linedit")
        self.gamess_path_linedit.setEnabled(0)
        self.gamess_path_linedit.setMaximumSize(QSize(32767,32767))
        self.gamess_path_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.gamess_path_linedit.setFrameShadow(QLineEdit.Sunken)
        self.gamess_path_linedit.setMaxLength(32767)
        self.gamess_path_linedit.setReadOnly(1)

        file_locations_grpLayout.addMultiCellWidget(self.gamess_path_linedit,4,4,1,2)

        self.povray_choose_btn = QPushButton(self.file_locations_grp,"povray_choose_btn")
        self.povray_choose_btn.setEnabled(0)
        self.povray_choose_btn.setAutoDefault(0)

        file_locations_grpLayout.addWidget(self.povray_choose_btn,1,3)

        self.megapov_choose_btn = QPushButton(self.file_locations_grp,"megapov_choose_btn")
        self.megapov_choose_btn.setEnabled(0)
        self.megapov_choose_btn.setAutoDefault(0)

        file_locations_grpLayout.addWidget(self.megapov_choose_btn,2,3)

        self.povdir_choose_btn = QPushButton(self.file_locations_grp,"povdir_choose_btn")
        self.povdir_choose_btn.setEnabled(0)
        self.povdir_choose_btn.setAutoDefault(0)

        file_locations_grpLayout.addWidget(self.povdir_choose_btn,3,3)

        self.gamess_choose_btn = QPushButton(self.file_locations_grp,"gamess_choose_btn")
        self.gamess_choose_btn.setEnabled(0)
        self.gamess_choose_btn.setAutoDefault(0)

        file_locations_grpLayout.addWidget(self.gamess_choose_btn,4,3)

        self.povdir_linedit = QLineEdit(self.file_locations_grp,"povdir_linedit")
        self.povdir_linedit.setEnabled(0)

        file_locations_grpLayout.addWidget(self.povdir_linedit,3,2)

        self.nanohive_choose_btn = QPushButton(self.file_locations_grp,"nanohive_choose_btn")
        self.nanohive_choose_btn.setEnabled(0)
        self.nanohive_choose_btn.setAutoDefault(0)

        file_locations_grpLayout.addWidget(self.nanohive_choose_btn,0,3)

        layout71_2 = QHBoxLayout(None,0,6,"layout71_2")

        self.nanohive_checkbox = QCheckBox(self.file_locations_grp,"nanohive_checkbox")
        self.nanohive_checkbox.setEnabled(1)
        layout71_2.addWidget(self.nanohive_checkbox)

        self.nanohive_lbl = QLabel(self.file_locations_grp,"nanohive_lbl")
        self.nanohive_lbl.setEnabled(1)
        self.nanohive_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.nanohive_lbl.sizePolicy().hasHeightForWidth()))
        self.nanohive_lbl.setMinimumSize(QSize(60,0))
        self.nanohive_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout71_2.addWidget(self.nanohive_lbl)

        file_locations_grpLayout.addLayout(layout71_2,0,0)

        layout72_2 = QHBoxLayout(None,0,6,"layout72_2")

        self.povray_checkbox = QCheckBox(self.file_locations_grp,"povray_checkbox")
        layout72_2.addWidget(self.povray_checkbox)

        self.povray_lbl = QLabel(self.file_locations_grp,"povray_lbl")
        self.povray_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.povray_lbl.sizePolicy().hasHeightForWidth()))
        self.povray_lbl.setMinimumSize(QSize(60,0))
        self.povray_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout72_2.addWidget(self.povray_lbl)

        file_locations_grpLayout.addLayout(layout72_2,1,0)

        layout73_2 = QHBoxLayout(None,0,6,"layout73_2")

        self.megapov_checkbox = QCheckBox(self.file_locations_grp,"megapov_checkbox")
        layout73_2.addWidget(self.megapov_checkbox)

        self.megapov_lbl = QLabel(self.file_locations_grp,"megapov_lbl")
        self.megapov_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.megapov_lbl.sizePolicy().hasHeightForWidth()))
        self.megapov_lbl.setMinimumSize(QSize(60,0))
        self.megapov_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout73_2.addWidget(self.megapov_lbl)

        file_locations_grpLayout.addLayout(layout73_2,2,0)

        layout74_2 = QHBoxLayout(None,0,6,"layout74_2")

        self.povdir_checkbox = QCheckBox(self.file_locations_grp,"povdir_checkbox")
        self.povdir_checkbox.setEnabled(0)
        self.povdir_checkbox.setPaletteForegroundColor(QColor(0,0,0))
        layout74_2.addWidget(self.povdir_checkbox)

        self.povdir_lbl = QLabel(self.file_locations_grp,"povdir_lbl")
        self.povdir_lbl.setEnabled(0)
        self.povdir_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout74_2.addWidget(self.povdir_lbl)

        file_locations_grpLayout.addMultiCellLayout(layout74_2,3,3,0,1)

        layout75_2 = QHBoxLayout(None,0,6,"layout75_2")

        self.gamess_checkbox = QCheckBox(self.file_locations_grp,"gamess_checkbox")
        layout75_2.addWidget(self.gamess_checkbox)

        self.gamess_lbl = QLabel(self.file_locations_grp,"gamess_lbl")
        self.gamess_lbl.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Preferred,0,0,self.gamess_lbl.sizePolicy().hasHeightForWidth()))
        self.gamess_lbl.setMinimumSize(QSize(60,0))
        self.gamess_lbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout75_2.addWidget(self.gamess_lbl)

        file_locations_grpLayout.addLayout(layout75_2,4,0)

        TabPageLayout_5.addWidget(self.file_locations_grp,0,0)
        self.prefs_tab.insertTab(self.TabPage_5,QString.fromLatin1(""))

        self.TabPage_6 = QWidget(self.prefs_tab,"TabPage_6")
        TabPageLayout_6 = QGridLayout(self.TabPage_6,1,1,11,6,"TabPageLayout_6")
        spacer10 = QSpacerItem(20,110,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_6.addItem(spacer10,2,0)

        layout68_3 = QHBoxLayout(None,0,6,"layout68_3")

        self.groupBox17 = QGroupBox(self.TabPage_6,"groupBox17")
        self.groupBox17.setColumnLayout(0,Qt.Vertical)
        self.groupBox17.layout().setSpacing(6)
        self.groupBox17.layout().setMargin(11)
        groupBox17Layout = QGridLayout(self.groupBox17.layout())
        groupBox17Layout.setAlignment(Qt.AlignTop)

        self.msg_serial_number_checkbox = QCheckBox(self.groupBox17,"msg_serial_number_checkbox")

        groupBox17Layout.addWidget(self.msg_serial_number_checkbox,0,0)

        self.msg_timestamp_checkbox = QCheckBox(self.groupBox17,"msg_timestamp_checkbox")

        groupBox17Layout.addWidget(self.msg_timestamp_checkbox,1,0)
        layout68_3.addWidget(self.groupBox17)
        spacer58_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout68_3.addItem(spacer58_2)

        TabPageLayout_6.addLayout(layout68_3,1,0)

        layout70_2 = QGridLayout(None,1,1,0,6,"layout70_2")
        spacer56_5 = QSpacerItem(268,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout70_2.addItem(spacer56_5,2,2)

        self.undo_automatic_checkpoints_checkbox = QCheckBox(self.TabPage_6,"undo_automatic_checkpoints_checkbox")

        layout70_2.addMultiCellWidget(self.undo_automatic_checkpoints_checkbox,1,1,0,2)

        self.undo_stack_memory_limit_spinbox = QSpinBox(self.TabPage_6,"undo_stack_memory_limit_spinbox")
        self.undo_stack_memory_limit_spinbox.setMaxValue(99999)

        layout70_2.addWidget(self.undo_stack_memory_limit_spinbox,2,1)

        self.undo_restore_view_checkbox = QCheckBox(self.TabPage_6,"undo_restore_view_checkbox")

        layout70_2.addMultiCellWidget(self.undo_restore_view_checkbox,0,0,0,2)

        self.undo_stack_memory_limit_label = QLabel(self.TabPage_6,"undo_stack_memory_limit_label")

        layout70_2.addWidget(self.undo_stack_memory_limit_label,2,0)

        TabPageLayout_6.addLayout(layout70_2,0,0)
        self.prefs_tab.insertTab(self.TabPage_6,QString.fromLatin1(""))

        self.TabPage_7 = QWidget(self.prefs_tab,"TabPage_7")
        TabPageLayout_7 = QGridLayout(self.TabPage_7,1,1,11,6,"TabPageLayout_7")
        spacer94 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        TabPageLayout_7.addItem(spacer94,2,0)

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

        TabPageLayout_7.addMultiCellLayout(layout15,1,1,0,1)
        spacer47 = QSpacerItem(70,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TabPageLayout_7.addItem(spacer47,0,1)

        self.groupBox10 = QGroupBox(self.TabPage_7,"groupBox10")
        self.groupBox10.setColumnLayout(0,Qt.Vertical)
        self.groupBox10.layout().setSpacing(6)
        self.groupBox10.layout().setMargin(11)
        groupBox10Layout = QGridLayout(self.groupBox10.layout())
        groupBox10Layout.setAlignment(Qt.AlignTop)

        layout115 = QVBoxLayout(None,0,6,"layout115")

        self.textLabel1_2 = QLabel(self.groupBox10,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout115.addWidget(self.textLabel1_2)

        self.textLabel1_2_2 = QLabel(self.groupBox10,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout115.addWidget(self.textLabel1_2_2)

        groupBox10Layout.addLayout(layout115,0,0)

        layout116 = QVBoxLayout(None,0,6,"layout116")

        self.save_current_btn = QPushButton(self.groupBox10,"save_current_btn")
        self.save_current_btn.setAutoDefault(0)
        layout116.addWidget(self.save_current_btn)

        self.restore_saved_size_btn = QPushButton(self.groupBox10,"restore_saved_size_btn")
        self.restore_saved_size_btn.setAutoDefault(0)
        layout116.addWidget(self.restore_saved_size_btn)

        groupBox10Layout.addLayout(layout116,0,2)

        layout117_2 = QGridLayout(None,1,1,0,6,"layout117_2")

        self.current_width_spinbox = QSpinBox(self.groupBox10,"current_width_spinbox")
        self.current_width_spinbox.setMaxValue(2048)
        self.current_width_spinbox.setMinValue(640)
        self.current_width_spinbox.setValue(640)

        layout117_2.addWidget(self.current_width_spinbox,0,0)

        self.saved_height_lineedit = QLineEdit(self.groupBox10,"saved_height_lineedit")
        self.saved_height_lineedit.setReadOnly(1)

        layout117_2.addWidget(self.saved_height_lineedit,1,2)

        self.current_height_spinbox = QSpinBox(self.groupBox10,"current_height_spinbox")
        self.current_height_spinbox.setMaxValue(2000)
        self.current_height_spinbox.setMinValue(480)
        self.current_height_spinbox.setValue(480)

        layout117_2.addWidget(self.current_height_spinbox,0,2)

        self.saved_width_lineedit = QLineEdit(self.groupBox10,"saved_width_lineedit")
        self.saved_width_lineedit.setReadOnly(1)

        layout117_2.addWidget(self.saved_width_lineedit,1,0)

        self.textLabel1_2_2_2 = QLabel(self.groupBox10,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignCenter)

        layout117_2.addWidget(self.textLabel1_2_2_2,0,1)

        self.textLabel1_2_2_2_2 = QLabel(self.groupBox10,"textLabel1_2_2_2_2")
        self.textLabel1_2_2_2_2.setAlignment(QLabel.AlignCenter)

        layout117_2.addWidget(self.textLabel1_2_2_2_2,1,1)

        groupBox10Layout.addLayout(layout117_2,0,1)

        self.remember_win_pos_and_size_checkbox = QCheckBox(self.groupBox10,"remember_win_pos_and_size_checkbox")

        groupBox10Layout.addMultiCellWidget(self.remember_win_pos_and_size_checkbox,1,1,0,2)

        TabPageLayout_7.addWidget(self.groupBox10,0,0)
        self.prefs_tab.insertTab(self.TabPage_7,QString.fromLatin1(""))

        UserPrefsDialogLayout.addWidget(self.prefs_tab,0,0)

        self.languageChange()

        self.resize(QSize(595,481).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.animation_speed_slider,SIGNAL("sliderReleased()"),self.change_view_animation_speed)
        self.connect(self.atom_hilite_color_btn,SIGNAL("clicked()"),self.change_atom_hilite_color)
        self.connect(self.ballstick_bondcolor_btn,SIGNAL("clicked()"),self.change_ballstick_bondcolor)
        self.connect(self.bond_hilite_color_btn,SIGNAL("clicked()"),self.change_bond_hilite_color)
        self.connect(self.bond_line_thickness_spinbox,SIGNAL("valueChanged(int)"),self.change_bond_line_thickness)
        self.connect(self.bond_stretch_color_btn,SIGNAL("clicked()"),self.change_bond_stretch_color)
        self.connect(self.bond_vane_color_btn,SIGNAL("clicked()"),self.change_bond_vane_color)
        self.connect(self.bondpoint_hilite_color_btn,SIGNAL("clicked()"),self.change_bondpoint_hilite_color)
        self.connect(self.caption_fullpath_checkbox,SIGNAL("stateChanged(int)"),self.set_caption_fullpath)
        self.connect(self.change_element_colors_btn,SIGNAL("clicked()"),self.change_element_colors)
        self.connect(self.choose_bg1_color_btn,SIGNAL("clicked()"),self.change_bg1_color)
        self.connect(self.cpk_atom_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_ballstick_atom_radius)
        self.connect(self.cpk_cylinder_rad_spinbox,SIGNAL("valueChanged(int)"),self.change_ballstick_cylinder_radius)
        self.connect(self.cpk_scale_factor_slider,SIGNAL("sliderReleased()"),self.save_cpk_scale_factor)
        self.connect(self.cpk_scale_factor_slider,SIGNAL("valueChanged(int)"),self.change_cpk_scale_factor)
        self.connect(self.default_display_btngrp,SIGNAL("clicked(int)"),self.set_default_display_mode)
        self.connect(self.default_mode_combox,SIGNAL("activated(int)"),self.change_default_mode)
        self.connect(self.default_projection_btngrp,SIGNAL("clicked(int)"),self.set_default_projection)
        self.connect(self.display_compass_checkbox,SIGNAL("stateChanged(int)"),self.display_compass)
        self.connect(self.display_mode_combox,SIGNAL("activated(int)"),self.change_display_mode)
        self.connect(self.fill_type_combox,SIGNAL("activated(const QString&)"),self.fill_type_changed)
        self.connect(self.gamess_checkbox,SIGNAL("toggled(bool)"),self.enable_gamess)
        self.connect(self.gamess_choose_btn,SIGNAL("clicked()"),self.set_gamess_path)
        self.connect(self.high_order_bond_display_btngrp,SIGNAL("clicked(int)"),self.change_high_order_bond_display)
        self.connect(self.high_quality_graphics_checkbox,SIGNAL("toggled(bool)"),self.change_high_quality_graphics)
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
        self.connect(self.ms_brightness_slider,SIGNAL("valueChanged(int)"),self.change_material_brightness)
        self.connect(self.ms_brightness_slider,SIGNAL("sliderPressed()"),self.change_material_brightness_start)
        self.connect(self.ms_finish_slider,SIGNAL("valueChanged(int)"),self.change_material_finish)
        self.connect(self.ms_finish_slider,SIGNAL("sliderReleased()"),self.change_material_finish_stop)
        self.connect(self.ms_finish_slider,SIGNAL("sliderPressed()"),self.change_material_finish_start)
        self.connect(self.ms_on_checkbox,SIGNAL("toggled(bool)"),self.toggle_material_specularity)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderPressed()"),self.change_material_shininess_start)
        self.connect(self.ms_shininess_slider,SIGNAL("sliderReleased()"),self.change_material_shininess_stop)
        self.connect(self.ms_shininess_slider,SIGNAL("valueChanged(int)"),self.change_material_shininess)
        self.connect(self.nanohive_checkbox,SIGNAL("toggled(bool)"),self.enable_nanohive)
        self.connect(self.nanohive_choose_btn,SIGNAL("clicked()"),self.set_nanohive_path)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.prefs_tab,SIGNAL("selected(const QString&)"),self.setup_current_page)
        self.connect(self.reset_atom_colors_btn,SIGNAL("clicked()"),self.reset_atom_colors)
        self.connect(self.reset_bond_colors_btn,SIGNAL("clicked()"),self.reset_bond_colors)
        self.connect(self.reset_cpk_scale_factor_btn,SIGNAL("clicked()"),self.reset_cpk_scale_factor)
        self.connect(self.restore_bgcolor_btn,SIGNAL("clicked()"),self.restore_default_bgcolor)
        self.connect(self.save_current_btn,SIGNAL("clicked()"),self.save_current_win_pos_and_size)
        self.connect(self.show_bond_labels_checkbox,SIGNAL("toggled(bool)"),self.change_bond_labels)
        self.connect(self.show_valence_errors_checkbox,SIGNAL("toggled(bool)"),self.change_show_valence_errors)
        self.connect(self.startup_mode_combox,SIGNAL("activated(const QString&)"),self.change_startup_mode)
        self.connect(self.undo_stack_memory_limit_spinbox,SIGNAL("valueChanged(int)"),self.change_undo_stack_memory_limit)
        self.connect(self.current_width_spinbox,SIGNAL("valueChanged(int)"),self.change_window_size)
        self.connect(self.current_height_spinbox,SIGNAL("valueChanged(int)"),self.change_window_size)
        self.connect(self.restore_saved_size_btn,SIGNAL("clicked()"),self.restore_saved_size)
        self.connect(self.povray_checkbox,SIGNAL("toggled(bool)"),self.enable_povray)
        self.connect(self.povray_choose_btn,SIGNAL("clicked()"),self.set_povray_path)
        self.connect(self.endrms_linedit,SIGNAL("textChanged(const QString&)"),self.change_endrms)
        self.connect(self.endmax_linedit,SIGNAL("textChanged(const QString&)"),self.change_endmax)
        self.connect(self.cutoverrms_linedit,SIGNAL("textChanged(const QString&)"),self.change_cutoverrms)
        self.connect(self.cutovermax_linedit,SIGNAL("textChanged(const QString&)"),self.change_cutovermax)
        self.connect(self.compass_position_combox,SIGNAL("activated(int)"),self.set_compass_position)
        self.connect(self.watch_min_in_realtime_checkbox,SIGNAL("toggled(bool)"),self.update_btngrp.setEnabled)
        self.connect(self.update_number_spinbox,SIGNAL("valueChanged(int)"),self.update_number_spinbox_valueChanged)
        self.connect(self.megapov_checkbox,SIGNAL("toggled(bool)"),self.enable_megapov)
        self.connect(self.megapov_choose_btn,SIGNAL("clicked()"),self.set_megapov_path)
        self.connect(self.povdir_checkbox,SIGNAL("toggled(bool)"),self.enable_povdir)
        self.connect(self.povdir_choose_btn,SIGNAL("clicked()"),self.set_povdir)
        self.connect(self.megapov_checkbox,SIGNAL("toggled(bool)"),self.povdir_checkbox.setEnabled)
        self.connect(self.megapov_checkbox,SIGNAL("toggled(bool)"),self.povdir_lbl.setEnabled)
        self.connect(self.megapov_checkbox,SIGNAL("toggled(bool)"),self.povdir_linedit.setEnabled)
        self.connect(self.megapov_checkbox,SIGNAL("toggled(bool)"),self.povdir_linedit.clear)

        self.setTabOrder(self.prefs_tab,self.display_compass_checkbox)
        self.setTabOrder(self.display_compass_checkbox,self.display_compass_labels_checkbox)
        self.setTabOrder(self.display_compass_labels_checkbox,self.display_origin_axis_checkbox)
        self.setTabOrder(self.display_origin_axis_checkbox,self.display_pov_axis_checkbox)
        self.setTabOrder(self.display_pov_axis_checkbox,self.watch_min_in_realtime_checkbox)
        self.setTabOrder(self.watch_min_in_realtime_checkbox,self.endrms_linedit)
        self.setTabOrder(self.endrms_linedit,self.endmax_linedit)
        self.setTabOrder(self.endmax_linedit,self.cutoverrms_linedit)
        self.setTabOrder(self.cutoverrms_linedit,self.cutovermax_linedit)
        self.setTabOrder(self.cutovermax_linedit,self.radioButton12)
        self.setTabOrder(self.radioButton12,self.high_quality_graphics_checkbox)
        self.setTabOrder(self.high_quality_graphics_checkbox,self.animate_views_checkbox)
        self.setTabOrder(self.animate_views_checkbox,self.animation_speed_slider)
        self.setTabOrder(self.animation_speed_slider,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.change_element_colors_btn)
        self.setTabOrder(self.change_element_colors_btn,self.atom_hilite_color_btn)
        self.setTabOrder(self.atom_hilite_color_btn,self.bondpoint_hilite_color_btn)
        self.setTabOrder(self.bondpoint_hilite_color_btn,self.hotspot_color_btn)
        self.setTabOrder(self.hotspot_color_btn,self.reset_atom_colors_btn)
        self.setTabOrder(self.reset_atom_colors_btn,self.cpk_atom_rad_spinbox)
        self.setTabOrder(self.cpk_atom_rad_spinbox,self.cpk_scale_factor_linedit)
        self.setTabOrder(self.cpk_scale_factor_linedit,self.cpk_scale_factor_slider)
        self.setTabOrder(self.cpk_scale_factor_slider,self.level_of_detail_combox)
        self.setTabOrder(self.level_of_detail_combox,self.bond_hilite_color_btn)
        self.setTabOrder(self.bond_hilite_color_btn,self.ballstick_bondcolor_btn)
        self.setTabOrder(self.ballstick_bondcolor_btn,self.bond_stretch_color_btn)
        self.setTabOrder(self.bond_stretch_color_btn,self.bond_vane_color_btn)
        self.setTabOrder(self.bond_vane_color_btn,self.reset_bond_colors_btn)
        self.setTabOrder(self.reset_bond_colors_btn,self.cpk_cylinder_rad_spinbox)
        self.setTabOrder(self.cpk_cylinder_rad_spinbox,self.bond_line_thickness_spinbox)
        self.setTabOrder(self.bond_line_thickness_spinbox,self.radioButton11)
        self.setTabOrder(self.radioButton11,self.show_bond_labels_checkbox)
        self.setTabOrder(self.show_bond_labels_checkbox,self.show_valence_errors_checkbox)
        self.setTabOrder(self.show_valence_errors_checkbox,self.startup_mode_combox)
        self.setTabOrder(self.startup_mode_combox,self.default_mode_combox)
        self.setTabOrder(self.default_mode_combox,self.mode_combox)
        self.setTabOrder(self.mode_combox,self.display_mode_combox)
        self.setTabOrder(self.display_mode_combox,self.fill_type_combox)
        self.setTabOrder(self.fill_type_combox,self.choose_bg1_color_btn)
        self.setTabOrder(self.choose_bg1_color_btn,self.restore_bgcolor_btn)
        self.setTabOrder(self.restore_bgcolor_btn,self.vwd_rbtn)
        self.setTabOrder(self.vwd_rbtn,self.cpk_rbtn)
        self.setTabOrder(self.cpk_rbtn,self.tubes_rbtn)
        self.setTabOrder(self.tubes_rbtn,self.lines_rbtn)
        self.setTabOrder(self.lines_rbtn,self.autobond_checkbox)
        self.setTabOrder(self.autobond_checkbox,self.buildmode_highlighting_checkbox)
        self.setTabOrder(self.buildmode_highlighting_checkbox,self.buildmode_select_atoms_checkbox)
        self.setTabOrder(self.buildmode_select_atoms_checkbox,self.water_checkbox)
        self.setTabOrder(self.water_checkbox,self.light_combobox)
        self.setTabOrder(self.light_combobox,self.light_checkbox)
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
        self.setTabOrder(self.light_z_linedit,self.ms_on_checkbox)
        self.setTabOrder(self.ms_on_checkbox,self.ms_finish_linedit)
        self.setTabOrder(self.ms_finish_linedit,self.ms_finish_slider)
        self.setTabOrder(self.ms_finish_slider,self.ms_shininess_linedit)
        self.setTabOrder(self.ms_shininess_linedit,self.ms_shininess_slider)
        self.setTabOrder(self.ms_shininess_slider,self.ms_brightness_linedit)
        self.setTabOrder(self.ms_brightness_linedit,self.ms_brightness_slider)
        self.setTabOrder(self.ms_brightness_slider,self.lighting_restore_defaults_btn)
        self.setTabOrder(self.lighting_restore_defaults_btn,self.gamess_checkbox)
        self.setTabOrder(self.gamess_checkbox,self.gamess_path_linedit)
        self.setTabOrder(self.gamess_path_linedit,self.gamess_choose_btn)
        self.setTabOrder(self.gamess_choose_btn,self.nanohive_checkbox)
        self.setTabOrder(self.nanohive_checkbox,self.nanohive_path_linedit)
        self.setTabOrder(self.nanohive_path_linedit,self.nanohive_choose_btn)
        self.setTabOrder(self.nanohive_choose_btn,self.undo_restore_view_checkbox)
        self.setTabOrder(self.undo_restore_view_checkbox,self.undo_automatic_checkpoints_checkbox)
        self.setTabOrder(self.undo_automatic_checkpoints_checkbox,self.undo_stack_memory_limit_spinbox)
        self.setTabOrder(self.undo_stack_memory_limit_spinbox,self.msg_serial_number_checkbox)
        self.setTabOrder(self.msg_serial_number_checkbox,self.msg_timestamp_checkbox)
        self.setTabOrder(self.msg_timestamp_checkbox,self.current_width_spinbox)
        self.setTabOrder(self.current_width_spinbox,self.current_height_spinbox)
        self.setTabOrder(self.current_height_spinbox,self.save_current_btn)
        self.setTabOrder(self.save_current_btn,self.saved_width_lineedit)
        self.setTabOrder(self.saved_width_lineedit,self.saved_height_lineedit)
        self.setTabOrder(self.saved_height_lineedit,self.restore_saved_size_btn)
        self.setTabOrder(self.restore_saved_size_btn,self.remember_win_pos_and_size_checkbox)
        self.setTabOrder(self.remember_win_pos_and_size_checkbox,self.caption_prefix_linedit)
        self.setTabOrder(self.caption_prefix_linedit,self.caption_suffix_linedit)
        self.setTabOrder(self.caption_suffix_linedit,self.caption_fullpath_checkbox)
        self.setTabOrder(self.caption_fullpath_checkbox,self.povray_path_linedit)
        self.setTabOrder(self.povray_path_linedit,self.povray_choose_btn)
        self.setTabOrder(self.povray_choose_btn,self.povray_checkbox)


    def languageChange(self):
        self.setCaption(self.__tr("Preferences"))
        self.ok_btn.setText(self.__tr("OK"))
        self.groupBox7_2.setTitle(self.__tr("Axes"))
        self.display_origin_axis_checkbox.setText(self.__tr("Display Origin Axis"))
        QToolTip.add(self.display_origin_axis_checkbox,self.__tr("Show/Hide Origin Axis"))
        self.display_pov_axis_checkbox.setText(self.__tr("Display Point of View Axis"))
        QToolTip.add(self.display_pov_axis_checkbox,self.__tr("Show/Hide Point of View Axis"))
        self.groupBox17_2.setTitle(self.__tr("Compass"))
        self.display_compass_checkbox.setText(self.__tr("Display Compass"))
        QToolTip.add(self.display_compass_checkbox,self.__tr("Show/Hide Display Compass"))
        self.display_compass_labels_checkbox.setText(self.__tr("Display Compass Labels"))
        QToolTip.add(self.display_compass_labels_checkbox,self.__tr("Show/Hide Display Compass"))
        self.textLabel1_4.setText(self.__tr("Location :"))
        self.compass_position_combox.clear()
        self.compass_position_combox.insertItem(self.__tr("Upper Right"))
        self.compass_position_combox.insertItem(self.__tr("Upper Left"))
        self.compass_position_combox.insertItem(self.__tr("Lower Left"))
        self.compass_position_combox.insertItem(self.__tr("Lower Right"))
        self.default_projection_btngrp.setTitle(self.__tr("Default Projection"))
        QToolTip.add(self.default_projection_btngrp,QString.null)
        self.radioButton12.setText(self.__tr("Perspective"))
        self.radioButton13.setText(self.__tr("Orthographic"))
        self.groupBox14.setTitle(self.__tr("Settings for Adjust"))
        self.watch_min_in_realtime_checkbox.setText(self.__tr("Watch motion in real time"))
        QToolTip.add(self.watch_min_in_realtime_checkbox,self.__tr("Enable/disable real time graphical updates for <b>Adjust All</b> or <b>Adjust Selection</b>"))
        self.update_btngrp.setTitle(QString.null)
        QToolTip.add(self.update_number_spinbox,self.__tr("Specify how often to update the screen during adjustments"))
        self.update_units_combobox.clear()
        self.update_units_combobox.insertItem(self.__tr("frames"))
        self.update_units_combobox.insertItem(self.__tr("seconds"))
        self.update_units_combobox.insertItem(self.__tr("minutes"))
        self.update_units_combobox.insertItem(self.__tr("hours"))
        QToolTip.add(self.update_units_combobox,self.__tr("Specify how often to update the screen during adjustments"))
        self.update_every_rbtn.setText(self.__tr("Update every"))
        QToolTip.add(self.update_every_rbtn,self.__tr("Specify how often to update the screen during adjustments"))
        self.update_asap_rbtn.setText(self.__tr("Update as fast as possible"))
        QToolTip.add(self.update_asap_rbtn,self.__tr("Update every 2 seconds, or faster if it doesn't slow adjustments by more than 20%"))
        self.groupBox20.setTitle(self.__tr("Convergence Criteria"))
        self.endrms_lbl.setText(self.__tr("EndRMS :"))
        QToolTip.add(self.endrms_lbl,self.__tr("Target RMS force (pN)"))
        self.endmax_lbl.setText(self.__tr("EndMax :"))
        QToolTip.add(self.endmax_lbl,self.__tr("Target max force (pN)"))
        self.endmax_linedit.setText(self.__tr("10.0"))
        QToolTip.add(self.endmax_linedit,self.__tr("Target max force (pN)"))
        self.endrms_linedit.setText(self.__tr("1.0"))
        QToolTip.add(self.endrms_linedit,self.__tr("Target RMS force (pN)"))
        self.cutovermax_lbl.setText(self.__tr("CutoverMax :"))
        QToolTip.add(self.cutovermax_lbl,self.__tr("Cutover max force (pN)"))
        self.cutovermax_linedit.setText(self.__tr("300.0"))
        QToolTip.add(self.cutovermax_linedit,self.__tr("Cutover max force (pN)"))
        self.cutoverrms_linedit.setText(self.__tr("50.0"))
        QToolTip.add(self.cutoverrms_linedit,self.__tr("Cutover RMS force (pN)"))
        self.cutoverrms_lbl.setText(self.__tr("CutoverRMS :"))
        QToolTip.add(self.cutoverrms_lbl,self.__tr("Cutover RMS force (pN)"))
        self.minimize_warning_lbl.setText(QString.null)
        self.groupBox8.setTitle(self.__tr("View Animation"))
        self.animate_views_checkbox.setText(self.__tr("Animate between views"))
        QToolTip.add(self.animate_views_checkbox,self.__tr("Enable/disable animation between current view and a new view"))
        self.textLabel1_5.setText(self.__tr("Speed :"))
        self.textLabel2_3.setText(self.__tr("Slow"))
        self.textLabel3_4.setText(self.__tr("Fast"))
        QToolTip.add(self.animation_speed_slider,self.__tr("View Animation Speed"))
        self.high_quality_graphics_checkbox.setText(self.__tr("High quality graphics"))
        self.prefs_tab.changeTab(self.tab,self.__tr("General"))
        self.textLabel1_7.setText(self.__tr("Level of Detail :"))
        QToolTip.add(self.textLabel1_7,self.__tr("Level of detail for atoms (and bonds)"))
        self.level_of_detail_combox.clear()
        self.level_of_detail_combox.insertItem(self.__tr("Low"))
        self.level_of_detail_combox.insertItem(self.__tr("Medium"))
        self.level_of_detail_combox.insertItem(self.__tr("High"))
        self.level_of_detail_combox.insertItem(self.__tr("Variable"))
        self.level_of_detail_combox.setCurrentItem(2)
        QToolTip.add(self.level_of_detail_combox,self.__tr("Sets graphics quality for atoms (and bonds)"))
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
        self.textLabel1_3_2.setText(self.__tr("Ball and Stick Atom Scale :"))
        QToolTip.add(self.textLabel1_3_2,self.__tr("Set Atom Scale factor for Ball and Stick display mode"))
        self.cpk_atom_rad_spinbox.setSuffix(self.__tr("%"))
        QToolTip.add(self.cpk_atom_rad_spinbox,self.__tr("Set Atom Scale factor for Ball and Stick display mode"))
        self.textLabel1_3_2_2.setText(self.__tr("CPK Atom Scale :"))
        QToolTip.add(self.textLabel1_3_2_2,self.__tr("CPK Atom Scale factor for CPK display mode"))
        QToolTip.add(self.cpk_scale_factor_linedit,self.__tr("Displays the value of the CPK Atom Scale"))
        QToolTip.add(self.cpk_scale_factor_slider,self.__tr("Changes Atom Scale factor for CPK display mode"))
        self.reset_cpk_scale_factor_btn.setText(QString.null)
        QToolTip.add(self.reset_cpk_scale_factor_btn,self.__tr("Restore default value"))
        self.prefs_tab.changeTab(self.TabPage,self.__tr("Atoms"))
        self.high_order_bond_display_btngrp.setTitle(self.__tr("High Order Bonds"))
        self.radioButton11.setText(self.__tr("Multiple Cylinders"))
        QToolTip.add(self.radioButton11,self.__tr("Display high order bonds using multiple cylinders"))
        self.radioButton11_2.setText(self.__tr("Vanes"))
        QToolTip.add(self.radioButton11_2,self.__tr("Display pi systems in high order bonds as Vanes"))
        self.radioButton11_2_2.setText(self.__tr("Ribbons"))
        QToolTip.add(self.radioButton11_2_2,self.__tr("Display pi systems in high order bonds as Ribbons"))
        self.show_bond_labels_checkbox.setText(self.__tr("Show Bond Type Letters"))
        QToolTip.add(self.show_bond_labels_checkbox,self.__tr("Display Bond Type Label"))
        self.show_valence_errors_checkbox.setText(self.__tr("Show Valence Errors"))
        QToolTip.add(self.show_valence_errors_checkbox,self.__tr("Enable/Disable Valence Error Checker"))
        self.groupBox4.setTitle(self.__tr("Colors"))
        self.reset_bond_colors_btn.setText(self.__tr("Restore Default Colors"))
        self.textLabel3_2.setText(self.__tr("Bond Highlighting :"))
        self.bond_stretch_color_btn.setText(self.__tr("Choose..."))
        self.bond_hilite_color_btn.setText(self.__tr("Choose..."))
        self.textLabel3_3.setText(self.__tr("Vane/Ribbon :"))
        self.ballstick_bondcolor_btn.setText(self.__tr("Choose..."))
        self.textLabel3.setText(self.__tr("Ball and Stick Cylinder :"))
        self.textLabel3_2_2.setText(self.__tr("Bond Stretch :"))
        self.bond_vane_color_btn.setText(self.__tr("Choose..."))
        self.textLabel1_3.setText(self.__tr("Ball and Stick Bond Scale :"))
        QToolTip.add(self.textLabel1_3,self.__tr("Set scale (size) factor for the cylinder representing bonds in Ball and Stick display mode"))
        self.textLabel1.setText(self.__tr("Bond Line Thickness :"))
        QToolTip.add(self.textLabel1,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.cpk_cylinder_rad_spinbox.setSuffix(self.__tr("%"))
        QToolTip.add(self.cpk_cylinder_rad_spinbox,self.__tr("Set scale (size) factor for the cylinder representing bonds in Ball and Stick display mode"))
        self.bond_line_thickness_spinbox.setSuffix(self.__tr(" pixel"))
        QToolTip.add(self.bond_line_thickness_spinbox,self.__tr("Bond thickness (in pixels) for Lines Display Mode"))
        self.prefs_tab.changeTab(self.TabPage_2,self.__tr("Bonds"))
        self.startup_mode_lbl.setText(self.__tr("Startup Mode :"))
        QToolTip.add(self.startup_mode_lbl,self.__tr("Startup Mode"))
        self.startup_mode_combox.clear()
        self.startup_mode_combox.insertItem(self.__tr("Default Mode"))
        self.startup_mode_combox.insertItem(self.__tr("Build"))
        QToolTip.add(self.startup_mode_combox,self.__tr("Startup Mode"))
        self.default_mode_lbl.setText(self.__tr("Default Mode :"))
        QToolTip.add(self.default_mode_lbl,self.__tr("Default Mode"))
        self.default_mode_combox.clear()
        self.default_mode_combox.insertItem(self.__tr("Select Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Move Chunks"))
        self.default_mode_combox.insertItem(self.__tr("Build"))
        QToolTip.add(self.default_mode_combox,self.__tr("Default Mode"))
        self.mode_groupbox.setTitle(self.__tr("Mode Settings"))
        self.mode_lbl.setText(self.__tr("Mode :"))
        self.display_mode_lbl.setText(self.__tr("Display Mode :"))
        self.mode_combox.clear()
        self.mode_combox.insertItem(self.__tr("Select Chunks"))
        self.mode_combox.insertItem(self.__tr("Move Chunks"))
        self.mode_combox.insertItem(self.__tr("Build"))
        self.mode_combox.insertItem(self.__tr("Cookie Cutter"))
        self.mode_combox.insertItem(self.__tr("Extrude"))
        self.mode_combox.insertItem(self.__tr("Fuse Chunks"))
        self.mode_combox.insertItem(self.__tr("Movie Player"))
        QToolTip.add(self.mode_combox,QString.null)
        self.display_mode_combox.clear()
        self.display_mode_combox.insertItem(self.__tr("Default"))
        self.display_mode_combox.insertItem(self.__tr("Invisible"))
        self.display_mode_combox.insertItem(self.__tr("CPK"))
        self.display_mode_combox.insertItem(self.__tr("Lines"))
        self.display_mode_combox.insertItem(self.__tr("Ball and Stick"))
        self.display_mode_combox.insertItem(self.__tr("Tubes"))
        QToolTip.add(self.display_mode_combox,self.__tr("Display Mode for this mode"))
        self.bg_groupbox.setTitle(self.__tr("Background Color"))
        self.fill_type_lbl.setText(self.__tr("Fill Type :"))
        self.bg1_color_lbl.setText(self.__tr("Color :"))
        self.fill_type_combox.clear()
        self.fill_type_combox.insertItem(self.__tr("Solid"))
        self.fill_type_combox.insertItem(self.__tr("Blue Sky"))
        QToolTip.add(self.fill_type_combox,self.__tr("Background fill type"))
        self.choose_bg1_color_btn.setText(self.__tr("Choose..."))
        self.restore_bgcolor_btn.setText(self.__tr("Restore Default Color"))
        self.default_display_btngrp.setTitle(self.__tr("Default Display Mode"))
        self.vwd_rbtn.setText(self.__tr("CPK"))
        QToolTip.add(self.vwd_rbtn,self.__tr("CPK (Space Filling) Display Mode"))
        self.cpk_rbtn.setText(self.__tr("Ball and Stick"))
        QToolTip.add(self.cpk_rbtn,self.__tr("Ball and Stick Display Mode"))
        self.lines_rbtn.setText(self.__tr("Lines"))
        QToolTip.add(self.lines_rbtn,self.__tr("Lines Display Mode"))
        self.tubes_rbtn.setText(self.__tr("Tubes"))
        QToolTip.add(self.tubes_rbtn,self.__tr("Tubes Display Mode"))
        self.buildmode_groupbox.setTitle(self.__tr("Build Mode Defaults"))
        self.autobond_checkbox.setText(self.__tr("Autobond"))
        QToolTip.add(self.autobond_checkbox,self.__tr("Build mode's default setting for Autobonding at startup (enabled/disabled)"))
        self.water_checkbox.setText(self.__tr("Water"))
        QToolTip.add(self.water_checkbox,self.__tr("Build mode's default setting for Water at startup (enabled/disabled)"))
        self.buildmode_select_atoms_checkbox.setText(self.__tr("Select Atoms of Deposited Object"))
        QToolTip.add(self.buildmode_select_atoms_checkbox,self.__tr("Automatically select atoms when depositing"))
        self.buildmode_highlighting_checkbox.setText(self.__tr("Highlighting"))
        QToolTip.add(self.buildmode_highlighting_checkbox,self.__tr("Build mode's default setting for Highlighting at startup (enabled/disabled)"))
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
        self.povray_path_linedit.setText(QString.null)
        QToolTip.add(self.povray_path_linedit,self.__tr("The full path to the POV-Ray executable file."))
        self.nanohive_path_linedit.setText(QString.null)
        QToolTip.add(self.nanohive_path_linedit,self.__tr("The full path to the Nano-Hive executable file."))
        self.megapov_path_linedit.setText(QString.null)
        QToolTip.add(self.megapov_path_linedit,self.__tr("The full path to the MegaPOV executable file (megapov.exe)."))
        self.gamess_path_linedit.setText(QString.null)
        QToolTip.add(self.gamess_path_linedit,self.__tr("The gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
        self.povray_choose_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.povray_choose_btn,self.__tr("Choose POV-Ray executable"))
        self.megapov_choose_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.megapov_choose_btn,self.__tr("Choose MegaPOV executable (megapov.exe)"))
        self.povdir_choose_btn.setText(self.__tr("Choose..."))
        self.gamess_choose_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.gamess_choose_btn,self.__tr("Choose GAMESS executable"))
        QToolTip.add(self.povdir_linedit,self.__tr("Select custom POV include directory"))
        self.nanohive_choose_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.nanohive_choose_btn,self.__tr("Choose location of Nano-Hive executable "))
        self.nanohive_checkbox.setText(QString.null)
        QToolTip.add(self.nanohive_checkbox,self.__tr("Enable Nano-Hive."))
        self.nanohive_lbl.setText(self.__tr("Nano-Hive :"))
        QToolTip.add(self.nanohive_lbl,self.__tr("Enable Nano-Hive."))
        self.povray_checkbox.setText(QString.null)
        QToolTip.add(self.povray_checkbox,self.__tr("Enable POV-Ray"))
        self.povray_lbl.setText(self.__tr("POV-Ray :"))
        QToolTip.add(self.povray_lbl,self.__tr("Enable POV-Ray"))
        self.megapov_checkbox.setText(QString.null)
        QToolTip.add(self.megapov_checkbox,self.__tr("Enable MegaPOV"))
        self.megapov_lbl.setText(self.__tr("MegaPOV :"))
        QToolTip.add(self.megapov_lbl,self.__tr("Enable MegaPOV"))
        self.povdir_checkbox.setText(QString.null)
        QToolTip.add(self.povdir_checkbox,self.__tr("User-custom directory for POV libraries"))
        self.povdir_lbl.setText(self.__tr("POV-Ray include dir :"))
        self.gamess_checkbox.setText(QString.null)
        QToolTip.add(self.gamess_checkbox,self.__tr("Enable GAMESS."))
        self.gamess_lbl.setText(self.__tr("GAMESS :"))
        QToolTip.add(self.gamess_lbl,self.__tr("Enable GAMESS."))
        self.prefs_tab.changeTab(self.TabPage_5,self.__tr("Plug-ins"))
        self.groupBox17.setTitle(self.__tr("History Preferences"))
        self.msg_serial_number_checkbox.setText(self.__tr("Include message serial number"))
        self.msg_timestamp_checkbox.setText(self.__tr("Include message timestamp"))
        self.undo_automatic_checkpoints_checkbox.setText(self.__tr("Automatic Checkpoints"))
        QToolTip.add(self.undo_automatic_checkpoints_checkbox,self.__tr("Specify Automatic or Manual Checkpoints at program startup."))
        self.undo_stack_memory_limit_spinbox.setSuffix(self.__tr(" MB"))
        self.undo_restore_view_checkbox.setText(self.__tr("Restore View when Undoing Structural Changes"))
        QToolTip.add(self.undo_restore_view_checkbox,self.__tr("Undo will switch to the view saved with each structural change."))
        self.undo_stack_memory_limit_label.setText(self.__tr("Undo Stack Memory Limit :"))
        self.prefs_tab.changeTab(self.TabPage_6,self.__tr("Undo"))
        self.groupBox3.setTitle(self.__tr("Window Caption Format"))
        QToolTip.add(self.groupBox3,self.__tr("Window Border Caption Format"))
        self.textLabel2.setText(self.__tr("Caption Prefix for Modified File :"))
        self.textLabel2_2.setText(self.__tr("Caption Suffix for Modified File :"))
        self.caption_suffix_linedit.setText(QString.null)
        self.caption_fullpath_checkbox.setText(self.__tr("Display full path of part"))
        self.groupBox10.setTitle(self.__tr("Window Position and Size"))
        self.textLabel1_2.setText(self.__tr("Current Size :"))
        self.textLabel1_2_2.setText(self.__tr("Saved Size :"))
        self.save_current_btn.setText(self.__tr("Save Current Size"))
        QToolTip.add(self.save_current_btn,self.__tr("Save current window position and size for next startup"))
        self.restore_saved_size_btn.setText(self.__tr("Restore Saved Size"))
        QToolTip.add(self.restore_saved_size_btn,self.__tr("Save current window position and size for next startup"))
        self.current_width_spinbox.setSuffix(self.__tr(" pixels"))
        self.current_height_spinbox.setSuffix(self.__tr(" pixels"))
        self.textLabel1_2_2_2.setText(self.__tr("x"))
        self.textLabel1_2_2_2_2.setText(self.__tr("x"))
        self.remember_win_pos_and_size_checkbox.setText(self.__tr("Always save current window position and size when quitting"))
        self.prefs_tab.changeTab(self.TabPage_7,self.__tr("Window"))


    def display_compass(self):
        print "UserPrefsDialog.display_compass(): Not implemented yet"

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

    def change_ballstick_bondcolor(self):
        print "UserPrefsDialog.change_ballstick_bondcolor(): Not implemented yet"

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

    def change_ballstick_atom_radius(self):
        print "UserPrefsDialog.change_ballstick_atom_radius(): Not implemented yet"

    def change_ballstick_cylinder_radius(self):
        print "UserPrefsDialog.change_ballstick_cylinder_radius(): Not implemented yet"

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

    def save_current_win_pos_and_size(self):
        print "UserPrefsDialog.save_current_win_pos_and_size(): Not implemented yet"

    def change_view_animation_speed(self):
        print "UserPrefsDialog.change_view_animation_speed(): Not implemented yet"

    def change_element_colors(self):
        print "UserPrefsDialog.change_element_colors(): Not implemented yet"

    def change_bondpoint_hilite_color(self):
        print "UserPrefsDialog.change_bondpoint_hilite_color(): Not implemented yet"

    def change_level_of_detail(self):
        print "UserPrefsDialog.change_level_of_detail(): Not implemented yet"

    def change_display_mode(self):
        print "UserPrefsDialog.change_display_mode(): Not implemented yet"

    def change_cpk_scale_factor(self):
        print "UserPrefsDialog.change_cpk_scale_factor(): Not implemented yet"

    def save_cpk_scale_factor(self):
        print "UserPrefsDialog.save_cpk_scale_factor(): Not implemented yet"

    def reset_cpk_scale_factor(self):
        print "UserPrefsDialog.reset_cpk_scale_factor(): Not implemented yet"

    def change_undo_restore_view(self):
        print "UserPrefsDialog.change_undo_restore_view(): Not implemented yet"

    def change_undo_automatic_checkpointing(self):
        print "UserPrefsDialog.change_undo_automatic_checkpointing(): Not implemented yet"

    def change_undo_stack_memory_limit(self):
        print "UserPrefsDialog.change_undo_stack_memory_limit(): Not implemented yet"

    def change_window_size(self):
        print "UserPrefsDialog.change_window_size(): Not implemented yet"

    def restore_saved_size(self):
        print "UserPrefsDialog.restore_saved_size(): Not implemented yet"

    def enable_povray(self):
        print "UserPrefsDialog.enable_povray(): Not implemented yet"

    def set_povray_path(self):
        print "UserPrefsDialog.set_povray_path(): Not implemented yet"

    def change_endrms(self):
        print "UserPrefsDialog.change_endrms(): Not implemented yet"

    def change_endmax(self):
        print "UserPrefsDialog.change_endmax(): Not implemented yet"

    def change_cutoverrms(self):
        print "UserPrefsDialog.change_cutoverrms(): Not implemented yet"

    def change_cutovermax(self):
        print "UserPrefsDialog.change_cutovermax(): Not implemented yet"

    def update_number_spinbox_valueChanged(self,a0):
        print "UserPrefsDialog.update_number_spinbox_valueChanged(int): Not implemented yet"

    def enable_megapov(self):
        print "UserPrefsDialog.enable_megapov(): Not implemented yet"

    def set_megapov_path(self):
        print "UserPrefsDialog.set_megapov_path(): Not implemented yet"

    def enable_povdir(self):
        print "UserPrefsDialog.enable_povdir(): Not implemented yet"

    def set_povdir(self):
        print "UserPrefsDialog.set_povdir(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("UserPrefsDialog",s,c)
