# -*- coding: utf-8 -*-

# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
# Form implementation generated from reading ui file 'LightingToolDialog.ui'
#
# Created: Wed Sep 20 10:27:48 2006
#      by: PyQt4 UI code generator 4.0.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_LightingToolDialog(object):
    def setupUi(self, LightingToolDialog):
        LightingToolDialog.setObjectName("LightingToolDialog")
        LightingToolDialog.resize(QtCore.QSize(QtCore.QRect(0,0,411,470).size()).expandedTo(LightingToolDialog.minimumSizeHint()))

        self.gridlayout = QtGui.QGridLayout(LightingToolDialog)
        self.gridlayout.setMargin(11)
        self.gridlayout.setSpacing(6)
        self.gridlayout.setObjectName("gridlayout")

        self.frame1_2 = QtGui.QFrame(LightingToolDialog)
        self.frame1_2.setFrameShape(QtGui.QFrame.Box)
        self.frame1_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame1_2.setMargin(0)
        self.frame1_2.setObjectName("frame1_2")

        self.gridlayout1 = QtGui.QGridLayout(self.frame1_2)
        self.gridlayout1.setMargin(11)
        self.gridlayout1.setSpacing(6)
        self.gridlayout1.setObjectName("gridlayout1")

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.setMargin(0)
        self.vboxlayout.setSpacing(6)
        self.vboxlayout.setObjectName("vboxlayout")

        self.light1CB = QtGui.QCheckBox(self.frame1_2)
        self.light1CB.setObjectName("light1CB")
        self.vboxlayout.addWidget(self.light1CB)

        self.gridlayout2 = QtGui.QGridLayout()
        self.gridlayout2.setMargin(0)
        self.gridlayout2.setSpacing(6)
        self.gridlayout2.setObjectName("gridlayout2")

        self.ambLight1LCD = QtGui.QLCDNumber(self.frame1_2)
        self.ambLight1LCD.setSmallDecimalPoint(False)
        self.ambLight1LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.ambLight1LCD.setProperty("value",QtCore.QVariant(1.0))
        self.ambLight1LCD.setProperty("intValue",QtCore.QVariant(1))
        self.ambLight1LCD.setObjectName("ambLight1LCD")
        self.gridlayout2.addWidget(self.ambLight1LCD,0,1,1,1)

        self.ambLight1SL = QtGui.QSlider(self.frame1_2)
        self.ambLight1SL.setMaximum(100)
        self.ambLight1SL.setSingleStep(1)
        self.ambLight1SL.setTickInterval(10)
        self.ambLight1SL.setObjectName("ambLight1SL")
        self.gridlayout2.addWidget(self.ambLight1SL,0,0,1,1)

        self.diffuseLight1SL = QtGui.QSlider(self.frame1_2)
        self.diffuseLight1SL.setMaximum(100)
        self.diffuseLight1SL.setSingleStep(1)
        self.diffuseLight1SL.setTickInterval(10)
        self.diffuseLight1SL.setObjectName("diffuseLight1SL")
        self.gridlayout2.addWidget(self.diffuseLight1SL,1,0,1,1)

        self.diffuseLight1LCD = QtGui.QLCDNumber(self.frame1_2)
        self.diffuseLight1LCD.setSmallDecimalPoint(False)
        self.diffuseLight1LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.diffuseLight1LCD.setProperty("value",QtCore.QVariant(1.0))
        self.diffuseLight1LCD.setProperty("intValue",QtCore.QVariant(1))
        self.diffuseLight1LCD.setObjectName("diffuseLight1LCD")
        self.gridlayout2.addWidget(self.diffuseLight1LCD,1,1,1,1)
        self.vboxlayout.addLayout(self.gridlayout2)
        self.gridlayout1.addLayout(self.vboxlayout,0,1,1,1)

        self.vboxlayout1 = QtGui.QVBoxLayout()
        self.vboxlayout1.setMargin(0)
        self.vboxlayout1.setSpacing(6)
        self.vboxlayout1.setObjectName("vboxlayout1")

        self.textLabel2_4 = QtGui.QLabel(self.frame1_2)
        self.textLabel2_4.setObjectName("textLabel2_4")
        self.vboxlayout1.addWidget(self.textLabel2_4)

        self.textLabel1_4 = QtGui.QLabel(self.frame1_2)
        self.textLabel1_4.setObjectName("textLabel1_4")
        self.vboxlayout1.addWidget(self.textLabel1_4)

        self.textLabel1_3_2 = QtGui.QLabel(self.frame1_2)
        self.textLabel1_3_2.setObjectName("textLabel1_3_2")
        self.vboxlayout1.addWidget(self.textLabel1_3_2)
        self.gridlayout1.addLayout(self.vboxlayout1,0,0,1,1)
        self.gridlayout.addWidget(self.frame1_2,0,0,1,1)

        self.frame5 = QtGui.QFrame(LightingToolDialog)
        self.frame5.setFrameShape(QtGui.QFrame.Box)
        self.frame5.setFrameShadow(QtGui.QFrame.Raised)
        self.frame5.setObjectName("frame5")

        self.gridlayout3 = QtGui.QGridLayout(self.frame5)
        self.gridlayout3.setMargin(11)
        self.gridlayout3.setSpacing(6)
        self.gridlayout3.setObjectName("gridlayout3")

        self.vboxlayout2 = QtGui.QVBoxLayout()
        self.vboxlayout2.setMargin(0)
        self.vboxlayout2.setSpacing(6)
        self.vboxlayout2.setObjectName("vboxlayout2")

        self.light2CB = QtGui.QCheckBox(self.frame5)
        self.light2CB.setObjectName("light2CB")
        self.vboxlayout2.addWidget(self.light2CB)

        self.gridlayout4 = QtGui.QGridLayout()
        self.gridlayout4.setMargin(0)
        self.gridlayout4.setSpacing(6)
        self.gridlayout4.setObjectName("gridlayout4")

        self.ambLight2SL = QtGui.QSlider(self.frame5)
        self.ambLight2SL.setMaximum(100)
        self.ambLight2SL.setSingleStep(1)
        self.ambLight2SL.setTickInterval(10)
        self.ambLight2SL.setObjectName("ambLight2SL")
        self.gridlayout4.addWidget(self.ambLight2SL,0,0,1,1)

        self.diffuseLight2LCD = QtGui.QLCDNumber(self.frame5)
        self.diffuseLight2LCD.setSmallDecimalPoint(False)
        self.diffuseLight2LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.diffuseLight2LCD.setProperty("value",QtCore.QVariant(1.0))
        self.diffuseLight2LCD.setProperty("intValue",QtCore.QVariant(1))
        self.diffuseLight2LCD.setObjectName("diffuseLight2LCD")
        self.gridlayout4.addWidget(self.diffuseLight2LCD,1,1,1,1)

        self.ambLight2LCD = QtGui.QLCDNumber(self.frame5)
        self.ambLight2LCD.setSmallDecimalPoint(False)
        self.ambLight2LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.ambLight2LCD.setProperty("value",QtCore.QVariant(1.0))
        self.ambLight2LCD.setObjectName("ambLight2LCD")
        self.gridlayout4.addWidget(self.ambLight2LCD,0,1,1,1)

        self.diffuseLight2SL = QtGui.QSlider(self.frame5)
        self.diffuseLight2SL.setMaximum(100)
        self.diffuseLight2SL.setSingleStep(1)
        self.diffuseLight2SL.setTickInterval(10)
        self.diffuseLight2SL.setObjectName("diffuseLight2SL")
        self.gridlayout4.addWidget(self.diffuseLight2SL,1,0,1,1)
        self.vboxlayout2.addLayout(self.gridlayout4)
        self.gridlayout3.addLayout(self.vboxlayout2,0,1,1,1)

        self.vboxlayout3 = QtGui.QVBoxLayout()
        self.vboxlayout3.setMargin(0)
        self.vboxlayout3.setSpacing(6)
        self.vboxlayout3.setObjectName("vboxlayout3")

        self.textLabel2_2 = QtGui.QLabel(self.frame5)
        self.textLabel2_2.setObjectName("textLabel2_2")
        self.vboxlayout3.addWidget(self.textLabel2_2)

        self.textLabel1_2 = QtGui.QLabel(self.frame5)
        self.textLabel1_2.setObjectName("textLabel1_2")
        self.vboxlayout3.addWidget(self.textLabel1_2)

        self.textLabel1_3_3 = QtGui.QLabel(self.frame5)
        self.textLabel1_3_3.setObjectName("textLabel1_3_3")
        self.vboxlayout3.addWidget(self.textLabel1_3_3)
        self.gridlayout3.addLayout(self.vboxlayout3,0,0,1,1)
        self.gridlayout.addWidget(self.frame5,1,0,1,1)

        self.frame6 = QtGui.QFrame(LightingToolDialog)
        self.frame6.setFrameShape(QtGui.QFrame.Box)
        self.frame6.setFrameShadow(QtGui.QFrame.Raised)
        self.frame6.setObjectName("frame6")

        self.gridlayout5 = QtGui.QGridLayout(self.frame6)
        self.gridlayout5.setMargin(11)
        self.gridlayout5.setSpacing(6)
        self.gridlayout5.setObjectName("gridlayout5")

        self.vboxlayout4 = QtGui.QVBoxLayout()
        self.vboxlayout4.setMargin(0)
        self.vboxlayout4.setSpacing(6)
        self.vboxlayout4.setObjectName("vboxlayout4")

        self.light3CB = QtGui.QCheckBox(self.frame6)
        self.light3CB.setObjectName("light3CB")
        self.vboxlayout4.addWidget(self.light3CB)

        self.gridlayout6 = QtGui.QGridLayout()
        self.gridlayout6.setMargin(0)
        self.gridlayout6.setSpacing(6)
        self.gridlayout6.setObjectName("gridlayout6")

        self.diffuseLight3SL = QtGui.QSlider(self.frame6)
        self.diffuseLight3SL.setMaximum(100)
        self.diffuseLight3SL.setSingleStep(1)
        self.diffuseLight3SL.setTickInterval(10)
        self.diffuseLight3SL.setObjectName("diffuseLight3SL")
        self.gridlayout6.addWidget(self.diffuseLight3SL,1,0,1,1)

        self.diffuseLight3LCD = QtGui.QLCDNumber(self.frame6)
        self.diffuseLight3LCD.setSmallDecimalPoint(False)
        self.diffuseLight3LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.diffuseLight3LCD.setProperty("value",QtCore.QVariant(1.0))
        self.diffuseLight3LCD.setProperty("intValue",QtCore.QVariant(1))
        self.diffuseLight3LCD.setObjectName("diffuseLight3LCD")
        self.gridlayout6.addWidget(self.diffuseLight3LCD,1,1,1,1)

        self.ambLight3LCD = QtGui.QLCDNumber(self.frame6)
        self.ambLight3LCD.setSmallDecimalPoint(False)
        self.ambLight3LCD.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.ambLight3LCD.setProperty("value",QtCore.QVariant(1.0))
        self.ambLight3LCD.setObjectName("ambLight3LCD")
        self.gridlayout6.addWidget(self.ambLight3LCD,0,1,1,1)

        self.ambLight3SL = QtGui.QSlider(self.frame6)
        self.ambLight3SL.setMaximum(100)
        self.ambLight3SL.setSingleStep(1)
        self.ambLight3SL.setTickInterval(10)
        self.ambLight3SL.setObjectName("ambLight3SL")
        self.gridlayout6.addWidget(self.ambLight3SL,0,0,1,1)
        self.vboxlayout4.addLayout(self.gridlayout6)
        self.gridlayout5.addLayout(self.vboxlayout4,0,1,1,1)

        self.vboxlayout5 = QtGui.QVBoxLayout()
        self.vboxlayout5.setMargin(0)
        self.vboxlayout5.setSpacing(6)
        self.vboxlayout5.setObjectName("vboxlayout5")

        self.textLabel2_3 = QtGui.QLabel(self.frame6)
        self.textLabel2_3.setObjectName("textLabel2_3")
        self.vboxlayout5.addWidget(self.textLabel2_3)

        self.textLabel1_2_2 = QtGui.QLabel(self.frame6)
        self.textLabel1_2_2.setObjectName("textLabel1_2_2")
        self.vboxlayout5.addWidget(self.textLabel1_2_2)

        self.textLabel1_3_3_2 = QtGui.QLabel(self.frame6)
        self.textLabel1_3_3_2.setObjectName("textLabel1_3_3_2")
        self.vboxlayout5.addWidget(self.textLabel1_3_3_2)
        self.gridlayout5.addLayout(self.vboxlayout5,0,0,1,1)
        self.gridlayout.addWidget(self.frame6,2,0,1,1)

        self.hboxlayout = QtGui.QHBoxLayout()
        self.hboxlayout.setMargin(0)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName("hboxlayout")

        self.okPB = QtGui.QPushButton(LightingToolDialog)
        self.okPB.setObjectName("okPB")
        self.hboxlayout.addWidget(self.okPB)

        self.restoreDefaultsPB = QtGui.QPushButton(LightingToolDialog)
        self.restoreDefaultsPB.setObjectName("restoreDefaultsPB")
        self.hboxlayout.addWidget(self.restoreDefaultsPB)

        self.cancelPB = QtGui.QPushButton(LightingToolDialog)
        self.cancelPB.setObjectName("cancelPB")
        self.hboxlayout.addWidget(self.cancelPB)
        self.gridlayout.addLayout(self.hboxlayout,3,0,1,1)

        self.retranslateUi(LightingToolDialog)
        QtCore.QObject.connect(self.okPB,QtCore.SIGNAL("clicked()"),LightingToolDialog.accept)
        QtCore.QObject.connect(self.cancelPB,QtCore.SIGNAL("clicked()"),LightingToolDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LightingToolDialog)
        LightingToolDialog.setTabOrder(self.light1CB,self.ambLight1SL)
        LightingToolDialog.setTabOrder(self.ambLight1SL,self.diffuseLight1SL)
        LightingToolDialog.setTabOrder(self.diffuseLight1SL,self.light2CB)
        LightingToolDialog.setTabOrder(self.light2CB,self.ambLight2SL)
        LightingToolDialog.setTabOrder(self.ambLight2SL,self.diffuseLight2SL)
        LightingToolDialog.setTabOrder(self.diffuseLight2SL,self.light3CB)
        LightingToolDialog.setTabOrder(self.light3CB,self.ambLight3SL)
        LightingToolDialog.setTabOrder(self.ambLight3SL,self.diffuseLight3SL)
        LightingToolDialog.setTabOrder(self.diffuseLight3SL,self.okPB)
        LightingToolDialog.setTabOrder(self.okPB,self.restoreDefaultsPB)
        LightingToolDialog.setTabOrder(self.restoreDefaultsPB,self.cancelPB)

    def retranslateUi(self, LightingToolDialog):
        LightingToolDialog.setWindowTitle(QtGui.QApplication.translate("LightingToolDialog", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
        self.light1CB.setText(QtGui.QApplication.translate("LightingToolDialog", "On", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_4.setText(QtGui.QApplication.translate("LightingToolDialog", "Light Source #1:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_4.setText(QtGui.QApplication.translate("LightingToolDialog", "Ambient Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3_2.setText(QtGui.QApplication.translate("LightingToolDialog", "Diffuse Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.light2CB.setText(QtGui.QApplication.translate("LightingToolDialog", "On", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_2.setText(QtGui.QApplication.translate("LightingToolDialog", "Light Source #2:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2.setText(QtGui.QApplication.translate("LightingToolDialog", "Ambient Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3_3.setText(QtGui.QApplication.translate("LightingToolDialog", "Diffuse Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.light3CB.setText(QtGui.QApplication.translate("LightingToolDialog", "On", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel2_3.setText(QtGui.QApplication.translate("LightingToolDialog", "Light Source #3:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_2_2.setText(QtGui.QApplication.translate("LightingToolDialog", "Ambient Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.textLabel1_3_3_2.setText(QtGui.QApplication.translate("LightingToolDialog", "Diffuse Brightness:", None, QtGui.QApplication.UnicodeUTF8))
        self.okPB.setText(QtGui.QApplication.translate("LightingToolDialog", "Save", None, QtGui.QApplication.UnicodeUTF8))
        self.restoreDefaultsPB.setText(QtGui.QApplication.translate("LightingToolDialog", "Restore Defaults", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelPB.setText(QtGui.QApplication.translate("LightingToolDialog", "Cancel", None, QtGui.QApplication.UnicodeUTF8))
