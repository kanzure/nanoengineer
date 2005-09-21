# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\GridPlanePropDialog.ui'
#
# Created: Tue Sep 20 23:33:44 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xb9\x49\x44\x41\x54\x78\x9c\x63\xfc\xff\xff\x3f" \
    "\x03\x35\x01\x0b\x32\xc7\xc6\x50\x8d\x72\xd3\xff" \
    "\xff\xff\x0f\xc7\xd6\x06\xaa\xff\x91\x41\x47\x9a" \
    "\x0b\x49\x7c\x6b\x03\xd5\xff\x4c\x14\xbb\x08\x0d" \
    "\xc0\x0d\xb4\x36\x54\xad\x47\x96\x38\xba\x65\x31" \
    "\x83\xac\x9a\x1e\xd1\xfc\x79\x33\x27\xa3\x7a\x99" \
    "\x1a\xde\xfd\xff\xff\x3f\x03\x23\x2c\x96\x6d\x0c" \
    "\xd5\xfe\xfb\x9a\xc9\x93\xed\xd5\xcd\xa7\x1e\x32" \
    "\x1c\x39\x7f\x8b\x91\xea\x2e\xa4\x5d\xa4\x20\x83" \
    "\xa3\x5b\x16\x93\xc4\x87\x47\x08\x03\x03\x24\x0c" \
    "\xad\x0d\x55\xeb\x19\x19\x18\x1b\xc8\x0d\xc3\x5b" \
    "\x4f\x3f\x32\xdc\x7c\xfa\x01\x11\x86\xd4\x0a\x3f" \
    "\xfa\x85\x21\x25\x80\xf1\xff\xff\xff\xd4\x4b\x83" \
    "\x0c\x0c\x0c\xd4\x0f\x43\xaa\xe5\x61\x18\xa0\xa6" \
    "\xeb\x68\x12\xcb\x8c\xd6\x06\xaa\x14\x97\xd2\xf0" \
    "\x08\x61\x60\x60\x00\x00\x4b\x6b\xd5\x9c\x69\xe0" \
    "\x02\x97\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"

class GridPlanePropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("GridPlanePropDialog")

        self.setIcon(self.image0)

        GridPlanePropDialogLayout = QGridLayout(self,1,1,11,6,"GridPlanePropDialogLayout")

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout26 = QVBoxLayout(None,0,6,"layout26")

        self.textLabel1_4 = QLabel(self,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel1_4)

        self.textLabel1_5 = QLabel(self,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel1_5)

        self.colorTextLabel_3 = QLabel(self,"colorTextLabel_3")
        self.colorTextLabel_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QLabel(self,"colorTextLabel_4")
        self.colorTextLabel_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel1)

        self.textLabel1_3 = QLabel(self,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel1_3)

        self.textLabel2_3 = QLabel(self,"textLabel2_3")
        self.textLabel2_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel2_3)

        self.textLabel2_3_2 = QLabel(self,"textLabel2_3_2")
        self.textLabel2_3_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel2_3_2)
        layout27.addLayout(layout26)

        layout25 = QVBoxLayout(None,0,6,"layout25")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        self.name_linedit.setAlignment(QLineEdit.AlignLeft)
        layout25.addWidget(self.name_linedit)

        layout24 = QHBoxLayout(None,0,6,"layout24")

        layout23 = QVBoxLayout(None,0,6,"layout23")

        layout20 = QHBoxLayout(None,0,6,"layout20")

        self.grid_type_combox = QComboBox(0,self,"grid_type_combox")
        layout20.addWidget(self.grid_type_combox)
        spacer12 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout20.addItem(spacer12)
        layout23.addLayout(layout20)

        layout48 = QHBoxLayout(None,0,6,"layout48")

        self.grid_color_pixmap = QLabel(self,"grid_color_pixmap")
        self.grid_color_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.grid_color_pixmap.sizePolicy().hasHeightForWidth()))
        self.grid_color_pixmap.setMinimumSize(QSize(40,0))
        self.grid_color_pixmap.setPaletteBackgroundColor(QColor(230,231,230))
        self.grid_color_pixmap.setFrameShape(QLabel.Box)
        self.grid_color_pixmap.setFrameShadow(QLabel.Plain)
        self.grid_color_pixmap.setScaledContents(1)
        layout48.addWidget(self.grid_color_pixmap)

        self.choose_grid_color_btn = QPushButton(self,"choose_grid_color_btn")
        self.choose_grid_color_btn.setEnabled(1)
        layout48.addWidget(self.choose_grid_color_btn)
        spacer14 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout48.addItem(spacer14)
        layout23.addLayout(layout48)

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
        layout23.addLayout(layout47)

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
        layout23.addLayout(layout46)

        layout46_2 = QHBoxLayout(None,0,6,"layout46_2")

        self.height_spinbox = QSpinBox(self,"height_spinbox")
        self.height_spinbox.setMaxValue(999)
        self.height_spinbox.setMinValue(1)
        self.height_spinbox.setValue(10)
        layout46_2.addWidget(self.height_spinbox)

        self.textLabel2_2 = QLabel(self,"textLabel2_2")
        layout46_2.addWidget(self.textLabel2_2)
        spacer18_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_2.addItem(spacer18_2)
        layout23.addLayout(layout46_2)

        layout46_2_2 = QHBoxLayout(None,0,6,"layout46_2_2")

        self.x_spacing_spinbox = QSpinBox(self,"x_spacing_spinbox")
        self.x_spacing_spinbox.setMaxValue(99)
        self.x_spacing_spinbox.setMinValue(1)
        self.x_spacing_spinbox.setValue(1)
        layout46_2_2.addWidget(self.x_spacing_spinbox)

        self.textLabel2_2_2 = QLabel(self,"textLabel2_2_2")
        layout46_2_2.addWidget(self.textLabel2_2_2)
        spacer18_2_2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_2_2.addItem(spacer18_2_2)
        layout23.addLayout(layout46_2_2)

        layout46_2_3 = QHBoxLayout(None,0,6,"layout46_2_3")

        self.y_spacing_spinbox = QSpinBox(self,"y_spacing_spinbox")
        self.y_spacing_spinbox.setMaxValue(99)
        self.y_spacing_spinbox.setMinValue(1)
        self.y_spacing_spinbox.setValue(1)
        layout46_2_3.addWidget(self.y_spacing_spinbox)

        self.textLabel2_2_3 = QLabel(self,"textLabel2_2_3")
        layout46_2_3.addWidget(self.textLabel2_2_3)
        spacer18_2_3 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout46_2_3.addItem(spacer18_2_3)
        layout23.addLayout(layout46_2_3)
        layout24.addLayout(layout23)
        spacer19 = QSpacerItem(22,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout24.addItem(spacer19)
        layout25.addLayout(layout24)
        layout27.addLayout(layout25)

        GridPlanePropDialogLayout.addLayout(layout27,0,0)
        spacer5 = QSpacerItem(101,16,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        GridPlanePropDialogLayout.addItem(spacer5,1,0)

        layout30 = QHBoxLayout(None,0,6,"layout30")
        spacer1 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30.addItem(spacer1)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,30))
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout30.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,30))
        self.cancel_btn.setAutoDefault(1)
        layout30.addWidget(self.cancel_btn)

        GridPlanePropDialogLayout.addLayout(layout30,2,0)

        self.languageChange()

        self.resize(QSize(265,322).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.choose_border_color_btn,SIGNAL("clicked()"),self.change_border_color)
        self.connect(self.choose_grid_color_btn,SIGNAL("clicked()"),self.change_grid_color)
        self.connect(self.width_spinbox,SIGNAL("valueChanged(int)"),self.change_width)
        self.connect(self.height_spinbox,SIGNAL("valueChanged(int)"),self.change_height)
        self.connect(self.x_spacing_spinbox,SIGNAL("valueChanged(int)"),self.change_x_spacing)
        self.connect(self.y_spacing_spinbox,SIGNAL("valueChanged(int)"),self.change_y_spacing)
        self.connect(self.grid_type_combox,SIGNAL("activated(const QString&)"),self.change_grid_type)


    def languageChange(self):
        self.setCaption(self.__tr("Grid Plane Properties"))
        self.textLabel1_4.setText(self.__tr("Name :"))
        self.textLabel1_5.setText(self.__tr("Grid Type :"))
        self.colorTextLabel_3.setText(self.__tr("Grid Color :"))
        self.colorTextLabel_4.setText(self.__tr("Border Color :"))
        self.textLabel1.setText(self.__tr("Width :"))
        self.textLabel1_3.setText(self.__tr("Height :"))
        self.textLabel2_3.setText(self.__tr("X Spacing :"))
        self.textLabel2_3_2.setText(self.__tr("Y Spacing :"))
        self.name_linedit.setText(QString.null)
        self.grid_type_combox.clear()
        self.grid_type_combox.insertItem(self.__tr("Square"))
        self.grid_type_combox.insertItem(self.__tr("SiC"))
        self.choose_grid_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_grid_color_btn,self.__tr("Change color"))
        self.choose_border_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_border_color_btn,self.__tr("Change color"))
        self.textLabel2.setText(self.__tr("Angstroms"))
        self.textLabel2_2.setText(self.__tr("Angstroms"))
        self.textLabel2_2_2.setText(self.__tr("Angstroms"))
        self.textLabel2_2_3.setText(self.__tr("Angstroms"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def change_grid_color(self):
        print "GridPlanePropDialog.change_grid_color(): Not implemented yet"

    def change_border_color(self):
        print "GridPlanePropDialog.change_border_color(): Not implemented yet"

    def change_width(self):
        print "GridPlanePropDialog.change_width(): Not implemented yet"

    def change_height(self):
        print "GridPlanePropDialog.change_height(): Not implemented yet"

    def change_x_spacing(self):
        print "GridPlanePropDialog.change_x_spacing(): Not implemented yet"

    def change_y_spacing(self):
        print "GridPlanePropDialog.change_y_spacing(): Not implemented yet"

    def change_grid_type(self):
        print "GridPlanePropDialog.change_grid_type(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GridPlanePropDialog",s,c)
