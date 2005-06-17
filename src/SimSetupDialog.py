# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\SimSetupDialog.ui'
#
# Created: Fri Jun 17 09:54:10 2005
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

        layout31 = QHBoxLayout(None,0,6,"layout31")

        layout29 = QVBoxLayout(None,0,6,"layout29")

        self.namelbl = QLabel(self,"namelbl")
        self.namelbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.namelbl)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1)

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel1_2)
        layout31.addLayout(layout29)

        layout30 = QVBoxLayout(None,0,6,"layout30")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        layout30.addWidget(self.name_linedit)

        self.description_linedit = QLineEdit(self,"description_linedit")
        self.description_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.description_linedit.setFrameShadow(QLineEdit.Sunken)
        self.description_linedit.setMaxLength(80)
        layout30.addWidget(self.description_linedit)

        layout28 = QHBoxLayout(None,0,6,"layout28")

        self.calculate_combox = QComboBox(0,self,"calculate_combox")
        layout28.addWidget(self.calculate_combox)
        spacer3 = QSpacerItem(167,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout28.addItem(spacer3)
        layout30.addLayout(layout28)
        layout31.addLayout(layout30)

        SimSetupDialogLayout.addLayout(layout31,0,0)

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

        self.server_grpbox = QGroupBox(self,"server_grpbox")
        self.server_grpbox.setColumnLayout(0,Qt.Vertical)
        self.server_grpbox.layout().setSpacing(6)
        self.server_grpbox.layout().setMargin(11)
        server_grpboxLayout = QHBoxLayout(self.server_grpbox.layout())
        server_grpboxLayout.setAlignment(Qt.AlignTop)

        self.server_combox = QComboBox(0,self.server_grpbox,"server_combox")
        server_grpboxLayout.addWidget(self.server_combox)

        self.server_manager_btn = QPushButton(self.server_grpbox,"server_manager_btn")
        server_grpboxLayout.addWidget(self.server_manager_btn)

        SimSetupDialogLayout.addWidget(self.server_grpbox,2,0)

        layout28_2 = QHBoxLayout(None,0,6,"layout28_2")

        self.queue_job_btn = QPushButton(self,"queue_job_btn")
        layout28_2.addWidget(self.queue_job_btn)

        self.launch_job_btn = QPushButton(self,"launch_job_btn")
        self.launch_job_btn.setDefault(1)
        layout28_2.addWidget(self.launch_job_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout28_2.addWidget(self.cancel_btn)

        SimSetupDialogLayout.addLayout(layout28_2,3,0)

        self.languageChange()

        self.resize(QSize(366,365).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.launch_job_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.queue_job_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.server_manager_btn,SIGNAL("clicked()"),self.serverManager)


    def languageChange(self):
        self.setCaption(self.__tr("nanoSIM-1 Setup"))
        self.namelbl.setText(self.__tr("Name :"))
        self.textLabel1.setText(self.__tr("Description :"))
        self.textLabel1_2.setText(self.__tr("Calculate :"))
        self.name_linedit.setText(QString.null)
        self.description_linedit.setText(QString.null)
        self.calculate_combox.clear()
        self.calculate_combox.insertItem(self.__tr("Trajectory"))
        self.calculate_combox.insertItem(self.__tr("Optimization"))
        self.parms_grpbox.setTitle(self.__tr("Parameters"))
        self.textLabel5.setText(self.__tr("Total Frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame :"))
        self.textLabel3.setText(self.__tr("Temperature :"))
        self.textLabel2_2.setText(self.__tr("0.1 femtosecond"))
        self.textLabel3_2.setText(self.__tr("Kelvin"))
        self.server_grpbox.setTitle(self.__tr("Server"))
        self.server_combox.clear()
        self.server_combox.insertItem(self.__tr("My Computer"))
        self.server_manager_btn.setText(self.__tr("Server Manager..."))
        self.queue_job_btn.setText(self.__tr("Queue Job"))
        self.launch_job_btn.setText(self.__tr("Launch Job"))
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
