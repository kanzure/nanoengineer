# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/huaicai/atom/cad/src/SimSetupDialog.ui'
#
# Created: Thu Dec 9 14:44:31 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x64\x49\x44\x41\x54\x78\x9c\xcd\x95\xb1\x4a\xc3" \
    "\x50\x14\x86\xbf\x5b\xc4\x76\xd1\x25\xa5\xda\x2e" \
    "\x8e\x75\xe9\xd3\x18\x30\x93\x4b\xa1\x19\xc4\xc5" \
    "\x07\x70\xa8\xb8\x85\x6c\x15\x52\x70\xd0\x41\xa2" \
    "\x44\xf0\x0d\xc4\xb7\xd0\xd1\xe5\x06\xc5\x16\xd4" \
    "\xa5\x38\x78\x1c\x42\xd2\xa4\x69\x4b\x5b\x5b\xf0" \
    "\x87\x43\xee\x3d\x37\xf9\xf8\x39\xf7\xdc\x1b\xa5" \
    "\x43\xcd\x2a\x54\x58\x09\xf5\xdf\x82\xab\xdb\x55" \
    "\x99\xb8\xa8\x43\x8d\x0e\x35\xae\xd3\x16\x60\xe1" \
    "\x70\x9d\xb6\xc4\x2c\x1d\x6a\x54\xbc\x79\xb5\x6a" \
    "\x4d\x02\xdf\x5b\xd8\xbd\x69\xd9\xe8\x50\xab\x78" \
    "\xbe\x36\xfa\xc2\xde\x7e\x6b\x6e\xe8\xdd\x4d\x37" \
    "\x97\x9b\x5a\xe3\x2b\x2e\x28\x53\xa2\x4c\x89\xbe" \
    "\x34\xe8\x4b\x03\xa5\x14\x74\xbb\xf4\xde\x9e\x01" \
    "\x92\xe7\xcc\xe0\xf3\xaf\x33\x8e\x39\xc4\xa5\x83" \
    "\x4b\x07\x80\x87\xdb\x23\x00\x5e\xae\x2f\x31\xee" \
    "\x1f\x01\x30\x2a\xf5\xb1\xdf\xe7\x4a\x11\x3b\x3d" \
    "\xd9\x38\xc5\xa5\xc3\x01\xcd\x28\xa9\x9a\x98\x96" \
    "\x22\xf0\x3d\x76\x3e\x00\xdb\x8e\xf2\xad\x09\xa5" \
    "\x8b\x77\x11\x90\xc0\xf7\x44\x44\xc4\x90\xa2\x18" \
    "\x52\x94\xb4\x02\xdf\x13\x60\x98\x80\x28\x52\x6b" \
    "\xe9\xae\x98\xb9\x8f\x4d\xcb\x66\x9e\xae\xc9\x81" \
    "\x95\x82\x9e\x1a\xd0\x53\x03\x94\x22\x09\x10\x4c" \
    "\xab\x35\xcc\x21\x51\xa8\x3c\x74\x2c\x78\x59\xca" \
    "\x6d\x5e\xe0\xe7\x7b\xf2\x4f\x60\xd7\x69\x63\x5a" \
    "\xf6\xc2\x20\xd7\x69\x67\xe6\xc9\x91\x5e\x2f\x7c" \
    "\x4e\xbc\x50\xca\x5b\xbb\xc9\xf8\xfd\xf5\x29\x19" \
    "\x1b\x95\x7a\xe6\x80\x7c\xff\x6c\x26\x15\x5f\x59" \
    "\x8d\xa7\x3a\x4e\x3b\x1d\x55\xda\x39\x64\xdd\x66" \
    "\xc0\xcb\xd6\xff\xfc\x83\x4c\xd3\x2f\x40\xa4\xbb" \
    "\x2c\x12\x83\xbf\x94\x00\x00\x00\x00\x49\x45\x4e" \
    "\x44\xae\x42\x60\x82"

class SimSetupDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("SimSetupDialog")

        self.setIcon(self.image0)
        self.setModal(1)

        SimSetupDialogLayout = QVBoxLayout(self,11,6,"SimSetupDialogLayout")

        self.textLabel6 = QLabel(self,"textLabel6")
        self.textLabel6.setAlignment(QLabel.WordBreak | QLabel.AlignCenter)
        SimSetupDialogLayout.addWidget(self.textLabel6)

        layout62 = QGridLayout(None,1,1,0,6,"layout62")

        layout61 = QVBoxLayout(None,0,6,"layout61")

        self.textLabel2 = QLabel(self,"textLabel2")
        layout61.addWidget(self.textLabel2)

        self.StepsPerFrameWidget = QSpinBox(self,"StepsPerFrameWidget")
        self.StepsPerFrameWidget.setMinValue(1)
        self.StepsPerFrameWidget.setValue(10)
        layout61.addWidget(self.StepsPerFrameWidget)

        layout62.addLayout(layout61,1,0)

        layout58 = QVBoxLayout(None,0,6,"layout58")

        self.textLabel1 = QLabel(self,"textLabel1")
        layout58.addWidget(self.textLabel1)

        self.TimeStepWidget = QSpinBox(self,"TimeStepWidget")
        self.TimeStepWidget.setMaxValue(999)
        self.TimeStepWidget.setMinValue(1)
        self.TimeStepWidget.setValue(10)
        layout58.addWidget(self.TimeStepWidget)

        layout62.addLayout(layout58,0,0)

        layout59 = QVBoxLayout(None,0,6,"layout59")

        self.textLabel3 = QLabel(self,"textLabel3")
        layout59.addWidget(self.textLabel3)

        self.TemperatureWidget = QSpinBox(self,"TemperatureWidget")
        self.TemperatureWidget.setMaxValue(999)
        self.TemperatureWidget.setValue(300)
        layout59.addWidget(self.TemperatureWidget)

        layout62.addLayout(layout59,0,1)

        layout60 = QVBoxLayout(None,0,6,"layout60")

        self.textLabel5 = QLabel(self,"textLabel5")
        layout60.addWidget(self.textLabel5)

        self.NumFramesWidget = QSpinBox(self,"NumFramesWidget")
        self.NumFramesWidget.setMaxValue(90000)
        self.NumFramesWidget.setMinValue(30)
        self.NumFramesWidget.setLineStep(15)
        self.NumFramesWidget.setValue(900)
        layout60.addWidget(self.NumFramesWidget)

        layout62.addLayout(layout60,1,1)
        SimSetupDialogLayout.addLayout(layout62)

        self.FileFormatWidget = QButtonGroup(self,"FileFormatWidget")
        self.FileFormatWidget.setSizePolicy(QSizePolicy(5,5,0,1,self.FileFormatWidget.sizePolicy().hasHeightForWidth()))
        self.FileFormatWidget.setAlignment(QButtonGroup.AlignVCenter)

        self.BinFileWidget = QRadioButton(self.FileFormatWidget,"BinFileWidget")
        self.BinFileWidget.setGeometry(QRect(20,60,221,22))
        self.BinFileWidget.setChecked(1)
        self.FileFormatWidget.insert( self.BinFileWidget,0)

        self.TextFile = QRadioButton(self.FileFormatWidget,"TextFile")
        self.TextFile.setGeometry(QRect(20,120,221,22))
        self.FileFormatWidget.insert( self.TextFile,1)
        SimSetupDialogLayout.addWidget(self.FileFormatWidget)

        layout63 = QHBoxLayout(None,0,26,"layout63")

        self.NameFileButton = QPushButton(self,"NameFileButton")
        layout63.addWidget(self.NameFileButton)

        self.GoButton = QPushButton(self,"GoButton")
        self.GoButton.setDefault(1)
        layout63.addWidget(self.GoButton)
        SimSetupDialogLayout.addLayout(layout63)

        self.languageChange()

        self.resize(QSize(408,487).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.NumFramesWidget,SIGNAL("valueChanged(int)"),self.NumFramesValueChanged)
        self.connect(self.FileFormatWidget,SIGNAL("clicked(int)"),self.FileFormat)
        self.connect(self.NameFileButton,SIGNAL("clicked()"),self.NameFilePressed)
        self.connect(self.GoButton,SIGNAL("clicked()"),self.GoPressed)
        self.connect(self.StepsPerFrameWidget,SIGNAL("valueChanged(int)"),self.StepsChanged)
        self.connect(self.TemperatureWidget,SIGNAL("valueChanged(int)"),self.TemperatureChanged)
        self.connect(self.TimeStepWidget,SIGNAL("valueChanged(int)"),self.TimeStepChanged)


    def languageChange(self):
        self.setCaption(self.__tr("Simulator"))
        self.textLabel6.setText(self.__tr("<b><h1>Simulation Setup</h1></b>"))
        self.textLabel2.setText(self.__tr("Steps per Frame"))
        self.textLabel1.setText(self.__tr("Timestep\n"
"(hundredths of\n"
"femtosecond)"))
        self.textLabel3.setText(self.__tr("Temperature\n"
"(Kelvins)"))
        self.textLabel5.setText(self.__tr("Total frames"))
        self.FileFormatWidget.setTitle(self.__tr("File Format"))
        self.BinFileWidget.setText(self.__tr("Binary trajectory file (*.dpb)"))
        self.TextFile.setText(self.__tr("Text trajectory file (*.xyz)"))
        self.NameFileButton.setText(self.__tr("Name File"))
        self.GoButton.setText(self.__tr("Go"))


    def NumFramesValueChanged(self,a0):
        print "SimSetupDialog.NumFramesValueChanged(int): Not implemented yet"

    def NameFilePressed(self):
        print "SimSetupDialog.NameFilePressed(): Not implemented yet"

    def GoPressed(self):
        print "SimSetupDialog.GoPressed(): Not implemented yet"

    def StepsChanged(self,a0):
        print "SimSetupDialog.StepsChanged(int): Not implemented yet"

    def TemperatureChanged(self,a0):
        print "SimSetupDialog.TemperatureChanged(int): Not implemented yet"

    def TimeStepChanged(self,a0):
        print "SimSetupDialog.TimeStepChanged(int): Not implemented yet"

    def FileFormat(self,a0):
        print "SimSetupDialog.FileFormat(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("SimSetupDialog",s,c)
