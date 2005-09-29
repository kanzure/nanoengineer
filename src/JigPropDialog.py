# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\JigPropDialog.ui'
#
# Created: Wed Sep 28 17:24:20 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class JigPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("JigPropDialog")

        self.setSizeGripEnabled(1)

        JigPropDialogLayout = QVBoxLayout(self,11,6,"JigPropDialogLayout")

        layout92 = QHBoxLayout(None,0,6,"layout92")

        layout90 = QVBoxLayout(None,0,6,"layout90")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout90.addWidget(self.nameTextLabel)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout90.addWidget(self.colorTextLabel)
        layout92.addLayout(layout90)

        layout91 = QVBoxLayout(None,0,6,"layout91")

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout91.addWidget(self.nameLineEdit)

        layout84 = QHBoxLayout(None,0,6,"layout84")

        layout83 = QHBoxLayout(None,0,6,"layout83")

        self.jig_color_pixmap = QLabel(self,"jig_color_pixmap")
        self.jig_color_pixmap.setMinimumSize(QSize(40,0))
        self.jig_color_pixmap.setPaletteBackgroundColor(QColor(0,0,0))
        self.jig_color_pixmap.setScaledContents(1)
        layout83.addWidget(self.jig_color_pixmap)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Fixed,1,0,self.choose_color_btn.sizePolicy().hasHeightForWidth()))
        layout83.addWidget(self.choose_color_btn)
        layout84.addLayout(layout83)
        spacer8 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout84.addItem(spacer8)
        layout91.addLayout(layout84)
        layout92.addLayout(layout91)
        JigPropDialogLayout.addLayout(layout92)
        spacer11 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        JigPropDialogLayout.addItem(spacer11)

        layout50 = QHBoxLayout(None,0,6,"layout50")
        spacer9 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout50.addItem(spacer9)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout50.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setAutoDefault(1)
        self.cancel_btn.setDefault(0)
        layout50.addWidget(self.cancel_btn)
        JigPropDialogLayout.addLayout(layout50)

        self.languageChange()

        self.resize(QSize(245,145).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.change_jig_color)

        self.setTabOrder(self.nameLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Jig Properties"))
        self.nameTextLabel.setText(self.__tr("Name:"))
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.nameLineEdit.setText(QString.null)
        self.choose_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_color_btn,self.__tr("Change Color"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def change_jig_color(self):
        print "JigPropDialog.change_jig_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("JigPropDialog",s,c)
