# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\StatPropDialog.ui'
#
# Created: Sat Jan 29 11:04:13 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.12
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"22 22 75 2",
".# c #0111e5",
".y c #0312db",
"#i c #0715c4",
".7 c #263138",
".I c #293232",
".9 c #293875",
".3 c #294545",
".A c #2a5459",
".q c #2b3f3f",
"## c #2c3837",
".w c #2c3a3a",
"#d c #2c5757",
".N c #2c5857",
".Y c #2d3939",
"#. c #2d4141",
".Q c #2f3c3c",
".r c #308282",
".p c #313e58",
".v c #318281",
".k c #334242",
".6 c #339494",
".0 c #339695",
"#b c #3441ea",
".L c #349c9b",
"#c c #35a3a2",
".i c #364747",
".U c #364d4d",
".R c #36a9a8",
".H c #37b0af",
".j c #395353",
".h c #3a4646",
".S c #3a4949",
".X c #3a5353",
".E c #3ac3c2",
".K c #3b4848",
".1 c #3c4b4b",
".W c #3ccbca",
".Z c #3ccfce",
".u c #3ed9d8",
".B c #3edcdb",
".s c #3fe0df",
".2 c #40e6e6",
".V c #41edec",
".M c #42f2f1",
".t c #42f3f2",
".C c #44fdfc",
".D c #44fefd",
".l c #495858",
".z c #4f5b5b",
".8 c #5b64cc",
"#f c #5b7575",
".O c #5e6e6e",
".f c #6068dc",
"#g c #617f7f",
".a c #6770ef",
"#e c #6b7e7e",
".x c #727d7d",
".4 c #738383",
".F c #778080",
"#h c #7a8b8b",
".g c #909c9c",
"#a c #9ea4a4",
".m c #acb3b3",
".J c #c2c8c8",
".c c #d7d7d7",
".d c #d9d9d9",
".o c #e1e1e1",
".b c #eaeaea",
".e c #f3f3f3",
".T c #f4f4f4",
".n c #f6f6f6",
".G c #fafafa",
".P c #fcfcfc",
".5 c #fefefe",
"Qt c #ffffff",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQt.#.#.#.#.#.#.#.#.#.#.#.#.#QtQt",
"QtQtQtQtQtQt.#.aQt.b.c.c.d.eQtQtQtQt.#.#QtQt",
"QtQtQtQtQt.#Qt.f.g.h.i.j.k.l.m.nQt.#Qt.#QtQt",
"QtQtQtQt.#Qt.o.p.q.r.s.t.u.v.w.x.yQtQt.#QtQt",
"QtQtQt.#Qt.b.z.A.B.C.D.D.D.C.E.#.F.GQt.#QtQt",
"QtQt.#.#.#.#.#.#.#.#.#.#.#.#.#.H.I.JQt.#QtQt",
"QtQt.#Qt.b.K.L.D.D.D.D.D.D.D.#.M.N.O.P.#QtQt",
"QtQt.#Qt.c.Q.u.D.D.D.D.D.D.D.#.D.R.S.T.#QtQt",
"QtQt.#Qt.c.U.V.D.D.D.D.D.D.D.#.D.W.X.T.#QtQt",
"QtQt.#Qt.d.Y.Z.D.D.D.D.D.D.D.#.D.0.1.T.#QtQt",
"QtQt.#Qt.e.l.v.C.D.D.D.D.D.D.#.2.3.4.5.#QtQt",
"QtQt.#QtQt.m.w.E.D.D.D.D.D.D.#.6.7.8.a.#QtQt",
"QtQt.#QtQt.n.9#..H.M.D.D.D.M.####a.5.#QtQtQt",
"QtQt.#QtQt#b.T.F.I.N.R.W#c#d.##a.P.#QtQtQtQt",
"QtQt.#Qt#bQtQt.G.J#e#f#g#f#h#i.5.#QtQtQtQtQt",
"QtQt.##bQtQtQtQtQtQtQtQtQtQt.#.#QtQtQtQtQtQt",
"QtQt.#.#.#.#.#.#.#.#.#.#.#.#.#QtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt",
"QtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQtQt"
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

        StatPropDialogLayout = QGridLayout(self,1,1,11,6,"StatPropDialogLayout")

        layout10 = QGridLayout(None,1,1,0,6,"layout10")

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

        layout10.addLayout(layout9,0,0)

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

        layout10.addLayout(layout11,3,0)

        layout7 = QHBoxLayout(None,0,6,"layout7")

        self.molnameTextLabel = QLabel(self,"molnameTextLabel")
        self.molnameTextLabel.setSizePolicy(QSizePolicy(5,5,0,0,self.molnameTextLabel.sizePolicy().hasHeightForWidth()))
        molnameTextLabel_font = QFont(self.molnameTextLabel.font())
        molnameTextLabel_font.setPointSize(9)
        molnameTextLabel_font.setBold(1)
        self.molnameTextLabel.setFont(molnameTextLabel_font)
        self.molnameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout7.addWidget(self.molnameTextLabel)

        self.molnameLineEdit = QLineEdit(self,"molnameLineEdit")
        self.molnameLineEdit.setEnabled(1)
        self.molnameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.molnameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.molnameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.molnameLineEdit.setReadOnly(1)
        layout7.addWidget(self.molnameLineEdit)

        layout10.addLayout(layout7,2,0)

        layout10_2 = QHBoxLayout(None,0,6,"layout10_2")

        self.nameTextLabel_2 = QLabel(self,"nameTextLabel_2")
        nameTextLabel_2_font = QFont(self.nameTextLabel_2.font())
        nameTextLabel_2_font.setPointSize(9)
        nameTextLabel_2_font.setBold(1)
        self.nameTextLabel_2.setFont(nameTextLabel_2_font)
        self.nameTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout10_2.addWidget(self.nameTextLabel_2)

        self.tempSpinBox = QSpinBox(self,"tempSpinBox")
        self.tempSpinBox.setSizePolicy(QSizePolicy(1,0,1,0,self.tempSpinBox.sizePolicy().hasHeightForWidth()))
        self.tempSpinBox.setMaxValue(1000)
        self.tempSpinBox.setValue(300)
        layout10_2.addWidget(self.tempSpinBox)

        layout10.addLayout(layout10_2,1,0)

        StatPropDialogLayout.addLayout(layout10,0,0)

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

        StatPropDialogLayout.addLayout(layout34,1,0)

        self.languageChange()

        self.resize(QSize(299,259).expandedTo(self.minimumSizeHint()))
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
        self.colorTextLabel.setText(self.__tr("Color:"))
        self.colorSelectorPushButton.setText(self.__tr("..."))
        QToolTip.add(self.colorSelectorPushButton,self.__tr("Change color"))
        self.molnameTextLabel.setText(self.__tr("Attached to:"))
        self.molnameLineEdit.setText(QString.null)
        self.nameTextLabel_2.setText(self.__tr("Temperature (K):"))
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
