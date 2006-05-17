# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DnaGeneratorDialog.ui'
#
# Created: Wed May 17 14:00:30 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x14\x00\x00\x00\x14" \
    "\x08\x06\x00\x00\x00\x8d\x89\x1d\x0d\x00\x00\x00" \
    "\x95\x49\x44\x41\x54\x38\x8d\xed\x94\x3d\x12\x82" \
    "\x30\x10\x85\xbf\x28\x45\x8c\x57\x08\x87\xc4\x52" \
    "\x2c\x74\xb4\xe5\x24\x5c\x80\xa1\xa5\xf1\x3a\xb6" \
    "\x5a\x3c\xab\x30\x68\x47\x58\x0a\x67\x7c\xe5\xb7" \
    "\x99\x97\xbf\xb7\xeb\x24\x61\xa9\x8d\xa9\xdb\x4f" \
    "\x18\xba\x18\xbc\xe9\x23\x6e\x1f\xcf\xd7\x05\x38" \
    "\xb7\x5d\x0f\xc0\x7d\x18\x00\xa8\x8e\x35\x73\x59" \
    "\xdb\xf5\x0e\x49\xc4\xe0\xd5\xdc\xae\x8a\xc1\x2b" \
    "\x29\x93\xc1\xb4\x98\x16\x2c\x61\xe3\x09\x13\x98" \
    "\x16\x33\x18\x48\x9f\xa6\xdf\x3b\xce\x60\x48\xb2" \
    "\x8f\x8d\xfd\x95\x57\xfb\x14\xab\xd8\x14\x29\x9c" \
    "\x87\xfa\x04\x40\xb9\xdf\x91\xcb\x60\x85\xd6\x73" \
    "\xfa\xcf\xc3\xa5\x7a\x03\xaf\xec\xb2\x69\x7f\xf9" \
    "\x68\x24\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42" \
    "\x60\x82"

class DnaGeneratorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap()
        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setName("DnaGeneratorDialog")

        self.setIcon(self.image0)


        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,20,90,30))

        self.lineEdit2 = QLineEdit(self,"lineEdit2")
        self.lineEdit2.setGeometry(QRect(100,20,340,24))

        self.checkBox2 = QCheckBox(self,"checkBox2")
        self.checkBox2.setGeometry(QRect(10,50,80,22))

        self.checkBox5 = QCheckBox(self,"checkBox5")
        self.checkBox5.setGeometry(QRect(360,50,80,22))

        self.checkBox4 = QCheckBox(self,"checkBox4")
        self.checkBox4.setGeometry(QRect(260,50,80,22))

        self.checkBox3 = QCheckBox(self,"checkBox3")
        self.checkBox3.setGeometry(QRect(100,50,80,22))

        LayoutWidget = QWidget(self,"layout30")
        LayoutWidget.setGeometry(QRect(10,100,300,32))
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

        self.languageChange()

        self.resize(QSize(463,145).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)

        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Dna Generator"))
        self.textLabel1.setText(self.__tr("Sequence :"))
        self.checkBox2.setText(self.__tr("Spine A"))
        self.checkBox5.setText(self.__tr("Bases B"))
        self.checkBox4.setText(self.__tr("Spine B"))
        self.checkBox3.setText(self.__tr("Bases A"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def __tr(self,s,c = None):
        return qApp.translate("DnaGeneratorDialog",s,c)
