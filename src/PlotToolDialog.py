# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\PlotToolDialog.ui'
#
# Created: Mon Jul 4 15:46:52 2005
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

        layout5 = QVBoxLayout(None,0,6,"layout5")

        layout2 = QGridLayout(None,1,1,0,6,"layout2")

        layout1 = QHBoxLayout(None,0,6,"layout1")

        self.plot_btn = QPushButton(self,"plot_btn")
        layout1.addWidget(self.plot_btn)

        self.done_btn = QPushButton(self,"done_btn")
        layout1.addWidget(self.done_btn)

        layout2.addLayout(layout1,2,0)

        self.plot_combox = QComboBox(0,self,"plot_combox")

        layout2.addWidget(self.plot_combox,1,0)

        self.textLabel1 = QLabel(self,"textLabel1")

        layout2.addWidget(self.textLabel1,0,0)
        layout5.addLayout(layout2)
        spacer2 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout5.addItem(spacer2)

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.open_trace_file_btn = QPushButton(self,"open_trace_file_btn")
        layout6.addWidget(self.open_trace_file_btn)

        self.open_gnuplot_btn = QPushButton(self,"open_gnuplot_btn")
        layout6.addWidget(self.open_gnuplot_btn)
        layout5.addLayout(layout6)

        PlotToolDialogLayout.addLayout(layout5,0,0)

        self.languageChange()

        self.resize(QSize(264,148).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.done_btn,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.plot_btn,SIGNAL("clicked()"),self.genPlot)
        self.connect(self.open_gnuplot_btn,SIGNAL("clicked()"),self.openGNUplotFile)
        self.connect(self.open_trace_file_btn,SIGNAL("clicked()"),self.openTraceFile)


    def languageChange(self):
        self.setCaption(self.__tr("Plot Tool"))
        self.plot_btn.setText(self.__tr("Plot"))
        self.done_btn.setText(self.__tr("Done"))
        self.textLabel1.setText(self.__tr("Select Jig to Graph:"))
        self.open_trace_file_btn.setText(self.__tr("Open Trace File"))
        self.open_gnuplot_btn.setText(self.__tr("Open GNUplot File"))


    def genPlot(self):
        print "PlotToolDialog.genPlot(): Not implemented yet"

    def openTraceFile(self):
        print "PlotToolDialog.openTraceFile(): Not implemented yet"

    def openGNUplotFile(self):
        print "PlotToolDialog.openGNUplotFile(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PlotToolDialog",s,c)
