# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\ESPWindowPropDialog.ui'
#
# Created: Mon Sep 26 09:27:29 2005
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

        ESPWindowPropDialogLayout = QVBoxLayout(self,11,6,"ESPWindowPropDialogLayout")

        layout30 = QHBoxLayout(None,0,6,"layout30")

        layout29 = QVBoxLayout(None,0,6,"layout29")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_4)

        self.colorTextLabel_3 = QLabel(self,"colorTextLabel_3")
        self.colorTextLabel_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QLabel(self,"colorTextLabel_4")
        self.colorTextLabel_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_3)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_5)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_2)
        layout30.addLayout(layout29)

        layout28 = QVBoxLayout(None,0,6,"layout28")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        self.name_linedit.setAlignment(QLineEdit.AlignLeft)
        layout28.addWidget(self.name_linedit)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout26 = QVBoxLayout(None,0,6,"layout26")

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
        layout48.addWidget(self.choose_fill_color_btn)
        spacer14 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout48.addItem(spacer14)
        layout26.addLayout(layout48)

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
        layout47.addWidget(self.choose_border_color_btn)
        spacer17 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout47.addItem(spacer17)
        layout26.addLayout(layout47)

        layout46 = QHBoxLayout(None,0,6,"layout46")

        self.width_spinbox = QSpinBox(self,"width_spinbox")
        self.width_spinbox.setMaxValue(999)
        self.width_spinbox.setMinValue(1)
        self.width_spinbox.setValue(10)
        layout46.addWidget(self.width_spinbox)

        self.textLabel2 = QLabel(self,"textLabel2")
        layout46.addWidget(self.textLabel2)
        spacer18 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46.addItem(spacer18)
        layout26.addLayout(layout46)

        layout46_2 = QHBoxLayout(None,0,6,"layout46_2")

        self.window_offset_spinbox = QSpinBox(self,"window_offset_spinbox")
        self.window_offset_spinbox.setMaxValue(99)
        self.window_offset_spinbox.setMinValue(1)
        self.window_offset_spinbox.setValue(1)
        layout46_2.addWidget(self.window_offset_spinbox)

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        layout46_2.addWidget(self.textLabel2_2)
        spacer18_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_2.addItem(spacer18_2)
        layout26.addLayout(layout46_2)

        layout46_3 = QHBoxLayout(None,0,6,"layout46_3")

        self.edge_offset_spinbox = QSpinBox(self,"edge_offset_spinbox")
        self.edge_offset_spinbox.setMaxValue(99)
        self.edge_offset_spinbox.setMinValue(1)
        self.edge_offset_spinbox.setValue(1)
        layout46_3.addWidget(self.edge_offset_spinbox)

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        layout46_3.addWidget(self.textLabel2_3)
        spacer18_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_3.addItem(spacer18_3)
        layout26.addLayout(layout46_3)

        layout13 = QHBoxLayout(None,0,6,"layout13")

        self.resolution_spinbox = QSpinBox(self,"resolution_spinbox")
        self.resolution_spinbox.setMaxValue(999)
        self.resolution_spinbox.setMinValue(1)
        self.resolution_spinbox.setValue(20)
        layout13.addWidget(self.resolution_spinbox)
        spacer16 = QSpacerItem(95,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout13.addItem(spacer16)
        layout26.addLayout(layout13)
        layout27.addLayout(layout26)
        spacer19 = QSpacerItem(18,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout27.addItem(spacer19)
        layout28.addLayout(layout27)
        layout30.addLayout(layout28)
        ESPWindowPropDialogLayout.addLayout(layout30)

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QVBoxLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.show_esp_bbox_checkbox = QCheckBox(self.groupBox1,"show_esp_bbox_checkbox")
        self.show_esp_bbox_checkbox.setChecked(1)
        groupBox1Layout.addWidget(self.show_esp_bbox_checkbox)

        self.select_atoms_btn = QPushButton(self.groupBox1,"select_atoms_btn")
        groupBox1Layout.addWidget(self.select_atoms_btn)
        ESPWindowPropDialogLayout.addWidget(self.groupBox1)
        spacer5 = QSpacerItem(101,20,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        ESPWindowPropDialogLayout.addItem(spacer5)

        layout30_2 = QHBoxLayout(None,0,6,"layout30_2")
        spacer1 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30_2.addItem(spacer1)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,30))
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout30_2.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,30))
        self.cancel_btn.setAutoDefault(1)
        layout30_2.addWidget(self.cancel_btn)
        ESPWindowPropDialogLayout.addLayout(layout30_2)

        self.languageChange()

        self.resize(QSize(301,392).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.choose_border_color_btn,SIGNAL("clicked()"),self.change_border_color)
        self.connect(self.choose_fill_color_btn,SIGNAL("clicked()"),self.change_fill_color)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.connect(self.window_offset_spinbox,SIGNAL("valueChanged(int)"),self.change_window_offset)
        self.connect(self.edge_offset_spinbox,SIGNAL("valueChanged(int)"),self.change_edge_offset)
        self.connect(self.show_esp_bbox_checkbox,SIGNAL("toggled(bool)"),self.show_esp_bbox)
        self.connect(self.select_atoms_btn,SIGNAL("clicked()"),self.select_atoms_in_bbox)

        self.setTabOrder(self.name_linedit,self.choose_fill_color_btn)
        self.setTabOrder(self.choose_fill_color_btn,self.choose_border_color_btn)
        self.setTabOrder(self.choose_border_color_btn,self.width_spinbox)
        self.setTabOrder(self.width_spinbox,self.window_offset_spinbox)
        self.setTabOrder(self.window_offset_spinbox,self.edge_offset_spinbox)
        self.setTabOrder(self.edge_offset_spinbox,self.resolution_spinbox)
        self.setTabOrder(self.resolution_spinbox,self.show_esp_bbox_checkbox)
        self.setTabOrder(self.show_esp_bbox_checkbox,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("ESP Window Properties"))
        self.textLabel1_4.setText(self.__tr("Name :"))
        self.colorTextLabel_3.setText(self.__tr("Fill Color :"))
        self.colorTextLabel_4.setText(self.__tr("Border Color :"))
        self.textLabel1.setText(self.__tr("Width :"))
        self.textLabel1_3.setText(self.__tr("Window Offset :"))
        self.textLabel1_5.setText(self.__tr("Edge Offset :"))
        self.textLabel1_2.setText(self.__tr("Resolution :"))
        self.name_linedit.setText(QString.null)
        self.choose_fill_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_fill_color_btn,self.__tr("Change color"))
        self.choose_border_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_border_color_btn,self.__tr("Change color"))
        self.textLabel2.setText(self.__tr("Angstroms"))
        self.textLabel2_2.setText(self.__tr("Angstroms"))
        self.textLabel2_3.setText(self.__tr("Angstroms"))
        self.groupBox1.setTitle(self.__tr("ESP Window Volume"))
        self.show_esp_bbox_checkbox.setText(self.__tr("Show Bounding Box of Volume"))
        self.select_atoms_btn.setText(self.__tr("Select Atoms Inside Volume"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def change_fill_color(self):
        print "ESPWindowPropDialog.change_fill_color(): Not implemented yet"

    def change_border_color(self):
        print "ESPWindowPropDialog.change_border_color(): Not implemented yet"

    def change_width(self):
        print "ESPWindowPropDialog.change_width(): Not implemented yet"

    def change_window_offset(self):
        print "ESPWindowPropDialog.change_window_offset(): Not implemented yet"

    def change_edge_offset(self):
        print "ESPWindowPropDialog.change_edge_offset(): Not implemented yet"

    def show_esp_bbox(self):
        print "ESPWindowPropDialog.show_esp_bbox(): Not implemented yet"

    def select_atoms_in_bbox(self):
        print "ESPWindowPropDialog.select_atoms_in_bbox(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ESPWindowPropDialog",s,c)
