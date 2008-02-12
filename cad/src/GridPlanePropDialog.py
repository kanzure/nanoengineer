# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GridPlanePropDialog.ui'
#
# Created: Tue Feb 12 00:08:03 2008
#      by: PyQt4 UI code generator 4.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_GridPlanePropDialog(object):
    def setupUi(self, GridPlanePropDialog):
        GridPlanePropDialog.setObjectName("GridPlanePropDialog")
        GridPlanePropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,265,374).size()).expandedTo(GridPlanePropDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(GridPlanePropDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        spacerItem = QtGui.QSpacerItem(101,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        self.gridlayout.addItem(spacerItem,1,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        spacerItem1 = QtGui.QSpacerItem(92,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout.addItem(spacerItem1)

        self.ok_btn = QtGui.QPushButton(GridPlanePropDialog)
        self.ok_btn.setMinimumSize(QtCore.QSize(0,30))
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout.addWidget(self.ok_btn)

        self.cancel_btn = QtGui.QPushButton(GridPlanePropDialog)
        self.cancel_btn.setMinimumSize(QtCore.QSize(0,30))
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout.addWidget(self.cancel_btn)
        self.gridlayout.addLayout(self.hboxlayout,2,0,1,1)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.textLabel1_4 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel1_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout.addWidget(self.textLabel1_4)

        self.textLabel1_5 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel1_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5.setObjectName("textLabel1_5")
        self.vboxlayout.addWidget(self.textLabel1_5)

        self.textLabel1_5_2 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel1_5_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_5_2.setObjectName("textLabel1_5_2")
        self.vboxlayout.addWidget(self.textLabel1_5_2)

        self.colorTextLabel_3 = QtGui.QLabel(GridPlanePropDialog)
        self.colorTextLabel_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_3.setObjectName("colorTextLabel_3")
        self.vboxlayout.addWidget(self.colorTextLabel_3)

        self.colorTextLabel_4 = QtGui.QLabel(GridPlanePropDialog)
        self.colorTextLabel_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.colorTextLabel_4.setObjectName("colorTextLabel_4")
        self.vboxlayout.addWidget(self.colorTextLabel_4)

        self.textLabel1 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1.setObjectName("textLabel1")
        self.vboxlayout.addWidget(self.textLabel1)

        self.textLabel1_3 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel1_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel1_3.setObjectName("textLabel1_3")
        self.vboxlayout.addWidget(self.textLabel1_3)

        self.textLabel2_3 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel2_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.vboxlayout.addWidget(self.textLabel2_3)

        self.textLabel2_3_2 = QtGui.QLabel(GridPlanePropDialog)
        self.textLabel2_3_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.textLabel2_3_2.setObjectName("textLabel2_3_2")
        self.vboxlayout.addWidget(self.textLabel2_3_2)
        self.hboxlayout1.addLayout(self.vboxlayout)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.name_linedit = QtGui.QLineEdit(GridPlanePropDialog)
        self.name_linedit.setAlignment(QtCore.Qt.AlignLeading)
        self.name_linedit.setObjectName("name_linedit")
        self.vboxlayout1.addWidget(self.name_linedit)

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.grid_type_combox = QtGui.QComboBox(GridPlanePropDialog)
        self.grid_type_combox.setObjectName("grid_type_combox")
        self.hboxlayout3.addWidget(self.grid_type_combox)

        spacerItem2 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem2)
        self.vboxlayout2.addLayout(self.hboxlayout3)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.line_type_combox = QtGui.QComboBox(GridPlanePropDialog)
        self.line_type_combox.setObjectName("line_type_combox")
        self.hboxlayout4.addWidget(self.line_type_combox)

        spacerItem3 = QtGui.QSpacerItem(40,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout4.addItem(spacerItem3)
        self.vboxlayout2.addLayout(self.hboxlayout4)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(0)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        self.grid_color_pixmap = QtGui.QLabel(GridPlanePropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grid_color_pixmap.sizePolicy().hasHeightForWidth())
        self.grid_color_pixmap.setSizePolicy(sizePolicy)
        self.grid_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.grid_color_pixmap.setFrameShape(QtGui.QFrame.Box)
        self.grid_color_pixmap.setFrameShadow(QtGui.QFrame.Plain)
        self.grid_color_pixmap.setScaledContents(True)
        self.grid_color_pixmap.setObjectName("grid_color_pixmap")
        self.hboxlayout5.addWidget(self.grid_color_pixmap)

        self.choose_grid_color_btn = QtGui.QPushButton(GridPlanePropDialog)
        self.choose_grid_color_btn.setEnabled(True)
        self.choose_grid_color_btn.setAutoDefault(False)
        self.choose_grid_color_btn.setObjectName("choose_grid_color_btn")
        self.hboxlayout5.addWidget(self.choose_grid_color_btn)

        spacerItem4 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem4)
        self.vboxlayout2.addLayout(self.hboxlayout5)

        self.hboxlayout6 = QtGui.QHBoxLayout()
        self.hboxlayout6.setMargin(0)
        self.hboxlayout6.setSpacing(6)
        self.hboxlayout6.setObjectName("hboxlayout6")

        self.border_color_pixmap = QtGui.QLabel(GridPlanePropDialog)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(5))
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.border_color_pixmap.sizePolicy().hasHeightForWidth())
        self.border_color_pixmap.setSizePolicy(sizePolicy)
        self.border_color_pixmap.setMinimumSize(QtCore.QSize(40,0))
        self.border_color_pixmap.setFrameShape(QtGui.QFrame.Box)
        self.border_color_pixmap.setFrameShadow(QtGui.QFrame.Plain)
        self.border_color_pixmap.setScaledContents(True)
        self.border_color_pixmap.setObjectName("border_color_pixmap")
        self.hboxlayout6.addWidget(self.border_color_pixmap)

        self.choose_border_color_btn = QtGui.QPushButton(GridPlanePropDialog)
        self.choose_border_color_btn.setEnabled(True)
        self.choose_border_color_btn.setAutoDefault(False)
        self.choose_border_color_btn.setObjectName("choose_border_color_btn")
        self.hboxlayout6.addWidget(self.choose_border_color_btn)

        spacerItem5 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout6.addItem(spacerItem5)
        self.vboxlayout2.addLayout(self.hboxlayout6)

        self.hboxlayout7 = QtGui.QHBoxLayout()
        self.hboxlayout7.setMargin(0)
        self.hboxlayout7.setSpacing(6)
        self.hboxlayout7.setObjectName("hboxlayout7")

        self.width_spinbox = QtGui.QSpinBox(GridPlanePropDialog)
        self.width_spinbox.setMaximum(9999)
        self.width_spinbox.setMinimum(5)
        self.width_spinbox.setSingleStep(10)
        self.width_spinbox.setProperty("value",QtCore.QVariant(20))
        self.width_spinbox.setObjectName("width_spinbox")
        self.hboxlayout7.addWidget(self.width_spinbox)

        spacerItem6 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout7.addItem(spacerItem6)
        self.vboxlayout2.addLayout(self.hboxlayout7)

        self.hboxlayout8 = QtGui.QHBoxLayout()
        self.hboxlayout8.setMargin(0)
        self.hboxlayout8.setSpacing(6)
        self.hboxlayout8.setObjectName("hboxlayout8")

        self.height_spinbox = QtGui.QSpinBox(GridPlanePropDialog)
        self.height_spinbox.setMaximum(9999)
        self.height_spinbox.setMinimum(5)
        self.height_spinbox.setSingleStep(10)
        self.height_spinbox.setProperty("value",QtCore.QVariant(20))
        self.height_spinbox.setObjectName("height_spinbox")
        self.hboxlayout8.addWidget(self.height_spinbox)

        spacerItem7 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout8.addItem(spacerItem7)
        self.vboxlayout2.addLayout(self.hboxlayout8)

        self.hboxlayout9 = QtGui.QHBoxLayout()
        self.hboxlayout9.setMargin(0)
        self.hboxlayout9.setSpacing(6)
        self.hboxlayout9.setObjectName("hboxlayout9")

        self.x_spacing_spinbox = QtGui.QSpinBox(GridPlanePropDialog)
        self.x_spacing_spinbox.setMaximum(1000)
        self.x_spacing_spinbox.setMinimum(1)
        self.x_spacing_spinbox.setSingleStep(5)
        self.x_spacing_spinbox.setProperty("value",QtCore.QVariant(1))
        self.x_spacing_spinbox.setObjectName("x_spacing_spinbox")
        self.hboxlayout9.addWidget(self.x_spacing_spinbox)

        spacerItem8 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout9.addItem(spacerItem8)
        self.vboxlayout2.addLayout(self.hboxlayout9)

        self.hboxlayout10 = QtGui.QHBoxLayout()
        self.hboxlayout10.setMargin(0)
        self.hboxlayout10.setSpacing(6)
        self.hboxlayout10.setObjectName("hboxlayout10")

        self.y_spacing_spinbox = QtGui.QSpinBox(GridPlanePropDialog)
        self.y_spacing_spinbox.setMaximum(1000)
        self.y_spacing_spinbox.setMinimum(1)
        self.y_spacing_spinbox.setSingleStep(5)
        self.y_spacing_spinbox.setProperty("value",QtCore.QVariant(1))
        self.y_spacing_spinbox.setObjectName("y_spacing_spinbox")
        self.hboxlayout10.addWidget(self.y_spacing_spinbox)

        spacerItem9 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout10.addItem(spacerItem9)
        self.vboxlayout2.addLayout(self.hboxlayout10)
        self.hboxlayout2.addLayout(self.vboxlayout2)

        spacerItem10 = QtGui.QSpacerItem(16,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem10)
        self.vboxlayout1.addLayout(self.hboxlayout2)
        self.hboxlayout1.addLayout(self.vboxlayout1)
        self.gridlayout.addLayout(self.hboxlayout1,0,0,1,1)

        self.retranslateUi(GridPlanePropDialog)
        self.line_type_combox.setCurrentIndex(1)
        QtCore.QObject.connect(self.ok_btn,QtCore.SIGNAL("clicked()"),GridPlanePropDialog.accept)
        QtCore.QObject.connect(self.cancel_btn,QtCore.SIGNAL("clicked()"),GridPlanePropDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(GridPlanePropDialog)
        GridPlanePropDialog.setTabOrder(self.name_linedit,self.grid_type_combox)
        GridPlanePropDialog.setTabOrder(self.grid_type_combox,self.line_type_combox)
        GridPlanePropDialog.setTabOrder(self.line_type_combox,self.choose_grid_color_btn)
        GridPlanePropDialog.setTabOrder(self.choose_grid_color_btn,self.choose_border_color_btn)
        GridPlanePropDialog.setTabOrder(self.choose_border_color_btn,self.width_spinbox)
        GridPlanePropDialog.setTabOrder(self.width_spinbox,self.height_spinbox)
        GridPlanePropDialog.setTabOrder(self.height_spinbox,self.x_spacing_spinbox)
        GridPlanePropDialog.setTabOrder(self.x_spacing_spinbox,self.y_spacing_spinbox)
        GridPlanePropDialog.setTabOrder(self.y_spacing_spinbox,self.ok_btn)
        GridPlanePropDialog.setTabOrder(self.ok_btn,self.cancel_btn)

    def retranslateUi(self, GridPlanePropDialog):
        GridPlanePropDialog.setWindowTitle(QtGui.QApplication.translate("GridPlanePropDialog", "Grid Plane Properties", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("GridPlanePropDialog", "&OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setShortcut(QtGui.QApplication.translate("GridPlanePropDialog", "Alt+O", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("GridPlanePropDialog", "&Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setShortcut(QtGui.QApplication.translate("GridPlanePropDialog", "Alt+C", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Name :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Grid Type :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_5_2.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Line Type :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_3.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Grid Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.colorTextLabel_4.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Border Color :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Width :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Height :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("GridPlanePropDialog", "X Spacing :", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3_2.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Y Spacing :", None, QtGui.QApplication.UnicodeUTF8))
        self.grid_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "Square", None, QtGui.QApplication.UnicodeUTF8))
        self.grid_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "SiC", None, QtGui.QApplication.UnicodeUTF8))
        self.line_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.line_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "Solid", None, QtGui.QApplication.UnicodeUTF8))
        self.line_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "Dashed", None, QtGui.QApplication.UnicodeUTF8))
        self.line_type_combox.addItem(QtGui.QApplication.translate("GridPlanePropDialog", "Dotted", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_grid_color_btn.setToolTip(QtGui.QApplication.translate("GridPlanePropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_grid_color_btn.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setToolTip(QtGui.QApplication.translate("GridPlanePropDialog", "Change color", None, QtGui.QApplication.UnicodeUTF8))
        self.choose_border_color_btn.setText(QtGui.QApplication.translate("GridPlanePropDialog", "Choose...", None, QtGui.QApplication.UnicodeUTF8))
        self.width_spinbox.setSuffix(QtGui.QApplication.translate("GridPlanePropDialog", " Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.height_spinbox.setSuffix(QtGui.QApplication.translate("GridPlanePropDialog", " Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.x_spacing_spinbox.setSuffix(QtGui.QApplication.translate("GridPlanePropDialog", " Angstroms", None, QtGui.QApplication.UnicodeUTF8))
        self.y_spacing_spinbox.setSuffix(QtGui.QApplication.translate("GridPlanePropDialog", " Angstroms", None, QtGui.QApplication.UnicodeUTF8))

