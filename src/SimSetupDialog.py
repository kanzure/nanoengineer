# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\SimSetupDialog.ui'
#
# Created: Thu Dec 9 13:20:01 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 14 1",
"b c #000000",
"l c #0000ff",
"e c #13ff07",
"a c #8e8c82",
"i c #95f284",
"d c #a1ff9c",
"c c #aca899",
"j c #e03f3a",
". c #e6e7e6",
"h c #ece9d8",
"f c #edfe2c",
"k c #ff0000",
"g c #ff9999",
"# c #ffffff",
"......................",
"......................",
"......................",
"...............#......",
"..abbbbbbbbbbbbbbba...",
"..bcccccccccccccccb...",
"..bc#############cb...",
"..bc###deeffbgh#hcb...",
"..bc##ieddfcbjg##cb...",
"..bc#ded###bcgkg#cb...",
"..bc#ee###cb##kk#cb...",
"..bc#ee###bc##kk#cb...",
"..bclllllllllllllcb...",
"..bclllllllllllllcb...",
"..bcccccccccccccccb...",
"..abbbbbbbbbbbbbbba...",
"..hhhhhhhbbbhhh#hhh...",
"..hhhhhhhbbbhhh#hhh...",
"..hhhhhbbbbbbbhhhh....",
"......................",
"......................",
"......................"
]

class SimSetupDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

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

        self.BinFileWidget = QRadioButton(self.FileFormatWidget,"BinFileWidget")
        self.BinFileWidget.setGeometry(QRect(20,20,190,22))
        self.BinFileWidget.setChecked(1)
        self.FileFormatWidget.insert( self.BinFileWidget,0)

        self.TextFile = QRadioButton(self.FileFormatWidget,"TextFile")
        self.TextFile.setGeometry(QRect(20,40,190,22))
        self.FileFormatWidget.insert( self.TextFile,1)
        SimSetupDialogLayout.addWidget(self.FileFormatWidget)

        layout63 = QHBoxLayout(None,0,6,"layout63")

        self.NameFileButton = QPushButton(self,"NameFileButton")
        layout63.addWidget(self.NameFileButton)

        self.GoButton = QPushButton(self,"GoButton")
        self.GoButton.setDefault(1)
        layout63.addWidget(self.GoButton)
        SimSetupDialogLayout.addLayout(layout63)

        self.languageChange()

        self.resize(QSize(290,330).expandedTo(self.minimumSizeHint()))
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
