# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Tue May 30 20:18:26 2006
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

        SimSetupDialogLayout = QGridLayout(self,1,1,0,0,"SimSetupDialogLayout")

        layout20 = QHBoxLayout(None,4,6,"layout20")
        spacer18 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout20.addItem(spacer18)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout20.addWidget(self.cancel_btn)

        self.run_sim_btn = QPushButton(self,"run_sim_btn")
        self.run_sim_btn.setDefault(1)
        layout20.addWidget(self.run_sim_btn)

        SimSetupDialogLayout.addLayout(layout20,2,0)
        spacer17 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        SimSetupDialogLayout.addItem(spacer17,1,0)

        self.base_frame = QFrame(self,"base_frame")
        self.base_frame.setFrameShape(QFrame.StyledPanel)
        self.base_frame.setFrameShadow(QFrame.Raised)
        base_frameLayout = QVBoxLayout(self.base_frame,3,3,"base_frameLayout")

        self.parms_grpbox = QGroupBox(self.base_frame,"parms_grpbox")
        self.parms_grpbox.setFrameShape(QGroupBox.StyledPanel)
        self.parms_grpbox.setColumnLayout(0,Qt.Vertical)
        self.parms_grpbox.layout().setSpacing(1)
        self.parms_grpbox.layout().setMargin(4)
        parms_grpboxLayout = QVBoxLayout(self.parms_grpbox.layout())
        parms_grpboxLayout.setAlignment(Qt.AlignTop)

        self.parameters_label = QLabel(self.parms_grpbox,"parameters_label")
        self.parameters_label.setPaletteForegroundColor(QColor(0,0,255))
        parms_grpboxLayout.addWidget(self.parameters_label)

        self.line2_4_2 = QFrame(self.parms_grpbox,"line2_4_2")
        self.line2_4_2.setFrameShape(QFrame.HLine)
        self.line2_4_2.setFrameShadow(QFrame.Sunken)
        self.line2_4_2.setMidLineWidth(0)
        self.line2_4_2.setFrameShape(QFrame.HLine)
        parms_grpboxLayout.addWidget(self.line2_4_2)

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
        base_frameLayout.addWidget(self.parms_grpbox)

        self.groupBox2 = QGroupBox(self.base_frame,"groupBox2")
        self.groupBox2.setFrameShape(QGroupBox.StyledPanel)
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(1)
        self.groupBox2.layout().setMargin(4)
        groupBox2Layout = QGridLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        self.sim_options_label = QLabel(self.groupBox2,"sim_options_label")
        self.sim_options_label.setPaletteForegroundColor(QColor(0,0,255))

        groupBox2Layout.addWidget(self.sim_options_label,0,0)

        self.line2_4 = QFrame(self.groupBox2,"line2_4")
        self.line2_4.setFrameShape(QFrame.HLine)
        self.line2_4.setFrameShadow(QFrame.Sunken)
        self.line2_4.setMidLineWidth(0)
        self.line2_4.setFrameShape(QFrame.HLine)

        groupBox2Layout.addWidget(self.line2_4,1,0)

        self.watch_motion_checkbox = QCheckBox(self.groupBox2,"watch_motion_checkbox")
        self.watch_motion_checkbox.setChecked(1)

        groupBox2Layout.addWidget(self.watch_motion_checkbox,2,0)

        self.update_grpbox = QButtonGroup(self.groupBox2,"update_grpbox")
        self.update_grpbox.setFrameShape(QButtonGroup.StyledPanel)
        self.update_grpbox.setFrameShadow(QButtonGroup.Sunken)
        self.update_grpbox.setColumnLayout(0,Qt.Vertical)
        self.update_grpbox.layout().setSpacing(6)
        self.update_grpbox.layout().setMargin(11)
        update_grpboxLayout = QGridLayout(self.update_grpbox.layout())
        update_grpboxLayout.setAlignment(Qt.AlignTop)

        self.update_number_spinbox = QSpinBox(self.update_grpbox,"update_number_spinbox")
        self.update_number_spinbox.setMaxValue(9999)
        self.update_number_spinbox.setMinValue(1)
        self.update_number_spinbox.setValue(1)

        update_grpboxLayout.addWidget(self.update_number_spinbox,1,1)

        self.update_units_combobox = QComboBox(0,self.update_grpbox,"update_units_combobox")

        update_grpboxLayout.addWidget(self.update_units_combobox,1,2)
        spacer2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        update_grpboxLayout.addItem(spacer2,1,3)

        self.update_every_rbtn = QRadioButton(self.update_grpbox,"update_every_rbtn")
        self.update_grpbox.insert( self.update_every_rbtn,1)

        update_grpboxLayout.addWidget(self.update_every_rbtn,1,0)

        self.update_asap_rbtn = QRadioButton(self.update_grpbox,"update_asap_rbtn")
        self.update_asap_rbtn.setChecked(1)
        self.update_grpbox.insert( self.update_asap_rbtn,0)

        update_grpboxLayout.addMultiCellWidget(self.update_asap_rbtn,0,0,0,3)

        groupBox2Layout.addWidget(self.update_grpbox,3,0)
        base_frameLayout.addWidget(self.groupBox2)

        SimSetupDialogLayout.addWidget(self.base_frame,0,0)

        self.languageChange()

        self.resize(QSize(305,293).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.watch_motion_checkbox,SIGNAL("toggled(bool)"),self.update_grpbox.setEnabled)


    def languageChange(self):
        self.setCaption(self.__tr("nanoDynamics-1 Setup"))
        QWhatsThis.add(self,self.__tr("<b>nanoDynamics-1 Setup</b><p>nanoENGINEER-1 Molecular Dynamics Simulator Setup. Enter the parameters of the simulation and click <b>Run Simulation</b>.</p>"))
        self.cancel_btn.setText(self.__tr("Cancel"))
        self.run_sim_btn.setText(self.__tr("Run Simulation"))
        self.parms_grpbox.setTitle(QString.null)
        self.parameters_label.setText(self.__tr("Parameters"))
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
        self.groupBox2.setTitle(QString.null)
        self.sim_options_label.setText(self.__tr("Simulation Options"))
        self.watch_motion_checkbox.setText(self.__tr("Watch motion in real time"))
        QToolTip.add(self.watch_motion_checkbox,self.__tr("Enables real time graphical updates during simulation runs"))
        QWhatsThis.add(self.watch_motion_checkbox,self.__tr("<p><b>Watch Motion In Real Time</b></p>Enables real time graphical updates during simulation runs."))
        self.update_grpbox.setTitle(QString.null)
        self.update_units_combobox.clear()
        self.update_units_combobox.insertItem(self.__tr("frames"))
        self.update_units_combobox.insertItem(self.__tr("seconds"))
        self.update_units_combobox.insertItem(self.__tr("minutes"))
        self.update_units_combobox.insertItem(self.__tr("hours"))
        self.update_every_rbtn.setText(self.__tr("Update every"))
        self.update_asap_rbtn.setText(self.__tr("Update as fast as possible"))


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
