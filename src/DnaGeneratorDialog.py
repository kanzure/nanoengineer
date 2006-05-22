# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DnaGeneratorDialog.ui'
#
# Created: Mon May 22 11:19:00 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class DnaGeneratorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("DnaGeneratorDialog")



        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,20,90,30))

        self.seq_linedit = QLineEdit(self,"seq_linedit")
        self.seq_linedit.setGeometry(QRect(100,20,150,24))

        LayoutWidget = QWidget(self,"layout30")
        LayoutWidget.setGeometry(QRect(10,170,220,40))
        layout30 = QHBoxLayout(LayoutWidget,11,6,"layout30")
        spacer1 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30.addItem(spacer1)

        self.ok_btn = QPushButton(LayoutWidget,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,30))
        self.ok_btn.setDefault(1)
        layout30.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(LayoutWidget,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,30))
        layout30.addWidget(self.cancel_btn)

        self.strandBchkbox = QCheckBox(self,"strandBchkbox")
        self.strandBchkbox.setGeometry(QRect(150,100,80,30))
        self.strandBchkbox.setChecked(1)

        self.strandAchkbox = QCheckBox(self,"strandAchkbox")
        self.strandAchkbox.setGeometry(QRect(150,60,80,30))
        self.strandAchkbox.setChecked(1)

        self.dnaTypeButtonGroup = QButtonGroup(self,"dnaTypeButtonGroup")
        self.dnaTypeButtonGroup.setGeometry(QRect(10,50,90,101))

        self.zDnaButton = QRadioButton(self.dnaTypeButtonGroup,"zDnaButton")
        self.zDnaButton.setGeometry(QRect(11,71,70,20))

        self.bDnaButton = QRadioButton(self.dnaTypeButtonGroup,"bDnaButton")
        self.bDnaButton.setGeometry(QRect(10,40,70,31))
        self.bDnaButton.setChecked(1)

        self.aDnaButton = QRadioButton(self.dnaTypeButtonGroup,"aDnaButton")
        self.aDnaButton.setGeometry(QRect(10,20,70,20))

        self.languageChange()

        self.resize(QSize(279,232).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.dnaTypeButtonGroup,SIGNAL("clicked(int)"),self.dnaTypeClicked)

        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Dna Generator"))
        self.textLabel1.setText(self.__tr("Sequence :"))
        self.seq_linedit.setText(self.__tr("GATTACA"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))
        self.strandBchkbox.setText(self.__tr("Strand B"))
        self.strandAchkbox.setText(self.__tr("Strand A"))
        self.dnaTypeButtonGroup.setTitle(self.__tr("DNA type"))
        self.zDnaButton.setText(self.__tr("Z DNA"))
        self.bDnaButton.setText(self.__tr("B DNA"))
        self.aDnaButton.setText(self.__tr("A DNA"))


    def dnaTypeClicked(self,a0):
        print "DnaGeneratorDialog.dnaTypeClicked(int): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("DnaGeneratorDialog",s,c)
