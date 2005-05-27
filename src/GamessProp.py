# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
runGamess.py

$Id$
'''
__author__ = "Mark"

contrl={'runtyp':'ENERGY', 'coord':'UNIQUE', 'scftyp':'RHF', 'icharg':0, 'mult':1, 'mplevl':0, 'maxit':200,
        'icut':11, 'inttyp':'HONDO', 'qmttol':'1.0E-6', 'dfttyp':0, 'nprint':9}
        
scftyp=['RHF', 'UHF', 'ROHF']
nprint=-5,-2,7,8,9

scf={'conv':8, 'nconv':8, 'extrap':'.T.','dirscf':'.T.', 'damp':'.F.', 'shift':'.F.', 'diis':'.T.',
     'soscf':'.F.','rstrct':'.F.'}
     
conv='10E-04','10E-05','10E-06','10E-07'
     
tf='.F.', '.T.'

system={'timlim':1000, 'memory':70000000}
mp2={'ncore':0}

DFT=1
MP2=2

dft={'dfttyp':'NONE', 'gridsize':0}
dfttyp='SLATER','BECKE','GILL','PBE','SVWN','SLYP', 'SOP', 'BVWN', \
    'BLYP', 'BOP', 'GVWN', 'GLYP', 'GOP', 'PBEVWN', 'PBELYP', \
    'PBEOP', 'HVWN', 'HLYP', 'HOP', 'BHHLYP', 'B3LYP'
gridsize='NRAD=48 NTHE=12 NPHI=24 SWITCH=1.0E-03', \
    'NRAD=96 NTHE=12 NPHI=24 SWITCH=3.0E-04', \
    'NRAD=96 NTHE=24 NPHI=48 SWITCH=3.0E-04', \
    'NRAD=96 NTHE=36 NPHI=72 SWITCH=3.0E-04'

guess={'guess':'HUCKEL'}
    
#statpt={'nstep':100, 'opttol':0.00005}
statpt={'hess':'GUESS'}

force={'vibanl':'.T.', 'vibsiz':0.01, 'prtifc':'.F.', 'method':'SEMINUM',}

#basis={'gbasis':'N311', 'ngauss':6, 'ndfunc':2, 'npfunc':2, 'diffsp':'.T.',}
basis={'gbasis':'AM1'}
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

GAMESS = 1 # GAMESS-US
PCGAMESS = 2 # PC GAMESS

from qt import *
from GamessPropDialog import *
import sys, os, time
from constants import *

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
        self.datfile = 'PUNCH' # PC-GAMESS ONLY - will need to change this based on GAMESS version.
        self.atomsfile = '' # Atoms List file containing $DATA info
        self.gmsbatfile = '' # The WinGAMESS batch filename.  Not implemented.
        #self.pset = gamessParms('Parameter Set 1') # The default parameter set object
        #self.psets.append(self.pset)
#        self.psets.append(gamessParms('Parameter Set 1'))
#        self.pset = self.gamess.psets[0]

        # THESE FIRST 4 VARIABLES SHOULD BE GLOBAL
        # AND CHANGABLE FROM THE USER PREFS AREA.
        self.gmsver = PCGAMESS # Set this to GAMESS or PCGAMESS
        self.gmsdir = 'C:/PCGAMESS' # Full path to GAMESS directory
        self.gmspath = os.path.join(self.gmsdir, 'gamess.exe')  # Full path to GAMESS executable
        wd = globalParms['WorkingDirectory']
        
        self.gmstmpdir  = os.path.join(wd,'gamess')
        if os.path.exists(self.gmstmpdir):
            print "Gamess tmpdir exists:", self.gmstmpdir
        else:
            os.mkdir(self.gmstmpdir)
            print "Created Gamess tmpdir:", self.gmstmpdir
        
        if self.setup(0): return
        self.exec_loop()

    def setup(self, pnum):
        ''' Setup widgets to default (or default) values. Return true on error (not yet possible).
        This is not implemented yet.
        '''
        
        gamess = self.gamess
        self.pset = self.gamess.pset_number(pnum)
        
        # Init the top widgets (name, psets drop box, comment)
        self.name_linedit.setText(self.name)
        self.load_psets_combox()
#        self.psets_combox.setCurrentItem(pnum)
        self.update_comment()
        
        # Init the Electronic Structure Props and Basis Set section.
        self.scftyp_btngrp.setButton(scftyp.index(self.pset.contrl.scftyp))
        self.icharg_spinbox.setValue(int(self.pset.contrl.icharg))
        self.multi_combox.setCurrentItem(int(self.pset.contrl.mult) - 1)

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
            self.pset = self.gamess.add_pset()
            self.setup(val)
            self.psets_combox.setCurrentItem(0)
        else: # Change to an existing pset.
            self.pset = self.gamess.pset_number(val)
            self.setup(val)
            self.psets_combox.setCurrentItem(val)
        
        
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
        
    def update_filenames(self):
        self.inputfile = self.name + '.inp'
        self.outputfile = self.name + '.out'
        self.atomsfile = self.name + '.xyz'
        self.gmsbatfile = ''
        
    def update_comment(self):
        timestr = "%s" % time.strftime("%Y-%m-%d %H:%M:%S")
        comment = 'Jig = "' + self.name + '" Parms Set = "' + self.pset.name + '" ' + timestr
        self.comment_linedit.setText(QString(comment))
        
#    def set_host_combox(self):
#        'Add default option to GAMESS Server Host and Version combo box'
#        if sys.platform == 'win32':
#            hoststr = 'localhost (PC GAMESS)'
#        else:
#            hoststr = 'localhost (GAMESS)'
#            
#        self.host_combox.clear() # Clear all combo box items
#        self.host_combox.insertItem(hoststr) # Add the default item.
            
    def set_mplevel(self, val):
        '''Enable/disable widgets when user changes Electron Correlation Method.
        '''
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
        if val != 0 and scftyp[self.scftyp_btngrp.selectedId()] == 'RHF':
            
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

    def save_parms(self):
        
        # $CONTRL Section ###########################################
        
        self.pset.contrl.scftyp = scftyp[self.scftyp_btngrp.selectedId()] # SCFTYP
        self.pset.contrl.icharg = str(self.icharg_spinbox.value()) # ICHARG
        self.pset.contrl.mult = str(self.multi_combox.currentText()) #MULT
        
        # MPLEVL
        mplvl = self.mplvl_btngrp.selectedId()
        if mplvl == MP2:
            self.pset.contrl.mplevl = '2'
        else:
            self.pset.contrl.mplevl = '0'
            
        # INTTYP
        if mplvl == MP2:
            self.pset.contrl.inttyp = 'HONDO'
        elif mplvl == DFT:
            self.pset.contrl.inttyp = 'POPLE'
        else: # None.  Not sure in INNTYP keyword should be included when None.  Ask Damian.  Mark 052105.
            self.pset.contrl.inttyp = 'POPLE' # or None?
        
        # ICUT and QMTTOL
        s = str(self.gbasis_combox.currentText())
        m = s.count('+') # If there is a plus sign in the basis set name, we have "diffuse orbitals"
        if m: # We have diffuse orbitals
            self.pset.contrl.icut = 11
            if sys.platform != 'win32': # PC-GAMESS does not support QMTTOL. Mark 052105
                self.pset.contrl.qmttol = '3.0E-6'
            else:
                self.pset.contrl.qmttol = None
        else:  # No diffuse orbitals
            self.pset.contrl.icut = 9
            if self.gmsver == GAMESS: 
                self.pset.contrl.qmttol = '1.0E-6'
            else:
                self.pset.contrl.qmttol = None # PC GAMESS does not support QMTTOL. Mark 052105
        
        # DFTTYP (Windows with PC GAMESS only)
        # The DFT section record is not supported for PC GAMESS.  Instead, the DFTTYP keyword 
        # is included in the CONTRL section.  Right now, I'm only testing if the platform is Windows and
        # assuming PC GAMESS is installed.  This will need to be fixed as there is another Windows
        # version of GAMESS (called the "American" version; PC GAMESS is the "Russian" version)
        # that does support the DFT section record.  I suggest we add a user pref to determine what
        # version of GAMESS is used and then test for that.  Mark 052105.
        if self.gmsver == PCGAMESS:
            self.pset.contrl.dfttyp = 0 # No DFTTYP keyword will be written.
            if mplvl == DFT:
                self.pset.contrl.dfttyp = dfttyp[self.dfttyp_combox.currentItem()] # DFTTYP
        
        # $SCF Section ###########################################
        
        self.pset.scf.extrap = tf[self.extrap_checkbox.isChecked()] # EXTRAP
        self.pset.scf.dirscf = tf[self.dirscf_checkbox.isChecked()] # DIRSCF
        self.pset.scf.damp = tf[self.damp_checkbox.isChecked()] # DAMP
        self.pset.scf.diis = tf[self.diis_checkbox.isChecked()] # DIIS
        self.pset.scf.shift = tf[self.shift_checkbox.isChecked()] # SHIFT
        self.pset.scf.soscf = tf[self.soscf_checkbox.isChecked()] # SOSCF
        self.pset.scf.rstrct = tf[self.rstrct_checkbox.isChecked()] # RSTRCT
        
        # CONV (GAMESS) or 
        # NCONV (PC GAMESS)
        if self.gmsver == GAMESS:
            self.pset.scf.conv = conv[self.density_conv_combox.currentItem()] # CONV (GAMESS)
            self.pset.scf.nconv = 0 # Turn off NCONV
        else: # PC GAMESS
            self.pset.scf.nconv = conv[self.density_conv_combox.currentItem()] # NCONV (PC GAMESS)
            self.pset.scf.conv = 0 # Turn off CONV
        
        # $SYSTEM Section ###########################################
        
        self.pset.system.timlin = 1000 # Time limit in minutes
        if self.ram_combox.currentItem() == 0:
            self.pset.system.memory = 70000000 # Default
        else:
            self.pset.system.memory = int(self.ram_combox.currentText()) * 1000000
        
        # $MP2 Section ###########################################
        
        self.pset.mp2.ncore = None
        if self.core_electrons_checkbox.isChecked():
            self.pset.mp2.ncore = '0'
        
        # $DFT Section ###########################################
        
        self.pset.dft.dfttyp = 'NONE'
        self.pset.dft.gridsize = 0
        if mplvl == DFT:
            self.pset.dft.dfttyp = dfttyp[self.dfttyp_combox.currentItem()] # DFTTYP
            self.pset.dft.gridsize = gridsize[self.gridsize_combox.currentItem()] # GRIDSIZE
        
        # $GUESS Section ###########################################
        
        # $STATPT Section ###########################################
        
        # $BASIS Section ###########################################
        
        self.pset.basis.gbasis = gbasis[self.gbasis_combox.currentItem()] # GBASIS
            
    def writeinpfile(self):
        'Write GAMESS input file'
        
        # Save parms and write to file
        self.save_parms()
        
        f = open(self.inputfile,'w') # Open GAMESS input file.
        
        # Write Header
        f.write ('!\n! GAMESS Input File Generated by nanoENGINEER-1 on ')
        timestr = "%s\n!\n" % time.strftime("%Y-%m-%d at %H:%M:%S")
        f.write(timestr)
        
        self.pset.prin1(f) # Write GAMESS parameters.

        self.write_atoms_data(f) # Write DATA section with molecule data.
        
        f.close() # Close INP file.
        
        self.close() # Close GAMESS dialog.
        
        open_file_in_editor(self.inputfile) # Show GAMESS input file for debugging purposes.

    def write_atoms_data(self, f):
        'Write the atoms list data to the DATA section of the GAMESS input file'
        
        # $DATA Section keyword
        f.write(" $DATA\n")
        
        # Comment (Title) line from UI
        f.write(str(self.comment_linedit.text()) + "\n")
        
        # Schoenflies symbol
        f.write("C1\n")
        
        # Write the list of atoms in the $DATA group
        self.writealistdata(f)

        #  $END
        f.write(' $END')

    def writealistdata(self, f=None):
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

        # Don't forget to create this file in the project's temp directory.
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
                
    def run_gamess(self):
        
        # Make sure the GAMESS executable exists
        if not os.path.exists(self.gmspath):
            msg = "GAMESS executable does not exist: " + self.gmspath
            print msg
            return
        
        # GAMESS (Linux or Mac OS X) or WinGAMESS (Windows)
        if self.gmsver == GAMESS:
            
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
        
        # PC GAMESS
        #
        # PC GAMESS creates 2 output files:
        #  - the DAT file, called "PUNCH", it written to the directory from which
        #    GAMESS is started.
        #  - the OUT file, which we name jigname.out, it written to the directory
        #    we specify in the full path in self.outputfile.
        # 
        else: 
        
            oldir = os.getcwd() # Save current directory
            print "Rungms: Old Dir = ",oldir
            print "Rungms: Changing to directory ", self.gmstmpdir
            os.chdir(self.gmstmpdir) # Change directory to the GAMESS temp directory.

            self.writeinpfile() # Write INP file with current parms, then we run GAMESS.
            
            gmscmd = self.gmspath + " -i " + self.inputfile + " -o " + self.outputfile
            print "PC GAMESS Command: ",gmscmd
            
            if os.path.exists(self.datfile): # Remove any previous DAT file.
                print "Removing DAT file: ", self.datfile
                os.remove(self.datfile)
            
            os.system(gmscmd) # Run, baby, run!
            
            outfile = os.path.join(self.gmstmpdir, self.outputfile)
            msg = "GAMESS Launched. Results located in " + outfile
            self.gamess.assy.w.history.message(msg)
            
            os.chdir(oldir)
            print "Rungms: Launched GAMESS. Changed back to old Dir = ",oldir
        
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