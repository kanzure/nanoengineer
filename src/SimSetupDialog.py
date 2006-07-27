# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SimSetupDialog.ui'
#
# Created: Wed Jul 26 23:37:19 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\xc5\x49\x44\x41\x54\x38\x8d\xb5\x94\xbd\x0d\x83" \
    "\x30\x14\x84\xef\xd2\x66\x02\x32\x42\xa6\xc0\x63" \
    "\xf8\x51\x67\x2a\xea\xb0\x06\x5b\xd0\x45\xe9\xc2" \
    "\x04\xd4\x97\x26\x41\xfc\x39\x82\x07\x79\x92\x8b" \
    "\xb3\xe4\xcf\x3e\x59\x77\x94\x84\x23\xe7\x74\x28" \
    "\xed\x0b\xb4\xc2\x44\x52\x56\xd8\xfe\xe7\x46\x8b" \
    "\x92\xa4\xb2\x6b\x54\x76\x8d\x3e\x1a\xde\x45\x00" \
    "\x2a\xbb\xa6\xbf\xe0\x76\xbe\x42\x12\xdd\x96\xa3" \
    "\xc5\x5e\xb4\x8f\x27\x86\xda\x35\x92\x10\x2d\x0a" \
    "\xc0\xc8\x6e\x9e\xe7\x2e\xeb\x27\x00\xa8\xee\x15" \
    "\x25\xb1\x7d\xb5\x00\x80\x10\xc2\xe8\x73\xa6\xfa" \
    "\xa7\xe5\xe9\x46\x08\x41\x75\x5d\x73\xa8\xb7\xc0" \
    "\x67\xc0\x29\x6c\x2b\x7c\x04\x1c\x1e\xde\x0a\x4f" \
    "\xbe\xd0\x03\x5f\x05\x5c\x03\xcf\x2e\x19\x66\x09" \
    "\xf3\x26\x22\x95\x30\x7a\xdb\x86\xe4\x62\xc2\xdc" \
    "\x6d\x93\x4c\xd8\x9e\x22\x58\x4a\x98\xdb\x72\x6a" \
    "\xfe\x53\xb0\x47\xce\x1b\x98\xac\x42\x98\x41\x7d" \
    "\x52\x01\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"

class SimSetupDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("SimSetupDialog")

        self.setIcon(self.image0)
        self.setModal(1)


        self.base_frame = QFrame(self,"base_frame")
        self.base_frame.setGeometry(QRect(0,0,336,304))
        self.base_frame.setFrameShape(QFrame.StyledPanel)
        self.base_frame.setFrameShadow(QFrame.Raised)

        self.groupBox2 = QGroupBox(self.base_frame,"groupBox2")
        self.groupBox2.setGeometry(QRect(6,165,324,133))
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

        self.update_btngrp = QButtonGroup(self.groupBox2,"update_btngrp")
        self.update_btngrp.setFrameShape(QButtonGroup.StyledPanel)
        self.update_btngrp.setFrameShadow(QButtonGroup.Sunken)
        self.update_btngrp.setColumnLayout(0,Qt.Vertical)
        self.update_btngrp.layout().setSpacing(6)
        self.update_btngrp.layout().setMargin(11)
        update_btngrpLayout = QGridLayout(self.update_btngrp.layout())
        update_btngrpLayout.setAlignment(Qt.AlignTop)

        self.update_number_spinbox = QSpinBox(self.update_btngrp,"update_number_spinbox")
        self.update_number_spinbox.setMaxValue(9999)
        self.update_number_spinbox.setMinValue(1)
        self.update_number_spinbox.setValue(1)

        update_btngrpLayout.addWidget(self.update_number_spinbox,1,1)

        self.update_units_combobox = QComboBox(0,self.update_btngrp,"update_units_combobox")

        update_btngrpLayout.addWidget(self.update_units_combobox,1,2)
        spacer2 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        update_btngrpLayout.addItem(spacer2,1,3)

        self.update_every_rbtn = QRadioButton(self.update_btngrp,"update_every_rbtn")
        self.update_btngrp.insert( self.update_every_rbtn,1)

        update_btngrpLayout.addWidget(self.update_every_rbtn,1,0)

        self.update_asap_rbtn = QRadioButton(self.update_btngrp,"update_asap_rbtn")
        self.update_asap_rbtn.setChecked(1)
        self.update_btngrp.insert( self.update_asap_rbtn,0)

        update_btngrpLayout.addMultiCellWidget(self.update_asap_rbtn,0,0,0,3)

        groupBox2Layout.addWidget(self.update_btngrp,3,0)

        self.parms_grpbox = QGroupBox(self.base_frame,"parms_grpbox")
        self.parms_grpbox.setGeometry(QRect(6,8,324,150))
        self.parms_grpbox.setFrameShape(QGroupBox.StyledPanel)

        self.potential_energy_checkbox = QCheckBox(self.parms_grpbox,"potential_energy_checkbox")
        self.potential_energy_checkbox.setGeometry(QRect(20,121,180,20))

        self.parameters_label = QLabel(self.parms_grpbox,"parameters_label")
        self.parameters_label.setGeometry(QRect(4,4,316,17))
        self.parameters_label.setPaletteForegroundColor(QColor(0,0,255))

        self.line2_4_2 = QFrame(self.parms_grpbox,"line2_4_2")
        self.line2_4_2.setGeometry(QRect(4,21,316,2))
        self.line2_4_2.setFrameShape(QFrame.HLine)
        self.line2_4_2.setFrameShadow(QFrame.Sunken)
        self.line2_4_2.setMidLineWidth(0)
        self.line2_4_2.setFrameShape(QFrame.HLine)

        self.textLabel3_2 = QLabel(self.parms_grpbox,"textLabel3_2")
        self.textLabel3_2.setGeometry(QRect(201,89,117,23))

        self.tempSB = QSpinBox(self.parms_grpbox,"tempSB")
        self.tempSB.setGeometry(QRect(131,89,62,23))
        self.tempSB.setMaxValue(99999)
        self.tempSB.setValue(300)

        self.nframesSB = QSpinBox(self.parms_grpbox,"nframesSB")
        self.nframesSB.setGeometry(QRect(131,31,62,23))
        self.nframesSB.setMaxValue(90000)
        self.nframesSB.setMinValue(1)
        self.nframesSB.setLineStep(15)
        self.nframesSB.setValue(900)

        self.textLabel2 = QLabel(self.parms_grpbox,"textLabel2")
        self.textLabel2.setGeometry(QRect(6,60,117,23))
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel3 = QLabel(self.parms_grpbox,"textLabel3")
        self.textLabel3.setGeometry(QRect(6,89,117,23))
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.stepsperSB = QSpinBox(self.parms_grpbox,"stepsperSB")
        self.stepsperSB.setGeometry(QRect(131,60,62,23))
        self.stepsperSB.setMaxValue(99999)
        self.stepsperSB.setMinValue(1)
        self.stepsperSB.setValue(10)

        self.textLabel2_2 = QLabel(self.parms_grpbox,"textLabel2_2")
        self.textLabel2_2.setGeometry(QRect(201,60,117,23))

        self.textLabel5 = QLabel(self.parms_grpbox,"textLabel5")
        self.textLabel5.setGeometry(QRect(6,31,117,23))
        self.textLabel5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        LayoutWidget = QWidget(self,"layout20")
        LayoutWidget.setGeometry(QRect(10,310,310,40))
        layout20 = QHBoxLayout(LayoutWidget,4,6,"layout20")
        spacer18 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout20.addItem(spacer18)

        self.cancel_btn = QPushButton(LayoutWidget,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout20.addWidget(self.cancel_btn)

        self.run_sim_btn = QPushButton(LayoutWidget,"run_sim_btn")
        self.run_sim_btn.setDefault(1)
        layout20.addWidget(self.run_sim_btn)

        self.languageChange()

        self.resize(QSize(337,361).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.watch_motion_checkbox,SIGNAL("toggled(bool)"),self.update_btngrp.setEnabled)


    def languageChange(self):
        self.setCaption(self.__tr("NanoDynamics-1"))
        QToolTip.add(self,self.__tr("NanoDynamics-1 Simulator Setup Dialog"))
        self.groupBox2.setTitle(QString.null)
        self.sim_options_label.setText(self.__tr("Simulation Options"))
        self.watch_motion_checkbox.setText(self.__tr("Watch motion in real time"))
        QToolTip.add(self.watch_motion_checkbox,self.__tr("Enables real time graphical updates during simulation runs"))
        self.update_btngrp.setTitle(QString.null)
        QToolTip.add(self.update_number_spinbox,self.__tr("Specify how often to update the screen during the simulation."))
        self.update_units_combobox.clear()
        self.update_units_combobox.insertItem(self.__tr("frames"))
        self.update_units_combobox.insertItem(self.__tr("seconds"))
        self.update_units_combobox.insertItem(self.__tr("minutes"))
        self.update_units_combobox.insertItem(self.__tr("hours"))
        QToolTip.add(self.update_units_combobox,self.__tr("Specify how often to update the screen during the simulation."))
        self.update_every_rbtn.setText(self.__tr("Update every"))
        QToolTip.add(self.update_every_rbtn,self.__tr("Specify how often to update the screen during the simulation."))
        self.update_asap_rbtn.setText(self.__tr("Update as fast as possible"))
        QToolTip.add(self.update_asap_rbtn,self.__tr("Update every 2 seconds, or faster if it doesn't slow simulation by more than 20%"))
        self.parms_grpbox.setTitle(QString.null)
        self.potential_energy_checkbox.setText(self.__tr("Plot energy in tracefile"))
        self.parameters_label.setText(self.__tr("Parameters"))
        self.textLabel3_2.setText(self.__tr("Kelvin"))
        QToolTip.add(self.tempSB,self.__tr("Temperature"))
        QToolTip.add(self.nframesSB,self.__tr("Total Frames value"))
        self.textLabel2.setText(self.__tr("Steps per Frame :"))
        self.textLabel3.setText(self.__tr("Temperature :"))
        QToolTip.add(self.stepsperSB,self.__tr("Steps per Frame"))
        self.textLabel2_2.setText(self.__tr("0.1 femtosecond"))
        self.textLabel5.setText(self.__tr("Total Frames:"))
        self.cancel_btn.setText(self.__tr("Cancel"))
        self.run_sim_btn.setText(self.__tr("Run Simulation"))


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
