# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\ESPImagePropDialog.ui'
#
# Created: Thu Feb 9 08:50:05 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xf8\x49\x44\x41\x54\x78\x9c\xad\x54\xcb\x0e\xc2" \
    "\x20\x10\x1c\x8c\x07\x7f\xa4\x47\x9a\x1e\x4d\xf4" \
    "\x3f\xfc\x0b\xff\xcb\xff\xa0\x89\x47\xc2\x1e\x89" \
    "\xf1\xe8\xdd\xbb\xd1\x83\x01\x97\x65\xa9\xaf\x4e" \
    "\xd2\xa4\x40\x67\x98\xee\x2c\x00\x33\xc3\xf0\xc1" \
    "\x66\xe8\xee\xff\x0a\x2e\xfe\x15\x90\x58\x7e\x4b" \
    "\x70\x3e\xe6\xf7\xed\xd0\x55\xeb\x4d\x87\xce\xc7" \
    "\xfc\x7c\x22\x9e\x90\x6b\xc8\xeb\x37\x25\x02\x00" \
    "\xbd\xb5\x00\x80\x40\x54\x38\x1d\x7d\x34\xd5\x2f" \
    "\x27\x31\x49\xe2\x73\xfb\xe3\xe1\x39\x5e\xef\x8a" \
    "\x75\xa0\x51\xc3\xde\xda\x82\x94\x10\x88\xb2\xe8" \
    "\xe5\x74\x56\xdd\x4f\x86\x92\x48\xdc\x45\x20\xca" \
    "\x9b\x04\xa2\x2a\x18\x55\x50\x92\x80\x57\x9d\x9c" \
    "\x8f\x85\x53\x89\x2a\x65\xbe\xa3\x26\xc6\xc7\xcd" \
    "\xb6\x91\x27\x84\x13\x34\xd2\xf5\xb6\xaa\xc2\x18" \
    "\x7d\x34\xaa\x43\xe7\xa3\x4a\x90\xe9\xf3\x39\x8e" \
    "\xa2\x86\xfc\x83\xde\x5a\x04\x5f\x8a\xca\xf4\xe5" \
    "\xa6\x95\xe0\x14\x89\x3b\x6b\xb5\x8c\x2a\x28\x49" \
    "\xb2\xc1\x65\xfa\x6f\x05\xb5\x96\x91\xeb\x09\x5a" \
    "\x60\x46\x26\x2c\x0b\x2d\x49\xda\x6d\x93\x12\x56" \
    "\x05\x7f\x01\x17\x9c\xfd\x82\x7d\x00\xba\x58\x94" \
    "\x46\x0a\xda\xa4\x2b\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"
