# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\StatPropDialog.ui'
#
# Created: Thu Dec 30 11:29:54 2004
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

class StatPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("StatPropDialog")

        self.setSizePolicy(QSizePolicy(7,7,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)


        LayoutWidget = QWidget(self,"layout14")
        LayoutWidget.setGeometry(QRect(6,16,260,95))
        layout14 = QGridLayout(LayoutWidget,1,1,11,6,"layout14")

        layout11 = QHBoxLayout(None,0,6,"layout11")

        layout121 = QHBoxLayout(None,0,6,"layout121")

        self.colorTextLabel = QLabel(LayoutWidget,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout121.addWidget(self.colorTextLabel)

        self.colorPixmapLabel = QLabel(LayoutWidget,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(5,5,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout121.addWidget(self.colorPixmapLabel)
        layout11.addLayout(layout121)

        self.colorSelectorPushButton = QPushButton(LayoutWidget,"colorSelectorPushButton")
        self.colorSelectorPushButton.setEnabled(1)
        self.colorSelectorPushButton.setSizePolicy(QSizePolicy(1,0,0,0,self.colorSelectorPushButton.sizePolicy().hasHeightForWidth()))
        layout11.addWidget(self.colorSelectorPushButton)

        layout14.addLayout(layout11,2,0)

        layout10 = QHBoxLayout(None,0,6,"layout10")

        self.nameTextLabel_2 = QLabel(LayoutWidget,"nameTextLabel_2")
        self.nameTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout10.addWidget(self.nameTextLabel_2)

        self.tempSpinBox = QSpinBox(LayoutWidget,"tempSpinBox")
        self.tempSpinBox.setSizePolicy(QSizePolicy(1,0,1,0,self.tempSpinBox.sizePolicy().hasHeightForWidth()))
        self.tempSpinBox.setMaxValue(1000)
        self.tempSpinBox.setValue(300)
        layout10.addWidget(self.tempSpinBox)

        layout14.addLayout(layout10,1,0)

        layout9 = QHBoxLayout(None,0,6,"layout9")

        self.nameTextLabel = QLabel(LayoutWidget,"nameTextLabel")
        self.nameTextLabel.setSizePolicy(QSizePolicy(5,5,0,0,self.nameTextLabel.sizePolicy().hasHeightForWidth()))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout9.addWidget(self.nameTextLabel)

        self.nameLineEdit = QLineEdit(LayoutWidget,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout9.addWidget(self.nameLineEdit)

        layout14.addLayout(layout9,0,0)

        self.cancelPushButton = QPushButton(self,"cancelPushButton")
        self.cancelPushButton.setGeometry(QRect(100,152,82,29))
        self.cancelPushButton.setMinimumSize(QSize(0,0))
        self.cancelPushButton.setAutoDefault(1)
        self.cancelPushButton.setDefault(0)

        self.okPushButton = QPushButton(self,"okPushButton")
        self.okPushButton.setGeometry(QRect(12,152,82,29))
        self.okPushButton.setMinimumSize(QSize(0,0))
        self.okPushButton.setAutoDefault(1)
        self.okPushButton.setDefault(1)

        self.applyPushButton = QPushButton(self,"applyPushButton")
        self.applyPushButton.setEnabled(0)
        self.applyPushButton.setGeometry(QRect(188,152,82,29))
        self.applyPushButton.setMinimumSize(QSize(0,0))

        self.languageChange()

        self.resize(QSize(289,194).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancelPushButton,SIGNAL("clicked()"),self,SLOT("reject()"))
        self.connect(self.okPushButton,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.nameLineEdit,SIGNAL("textChanged(const QString&)"),self.propertyChanged)
        self.connect(self.applyPushButton,SIGNAL("clicked()"),self.applyButtonPressed)
        self.connect(self.colorSelectorPushButton,SIGNAL("clicked()"),self.changeStatColor)



    def languageChange(self):
        self.setCaption(self.__tr("Stat Properties"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.nameTextLabel_2.setText(self.__tr("Temp (K):"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.nameLineEdit.setText(QString.null)
        self.cancelPushButton.setText(self.__tr("&Cancel"))
        self.cancelPushButton.setAccel(self.__tr("Alt+C"))
        self.okPushButton.setText(self.__tr("&OK"))
        self.okPushButton.setAccel(self.__tr("Alt+O"))
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
