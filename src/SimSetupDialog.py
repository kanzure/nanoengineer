# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Sun Jul 3 23:50:27 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"20 20 6 1",
"a c #000000",
"d c #404040",
"# c #595a59",
"c c #82d2b5",
"b c #9bf5d6",
". c #ffffff",
"....................",
"....................",
".#a#................",
"#.bb#...............",
"abbba...............",
"#bbc#...............",
".#a#..d.............",
"...d.dd..d..........",
"...dd.d.dd..d.......",
"...d..dd.d.dd..d....",
"......d..dd.d.dd....",
".........d..dd.d....",
"............d..#a#..",
"..............#.bb#.",
"..............abbba.",
"..............#bbc#.",
"...............#a#..",
"....................",
"....................",
"...................."
]

class SimSetupDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("SimSetupDialog")

        self.setIcon(self.image0)
        self.setModal(1)

        SimSetupDialogLayout = QGridLayout(self,1,1,11,21,"SimSetupDialogLayout")

        self.parms_grpbox = QGroupBox(self,"parms_grpbox")
        self.parms_grpbox.setColumnLayout(0,Qt.Vertical)
        self.parms_grpbox.layout().setSpacing(6)
        self.parms_grpbox.layout().setMargin(11)
        parms_grpboxLayout = QHBoxLayout(self.parms_grpbox.layout())
        parms_grpboxLayout.setAlignment(Qt.AlignTop)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout24 = QVBoxLayout(None,0,6,"layout24")

        self.textLabel5 = QLabel(self.parms_grpbox,"textLabel5")
        self.textLabel5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel5)

        self.textLabel2 = QLabel(self.parms_grpbox,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel2)

        self.textLabel3 = QLabel(self.parms_grpbox,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel3)
        layout27.addLayout(layout24)

        layout25 = QVBoxLayout(None,0,6,"layout25")

        self.nframesSB = QSpinBox(self.parms_grpbox,"nframesSB")
        self.nframesSB.setMaxValue(90000)
        self.nframesSB.setMinValue(1)
        self.nframesSB.setLineStep(15)
        self.nframesSB.setValue(900)
        layout25.addWidget(self.nframesSB)

        self.stepsperSB = QSpinBox(self.parms_grpbox,"stepsperSB")
        self.stepsperSB.setMaxValue(99999)
        self.stepsperSB.setMinValue(1)
        self.stepsperSB.setValue(10)
        layout25.addWidget(self.stepsperSB)

        self.tempSB = QSpinBox(self.parms_grpbox,"tempSB")
        self.tempSB.setMaxValue(99999)
        self.tempSB.setValue(300)
        layout25.addWidget(self.tempSB)
        layout27.addLayout(layout25)

        layout26 = QVBoxLayout(None,0,6,"layout26")
        spacer4 = QSpacerItem(255,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout26.addItem(spacer4)

        self.textLabel2_2 = QLabel(self.parms_grpbox,"textLabel2_2")
        layout26.addWidget(self.textLabel2_2)

        self.textLabel3_2 = QLabel(self.parms_grpbox,"textLabel3_2")
        layout26.addWidget(self.textLabel3_2)
        layout27.addLayout(layout26)
        parms_grpboxLayout.addLayout(layout27)

        SimSetupDialogLayout.addWidget(self.parms_grpbox,1,0)

        layout28 = QHBoxLayout(None,0,6,"layout28")

        self.run_sim_btn = QPushButton(self,"run_sim_btn")
        self.run_sim_btn.setDefault(1)
        layout28.addWidget(self.run_sim_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout28.addWidget(self.cancel_btn)

        SimSetupDialogLayout.addLayout(layout28,2,0)

        self.languageChange()

        self.resize(QSize(325,181).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self,SLOT("close()"))


    def languageChange(self):
        self.setCaption(self.__tr("nanoSIM-1 Setup"))
        self.parms_grpbox.setTitle(self.__tr("Parameters"))
        self.textLabel5.setText(self.__tr("Total Frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame :"))
        self.textLabel3.setText(self.__tr("Temperature :"))
        self.textLabel2_2.setText(self.__tr("0.1 femtosecond"))
        self.textLabel3_2.setText(self.__tr("Kelvin"))
        self.run_sim_btn.setText(self.__tr("Run Simulation"))
        self.cancel_btn.setText(self.__tr("Cancel"))


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

    def serverManager(self):
        print "SimSetupDialog.serverManager(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("SimSetupDialog",s,c)
