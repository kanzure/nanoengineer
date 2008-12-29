# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
jig_Gamess.py

@author: Mark
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""

import sys

from model.jigs import Jig
from graphics.drawing.drawers import drawwirecube
from graphics.rendering.povray.povheader import povpoint # Fix for bug 692 Mark 050628
from analysis.GAMESS.files_gms import get_energy_from_gms_outfile, get_atompos_from_gms_outfile
from utilities.Log import redmsg, greenmsg
import foundation.env as env
from utilities.Log import redmsg
from model.chem import move_alist_and_snuggle
import foundation.state_utils as state_utils
from utilities.debug import print_compact_traceback

from analysis.GAMESS.GamessJob import GamessJob
from analysis.GAMESS.GamessProp import scftyp
from analysis.GAMESS.GamessProp import ecm
from analysis.GAMESS.GamessProp import pcgms_dfttyp_items
from analysis.GAMESS.GamessProp import gms_dfttyp_items
from analysis.GAMESS.GamessProp import runtyp
from analysis.GAMESS.GamessProp import mplevl
from analysis.GAMESS.GamessProp import inttyp
from analysis.GAMESS.GamessProp import pcgms_gridsize
from analysis.GAMESS.GamessProp import tf
from analysis.GAMESS.GamessProp import conv
from analysis.GAMESS.GamessProp import ncore
from analysis.GAMESS.GamessProp import gms_gridsize
from analysis.GAMESS.GamessProp import opttol
from analysis.GAMESS.GamessProp import gbasis
from analysis.GAMESS.GamessProp import contrl
from analysis.GAMESS.GamessProp import scf
from analysis.GAMESS.GamessProp import system
from analysis.GAMESS.GamessProp import mp2
from analysis.GAMESS.GamessProp import dft
from analysis.GAMESS.GamessProp import guess
from analysis.GAMESS.GamessProp import statpt
from analysis.GAMESS.GamessProp import basis
from analysis.GAMESS.GamessProp import ui

from utilities import debug_flags

from utilities.constants import magenta

from files.mmp.files_mmp_registration import MMP_RecordParser
from files.mmp.files_mmp_registration import register_MMP_RecordParser

from files.mmp.files_mmp import mmp_interp_just_for_decode_methods # for a kluge

# == GAMESS

