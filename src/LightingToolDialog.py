# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\LightingToolDialog.ui'
#
# Created: Thu Sep 8 09:01:39 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class LightingToolDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("LightingToolDialog")


        LightingToolDialogLayout = QGridLayout(self,1,1,11,6,"LightingToolDialogLayout")

        self.frame1_2 = QFrame(self,"frame1_2")
        self.frame1_2.setFrameShape(QFrame.Box)
        self.frame1_2.setFrameShadow(QFrame.Raised)
        self.frame1_2.setMargin(0)
        frame1_2Layout = QGridLayout(self.frame1_2,1,1,11,6,"frame1_2Layout")

        layout34 = QVBoxLayout(None,0,6,"layout34")

        self.light1CB = QCheckBox(self.frame1_2,"light1CB")
        layout34.addWidget(self.light1CB)

        layout33 = QGridLayout(None,1,1,0,6,"layout33")

        self.ambLight1LCD = QLCDNumber(self.frame1_2,"ambLight1LCD")
        self.ambLight1LCD.setSmallDecimalPoint(0)
        self.ambLight1LCD.setSegmentStyle(QLCDNumber.Flat)
        self.ambLight1LCD.setProperty("value",QVariant(1))
        self.ambLight1LCD.setProperty("intValue",QVariant(1))

        layout33.addWidget(self.ambLight1LCD,0,1)

        self.ambLight1SL = QSlider(self.frame1_2,"ambLight1SL")
        self.ambLight1SL.setMaxValue(100)
        self.ambLight1SL.setLineStep(1)
        self.ambLight1SL.setOrientation(QSlider.Horizontal)
        self.ambLight1SL.setTickmarks(QSlider.Below)
        self.ambLight1SL.setTickInterval(10)

        layout33.addWidget(self.ambLight1SL,0,0)

        self.diffuseLight1SL = QSlider(self.frame1_2,"diffuseLight1SL")
        self.diffuseLight1SL.setMaxValue(100)
        self.diffuseLight1SL.setLineStep(1)
        self.diffuseLight1SL.setOrientation(QSlider.Horizontal)
        self.diffuseLight1SL.setTickmarks(QSlider.Below)
        self.diffuseLight1SL.setTickInterval(10)

        layout33.addWidget(self.diffuseLight1SL,1,0)

        self.diffuseLight1LCD = QLCDNumber(self.frame1_2,"diffuseLight1LCD")
        self.diffuseLight1LCD.setSmallDecimalPoint(0)
        self.diffuseLight1LCD.setSegmentStyle(QLCDNumber.Flat)
        self.diffuseLight1LCD.setProperty("value",QVariant(1))
        self.diffuseLight1LCD.setProperty("intValue",QVariant(1))

        layout33.addWidget(self.diffuseLight1LCD,1,1)
        layout34.addLayout(layout33)

        frame1_2Layout.addLayout(layout34,0,1)

        layout35 = QVBoxLayout(None,0,6,"layout35")

        self.textLabel2_4 = QLabel(self.frame1_2,"textLabel2_4")
        layout35.addWidget(self.textLabel2_4)

        self.textLabel1_4 = QLabel(self.frame1_2,"textLabel1_4")
        layout35.addWidget(self.textLabel1_4)

        self.textLabel1_3_2 = QLabel(self.frame1_2,"textLabel1_3_2")
        layout35.addWidget(self.textLabel1_3_2)

        frame1_2Layout.addLayout(layout35,0,0)

        LightingToolDialogLayout.addWidget(self.frame1_2,0,0)

        self.frame5 = QFrame(self,"frame5")
        self.frame5.setFrameShape(QFrame.Box)
        self.frame5.setFrameShadow(QFrame.Raised)
        frame5Layout = QGridLayout(self.frame5,1,1,11,6,"frame5Layout")

        layout37 = QVBoxLayout(None,0,6,"layout37")

        self.light2CB = QCheckBox(self.frame5,"light2CB")
        layout37.addWidget(self.light2CB)

        layout36 = QGridLayout(None,1,1,0,6,"layout36")

        self.ambLight2SL = QSlider(self.frame5,"ambLight2SL")
        self.ambLight2SL.setMaxValue(100)
        self.ambLight2SL.setLineStep(1)
        self.ambLight2SL.setOrientation(QSlider.Horizontal)
        self.ambLight2SL.setTickmarks(QSlider.Below)
        self.ambLight2SL.setTickInterval(10)

        layout36.addWidget(self.ambLight2SL,0,0)

        self.diffuseLight2LCD = QLCDNumber(self.frame5,"diffuseLight2LCD")
        self.diffuseLight2LCD.setSmallDecimalPoint(0)
        self.diffuseLight2LCD.setSegmentStyle(QLCDNumber.Flat)
        self.diffuseLight2LCD.setProperty("value",QVariant(1))
        self.diffuseLight2LCD.setProperty("intValue",QVariant(1))

        layout36.addWidget(self.diffuseLight2LCD,1,1)

        self.ambLight2LCD = QLCDNumber(self.frame5,"ambLight2LCD")
        self.ambLight2LCD.setSmallDecimalPoint(0)
        self.ambLight2LCD.setSegmentStyle(QLCDNumber.Flat)
        self.ambLight2LCD.setProperty("value",QVariant(1))

        layout36.addWidget(self.ambLight2LCD,0,1)

        self.diffuseLight2SL = QSlider(self.frame5,"diffuseLight2SL")
        self.diffuseLight2SL.setMaxValue(100)
        self.diffuseLight2SL.setLineStep(1)
        self.diffuseLight2SL.setOrientation(QSlider.Horizontal)
        self.diffuseLight2SL.setTickmarks(QSlider.Below)
        self.diffuseLight2SL.setTickInterval(10)

        layout36.addWidget(self.diffuseLight2SL,1,0)
        layout37.addLayout(layout36)

        frame5Layout.addLayout(layout37,0,1)

        layout38 = QVBoxLayout(None,0,6,"layout38")

        self.textLabel2_2 = QLabel(self.frame5,"textLabel2_2")
        layout38.addWidget(self.textLabel2_2)

        self.textLabel1_2 = QLabel(self.frame5,"textLabel1_2")
        layout38.addWidget(self.textLabel1_2)

        self.textLabel1_3_3 = QLabel(self.frame5,"textLabel1_3_3")
        layout38.addWidget(self.textLabel1_3_3)

        frame5Layout.addLayout(layout38,0,0)

        LightingToolDialogLayout.addWidget(self.frame5,1,0)

        self.frame6 = QFrame(self,"frame6")
        self.frame6.setFrameShape(QFrame.Box)
        self.frame6.setFrameShadow(QFrame.Raised)
        frame6Layout = QGridLayout(self.frame6,1,1,11,6,"frame6Layout")

        layout40 = QVBoxLayout(None,0,6,"layout40")

        self.light3CB = QCheckBox(self.frame6,"light3CB")
        layout40.addWidget(self.light3CB)

        layout39 = QGridLayout(None,1,1,0,6,"layout39")

        self.diffuseLight3SL = QSlider(self.frame6,"diffuseLight3SL")
        self.diffuseLight3SL.setMaxValue(100)
        self.diffuseLight3SL.setLineStep(1)
        self.diffuseLight3SL.setOrientation(QSlider.Horizontal)
        self.diffuseLight3SL.setTickmarks(QSlider.Below)
        self.diffuseLight3SL.setTickInterval(10)

        layout39.addWidget(self.diffuseLight3SL,1,0)

        self.diffuseLight3LCD = QLCDNumber(self.frame6,"diffuseLight3LCD")
        self.diffuseLight3LCD.setSmallDecimalPoint(0)
        self.diffuseLight3LCD.setSegmentStyle(QLCDNumber.Flat)
        self.diffuseLight3LCD.setProperty("value",QVariant(1))
        self.diffuseLight3LCD.setProperty("intValue",QVariant(1))

        layout39.addWidget(self.diffuseLight3LCD,1,1)

        self.ambLight3LCD = QLCDNumber(self.frame6,"ambLight3LCD")
        self.ambLight3LCD.setSmallDecimalPoint(0)
        self.ambLight3LCD.setSegmentStyle(QLCDNumber.Flat)
        self.ambLight3LCD.setProperty("value",QVariant(1))

        layout39.addWidget(self.ambLight3LCD,0,1)

        self.ambLight3SL = QSlider(self.frame6,"ambLight3SL")
        self.ambLight3SL.setMaxValue(100)
        self.ambLight3SL.setLineStep(1)
        self.ambLight3SL.setOrientation(QSlider.Horizontal)
        self.ambLight3SL.setTickmarks(QSlider.Below)
        self.ambLight3SL.setTickInterval(10)

        layout39.addWidget(self.ambLight3SL,0,0)
        layout40.addLayout(layout39)

        frame6Layout.addLayout(layout40,0,1)

        layout41 = QVBoxLayout(None,0,6,"layout41")

        self.textLabel2_3 = QLabel(self.frame6,"textLabel2_3")
        layout41.addWidget(self.textLabel2_3)

        self.textLabel1_2_2 = QLabel(self.frame6,"textLabel1_2_2")
        layout41.addWidget(self.textLabel1_2_2)

        self.textLabel1_3_3_2 = QLabel(self.frame6,"textLabel1_3_3_2")
        layout41.addWidget(self.textLabel1_3_3_2)

        frame6Layout.addLayout(layout41,0,0)

        LightingToolDialogLayout.addWidget(self.frame6,2,0)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.okPB = QPushButton(self,"okPB")
        layout11.addWidget(self.okPB)

        self.restoreDefaultsPB = QPushButton(self,"restoreDefaultsPB")
        layout11.addWidget(self.restoreDefaultsPB)

        self.cancelPB = QPushButton(self,"cancelPB")
        layout11.addWidget(self.cancelPB)

        LightingToolDialogLayout.addLayout(layout11,3,0)

        self.languageChange()

        self.resize(QSize(411,470).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okPB,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.cancelPB,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.ambLight1SL,SIGNAL("valueChanged(int)"),self.valueChangedAmbient1)
        self.connect(self.diffuseLight1SL,SIGNAL("valueChanged(int)"),self.valueChangedDiffuse1)
        self.connect(self.diffuseLight2SL,SIGNAL("valueChanged(int)"),self.valueChangedDiffuse2)
        self.connect(self.diffuseLight3SL,SIGNAL("valueChanged(int)"),self.valueChangedDiffuse3)
        self.connect(self.ambLight2SL,SIGNAL("valueChanged(int)"),self.valueChangedAmbient2)
        self.connect(self.ambLight3SL,SIGNAL("valueChanged(int)"),self.valueChangedAmbient3)
        self.connect(self.light1CB,SIGNAL("clicked()"),self.setLights)
        self.connect(self.light2CB,SIGNAL("clicked()"),self.setLights)
        self.connect(self.light3CB,SIGNAL("clicked()"),self.setLights)
        self.connect(self.restoreDefaultsPB,SIGNAL("clicked()"),self.restore)

        self.setTabOrder(self.light1CB,self.ambLight1SL)
        self.setTabOrder(self.ambLight1SL,self.diffuseLight1SL)
        self.setTabOrder(self.diffuseLight1SL,self.light2CB)
        self.setTabOrder(self.light2CB,self.ambLight2SL)
        self.setTabOrder(self.ambLight2SL,self.diffuseLight2SL)
        self.setTabOrder(self.diffuseLight2SL,self.light3CB)
        self.setTabOrder(self.light3CB,self.ambLight3SL)
        self.setTabOrder(self.ambLight3SL,self.diffuseLight3SL)
        self.setTabOrder(self.diffuseLight3SL,self.okPB)
        self.setTabOrder(self.okPB,self.restoreDefaultsPB)
        self.setTabOrder(self.restoreDefaultsPB,self.cancelPB)


    def languageChange(self):
        self.setCaption(self.__tr("Lighting"))
        self.light1CB.setText(self.__tr("On"))
        self.textLabel2_4.setText(self.__tr("Light Source #1:"))
        self.textLabel1_4.setText(self.__tr("Ambient Brightness:"))
        self.textLabel1_3_2.setText(self.__tr("Diffuse Brightness:"))
        self.light2CB.setText(self.__tr("On"))
        self.textLabel2_2.setText(self.__tr("Light Source #2:"))
        self.textLabel1_2.setText(self.__tr("Ambient Brightness:"))
        self.textLabel1_3_3.setText(self.__tr("Diffuse Brightness:"))
        self.light3CB.setText(self.__tr("On"))
        self.textLabel2_3.setText(self.__tr("Light Source #3:"))
        self.textLabel1_2_2.setText(self.__tr("Ambient Brightness:"))
        self.textLabel1_3_3_2.setText(self.__tr("Diffuse Brightness:"))
        self.okPB.setText(self.__tr("Save"))
        self.restoreDefaultsPB.setText(self.__tr("Restore Defaults"))
        self.cancelPB.setText(self.__tr("Cancel"))


    def valueChangedAmbient1(self):
        print "LightingToolDialog.valueChangedAmbient1(): Not implemented yet"

    def valueChangedDiffuse1(self):
        print "LightingToolDialog.valueChangedDiffuse1(): Not implemented yet"

    def valueChangedAmbient2(self):
        print "LightingToolDialog.valueChangedAmbient2(): Not implemented yet"

    def valueChangedAmbient3(self):
        print "LightingToolDialog.valueChangedAmbient3(): Not implemented yet"

    def valueChangedDiffuse2(self):
        print "LightingToolDialog.valueChangedDiffuse2(): Not implemented yet"

    def valueChangedDiffuse3(self):
        print "LightingToolDialog.valueChangedDiffuse3(): Not implemented yet"

    def setLights(self):
        print "LightingToolDialog.setLights(): Not implemented yet"

    def restore(self):
        print "LightingToolDialog.restore(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("LightingToolDialog",s,c)
