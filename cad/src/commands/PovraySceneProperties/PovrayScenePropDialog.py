# -*- coding: utf-8 -*-
# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PovrayScenePropDialog.py

Note: this file is not presently used in NE1 (as of before 080515).

@author: Mark
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

History:

This used to be made by pyuic from a .ui file,
but since then it has been hand-modified in ways
that are not possible to do using the .ui file
(though they might be doable in the subclass instead),
and the .ui file has been moved to a non-active name.
If this command is revived, either those changes need
abandoning or to be done in the subclass (if the .ui file
is also revived), or (preferably) the .ui file should be
removed and the UI rewritten to use the PM module.

The comment from pyuic claims that it was last created
from the .ui file on this date:
# Created: Wed Sep 27 14:24:15 2006
#      by: PyQt4 UI code generator 4.0.1
"""

from PyQt4 import QtCore, QtGui
from utilities.icon_utilities import geticon
#@from PM.PM_Constants import getHeaderFont
#@from PM.PM_Constants import pmLabelLeftAlignment

class Ui_PovrayScenePropDialog(object):
    def setupUi(self, PovrayScenePropDialog):
        PovrayScenePropDialog.setObjectName("PovrayScenePropDialog")
        PovrayScenePropDialog.resize(QtCore.QSize(QtCore.QRect(0,0,207,368).size()).expandedTo(PovrayScenePropDialog.minimumSizeHint()))

        self.vboxlayout = QtGui.QVBoxLayout(PovrayScenePropDialog)
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(0)
        self.vboxlayout.setObjectName("vboxlayout")

        self.heading_frame = QtGui.QFrame(PovrayScenePropDialog)
        self.heading_frame.setFrameShape(QtGui.QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QtGui.QFrame.Plain)
        self.heading_frame.setObjectName("heading_frame")

        self.hboxlayout = QtGui.QHBoxLayout(self.heading_frame)
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(3)
        self.hboxlayout.setObjectName("hboxlayout")

        self.heading_pixmap = QtGui.QLabel(self.heading_frame)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.heading_pixmap.sizePolicy().hasHeightForWidth())
        self.heading_pixmap.setSizePolicy(sizePolicy)
        self.heading_pixmap.setScaledContents(True)
        self.heading_pixmap.setAlignment(QtCore.Qt.AlignVCenter)
        self.heading_pixmap.setObjectName("heading_pixmap")
        self.hboxlayout.addWidget(self.heading_pixmap)

        self.heading_label = QtGui.QLabel(self.heading_frame)
        #@self.heading_label.setFont(getHeaderFont())
        #@self.heading_label.setAlignment(pmLabelLeftAlignment)
        self.hboxlayout.addWidget(self.heading_label)
        self.vboxlayout.addWidget(self.heading_frame)

        self.body_frame = QtGui.QFrame(PovrayScenePropDialog)
        self.body_frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QtGui.QFrame.Raised)
        self.body_frame.setObjectName("body_frame")

        self.vboxlayout1 = QtGui.QVBoxLayout(self.body_frame)
        self.vboxlayout1.setMargin(3)
        self.vboxlayout1.setSpacing(3)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.sponsor_btn = QtGui.QPushButton(self.body_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.sponsor_btn.setObjectName("sponsor_btn")
        self.vboxlayout1.addWidget(self.sponsor_btn)

        self.hboxlayout1 = QtGui.QHBoxLayout()
        self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName("hboxlayout1")

        spacerItem = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem)

        self.done_btn = QtGui.QToolButton(self.body_frame)
        self.done_btn.setIcon(
            geticon("ui/actions/Properties Manager/Done.png"))
        self.done_btn.setObjectName("done_btn")
        self.hboxlayout1.addWidget(self.done_btn)

        self.abort_btn = QtGui.QToolButton(self.body_frame)
        self.abort_btn.setIcon(
            geticon("ui/actions/Properties Manager/Abort.png"))
        self.abort_btn.setObjectName("abort_btn")
        self.hboxlayout1.addWidget(self.abort_btn)

        self.restore_btn = QtGui.QToolButton(self.body_frame)
        self.restore_btn.setIcon(
            geticon("ui/actions/Properties Manager/Restore.png"))
        self.restore_btn.setObjectName("restore_btn")
        self.hboxlayout1.addWidget(self.restore_btn)

        self.preview_btn = QtGui.QToolButton(self.body_frame)
        self.preview_btn.setIcon(
            geticon("ui/actions/Properties Manager/Preview.png"))
        self.preview_btn.setObjectName("preview_btn")
        self.hboxlayout1.addWidget(self.preview_btn)

        self.whatsthis_btn = QtGui.QToolButton(self.body_frame)
        self.whatsthis_btn.setIcon(
            geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatsthis_btn.setObjectName("whatsthis_btn")
        self.hboxlayout1.addWidget(self.whatsthis_btn)

        spacerItem1 = QtGui.QSpacerItem(35,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout1.addItem(spacerItem1)
        self.vboxlayout1.addLayout(self.hboxlayout1)

        self.name_grpbox = QtGui.QGroupBox(self.body_frame)
        self.name_grpbox.setObjectName("name_grpbox")

        self.vboxlayout2 = QtGui.QVBoxLayout(self.name_grpbox)
        self.vboxlayout2.setMargin(4)
        self.vboxlayout2.setSpacing(1)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.hboxlayout2 = QtGui.QHBoxLayout()
        self.hboxlayout2.setMargin(0)
        self.hboxlayout2.setSpacing(6)
        self.hboxlayout2.setObjectName("hboxlayout2")

        self.name_grpbox_label = QtGui.QLabel(self.name_grpbox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name_grpbox_label.sizePolicy().hasHeightForWidth())
        self.name_grpbox_label.setSizePolicy(sizePolicy)
        self.name_grpbox_label.setAlignment(QtCore.Qt.AlignVCenter)
        self.name_grpbox_label.setObjectName("name_grpbox_label")
        self.hboxlayout2.addWidget(self.name_grpbox_label)

        spacerItem2 = QtGui.QSpacerItem(67,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout2.addItem(spacerItem2)

        self.grpbtn_1 = QtGui.QPushButton(self.name_grpbox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_1.sizePolicy().hasHeightForWidth())
        self.grpbtn_1.setSizePolicy(sizePolicy)
        self.grpbtn_1.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_1.setIcon(
            geticon("ui/actions/Properties Manager/Group_Button.png"))
        self.grpbtn_1.setAutoDefault(False)
        self.grpbtn_1.setFlat(True)
        self.grpbtn_1.setObjectName("grpbtn_1")
        self.hboxlayout2.addWidget(self.grpbtn_1)
        self.vboxlayout2.addLayout(self.hboxlayout2)

        self.line2 = QtGui.QFrame(self.name_grpbox)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setMidLineWidth(0)
        self.line2.setFrameShape(QtGui.QFrame.HLine)
        self.line2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line2.setObjectName("line2")
        self.vboxlayout2.addWidget(self.line2)

        self.name_linedit = QtGui.QLineEdit(self.name_grpbox)
        self.name_linedit.setObjectName("name_linedit")
        self.vboxlayout2.addWidget(self.name_linedit)
        self.vboxlayout1.addWidget(self.name_grpbox)

        self.output_image_grpbox = QtGui.QGroupBox(self.body_frame)
        self.output_image_grpbox.setCheckable(False)
        self.output_image_grpbox.setChecked(False)
        self.output_image_grpbox.setObjectName("output_image_grpbox")

        self.vboxlayout3 = QtGui.QVBoxLayout(self.output_image_grpbox)
        self.vboxlayout3.setMargin(4)
        self.vboxlayout3.setSpacing(1)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.hboxlayout3 = QtGui.QHBoxLayout()
        self.hboxlayout3.setMargin(0)
        self.hboxlayout3.setSpacing(6)
        self.hboxlayout3.setObjectName("hboxlayout3")

        self.image_size_grpbox_label = QtGui.QLabel(self.output_image_grpbox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(5),QtGui.QSizePolicy.Policy(1))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_size_grpbox_label.sizePolicy().hasHeightForWidth())
        self.image_size_grpbox_label.setSizePolicy(sizePolicy)
        self.image_size_grpbox_label.setAlignment(QtCore.Qt.AlignVCenter)
        self.image_size_grpbox_label.setObjectName("image_size_grpbox_label")
        self.hboxlayout3.addWidget(self.image_size_grpbox_label)

        spacerItem3 = QtGui.QSpacerItem(40,16,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout3.addItem(spacerItem3)

        self.grpbtn_2 = QtGui.QPushButton(self.output_image_grpbox)

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Policy(0),QtGui.QSizePolicy.Policy(0))
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpbtn_2.sizePolicy().hasHeightForWidth())
        self.grpbtn_2.setSizePolicy(sizePolicy)
        self.grpbtn_2.setMaximumSize(QtCore.QSize(16,16))
        self.grpbtn_2.setIcon(
            geticon("ui/actions/Properties Manager/Group_Button.png"))
        self.grpbtn_2.setAutoDefault(False)
        self.grpbtn_2.setFlat(True)
        self.grpbtn_2.setObjectName("grpbtn_2")
        self.hboxlayout3.addWidget(self.grpbtn_2)
        self.vboxlayout3.addLayout(self.hboxlayout3)

        self.line3 = QtGui.QFrame(self.output_image_grpbox)
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setMidLineWidth(0)
        self.line3.setFrameShape(QtGui.QFrame.HLine)
        self.line3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line3.setObjectName("line3")
        self.vboxlayout3.addWidget(self.line3)

        self.hboxlayout4 = QtGui.QHBoxLayout()
        self.hboxlayout4.setMargin(0)
        self.hboxlayout4.setSpacing(6)
        self.hboxlayout4.setObjectName("hboxlayout4")

        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setMargin(0)
        self.vboxlayout4.setSpacing(6)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.output_type_label = QtGui.QLabel(self.output_image_grpbox)
        self.output_type_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.output_type_label.setObjectName("output_type_label")
        self.vboxlayout4.addWidget(self.output_type_label)

        self.width_label = QtGui.QLabel(self.output_image_grpbox)
        self.width_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.width_label.setObjectName("width_label")
        self.vboxlayout4.addWidget(self.width_label)

        self.height_label = QtGui.QLabel(self.output_image_grpbox)
        self.height_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.height_label.setObjectName("height_label")
        self.vboxlayout4.addWidget(self.height_label)

        self.aspect_ratio_label = QtGui.QLabel(self.output_image_grpbox)
        self.aspect_ratio_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.aspect_ratio_label.setObjectName("aspect_ratio_label")
        self.vboxlayout4.addWidget(self.aspect_ratio_label)
        self.hboxlayout4.addLayout(self.vboxlayout4)

        self.vboxlayout5 = QtGui.QVBoxLayout()
        self.vboxlayout5.setMargin(0)
        self.vboxlayout5.setSpacing(6)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.output_type_combox = QtGui.QComboBox(self.output_image_grpbox)
        self.output_type_combox.setObjectName("output_type_combox")
        self.vboxlayout5.addWidget(self.output_type_combox)

        self.width_spinbox = QtGui.QSpinBox(self.output_image_grpbox)
        self.width_spinbox.setMaximum(5000)
        self.width_spinbox.setMinimum(20)
        self.width_spinbox.setProperty("value",QtCore.QVariant(1024))
        self.width_spinbox.setObjectName("width_spinbox")
        self.vboxlayout5.addWidget(self.width_spinbox)

        self.height_spinbox = QtGui.QSpinBox(self.output_image_grpbox)
        self.height_spinbox.setMaximum(5000)
        self.height_spinbox.setMinimum(20)
        self.height_spinbox.setProperty("value",QtCore.QVariant(768))
        self.height_spinbox.setObjectName("height_spinbox")
        self.vboxlayout5.addWidget(self.height_spinbox)

        self.aspect_ratio_value_label = QtGui.QLabel(self.output_image_grpbox)
        self.aspect_ratio_value_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.aspect_ratio_value_label.setObjectName("aspect_ratio_value_label")
        self.vboxlayout5.addWidget(self.aspect_ratio_value_label)
        self.hboxlayout4.addLayout(self.vboxlayout5)
        self.vboxlayout3.addLayout(self.hboxlayout4)
        self.vboxlayout1.addWidget(self.output_image_grpbox)
        self.vboxlayout.addWidget(self.body_frame)

        spacerItem4 = QtGui.QSpacerItem(20,16,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.vboxlayout.addItem(spacerItem4)

        self.hboxlayout5 = QtGui.QHBoxLayout()
        self.hboxlayout5.setMargin(4)
        self.hboxlayout5.setSpacing(6)
        self.hboxlayout5.setObjectName("hboxlayout5")

        spacerItem5 = QtGui.QSpacerItem(59,20,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Minimum)
        self.hboxlayout5.addItem(spacerItem5)

        self.cancel_btn = QtGui.QPushButton(PovrayScenePropDialog)
        self.cancel_btn.setAutoDefault(False)
        self.cancel_btn.setObjectName("cancel_btn")
        self.hboxlayout5.addWidget(self.cancel_btn)

        self.ok_btn = QtGui.QPushButton(PovrayScenePropDialog)
        self.ok_btn.setAutoDefault(False)
        self.ok_btn.setObjectName("ok_btn")
        self.hboxlayout5.addWidget(self.ok_btn)
        self.vboxlayout.addLayout(self.hboxlayout5)

        self.retranslateUi(PovrayScenePropDialog)
        QtCore.QMetaObject.connectSlotsByName(PovrayScenePropDialog)

    def retranslateUi(self, PovrayScenePropDialog):
        PovrayScenePropDialog.setWindowTitle(QtGui.QApplication.translate("PovrayScenePropDialog", "POV-Ray Scene", None, QtGui.QApplication.UnicodeUTF8))
        PovrayScenePropDialog.setWindowIcon(QtGui.QIcon("ui/border/PovrayScene"))
        self.heading_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "POV-Ray Scene", None, QtGui.QApplication.UnicodeUTF8))
        self.done_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.abort_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.restore_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.preview_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Preview", None, QtGui.QApplication.UnicodeUTF8))
        self.whatsthis_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "What\'s This Help", None, QtGui.QApplication.UnicodeUTF8))
        self.name_grpbox_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "POV-Ray Scene Name", None, QtGui.QApplication.UnicodeUTF8))
        self.name_linedit.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Name of POV-Ray Scene node in Model Tree", None, QtGui.QApplication.UnicodeUTF8))
        self.name_linedit.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "POV-Ray Scene-1.pov", None, QtGui.QApplication.UnicodeUTF8))
        self.image_size_grpbox_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Render Image Parameters", None, QtGui.QApplication.UnicodeUTF8))
        self.output_type_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Output Type :", None, QtGui.QApplication.UnicodeUTF8))
        self.width_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Width :", None, QtGui.QApplication.UnicodeUTF8))
        self.height_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Height :", None, QtGui.QApplication.UnicodeUTF8))
        self.aspect_ratio_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Aspect Ratio :", None, QtGui.QApplication.UnicodeUTF8))
        self.output_type_combox.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Output image format", None, QtGui.QApplication.UnicodeUTF8))
        self.output_type_combox.addItem(QtGui.QApplication.translate("PovrayScenePropDialog", "PNG", None, QtGui.QApplication.UnicodeUTF8))
        self.output_type_combox.addItem(QtGui.QApplication.translate("PovrayScenePropDialog", "BMP", None, QtGui.QApplication.UnicodeUTF8))
        self.width_spinbox.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Width of output image", None, QtGui.QApplication.UnicodeUTF8))
        self.width_spinbox.setSuffix(QtGui.QApplication.translate("PovrayScenePropDialog", " pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.height_spinbox.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Height of output image", None, QtGui.QApplication.UnicodeUTF8))
        self.height_spinbox.setSuffix(QtGui.QApplication.translate("PovrayScenePropDialog", " pixels", None, QtGui.QApplication.UnicodeUTF8))
        self.aspect_ratio_value_label.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "1.333 to 1", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel_btn.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setToolTip(QtGui.QApplication.translate("PovrayScenePropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
        self.ok_btn.setText(QtGui.QApplication.translate("PovrayScenePropDialog", "OK", None, QtGui.QApplication.UnicodeUTF8))
