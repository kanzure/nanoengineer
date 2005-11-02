# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'NanotubeGeneratorDialog.ui'
#
# Created: Wed Nov 2 12:23:02 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class NanotubeGeneratorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("NanotubeGeneratorDialog")



        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,10,170,20))
        textLabel1_font = QFont(self.textLabel1.font())
        textLabel1_font.setPointSize(16)
        self.textLabel1.setFont(textLabel1_font)

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,40,70,20))

        self.textEdit1 = QTextEdit(self,"textEdit1")
        self.textEdit1.setGeometry(QRect(90,40,50,20))

        self.textLabel3 = QLabel(self,"textLabel3")
        self.textLabel3.setGeometry(QRect(170,40,20,20))

        self.textEdit2 = QTextEdit(self,"textEdit2")
        self.textEdit2.setGeometry(QRect(200,40,50,20))

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,70,120,20))

        self.textEdit3 = QTextEdit(self,"textEdit3")
        self.textEdit3.setGeometry(QRect(130,70,100,20))

        self.languageChange()

        self.resize(QSize(299,110).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.textEdit1,SIGNAL("textChanged()"),self.setN)
        self.connect(self.textEdit2,SIGNAL("textChanged()"),self.setM)
        self.connect(self.textEdit3,SIGNAL("textChanged()"),self.setLength)


    def languageChange(self):
        self.setCaption(self.__tr("Form1"))
        self.textLabel1.setText(self.__tr("Nanotube Generator"))
        self.textLabel2.setText(self.__tr("Chirality     N"))
        self.textLabel3.setText(self.__tr("M"))
        self.textLabel4.setText(self.__tr("Length (nanometers)"))


    def setN(self):
        print "NanotubeGeneratorDialog.setN(): Not implemented yet"

    def setM(self):
        print "NanotubeGeneratorDialog.setM(): Not implemented yet"

    def setLength(self):
        print "NanotubeGeneratorDialog.setLength(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("NanotubeGeneratorDialog",s,c)