class Gamess(Jig):
    """
    A Gamess jig has a list of atoms with one or more parameter sets used to run a GAMESS calcuation.
    """
    sym = "GAMESS"
    icon_names = ["modeltree/gamess.png", "modeltree/gamess-hide.png"]
    featurename = "GAMESS Jig" #bruce 051203

    #bruce 050704 added these attrs and related methods, to make copying of this jig work properly
    mutable_attrs = ('pset',)
    copyable_attrs = Jig.copyable_attrs + () + mutable_attrs
    
    # Default job parameters for a GAMESS job.
    job_parms = {
        'Engine':'GAMESS',
        'Calculation':'',
        'Description':"No comments? How about today's weather?",
        'Status':'',
        'Server_id':'',
        'Job_id':'',
        'Time':'0.0'}

    # create a blank Gamess jig with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        self.cancelled = False
        # set default color of new gamess jig to magenta
        self.color = magenta # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = magenta # This is the normal (unselected) color.
        #bruce 050913 thinks self.history is no longer needed:
        ## self.history = env.history
        #self.psets = [] # list of parms set objects [as of circa 050704, only the first of these is ever defined (thinks bruce)]
        self.pset = gamessParms('Parameter Set 1')
        self.gmsjob = GamessJob(Gamess.job_parms, jig=self)
        ## bruce 050701 removing this: self.gmsjob.edit()
        self.outputfile = '' # Name of jig's most recent output file. [this attr is intentionally not copied -- bruce 050704]

    def edit(self):
        self.gmsjob.edit()
        
    # it's drawn as a wire cube around each atom.
    def _draw(self, glpane, dispdef):
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "gamess" record to POV-Ray file in the format:
    # gamess(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "gamess(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def _getinfo(self):
        return "[Object: Gamess Jig] [Name: " + str(self.name) + "] [Total Atoms: " + str(len(self.atoms)) + "] [Parameters: " + self.gms_parms_info() + "]"
     
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        attachedAtomCount = "<font color=\"#0000FF\">Total  Atoms: </font>%d"%(len(self.atoms))
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Gamess Jig"\
        + "<br>"  +  "<font color=\"#0000FF\"> Parameters:</font>" + self.gms_parms_info()\
        + "<br>" +  str(attachedAtomCount)

    def getstatistics(self, stats):
        stats.ngamess += 1

    def gms_parms_info(self, delimeter='/'):
        """
        Return a GAMESS parms shorthand string.
        """
        # This is something Damian and I discussed to quickly display the parms set for
        # a Gamess jig. It is used in the header of the GAMESS INP file and in the naming of
        # the new chunk made from a GAMESS optimization.  It is also used to display the
        # parameter info (along with the energy) when doing an energy calculation.
        # Mark 050625.
        
        d = delimeter
        
        pset = self.pset
        
        # SCFTYP (RHF, UHF, or ROHF)
        s1 = scftyp[pset.ui.scftyp]
        
        # Hartree-Fock (display nothing), DFT (display functional) or MP2
        if ecm[pset.ui.ecm] == 'DFT':
            if sys.platform == 'win32': # Windows - PC GAMESS
                item = pcgms_dfttyp_items[pset.ui.dfttyp]
            else: # Linux or MacOS - GAMESS
                item = gms_dfttyp_items[pset.ui.dfttyp]
            
            s2, junk = item.split(' ',1)
            s2 = d + s2
        elif ecm[pset.ui.ecm] == 'MP2':
            s2 = d + 'MP2'
        else:
            s2 = ''
        
        # Basis Set    
        s3 = d + pset.ui.gbasisname
        
        # Charge
        s4 = d + 'Ch' + str(pset.ui.icharg)
        
        # Multiplicity
        s5 = d + 'M' + str(pset.ui.mult + 1)

        return s1 + s2 + s3 + s4 + s5
                        
    def __CM_Calculate_Energy(self):
        """
        Gamess Jig context menu "Calculate Energy"
        """
        self.calculate_energy()
        
    def calculate_energy(self):
        """
        Calculate energy.
        """
        
        cmd = greenmsg("Calculate Energy: ")
        
        errmsgs = ["GAMESS job aborted.",
                            "Error: GAMESS job failed."]
                            
        pset = self.pset
        runtyp = pset.ui.runtyp # Save runtyp (Calculate) setting to restore it later.
        pset.ui.runtyp = 0 # Energy calculation
        origCalType = self.gmsjob.Calculation
        self.gmsjob.Calculation = 'Energy'
        
        self.update_gamess_parms()
        
        # Run GAMESS job.  Return value r:
        # 0 = success
        # 1 = job aborted
        # 2 = job failed.
        r = self.gmsjob.launch()
        
        pset.ui.runtyp = runtyp # Restore to original value
        self.gmsjob.Calculation = origCalType
        
        if r: # Job was aborted or an error occurred.
            msg = redmsg(errmsgs[r-1])
            env.history.message( cmd + msg )
            return
            
        self.print_energy()
            
    def __CM_Optimize_Geometry(self):
        """
        Gamess Jig context menu "Optimize Geometry"
        """
        self.optimize_geometry()
        
    def optimize_geometry(self):
        """
        Optimize geometry
        """
        
        cmd = greenmsg("Optimize Geometry: ")
        
        errmsgs = ["GAMESS job aborted.",
                            "Error: GAMESS job failed."]
                            
        pset = self.pset
        runtyp = pset.ui.runtyp # Save runtyp (Calculate) setting to restore it later.
        pset.ui.runtyp = 1 # Optimize
        origCalType = self.gmsjob.Calculation
        self.gmsjob.Calculation = 'Optimize'
        
        self.update_gamess_parms()
        
        # Run GAMESS job.  Return value r:
        # 0 = success
        # 1 = job aborted.
        # 2 = job failed.
        r = self.gmsjob.launch()
        
        pset.ui.runtyp = runtyp # Restore to original value
        self.gmsjob.Calculation = origCalType
        
        if r: # Job was aborted or an error occurred.
            msg = redmsg(errmsgs[r-1])
            env.history.message( cmd + msg )
            return
        
        try:
            r2 = self.move_optimized_atoms()
        except:
            print_compact_traceback( "GamessProp.run_job(): error reading GAMESS OUT file [%s]: " % \
                    self.outputfile )
            env.history.message( redmsg( cmd + "Internal error while inserting GAMESS geometry: " + self.outputfile) )
        else:
            if r2:
                env.history.message(cmd + redmsg( "Atoms not adjusted."))
            else:
                self.assy.changed() # The file and the part are not the same.
                self.print_energy() # Print the final energy from the optimize OUT file, too.
                env.history.message( cmd + "Atoms adjusted.")
    
    def __CM_Optimize_Geometry__options(self):
        if Jig.is_disabled(self):
            return ['disabled']
        else:
            return []
    
    def __CM_Calculate_Energy__options(self):
        if Jig.is_disabled(self):
            return ['disabled']
        else:
            return []
        pass

    def print_energy(self):
        
        r, final_energy_str = get_energy_from_gms_outfile(self.outputfile)

        if r == 1: # GAMESS terminated abnormally.
            if final_energy_str:
                env.history.message(redmsg(final_energy_str + " Check if you have set the right Gamess executable file. Usually it's called gamess.??.x or ??gamess.exe."))
                return
                
            msg = "Final energy value not found. The output file is located at: " + self.outputfile
            env.history.message(redmsg(msg))
        
        elif r == 2: # The output file not exist
            msg = "The output file %s doesn't exist. The reason is either that Gamess didn't run or the output file has been deleted. " % self.outputfile
            env.history.message(redmsg(msg))
            
        else: # Final energy was found.
            gmstr = self.gms_parms_info()
            msg = "GAMESS finished. The output file is located at: " + self.outputfile
            env.history.message(msg)
            msg = "Parameters: " + gmstr + ".  The final energy is: " + final_energy_str + " Hartree."
            env.history.message(msg)

    mmp_record_name = "gamess" #bruce 050701


    def move_optimized_atoms(self):
        
        newPositions = get_atompos_from_gms_outfile( self.assy, self.outputfile, self.atoms )
        # retval is either a list of atom posns or an error message string.
        assert type(newPositions) in [type([]),type("")]
        if type(newPositions) == type([]):
            self.move_atoms(newPositions)
            self.assy.changed()
            self.assy.o.gl_update()
            #self.assy.w.win_update()
            return 0
        else:
            env.history.message(redmsg( newPositions))
            return 1
                
    def move_atoms(self, newPositions): # used when reading xyz files
        """
        [Borrowed from movie.moveAtoms.]
        
        Move a list of atoms to newPosition. After 
        all atoms moving, bond updated, update display once.
        <parameter>newPosition is a list of atom absolute position,
        the list order is the same as self.alist
        """   
        
        atomList = self.atoms
        
        if len(newPositions) != len(atomList):
            #bruce 050225 added some parameters to this error message
            #bruce 050406 comment: but it probably never comes out, since readxyz checks this,
            # so I won't bother to print it to history here. But leaving it in is good for safety.
            print "move_atoms: The number of atoms from GAMESS file (%d) is not matching with that of the current model (%d)" % \
                  (len(newPositions), len(atomList))
            return
        move_alist_and_snuggle(atomList, newPositions)
            #bruce 051221 fix a bug analogous to bug 1239 by letting this new function (containing a loop)
            # replace a copy (which was right here) of the older buggy version of that loop
        self.assy.o.gl_update()
        return
                        
    def writemmp(self, mapping): #bruce 050701
        "[extends Jig method]"
        super = Jig
        super.writemmp(self, mapping) # this writes the main gamess record, and some general info leaf records valid for all nodes
        pset = self.pset
        pset.writemmp(mapping, 0)
            # This writes the pset's info, as a series of "info gamess" records which modify the last gamess jig;
            # in case we ever want to extend this to permit more than one pset per jig in the mmp file,
            # each of those records has a "pset index" which we pass here as 0 (and which is written using "%s").
            # So if we wanted to write more psets we could say self.psets[i].writemmp(mapping, i) for each one.
        return

    def readmmp_info_gamess_setitem( self, key, val, interp ): #bruce 050701
        """
        This is called when reading an mmp file, for each "info gamess" record
        which occurs right after this node is read and no other (gamess jig) node has been read.
           Key is a list of words, val a string; the entire record format
        is presently [050701] "info gamess <key> = <val>", and there are exactly
        two words in <key>, the "parameter set index" (presently always 0) and the "param name".
           Interp is an object to help us translate references in <val>
        into other objects read from the same mmp file or referred to by it.
        See the calls of this or similar methods from files_mmp for the doc of interp methods.
           If key is recognized, this method should set the attribute or property
        it refers to to val; otherwise it must do nothing.
           (An unrecognized key, even if longer than any recognized key,
        is not an error. Someday it would be ok to warn about an mmp file
        containing unrecognized info records or keys, but not too verbosely
        (at most once per file per type of info).)
        """
        if len(key) != 2 or not key[0].isdigit():
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info gamess with unrecognized key %r (not an error)" % (key,)
            return
        pset_index, name = key
        pset_index = int(pset_index)
            # pset_index is presently always 0, but this code should work provided self.psets has an element with this index;
        try:
            pset = self.pset
        except:
            # not an error -- future mmp formats might use non-existent indices and expect readers to create new psets.
            if debug_flags.atom_debug:
                print "atom_debug: fyi: info gamess with non-existent pset index in key %r (not an error)" % (key,)
            return
        # the rest of the work should be done by the pset.
        try:
            self.pset.info_gamess_setitem( name, val, interp )
            
        except:
            print_compact_traceback("bug: exception (ignored) in pset.info_gamess_setitem( %r, %r, interp ): " % (name,val) )
            return
        pass
    
    def own_mutable_copyable_attrs(self): #bruce 050704
        """
        [overrides Node method]
        """
        super = Jig
        super.own_mutable_copyable_attrs( self)
        for attr in self.mutable_attrs:
            if attr == 'pset':
                # special-case code for this attr, a list of gamessParms objects
                # (those objects, and the list itself, are mutable and need to be de-shared)
                val = getattr(self, attr)
                #assert type(val) == type([])
                newval = val.deepcopy()#for item in val]
                setattr(self, attr, newval)
            else:
                print "bug: don't know how to copy attr %r in %r", attr, self
            pass
        return

    def cm_duplicate(self): #bruce 050704.
        """
        Make a sibling node in the MT which has the same atoms, and a copy of the params, of this jig.
        """
            #e Warning: The API (used by modelTree to decide whether to offer this command) is wrong,
            # and the implem should be generalized (to work on any Node or Group). Specifically,
            # this should become a Node method which always works (whether or not it's advisable to use it);
            # then the MT cmenu should dim it if some other method (which might depend on more than just the class)
            # says it's not advisable to use it.
            #    I think it's advisable only on a Gamess jig, and on a chunk,
            # and maybe on a Group -- but what to do about contained jigs in a Group for which
            # some but not all atoms are being duplicated, or even other jigs in the Group, is a
            # design question, and it might turn out to be too ambiguous to safely offer it at all
            # for a Group with jigs in it.
        # Some code taken from Jig.copy_full_in_mapping and Jig._copy_fixup_at_end.
        copy = self.__class__( self.assy, self.atoms[:] )
        orig = self
        orig.copy_copyable_attrs_to(copy) # replaces .name set by __init__
        copy.name = copy.name + "-copy" #e could improve
        copy.own_mutable_copyable_attrs() # eliminate unwanted sharing of mutable copyable_attrs
        if orig.picked:
            self.color = self.normcolor
        orig.addsibling(copy)
        if copy.part is None: #bruce 050707 see if this is enough to fix bug 755
            self.assy.update_parts()
        env.history.message( "Made duplicate Gamess jig on same atoms: [%s]" % copy.name )
            # note: the wire cubes from multiple jigs on the sme atoms get overdrawn,
            # which will mess up the selection coloring of those wirecubes
            # since the order of drawing them is unrelated to which one is selected
            # (and since the OpenGL behavior seems a bit unpredictable anyway).
            ##e Should fix this to only draw one wirecube, of the "maximal color", I guess...
        self.assy.w.win_update() # MT and glpane both might need update
        return
    
    
    #def set_disabled_by_user_choice(self, val):
    #    """Called when users disable/enable the jig"""
    #    self.gmsjob.edit_cntl.run_job_btn.setEnabled(not val)
    #    Jig.set_disabled_by_user_choice(self, val)
    def is_disabled(self):
        """
        Which is called when model tree is updated?
        """
        val = Jig.is_disabled(self)
        self.gmsjob.edit_cntl.run_job_btn.setEnabled(not val)
        return val
   
    def update_gamess_parms(self):
        """
        Update the GAMESS parameter set values using the settings in the UI object.
        """
        # $CONTRL group ###########################################
        
        # Parms Values
        self.pset.contrl.runtyp = runtyp[self.pset.ui.runtyp] # RUNTYP
        self.pset.contrl.scftyp = scftyp[self.pset.ui.scftyp] # SCFTYP
        self.pset.contrl.icharg = str(self.pset.ui.icharg) # ICHARG
        self.pset.contrl.mult = str(self.pset.ui.mult + 1) # MULT
        self.pset.contrl.mplevl = mplevl[self.pset.ui.ecm] # MPLEVL
        self.pset.contrl.inttyp = inttyp[self.pset.ui.ecm] # INTTYP
        self.pset.contrl.maxit = self.pset.ui.iterations # Iterations
        
        # ICUT and QMTTOL
        #s = str(self.gbasis_combox.currentText())
        m = self.pset.ui.gbasisname.count('+') # If there is a plus sign in the basis set name, we have "diffuse orbitals"
        if m: # We have diffuse orbitals
            self.pset.contrl.icut = 11
            if self.gmsjob.server.engine != 'PC GAMESS': # PC GAMESS does not support QMTTOL. Mark 052105
                self.pset.contrl.qmttol = '3.0E-6'
            else:
                self.pset.contrl.qmttol = None
        else:  # No diffuse orbitals
            self.pset.contrl.icut = 9
            if self.gmsjob.server.engine == 'GAMESS': 
                self.pset.contrl.qmttol = '1.0E-6'
            else:
                self.pset.contrl.qmttol = None # PC GAMESS does not support QMTTOL. Mark 052105
        
        # DFTTYP (PC GAMESS only)
        # For PC GAMESS, the DFTTYP keyword is included in the CONTRL section, not the $DFT group.
        if self.gmsjob.server.engine == 'PC GAMESS':
            if ecm[self.pset.ui.ecm] == 'DFT':
                item = pcgms_dfttyp_items[self.pset.ui.dfttyp] # Item's full text, including the '(xxx)'
                self.pset.contrl.dfttyp, junk = item.split(' ',1) # DFTTYPE, removing the '(xxx)'.
                self.pset.dft.nrad = pcgms_gridsize[self.pset.ui.gridsize] # Grid Size parameters
            else: # None or MP2
                self.pset.contrl.dfttyp = 0
                self.pset.dft.nrad = 0
        
        # $SCF group ###########################################
        
        self.pset.scf.extrap = tf[self.pset.ui.extrap] # EXTRAP
        self.pset.scf.dirscf = tf[self.pset.ui.dirscf] # DIRSCF
        self.pset.scf.damp = tf[self.pset.ui.damp] # DAMP
        self.pset.scf.diis = tf[self.pset.ui.diis] # DIIS
        self.pset.scf.shift = tf[self.pset.ui.shift] # SHIFT
        self.pset.scf.soscf = tf[self.pset.ui.soscf] # SOSCF
        self.pset.scf.rstrct = tf[self.pset.ui.rstrct] # RSTRCT
        
        # CONV (GAMESS) or 
        # NCONV (PC GAMESS)
        if self.gmsjob.server.engine == 'GAMESS':
            self.pset.scf.conv = conv[self.pset.ui.conv] # CONV (GAMESS)
            self.pset.scf.nconv = 0 # Turn off NCONV
        else: # PC GAMESS
            self.pset.scf.nconv = conv[self.pset.ui.conv] # NCONV (PC GAMESS)
            self.pset.scf.conv = 0 # Turn off CONV
        
        # $SYSTEM group ###########################################
        
        self.pset.system.timlin = 1000 # Time limit in minutes
        self.pset.system.memory = self.pset.ui.memory * 1000000
        
        # $MP2 group ###########################################
        
        self.pset.mp2.ncore = ncore[self.pset.ui.ncore]
        
        # $DFT group ###########################################

        # The DFT section record is supported in GAMESS only.
        if self.gmsjob.server.engine == 'GAMESS':
            if ecm[self.pset.ui.ecm] == 'DFT':
                item = gms_dfttyp_items[self.pset.ui.dfttyp]
                self.pset.dft.dfttyp, junk = item.split(' ',1) # DFTTYP in $CONTRL
                self.pset.dft.nrad = gms_gridsize[self.pset.ui.gridsize] # Grid Size parameters
            else: # None or MP2
                self.pset.dft.dfttyp = 'NONE'
                self.pset.dft.nrad = 0
        
        # $GUESS group ###########################################
        
        # $STATPT group ###########################################
        
        if runtyp[self.pset.ui.runtyp] == 'optimize':
            self.pset.statpt.opttol = float(opttol[self.pset.ui.rmsdconv])
        else:
            self.pset.statpt.opttol = None
        
        # $BASIS group ###########################################
        
        if ecm[self.pset.ui.ecm] == 'None':
            self.pset.basis.gbasis = gbasis[self.pset.ui.gbasis] # GBASIS
        else:
            self.pset.basis.gbasis = gbasis[self.pset.ui.gbasis + 2] # GBASIS
        return
    
    pass # end of class Gamess

