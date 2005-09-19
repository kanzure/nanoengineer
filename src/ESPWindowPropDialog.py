# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ESPWindowPropDialog.ui'
#
# Created: Mon Sep 19 18:05:06 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *


class ESPWindowPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("ESPWindowPropDialog")


        ESPWindowPropDialogLayout = QVBoxLayout(self,11,6,"ESPWindowPropDialogLayout")

        layout19 = QHBoxLayout(None,0,16,"layout19")

        layout15 = QHBoxLayout(None,0,1,"layout15")

        layout14 = QVBoxLayout(None,0,6,"layout14")

        self.textLabel1 = QLabel(self,"textLabel1")
        layout14.addWidget(self.textLabel1)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter)
        layout14.addWidget(self.colorTextLabel)
        layout15.addLayout(layout14)

        layout13 = QVBoxLayout(None,0,6,"layout13")

        self.wdLineEdit = QLineEdit(self,"wdLineEdit")
        self.wdLineEdit.setMinimumSize(QSize(0,30))
        self.wdLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.wdLineEdit.setFrameShadow(QLineEdit.Sunken)
        layout13.addWidget(self.wdLineEdit)

        self.planeColorButton = QPushButton(self,"planeColorButton")
        self.planeColorButton.setMinimumSize(QSize(0,30))
        self.planeColorButton.setPaletteForegroundColor(QColor(0,0,0))
        self.planeColorButton.setPaletteBackgroundColor(QColor(85,170,127))
        pal = QPalette()
        cg = QColorGroup()
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(106,212,159))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,Qt.black)
        cg.setColor(QColorGroup.LinkVisited,Qt.black)
        pal.setActive(cg)
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(97,195,146))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setInactive(cg)
        cg.setColor(QColorGroup.Foreground,QColor(128,128,128))
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(97,195,146))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,QColor(128,128,128))
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,QColor(128,128,128))
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setDisabled(cg)
        self.planeColorButton.setPalette(pal)
        self.planeColorButton.setFocusPolicy(QPushButton.NoFocus)
        self.planeColorButton.setFlat(1)
        layout13.addWidget(self.planeColorButton)
        layout15.addLayout(layout13)
        layout19.addLayout(layout15)

        layout18 = QHBoxLayout(None,0,1,"layout18")

        layout17 = QVBoxLayout(None,0,6,"layout17")

        self.textLabel1_2 = QLabel(self,"textLabel1_2")
        layout17.addWidget(self.textLabel1_2)

        self.colorTextLabel_2 = QLabel(self,"colorTextLabel_2")
        self.colorTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout17.addWidget(self.colorTextLabel_2)
        layout18.addLayout(layout17)

        layout16 = QVBoxLayout(None,0,6,"layout16")

        self.resolutionLineEdit = QLineEdit(self,"resolutionLineEdit")
        self.resolutionLineEdit.setMinimumSize(QSize(0,30))
        layout16.addWidget(self.resolutionLineEdit)

        self.gridColorButton = QPushButton(self,"gridColorButton")
        self.gridColorButton.setMinimumSize(QSize(0,30))
        self.gridColorButton.setPaletteForegroundColor(QColor(0,0,0))
        self.gridColorButton.setPaletteBackgroundColor(QColor(85,170,127))
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(106,212,159))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,Qt.black)
        cg.setColor(QColorGroup.LinkVisited,Qt.black)
        pal.setActive(cg)
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(97,195,146))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setInactive(cg)
        cg.setColor(QColorGroup.Foreground,QColor(128,128,128))
        cg.setColor(QColorGroup.Button,QColor(85,170,127))
        cg.setColor(QColorGroup.Light,QColor(127,255,191))
        cg.setColor(QColorGroup.Midlight,QColor(97,195,146))
        cg.setColor(QColorGroup.Dark,QColor(42,85,64))
        cg.setColor(QColorGroup.Mid,QColor(56,113,85))
        cg.setColor(QColorGroup.Text,QColor(128,128,128))
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,QColor(128,128,128))
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(85,170,127))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,255))
        cg.setColor(QColorGroup.LinkVisited,QColor(255,0,255))
        pal.setDisabled(cg)
        self.gridColorButton.setPalette(pal)
        self.gridColorButton.setFlat(1)
        layout16.addWidget(self.gridColorButton)
        layout18.addLayout(layout16)
        layout19.addLayout(layout18)
        ESPWindowPropDialogLayout.addLayout(layout19)
        spacer5 = QSpacerItem(101,150,QSizePolicy.Minimum,QSizePolicy.Expanding)
        ESPWindowPropDialogLayout.addItem(spacer5)

        layout16_2 = QHBoxLayout(None,0,6,"layout16_2")
        spacer1 = QSpacerItem(109,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout16_2.addItem(spacer1)

        self.okButton = QPushButton(self,"okButton")
        self.okButton.setMinimumSize(QSize(0,30))
        self.okButton.setAutoDefault(1)
        self.okButton.setDefault(1)
        layout16_2.addWidget(self.okButton)

        self.cancelButton = QPushButton(self,"cancelButton")
        self.cancelButton.setMinimumSize(QSize(0,30))
        self.cancelButton.setAutoDefault(1)
        layout16_2.addWidget(self.cancelButton)
        ESPWindowPropDialogLayout.addLayout(layout16_2)

        self.languageChange()

        self.resize(QSize(375,198).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.okButton,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancelButton,SIGNAL("clicked()"),self.reject)
        self.connect(self.planeColorButton,SIGNAL("clicked()"),self.changePlaneColor)
        self.connect(self.gridColorButton,SIGNAL("clicked()"),self.changeGridColor)


    def languageChange(self):
        self.setCaption(self.__tr("ESP Plane Properties"))
        self.textLabel1.setText(self.__tr("Plane Width:"))
        self.colorTextLabel.setText(self.__tr("Plane Color:"))
        self.planeColorButton.setText(QString.null)
        self.textLabel1_2.setText(self.__tr("Resolution:"))
        self.colorTextLabel_2.setText(self.__tr("Outline Color:"))
        self.gridColorButton.setText(QString.null)
        self.okButton.setText(self.__tr("&OK"))
        self.okButton.setAccel(self.__tr("Alt+O"))
        self.cancelButton.setText(self.__tr("&Cancel"))
        self.cancelButton.setAccel(self.__tr("Alt+C"))


    def changePlaneColor(self):
        print "ESPWindowPropDialog.changePlaneColor(): Not implemented yet"

    def changeGridColor(self):
        print "ESPWindowPropDialog.changeGridColor(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("ESPWindowPropDialog",s,c)
