# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Mon Jan 10 12:55:32 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 14 1",
". c None",
"a c #000000",
"l c #0000ff",
"e c #13ff07",
"# c #8e8c82",
"i c #95f284",
"d c #a1ff9c",
"b c #aca899",
"j c #e03f3a",
"h c #ece9d8",
"f c #edfe2c",
"k c #ff0000",
"g c #ff9999",
"c c #ffffff",
"......................",
"......................",
"......................",
"......................",
"..#aaaaaaaaaaaaaaa#...",
"..abbbbbbbbbbbbbbba...",
"..abcccccccccccccba...",
"..abcccdeeffaghchba...",
"..abccieddfbajgccba...",
"..abcdedcccabgkgcba...",
"..abceecccbacckkcba...",
"..abceecccabcckkcba...",
"..ablllllllllllllba...",
"..ablllllllllllllba...",
"..abbbbbbbbbbbbbbba...",
"..#aaaaaaaaaaaaaaa#...",
".........aaa..........",
".........aaa..........",
".......aaaaaaa........",
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


        LayoutWidget = QWidget(self,"layout8")
        LayoutWidget.setGeometry(QRect(20,10,210,169))
        layout8 = QVBoxLayout(LayoutWidget,11,6,"layout8")

        self.textLabel5 = QLabel(LayoutWidget,"textLabel5")
        layout8.addWidget(self.textLabel5)

        self.nframesSB = QSpinBox(LayoutWidget,"nframesSB")
        self.nframesSB.setMaxValue(90000)
        self.nframesSB.setMinValue(10)
        self.nframesSB.setLineStep(15)
        self.nframesSB.setValue(900)
        layout8.addWidget(self.nframesSB)

        self.textLabel2 = QLabel(LayoutWidget,"textLabel2")
        layout8.addWidget(self.textLabel2)

        self.stepsperSB = QSpinBox(LayoutWidget,"stepsperSB")
        self.stepsperSB.setMinValue(1)
        self.stepsperSB.setValue(10)
        layout8.addWidget(self.stepsperSB)

        self.textLabel3 = QLabel(LayoutWidget,"textLabel3")
        layout8.addWidget(self.textLabel3)

        self.tempSB = QSpinBox(LayoutWidget,"tempSB")
        self.tempSB.setMaxValue(999)
        self.tempSB.setValue(300)
        layout8.addWidget(self.tempSB)

        self.MovieButton = QPushButton(self,"MovieButton")
        self.MovieButton.setGeometry(QRect(21,191,106,29))
        self.MovieButton.setDefault(1)

        self.CancelButton = QPushButton(self,"CancelButton")
        self.CancelButton.setGeometry(QRect(133,191,100,29))
        self.CancelButton.setDefault(1)

        self.languageChange()

        self.resize(QSize(265,245).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.MovieButton,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.CancelButton,SIGNAL("clicked()"),self,SLOT("close()"))


    def languageChange(self):
        self.setCaption(self.__tr("Simulator Setup"))
        self.textLabel5.setText(self.__tr("Total frames"))
        self.textLabel2.setText(self.__tr("Steps per Frame"))
        self.textLabel3.setText(self.__tr("Temperature\n"
"(Kelvins)"))
        self.MovieButton.setText(self.__tr("Create Movie"))
        self.CancelButton.setText(self.__tr("Cancel"))


    def NumFramesValueChanged(self,a0):
        print "SimSetupDialog.NumFramesValueChanged(int): Not implemented yet"

    def createMoviePressed(self):
        print "SimSetupDialog.createMoviePressed(): Not implemented yet"

    def StepsChanged(self,a0):
        print "SimSetupDialog.StepsChanged(int): Not implemented yet"

    def TemperatureChanged(self,a0):
        print "SimSetupDialog.TemperatureChanged(int): Not implemented yet"

    def TimeStepChanged(self,a0):
        print "SimSetupDialog.TimeStepChanged(int): Not implemented yet"

    def saveFilePressed(self):
        print "SimSetupDialog.saveFilePressed(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("SimSetupDialog",s,c)
