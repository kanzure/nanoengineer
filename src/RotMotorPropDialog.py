# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '../GUI/rotaryMotorProp.ui'
#
# Created: Sat Jun 12 17:39:42 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class RotMotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("RotMotorPropDialog")

        self.setSizeGripEnabled(1)


        LayoutWidget = QWidget(self,"layout22")
        LayoutWidget.setGeometry(QRect(10,10,690,280))
        layout22 = QHBoxLayout(LayoutWidget,11,13,"layout22")

        layout7 = QVBoxLayout(None,2,6,"layout7")

        layout4 = QHBoxLayout(None,0,6,"layout4")

        self.textLabel1 = QLabel(LayoutWidget,"textLabel1")
        textLabel1_font = QFont(self.textLabel1.font())
        self.textLabel1.setFont(textLabel1_font)
        layout4.addWidget(self.textLabel1)

        self.torque = QLineEdit(LayoutWidget,"torque")
        layout4.addWidget(self.torque)

        self.textLabel1_2 = QLabel(LayoutWidget,"textLabel1_2")
        layout4.addWidget(self.textLabel1_2)

        self.speed = QLineEdit(LayoutWidget,"speed")
        layout4.addWidget(self.speed)

        self.textLabel1_3 = QLabel(LayoutWidget,"textLabel1_3")
        layout4.addWidget(self.textLabel1_3)

        self.atomsList = QComboBox(0,LayoutWidget,"atomsList")
        layout4.addWidget(self.atomsList)
        layout7.addLayout(layout4)

        self.groupBox3 = QGroupBox(LayoutWidget,"groupBox3")

        self.textLabel1_4_3 = QLabel(self.groupBox3,"textLabel1_4_3")
        self.textLabel1_4_3.setGeometry(QRect(328,51,13,23))

        self.textLabel1_4_2 = QLabel(self.groupBox3,"textLabel1_4_2")
        self.textLabel1_4_2.setGeometry(QRect(169,51,14,23))

        self.cX = QLineEdit(self.groupBox3,"cX")
        self.cX.setGeometry(QRect(31,51,132,23))

        self.textLabel1_4 = QLabel(self.groupBox3,"textLabel1_4")
        self.textLabel1_4.setGeometry(QRect(11,51,14,23))

        self.cZ = QLineEdit(self.groupBox3,"cZ")
        self.cZ.setGeometry(QRect(347,51,132,23))

        self.cY = QLineEdit(self.groupBox3,"cY")
        self.cY.setGeometry(QRect(189,51,133,23))
        layout7.addWidget(self.groupBox3)

        self.groupBox3_2 = QGroupBox(LayoutWidget,"groupBox3_2")

        self.aZ = QLineEdit(self.groupBox3_2,"aZ")
        self.aZ.setGeometry(QRect(347,51,132,23))

        self.textLabel1_4_2_2 = QLabel(self.groupBox3_2,"textLabel1_4_2_2")
        self.textLabel1_4_2_2.setGeometry(QRect(169,51,14,23))

        self.textLabel1_4_3_2 = QLabel(self.groupBox3_2,"textLabel1_4_3_2")
        self.textLabel1_4_3_2.setGeometry(QRect(328,51,13,23))

        self.textLabel1_4_4 = QLabel(self.groupBox3_2,"textLabel1_4_4")
        self.textLabel1_4_4.setGeometry(QRect(11,51,14,23))

        self.aX = QLineEdit(self.groupBox3_2,"aX")
        self.aX.setGeometry(QRect(31,51,132,23))

        self.aY = QLineEdit(self.groupBox3_2,"aY")
        self.aY.setGeometry(QRect(189,51,133,23))
        layout7.addWidget(self.groupBox3_2)
        layout22.addLayout(layout7)

        self.groupBox13 = QGroupBox(LayoutWidget,"groupBox13")
        self.groupBox13.setFrameShadow(QGroupBox.Sunken)
        self.groupBox13.setLineWidth(2)

        self.buttonAlignAxis = QPushButton(self.groupBox13,"buttonAlignAxis")
        self.buttonAlignAxis.setEnabled(0)
        self.buttonAlignAxis.setGeometry(QRect(10,20,108,32))

        self.buttonMoveCenter = QPushButton(self.groupBox13,"buttonMoveCenter")
        self.buttonMoveCenter.setEnabled(0)
        self.buttonMoveCenter.setGeometry(QRect(10,70,108,32))

        self.buttonCancel = QPushButton(self.groupBox13,"buttonCancel")
        self.buttonCancel.setGeometry(QRect(10,226,108,32))
        self.buttonCancel.setAutoDefault(1)

        self.buttonOk = QPushButton(self.groupBox13,"buttonOk")
        self.buttonOk.setGeometry(QRect(10,178,108,32))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        layout22.addWidget(self.groupBox13)

        self.languageChange()

        self.resize(QSize(713,294).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.buttonCancel,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.buttonOk,SIGNAL("clicked()"),self,SLOT("accept()"))

        self.setTabOrder(self.torque,self.speed)
        self.setTabOrder(self.speed,self.atomsList)
        self.setTabOrder(self.atomsList,self.buttonAlignAxis)
        self.setTabOrder(self.buttonAlignAxis,self.buttonMoveCenter)
        self.setTabOrder(self.buttonMoveCenter,self.buttonOk)
        self.setTabOrder(self.buttonOk,self.buttonCancel)


    def languageChange(self):
        self.setCaption(self.__tr("Rotary Motor Properties"))
        self.textLabel1.setText(self.__tr("Torque:"))
        self.textLabel1_2.setText(self.__tr("Speed:"))
        self.textLabel1_3.setText(self.__tr("Atoms:"))
        self.groupBox3.setTitle(self.__tr("Center Coordinates"))
        self.textLabel1_4_3.setText(self.__tr("Z:"))
        self.textLabel1_4_2.setText(self.__tr("Y:"))
        self.textLabel1_4.setText(self.__tr("X:"))
        self.groupBox3_2.setTitle(self.__tr("Axis Vector"))
        self.textLabel1_4_2_2.setText(self.__tr("Y:"))
        self.textLabel1_4_3_2.setText(self.__tr("Z:"))
        self.textLabel1_4_4.setText(self.__tr("X:"))
        self.groupBox13.setTitle(QString.null)
        self.buttonAlignAxis.setText(self.__tr("Align Axis"))
        self.buttonAlignAxis.setAccel(QString.null)
        self.buttonMoveCenter.setText(self.__tr("Move Center"))
        self.buttonMoveCenter.setAccel(QString.null)
        self.buttonCancel.setText(self.__tr("Cancel"))
        self.buttonCancel.setAccel(QString.null)
        self.buttonOk.setText(self.__tr("OK"))
        self.buttonOk.setAccel(QString.null)


    def __tr(self,s,c = None):
        return qApp.translate("RotMotorPropDialog",s,c)
