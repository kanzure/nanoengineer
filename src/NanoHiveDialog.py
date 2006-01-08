# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\atom\cad\src\NanoHiveDialog.ui'
#
# Created: Sun Jan 8 13:48:51 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!


from qt import *

image0_data = [
"20 20 88 2",
".o c #000000",
".U c #000d00",
".4 c #001a00",
".i c #003500",
".y c #005d00",
".3 c #007800",
".W c #007f00",
"## c #008500",
"#n c #009100",
"#b c #009200",
".u c #00a000",
".n c #00a100",
"#j c #00ad00",
"#m c #00ae00",
".p c #00bb00",
".V c #00be00",
".z c #00d300",
".I c #00d500",
"#a c #00de00",
".5 c #00e400",
".K c #00e800",
"#c c #00f100",
".J c #00f300",
".b c #00fd00",
".m c #00ff00",
".X c #012501",
"#p c #012601",
".2 c #08a408",
".T c #08a508",
".1 c #09be09",
".Y c #0be50b",
"#o c #0ce50c",
".S c #0dfe0d",
".L c #15d915",
"#r c #15da15",
".A c #1afe1a",
".l c #21b321",
".h c #21b421",
".q c #21fe21",
".j c #27c927",
".g c #35fe35",
".E c #3ac23a",
".x c #3bc33b",
".R c #3ffe3f",
".D c #44d344",
".t c #50fe50",
"#d c #52fe52",
"#. c #54d154",
".w c #5dfe5d",
".f c #5ffe5f",
"#f c #62de62",
"#l c #6de06d",
"#i c #6ee06e",
".k c #74fe74",
".r c #79fe79",
"#s c #7afe7a",
"#e c #7efe7e",
"#k c #7fe87f",
".v c #7ffe7f",
".9 c #85fe85",
".Q c #86ef86",
".7 c #86fe86",
".H c #87ef87",
".0 c #8cfe8c",
".C c #90fe90",
".P c #9df39d",
".8 c #9efe9e",
".d c #9ffd9f",
".a c #a0fda0",
"#v c #a0ffa0",
"#t c #a1ffa1",
"#h c #adfead",
".6 c #aefeae",
".Z c #b2feb2",
".c c #bafdba",
"#u c #bbffbb",
"#g c #befebe",
".M c #bff9bf",
"#q c #c0f9c0",
".G c #d5fed5",
".F c #defede",
".B c #e4fee4",
".O c #ebfeeb",
".s c #eefeee",
".N c #f1fef1",
".# c #fdfefd",
".e c #fefefe",
"Qt c #ffffff",
"Qt.#.#.a.b.b.c.#.#QtQt.#.#.c.b.b.d.#.#.e",
"Qt.f.g.h.i.i.j.g.kQtQt.k.g.j.i.i.l.g.f.e",
"Qt.g.m.n.o.o.p.m.q.r.s.t.m.p.o.o.u.m.g.e",
"Qt.v.w.x.y.y.z.m.m.A.B.C.w.D.y.y.E.w.v.e",
"Qt.F.G.H.I.I.J.K.I.L.M.N.O.P.I.I.Q.G.F.e",
"Qt.R.S.T.U.U.V.W.U.X.Y.Z.0.1.U.U.2.S.R.e",
"Qt.g.m.n.o.o.p.3.o.4.5.6.7.p.o.o.u.m.g.e",
"Qt.8.9#.#####a.V###b#c#d#e#f#####..9.8.e",
"Qt#g#h#i#j#j.K.m.5#j#j.5#d#k#j#j#l#h#g.e",
"Qt.g.m.n.o.o.p.m#m.o.o#m.m.p.o.o.u.m.g.e",
"Qt.g.m.n.o.o.p.m#m.o.o#m.m.p.o.o.u.m.g.e",
"Qt#g#h#i#j#j#k#d.5#j#j.5.m.K#j#j#l#h#g.e",
"Qt.8.9#.#####f#e#d#c#n##.V#a#####..9.8.e",
"Qt.g.m.n.o.o.p.7.6.5.4.o.3.p.o.o.u.m.g.e",
"Qt.R.S.T.U.U.1.0.Z#o#p.U.W.V.U.U.2.S.R.e",
"Qt.F.G.H.I.I.P.O.N#q#r.I.K.J.I.I.Q.G.F.e",
"Qt.v.w.x.y.y.D.w.C.B.A.m.m.z.y.y.E.w.v.e",
"Qt.g.m.n.o.o.p.m.t.s#s.q.m.p.o.o.u.m.g.e",
"Qt.f.g.h.i.i.j.g.kQtQt.k.g.j.i.i.l.g.f.e",
"QtQtQt#t.m.m#uQtQtQtQtQtQt#u.m.m#vQtQtQt"
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

        self.ESP_image_combox = QComboBox(0,self.buttonGroup1,"ESP_image_combox")
        self.ESP_image_combox.setEnabled(0)
        layout44.addWidget(self.ESP_image_combox)

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
        self.connect(self.ESP_image_combox,SIGNAL("activated(int)"),self.set_ESP_window)
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
        self.ESP_image_combox.clear()
        self.ESP_image_combox.insertItem(self.__tr("(No ESP Image jigs)"))
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
