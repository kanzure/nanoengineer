# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\PlotToolDialog.ui'
#
# Created: Wed Mar 9 21:26:40 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class PlotToolDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("PlotToolDialog")


        PlotToolDialogLayout = QGridLayout(self,1,1,11,6,"PlotToolDialogLayout")

        layout2 = QGridLayout(None,1,1,0,6,"layout2")

        layout1 = QHBoxLayout(None,0,6,"layout1")

        self.plotPB = QPushButton(self,"plotPB")
        layout1.addWidget(self.plotPB)

        self.quitPB = QPushButton(self,"quitPB")
        layout1.addWidget(self.quitPB)

        layout2.addLayout(layout1,2,0)

        self.plotCB = QComboBox(0,self,"plotCB")

        layout2.addWidget(self.plotCB,1,0)

        self.textLabel1 = QLabel(self,"textLabel1")

        layout2.addWidget(self.textLabel1,0,0)

        PlotToolDialogLayout.addLayout(layout2,0,0)

        self.languageChange()

        self.resize(QSize(198,109).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.quitPB,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.plotPB,SIGNAL("clicked()"),self.genPlot)


    def languageChange(self):
        self.setCaption(self.__tr("Plot Tool"))
        self.plotPB.setText(self.__tr("Plot"))
        self.quitPB.setText(self.__tr("Quit"))
        self.textLabel1.setText(self.__tr("Select Jig to Graph:"))


    def genPlot(self):
        print "PlotToolDialog.genPlot(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PlotToolDialog",s,c)
