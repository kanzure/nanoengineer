# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\ThermoPropDialog.ui'
#
# Created: Mon Jan 24 17:12:16 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 8 1",
"b c #170f07",
"a c #4e4942",
"d c #afadab",
"# c #bebcbb",
"e c #f19977",
"f c #f5b49b",
"c c #ff0000",
". c #ffffff",
"......................",
".........#aa#.........",
".........a..a.........",
".........b..b.........",
".........b.bb.........",
".........b..b.........",
".........b..b.........",
".........b.bb.........",
".........b..b.........",
".........bccb.........",
".........bcbb.........",
".........bccb.........",
".........bccb.........",
".........bcbb.........",
"........daccad........",
".......daccccad.......",
".......acceccca.......",
".......bceccccb.......",
".......bcfccccb.......",
".......accfccca.......",
".......daccccad.......",
"........dabbad........"
]

class ThermoPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("ThermoPropDialog")

        self.setSizePolicy(QSizePolicy(7,7,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        ThermoPropDialogLayout = QVBoxLayout(self,11,6,"ThermoPropDialogLayout")

        layout7 = QGridLayout(None,1,1,0,6,"layout7")

        layout11 = QHBoxLayout(None,0,6,"layout11")

        layout121 = QHBoxLayout(None,0,6,"layout121")

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        colorTextLabel_font = QFont(self.colorTextLabel.font())
        colorTextLabel_font.setPointSize(9)
        colorTextLabel_font.setBold(1)
        self.colorTextLabel.setFont(colorTextLabel_font)
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout121.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout121.addWidget(self.colorPixmapLabel)
        layout11.addLayout(layout121)

        self.colorSelectorPushButton = QPushButton(self,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setSizePolicy(QSizePolicy(1,0,0,0,self.colorSelectorPushButton.sizePolicy().hasHeightForWidth()))
        layout11.addWidget(self.colorSelectorPushButton)

        layout7.addLayout(layout11,1,0)

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setSizePolicy(QSizePolicy(5,5,0,0,self.nameTextLabel.sizePolicy().hasHeightForWidth()))
        nameTextLabel_font = QFont(self.nameTextLabel.font())
        nameTextLabel_font.setPointSize(9)
        nameTextLabel_font.setBold(1)
        self.nameTextLabel.setFont(nameTextLabel_font)
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout9.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout9.addWidget(self.nameLineEdit)

        layout7.addLayout(layout9,0,0)
        ThermoPropDialogLayout.addLayout(layout7)

        layout34 = QHBoxLayout(None,0,6,"layout34")

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setMinimumSize(QSize(0,0))
        okPushButton_font = QFont(self.okPushButton.font())
        okPushButton_font.setPointSize(9)
        okPushButton_font.setBold(1)
        self.okPushButton.setFont(okPushButton_font)
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)
        layout34.addWidget(self.okPushButton)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setMinimumSize(QSize(0,0))
        cancelPushButton_font = QFont(self.cancelPushButton.font())
        cancelPushButton_font.setPointSize(9)
        cancelPushButton_font.setBold(1)
        self.cancelPushButton.setFont(cancelPushButton_font)
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)
        layout34.addWidget(self.cancelPushButton)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setMinimumSize(QSize(0,0))
        applyPushButton_font = QFont(self.applyPushButton.font())
        applyPushButton_font.setPointSize(9)
        applyPushButton_font.setBold(1)
        self.applyPushButton.setFont(applyPushButton_font)
        layout34.addWidget(self.applyPushButton)
        ThermoPropDialogLayout.addLayout(layout34)

        self.languageChange()

        self.resize(QSize(299,213).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeThermoColor)



    def languageChange(self):
        self.setCaption(self.__tr("Thermometer Properties"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.applyPushButton.setText(self.__tr("Apply"))
        self.applyPushButton.setAccel(QString.null)


    def applyButtonPressed(self):
        print "ThermoPropDialog.applyButtonPressed(): Not implemented yet"

    def changeThermoColor(self):
        print "ThermoPropDialog.changeThermoColor(): Not implemented yet"

    def propertyChanged(self):
        print "ThermoPropDialog.propertyChanged(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ThermoPropDialog",s,c)
