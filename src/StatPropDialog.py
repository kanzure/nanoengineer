# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'StatPropDialog.ui'
#
# Created: Tue Sep 13 16:00:28 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
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

        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setIcon(self.image0)
        self.setSizeGripEnabled(1)

        StatPropDialogLayout = QVBoxLayout(self,11,6,"StatPropDialogLayout")

        layout74 = QHBoxLayout(None,0,6,"layout74")

        layout80 = QVBoxLayout(None,0,6,"layout80")

        self.nameTextLabel = QLabel(self,"nameTextLabel")
        self.nameTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.nameTextLabel.sizePolicy().hasHeightForWidth()))
        self.nameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout80.addWidget(self.nameTextLabel)

        self.nameTextLabel_2 = QLabel(self,"nameTextLabel_2")
        self.nameTextLabel_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout80.addWidget(self.nameTextLabel_2)

        self.molnameTextLabel = QLabel(self,"molnameTextLabel")
        self.molnameTextLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.molnameTextLabel.sizePolicy().hasHeightForWidth()))
        self.molnameTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout80.addWidget(self.molnameTextLabel)

        self.colorTextLabel = QLabel(self,"colorTextLabel")
        self.colorTextLabel.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout80.addWidget(self.colorTextLabel)
        layout74.addLayout(layout80)

        layout73 = QVBoxLayout(None,0,6,"layout73")

        self.nameLineEdit = QLineEdit(self,"nameLineEdit")
        self.nameLineEdit.setEnabled(1)
        self.nameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.nameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.nameLineEdit.setAlignment(QLineEdit.AlignLeft)
        layout73.addWidget(self.nameLineEdit)

        layout101 = QHBoxLayout(None,0,6,"layout101")

        layout100 = QHBoxLayout(None,0,6,"layout100")

        self.tempSpinBox = QSpinBox(self,"tempSpinBox")
        self.tempSpinBox.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,1,0,self.tempSpinBox.sizePolicy().hasHeightForWidth()))
        self.tempSpinBox.setMaxValue(9999)
        self.tempSpinBox.setValue(300)
        layout100.addWidget(self.tempSpinBox)

        self.textLabel1 = QLabel(self,"textLabel1")
        self.textLabel1.setAlignment(QLabel.AlignVCenter | QLabel.AlignLeft)
        layout100.addWidget(self.textLabel1)
        layout101.addLayout(layout100)
        spacer16 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout101.addItem(spacer16)
        layout73.addLayout(layout101)

        self.molnameLineEdit = QLineEdit(self,"molnameLineEdit")
        self.molnameLineEdit.setEnabled(1)
        self.molnameLineEdit.setFrameShape(QLineEdit.LineEditPanel)
        self.molnameLineEdit.setFrameShadow(QLineEdit.Sunken)
        self.molnameLineEdit.setAlignment(QLineEdit.AlignLeft)
        self.molnameLineEdit.setReadOnly(1)
        layout73.addWidget(self.molnameLineEdit)

        layout72 = QHBoxLayout(None,0,6,"layout72")

        layout71 = QHBoxLayout(None,0,6,"layout71")

        self.colorPixmapLabel = QLabel(self,"colorPixmapLabel")
        self.colorPixmapLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,1,0,self.colorPixmapLabel.sizePolicy().hasHeightForWidth()))
        self.colorPixmapLabel.setMinimumSize(QSize(40,0))
        self.colorPixmapLabel.setPaletteBackgroundColor(QColor(0,0,0))
        self.colorPixmapLabel.setScaledContents(1)
        layout71.addWidget(self.colorPixmapLabel)

        self.choose_color_btn = QPushButton(self,"choose_color_btn")
        self.choose_color_btn.setEnabled(1)
        self.choose_color_btn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.choose_color_btn.sizePolicy().hasHeightForWidth()))
        layout71.addWidget(self.choose_color_btn)
        layout72.addLayout(layout71)
        spacer13 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout72.addItem(spacer13)
        layout73.addLayout(layout72)
        layout74.addLayout(layout73)
        StatPropDialogLayout.addLayout(layout74)
        spacer16_2 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        StatPropDialogLayout.addItem(spacer16_2)

        layout59 = QHBoxLayout(None,0,6,"layout59")
        spacer14 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(spacer14)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,0))
        self.ok_btn.setAutoDefault(1)
        self.ok_btn.setDefault(1)
        layout59.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,0))
        self.cancel_btn.setAutoDefault(1)
        self.cancel_btn.setDefault(0)
        layout59.addWidget(self.cancel_btn)
        StatPropDialogLayout.addLayout(layout59)

        self.languageChange()

        self.resize(QSize(299,202).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.choose_color_btn,SIGNAL("clicked()"),self.choose_color)

        self.setTabOrder(self.nameLineEdit,self.tempSpinBox)
        self.setTabOrder(self.tempSpinBox,self.molnameLineEdit)
        self.setTabOrder(self.molnameLineEdit,self.choose_color_btn)
        self.setTabOrder(self.choose_color_btn,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Stat Properties"))
        self.nameTextLabel.setText(self.__tr("Name :"))
        self.nameTextLabel_2.setText(self.__tr("Temperature :"))
        self.molnameTextLabel.setText(self.__tr("Attached to :"))
        self.colorTextLabel.setText(self.__tr("Color :"))
        self.nameLineEdit.setText(QString.null)
        self.textLabel1.setText(self.__tr("Kelvin"))
        self.molnameLineEdit.setText(QString.null)
        self.choose_color_btn.setText(self.__tr("Choose..."))
        QToolTip.add(self.choose_color_btn,self.__tr("Change color"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))


    def choose_color(self):
        print "StatPropDialog.choose_color(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("StatPropDialog",s,c)
