# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\StatPropDialog.ui'
#
# Created: Sat Oct 9 08:13:23 2004
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *


class StatPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("StatPropDialog")

        self.setSizeGripEnabled(1)


        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setGeometry(QRect(272,71,30,27))

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(21,121,82,27))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setGeometry(QRect(171,71,44,27))
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(217,121,82,27))

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(119,121,82,27))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setGeometry(QRect(223,71,40,27))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setGeometry(QRect(21,11,42,26))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setGeometry(QRect(21,71,42,23))
        self.atomsTextLabel.setMouseTracking(0)

        self.nameTextLabel_2 = QLabel(self,"nameTextLabel_2")
        self.nameTextLabel_2.setGeometry(QRect(3,41,60,26))
        self.nameTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        self.atomsComboBox.setGeometry(QRect(69,71,85,23))

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setGeometry(QRect(68,11,211,21))
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)

        self.tempSpinBox = QSpinBox(self,"tempSpinBox")
        self.tempSpinBox.setGeometry(QRect(70,40,55,23))
        self.tempSpinBox.setMaxValue(1000)
        self.tempSpinBox.setValue(300)

        self.languageChange()

        self.resize(QSize(339,167).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeStatColor)
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)



    def languageChange(self):
        self.setCaption(self.__tr("Stat Properties"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.nameTextLabel_2.setText(self.__tr("Temp (K):"))
        self.nameLineEdit.setText(QString.null)


    def applyButtonPressed(self):
        print "StatPropDialog.applyButtonPressed(): Not implemented yet"

    def changeStatColor(self):
        print "StatPropDialog.changeStatColor(): Not implemented yet"

    def propertyChanged(self):
        print "StatPropDialog.propertyChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("StatPropDialog",s,c)
