# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Huaicai\Main\cad\src\StatPropDialog.ui'
#
# Created: Thu Dec 9 13:20:06 2004
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

        StatPropDialogLayout = QVBoxLayout(self,11,17,"StatPropDialogLayout")

        layout110 = QHBoxLayout(None,0,6,"layout110")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout110.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout110.addWidget(self.nameLineEdit)
        StatPropDialogLayout.addLayout(layout110)

        layout120 = QHBoxLayout(None,0,22,"layout120")

        layout118 = QHBoxLayout(None,0,6,"layout118")

        self.nameTextLabel_2 = QLabel(self,"nameTextLabel_2")
        self.nameTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout118.addWidget(self.nameTextLabel_2)

        self.tempSpinBox = QSpinBox(self,"tempSpinBox")
        self.tempSpinBox.setSizePolicy(QSizePolicy(1,0,1,0,self.tempSpinBox.sizePolicy().hasHeightForWidth()))
        self.tempSpinBox.setMaxValue(1000)
        self.tempSpinBox.setValue(300)
        layout118.addWidget(self.tempSpinBox)
        layout120.addLayout(layout118)

        layout119 = QHBoxLayout(None,0,6,"layout119")

        self.atomsTextLabel = QLabel(self,"atomsTextLabel")
        self.atomsTextLabel.setMouseTracking(0)
        self.atomsTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout119.addWidget(self.atomsTextLabel)

        self.atomsComboBox = QComboBox(0,self,"atomsComboBox")
        layout119.addWidget(self.atomsComboBox)
        layout120.addLayout(layout119)
        StatPropDialogLayout.addLayout(layout120)

        layout122 = QHBoxLayout(None,0,46,"layout122")

        layout121 = QHBoxLayout(None,0,6,"layout121")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout121.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout121.addWidget(self.colorPixmapLabel)
        layout122.addLayout(layout121)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setSizePolicy(QSizePolicy(1,0,0,0,self.colorSelectorPushButton.sizePolicy().hasHeightForWidth()))
        layout122.addWidget(self.colorSelectorPushButton)
        StatPropDialogLayout.addLayout(layout122)
        spacer15 = QSpacerItem(20,110,QSizePolicy.Minimum,QSizePolicy.Expanding)
        StatPropDialogLayout.addItem(spacer15)

        layout116 = QHBoxLayout(None,10,6,"layout116")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,30))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout116.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,30))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout116.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setMinimumSize(QSize(0,30))
        layout116.addWidget(self.applyPushButton)
        StatPropDialogLayout.addLayout(layout116)

        self.languageChange()

        self.resize(QSize(385,241).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeStatColor)



    def languageChange(self):
        self.setCaption(self.__tr("Stat Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.nameTextLabel_2.setText(self.__tr("Temp (K):"))
        self.atomsTextLabel.setText(self.__tr("Atoms:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.applyPushButton.setAccel(QString.null)


    def applyButtonPressed(self):
        print "StatPropDialog.applyButtonPressed(): Not implemented yet"

    def changeStatColor(self):
        print "StatPropDialog.changeStatColor(): Not implemented yet"

    def propertyChanged(self):
        print "StatPropDialog.propertyChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("StatPropDialog",s,c)
