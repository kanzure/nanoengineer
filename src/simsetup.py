# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simsetup.ui'
#
# Created: Tue Aug 10 11:37:19 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class simSetup(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("simSetup")



        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,200,130,30))

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setGeometry(QRect(40,10,290,37))

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,70,130,60))

        self.textLabel5 = QLabel(self,"textLabel5")
        self.textLabel5.setGeometry(QRect(210,190,100,41))

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(210,80,100,31))

        self.NameFileButton = QPushButton(self,"NameFileButton")
        self.NameFileButton.setGeometry(QRect(30,400,121,41))

        self.GoButton = QPushButton(self,"GoButton")
        self.GoButton.setGeometry(QRect(210,400,131,41))
        self.GoButton.setDefault(1)

        self.NumFramesWidget = QSpinBox(self,"NumFramesWidget")
        self.NumFramesWidget.setGeometry(QRect(210,240,90,30))
        self.NumFramesWidget.setMaxValue(90000)
        self.NumFramesWidget.setMinValue(30)
        self.NumFramesWidget.setLineStep(15)
        self.NumFramesWidget.setValue(900)

        self.TemperatureWidget = QSpinBox(self,"TemperatureWidget")
        self.TemperatureWidget.setGeometry(QRect(210,140,81,31))
        self.TemperatureWidget.setMaxValue(999)
        self.TemperatureWidget.setValue(300)

        self.StepsPerFrameWidget = QSpinBox(self,"StepsPerFrameWidget")
        self.StepsPerFrameWidget.setGeometry(QRect(10,240,80,30))
        self.StepsPerFrameWidget.setMinValue(1)
        self.StepsPerFrameWidget.setValue(10)

        self.TimeStepWidget = QSpinBox(self,"TimeStepWidget")
        self.TimeStepWidget.setGeometry(QRect(10,140,90,30))
        self.TimeStepWidget.setMaxValue(999)
        self.TimeStepWidget.setMinValue(1)
        self.TimeStepWidget.setValue(10)

        self.FileFormatWidget = QButtonGroup(self,"FileFormatWidget")
        self.FileFormatWidget.setGeometry(QRect(10,300,351,71))

        self.TextFile = QRadioButton(self.FileFormatWidget,"TextFile")
        self.TextFile.setGeometry(QRect(20,40,310,22))
        self.FileFormatWidget.insert( self.TextFile,1)

        self.BinFileWidget = QRadioButton(self.FileFormatWidget,"BinFileWidget")
        self.BinFileWidget.setGeometry(QRect(20,20,300,22))
        self.BinFileWidget.setChecked(1)
        self.FileFormatWidget.insert( self.BinFileWidget,0)

        self.languageChange()

        self.resize(QSize(375,480).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.NumFramesWidget,SIGNAL("valueChanged(int)"),self.NumFramesValueChanged)
        self.connect(self.FileFormatWidget,SIGNAL("clicked(int)"),self.FileFormat)
        self.connect(self.NameFileButton,SIGNAL("clicked()"),self.NameFilePressed)
        self.connect(self.GoButton,SIGNAL("clicked()"),self.GoPressed)
        self.connect(self.StepsPerFrameWidget,SIGNAL("valueChanged(int)"),self.StepsChanged)
        self.connect(self.TemperatureWidget,SIGNAL("valueChanged(int)"),self.TemperatureChanged)
        self.connect(self.TimeStepWidget,SIGNAL("valueChanged(int)"),self.TimeStepChanged)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.textLabel2.setText(self.__tr("steps per frame"))
        self.textLabel6.setText(self.__tr("<b><h1>Simulation Setup</h1></b>"))
        self.textLabel1.setText(self.__tr("Timestep\n"
"(hundredths of\n"
"femtosecond)"))
        self.textLabel5.setText(self.__tr("Total frames"))
        self.textLabel3.setText(self.__tr("Temperature\n"
"(Kelvins)"))
        self.NameFileButton.setText(self.__tr("Name File"))
        self.GoButton.setText(self.__tr("Go"))
        self.FileFormatWidget.setTitle(self.__tr("File Format"))
        self.TextFile.setText(self.__tr("Text trajectory file"))
        self.BinFileWidget.setText(self.__tr("Binary trajectory file"))


    def NumFramesValueChanged(self,a0):
        print "simSetup.NumFramesValueChanged(int): Not implemented yet"

    def NameFilePressed(self):
        print "simSetup.NameFilePressed(): Not implemented yet"

    def GoPressed(self):
        print "simSetup.GoPressed(): Not implemented yet"

    def StepsChanged(self,a0):
        print "simSetup.StepsChanged(int): Not implemented yet"

    def TemperatureChanged(self,a0):
        print "simSetup.TemperatureChanged(int): Not implemented yet"

    def TimeStepChanged(self,a0):
        print "simSetup.TimeStepChanged(int): Not implemented yet"

    def FileFormat(self,a0):
        print "simSetup.FileFormat(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("simSetup",s,c)