# ==

class gamessParms(state_utils.DataMixin): #bruce 060306 added superclass
    def __init__(self, name):
        """
        A GAMESS parameter set contains all the parameters for a Gamess Jig.
        
        The ui ctlRec object is the "master".  From it, all the other ctlRec objects 
        have their parms set/reset, in GamessProp._save_parms(), each time the user
        selects "Save and Run" or "Save".  The reason for this has to do with 
        the fact that there is not a one-to-one relationship between UI settings (in the
        Gamess Jig Properties dialog) and the parameters written to the GAMESS
        input file.  There are all sorts of strange combinations and permutations 
        between the UI settings and what the GAMESS input file parameters end up being.  
        This is also why it is very difficult (but not impossible) to go from a raw GAMESS 
        input file to the proper UI settings in the Gamess Jig Properties dialog.
        
        Many parameters have a value for the ui object and another value in one of 
        the other ctlRec objects.  The ui object is used to setup the UI and 
        read/write parms to/from the MMP file. The values for the other
        ctlRec objects are set (and only important) when writing the GAMESS input file.
        """
        self.name = name or "" # Parms set name, assumed to be a string by some code
        self.ui = ctlRec('UI', ui) # "Master" ui object.
        self.contrl = ctlRec('CONTRL',contrl) # $CONTRL group object
        self.scf = ctlRec('SCF',scf) # $SCF group object
        self.system = ctlRec('SYSTEM',system) # $SYSTEM group object
        self.mp2 = ctlRec('MP2',mp2) # $MP2 group object
        self.dft = ctlRec('DFT',dft) # $DFT group object
        self.guess = ctlRec('GUESS',guess) # $GUESS group object
        self.statpt = ctlRec('STATPT',statpt) # $STATPT group object
        self.basis = ctlRec('BASIS',basis) # $BASIS group object

    def prin1(self, f=None):
        """
        Write all parms to input file
        """
        self.contrl.prin1(f)
        self.scf.prin1(f)
        self.system.prin1(f)
        self.mp2.prin1(f)
        self.dft.prin1(f)
        self.guess.prin1(f)
        self.statpt.prin1(f)
