# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Sun Feb 6 00:41:43 2005
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

        SimSetupDialogLayout = QVBoxLayout(self,11,21,"SimSetupDialogLayout")

        layout28 = QGridLayout(None,1,1,0,6,"layout28")

        self.textLabel5 = QLabel(self,"textLabel5")
        textLabel5_font = QFont(self.textLabel5.font())
        textLabel5_font.setPointSize(9)
        textLabel5_font.setBold(1)
        self.textLabel5.setFont(textLabel5_font)

        layout28.addWidget(self.textLabel5,0,0)

        self.textLabel2 = QLabel(self,"textLabel2")
        textLabel2_font = QFont(self.textLabel2.font())
        textLabel2_font.setPointSize(9)
        textLabel2_font.setBold(1)
        self.textLabel2.setFont(textLabel2_font)

        layout28.addWidget(self.textLabel2,2,0)

        self.nframesSB = QSpinBox(self,"nframesSB")
        self.nframesSB.setMaxValue(90000)
        self.nframesSB.setMinValue(1)
        self.nframesSB.setLineStep(15)
        print "SimSetupDialog: setting nframe = 900"
        self.nframesSB.setValue(900)

        layout28.addWidget(self.nframesSB,1,0)

        self.stepsperSB = QSpinBox(self,"stepsperSB")
        self.stepsperSB.setMaxValue(99999)
        self.stepsperSB.setMinValue(1)
        self.stepsperSB.setValue(10)

        layout28.addWidget(self.stepsperSB,3,0)

        self.tempSB = QSpinBox(self,"tempSB")
        self.tempSB.setMaxValue(99999)
        print "SimSetupDialog: setting temp = 300"
        self.tempSB.setValue(300)

        layout28.addWidget(self.tempSB,5,0)

        self.textLabel3 = QLabel(self,"textLabel3")
        textLabel3_font = QFont(self.textLabel3.font())
        textLabel3_font.setPointSize(9)
        textLabel3_font.setBold(1)
        self.textLabel3.setFont(textLabel3_font)

        layout28.addWidget(self.textLabel3,4,0)
        SimSetupDialogLayout.addLayout(layout28)

        layout27 = QHBoxLayout(None,0,10,"layout27")

        self.MovieButton = QPushButton(self,"MovieButton")
        MovieButton_font = QFont(self.MovieButton.font())
        MovieButton_font.setPointSize(9)
        MovieButton_font.setBold(1)
        self.MovieButton.setFont(MovieButton_font)
        self.MovieButton.setDefault(1)
        layout27.addWidget(self.MovieButton)

        self.CancelButton = QPushButton(self,"CancelButton")
        CancelButton_font = QFont(self.CancelButton.font())
        CancelButton_font.setPointSize(9)
        CancelButton_font.setBold(1)
        self.CancelButton.setFont(CancelButton_font)
        self.CancelButton.setDefault(1)
        layout27.addWidget(self.CancelButton)
        SimSetupDialogLayout.addLayout(layout27)

        self.languageChange()

        self.resize(QSize(298,318).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.MovieButton,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.CancelButton,SIGNAL("clicked()"),self,SLOT("close()"))


    def languageChange(self):
        self.setCaption(self.__tr("Simulator Setup"))
        self.textLabel5.setText(self.__tr("Total frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame:"))
        self.textLabel3.setText(self.__tr("Temperature(Kelvins):"))
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