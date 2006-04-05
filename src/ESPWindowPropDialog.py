# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ESPWindowPropDialog.ui'
#
# Created: Tue Oct 11 17:46:51 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x01" \
    "\x3c\x49\x44\x41\x54\x78\x9c\xad\x93\x3d\x6e\xc3" \
    "\x30\x0c\x85\x9f\x0b\x4f\xde\x93\x1b\x64\xa4\x91" \
    "\x2d\x46\x3d\x66\xee\xdc\x5b\x74\x8d\x8f\xa0\xac" \
    "\xb9\x43\x87\xce\x3d\x43\x8a\x8e\x85\x38\x06\x45" \
    "\xc7\x02\xf6\xae\x55\x1d\x54\xa9\x92\xa8\x3a\xfd" \
    "\x09\x01\x01\x26\xe9\xf7\x91\x32\x69\xe0\xc2\x56" \
    "\xc5\x4e\xbf\x5e\xd9\xff\x02\xeb\x3c\x70\xf3\x74" \
    "\xfc\x33\xec\xf1\xba\x97\xc0\x73\xb6\x6b\x96\xe1" \
    "\x79\x6f\x46\x91\xbf\x9a\x13\xfa\xf3\x13\xb8\xb0" \
    "\x7e\xbd\xb2\xca\x8c\x56\x99\xd1\x5a\x60\xf6\x10" \
    "\x91\x25\xa2\xe0\x2b\x33\x5a\xff\xfd\xc5\x95\x7d" \
    "\xd5\x96\x08\x00\xa0\x99\x43\xce\xc7\xee\x9e\x1f" \
    "\x9c\xdf\xdd\x26\xf9\x22\xd0\x0b\x63\x91\x37\xcd" \
    "\x1c\xa0\xef\xaf\x6f\xc5\x9b\xce\x0e\xc5\x8b\xe2" \
    "\x2e\x34\x73\x28\xa2\x99\xc5\x60\x8a\xc0\x5c\x04" \
    "\x7c\x4d\x74\xd7\x2c\x93\x4e\x73\x13\x53\x8e\x2b" \
    "\xe6\xb0\xa1\x59\xa0\x82\x45\xf5\xf9\x43\x94\xd6" \
    "\xa6\x06\xdc\x84\xe3\x85\xde\x9b\x11\xd8\x6c\x8b" \
    "\x02\x00\x20\x22\xcb\xac\x01\x4c\x00\xdc\x42\x1f" \
    "\x5f\x4e\x55\xb1\xc3\xa1\x59\xe0\x7e\xb3\x85\x13" \
    "\xa4\x71\x07\x6b\x45\x4c\x74\x58\x7a\x81\xa8\xc5" \
    "\xd0\xa4\x50\xa2\x36\x4c\xff\xd0\xb5\xa2\xa8\x00" \
    "\xce\x89\xe2\xce\xbe\x5b\x99\x22\x30\x17\x79\x90" \
    "\x07\x1f\xba\xd4\x3f\x0b\x64\xd6\xb3\xa2\x38\xa6" \
    "\xcc\x24\xf2\x55\x3e\xe1\xfc\x43\xe7\xa2\x38\xaf" \
    "\xcc\x94\x4c\xb8\xd8\x61\xa9\xea\x6f\xf2\x35\xe0" \
    "\xf6\xe8\x52\xf6\x01\x33\x11\xb3\xd2\x11\x6b\xc7" \
    "\xb7\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60" \
    "\x82"

class ESPWindowPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("ESPWindowPropDialog")

        self.setIcon(self.image0)

        ESPWindowPropDialogLayout = QGridLayout(self,1,1,11,6,"ESPWindowPropDialogLayout")

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QVBoxLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.show_esp_bbox_checkbox = QCheckBox(self.groupBox1,"show_esp_bbox_checkbox")
        self.show_esp_bbox_checkbox.setChecked(1)
        groupBox1Layout.addWidget(self.show_esp_bbox_checkbox)

        self.highlight_atoms_in_bbox_checkbox = QCheckBox(self.groupBox1,"highlight_atoms_in_bbox_checkbox")
        self.highlight_atoms_in_bbox_checkbox.setChecked(0)
        groupBox1Layout.addWidget(self.highlight_atoms_in_bbox_checkbox)

        self.select_atoms_btn = QPushButton(self.groupBox1,"select_atoms_btn")
        self.select_atoms_btn.setAutoDefault(0)
        groupBox1Layout.addWidget(self.select_atoms_btn)

        ESPWindowPropDialogLayout.addWidget(self.groupBox1,1,0)

        layout30 = QHBoxLayout(None,0,6,"layout30")
        spacer1 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30.addItem(spacer1)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,30))
        self.ok_btn.setAutoDefault(0)
        self.ok_btn.setDefault(0)
        layout30.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,30))
        self.cancel_btn.setAutoDefault(0)
        layout30.addWidget(self.cancel_btn)

        ESPWindowPropDialogLayout.addLayout(layout30,4,0)
        spacer5 = QSpacerItem(101,20,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        ESPWindowPropDialogLayout.addItem(spacer5,3,0)

        self.groupBox5 = QGroupBox(self,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        self.choose_file_btn = QToolButton(self.groupBox5,"choose_file_btn")

        groupBox5Layout.addWidget(self.choose_file_btn,2,6)

        self.mirror_btn = QToolButton(self.groupBox5,"mirror_btn")

        groupBox5Layout.addWidget(self.mirror_btn,3,4)
        spacer29 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        groupBox5Layout.addMultiCell(spacer29,3,3,5,6)

        self.rotate_ccw_btn = QToolButton(self.groupBox5,"rotate_ccw_btn")

        groupBox5Layout.addWidget(self.rotate_ccw_btn,3,0)

        self.png_fname_linedit = QLineEdit(self.groupBox5,"png_fname_linedit")
        self.png_fname_linedit.setReadOnly(0)

        groupBox5Layout.addMultiCellWidget(self.png_fname_linedit,2,2,0,5)

        self.rotate_cw_btn = QToolButton(self.groupBox5,"rotate_cw_btn")

        groupBox5Layout.addMultiCellWidget(self.rotate_cw_btn,3,3,1,2)

        self.flip_btn = QToolButton(self.groupBox5,"flip_btn")

        groupBox5Layout.addWidget(self.flip_btn,3,3)

        self.calculate_esp_btn = QPushButton(self.groupBox5,"calculate_esp_btn")
        self.calculate_esp_btn.setAutoDefault(0)

        groupBox5Layout.addMultiCellWidget(self.calculate_esp_btn,0,0,0,3)

        self.clear_btn = QToolButton(self.groupBox5,"clear_btn")

        groupBox5Layout.addMultiCellWidget(self.clear_btn,1,1,2,3)

        self.load_btn = QToolButton(self.groupBox5,"load_btn")

        groupBox5Layout.addMultiCellWidget(self.load_btn,1,1,0,1)

        self.textLabel1_6 = QLabel(self.groupBox5,"textLabel1_6")

        groupBox5Layout.addMultiCellWidget(self.textLabel1_6,0,0,4,5)

        self.textLabel1_6_2 = QLabel(self.groupBox5,"textLabel1_6_2")

        groupBox5Layout.addMultiCellWidget(self.textLabel1_6_2,1,1,4,5)

        self.xaxis_spinbox = QSpinBox(self.groupBox5,"xaxis_spinbox")
        self.xaxis_spinbox.setMaxValue(1)
        self.xaxis_spinbox.setMinValue(-1)

        groupBox5Layout.addWidget(self.xaxis_spinbox,0,6)

        self.yaxis_spinbox = QSpinBox(self.groupBox5,"yaxis_spinbox")
        self.yaxis_spinbox.setMaxValue(1)
        self.yaxis_spinbox.setMinValue(-1)
        self.yaxis_spinbox.setValue(0)

        groupBox5Layout.addWidget(self.yaxis_spinbox,1,6)

        ESPWindowPropDialogLayout.addWidget(self.groupBox5,2,0)

        layout20 = QHBoxLayout(None,0,6,"layout20")

        layout17 = QVBoxLayout(None,0,6,"layout17")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1_4)

        self.colorTextLabel_3 = QLabel(self,"colorTextLabel_3")
        self.colorTextLabel_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QLabel(self,"colorTextLabel_4")
        self.colorTextLabel_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1_3)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1_5)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1_2)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17.addWidget(self.textLabel1_2_2)
        layout20.addLayout(layout17)

        layout19 = QVBoxLayout(None,0,6,"layout19")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        self.name_linedit.setAlignment(QLineEdit.AlignLeft)
        layout19.addWidget(self.name_linedit)

        layout18 = QHBoxLayout(None,0,6,"layout18")

        layout17_2 = QVBoxLayout(None,0,6,"layout17_2")

        layout48 = QHBoxLayout(None,0,6,"layout48")

        self.fill_color_pixmap = QLabel(self,"fill_color_pixmap")
        self.fill_color_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.fill_color_pixmap.sizePolicy().hasHeightForWidth()))
        self.fill_color_pixmap.setMinimumSize(QSize(40,0))
        self.fill_color_pixmap.setPaletteBackgroundColor(QColor(230,231,230))
        self.fill_color_pixmap.setFrameShape(QLabel.Box)
        self.fill_color_pixmap.setFrameShadow(QLabel.Plain)
        self.fill_color_pixmap.setScaledContents(1)
        layout48.addWidget(self.fill_color_pixmap)

        self.choose_fill_color_btn = QPushButton(self,"choose_fill_color_btn")
        self.choose_fill_color_btn.setEnabled(1)
        self.choose_fill_color_btn.setAutoDefault(0)
        layout48.addWidget(self.choose_fill_color_btn)
        spacer14 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout48.addItem(spacer14)
        layout17_2.addLayout(layout48)

        layout47 = QHBoxLayout(None,0,6,"layout47")

        self.border_color_pixmap = QLabel(self,"border_color_pixmap")
        self.border_color_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.border_color_pixmap.sizePolicy().hasHeightForWidth()))
        self.border_color_pixmap.setMinimumSize(QSize(40,0))
        self.border_color_pixmap.setPaletteBackgroundColor(QColor(230,231,230))
        self.border_color_pixmap.setFrameShape(QLabel.Box)
        self.border_color_pixmap.setFrameShadow(QLabel.Plain)
        self.border_color_pixmap.setScaledContents(1)
        layout47.addWidget(self.border_color_pixmap)

        self.choose_border_color_btn = QPushButton(self,"choose_border_color_btn")
        self.choose_border_color_btn.setEnabled(1)
        self.choose_border_color_btn.setAutoDefault(0)
        layout47.addWidget(self.choose_border_color_btn)
        spacer17 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout47.addItem(spacer17)
        layout17_2.addLayout(layout47)

        layout16 = QHBoxLayout(None,0,6,"layout16")

        self.width_linedit = QLineEdit(self,"width_linedit")
        self.width_linedit.setMaximumSize(QSize(80,32767))
        layout16.addWidget(self.width_linedit)

        self.textLabel2 = QLabel(self,"textLabel2")
        layout16.addWidget(self.textLabel2)
        spacer18 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout16.addItem(spacer18)
        layout17_2.addLayout(layout16)

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.window_offset_linedit = QLineEdit(self,"window_offset_linedit")
        self.window_offset_linedit.setMaximumSize(QSize(80,32767))
        layout15.addWidget(self.window_offset_linedit)

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        layout15.addWidget(self.textLabel2_2)
        spacer18_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout15.addItem(spacer18_2)
        layout17_2.addLayout(layout15)

        layout14 = QHBoxLayout(None,0,6,"layout14")

        self.edge_offset_linedit = QLineEdit(self,"edge_offset_linedit")
        self.edge_offset_linedit.setMaximumSize(QSize(80,32767))
        layout14.addWidget(self.edge_offset_linedit)

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        layout14.addWidget(self.textLabel2_3)
        spacer18_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout14.addItem(spacer18_3)
        layout17_2.addLayout(layout14)

        layout13 = QHBoxLayout(None,0,6,"layout13")

        self.resolution_spinbox = QSpinBox(self,"resolution_spinbox")
        self.resolution_spinbox.setMaxValue(512)
        self.resolution_spinbox.setMinValue(1)
        self.resolution_spinbox.setValue(20)
        layout13.addWidget(self.resolution_spinbox)
        spacer16 = QSpacerItem(95,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addItem(spacer16)
        layout17_2.addLayout(layout13)

        layout83 = QHBoxLayout(None,0,6,"layout83")

        self.opacity_linedit = QLineEdit(self,"opacity_linedit")
        self.opacity_linedit.setMaximumSize(QSize(40,32767))
        self.opacity_linedit.setMaxLength(5)
        self.opacity_linedit.setReadOnly(1)
        layout83.addWidget(self.opacity_linedit)

        self.opacity_slider = QSlider(self,"opacity_slider")
        self.opacity_slider.setMaxValue(100)
        self.opacity_slider.setOrientation(QSlider.Horizontal)
        layout83.addWidget(self.opacity_slider)
        layout17_2.addLayout(layout83)
        layout18.addLayout(layout17_2)
        spacer19 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout18.addItem(spacer19)
        layout19.addLayout(layout18)
        layout20.addLayout(layout19)

        ESPWindowPropDialogLayout.addLayout(layout20,0,0)

        self.languageChange()

        self.resize(QSize(281,592).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.choose_border_color_btn,SIGNAL("clicked()"),self.change_border_color)
        self.connect(self.choose_fill_color_btn,SIGNAL("clicked()"),self.change_fill_color)
        self.connect(self.show_esp_bbox_checkbox,SIGNAL("toggled(bool)"),self.show_esp_bbox)
        self.connect(self.select_atoms_btn,SIGNAL("clicked()"),self.select_atoms_inside_esp_bbox)
        self.connect(self.highlight_atoms_in_bbox_checkbox,SIGNAL("toggled(bool)"),self.highlight_atoms_in_bbox)
        self.connect(self.calculate_esp_btn,SIGNAL("clicked()"),self.calculate_esp)
        self.connect(self.rotate_ccw_btn,SIGNAL("clicked()"),self.rotate_90)
        self.connect(self.rotate_cw_btn,SIGNAL("clicked()"),self.rotate_neg_90)
        self.connect(self.flip_btn,SIGNAL("clicked()"),self.flip_esp_image)
        self.connect(self.mirror_btn,SIGNAL("clicked()"),self.mirror_esp_image)
        self.connect(self.opacity_slider,SIGNAL("valueChanged(int)"),self.change_opacity)
        self.connect(self.choose_file_btn,SIGNAL("clicked()"),self.change_esp_image)
        self.connect(self.load_btn,SIGNAL("clicked()"),self.load_esp_image)
        self.connect(self.clear_btn,SIGNAL("clicked()"),self.clear_esp_image)
        self.connect(self.xaxis_spinbox,SIGNAL("valueChanged(int)"),self.change_xaxisOrient)
        self.connect(self.yaxis_spinbox,SIGNAL("valueChanged(int)"),self.change_yaxisOrient)
        self.connect(self.width_linedit,SIGNAL("returnPressed()"),self.change_jig_size)
        self.connect(self.edge_offset_linedit,SIGNAL("returnPressed()"),self.change_jig_size)
        self.connect(self.window_offset_linedit,SIGNAL("returnPressed()"),self.change_jig_size)

        self.setTabOrder(self.name_linedit,self.choose_fill_color_btn)
        self.setTabOrder(self.choose_fill_color_btn,self.choose_border_color_btn)
        self.setTabOrder(self.choose_border_color_btn,self.resolution_spinbox)
        self.setTabOrder(self.resolution_spinbox,self.show_esp_bbox_checkbox)
        self.setTabOrder(self.show_esp_bbox_checkbox,self.highlight_atoms_in_bbox_checkbox)
        self.setTabOrder(self.highlight_atoms_in_bbox_checkbox,self.select_atoms_btn)
        self.setTabOrder(self.select_atoms_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("ESP Window Properties"))
        self.groupBox1.setTitle(self.__tr("ESP Window Volume"))
        self.show_esp_bbox_checkbox.setText(self.__tr("Show Bounding Box of Volume"))
        self.highlight_atoms_in_bbox_checkbox.setText(self.__tr("Highlight Atoms Inside Volume"))
        self.select_atoms_btn.setText(self.__tr("Select Atoms Inside Volume"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))
        self.groupBox5.setTitle(self.__tr("ESP Results Image"))
        self.choose_file_btn.setText(self.__tr("..."))
        self.mirror_btn.setText(self.__tr("Mirror"))
        QToolTip.add(self.mirror_btn,self.__tr("Flip image horizontally (left to right)."))
        self.rotate_ccw_btn.setText(self.__tr("+90"))
        QToolTip.add(self.rotate_ccw_btn,self.__tr("Rotate  90 degrees counter clock-wisely."))
        self.rotate_cw_btn.setText(self.__tr("-90"))
        QToolTip.add(self.rotate_cw_btn,self.__tr("Rotate  90 degrees clock-wisely."))
        self.flip_btn.setText(self.__tr("Flip"))
        QToolTip.add(self.flip_btn,self.__tr("Flip the image vertically (top to bottom)."))
        self.calculate_esp_btn.setText(self.__tr("Calculate ESP"))
        self.clear_btn.setText(self.__tr("Clear"))
        self.load_btn.setText(self.__tr("Load"))
        self.textLabel1_6.setText(self.__tr("xaxisOrient :"))
        self.textLabel1_6_2.setText(self.__tr("yaxisOrient :"))
        self.textLabel1_4.setText(self.__tr("Name :"))
        self.colorTextLabel_3.setText(self.__tr("Fill Color :"))
        self.colorTextLabel_4.setText(self.__tr("Border Color :"))
        self.textLabel1.setText(self.__tr("Width :"))
        self.textLabel1_3.setText(self.__tr("Window Offset :"))
        self.textLabel1_5.setText(self.__tr("Edge Offset :"))
        self.textLabel1_2.setText(self.__tr("Resolution :"))
        self.textLabel1_2_2.setText(self.__tr("Opacity:"))
        self.name_linedit.setText(QString.null)
        self.choose_fill_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_fill_color_btn,self.__tr("Change color"))
        self.choose_border_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_border_color_btn,self.__tr("Change color"))
        self.textLabel2.setText(self.__tr("Angstroms"))
        self.textLabel2_2.setText(self.__tr("Angstroms"))
        self.textLabel2_3.setText(self.__tr("Angstroms"))


    def change_fill_color(self):
        print "ESPWindowPropDialog.change_fill_color(): Not implemented yet"

    def change_border_color(self):
        print "ESPWindowPropDialog.change_border_color(): Not implemented yet"

    def show_esp_bbox(self):
        print "ESPWindowPropDialog.show_esp_bbox(): Not implemented yet"

    def select_atoms_inside_esp_bbox(self):
        print "ESPWindowPropDialog.select_atoms_inside_esp_bbox(): Not implemented yet"

    def highlight_atoms_in_bbox(self):
        print "ESPWindowPropDialog.highlight_atoms_in_bbox(): Not implemented yet"

    def change_opacity(self):
        print "ESPWindowPropDialog.change_opacity(): Not implemented yet"

    def change_esp_image(self):
        print "ESPWindowPropDialog.change_esp_image(): Not implemented yet"

    def rotate_90(self):
        print "ESPWindowPropDialog.rotate_90(): Not implemented yet"

    def rotate_neg_90(self):
        print "ESPWindowPropDialog.rotate_neg_90(): Not implemented yet"

    def flip_esp_image(self):
        print "ESPWindowPropDialog.flip_esp_image(): Not implemented yet"

    def mirror_esp_image(self):
        print "ESPWindowPropDialog.mirror_esp_image(): Not implemented yet"

    def load_esp_image(self):
        print "ESPWindowPropDialog.load_esp_image(): Not implemented yet"

    def clear_esp_image(self):
        print "ESPWindowPropDialog.clear_esp_image(): Not implemented yet"

    def calculate_esp(self):
        print "ESPWindowPropDialog.calculate_esp(): Not implemented yet"

    def change_yaxisOrient(self):
        print "ESPWindowPropDialog.change_yaxisOrient(): Not implemented yet"

    def change_xaxisOrient(self):
        print "ESPWindowPropDialog.change_xaxisOrient(): Not implemented yet"

    def change_jig_size(self):
        print "ESPWindowPropDialog.change_jig_size(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ESPWindowPropDialog",s,c)