#        self.force.prin1()
        self.basis.prin1(f)

    def param_names_and_valstrings(self, canonical = False): #bruce 050701; extended by Mark 050704 to return the proper set of params
        """
        Return a list of pairs of (<param name>, <param value printable by %s>) for all
        gamess params we want to write to an mmp file from this set, sorted by <param name>.

        These names and value-strings need to be recognized and decoded by the
        info_gamess_setitem method of this class, and they need to strictly follow certain rules
        documented in comments in the self.writemmp() method.
        """
        # Note: If we implement a "duplicate" context menu command for gamess jigs,
        # it should work by generating this same set of items, and feeding them to that
        # same info_gamess_setitem method (or an appropriate subroutine it calls)
        # of the new jig being made as a copy.
        # [Since that was written, we did it differently (see cm_duplicate); we should
        # review someday whether this advice is obsolete or should have been taken. -- bruce 060307]
        return self.ui.get_mmp_parms(canonical = canonical)

    def deepcopy(self, alter_name = True): #bruce 051003 added alter_name, but I don't know if passing False is ever legal. ###@@@
        #bruce 050704; don't know whether this is complete [needs review by Mark; is it ok it only sets .ui?]
        """
        Make a copy of self (a gamessParms object), which shares no mutable state with self.
        (Used to copy a Gamess Jig containing self.)
        """
        if alter_name:
            newname = self.name + " copy"
            # copy needs a different name #e could improve this -- see the code used to rename chunk copies
        else:
            newname = self.name
        new = self.__class__(newname)
        interp = mmp_interp_just_for_decode_methods() #kluge
        for name, valstring in self.param_names_and_valstrings():
            valstring = "%s" % (valstring,)
            valstring = valstring.strip()
            # we're too lazy to also check whether valstring is multiline or too long, like writemmp does;
            # result of this is only that some bugs will show up in writemmp but not in deepcopy (used to copy this kind of jig).
            new.info_gamess_setitem( name, valstring, interp, error_if_name_not_known = True )
        return new

    # override abstract method of DataMixin
    def _copyOfObject(self): #bruce 051003, for use by state_utils.copy_val
        return self.deepcopy(alter_name = False) ###k I'm not sure alter_name = False can ever be legal,
            # or (if it can be) whether it's good here. I think Mark or I should review this,
            # and we should not change the code to rely on copy_val alone on this object
            # (i.e. we should not remove the mutable_attr decl for pset and the related code that calls deepcopy directly)
            # until that's reviewed. [bruce 051003]

    # override abstract method of DataMixin
    def __eq__(self, other): #bruce 060306-08 for Undo bug 1616
        # note: defining __eq__ is sufficient, but only because we inherit
        # from DataMixin, which defines __ne__ based on __eq__
        if other.__class__ is not self.__class__:
            return False
        return self.param_names_and_valstrings(canonical = True) == other.param_names_and_valstrings(canonical = True)
            # without canonical = True, self has 0/1 where other has False/True, which caused first try of __eq__ to not fix bug 1616.

    def writemmp(self, mapping, pset_index): #bruce 050701
        mapping.write("# gamess parameter set %s for preceding jig\n" % pset_index)
            # you can write any comment starting "# " into an mmp file (if length < 512).
            # You always have to explicitly write the newline at the end (when using mapping.write).
            # But this is not for comments which need to be read back in and shown in the params dialog!
            # Those need to be string-valued params (and not contain newlines, or encode those if they do).
        items = self.param_names_and_valstrings()
            # Rules for these name/valstring pairs [bruce 050701]: 
            # param names must not contain whitespace.
            # valstrings must not start or end with whitespace, or contain newlines, but they can contain blanks or tabs.
            # (if you need to write comments that might contain newlines, these must be encoded somehow as non-newlines.)
            # it's ok to append comments "# ..." to valstrings, but only if these are noticed and stripped by the parsing methods
            # you also write.
            # entire line must be <512 chars in length (this limit applies to any line in any mmp file).
            # if valstring might be too long, you have to truncate it or split it into more than one valstring.
        for name, valstring in items:
            assert type(name) == type("")
            assert name and (' ' not in name) and len(name.split()) == 1 and name.strip() == name, "illegal param name %r" % name
                # some of these checks are redundant
            valstring = "%s" % (valstring,)
            # the next bit of code is just to work around bugs in valstrings without completely failing to write them.
            valstring = valstring.strip() # the reader does this, so we might as well not fool ourselves and do it now
            if '\n' in valstring:
                print "error: multiline valstring in gamess writemmp. workaround: writing only the first line."
                valstring = valstring.split('\n',1)[0]
                valstring = valstring.strip()
            line = "info gamess %s %s = %s\n" % (pset_index, name, valstring)
            if len(line) > 511:
                msg = "can't write this mmp line (too long for mmp format): " + line
                    #bruce 050913 comment: this restriction might no longer be valid for sim executables as of a few days ago
                print msg
                env.history.message( redmsg( "Error: " + msg) )
                mapping.write("# didn't write too-long valstring for info gamess %s %s = ...\n" % (pset_index, name))
            else:
                mapping.write(line)
        mapping.write("# end of gamess parameter set %s\n" % pset_index)
        return

    boolparms = ('damp', 'diis', 'dirscf', 'extrap', 'ncore', 'rstrct', 'shift', 'soscf' )
        # these MUST MATCH info_gamess_setitem uses of decode_bool [bruce 060307, to help with bug 1616]
    
    def info_gamess_setitem(self, name, val, interp, error_if_name_not_known = False):
        #bruce 050701; extended by Mark 050704 to read and set the actual params; bruce 050704 added error_if_name_not_known
        """
        This must set the parameter in self with the given name
        to the value encoded by the string val
        (read from an mmp file from which this parameter set and its gamess jig is being read).
           If it doesn't recognize name or can't parse val,
        it should do nothing (except possibly print a message if atom_debug is set),
        unless error_if_name_not_known is true, in which case it should print an error message reporting a bug.
           (If it's too tedious to avoid exceptions in parsing val,
        change the caller (which already ignores those exceptions, but always prints a message calling them bugs)
        to classify those exceptions as not being bugs (and to only print a message when atom_debug is set).

        [See also the docstring of Gamess.readmmp_info_gamess_setitem, which calls this.]
        """
        if name == 'comment':       # Description/Comment
            self.ui.comment = val
        elif name == 'conv':            # Density and Energy Convergence (1-4)
            p = interp.decode_int(val)
            if p is not None:
                self.ui.conv = p
        elif name == 'damp':            # DAMP
            p = interp.decode_bool(val) # if you add, remove, or rename decode_bool params here, you must also fix boolparms above
            if p is not None:
                self.ui.damp = p
        elif name == 'dfttyp':          # DFT Functional Type
            p = interp.decode_int(val)
            if p is not None:
                self.ui.dfttyp = p
        elif name == 'diis':            # DIIS
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.diis = p
        elif name == 'dirscf':          # DIRSCF
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.dirscf = p
        elif name == 'ecm':            # emc = None (0), DFT (1) or MP2 (2)
            p = interp.decode_int(val)
            if p is not None:
                self.ui.ecm = p
        elif name == 'extrap':          # EXTRAP
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.extrap = p
        elif name == 'gbasis':            # Basis Set Id
            p = interp.decode_int(val)
            if p is not None:
                self.ui.gbasis = p
        elif name == 'gbasisname':      # Basis Set Name
            self.ui.gbasisname = val
        elif name == 'gridsize':            # Grid Size
            p = interp.decode_int(val)
            if p is not None:
                self.ui.gridsize = p
        elif name == 'icharg':            # Charge
            p = interp.decode_int(val)
            if p is not None:
                self.ui.icharg = p
        elif name == 'iterations':            # Iterations
            p = interp.decode_int(val)
            if p is not None:
                self.ui.iterations = p
        elif name == 'memory':            # System Memory
            p = interp.decode_int(val)
            if p is not None:
                self.ui.memory = p
        elif name == 'mult':            # Multiplicity
            p = interp.decode_int(val)
            if p is not None:
                self.ui.mult = p
        elif name == 'ncore':            # Include core electrons
            p = interp.decode_bool(val)
            if p is not None:
                self.ui.ncore = p
        elif name == 'rmsdconv':            # RMSD convergence (1-4)
            p = interp.decode_int(val)
            if p is not None:
                self.ui.rmsdconv = p
        elif name == 'rstrct':          # RSTRCT
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.rstrct = p
        elif name == 'runtyp':            # RUNTYP = Energy (0), or Optimize (1)
            p = interp.decode_int(val)
            if p is not None:
                self.ui.runtyp = p
        elif name == 'scftyp':            # SCFTYP = RHF (0), UHF (1), or ROHF (2)
            p = interp.decode_int(val)
            if p is not None:
                self.ui.scftyp = p
        elif name == 'shift':          # SHIFT
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.shift = p
        elif name == 'soscf':          # SOSCF
            p = interp.decode_bool(val) 
            if p is not None:
                self.ui.soscf = p
        
        # Unused - keeping them for examples.
        # Mark 050603
        elif name == 'param2':
            self.param2 = val.split() # always legal for strings
        elif name == 'param3':
            p3 = interp.decode_int(val) # use this method for int-valued params
            if p3 is not None:
                self.param3 = p3
            # otherwise it was a val we don't recognize as an int; not an error
            # (since the mmp file format might be extended to permit it),
            # but a debug message was printed if atom_debug is set.
        elif name == 'param4':
            p4 = interp.decode_bool(val) # use this method for boolean-valued params
                # (they can be written as 0, 1, False, True, or in a few other forms)
            if p4 is not None:
                self.param4 = p4
                
        else:
            if error_if_name_not_known:
                #bruce 050704, only correct when this method is used internally to copy an object of this class
                print "error: unrecognized parameter name %r in info_gamess_setitem" % (name,)
            elif debug_flags.atom_debug:
                print "atom_debug: fyi: info gamess with unrecognized parameter name %r (not an error)" % (name,)
            # this is not an error, since old code might read newer mmp files which know about more gamess params;
            # it's better (in general) to ignore those than for this to make it impossible to read the mmp file.
            # If non-debug warnings were added, that might be ok in this case since not many lines per file will trigger them.
        
        return # from info_gamess_setitem

    pass # end of class gamessParms

