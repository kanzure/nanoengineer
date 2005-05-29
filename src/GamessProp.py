# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
runGamess.py

$Id$
'''
__author__ = "Mark"


# Ask Bruce where all this should ultimately live.

# This is the GAMESS UI widget default settings (for energy).

ui={'scftyp':0, 'icharg':0, 'mult':0, 'gbasis':0, 'ecm':0, 'dfttyp':0, 'gridsize':1, 'ncore':0,
        'conv':1, 'memory':70, 'extrap':1, 'dirscf':1, 'damp':0, 'shift':0, 'diis':1,'soscf':0,'rstrct':0}

# These are the GAMESS parms set defaults (for energy).

# $CONTRL group section ####################################
#
# The general form for the $CONTRL group is (keyword order does not matter):
#
#   $CONTRL
#   runtyp=energy coord=unique scftyp=rhf icharg=1 mult=1 mplevl=0 
#   maxit=200 inttyp=pople icut=11 qmttol=1.0E-6
#   $END
#
# $CONTRL group keywords and their default values.
contrl={'runtyp':'ENERGY', 'coord':'unique', 'scftyp':'RHF', 'icharg':0, 'mult':1, 'mplevl':'0', 
        'maxit':200, 'icut':11, 'inttyp':'hondo', 'qmttol':'1.0E-6', 'dfttyp':0, 'nprint':9}
# Note: The 'dfttyp' keyword in the $CONTRL group is only valid for PC GAMESS.

# $CONTRL keywords and their optional values 
scftyp=['RHF', 'UHF', 'ROHF'] # SCFTYP
mplevl=[ 0, 0, '2'] # MPLEVL: None=0, DFT=0, MP2='2'
inttyp=['pople', 'pople', 'hondo'] # Set by EMC, None=POPLE, DFT=POPLE, MP2=HONDO
nprint=-5,-2,7,8,9 # Not currently used. nprint is always 9 for now.

# $SCF group section ####################################
#
# The general form for the $SCF group is (keyword order does not matter):
#
#   $SCF
#   conv=10E-05 coord=unique extrap=.T. dirscf=.T. damp=.F shift=.F. diis=.T. soscf=.F. rstrct=.F.
#   $END
#
# $SCF group keywords and their default values.
scf={'conv':5, 'nconv':5, 'extrap':'.T.','dirscf':'.T.', 'damp':'.F.', 'shift':'.F.', 'diis':'.T.',
     'soscf':'.F.','rstrct':'.F.'}
# Note: Keyword 'conv' is used by GAMESS, 'nconv' is used by PC GAMESS.

# CONV keyword and its optional values
conv='10E-04','10E-05','10E-06','10E-07' # Density Convergence

# Useful true or false tuple.
tf='.F.', '.T.' # True/False for SCF parameters

# $SYSTEM group section ####################################
#
# The general form for the $SYSTEM group is:
#
#   $SYSTEM
#   timlim=1000 memory=70000000
#   $END
#
# $SYSTEM group keywords and their default values.
system={'timlim':1000, 'memory':70000000}

# $MP2 group section ####################################
#
# The general form for the $MP2 group is (keyword order does not matter):
#
#   $MP2
#   ncore=0
#   $END
#
# The $MP2 group is written only when the Electron Correlation Method = MP2.
# To include core electrons, we add the keyword NCORE=0.
# To exclude core electrons, we leave NCORE out of the $MP2 group altogether.
# So, with the checkbox not checked, ncore=0, and the NCORE keyword isn't written.
# With the checkbox checked, ncore='0' (string type), NCORE=0 is written.  Mark 050528.
mp2={'ncore':0} # Core electrons for MP2
ncore=[0, '0'] # Core electrons: Not included=0, Included='0'. 

# Useful Electron Correlation Method variables.
ecm=['None', 'DFT', 'MP2'] 
DFT=1
MP2=2

# $DFT group section (GAMESS only) ##############################
#
# The general form for the $DFT group is (keyword order does not matter):
#
#   $DFT
#    dfttyp=SLATER nrad=96 nthe=12 nphi=24 switch=3.0E-04
#   $END
#
# $DFT group keywords and their default values.
dft={'dfttyp':0, 'nrad':0}
# Note: In PC GAMESS, the $DFT group contains the grid size parameters 
# only, and the DFTTYP keyword is placed in the $CONTRL group.

# DFTTYP functions for GAMESS, specified by the DFTTYP keyword in the $DFT group.
# The PC GAMESS DFTTYP functions are different (see pcgms_dfttyp_items).
# The DFTTYP keyword values are the same without the '(x)' text.  The selected
# item is written to the $DFT group like this: dfttyp=SLATER
gms_dfttyp_items='SLATER (E)','BECKE (E)','GILL (E)','PBE (E)','VWN (C)', \
    'LYP (C)', 'OP (C)', 'SVWN (E+C)', 'SLYP (E+C)', 'SOP (E+C)', 'BVWN (E+C)', \
    'BLYP (E+C)', 'BOP (E+C)', 'GVWN (E+C)', 'GLYP (E+C)', 'GOP (E+C)', \
    'PBEVWN (E+C)', 'PBELYP (E+C)', 'PBEOP (E+C)', 'BHHLYP (H)', 'B3LYP (H)'

# DFTTYP functions for PC GAMESS. These are different for GAMESS.
# The DFTTYP keyword values are the same without the '(x)' text.                
pcgms_dfttyp_items = 'SLATER (E)','B88 (E)','GILL96 (E)','XPBE96 (E)','LYP (C)', \
    'VWN1RPA (C)','VWN5 (C)','PW91LDA (C)','CPBE96 (C)','CPW91 (C)', \
    'SLYP (E+C)','BLYP (E+C)','GLYP (E+C)','SVWN1RPA (E+C)', \
    'BVWN1RPA (E+C)','VWN5 (E+C)','BVWN5 (E+C)','PBE96 (E+C)', \
    'PBEPW91 (E+C)','B3LYP1 (H)','BELYP5 (H)','BHHLYP (H)','PBE0 (H)', \
    'PBE1PW91 (H)','B3PW91 (H)'

# The 5 DFT grid size parameters for:
#   - Course
#   - Default, 
#   - Fine
#   - Very Fine
#   - Army Grade.
# These are the $DFT grid size parameters for GAMESS.
gms_gridsize= '=48 nthe=12 nphi=24 switch=1.0E-03', \
                '96 nthe=12 nphi=24 switch=3.0E-04', \
                '96 nthe=24 nphi=48 switch=3.0E-04', \
                '96 nthe=36 nphi=72 switch=3.0E-04', \
                '96 nthe=36 nphi=72 switch=3.0E-04'
# Note: the first number is the 'nrad' parm. 'nrad=' is printed by the prin1 method.
                
# These are the $DFT grid size parameters for PC GAMESS.
pcgms_gridsize='48 lmax=19', \
                            '63 lmax=29', \
                            '63 lmax=53', \
                            '95 lmax=89', \
                            '128 lmax=131'
# Note: the first number is the 'nrad' parm. 'nrad=' is printed by the prin1 method.

# $GUESS group section ##############################
#
# The general form for the $GUESS group is:
#
#   $GUESS
#    guess=huckel
#   $END
#
# $GUESS group keywords and their default values.
guess={'guess':'huckel'}

# The GUESS keyword and its optional values
guess_keyword=['huckel', 'moread']
# Note: Writing the 'guess' keyword requires special case code in the prin1 method 
# since its group name is the same ('guess'). Mark 050529
    
# $STATPT group section ##############################
#
# The general form for the $STATPT group is:
#
#   $STATPT
#    hess=guess
#   $END
#
# $STATPT group keywords and their default values.
statpt={'hess':'guess'}

# The HESS keyword and its optional values
hess=['guess', 'read']

# $BASIS group section ##############################
#
# The general form for the $BASIS group is:
#
#   $BASIS
#   gbasis=AM1 NGAUSS=0 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.
#   $END
#
# $BASIS group keywords and their default values.
basis={'gbasis':'AM1'}

# The GBASIS keyword and its optional values
gbasis='AM1 NGAUSS=0 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'PM3 NGAUSS=0 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'STO NGAUSS=3 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'STO NGAUSS=6 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N21 NGAUSS=3 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N21 NGAUSS=3 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.T. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.T. DIFFS=.F.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.T. DIFFS=.T.', \
    'N31 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.T. DIFFS=.T.', \
    'N311 NGAUSS=6 NDFUNC=0 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.F. DIFFS=.F.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.T. DIFFS=.F.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.T. DIFFS=.F.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=0 NFFUNC=0 DIFFSP=.T. DIFFS=.T.', \
    'N311 NGAUSS=6 NDFUNC=1 NPFUNC=1 NFFUNC=0 DIFFSP=.T. DIFFS=.T.'

GAMESS = 1 # GAMESS-US (and WinGAMESS)
PCGAMESS = 2 # PC GAMESS

from qt import *
from GamessPropDialog import *
import sys, os, time
from constants import *

def get_gamess_info(gms_version):
    if gms_version == PCGAMESS:
        return "PC GAMESS"
    else:
        if sys.platform == "win32":
            return "WinGAMESS"
        else:
            return "GAMESS"
    
def open_file_in_editor(file):
    """Opens a file in a standard text editor.
    """
    if not os.path.exists(file): #bruce 050326 added this check
        msg = "File does not exist: " + file
        print msg
#        self.history.message(redmsg(msg))
        return
        
    editor = get_text_editor()
        
    if os.path.exists(editor):
        args = [editor, file]
#        print  "editor = ",editor
#        print  "Spawnv args are %r" % (args,)

        try:
            # Spawn the editor.
            kid = os.spawnv(os.P_NOWAIT, editor, args)
        except: # We had an exception.
#            print_compact_traceback("Exception in editor; continuing: ")
            msg = "Cannot open file " + file + ".  Trouble spawning editor " + editor
            print msg
#            self.history.message(redmsg(msg))
    else:
        msg = "Cannot open file " + file + ".  Editor " + editor + " not found."
#        self.history.message(redmsg(msg))
            
def get_text_editor():
    """Returns the name of a text editor for this platform.
    """
    if sys.platform == 'win32': # Windows
        editor = "C:/WINDOWS/notepad.exe"
    elif sys.platform == 'darwin': # MacOSX
        editor = "/usr/bin/open"
    else: # Linux
        editor = "/usr/bin/kwrite"
            
    return editor

                
class GamessProp(GamessPropDialog):
    def __init__(self, gamess, glpane):
        GamessPropDialog.__init__(self)
        
        self.gamess = gamess
        self.glpane = glpane
        self.name =gamess.name # The name of this GAMESS jig
        self.inputfile = '' # GAMESS INP filename
        self.outputfile = '' # GAMESS OUT filename (aka log file)
        self.datfile = 'PUNCH' # PC GAMESS only - will need to change this if GAMESS version.
        self.atomsfile = '' # Atoms List file containing $DATA info
        self.gmsbatfile = '' # The WinGAMESS batch filename.  Not implemented.

        # THESE FIRST 4 VARIABLES SHOULD BE GLOBAL
        # AND CHANGABLE FROM THE USER PREFS AREA.
        self.gmsver = PCGAMESS # Set this to GAMESS or PCGAMESS
        
        if self.gmsver == PCGAMESS:
            self.gmsdir = 'C:/PCGAMESS' # Full path to GAMESS directory
            self.gmspath = os.path.join(self.gmsdir, 'gamess.exe')  # Full path to PC GAMESS executable
        else:
            self.gmsdir = 'C:/WinGAMESS' # Full path to GAMESS directory
            if sys.platform == 'win32':
                self.gmspath = os.path.join(self.gmsdir, 'rungms.bat')  # Full path to WinGAMESS executable
            else:
                self.gmspath = os.path.join(self.gmsdir, 'rungms')  # Full path to GAMESS executable (Linux/Mac)
        
        wd = globalParms['WorkingDirectory'] # Get working directory.
        
        self.gmstmpdir  = os.path.join(wd,'gamess')
        if os.path.exists(self.gmstmpdir):
            print "Gamess tmpdir exists:", self.gmstmpdir
        else:
            os.mkdir(self.gmstmpdir)
            print "Created Gamess tmpdir:", self.gmstmpdir
        
        self.load_dfttyp_combox() # SHOULD LIVE ELSEWHERE. 
        
        if self.setup(0): return
        self.exec_loop()

    def setup(self, pnum):
        ''' Setup widgets to initial (default or defined) values. Return True on error.
        '''
        print "setup: pset number =", pnum
        
        gamess = self.gamess
        self.pset = self.gamess.pset_number(pnum)
        
        # Init the top widgets (name, psets drop box, comment)
        self.name_linedit.setText(self.name)
        self.load_psets_combox()
        self.psets_combox.setCurrentItem(pnum)
        self.update_comment()
        
        # Electronic Structure Props and Basis Set section.
        self.scftyp_btngrp.setButton(self.pset.ui.scftyp) # RHF, UHF, or ROHF
        self.gbasis_combox.setCurrentItem(self.pset.ui.gbasis) # Basis set
        self.icharg_spinbox.setValue(self.pset.ui.icharg) # Charge
        self.multi_combox.setCurrentItem(self.pset.ui.mult) # Multiplicity
        # Disable RHF if multiplicity is not the first item.
        if self.pset.ui.mult == 0:
            self.rhf_radiobtn.setEnabled(1) # Enable RHF
        else:
            self.rhf_radiobtn.setEnabled(0) # Disable RHF
        
        # Electron Correlation Method
        ecm = self.pset.ui.ecm
        print "Setup: ECM = ",ecm
        self.ecm_btngrp.setButton(self.pset.ui.ecm) # None, DFT or MP2
        self.set_ecmethod(self.pset.ui.ecm) # None, DFT or MP2
        self.dfttyp_combox.setCurrentItem(self.pset.ui.dfttyp) # DFT Functional
        self.gridsize_combox.setCurrentItem(self.pset.ui.gridsize) # Grid Size
        self.core_electrons_checkbox.setChecked(self.pset.ui.ncore) # Include core electrons
            
        # Convergence Criteria and Memory Usage
        # Set Density Convergence
        self.density_conv_combox.setCurrentItem(self.pset.ui.conv)
        # Set RAM
        self.extrap_checkbox.setChecked(self.pset.ui.extrap) # EXTRAP
        self.dirscf_checkbox.setChecked(self.pset.ui.dirscf) # DIRSCF
        self.damp_checkbox.setChecked(self.pset.ui.damp) # DAMP
        self.diis_checkbox.setChecked(self.pset.ui.diis) # DIIS
        self.shift_checkbox.setChecked(self.pset.ui.shift) # SHIFT
        self.soscf_checkbox.setChecked(self.pset.ui.soscf) # SOSCF
        self.rstrct_checkbox.setChecked(self.pset.ui.rstrct) # RSTRCT
        
        self.update_filenames() # This updates the GAMESS filenames.
        
        # If there is an error, return 1. NIY.
        return 0
        
    def rename(self):
        '''Rename the jig.
        '''
        self.name = str(self.name_linedit.text())
        self.update_comment()

    def add_pset(self, val):
        '''Add or change a pset from the pset combo box.'''
        # New.. was selected.  Add a new pset.
        if val == self.psets_combox.count()-1:
            print "add_pset: Adding new pset, val = ", val
            self.save_ui_settings() # Save the UI settings, which will also save parms set.
            self.pset = self.gamess.add_pset()
            self.setup(0)
        else: # Change to an existing pset.
            print "add_pset: Changing to existing pset, val = ", val
            self.save_ui_settings() # Save the UI settings, which will also save parms set.
            self.pset = self.gamess.pset_number(val)
            self.setup(val)

    def load_psets_combox(self):
        '''Load list of parms sets in the combobox widget'''
        
        # This currently loads 2 items.  It should load the combo box with a list
        # of the defaults or the actual list
        self.psets_combox.clear() # Clear all combo box items
        for p in self.gamess.psets[::-1]:
            self.psets_combox.insertItem(p.name)
        self.psets_combox.insertItem("New...")
        
    def rename_pset(self):
        '''Rename the current parms set name.
        '''
        self.pset.name = str(self.pset_name_linedit.text())
        self.update_pset_combox_item()
        self.update_comment()
        
    def update_pset_combox_item(self):
        '''Rename the current pset name in the combo box'''
        print 'update_pset_combox_item: Not Implemented Yet'

    def load_dfttyp_combox(self):
        '''Load list of DFT function in a combobox widget'''
        self.dfttyp_combox.clear() # Clear all combo box items
        if self.gmsver == GAMESS:
            for f in gms_dfttyp_items:
                self.dfttyp_combox.insertItem(f)
        else:
            for f in pcgms_dfttyp_items:
                self.dfttyp_combox.insertItem(f)
                
    def update_filenames(self):
        self.inputfile = self.name + '.inp'
        self.outputfile = self.name + '.out'
        self.atomsfile = self.name + '.xyz'
        self.gmsbatfile = ''
        
    def update_comment(self):
        timestr = "%s" % time.strftime("%Y-%m-%d %H:%M:%S")
        comment = 'Jig = "' + self.name + '" Parms Set = "' + self.pset.name + '" ' + timestr
        self.comment_linedit.setText(QString(comment))
        
    def set_ecmethod(self, val):
        '''Enable/disable widgets when user changes Electron Correlation Method.
        '''
#        print "set_ecmethod = ", val
        if val == DFT:
            self.dfttyp_label.setEnabled(1)
            self.dfttyp_combox.setEnabled(1)
            self.gridsize_label.setEnabled(1)
            self.gridsize_combox.setEnabled(1)
            self.core_electrons_checkbox.setChecked(0)
            self.core_electrons_checkbox.setEnabled(0)
            
        elif val == MP2:
            self.core_electrons_checkbox.setEnabled(1)
            self.dfttyp_label.setEnabled(0)
            self.dfttyp_combox.setEnabled(0)
            self.gridsize_label.setEnabled(0)
            self.gridsize_combox.setEnabled(0)
            
        else: #None
            self.dfttyp_label.setEnabled(0)
            self.dfttyp_combox.setEnabled(0)
            self.gridsize_label.setEnabled(0)
            self.gridsize_combox.setEnabled(0)
            self.core_electrons_checkbox.setChecked(0)
            self.core_electrons_checkbox.setEnabled(0)
            
    def set_multiplicity(self, val):
        '''Enable/disable widgets when user changes Multiplicity.
        '''
        
        if val != 0:
            if scftyp[self.scftyp_btngrp.selectedId()] != 'RHF':
                self.rhf_radiobtn.setEnabled(0)
                return
            
            ret = QMessageBox.warning( self, "Multiplicity Conflict",
                "If Multiplicity is greater than 1, then <b>UHF</b> or <b>ROHF</b> must be selected.\n"
                "Select Cancel to keep <b>RHF</b>.",
                "&UHF", "&ROHF", "Cancel",
                0, 2 )
            
            if ret==0: # UHF
                self.uhf_radiobtn.toggle()
                self.rhf_radiobtn.setEnabled(0)
                
            elif ret==1: # ROHF
                self.rohf_radiobtn.toggle()
                self.rhf_radiobtn.setEnabled(0)
            
            elif ret==2: # Cancel
                self.multi_combox.setCurrentItem(0)
        
        elif val == 0:
            self.rhf_radiobtn.setEnabled(1)
                
    def restore(self):
        '''Implement a button for Use Defaults or Restore Default Values, if one is added to the UI.
        '''
#        save_params = self.pset # save original params, in case of Cancel after this restore
#        self.setup() # set widgets to the restored values; also does unwanted set of self.myparms
#        self.myparms = save_params
        return

    def save_ui_settings(self):
        
        # Electronic Structure Props and Basis Set section.
        self.pset.ui.scftyp = self.scftyp_btngrp.selectedId() # SCFTYP = RHF, UHF, or ROHF
        self.pset.ui.icharg = self.icharg_spinbox.value() # Charge
        self.pset.ui.mult = self.multi_combox.currentItem() # Multiplicity
        
        # Electron Correlation Method
        self.pset.ui.ecm = self.ecm_btngrp.selectedId() # None, DFT or MP2
        self.pset.ui.inttyp = self.ecm_btngrp.selectedId() # INTTYP
        self.pset.ui.gbasis = self.gbasis_combox.currentItem() # Basis Set
        self.pset.ui.dfttyp = self.dfttyp_combox.currentItem() # DFT Functional Type
        self.pset.ui.gridsize = self.gridsize_combox.currentItem() # Grid Size
        self.pset.ui.ncore = self.core_electrons_checkbox.isChecked() # Include core electrons
        
        # Convergence Criteria and Memory Usage
        
        self.pset.ui.conv = self.density_conv_combox.currentItem() # Density Convergence
        self.pset.ui.memory = self.memory_spinbox.value() # Memory
        self.pset.ui.extrap = self.extrap_checkbox.isChecked() # EXTRAP
        self.pset.ui.dirscf = self.dirscf_checkbox.isChecked() # DIRSCF
        self.pset.ui.damp = self.damp_checkbox.isChecked() # DAMP
        self.pset.ui.diis = self.diis_checkbox.isChecked() # DIIS
        self.pset.ui.shift = self.shift_checkbox.isChecked() # SHIFT
        self.pset.ui.soscf = self.soscf_checkbox.isChecked() # SOSCF
        self.pset.ui.rstrct = self.rstrct_checkbox.isChecked() # RSTRCT
        
        self.save_parms() # Now save params.
        
    def save_parms(self):
        '''Save parameter set.'''
        
        # $CONTRL Section ###########################################
        
        # Parms Values
        self.pset.contrl.scftyp = scftyp[self.pset.ui.scftyp] # SCFTYP
        self.pset.contrl.icharg = str(self.pset.ui.icharg) # ICHARG
        self.pset.contrl.mult = str(self.pset.ui.mult) #MULT
        self.pset.contrl.mplevl = mplevl[self.pset.ui.ecm] # MPLEVL
        self.pset.contrl.inttyp = inttyp[self.pset.ui.inttyp] # INTTYP
        
        
        # ICUT and QMTTOL
        s = str(self.gbasis_combox.currentText())
        m = s.count('+') # If there is a plus sign in the basis set name, we have "diffuse orbitals"
        if m: # We have diffuse orbitals
            self.pset.contrl.icut = 11
            if sys.platform != 'win32': # PC GAMESS does not support QMTTOL. Mark 052105
                self.pset.contrl.qmttol = '3.0E-6'
            else:
                self.pset.contrl.qmttol = None
        else:  # No diffuse orbitals
            self.pset.contrl.icut = 9
            if self.gmsver == GAMESS: 
                self.pset.contrl.qmttol = '1.0E-6'
            else:
                self.pset.contrl.qmttol = None # PC GAMESS does not support QMTTOL. Mark 052105
        
        # DFTTYP (PC GAMESS only)
        # The DFTTYP keyword is included in the CONTRL section, not the $DFT group.
        if self.gmsver == PCGAMESS:
            if ecm[self.pset.ui.ecm] == 'DFT':
                item = pcgms_dfttyp_items[self.pset.ui.dfttyp] # Item's full text, including the '(xxx)'
                self.pset.contrl.dfttyp, junk = item.split(' ',1) # DFTTYPE, removing the '(xxx)'.
                self.pset.dft.nrad = pcgms_gridsize[self.pset.ui.gridsize] # Grid Size parameters
            else: # None or MP2
                self.pset.contrl.dfttyp = 0
                self.pset.dft.nrad = 0
        
        # $SCF Section ###########################################
        
        self.pset.scf.extrap = tf[self.pset.ui.extrap] # EXTRAP
        self.pset.scf.dirscf = tf[self.pset.ui.dirscf] # DIRSCF
        self.pset.scf.damp = tf[self.pset.ui.damp] # DAMP
        self.pset.scf.diis = tf[self.pset.ui.diis] # DIIS
        self.pset.scf.shift = tf[self.pset.ui.shift] # SHIFT
        self.pset.scf.soscf = tf[self.pset.ui.soscf] # SOSCF
        self.pset.scf.rstrct = tf[self.pset.ui.rstrct] # RSTRCT
        
        # CONV (GAMESS) or 
        # NCONV (PC GAMESS)
        if self.gmsver == GAMESS:
            self.pset.scf.conv = conv[self.pset.ui.conv] # CONV (GAMESS)
            self.pset.scf.nconv = 0 # Turn off NCONV
        else: # PC GAMESS
            self.pset.scf.nconv = conv[self.pset.ui.conv] # NCONV (PC GAMESS)
            self.pset.scf.conv = 0 # Turn off CONV
        
        # $SYSTEM Section ###########################################
        
        self.pset.system.timlin = 1000 # Time limit in minutes
        self.pset.system.memory = self.pset.ui.memory * 1000000
        
        # $MP2 Section ###########################################
        
        self.pset.mp2.ncore = ncore[self.pset.ui.ncore]
        
#        self.pset.mp2.ncore = None
#        if self.core_electrons_checkbox.isChecked():
#            self.pset.mp2.ncore = '0'
        
        # $DFT Section ###########################################

        # The DFT section record is supported in GAMESS only.
        if self.gmsver == GAMESS:
            if ecm[self.pset.ui.ecm] == 'DFT':
                item = gms_dfttyp_items[self.pset.ui.dfttyp]
                self.pset.dft.dfttyp, junk = item.split(' ',1) # DFTTYP in $CONTRL
                self.pset.dft.nrad = gms_gridsize[self.pset.ui.gridsize] # Grid Size parameters
            else: # None or MP2
                self.pset.dft.dfttyp = 'NONE'
                self.pset.dft.nrad = 0
                        
#        self.pset.dft.dfttyp = 'NONE'
#        self.pset.dft.gridsize = 0
#        if mplevl[self.ecm_btngrp.selectedId()] == 'DFT':
#            self.pset.dft.dfttyp = dfttyp[self.dfttyp_combox.currentItem()] # DFTTYP
#            self.pset.dft.gridsize = gridsize[self.gridsize_combox.currentItem()] # GRIDSIZE
        
        # $GUESS Section ###########################################
        
        # $STATPT Section ###########################################
        
        # $BASIS Section ###########################################
        
        self.pset.basis.gbasis = gbasis[self.gbasis_combox.currentItem()] # GBASIS
            
    def writeinpfile(self):
        'Write GAMESS INP file'
        
        # Save UI settings
        self.save_ui_settings()
        
        # Save parms and write to file
#        self.save_parms()
        
        f = open(self.inputfile,'w') # Open GAMESS input file.
        
        # Write Header
        gmsver = get_gamess_info(self.gmsver)
        f.write ('!\n! ' + gmsver + ' INP file created by nanoENGINEER-1 on ')
        timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
        f.write(timestr)
        
        self.pset.prin1(f) # Write GAMESS parameters.

        self.write_atoms_data(f) # Write DATA section with molecule data.
        
        f.close() # Close INP file.
        
        self.close() # Close GAMESS dialog.
        
        open_file_in_editor(self.inputfile) # Show GAMESS input file for debugging purposes.

    def write_atoms_data(self, f):
        'Write the atoms list data to the DATA section of the GAMESS INP file'
        
        # $DATA Section keyword
        f.write(" $DATA\n")
        
        # Comment (Title) line from UI
        f.write(str(self.comment_linedit.text()) + "\n")
        
        # Schoenflies symbol
        f.write("C1\n")
        
        # Write the list of jig atoms for the $DATA group
        self.writealistdata(f)

        #  $END
        f.write(' $END\n')

    def writealistdata(self, f):
        '''Write the list of atoms in $DATA format to a file'''
        
        from jigs import povpoint
        for a in self.gamess.atoms:
            pos = a.posn()
            fpos = (float(pos[0]), float(pos[1]), float(pos[2]))
            f.write("%2s" % a.element.symbol)
            f.write("%8.1f" % a.element.eltnum)
            f.write("%8.3f%8.3f%8.3f\n" % fpos)

    def open_atoms_list_in_editor(self):
        'Open Atoms List in text editor'

        # Don't forget to write this file to the project's temp directory.
        # projtmpdir = ...
        # os.path.join (projtmpdir, self.atomsfile)
        f = open(self.atomsfile, 'w') # This only occurs when the user selects "Atom List.." in UI.
        self.writealistdata(f)
        f.close()
        
        open_file_in_editor(self.atomsfile)
                    
    def writewgmsbatfile(self):
        '''Write a WinGAMESS (not PC GAMESS) BAT file for Windows'''
        
        # Example job file for a WinGAMESS BAT for Windows
        #
        # @echo off
        # echo Gamess runs on DELL8600 using 1 CPU
        # echo Running GamessJig.inp ...
        # del C:\WinGAMESS\temp\*.*
        # cd C:\WinGAMESS\
        # copy GamessJig.inp C:\WinGAMESS\scratch\GamessJig.F05
        # csh -f runscript.csh GamessJig 04 1 C:\WinGAMESS DELL8600 5/25/2005 4:11:17 AM > GamessJig.out
        # echo Job GamessJig.inp finished.
        # @echo off
        # echo All jobs processed
        
        self.gmsbatfile = os.path.join(self.gmsdir, 'rungms.bat')
        wgmstemp = os.path.join(self.gmsdir, 'temp', self.jigname)
        wgmsscratch = os.path.join(self.gmsdir, 'scratch')
        wgmsinpfile = os.path.join(wgmstemp, self.inputfile)
        
        if os.path.exists(self.gmsbatfile): # Remove any previous BAT file.
            os.remove(self.gmsbatfile)
        
        if os.path.exists(wgmsinpfile): # Remove any previous INP file.
            os.remove(wgmsinpfile)
            
        f = open(self.gmsbatfile,'w') # Open GAMESS input file.
        
        f.write('@echo off\n')
        f.write('echo WinGAMESS started using 1 CPU\n')
        f.write('del ' + self.gmstempfile + '.*')
        f.write('cd ' + self.gmsdir + '\n')
        f.write('csh -f runscript.csh GamessJig 04 1 C:\\WinGAMESS DELL8600 5/25/2005 4:11:17 AM > GamessJig.out')
        f.write('echo WinGAMESS finished.')
        f.write('@echo off')
        f.write('echo All jobs processed')
        
        f.close()

    def run_pcgamess(self):
        '''Run PC GAMESS (Windows or Linux only).
        PC GAMESS creates 2 output files:
          - the DAT file, called "PUNCH", is written to the directory from which
            PC GAMESS is started.  This is why we chdir to the gamess temp directory
            before we run PC GAMESS.
          - the OUT file (aka the log file), which we name jigname.out.
        '''
        # Make sure the PC GAMESS executable exists
        if not os.path.exists(self.gmspath):
            msg = "PC GAMESS executable does not exist: " + self.gmspath
            print msg
            return

        oldir = os.getcwd() # Save current directory
        print "run_pcgamess: Current dir = ",oldir
        print "run_pcgamess: Changing to directory ", self.gmstmpdir
        os.chdir(self.gmstmpdir) # Change directory to the GAMESS temp directory.

        self.writeinpfile() # Write INP file with current parms.
            
        gmscmd = self.gmspath + " -i " + self.inputfile + " -o " + self.outputfile
        print "run_pcgamess: PC GAMESS Command: ",gmscmd
            
        if os.path.exists(self.datfile): # Remove any previous DAT (PUNCH) file.
            print "run_pcgamess: Removing DAT file: ", self.datfile
            os.remove(self.datfile)
            
        os.system(gmscmd) # Run, baby, run!
            
        outfile = os.path.join(self.gmstmpdir, self.outputfile)
        msg = "PC GAMESS launched. Results located in " + outfile
        self.gamess.assy.w.history.message(msg)
            
        os.chdir(oldir)
        print "run_pcgamess: Launched PC GAMESS. Changed back to previous dir = ",oldir
                            
    def run_gamess(self):
        '''Run GAMESS (Linux or Mac OS X) or WinGAMESS (Windows).
        '''
        # Make sure the GAMESS executable exists
        if not os.path.exists(self.gmspath):
            msg = "GAMESS executable does not exist: " + self.gmspath
            print msg
            return
            
        # GAMESS for Linux or Mac OS X
        if sys.platform != 'win32':
                
            self.gmspath = os.path.join(self.gmsdir, "rungms") # GAMESS Executable
                
            gmscmd = self.gmspath + " " + self.inputfile + " 1 > " + self.outputfile
            print "Linux/MacOS GAMESS Command: ",gmscmd
                
            os.system(gmscmd)
            
        # WinGAMESS
        # NOT CURRENTLY SUPPORTED. Mark 050525
        else:
            self.writegmsbatfile()
                
            gmscmd = self.gmsbatfile
            print "WinGAMESS not supported yet.  If it was supported, it would generate this command:"
            print "WinGAMESS Command: ",gmscmd
        
# Everything below has not been implemented.  Mark 052505
        
# from GamessHostProp import *

class gamessHost:
    '''a gamessHost has all the attributes needed to connect to a GAMESS server'''

    # create a blank GamessHost with the given list of atoms
    def __init__(self, hostinfo):
        self.hostname = hostinfo[0] # Hostname of server
        self.ip = hostinfo[1] # IP Address of server
        self.sw_version = hostinfo[2] # GAMESS software version
        self.cntl = GamessHostProp()
        self.cntl.exec_loop()

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()