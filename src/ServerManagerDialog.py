# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\atom\cad\src\ServerManagerDialog.ui'
#
# Created: Mon Jun 20 15:02:03 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ServerManagerDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ServerManagerDialog")


        ServerManagerDialogLayout = QVBoxLayout(self,11,6,"ServerManagerDialogLayout")

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.server_listview = QListView(self,"server_listview")
        self.server_listview.addColumn(self.__tr("Server ID"))
        self.server_listview.addColumn(self.__tr("Engine"))
        layout7.addWidget(self.server_listview)

        self.frame4 = QFrame(self,"frame4")
        self.frame4.setFrameShape(QFrame.Box)
        self.frame4.setFrameShadow(QFrame.Raised)
        frame4Layout = QVBoxLayout(self.frame4,11,6,"frame4Layout")

        self.textLabel1 = QLabel(self.frame4,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1)

        self.name_linedit = QLineEdit(self.frame4,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        frame4Layout.addWidget(self.name_linedit)

        self.textLabel1_3 = QLabel(self.frame4,"textLabel1_3")
        self.textLabel1_3.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1_3)

        self.ipaddress_linedit = QLineEdit(self.frame4,"ipaddress_linedit")
        frame4Layout.addWidget(self.ipaddress_linedit)

        layout6 = QGridLayout(None,1,1,0,6,"layout6")

        self.textLabel1_2 = QLabel(self.frame4,"textLabel1_2")
        self.textLabel1_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)

        layout6.addWidget(self.textLabel1_2,0,0)

        self.method_combox = QComboBox(0,self.frame4,"method_combox")

        layout6.addWidget(self.method_combox,1,1)

        self.textLabel1_6 = QLabel(self.frame4,"textLabel1_6")

        layout6.addWidget(self.textLabel1_6,0,1)

        self.platform_combox = QComboBox(0,self.frame4,"platform_combox")

        layout6.addWidget(self.platform_combox,1,0)
        frame4Layout.addLayout(layout6)

        self.textLabel1_4 = QLabel(self.frame4,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1_4)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        self.engine_combox = QComboBox(0,self.frame4,"engine_combox")
        layout27.addWidget(self.engine_combox)
        spacer2_2 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout27.addItem(spacer2_2)
        frame4Layout.addLayout(layout27)

        self.textLabel1_5 = QLabel(self.frame4,"textLabel1_5")
        self.textLabel1_5.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1_5)

        self.program_linedit = QLineEdit(self.frame4,"program_linedit")
        frame4Layout.addWidget(self.program_linedit)

        self.textLabel1_2_2 = QLabel(self.frame4,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1_2_2)

        self.username_linedit = QLineEdit(self.frame4,"username_linedit")
        frame4Layout.addWidget(self.username_linedit)

        self.textLabel1_2_2_2 = QLabel(self.frame4,"textLabel1_2_2_2")
        self.textLabel1_2_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        frame4Layout.addWidget(self.textLabel1_2_2_2)

        self.password_linedit = QLineEdit(self.frame4,"password_linedit")
        self.password_linedit.setEchoMode(QLineEdit.Password)
        frame4Layout.addWidget(self.password_linedit)
        layout7.addWidget(self.frame4)
        ServerManagerDialogLayout.addLayout(layout7)

        layout5 = QHBoxLayout(None,0,6,"layout5")

        self.new_btn = QPushButton(self,"new_btn")
        self.new_btn.setEnabled(1)
        layout5.addWidget(self.new_btn)

        self.del_btn = QPushButton(self,"del_btn")
        layout5.addWidget(self.del_btn)

        self.test_btn = QPushButton(self,"test_btn")
        layout5.addWidget(self.test_btn)

        self.exit_btn = QPushButton(self,"exit_btn")
        layout5.addWidget(self.exit_btn)
        ServerManagerDialogLayout.addLayout(layout5)

        self.languageChange()

        self.resize(QSize(673,677).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.new_btn,SIGNAL("clicked()"),self.addServer)
        self.connect(self.exit_btn,SIGNAL("clicked()"),self,SLOT("close()"))
        self.connect(self.server_listview,SIGNAL("currentChanged(QListViewItem*)"),self.changeServer)
        self.connect(self.engine_combox,SIGNAL("activated(const QString&)"),self.engineChanged)
        self.connect(self.del_btn,SIGNAL("clicked()"),self.deleteServer)


    def languageChange(self):
        self.setCaption(self.__tr("Server Manager"))
        self.server_listview.header().setLabel(0,self.__tr("Server ID"))
        self.server_listview.header().setLabel(1,self.__tr("Engine"))
        self.textLabel1.setText(self.__tr("Server Name :"))
        self.name_linedit.setText(self.__tr("localhost"))
        self.textLabel1_3.setText(self.__tr("IP Address :"))
        self.ipaddress_linedit.setText(self.__tr("127.0.0.1"))
        self.textLabel1_2.setText(self.__tr("Platform :"))
        self.method_combox.clear()
        self.method_combox.insertItem(self.__tr("Local access"))
        self.method_combox.insertItem(self.__tr("Ssh/scp"))
        self.method_combox.insertItem(self.__tr("Rsh/rcp"))
        self.method_combox.insertItem(self.__tr("Telnet/ftp"))
        self.textLabel1_6.setText(self.__tr("Method:"))
        self.platform_combox.clear()
        self.platform_combox.insertItem(self.__tr("Linux"))
        self.platform_combox.insertItem(self.__tr("Mac OS"))
        self.platform_combox.insertItem(self.__tr("Windows"))
        self.textLabel1_4.setText(self.__tr("Engine :"))
        self.engine_combox.clear()
        self.engine_combox.insertItem(self.__tr("PC GAMESS"))
        self.engine_combox.insertItem(self.__tr("nanoSIM-1"))
        self.engine_combox.insertItem(self.__tr("GAMESS"))
        self.textLabel1_5.setText(self.__tr("Executing Program :"))
        self.program_linedit.setText(self.__tr("C:\\PCGAMESS"))
        self.textLabel1_2_2.setText(self.__tr("Username :"))
        self.username_linedit.setText(self.__tr("nanorex"))
        self.textLabel1_2_2_2.setText(self.__tr("Password :"))
        self.password_linedit.setText(self.__tr("nanorex"))
        self.new_btn.setText(self.__tr("New"))
        self.del_btn.setText(self.__tr("Delete"))
        self.test_btn.setText(self.__tr("Test"))
        self.exit_btn.setText(self.__tr("Exit"))


    def addServer(self):
        print "ServerManagerDialog.addServer(): Not implemented yet"

    def changeServer(self):
        print "ServerManagerDialog.changeServer(): Not implemented yet"

    def deleteServer(self):
        print "ServerManagerDialog.deleteServer(): Not implemented yet"

    def engineChanged(self):
        print "ServerManagerDialog.engineChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ServerManagerDialog",s,c)
