# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\NanoHiveDialog.ui'
#
# Created: Mon Sep 19 20:18:53 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"20 20 95 2",
".p c #000000",
".O c #199c00",
".K c #1a9c00",
".A c #1a9f00",
".G c #1b9b03",
"#t c #1b9d03",
".Q c #1b9e02",
"#k c #1daf00",
".s c #1daf01",
".q c #1db000",
"#b c #1db200",
".8 c #1eae02",
"#v c #1eaf02",
".U c #1eb102",
".H c #1f9b07",
".Y c #1f9d07",
"#q c #1f9e07",
"#a c #1fbe00",
".Z c #209d09",
".x c #20ae04",
".V c #20be01",
".5 c #20c300",
".4 c #20c400",
"#h c #21ae06",
"#p c #22ae07",
".o c #23d700",
"#u c #24d502",
"#j c #24d601",
".S c #24de00",
".j c #24df00",
"#A c #25dd01",
".3 c #27d605",
".N c #28d508",
"#g c #28d608",
".i c #29de06",
"#o c #2ad509",
".7 c #2afc02",
".6 c #2afd01",
".L c #2afe00",
".e c #2aff00",
"#n c #2bfd02",
"#m c #2bfe01",
".w c #2bfe02",
".2 c #2cfd03",
".I c #2cfd04",
".n c #2cfe03",
".f c #2dfd04",
"#x c #2dfd05",
".b c #2efd06",
".a c #2ffc07",
".M c #2ffc08",
".T c #74d061",
"#c c #74d062",
".R c #76de62",
".B c #76e161",
"#d c #77de63",
"#s c #77e063",
"#r c #81e16e",
"## c #82e16f",
".F c #84e072",
".X c #84e073",
".z c #98f086",
".0 c #99ef89",
"#. c #99f088",
"#e c #9aef8a",
".P c #9bef8b",
".W c #9ef08e",
".k c #a9f59a",
"#l c #adfe9d",
".J c #adff9c",
".C c #aefe9e",
"#i c #aefe9f",
".y c #aeff9f",
".9 c #affe9f",
".1 c #b0fea1",
".E c #b1fda2",
"#f c #b1fea2",
"#w c #b2fea3",
".t c #b2fea4",
".d c #bdffb0",
".c c #befeb2",
"#z c #c6fabc",
".h c #c8f9bf",
".v c #defed8",
".r c #deffd7",
".# c #dffed9",
"#y c #e3ffde",
"#C c #e4fedf",
".l c #e4ffdf",
".g c #e5fee0",
".u c #ebfee7",
".D c #f3fef0",
"#B c #fafefa",
".m c #fafffa",
"Qt c #ffffff",
"QtQtQt.#.a.b.cQtQtQtQtQtQt.d.e.f.#QtQtQt",
"QtQt.g.h.i.j.k.l.mQtQt.m.l.k.j.i.h.lQtQt",
"QtQt.n.o.p.p.q.e.rQtQt.r.e.s.p.p.o.eQtQt",
"QtQt.e.o.p.p.q.e.t.uQt.v.w.x.p.p.o.eQtQt",
"QtQt.y.z.A.A.B.e.n.CQt.D.E.F.A.A.z.yQtQt",
"QtQt.e.o.p.p.G.p.p.H.I.J.e.q.p.p.o.eQtQt",
"QtQt.f.o.p.p.G.p.p.K.L.J.e.q.p.p.o.LQtQt",
"QtQt.M.N.p.p.G.p.p.O.e.J.e.q.p.p.o.bQtQt",
"QtQt.E.P.Q.A.R.S.T.U.V.W.y.X.Y.Z.0.1QtQt",
"QtQt.2.3.p.p.s.e.4.p.p.5.6.s.p.p.o.wQtQt",
"QtQt.e.o.p.p.s.e.4.p.p.5.7.8.p.p.3.nQtQt",
"QtQt.9#..A.A##.y.W#a#b#c.S#d.A.A#e#fQtQt",
"QtQt.w#g.p.p#h.e#i.2.O.p.p.G.p.p.o.bQtQt",
"QtQt.L#j.p.p#k.e#l#m.K.p.p.K.p.p.o.fQtQt",
"QtQt#n#o.p.p#p.e#i.M.H.p.p.O.p.p.o.eQtQt",
"QtQt.y.0#q.A#r.E.DQt.C.2#n#s#t.A.z.yQtQt",
"QtQt.L#u.p.p#v.w.vQt.u#w.e.s.p.p#u.LQtQt",
"QtQt.L#j.p.p.s.e.rQtQt.v#x.s.p.p#j.2QtQt",
"QtQt#y#z#A.S.k#y.mQtQt#B#C.k.S.S#z#CQtQt",
"QtQtQt.v.2.L.dQtQtQtQtQtQt.c.b.2.rQtQtQt"
]

class NanoHiveDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        self.image0 = QPixmap(image0_data)

        if not name:
            self.setName("NanoHiveDialog")

        self.setIcon(self.image0)
        self.setModal(1)

        NanoHiveDialogLayout = QGridLayout(self,1,1,11,21,"NanoHiveDialogLayout")

        layout46 = QHBoxLayout(None,0,6,"layout46")

        layout40 = QVBoxLayout(None,0,6,"layout40")

        self.namelbl = QLabel(self,"namelbl")
        self.namelbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout40.addWidget(self.namelbl)

        layout38 = QVBoxLayout(None,0,6,"layout38")

        self.desclbl = QLabel(self,"desclbl")
        self.desclbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout38.addWidget(self.desclbl)
        spacer31 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout38.addItem(spacer31)
        layout40.addLayout(layout38)
        layout46.addLayout(layout40)

        layout45 = QVBoxLayout(None,0,6,"layout45")

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)
        layout45.addWidget(self.name_linedit)

        self.description_textedit = QTextEdit(self,"description_textedit")
        self.description_textedit.setMinimumSize(QSize(0,0))
        self.description_textedit.setTextFormat(QTextEdit.PlainText)
        layout45.addWidget(self.description_textedit)
        layout46.addLayout(layout45)

        NanoHiveDialogLayout.addLayout(layout46,0,0)

        self.parms_grpbox = QGroupBox(self,"parms_grpbox")
        self.parms_grpbox.setColumnLayout(0,Qt.Vertical)
        self.parms_grpbox.layout().setSpacing(6)
        self.parms_grpbox.layout().setMargin(11)
        parms_grpboxLayout = QGridLayout(self.parms_grpbox.layout())
        parms_grpboxLayout.setAlignment(Qt.AlignTop)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout24 = QVBoxLayout(None,0,6,"layout24")

        self.textLabel5 = QLabel(self.parms_grpbox,"textLabel5")
        self.textLabel5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel5)

        self.textLabel2 = QLabel(self.parms_grpbox,"textLabel2")
        self.textLabel2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel2)

        self.textLabel3 = QLabel(self.parms_grpbox,"textLabel3")
        self.textLabel3.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout24.addWidget(self.textLabel3)
        layout27.addLayout(layout24)

        layout25 = QVBoxLayout(None,0,6,"layout25")

        self.nframes_spinbox = QSpinBox(self.parms_grpbox,"nframes_spinbox")
        self.nframes_spinbox.setMaxValue(90000)
        self.nframes_spinbox.setMinValue(1)
        self.nframes_spinbox.setLineStep(15)
        self.nframes_spinbox.setValue(900)
        layout25.addWidget(self.nframes_spinbox)

        self.stepsper_spinbox = QSpinBox(self.parms_grpbox,"stepsper_spinbox")
        self.stepsper_spinbox.setMaxValue(99999)
        self.stepsper_spinbox.setMinValue(1)
        self.stepsper_spinbox.setValue(10)
        layout25.addWidget(self.stepsper_spinbox)

        self.temp_spinbox = QSpinBox(self.parms_grpbox,"temp_spinbox")
        self.temp_spinbox.setMaxValue(99999)
        self.temp_spinbox.setValue(300)
        layout25.addWidget(self.temp_spinbox)
        layout27.addLayout(layout25)

        layout26 = QVBoxLayout(None,0,6,"layout26")
        spacer4 = QSpacerItem(255,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout26.addItem(spacer4)

        self.textLabel2_2 = QLabel(self.parms_grpbox,"textLabel2_2")
        layout26.addWidget(self.textLabel2_2)

        self.textLabel3_2 = QLabel(self.parms_grpbox,"textLabel3_2")
        layout26.addWidget(self.textLabel3_2)
        layout27.addLayout(layout26)

        parms_grpboxLayout.addLayout(layout27,0,0)

        NanoHiveDialogLayout.addWidget(self.parms_grpbox,1,0)

        self.buttonGroup1 = QButtonGroup(self,"buttonGroup1")
        self.buttonGroup1.setColumnLayout(0,Qt.Vertical)
        self.buttonGroup1.layout().setSpacing(6)
        self.buttonGroup1.layout().setMargin(11)
        buttonGroup1Layout = QGridLayout(self.buttonGroup1.layout())
        buttonGroup1Layout.setAlignment(Qt.AlignTop)

        layout43 = QHBoxLayout(None,0,6,"layout43")

        self.MPQC_GD_checkbox = QCheckBox(self.buttonGroup1,"MPQC_GD_checkbox")
        layout43.addWidget(self.MPQC_GD_checkbox)

        self.MPQC_GD_options_btn = QPushButton(self.buttonGroup1,"MPQC_GD_options_btn")
        self.MPQC_GD_options_btn.setEnabled(0)
        layout43.addWidget(self.MPQC_GD_options_btn)

        buttonGroup1Layout.addLayout(layout43,1,0)

        layout44 = QHBoxLayout(None,0,6,"layout44")

        self.MPQC_ESP_checkbox = QCheckBox(self.buttonGroup1,"MPQC_ESP_checkbox")
        layout44.addWidget(self.MPQC_ESP_checkbox)

        self.ESP_window_combox = QComboBox(0,self.buttonGroup1,"ESP_window_combox")
        self.ESP_window_combox.setEnabled(0)
        layout44.addWidget(self.ESP_window_combox)

        buttonGroup1Layout.addLayout(layout44,0,0)

        self.AIREBO_checkbox = QCheckBox(self.buttonGroup1,"AIREBO_checkbox")

        buttonGroup1Layout.addWidget(self.AIREBO_checkbox,2,0)

        NanoHiveDialogLayout.addWidget(self.buttonGroup1,2,0)

        self.buttonGroup1_2 = QButtonGroup(self,"buttonGroup1_2")
        self.buttonGroup1_2.setColumnLayout(0,Qt.Vertical)
        self.buttonGroup1_2.layout().setSpacing(6)
        self.buttonGroup1_2.layout().setMargin(11)
        buttonGroup1_2Layout = QVBoxLayout(self.buttonGroup1_2.layout())
        buttonGroup1_2Layout.setAlignment(Qt.AlignTop)

        self.Measurements_to_File_checkbox = QCheckBox(self.buttonGroup1_2,"Measurements_to_File_checkbox")
        buttonGroup1_2Layout.addWidget(self.Measurements_to_File_checkbox)

        self.POVRayVideo_checkbox = QCheckBox(self.buttonGroup1_2,"POVRayVideo_checkbox")
        buttonGroup1_2Layout.addWidget(self.POVRayVideo_checkbox)

        NanoHiveDialogLayout.addWidget(self.buttonGroup1_2,3,0)

        self.nh_instance_grpbox = QGroupBox(self,"nh_instance_grpbox")
        self.nh_instance_grpbox.setColumnLayout(0,Qt.Vertical)
        self.nh_instance_grpbox.layout().setSpacing(6)
        self.nh_instance_grpbox.layout().setMargin(11)
        nh_instance_grpboxLayout = QGridLayout(self.nh_instance_grpbox.layout())
        nh_instance_grpboxLayout.setAlignment(Qt.AlignTop)

        self.nh_instance_combox = QComboBox(0,self.nh_instance_grpbox,"nh_instance_combox")

        nh_instance_grpboxLayout.addWidget(self.nh_instance_combox,0,0)
        spacer5 = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        nh_instance_grpboxLayout.addItem(spacer5,0,1)

        NanoHiveDialogLayout.addWidget(self.nh_instance_grpbox,4,0)
        spacer6 = QSpacerItem(20,16,QSizePolicy.Minimum,QSizePolicy.Expanding)
        NanoHiveDialogLayout.addItem(spacer6,5,0)

        layout28 = QHBoxLayout(None,0,6,"layout28")

        self.run_sim_btn = QPushButton(self,"run_sim_btn")
        self.run_sim_btn.setDefault(1)
        layout28.addWidget(self.run_sim_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        self.cancel_btn.setDefault(0)
        layout28.addWidget(self.cancel_btn)

        NanoHiveDialogLayout.addLayout(layout28,6,0)

        self.languageChange()

        self.resize(QSize(355,648).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.run_sim_btn,SIGNAL("clicked()"),self.accept)
        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.reject)
        self.connect(self.MPQC_ESP_checkbox,SIGNAL("toggled(bool)"),self.update_ESP_window_combox)
        self.connect(self.MPQC_GD_checkbox,SIGNAL("toggled(bool)"),self.update_MPQC_GD_options_btn)
        self.connect(self.ESP_window_combox,SIGNAL("activated(int)"),self.set_ESP_window)
        self.connect(self.MPQC_GD_options_btn,SIGNAL("clicked()"),self.show_MPQC_GD_options_dialog)


    def languageChange(self):
        self.setCaption(self.__tr("Nano-Hive Setup"))
        self.namelbl.setText(self.__tr("Name :"))
        self.desclbl.setText(self.__tr("Description :"))
        self.name_linedit.setText(QString.null)
        self.parms_grpbox.setTitle(self.__tr("Parameters"))
        self.textLabel5.setText(self.__tr("Total Frames:"))
        self.textLabel2.setText(self.__tr("Steps per Frame :"))
        self.textLabel3.setText(self.__tr("Temperature :"))
        self.textLabel2_2.setText(self.__tr("0.1 femtosecond"))
        self.textLabel3_2.setText(self.__tr("Kelvin"))
        self.buttonGroup1.setTitle(self.__tr("Physical Interaction Plugins"))
        self.MPQC_GD_checkbox.setText(self.__tr("MPQC - Gradient Dynamics"))
        self.MPQC_GD_options_btn.setText(self.__tr("Options..."))
        self.MPQC_ESP_checkbox.setText(self.__tr("MPQC - ESP Plane"))
        self.ESP_window_combox.clear()
        self.ESP_window_combox.insertItem(self.__tr("(No ESP Window jigs)"))
        self.AIREBO_checkbox.setText(self.__tr("AIREBO"))
        self.buttonGroup1_2.setTitle(self.__tr("Results Plugins"))
        self.Measurements_to_File_checkbox.setText(self.__tr("Measurement Set to File"))
        self.POVRayVideo_checkbox.setText(self.__tr("POV-Ray Video"))
        self.nh_instance_grpbox.setTitle(self.__tr("Nano-Hive Instance"))
        self.nh_instance_combox.clear()
        self.nh_instance_combox.insertItem(self.__tr("My Computer"))
        self.run_sim_btn.setText(self.__tr("Run Simulation"))
        self.cancel_btn.setText(self.__tr("Cancel"))


    def update_ESP_window_combox(self):
        print "NanoHiveDialog.update_ESP_window_combox(): Not implemented yet"

    def update_MPQC_GD_options_btn(self):
        print "NanoHiveDialog.update_MPQC_GD_options_btn(): Not implemented yet"

    def set_ESP_window(self):
        print "NanoHiveDialog.set_ESP_window(): Not implemented yet"

    def show_MPQC_GD_options_dialog(self):
        print "NanoHiveDialog.show_MPQC_GD_options_dialog(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("NanoHiveDialog",s,c)
