# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\atom\cad\src\SimSetupDialog.ui'
#
# Created: Fri Mar 11 16:08:26 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x01" \
    "\x40\x49\x44\x41\x54\x78\x9c\xd5\x95\x31\x4b\xc3" \
    "\x40\x18\x86\x9f\x4f\x3a\x74\x71\x6a\x71\x75\x74" \
    "\xea\x2e\x37\xfb\x0f\x1a\x68\x26\x97\x42\x32\x14" \
    "\x97\xe2\xdc\x21\xe2\x16\xb2\x45\x68\xc0\x41\x07" \
    "\x89\x12\xc1\x1f\x20\x88\xcb\xe1\x5f\x70\x74\x15" \
    "\x5a\x10\x97\x6e\xe7\x50\x92\xd4\x26\xb6\x49\xa5" \
    "\x43\x5f\x38\x72\xf7\x91\x3c\xbc\xbc\xdf\xdd\x45" \
    "\xb4\xd6\x6c\x43\x7b\x5b\xa1\xee\x24\xb8\x91\x4e" \
    "\xde\xf4\xb3\x19\x9e\x8f\x36\x06\x05\xbe\xc7\xb1" \
    "\x3a\x91\x74\x2d\x69\xf3\x94\x52\x26\x89\xc7\x1b" \
    "\x83\x2d\xdb\x45\x6b\x9d\x81\x1b\xcb\x2f\x74\x7b" \
    "\x4e\x6d\xe8\xe3\x7d\x54\xa8\xad\xcc\xf8\x96\x6b" \
    "\xda\x34\x69\xd3\x64\x6a\x3a\x4c\x4d\x07\x11\x81" \
    "\x28\x62\xf2\xf9\x0e\x90\x3d\x2b\x83\xaf\xbe\x2f" \
    "\x19\x32\x20\x20\x24\x20\x04\xe0\xe5\xe1\x0c\x80" \
    "\x8f\xbb\x1b\x5a\x4f\xaf\x00\xb4\x0e\x8e\x4a\xbf" \
    "\x2f\x44\x91\x3a\x1d\xed\x5f\x10\x10\x72\x4a\x7f" \
    "\x5e\x94\x3e\x96\x2d\x24\xf1\x98\xc3\x2f\xc0\x75" \
    "\xe7\x75\xa7\x3c\xba\x52\xc7\x43\x06\x00\x39\x94" \
    "\x3c\xc7\x6e\xcf\xc9\x61\x29\xbc\x2a\xb8\x4c\x96" \
    "\xed\x52\x67\xd7\x14\xc0\x22\x30\x91\x19\x13\x99" \
    "\x21\x42\x36\xc0\x60\xd9\x4e\x5e\xc3\xcc\x87\x14" \
    "\xa1\xb5\x1c\xd7\x55\xa1\x79\x49\x5c\xdc\x93\xff" \
    "\x02\x07\xbe\x87\x65\xff\xdd\x8c\x75\x0a\x7c\xef" \
    "\xd7\x5a\xaa\xdc\xc7\x4a\x29\x93\xce\x17\x8f\xed" \
    "\x2a\x6d\x2d\xe3\x95\x8e\x17\x9d\x2e\x6b\x9d\xf3" \
    "\x4a\x51\x6c\xa2\xdd\xfb\x83\xfc\x00\xc2\x71\x5d" \
    "\x46\x4b\x9b\x9c\x29\x00\x00\x00\x00\x49\x45\x4e" \
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
        self.nframesSB.setValue(900)

        layout28.addWidget(self.nframesSB,1,0)

        self.stepsperSB = QSpinBox(self,"stepsperSB")
        self.stepsperSB.setMaxValue(99999)
        self.stepsperSB.setMinValue(1)
        self.stepsperSB.setValue(10)

        layout28.addWidget(self.stepsperSB,3,0)

        self.tempSB = QSpinBox(self,"tempSB")
        self.tempSB.setMaxValue(99999)
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
        self.CancelButton.setDefault(0)
        layout27.addWidget(self.CancelButton)
        SimSetupDialogLayout.addLayout(layout27)

        self.languageChange()

        self.resize(QSize(347,321).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.MovieButton,SIGNAL("clicked()"),self.createMoviePressed)
        self.connect(self.CancelButton,SIGNAL("clicked()"),self,SLOT("close()"))


    def languageChange(self):
        self.setCaption(self.__tr("Simulator Setup"))
        self.textLabel5.setText(self.__tr("Total frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame (0.1 femtosecond):"))
        self.textLabel3.setText(self.__tr("Temperature (Kelvins):"))
        self.MovieButton.setText(self.__tr("Run Simulation"))
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
