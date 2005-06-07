# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\JobManagerDialog.ui'
#
# Created: Tue Jun 7 15:25:49 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *
from qttable import QTable

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x16\x00\x00\x00\x16" \
    "\x08\x06\x00\x00\x00\xc4\xb4\x6c\x3b\x00\x00\x00" \
    "\xa7\x49\x44\x41\x54\x78\x9c\xed\x92\x31\x0a\x83" \
    "\x30\x14\x86\xbf\x94\x8e\xde\xa2\xab\x7b\xa4\x07" \
    "\x69\x0e\xe2\x21\x7a\x16\x3b\x7b\x08\x73\x85\xb8" \
    "\x2a\x81\x4e\x76\x10\xe9\x94\x2e\x26\xa5\x68\xa5" \
    "\x48\xba\xe5\x83\x47\xe0\x7f\xe1\x1b\x7e\x1e\x24" \
    "\x66\x04\x80\x94\x95\x2b\x4b\x81\xb5\x16\x6b\xed" \
    "\x6e\x99\x31\x86\xbe\x57\x68\xad\xc4\xd1\x87\x5d" \
    "\x77\x06\x60\x9a\x9e\xbb\xc5\xc3\xf0\x00\x5a\x00" \
    "\x82\xb8\xae\xef\x8c\x63\xfb\xb3\xa4\x69\x2e\x14" \
    "\xc5\xed\xe3\xcd\xf3\x2b\x59\x76\x7a\x7f\x92\xb2" \
    "\x72\x40\x94\x99\x5d\x1c\xbc\xdc\x39\xb7\x18\x29" \
    "\xab\xd5\x7c\x6b\xe7\x09\xe2\xd8\x84\xab\x88\x29" \
    "\xd5\x5a\x09\xbc\x78\x8d\x6f\xf9\xd6\x6e\xd1\x71" \
    "\x6c\x52\x15\x81\x54\x45\xe0\xbf\x55\x24\x00\x5e" \
    "\xdb\xf8\x56\x33\xba\x04\x52\x98\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"

class JobManagerDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
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
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Server"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Job Id"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Time"))
        self.job_table.setNumCols(self.job_table.numCols() + 1)
        self.job_table.horizontalHeader().setLabel(self.job_table.numCols() - 1,self.__tr("Start Time"))
        self.job_table.setNumRows(1)
        self.job_table.setNumCols(9)
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

        self.resize(QSize(883,252).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.close_btn,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.job_table,SIGNAL("clicked(int,int,int,const QPoint&)"),self.cell_clicked)
        self.connect(self.delete_btn,SIGNAL("clicked()"),self.delete_job)
        self.connect(self.refresh_btn,SIGNAL("clicked()"),self.refresh_job_table)


    def languageChange(self):
        self.setCaption(self.__tr("nanoENGINEER-1 Job Manager"))
        self.groupBox1.setTitle(self.__tr("Jobs"))
        self.job_table.horizontalHeader().setLabel(0,self.__tr("Name"))
        self.job_table.horizontalHeader().setLabel(1,self.__tr("Engine"))
        self.job_table.horizontalHeader().setLabel(2,self.__tr("Calculation"))
        self.job_table.horizontalHeader().setLabel(3,self.__tr("Description"))
        self.job_table.horizontalHeader().setLabel(4,self.__tr("Status"))
        self.job_table.horizontalHeader().setLabel(5,self.__tr("Server"))
        self.job_table.horizontalHeader().setLabel(6,self.__tr("Job Id"))
        self.job_table.horizontalHeader().setLabel(7,self.__tr("Time"))
        self.job_table.horizontalHeader().setLabel(8,self.__tr("Start Time"))
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

    def __tr(self,s,c = None):
        return qApp.translate("JobManagerDialog",s,c)
