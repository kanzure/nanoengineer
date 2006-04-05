# Copyright (c) 2006 Nanorex, Inc. All rights reserved.
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\NanotubeGeneratorDialog.ui'
#
# Created: Tue Nov 22 17:51:09 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"20 20 3 1",
"# c #1c0a08",
"a c #8d8483",
". c #ffffff",
"....................",
"....................",
"....................",
"....................",
"####################",
".a.a##a.a##a.a##a.a.",
".#a#..#a#..#a#..#a#.",
"#...##...##...##...#",
".#.#..#.#..#.#..#.#.",
"..#....#....#....#..",
"..#....#....#....#..",
".#.#..#.#..#.#..#.#.",
"#...##...##...##...#",
".#a#..#a#..#a#..#a#.",
".a.a##a.a##a.a##a.a.",
"####################",
"....................",
"....................",
"....................",
"...................."
]

class NanotubeGeneratorDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("NanotubeGeneratorDialog")

        self.setIcon(self.image0)

        NanotubeGeneratorDialogLayout = QGridLayout(self,1,1,11,6,"NanotubeGeneratorDialogLayout")

        layout30 = QHBoxLayout(None,0,6,"layout30")
        spacer1 = QSpacerItem(92,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30.addItem(spacer1)

        self.ok_btn = QPushButton(self,"ok_btn")
        self.ok_btn.setMinimumSize(QSize(0,30))
        self.ok_btn.setDefault(1)
        layout30.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0,30))
        layout30.addWidget(self.cancel_btn)

        NanotubeGeneratorDialogLayout.addLayout(layout30,2,0)
        spacer5 = QSpacerItem(101,20,QSizePolicy.Minimum,QSizePolicy.MinimumExpanding)
        NanotubeGeneratorDialogLayout.addItem(spacer5,1,0)

        layout30_2 = QHBoxLayout(None,0,6,"layout30_2")

        layout29 = QHBoxLayout(None,0,6,"layout29")

        layout14 = QVBoxLayout(None,0,6,"layout14")

        self.textLabel2 = QLabel(self,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout14.addWidget(self.textLabel2)

        self.textLabel4 = QLabel(self,"textLabel4")
        self.textLabel4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout14.addWidget(self.textLabel4)
        layout29.addLayout(layout14)

        layout28 = QVBoxLayout(None,0,6,"layout28")

        layout15 = QHBoxLayout(None,0,6,"layout15")

        self.n_spinbox = QSpinBox(self,"n_spinbox")
        self.n_spinbox.setMinValue(1)
        self.n_spinbox.setValue(5)
        layout15.addWidget(self.n_spinbox)

        self.m_spinbox = QSpinBox(self,"m_spinbox")
        self.m_spinbox.setValue(5)
        layout15.addWidget(self.m_spinbox)
        layout28.addLayout(layout15)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        self.length_linedit = QLineEdit(self,"length_linedit")
        self.length_linedit.setMaxLength(8)
        layout27.addWidget(self.length_linedit)

        self.textLabel1 = QLabel(self,"textLabel1")
        layout27.addWidget(self.textLabel1)
        layout28.addLayout(layout27)
        layout29.addLayout(layout28)
        layout30_2.addLayout(layout29)
        spacer26 = QSpacerItem(16,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout30_2.addItem(spacer26)

        NanotubeGeneratorDialogLayout.addLayout(layout30_2,0,0)

        self.languageChange()

        self.resize(QSize(286,144).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.n_spinbox,SIGNAL("valueChanged(int)"),self.setN)
        self.connect(self.m_spinbox,SIGNAL("valueChanged(int)"),self.setM)
        self.connect(self.ok_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.length_linedit,SIGNAL("textChanged(const QString&)"),self.length_fixup)

        self.setTabOrder(self.n_spinbox,self.m_spinbox)
        self.setTabOrder(self.m_spinbox,self.length_linedit)
        self.setTabOrder(self.length_linedit,self.ok_btn)
        self.setTabOrder(self.ok_btn,self.cancel_btn)


    def languageChange(self):
        self.setCaption(self.__tr("Nanotube Generator"))
        self.ok_btn.setText(self.__tr("&OK"))
        self.ok_btn.setAccel(self.__tr("Alt+O"))
        self.cancel_btn.setText(self.__tr("&Cancel"))
        self.cancel_btn.setAccel(self.__tr("Alt+C"))
        self.textLabel2.setText(self.__tr("Chirality (N, M) :"))
        self.textLabel4.setText(self.__tr("Length :"))
        self.textLabel1.setText(self.__tr("Angstroms"))


    def setN(self):
        print "NanotubeGeneratorDialog.setN(): Not implemented yet"

    def setM(self):
        print "NanotubeGeneratorDialog.setM(): Not implemented yet"

    def length_fixup(self):
        print "NanotubeGeneratorDialog.length_fixup(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("NanotubeGeneratorDialog",s,c)
