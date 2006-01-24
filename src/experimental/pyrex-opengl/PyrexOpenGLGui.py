# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PyrexOpenGLGui.ui'
#
# Created: Tue Jan 24 10:48:54 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class PyrexOpenGLGui(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("PyrexOpenGL")



        self.frame1 = QFrame(self,"frame1")
        self.frame1.setGeometry(QRect(20,20,640,450))
        self.frame1.setMinimumSize(QSize(400,300))
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)

        self.pushButton1 = QPushButton(self,"pushButton1")
        self.pushButton1.setGeometry(QRect(280,480,111,41))

        self.languageChange()

        self.resize(QSize(689,541).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.pushButton1,SIGNAL("clicked()"),self.pushButton1_clicked)


    def languageChange(self):
        self.setCaption(self.__tr("PyrexOpenGL"))
        self.pushButton1.setText(self.__tr("Quit"))


    def pushButton1_clicked(self):
        print "PyrexOpenGLGui.pushButton1_clicked(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("PyrexOpenGLGui",s,c)
