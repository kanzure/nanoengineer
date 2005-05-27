# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'GamessPropDialog.ui'
#
# Created: Thu May 26 22:32:45 2005
#      by: The PyQt User Interface Compiler (pyuic) 3.13
#
# WARNING! All changes made in this file will be lost!


from qt import *


class GamessPropDialog(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if not name:
            self.setName("GamessPropDialog")


        GamessPropDialogLayout = QVBoxLayout(self,11,6,"GamessPropDialogLayout")

        layout35 = QGridLayout(None,1,1,0,6,"layout35")

        self.atoms_list_btn = QPushButton(self,"atoms_list_btn")

        layout35.addWidget(self.atoms_list_btn,0,2)

        self.name_linedit = QLineEdit(self,"name_linedit")
        self.name_linedit.setFrameShape(QLineEdit.LineEditPanel)
        self.name_linedit.setFrameShadow(QLineEdit.Sunken)

        layout35.addWidget(self.name_linedit,0,1)

        self.psets_combox = QComboBox(0,self,"psets_combox")

        layout35.addWidget(self.psets_combox,1,1)

        self.atoms_list_btn_2 = QPushButton(self,"atoms_list_btn_2")

        layout35.addWidget(self.atoms_list_btn_2,1,2)

        self.psetslbl = QLabel(self,"psetslbl")
        self.psetslbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout35.addWidget(self.psetslbl,1,0)

        self.namelbl = QLabel(self,"namelbl")
        self.namelbl.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)

        layout35.addWidget(self.namelbl,0,0)
        GamessPropDialogLayout.addLayout(layout35)

        layout25 = QHBoxLayout(None,0,6,"layout25")

        self.txtlabel4 = QLabel(self,"txtlabel4")
        self.txtlabel4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout25.addWidget(self.txtlabel4)

        self.comment_linedit = QLineEdit(self,"comment_linedit")
        self.comment_linedit.setMaxLength(80)
        layout25.addWidget(self.comment_linedit)
        GamessPropDialogLayout.addLayout(layout25)

        self.groupBox1 = QGroupBox(self,"groupBox1")
        self.groupBox1.setColumnLayout(0,Qt.Vertical)
        self.groupBox1.layout().setSpacing(6)
        self.groupBox1.layout().setMargin(11)
        groupBox1Layout = QGridLayout(self.groupBox1.layout())
        groupBox1Layout.setAlignment(Qt.AlignTop)

        layout11 = QHBoxLayout(None,0,6,"layout11")

        self.gbasis_label = QLabel(self.groupBox1,"gbasis_label")
        self.gbasis_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout11.addWidget(self.gbasis_label)

        self.gbasis_combox = QComboBox(0,self.groupBox1,"gbasis_combox")
        layout11.addWidget(self.gbasis_combox)

        groupBox1Layout.addLayout(layout11,0,1)

        self.scftyp_btngrp = QButtonGroup(self.groupBox1,"scftyp_btngrp")
        self.scftyp_btngrp.setExclusive(1)
        self.scftyp_btngrp.setColumnLayout(0,Qt.Vertical)
        self.scftyp_btngrp.layout().setSpacing(6)
        self.scftyp_btngrp.layout().setMargin(11)
        scftyp_btngrpLayout = QGridLayout(self.scftyp_btngrp.layout())
        scftyp_btngrpLayout.setAlignment(Qt.AlignTop)

        layout33 = QHBoxLayout(None,0,6,"layout33")

        self.rhf_radiobtn = QRadioButton(self.scftyp_btngrp,"rhf_radiobtn")
        self.rhf_radiobtn.setChecked(1)
        self.scftyp_btngrp.insert( self.rhf_radiobtn,-1)
        layout33.addWidget(self.rhf_radiobtn)

        self.uhf_radiobtn = QRadioButton(self.scftyp_btngrp,"uhf_radiobtn")
        self.scftyp_btngrp.insert( self.uhf_radiobtn,-1)
        layout33.addWidget(self.uhf_radiobtn)

        self.rohf_radiobtn = QRadioButton(self.scftyp_btngrp,"rohf_radiobtn")
        self.scftyp_btngrp.insert( self.rohf_radiobtn,-1)
        layout33.addWidget(self.rohf_radiobtn)

        scftyp_btngrpLayout.addLayout(layout33,0,0)

        groupBox1Layout.addWidget(self.scftyp_btngrp,0,0)

        layout23 = QHBoxLayout(None,0,6,"layout23")

        self.textLabel1_4 = QLabel(self.groupBox1,"textLabel1_4")
        self.textLabel1_4.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout23.addWidget(self.textLabel1_4)

        self.icharg_spinbox = QSpinBox(self.groupBox1,"icharg_spinbox")
        self.icharg_spinbox.setMaxValue(1)
        self.icharg_spinbox.setMinValue(-1)
        layout23.addWidget(self.icharg_spinbox)

        self.textLabel1_2_2 = QLabel(self.groupBox1,"textLabel1_2_2")
        self.textLabel1_2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout23.addWidget(self.textLabel1_2_2)

        self.multi_combox = QComboBox(0,self.groupBox1,"multi_combox")
        layout23.addWidget(self.multi_combox)

        groupBox1Layout.addLayout(layout23,1,0)
        GamessPropDialogLayout.addWidget(self.groupBox1)

        self.groupBox2 = QGroupBox(self,"groupBox2")
        self.groupBox2.setColumnLayout(0,Qt.Vertical)
        self.groupBox2.layout().setSpacing(6)
        self.groupBox2.layout().setMargin(11)
        groupBox2Layout = QHBoxLayout(self.groupBox2.layout())
        groupBox2Layout.setAlignment(Qt.AlignTop)

        layout31 = QVBoxLayout(None,0,6,"layout31")

        self.mplvl_btngrp = QButtonGroup(self.groupBox2,"mplvl_btngrp")
        self.mplvl_btngrp.setExclusive(1)
        self.mplvl_btngrp.setColumnLayout(0,Qt.Vertical)
        self.mplvl_btngrp.layout().setSpacing(6)
        self.mplvl_btngrp.layout().setMargin(11)
        mplvl_btngrpLayout = QGridLayout(self.mplvl_btngrp.layout())
        mplvl_btngrpLayout.setAlignment(Qt.AlignTop)

        layout30 = QHBoxLayout(None,0,6,"layout30")

        self.none_radiobtn = QRadioButton(self.mplvl_btngrp,"none_radiobtn")
        self.none_radiobtn.setChecked(1)
        self.mplvl_btngrp.insert( self.none_radiobtn,-1)
        layout30.addWidget(self.none_radiobtn)

        self.dft_radiobtn = QRadioButton(self.mplvl_btngrp,"dft_radiobtn")
        layout30.addWidget(self.dft_radiobtn)

        self.mp2_radiobtn = QRadioButton(self.mplvl_btngrp,"mp2_radiobtn")
        self.mplvl_btngrp.insert( self.mp2_radiobtn,-1)
        layout30.addWidget(self.mp2_radiobtn)

        mplvl_btngrpLayout.addLayout(layout30,0,0)
        layout31.addWidget(self.mplvl_btngrp)

        self.core_electrons_checkbox = QCheckBox(self.groupBox2,"core_electrons_checkbox")
        self.core_electrons_checkbox.setEnabled(0)
        layout31.addWidget(self.core_electrons_checkbox)
        groupBox2Layout.addLayout(layout31)

        layout32 = QHBoxLayout(None,0,6,"layout32")

        layout22 = QVBoxLayout(None,0,6,"layout22")

        self.dfttyp_label = QLabel(self.groupBox2,"dfttyp_label")
        self.dfttyp_label.setEnabled(0)
        self.dfttyp_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout22.addWidget(self.dfttyp_label)

        self.gridsize_label = QLabel(self.groupBox2,"gridsize_label")
        self.gridsize_label.setEnabled(0)
        self.gridsize_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout22.addWidget(self.gridsize_label)
        layout32.addLayout(layout22)

        layout23_2 = QVBoxLayout(None,0,6,"layout23_2")

        self.dfttyp_combox = QComboBox(0,self.groupBox2,"dfttyp_combox")
        self.dfttyp_combox.setEnabled(0)
        layout23_2.addWidget(self.dfttyp_combox)

        self.gridsize_combox = QComboBox(0,self.groupBox2,"gridsize_combox")
        self.gridsize_combox.setEnabled(0)
        layout23_2.addWidget(self.gridsize_combox)
        layout32.addLayout(layout23_2)
        groupBox2Layout.addLayout(layout32)
        GamessPropDialogLayout.addWidget(self.groupBox2)

        self.groupBox3 = QGroupBox(self,"groupBox3")
        self.groupBox3.setColumnLayout(0,Qt.Vertical)
        self.groupBox3.layout().setSpacing(6)
        self.groupBox3.layout().setMargin(11)
        groupBox3Layout = QVBoxLayout(self.groupBox3.layout())
        groupBox3Layout.setAlignment(Qt.AlignTop)

        layout27 = QHBoxLayout(None,0,6,"layout27")

        layout29 = QHBoxLayout(None,0,6,"layout29")

        self.textLabel5 = QLabel(self.groupBox3,"textLabel5")
        self.textLabel5.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout29.addWidget(self.textLabel5)

        self.density_conv_combox = QComboBox(0,self.groupBox3,"density_conv_combox")
        layout29.addWidget(self.density_conv_combox)
        layout27.addLayout(layout29)

        layout26 = QHBoxLayout(None,0,6,"layout26")

        self.textLabel2_2 = QLabel(self.groupBox3,"textLabel2_2")
        self.textLabel2_2.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
        layout26.addWidget(self.textLabel2_2)

        self.ram_combox = QComboBox(0,self.groupBox3,"ram_combox")
        layout26.addWidget(self.ram_combox)
        layout27.addLayout(layout26)
        groupBox3Layout.addLayout(layout27)

        layout54 = QHBoxLayout(None,0,6,"layout54")

        layout50 = QVBoxLayout(None,0,6,"layout50")

        self.extrap_checkbox = QCheckBox(self.groupBox3,"extrap_checkbox")
        self.extrap_checkbox.setChecked(1)
        layout50.addWidget(self.extrap_checkbox)

        self.dirscf_checkbox = QCheckBox(self.groupBox3,"dirscf_checkbox")
        self.dirscf_checkbox.setChecked(1)
        layout50.addWidget(self.dirscf_checkbox)
        layout54.addLayout(layout50)

        layout51 = QVBoxLayout(None,0,6,"layout51")

        self.damp_checkbox = QCheckBox(self.groupBox3,"damp_checkbox")
        layout51.addWidget(self.damp_checkbox)

        self.diis_checkbox = QCheckBox(self.groupBox3,"diis_checkbox")
        self.diis_checkbox.setChecked(1)
        layout51.addWidget(self.diis_checkbox)
        layout54.addLayout(layout51)

        layout52 = QVBoxLayout(None,0,6,"layout52")

        self.shift_checkbox = QCheckBox(self.groupBox3,"shift_checkbox")
        layout52.addWidget(self.shift_checkbox)

        self.soscf_checkbox = QCheckBox(self.groupBox3,"soscf_checkbox")
        layout52.addWidget(self.soscf_checkbox)
        layout54.addLayout(layout52)

        layout53 = QVBoxLayout(None,0,6,"layout53")

        self.rstrct_checkbox = QCheckBox(self.groupBox3,"rstrct_checkbox")
        layout53.addWidget(self.rstrct_checkbox)
        layout54.addLayout(layout53)
        groupBox3Layout.addLayout(layout54)
        GamessPropDialogLayout.addWidget(self.groupBox3)

        layout23_3 = QHBoxLayout(None,0,6,"layout23_3")

        self.save_parms_btn = QPushButton(self,"save_parms_btn")
        layout23_3.addWidget(self.save_parms_btn)

        self.run_gamess_btn = QPushButton(self,"run_gamess_btn")
        layout23_3.addWidget(self.run_gamess_btn)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        layout23_3.addWidget(self.cancel_btn)
        GamessPropDialogLayout.addLayout(layout23_3)

        self.languageChange()

        self.resize(QSize(475,500).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.cancel_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.mplvl_btngrp,SIGNAL("clicked(int)"),self.set_mplevel)
        self.connect(self.save_parms_btn,SIGNAL("clicked()"),self.writeinpfile)
        self.connect(self.atoms_list_btn,SIGNAL("clicked()"),self.open_atoms_list_in_editor)
        self.connect(self.name_linedit,SIGNAL("returnPressed()"),self.set_jig_filenames)
        self.connect(self.run_gamess_btn,SIGNAL("clicked()"),self.run_gamess)
        self.connect(self.multi_combox,SIGNAL("activated(int)"),self.set_multiplicity)
        self.connect(self.psets_combox,SIGNAL("activated(int)"),self.add_pset)


    def languageChange(self):
        self.setCaption(self.__tr("GAMESS Properties"))
        self.atoms_list_btn.setText(self.__tr("Atom List..."))
        self.name_linedit.setText(QString.null)
        QToolTip.add(self.name_linedit,self.__tr("The name of the GAMESS jig.."))
        QWhatsThis.add(self.name_linedit,self.__tr("The name of the GAMESS jig.."))
        self.atoms_list_btn_2.setText(self.__tr("Edit/Delete..."))
        self.psetslbl.setText(self.__tr("Parameter Set :"))
        self.namelbl.setText(self.__tr("Name :"))
        self.txtlabel4.setText(self.__tr("Comment :"))
        self.comment_linedit.setText(QString.null)
        QToolTip.add(self.comment_linedit,self.__tr("Text placed here is incorporated into the standard GAMESS comment line."))
        QWhatsThis.add(self.comment_linedit,self.__tr("Text placed here is incorporated into the standard GAMESS comment line."))
        self.groupBox1.setTitle(self.__tr("Electronic Structure Properties and Basis Set Selection"))
        self.gbasis_label.setText(self.__tr("Basis Set :"))
        self.gbasis_combox.clear()
        self.gbasis_combox.insertItem(self.__tr("AM1"))
        self.gbasis_combox.insertItem(self.__tr("PM3"))
        self.gbasis_combox.insertItem(self.__tr("STO-3G"))
        self.gbasis_combox.insertItem(self.__tr("STO-6G"))
        self.gbasis_combox.insertItem(self.__tr("3-21G"))
        self.gbasis_combox.insertItem(self.__tr("3-21G*"))
        self.gbasis_combox.insertItem(self.__tr("6-31G"))
        self.gbasis_combox.insertItem(self.__tr("6-31G(d)"))
        self.gbasis_combox.insertItem(self.__tr("6-31G(d,p)"))
        self.gbasis_combox.insertItem(self.__tr("6-31+G(d)"))
        self.gbasis_combox.insertItem(self.__tr("6-31+G(d,p)"))
        self.gbasis_combox.insertItem(self.__tr("6-31++G(d)"))
        self.gbasis_combox.insertItem(self.__tr("6-31++G(d,p)"))
        self.gbasis_combox.insertItem(self.__tr("6-311G"))
        self.gbasis_combox.insertItem(self.__tr("6-311G(d)"))
        self.gbasis_combox.insertItem(self.__tr("6-311G(d,p)"))
        self.gbasis_combox.insertItem(self.__tr("6-311+G(d,p)"))
        self.gbasis_combox.insertItem(self.__tr("6-311++G(d,p)"))
        self.gbasis_combox.setCurrentItem(0)
        QToolTip.add(self.gbasis_combox,self.__tr("Select from among the standard Gaussian-type basis sets and semi-empirical parameters in GAMESS."))
        QWhatsThis.add(self.gbasis_combox,self.__tr("Select from among the standard Gaussian-type basis sets and semi-empirical parameters in GAMESS."))
        self.scftyp_btngrp.setTitle(QString.null)
        self.rhf_radiobtn.setText(self.__tr("RHF"))
        QToolTip.add(self.rhf_radiobtn,self.__tr("Restricted Hartree-Fock.  All electrons are paired and each spatial orbital is doubly occupied.  Cannot be used with multiplicities greater than 1."))
        QWhatsThis.add(self.rhf_radiobtn,self.__tr("Restricted Hartree-Fock.  All electrons are paired and each spatial orbital is doubly occupied.  Cannot be used with multiplicities greater than 1."))
        self.uhf_radiobtn.setText(self.__tr("UHF"))
        QToolTip.add(self.uhf_radiobtn,self.__tr("Unrestricted Hartree-Fock.  All electrons are unpaired and spatial (spin) orbitals are uniquely defined for each electron.  More time consuming, but more accurate, than ROHF.  "))
        QWhatsThis.add(self.uhf_radiobtn,self.__tr("Unrestricted Hartree-Fock.  All electrons are unpaired and spatial (spin) orbitals are uniquely defined for each electron.  More time consuming, but more accurate, than ROHF.  "))
        self.rohf_radiobtn.setText(self.__tr("ROHF"))
        QToolTip.add(self.rohf_radiobtn,self.__tr("Restricted Open-shell Hartree-Fock.  Spin-paired electrons are assigned to doubly-occupied spatial orbitals, while electrons with unpaired spins are provided unique spatial orbitals."))
        QWhatsThis.add(self.rohf_radiobtn,self.__tr("Restricted Open-shell Hartree-Fock.  Spin-paired electrons are assigned to doubly-occupied spatial orbitals, while electrons with unpaired spins are provided unique spatial orbitals."))
        self.textLabel1_4.setText(self.__tr("Charge:"))
        QToolTip.add(self.icharg_spinbox,self.__tr("The total charge of the structure to be treated quantum mechanically."))
        QWhatsThis.add(self.icharg_spinbox,self.__tr("The total charge of the structure to be treated quantum mechanically."))
        self.textLabel1_2_2.setText(self.__tr("Multiplicity:"))
        self.multi_combox.clear()
        self.multi_combox.insertItem(self.__tr("1"))
        self.multi_combox.insertItem(self.__tr("2"))
        self.multi_combox.insertItem(self.__tr("3"))
        self.multi_combox.insertItem(self.__tr("4"))
        self.multi_combox.insertItem(self.__tr("5"))
        self.multi_combox.insertItem(self.__tr("6"))
        self.multi_combox.insertItem(self.__tr("7"))
        QToolTip.add(self.multi_combox,self.__tr("N + 1, where N is the number of unpaired electrons."))
        QWhatsThis.add(self.multi_combox,self.__tr("N + 1, where N is the number of unpaired electrons."))
        self.groupBox2.setTitle(self.__tr("Electron Correlation Method"))
        self.mplvl_btngrp.setTitle(QString.null)
        self.none_radiobtn.setText(self.__tr("None"))
        QToolTip.add(self.none_radiobtn,self.__tr("Select this button to neglect electron correlation in the calculation."))
        QWhatsThis.add(self.none_radiobtn,self.__tr("Select this button to neglect electron correlation in the calculation."))
        self.dft_radiobtn.setText(self.__tr("DFT"))
        QToolTip.add(self.dft_radiobtn,self.__tr("Select this button to perform a density functional theory calculation."))
        QWhatsThis.add(self.dft_radiobtn,self.__tr("Select this button to perform a density functional theory calculation."))
        self.mp2_radiobtn.setText(self.__tr("MP2"))
        QToolTip.add(self.mp2_radiobtn,self.__tr("Select this button to perform a Second-Order Moeller Plesset calculation."))
        QWhatsThis.add(self.mp2_radiobtn,self.__tr("Select this button to perform a Second-Order Moeller Plesset calculation."))
        self.core_electrons_checkbox.setText(self.__tr("Include core electrons"))
        QToolTip.add(self.core_electrons_checkbox,self.__tr("Check this box to include both the valence and core electrons in the MP2 calculation."))
        QWhatsThis.add(self.core_electrons_checkbox,self.__tr("Check this box to include both the valence and core electrons in the MP2 calculation."))
        self.dfttyp_label.setText(self.__tr("Functional:"))
        self.gridsize_label.setText(self.__tr("Grid Size:"))
        self.dfttyp_combox.clear()
        self.dfttyp_combox.insertItem(self.__tr("SLATER (E)"))
        self.dfttyp_combox.insertItem(self.__tr("BECKE (E)"))
        self.dfttyp_combox.insertItem(self.__tr("GILL (E)"))
        self.dfttyp_combox.insertItem(self.__tr("PBE (E)"))
        self.dfttyp_combox.insertItem(self.__tr("VWN (C)"))
        self.dfttyp_combox.insertItem(self.__tr("LYP (C)"))
        self.dfttyp_combox.insertItem(self.__tr("OP (C)"))
        self.dfttyp_combox.insertItem(self.__tr("SVWN/LDA (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("SLYP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("SOP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("BVWN (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("BLYP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("BOP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("GVWN (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("GLYP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("GOP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("PBEVWN (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("PBELYP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("PBEOP (E+C)"))
        self.dfttyp_combox.insertItem(self.__tr("BHHLYP (H)"))
        self.dfttyp_combox.insertItem(self.__tr("B3LYP (H)"))
        QToolTip.add(self.dfttyp_combox,self.__tr("Select an available density functional in GAMESS."))
        QWhatsThis.add(self.dfttyp_combox,self.__tr("Select an available density functional in GAMESS."))
        self.gridsize_combox.clear()
        self.gridsize_combox.insertItem(self.__tr("Coarse"))
        self.gridsize_combox.insertItem(self.__tr("Default"))
        self.gridsize_combox.insertItem(self.__tr("Fine"))
        self.gridsize_combox.insertItem(self.__tr("Army Grade"))
        self.gridsize_combox.setCurrentItem(1)
        QToolTip.add(self.gridsize_combox,self.__tr("Select the grid spacing for the DFT calculation."))
        QWhatsThis.add(self.gridsize_combox,self.__tr("Select the grid spacing for the DFT calculation."))
        self.groupBox3.setTitle(self.__tr("Convergence Criteria and Memory Usage"))
        self.textLabel5.setText(self.__tr("Density Convergence :"))
        self.density_conv_combox.clear()
        self.density_conv_combox.insertItem(self.__tr("Coarse (10E-4)"))
        self.density_conv_combox.insertItem(self.__tr("Default (10E-5)"))
        self.density_conv_combox.insertItem(self.__tr("Fine (10E-6)"))
        self.density_conv_combox.insertItem(self.__tr("Very Fine (10E-7)"))
        self.density_conv_combox.setCurrentItem(1)
        QToolTip.add(self.density_conv_combox,self.__tr("Selects the accuracy of the electron density convergence for the energy calculation."))
        QWhatsThis.add(self.density_conv_combox,self.__tr("Selects the accuracy of the electron density convergence for the energy calculation."))
        self.textLabel2_2.setText(self.__tr("RAM (MB) :"))
        self.ram_combox.clear()
        self.ram_combox.insertItem(self.__tr("Default"))
        self.ram_combox.insertItem(self.__tr("2000"))
        QToolTip.add(self.ram_combox,self.__tr("Select the amount of system memory to use in the energy calculation."))
        QWhatsThis.add(self.ram_combox,self.__tr("Select the amount of system memory to use in the energy calculation."))
        self.extrap_checkbox.setText(self.__tr("EXTRAP"))
        QToolTip.add(self.extrap_checkbox,self.__tr("Controls Pople extrapolation of the Fock matrix."))
        QWhatsThis.add(self.extrap_checkbox,self.__tr("Controls Pople extrapolation of the Fock matrix."))
        self.dirscf_checkbox.setText(self.__tr("DirectSCF"))
        QToolTip.add(self.dirscf_checkbox,self.__tr("Check this box to run the calculation in RAM and avoid hard disk usage for integral storage."))
        QWhatsThis.add(self.dirscf_checkbox,self.__tr("Check this box to run the calculation in RAM and avoid hard disk usage for integral storage."))
        self.damp_checkbox.setText(self.__tr("DAMP"))
        QToolTip.add(self.damp_checkbox,self.__tr("Controls Davidson damping of the Fock matrix."))
        QWhatsThis.add(self.damp_checkbox,self.__tr("Controls Davidson damping of the Fock matrix."))
        self.diis_checkbox.setText(self.__tr("DIIS"))
        QToolTip.add(self.diis_checkbox,self.__tr("Controls Pulay's DIIS interpolation."))
        QWhatsThis.add(self.diis_checkbox,self.__tr("Controls Pulay's DIIS interpolation."))
        self.shift_checkbox.setText(self.__tr("SHIFT"))
        QToolTip.add(self.shift_checkbox,self.__tr("Controls level shifting of the Fock matrix."))
        QWhatsThis.add(self.shift_checkbox,self.__tr("Controls level shifting of the Fock matrix."))
        self.soscf_checkbox.setText(self.__tr("SOSCF"))
        QToolTip.add(self.soscf_checkbox,self.__tr("Controls second order SCF orbital optimization."))
        QWhatsThis.add(self.soscf_checkbox,self.__tr("Controls second order SCF orbital optimization."))
        self.rstrct_checkbox.setText(self.__tr("RSTRCT"))
        QToolTip.add(self.rstrct_checkbox,self.__tr("Controls restriction of orbital interchanges."))
        QWhatsThis.add(self.rstrct_checkbox,self.__tr("Controls restriction of orbital interchanges."))
        self.save_parms_btn.setText(self.__tr("Save and Exit"))
        QToolTip.add(self.save_parms_btn,self.__tr("Save GAMESS parameters only."))
        QWhatsThis.add(self.save_parms_btn,self.__tr("Save GAMESS parameters only."))
        self.run_gamess_btn.setText(self.__tr("Save and Run GAMESS"))
        QToolTip.add(self.run_gamess_btn,self.__tr("Save GAMESS parameters and launch job."))
        self.cancel_btn.setText(self.__tr("Cancel"))
        QToolTip.add(self.cancel_btn,self.__tr("Closes this window."))
        QWhatsThis.add(self.cancel_btn,self.__tr("Closes this window."))


    def writeinpfile(self):
        print "GamessPropDialog.writeinpfile(): Not implemented yet"

    def set_mplevel(self):
        print "GamessPropDialog.set_mplevel(): Not implemented yet"

    def set_multiplicity(self):
        print "GamessPropDialog.set_multiplicity(): Not implemented yet"

    def open_atoms_list_in_editor(self):
        print "GamessPropDialog.open_atoms_list_in_editor(): Not implemented yet"

    def set_jig_filenames(self):
        print "GamessPropDialog.set_jig_filenames(): Not implemented yet"

    def run_gamess(self):
        print "GamessPropDialog.run_gamess(): Not implemented yet"

    def edit_gmshost(self):
        print "GamessPropDialog.edit_gmshost(): Not implemented yet"

    def remove_host(self):
        print "GamessPropDialog.remove_host(): Not implemented yet"

    def add_pset(self):
        print "GamessPropDialog.add_pset(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("GamessPropDialog",s,c)
