# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'motorPropDialog.ui'
#
# Created: Thu Jul 29 16:06:15 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class MotorPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("MotorPropDialog")

        self.setSizePolicy(QSizePolicy(2,2,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setModal(1)


        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,10,50,31))
        textLabel1_font = QFont(self.textLabel1.font())
        textLabel1_font.setBold(1)
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setAlignment(QLabel.AlignCenter)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(140,10,61,31))
        textLabel2_font = QFont(self.textLabel2.font())
        textLabel2_font.setBold(1)
        self.textLabel2.setFont(textLabel2_font)

        self.groupBox1_2 = QGroupBox(self,"groupBox1_2")
        self.groupBox1_2.setGeometry(QRect(20,140,350,71))
        groupBox1_2_font = QFont(self.groupBox1_2.font())
        groupBox1_2_font.setPointSize(11)
        groupBox1_2_font.setBold(1)
        self.groupBox1_2.setFont(groupBox1_2_font)
        self.groupBox1_2.setFrameShadow(QGroupBox.Raised)

        self.textLabel3_3 = QLabel(self.groupBox1_2,"textLabel3_3")
        self.textLabel3_3.setGeometry(QRect(10,20,16,31))

        self.textLabel3_2_3 = QLabel(self.groupBox1_2,"textLabel3_2_3")
        self.textLabel3_2_3.setGeometry(QRect(120,20,16,31))

        self.textLabel3_2_2_2 = QLabel(self.groupBox1_2,"textLabel3_2_2_2")
        self.textLabel3_2_2_2.setGeometry(QRect(230,20,16,31))

        self.aX = QLineEdit(self.groupBox1_2,"aX")
        self.aX.setGeometry(QRect(30,20,61,31))

        self.aY = QLineEdit(self.groupBox1_2,"aY")
        self.aY.setGeometry(QRect(140,20,61,31))

        self.aZ = QLineEdit(self.groupBox1_2,"aZ")
        self.aZ.setGeometry(QRect(250,20,61,31))

        self.force = QLineEdit(self,"force")
        self.force.setGeometry(QRect(60,10,60,31))

        self.cancelButton = QPushButton(self,"cancelButton")
        self.cancelButton.setGeometry(QRect(220,250,71,31))
        cancelButton_font = QFont(self.cancelButton.font())
        cancelButton_font.setBold(1)
        self.cancelButton.setFont(cancelButton_font)

        self.stiffness = QLineEdit(self,"stiffness")
        self.stiffness.setGeometry(QRect(200,10,50,31))

        self.okButton = QPushButton(self,"okButton")
        self.okButton.setGeometry(QRect(70,250,71,31))
        okButton_font = QFont(self.okButton.font())
        okButton_font.setBold(1)
        self.okButton.setFont(okButton_font)
        self.okButton.setDefault(1)

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(261,10,50,31))
        textLabel5_font = QFont(self.textLabel5.font())
        textLabel5_font.setBold(1)
        self.textLabel5.setFont(textLabel5_font)
        self.textLabel5.setAlignment(QLabel.AlignCenter)

        self.atomsList = QComboBox(0,self,"atomsList")
        self.atomsList.setGeometry(QRect(310,10,70,30))

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setGeometry(QRect(20,60,350,71))
        groupBox1_font = QFont(self.groupBox1.font())
        groupBox1_font.setPointSize(11)
        groupBox1_font.setBold(1)
        self.groupBox1.setFont(groupBox1_font)
        self.groupBox1.setFrameShadow(QGroupBox.Raised)

        self.textLabel3_2_2 = QLabel(self.groupBox1,"textLabel3_2_2")
        self.textLabel3_2_2.setGeometry(QRect(230,20,16,31))

        self.textLabel3 = QLabel(self.groupBox1,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,20,16,31))

        self.textLabel3_2 = QLabel(self.groupBox1,"textLabel3_2")
        self.textLabel3_2.setGeometry(QRect(120,20,16,31))

        self.cX = QLineEdit(self.groupBox1,"cX")
        self.cX.setGeometry(QRect(30,20,61,31))

        self.cY = QLineEdit(self.groupBox1,"cY")
        self.cY.setGeometry(QRect(140,20,61,31))

        self.cZ = QLineEdit(self.groupBox1,"cZ")
        self.cZ.setGeometry(QRect(250,20,61,31))

        self.languageChange()

        self.resize(QSize(395,297).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelButton,SIGNAL("clicked()"),self,SLOT("reject()"))


    def languageChange(self):
        self.setCaption(self.__tr("Motor Properties"))
        self.textLabel1.setText(self.__tr("Force:"))
        self.textLabel2.setText(self.__tr("Stiffness:"))
        self.groupBox1_2.setTitle(self.__tr("Motor Axis Vector"))
        self.textLabel3_3.setText(self.__tr("x:"))
        self.textLabel3_2_3.setText(self.__tr("y:"))
        self.textLabel3_2_2_2.setText(self.__tr("z:"))
        self.aX.setText(self.__tr("0.0"))
        self.aY.setText(self.__tr("0.0"))
        self.aZ.setText(self.__tr("0.0"))
        self.force.setText(self.__tr("0.0"))
        self.cancelButton.setText(self.__tr("Cancel"))
        self.stiffness.setText(self.__tr("0.0"))
        self.okButton.setText(self.__tr("OK"))
        self.textLabel5.setText(self.__tr("Atoms:"))
        self.groupBox1.setTitle(self.__tr("Motor Center Coordinates"))
        self.textLabel3_2_2.setText(self.__tr("z:"))
        self.textLabel3.setText(self.__tr("x:"))
        self.textLabel3_2.setText(self.__tr("y:"))
        self.cX.setText(self.__tr("0.0"))
        self.cY.setText(self.__tr("0.0"))
        self.cZ.setText(self.__tr("0.0"))


    def __tr(self,s,c = None):
        return qApp.translate("MotorPropDialog",s,c)


    ## Functions written by myself
    def accept(self):
        QDialog.accept(self)

    def reject(self):
        QDialog.reject(self)

         

