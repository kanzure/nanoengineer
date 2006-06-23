# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'JobManagerDialog.ui'
#
# Created: Tue Sep 13 16:00:26 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable

image0_data = [
"22 22 12 1",
". c None",
"j c #000000",
"i c #2b2b86",
"# c #3737a9",
"g c #4242ce",
"d c #525252",
"f c #6f6fdd",
"c c #787878",
"e c #8e8ee4",
"b c #919191",
"a c #aaaaaa",
"h c #ffffff",
"......................",
"......................",
"......................",
".#abcccccccccccccccd#.",
".#eefffffffffffffffg#.",
".#g###########h#h#hi#.",
".#jjjjjjjjjjjjjjjjjj#.",
".#hhhhh#hhhhhh#hhhhh#.",
".#hhhhh#hhhhhh#hhhhh#.",
".####################.",
".#hhhhh#hhhhhh#hhhhh#.",
".#hhhhh#hhhhhh#hhhhh#.",
".####################.",
".#hhhhh#hhhhhh#hhhhh#.",
".#hhhhh#hhhhhh#hhhhh#.",
".####################.",
".#hhhhh#hhhhhh#hhhhh#.",
".#hhhhh#hhhhhh#hhhhh#.",
".####################.",
"......................",
"......................",
"......................"
]

class JobManagerDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("JobManagerDialog")

        self.setIcon(self.image0)

        JobManagerDialogLayout = QVBoxLayout(self,11,6,"JobManagerDialogLayout")

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QVBoxLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        self.job_table = QTable(self.groupBox1,"job_table")
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Name"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Engine"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Calculation"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Description"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Status"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Server Id"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Job Id"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Time"))
        self.job_table.setNumRows(self.job_table.numRows() + 1)
        self.job_table.verticalHeader().setLabel(self.job_table.numRows() - 1,self.__tr("1"))
        self.job_table.setNumRows(1)
        self.job_table.setNumCols(8)
        self.job_table.setSorting(0)
        self.job_table.setSelectionMode(QTable.SingleRow)
        groupBox1Layout.addWidget(self.job_table)

        layout6 = QHBoxLayout(None,0,6,"layout6")

        self.start_btn = QPushButton(self.groupBox1,"start_btn")
        self.start_btn.setEnabled(0)
        layout6.addWidget(self.start_btn)

        self.stop_btn = QPushButton(self.groupBox1,"stop_btn")
        self.stop_btn.setEnabled(0)
        layout6.addWidget(self.stop_btn)

        self.edit_btn = QPushButton(self.groupBox1,"edit_btn")
        self.edit_btn.setEnabled(0)
        layout6.addWidget(self.edit_btn)

        self.view_btn = QPushButton(self.groupBox1,"view_btn")
        self.view_btn.setEnabled(0)
        layout6.addWidget(self.view_btn)

        self.delete_btn = QPushButton(self.groupBox1,"delete_btn")
        self.delete_btn.setEnabled(0)
        layout6.addWidget(self.delete_btn)

        self.move_btn = QPushButton(self.groupBox1,"move_btn")
        self.move_btn.setEnabled(0)
        layout6.addWidget(self.move_btn)
        spacer1 = QSpacerItem(280,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout6.addItem(spacer1)
        groupBox1Layout.addLayout(layout6)
        JobManagerDialogLayout.addWidget(self.groupBox1)

        layout2 = QHBoxLayout(None,0,6,"layout2")

        self.refresh_btn = QPushButton(self,"refresh_btn")
        layout2.addWidget(self.refresh_btn)

        self.filter_btn = QPushButton(self,"filter_btn")
        layout2.addWidget(self.filter_btn)
        spacer2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout2.addItem(spacer2)

        self.close_btn = QPushButton(self,"close_btn")
        layout2.addWidget(self.close_btn)
        JobManagerDialogLayout.addLayout(layout2)

        self.languageChange()

        self.resize(QSize(1009,258).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.close_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.job_table,SIGNAL("clicked(int,int,int,const QPoint&)"),self.cell_clicked)
        self.connect(self.delete_btn,SIGNAL("clicked()"),self.delete_job)
        self.connect(self.refresh_btn,SIGNAL("clicked()"),self.refresh_job_table)
        self.connect(self.start_btn,SIGNAL("clicked()"),self.startJob)
        self.connect(self.stop_btn,SIGNAL("clicked()"),self.stopJob)


    def languageChange(self):
        self.setCaption(self.__tr("NanoEngineer-1 Job Manager"))
        self.groupBox1.setTitle(self.__tr("Jobs"))
        self.job_table.horizontalHeader().setLabel(0,self.__tr("Name"))
        self.job_table.horizontalHeader().setLabel(1,self.__tr("Engine"))
        self.job_table.horizontalHeader().setLabel(2,self.__tr("Calculation"))
        self.job_table.horizontalHeader().setLabel(3,self.__tr("Description"))
        self.job_table.horizontalHeader().setLabel(4,self.__tr("Status"))
        self.job_table.horizontalHeader().setLabel(5,self.__tr("Server Id"))
        self.job_table.horizontalHeader().setLabel(6,self.__tr("Job Id"))
        self.job_table.horizontalHeader().setLabel(7,self.__tr("Time"))
        self.job_table.verticalHeader().setLabel(0,self.__tr("1"))
        self.start_btn.setText(self.__tr("Start"))
        self.stop_btn.setText(self.__tr("Stop"))
        self.edit_btn.setText(self.__tr("Edit"))
        self.view_btn.setText(self.__tr("View"))
        self.delete_btn.setText(self.__tr("Delete"))
        self.move_btn.setText(self.__tr("Move"))
        self.refresh_btn.setText(self.__tr("Refresh"))
        self.filter_btn.setText(self.__tr("Filter..."))
        self.close_btn.setText(self.__tr("Close"))


    def cell_clicked(self):
        print "JobManagerDialog.cell_clicked(): Not implemented yet"

    def delete_job(self):
        print "JobManagerDialog.delete_job(): Not implemented yet"

    def refresh_job_table(self):
        print "JobManagerDialog.refresh_job_table(): Not implemented yet"

    def startJob(self):
        print "JobManagerDialog.startJob(): Not implemented yet"

    def stopJob(self):
        print "JobManagerDialog.stopJob(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("JobManagerDialog",s,c)
