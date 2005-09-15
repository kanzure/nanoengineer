# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ThermoPropDialog.ui'
#
# Created: Tue Sep 13 16:00:28 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
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

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        ThermoPropDialogLayout = QVBoxLayout(self,11,6,"ThermoPropDialogLayout")

        layout89 = QHBoxLayout(None,0,6,"layout89")

        layout91 = QVBoxLayout(None,0,6,"layout91")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.nameTextLabel.sizePolicy().hasHeightForWidth()))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout91.addWidget(self.nameTextLabel)

        self.molnameTextLabel = QLabel(self,"molnameTextLabel")
        self.molnameTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.molnameTextLabel.sizePolicy().hasHeightForWidth()))
        self.molnameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout91.addWidget(self.molnameTextLabel)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout91.addWidget(self.colorTextLabel)
        layout89.addLayout(layout91)

        layout88 = QVBoxLayout(None,0,6,"layout88")

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout88.addWidget(self.nameLineEdit)

        self.molnameLineEdit = QLineEdit(self,"molnameLineEdit")
        self.molnameLineEdit.setEnabled(1)
        self.molnameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.molnameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.molnameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.molnameLineEdit.setReadOnly(1)
        layout88.addWidget(self.molnameLineEdit)

        layout87 = QHBoxLayout(None,0,6,"layout87")

        layout86 = QHBoxLayout(None,0,6,"layout86")

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout86.addWidget(self.colorPixmapLabel)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.choose_color_btn.sizePolicy().hasHeightForWidth()))
        layout86.addWidget(self.choose_color_btn)
        layout87.addLayout(layout86)
        spacer19 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout87.addItem(spacer19)
        layout88.addLayout(layout87)
        layout89.addLayout(layout88)
        ThermoPropDialogLayout.addLayout(layout89)
        spacer6 = QSpacerItem(20,25,QSizePolicy.Minimum,QSizePolicy.Expanding)
        ThermoPropDialogLayout.addItem(spacer6)

        layout67 = QHBoxLayout(None,0,6,"layout67")
        spacer17 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout67.addItem(spacer17)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,0))
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout67.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,0))
        self.cancel_btn.setAutoDefault(1)
        self.cancel_btn.setDefault(0)
        layout67.addWidget(self.cancel_btn)
        ThermoPropDialogLayout.addLayout(layout67)

        self.languageChange()

        self.resize(QSize(307,170).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.choose_color)

        self.setTabOrder(self.nameLineEdit,self.molnameLineEdit)
        self.setTabOrder(self.molnameLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Thermometer Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.molnameTextLabel.setText(self.__tr("Attached to:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameLineEdit.setText(QString.null)
        self.molnameLineEdit.setText(QString.null)
        self.choose_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_color_btn,self.__tr("Change color"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def choose_color(self):
        print "ThermoPropDialog.choose_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ThermoPropDialog",s,c)
