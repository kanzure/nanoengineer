# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Fri Apr 14 13:32:51 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
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

        SimSetupDialogLayout.addWidget(self.parms_grpbox,0,0)

        layout28 = QHBoxLayout(None,0,6,"layout28")

        self.run_sim_btn = QPushButton(self,"run_sim_btn")
        self.run_sim_btn.setDefault(1)
        layout28.addWidget(self.run_sim_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout28.addWidget(self.cancel_btn)

        SimSetupDialogLayout.addLayout(layout28,2,0)

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QGridLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        self.watch_motion_checkbox = QCheckBox(self.groupBox2,"watch_motion_checkbox")
        self.watch_motion_checkbox.setChecked(1)

        groupBox2Layout.addWidget(self.watch_motion_checkbox,0,0)

        SimSetupDialogLayout.addWidget(self.groupBox2,1,0)

        self.languageChange()

        self.resize(QSize(333,258).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.close)


    def languageChange(self):
        self.setCaption(self.__tr("nanoDynamics-1 Setup"))
        QWhatsThis.add(self,self.__tr("<b>nanoDynamics-1 Setup</b><p>nanoENGINEER-1 Molecular Dynamics Simulator Setup. Enter the parameters of the simulation and click <b>Run Simulation</b>.</p>"))
        self.parms_grpbox.setTitle(self.__tr("Parameters"))
        self.textLabel5.setText(self.__tr("Total Frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame :"))
        self.textLabel3.setText(self.__tr("Temperature :"))
        QToolTip.add(self.nframesSB,self.__tr("Total Frames value"))
        QWhatsThis.add(self.nframesSB,self.__tr("<b>Total Frames</b><p>The number of frames for the simulation run.</p>"))
        QToolTip.add(self.stepsperSB,self.__tr("Steps per Frame"))
        QWhatsThis.add(self.stepsperSB,self.__tr("<b>Steps per Frame</b><p>The time duration between frames. 10 steps = 1 femtosecond.</p>"))
        QToolTip.add(self.tempSB,self.__tr("Temperature"))
        QWhatsThis.add(self.tempSB,self.__tr("<b>Temperature</b><p>The temperature of the simulation in Kelvin (300 K = room temp)</p>"))
        self.textLabel2_2.setText(self.__tr("0.1 femtosecond"))
        self.textLabel3_2.setText(self.__tr("Kelvin"))
        self.run_sim_btn.setText(self.__tr("Run Simulation"))
        self.cancel_btn.setText(self.__tr("Cancel"))
        self.groupBox2.setTitle(self.__tr("Simulation Options"))
        self.watch_motion_checkbox.setText(self.__tr("Watch motion in real time"))
        QToolTip.add(self.watch_motion_checkbox,self.__tr("Enables real time graphical updates during simulation runs"))
        QWhatsThis.add(self.watch_motion_checkbox,self.__tr("<p><b>Watch Motion In Real Time</b></p>Enables real time graphical updates during simulation runs."))


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