image1_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x02" \
    "\xcb\x49\x44\x41\x54\x78\x9c\xb5\x94\xcd\x4b\x54" \
    "\x51\x18\xc6\x7f\xe7\x8e\x7f\x84\xa0\xa8\x61\x2d" \
    "\x9c\x55\x20\xb4\x10\xd7\x86\x31\x2e\x5a\xd9\x14" \
    "\xb8\x90\x1a\x17\xb6\x18\xb0\x1c\x32\x27\x07\x24" \
    "\x02\xc1\xb0\x48\x71\x66\xa2\x68\x20\x45\x84\x40" \
    "\x9d\xc6\x46\x37\x21\x56\xe0\x2a\x18\xd0\x85\x1f" \
    "\xa3\x0b\x6d\x19\x08\xf7\x5e\xe7\x9e\x13\xa7\xc5" \
    "\x7c\x30\xe3\x4c\xe3\x07\x74\xe0\xe5\x70\x2e\x9c" \
    "\xe7\x79\xde\xdf\xbd\xf7\x15\x5a\x6b\xfe\xc7\x32" \
    "\x4e\x3f\x10\x42\x84\x85\x10\xba\x42\x85\x2f\xa4" \
    "\xac\xb5\x2e\x29\x40\xcf\xcf\xcf\x6b\x40\x03\x3a" \
    "\xbe\x3b\xae\xc7\x66\xef\x17\xce\x40\xf8\xf4\x9d" \
    "\x4a\x55\x51\x58\x29\xa5\xa5\x94\x7a\x6e\x6e\xae" \
    "\xaa\x41\x35\xb3\x8a\xc2\x96\x65\x69\xd3\x34\xb5" \
    "\x69\x9a\xda\xb2\x2c\x3d\x33\x33\x53\xd1\xa0\x5a" \
    "\x37\x42\x6b\x4d\x8e\x9f\x2f\x8f\x27\x16\x8b\xd1" \
    "\xd5\xd5\x55\xcc\x1d\x21\x04\x0b\x0b\x0b\xf4\xf4" \
    "\xf4\x00\x10\xdf\x1d\x2f\x41\xba\xb9\xb1\xc5\xa0" \
    "\xf7\x6d\xfe\x18\xc9\x0b\xeb\x50\xf8\x2e\xc2\x10" \
    "\x8c\x3c\xf8\x08\x40\x34\x1a\xc5\xe3\xf1\x9c\x7e" \
    "\xb1\x18\x86\x41\x3c\x1e\xa7\xb7\xb7\x17\x80\xb1" \
    "\xd9\xfb\xb8\x6f\xb4\x94\x19\x14\x84\x83\x93\x77" \
    "\xb8\x76\xbd\x19\x61\x18\xec\xa5\xf6\xf8\xfc\x3e" \
    "\xc1\xc6\x8f\xdf\x4c\x4d\x4d\xd1\xd9\xd9\x59\x66" \
    "\xe0\x72\xb9\x58\x5e\x5e\xc6\xe7\xf3\x95\x19\x78" \
    "\x9a\x07\x4a\x51\xbc\xfb\x1a\x40\x18\x06\x86\x21" \
    "\x30\x5c\x06\xbb\xa9\x34\x21\x5f\xb6\x83\x89\x89" \
    "\x09\x3a\x3a\x3a\xca\x0c\x6a\x6a\x6a\x58\x59\x59" \
    "\xa1\xbf\xbf\xbf\x80\xc8\xd3\x3c\x90\xfd\x8e\xb5" \
    "\xd6\x7d\x00\xdb\x3f\xb7\x51\x52\xa2\xa4\x42\x3a" \
    "\x8a\x2b\xee\x46\x62\xdf\x87\x09\x85\xef\xe2\xf7" \
    "\xfb\x71\xbb\xdd\x2c\x2d\x2d\x61\xdb\x36\xb6\x6d" \
    "\x63\x59\x16\xc7\xc7\xc7\xb4\xb5\xb5\xb1\xba\xba" \
    "\x5a\x62\x5a\xfc\x83\x44\x5e\xf8\x3f\xa1\x32\x59" \
    "\xd1\x3f\x52\x22\x1d\x85\x92\x92\x26\x77\x13\xb1" \
    "\x6f\x4f\x09\x4d\x7b\x09\x04\x02\xb4\xb6\xb6\x92" \
    "\x48\x24\x0a\x06\xa6\x69\x72\x74\x74\x54\x59\x38" \
    "\x9f\x7a\x27\xb5\x87\x72\x1c\xa4\xf3\x07\xe9\xc8" \
    "\x9c\x51\xb6\x8b\x46\x77\x13\x1f\xd6\x87\x08\x4d" \
    "\x7b\x09\x06\x83\xb4\xb7\xb7\x93\x4c\x26\xb1\x6d" \
    "\x9b\x4c\x26\xf3\xcf\xc4\x00\x91\xf1\xc0\x22\x32" \
    "\xa3\x90\x8e\x83\x72\x24\x52\xaa\xec\xee\xc8\x02" \
    "\xa6\x86\x96\x46\x3e\xac\x0f\x31\x32\xed\x65\x74" \
    "\x74\xf4\x6c\xe1\x7c\xea\xf4\xd6\x3e\x32\x93\x43" \
    "\x91\xdb\x65\x46\x95\x61\x6a\x6c\x69\x00\xc0\xb6" \
    "\x6d\x4e\x4e\x4e\xaa\x26\x06\x88\xbc\x0e\x7e\xe1" \
    "\x51\x77\x94\xfd\xcd\x34\x8e\xcc\xa6\x95\x52\xe2" \
    "\x38\xb2\x0c\x13\xc0\xda\xda\xda\x99\x28\xd0\x5a" \
    "\xf7\x69\xad\x05\x10\x79\xfd\x2c\xc9\xe3\xee\x28" \
    "\x07\x9b\xd9\x0e\x94\x23\xcb\x30\x05\x5e\xde\x66" \
    "\x72\x72\xf2\x6c\xe1\x8a\x06\x23\x49\x06\xbd\x6f" \
    "\x49\x6f\x1e\x64\xd3\x17\x61\xaa\x6b\xae\x03\x20" \
    "\x95\x4a\x95\xdc\x17\xe7\x1d\xf4\xc5\xf3\xe4\x61" \
    "\xe8\x26\x0d\xd7\xea\x10\x35\x2e\x0c\xc3\xe0\x70" \
    "\xe7\x90\x97\x4f\xe2\xc0\xa9\x1f\xe4\x3c\xab\xb8" \
    "\x83\x37\xa1\x24\x83\xf7\xde\xb1\xba\x98\x46\x65" \
    "\x24\xb5\x4d\xb5\xf8\x9f\xdf\xba\x5c\xe2\x6a\x1d" \
    "\xf4\x8f\x74\x50\x7f\xb5\x1e\x97\x4b\x70\xb8\xf7" \
    "\x8b\x57\xc3\x89\xf2\x79\x7c\xd1\xa2\x74\xe0\x17" \
    "\xe6\xf2\xa5\x13\x9f\xb5\xfe\x02\xaa\xf1\x6e\xe3" \
    "\xc8\x04\x53\x40\x00\x00\x00\x00\x49\x45\x4e\x44" \
    "\xae\x42\x60\x82"

class ESPImagePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG")
        if not name:
            self.setName("ESPImagePropDialog")

        self.setIcon(self.image0)

        ESPImagePropDialogLayout = QGridLayout(self,1,1,11,6,"ESPImagePropDialogLayout")

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

        ESPImagePropDialogLayout.addWidget(self.groupBox1,1,0)

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

        ESPImagePropDialogLayout.addLayout(layout30,4,0)
        spacer5 = QSpacerItem(101,20,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        ESPImagePropDialogLayout.addItem(spacer5,3,0)

        self.groupBox5 = QGroupBox(self,"groupBox5")
        self.groupBox5.setColumnLayout(0,Qt.Vertical)
        self.groupBox5.layout().setSpacing(6)
        self.groupBox5.layout().setMargin(11)
        groupBox5Layout = QGridLayout(self.groupBox5.layout())
        groupBox5Layout.setAlignment(Qt.AlignTop)

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.calculate_esp_btn = QPushButton(self.groupBox5,"calculate_esp_btn")
        self.calculate_esp_btn.setAutoDefault(0)
        layout15.addWidget(self.calculate_esp_btn)

        self.textLabel1_6 = QLabel(self.groupBox5,"textLabel1_6")
        layout15.addWidget(self.textLabel1_6)

        self.xaxis_spinbox = QSpinBox(self.groupBox5,"xaxis_spinbox")
        self.xaxis_spinbox.setMaxValue(1)
        self.xaxis_spinbox.setMinValue(-1)
        layout15.addWidget(self.xaxis_spinbox)

        groupBox5Layout.addLayout(layout15,0,0)

        layout17 = QHBoxLayout(None,0,6,"layout17")

        self.load_btn = QToolButton(self.groupBox5,"load_btn")
        layout17.addWidget(self.load_btn)

        self.clear_btn = QToolButton(self.groupBox5,"clear_btn")
        layout17.addWidget(self.clear_btn)

        self.textLabel1_6_2 = QLabel(self.groupBox5,"textLabel1_6_2")
        layout17.addWidget(self.textLabel1_6_2)

        self.yaxis_spinbox = QSpinBox(self.groupBox5,"yaxis_spinbox")
        self.yaxis_spinbox.setMaxValue(1)
        self.yaxis_spinbox.setMinValue(-1)
        self.yaxis_spinbox.setValue(0)
        layout17.addWidget(self.yaxis_spinbox)

        groupBox5Layout.addLayout(layout17,1,0)

        layout18 = QHBoxLayout(None,0,6,"layout18")

        self.png_fname_linedit = QLineEdit(self.groupBox5,"png_fname_linedit")
        self.png_fname_linedit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.png_fname_linedit.sizePolicy().hasHeightForWidth()))
        self.png_fname_linedit.setReadOnly(0)
        layout18.addWidget(self.png_fname_linedit)

        self.choose_file_btn = QToolButton(self.groupBox5,"choose_file_btn")
        self.choose_file_btn.setIconSet(QIconSet(self.image1))
        layout18.addWidget(self.choose_file_btn)

        groupBox5Layout.addLayout(layout18,2,0)

        layout19 = QHBoxLayout(None,0,6,"layout19")

        self.rotate_ccw_btn = QToolButton(self.groupBox5,"rotate_ccw_btn")
        layout19.addWidget(self.rotate_ccw_btn)

        self.rotate_cw_btn = QToolButton(self.groupBox5,"rotate_cw_btn")
        layout19.addWidget(self.rotate_cw_btn)

        self.flip_btn = QToolButton(self.groupBox5,"flip_btn")
        layout19.addWidget(self.flip_btn)

        self.mirror_btn = QToolButton(self.groupBox5,"mirror_btn")
        layout19.addWidget(self.mirror_btn)
        spacer29 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout19.addItem(spacer29)

        groupBox5Layout.addLayout(layout19,3,0)

        ESPImagePropDialogLayout.addWidget(self.groupBox5,2,0)

        layout20 = QHBoxLayout(None,0,6,"layout20")

        layout17_2 = QVBoxLayout(None,0,6,"layout17_2")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1_4)

        self.colorTextLabel_3 = QLabel(self,"colorTextLabel_3")
        self.colorTextLabel_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QLabel(self,"colorTextLabel_4")
        self.colorTextLabel_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1_3)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1_5)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1_2)

        self.textLabel1_2_2 = QLabel(self,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout17_2.addWidget(self.textLabel1_2_2)
        layout20.addLayout(layout17_2)

        layout19_2 = QVBoxLayout(None,0,6,"layout19_2")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        self.name_linedit.setAlignment(QLineEdit.AlignLeft)
        layout19_2.addWidget(self.name_linedit)

        layout18_2 = QHBoxLayout(None,0,6,"layout18_2")

        layout17_3 = QVBoxLayout(None,0,6,"layout17_3")

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
        layout17_3.addLayout(layout48)

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
        layout17_3.addLayout(layout47)

        layout16 = QHBoxLayout(None,0,6,"layout16")

        self.width_linedit = QLineEdit(self,"width_linedit")
        self.width_linedit.setMaximumSize(QSize(80,32767))
        layout16.addWidget(self.width_linedit)

        self.textLabel2 = QLabel(self,"textLabel2")
        layout16.addWidget(self.textLabel2)
        spacer18 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout16.addItem(spacer18)
        layout17_3.addLayout(layout16)

        layout15_2 = QHBoxLayout(None,0,6,"layout15_2")

        self.image_offset_linedit = QLineEdit(self,"image_offset_linedit")
        self.image_offset_linedit.setMaximumSize(QSize(80,32767))
        layout15_2.addWidget(self.image_offset_linedit)

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        layout15_2.addWidget(self.textLabel2_2)
        spacer18_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout15_2.addItem(spacer18_2)
        layout17_3.addLayout(layout15_2)

        layout14 = QHBoxLayout(None,0,6,"layout14")

        self.edge_offset_linedit = QLineEdit(self,"edge_offset_linedit")
        self.edge_offset_linedit.setMaximumSize(QSize(80,32767))
        layout14.addWidget(self.edge_offset_linedit)

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        layout14.addWidget(self.textLabel2_3)
        spacer18_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout14.addItem(spacer18_3)
        layout17_3.addLayout(layout14)

        layout13 = QHBoxLayout(None,0,6,"layout13")

        self.resolution_spinbox = QSpinBox(self,"resolution_spinbox")
        self.resolution_spinbox.setMaxValue(512)
        self.resolution_spinbox.setMinValue(1)
        self.resolution_spinbox.setValue(20)
        layout13.addWidget(self.resolution_spinbox)
        spacer16 = QSpacerItem(95,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addItem(spacer16)
        layout17_3.addLayout(layout13)

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
        layout17_3.addLayout(layout83)
        layout18_2.addLayout(layout17_3)
        spacer19 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout18_2.addItem(spacer19)
        layout19_2.addLayout(layout18_2)
        layout20.addLayout(layout19_2)

        ESPImagePropDialogLayout.addLayout(layout20,0,0)

        self.languageChange()

        self.resize(QSize(291,605).expandedTo(self.minimumSizeHint()))
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
        self.connect(self.image_offset_linedit,SIGNAL("returnPressed()"),self.change_jig_size)

        self.setTabOrder(self.name_linedit,self.choose_fill_color_btn)
        self.setTabOrder(self.choose_fill_color_btn,self.choose_border_color_btn)
        self.setTabOrder(self.choose_border_color_btn,self.resolution_spinbox)
        self.setTabOrder(self.resolution_spinbox,self.show_esp_bbox_checkbox)
        self.setTabOrder(self.show_esp_bbox_checkbox,self.highlight_atoms_in_bbox_checkbox)
        self.setTabOrder(self.highlight_atoms_in_bbox_checkbox,self.select_atoms_btn)
        self.setTabOrder(self.select_atoms_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("ESP Image Properties"))
        self.groupBox1.setTitle(self.__tr("ESP Image Bounding Box"))
        self.show_esp_bbox_checkbox.setText(self.__tr("Show Bounding Box"))
        self.highlight_atoms_in_bbox_checkbox.setText(self.__tr("Highlight Atoms Inside Bounding Box"))
        self.select_atoms_btn.setText(self.__tr("Select Atoms Inside Volume"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))
        self.groupBox5.setTitle(self.__tr("ESP Results Image"))
        self.calculate_esp_btn.setText(self.__tr("Calculate ESP"))
        self.textLabel1_6.setText(self.__tr("xaxisOrient :"))
        self.load_btn.setText(self.__tr("Load"))
        self.clear_btn.setText(self.__tr("Clear"))
        self.textLabel1_6_2.setText(self.__tr("yaxisOrient :"))
        self.choose_file_btn.setText(QString.null)
        self.rotate_ccw_btn.setText(self.__tr("+90"))
        QToolTip.add(self.rotate_ccw_btn,self.__tr("Rotate  90 degrees counter clock-wisely."))
        self.rotate_cw_btn.setText(self.__tr("-90"))
        QToolTip.add(self.rotate_cw_btn,self.__tr("Rotate  90 degrees clock-wisely."))
        self.flip_btn.setText(self.__tr("Flip"))
        QToolTip.add(self.flip_btn,self.__tr("Flip the image vertically (top to bottom)."))
        self.mirror_btn.setText(self.__tr("Mirror"))
        QToolTip.add(self.mirror_btn,self.__tr("Flip image horizontally (left to right)."))
        self.textLabel1_4.setText(self.__tr("Name :"))
        self.colorTextLabel_3.setText(self.__tr("Fill Color :"))
        self.colorTextLabel_4.setText(self.__tr("Border Color :"))
        self.textLabel1.setText(self.__tr("Width :"))
        self.textLabel1_3.setText(self.__tr("Height Offset :"))
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
        print "ESPImagePropDialog.change_fill_color(): Not implemented yet"

    def change_border_color(self):
        print "ESPImagePropDialog.change_border_color(): Not implemented yet"

    def show_esp_bbox(self):
        print "ESPImagePropDialog.show_esp_bbox(): Not implemented yet"

    def select_atoms_inside_esp_bbox(self):
        print "ESPImagePropDialog.select_atoms_inside_esp_bbox(): Not implemented yet"

    def highlight_atoms_in_bbox(self):
        print "ESPImagePropDialog.highlight_atoms_in_bbox(): Not implemented yet"

    def change_opacity(self):
        print "ESPImagePropDialog.change_opacity(): Not implemented yet"

    def change_esp_image(self):
        print "ESPImagePropDialog.change_esp_image(): Not implemented yet"

    def rotate_90(self):
        print "ESPImagePropDialog.rotate_90(): Not implemented yet"

    def rotate_neg_90(self):
        print "ESPImagePropDialog.rotate_neg_90(): Not implemented yet"

    def flip_esp_image(self):
        print "ESPImagePropDialog.flip_esp_image(): Not implemented yet"

    def mirror_esp_image(self):
        print "ESPImagePropDialog.mirror_esp_image(): Not implemented yet"

    def load_esp_image(self):
        print "ESPImagePropDialog.load_esp_image(): Not implemented yet"

    def clear_esp_image(self):
        print "ESPImagePropDialog.clear_esp_image(): Not implemented yet"

    def calculate_esp(self):
        print "ESPImagePropDialog.calculate_esp(): Not implemented yet"

    def change_yaxisOrient(self):
        print "ESPImagePropDialog.change_yaxisOrient(): Not implemented yet"

    def change_xaxisOrient(self):
        print "ESPImagePropDialog.change_xaxisOrient(): Not implemented yet"

    def change_jig_size(self):
        print "ESPImagePropDialog.change_jig_size(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ESPImagePropDialog",s,c)