# ==

_boolparms = {} # used in ctlRec [bruce 060308]
for p in gamessParms.boolparms:
    _boolparms[p] = None
    
class ctlRec:
    def __init__(self, name, parms):
        self.name = name
        self.parms = parms.keys()
        self.parms.sort() # Sort parms.
        
        # WARNING: Bugs will be caused if any of ctlRec's own methods or 
        # instance variables had the same name as any of the parameter ('k') values.

        for k in self.parms:
            self.__dict__[k] = parms[k]

    def prin1(self, f):
        """
        Write parms group to input file
        """
        f.write (" $"  + self.name + ' ')
        col = len(self.name) + 3
        for k in self.parms:
            if not self.__dict__[k]: continue # Do not print null parms.
            phrase = k + '=' + str(self.__dict__[k])
            col += 1 + len(phrase)
            if col > 70: 
                col = len(phrase)
                f.write ('\n')
            f.write (phrase + ' ')
        f.write('$END\n')

    def get_mmp_parms(self, canonical = False): 
        """
        Return a list of pairs (parmname, str(parmvalue)) of all the Gamess jig parms
        (and str() of their values) to be stored in the MMP file, sorted by parm name.

        If option canonical = True, canonicalize the values for comparison
        (i.e. use "False" and "True" rather than "0" and "1", for all booleans).
        WARNING: This option is only reviewed for correctness in the instance of this class
        stored in the .ui attribute of its gamesParms object.
        """
        #bruce 060308 added canonical option, to help fix bug 1616
        #bruce 060307 revised docstring to fit code (added str())
        items = []
        
        for p in self.parms: # note: self.parms is already sorted [bruce 060307 comment]
            val = self.__dict__[p]
            if canonical and p in _boolparms:
                val = not not val
            items.append((p, str(val)))
      
        return items
        
    pass # end of class ctlRec

# ==

class _MMP_RecordParser_for_Gamess( MMP_RecordParser): #bruce 071023
    """
    Read the first line of the MMP record for a Gamess Jig.
    (Subsequent lines are "info records" which are
    read separately and interpreted by methods in the new
    Gamess object created by our read_record method.)
    """
    def read_record(self, card): #bruce 050701
        constructor = Gamess
        jig = self.read_new_jig(card, constructor)
            # note: this includes a call of self.addmember
            # to add the new jig into the model
        # for interpreting "info gamess" records:
        self.set_info_object('gamess', jig)
        return
    pass

def register_MMP_RecordParser_for_Gamess():
    """
    [call this during init, before reading any mmp files]
    """
    register_MMP_RecordParser( 'gamess', _MMP_RecordParser_for_Gamess )
    return

# end
