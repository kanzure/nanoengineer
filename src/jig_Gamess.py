# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
jig_Gamess.py

$Id$
'''
__author__ = "Mark"

from jigs import Jig
from drawer import drawwirecube
from GamessProp import *
from GamessJob import *
from povheader import povpoint # Fix for bug 692 Mark 050628
from SimServer import SimServer
from files_gms import get_energy_from_pcgms_outfile

# == GAMESS

class Gamess(Jig):
    '''A Gamess jig has a list of atoms with one or more parameter sets used to run a GAMESS calcuation.'''

    sym = "Gamess"
    icon_names = ["gamess.png", "gamess-hide.png"]

    #bruce 050704 added these attrs and related methods, to make copying of this jig work properly
    mutable_attrs = ('psets',)
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
        self.color = (0.0, 0.0, 0.0)
        self.normcolor = (0.0, 0.0, 0.0) # set default color of ground to black
        self.history = assy.w.history
        self.psets = [] # list of parms set objects [as of circa 050704, only the first of these is ever defined (thinks bruce)]
        self.psets.append(gamessParms('Parameter Set 1'))
        self.gmsjob = GamessJob(Gamess.job_parms, jig=self)
        ## bruce 050701 removing this: self.gmsjob.edit()
        self.outputfile = '' # Name of jig's most recent output file. [this attr is intentionally not copied -- bruce 050704]

    def edit(self):
        self.gmsjob.edit()
        
    # it's drawn as a wire cube around each atom (default color = black)
    def _draw(self, win, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
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

    def getstatistics(self, stats):
        stats.ngamess += 1

    def gms_parms_info(self, delimeter='/'):
        '''Return a GAMESS parms shorthand string.
        '''
        # This is something Damian and I discussed to quickly display the parms set for
        # a Gamess jig. It is used in the header of the GAMESS INP file and in the naming of
        # the new chunk made from a GAMESS optimization.  It is also used to display the
        # parameter info (along with the energy) when doing an energy calculation.
        # Mark 050625.
        
        d = delimeter
        
        pset = self.psets[0]
        
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
        '''Gamess Jig context menu "Calculate Energy"
        '''
        
        pset = self.psets[0]
        runtyp = pset.contrl.runtyp # Save runtyp (Calculate) setting to restore it later.
        pset.contrl.runtyp = 'energy' # Energy calculation
        
        # Run GAMESS job.  Return value r:
        # 0 = success
        # 1 = job cancelled
        # 2 = job failed.
        r = self.gmsjob.launch()
        
        pset.contrl.runtyp = runtyp # Restore to original value
        
        if r == 0: # Success
            self.print_energy()
        elif r==1: # Job was cancelled
            self.history.message( redmsg( "GAMESS job cancelled."))
        else: # Job failed.
            self.history.message( redmsg( "GAMESS job failed."))
        
    def print_energy(self):
        
        final_energy = get_energy_from_pcgms_outfile(self.outputfile)

        if final_energy != None:
            gmstr = self.gms_parms_info()
            msg = "GAMESS finished. Parameters: " + gmstr + ".  The final energy is: " + str(final_energy) + " Hartree"
        else:
            msg = redmsg("Final energy value not found.")
        self.history.message(msg)
        
        return

    mmp_record_name = "gamess" #bruce 050701

    def writemmp(self, mapping): #bruce 050701
        "[extends Jig method]"
        super = Jig
        super.writemmp(self, mapping) # this writes the main gamess record, and some general info leaf records valid for all nodes
        pset = self.psets[0]
        pset.writemmp(mapping, 0)
            # This writes the pset's info, as a series of "info gamess" records which modify the last gamess jig;
            # in case we ever want to extend this to permit more than one pset per jig in the mmp file,
            # each of those records has a "pset index" which we pass here as 0 (and which is written using "%s").
            # So if we wanted to write more psets we could say self.psets[i].writemmp(mapping, i) for each one.
        return

    def readmmp_info_gamess_setitem( self, key, val, interp ): #bruce 050701
        """This is called when reading an mmp file, for each "info gamess" record
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
            if platform.atom_debug:
                print "atom_debug: fyi: info gamess with unrecognized key %r (not an error)" % (key,)
            return
        pset_index, name = key
        pset_index = int(pset_index)
            # pset_index is presently always 0, but this code should work provided self.psets has an element with this index;
        try:
            pset = self.psets[pset_index]
        except:
            # not an error -- future mmp formats might use non-existent indices and expect readers to create new psets.
            if platform.atom_debug:
                print "atom_debug: fyi: info gamess with non-existent pset index in key %r (not an error)" % (key,)
            return
        # the rest of the work should be done by the pset.
        try:
            pset.info_gamess_setitem( name, val, interp )
            
            # Added by Huaicai 7/7/05 to fix bug 758
            # CONV (GAMESS) or  NCONV (PC GAMESS)
            if self.gmsjob.server.engine == 'GAMESS':
                pset.scf.conv = conv[pset.ui.conv] # CONV (GAMESS)
                pset.scf.nconv = 0 # Turn off NCONV
            else: # PC GAMESS
                pset.scf.nconv = conv[pset.ui.conv] # NCONV (PC GAMESS)
                pset.scf.conv = 0 # Turn off CONV
            
        except:
            print_compact_traceback("bug: exception (ignored) in pset.info_gamess_setitem( %r, %r, interp ): " % (name,val) )
            return
        pass
    
    def own_mutable_copyable_attrs(self): #bruce 050704
        """[overrides Node method]"""
        super = Jig
        super.own_mutable_copyable_attrs( self)
        for attr in self.mutable_attrs:
            if attr == 'psets':
                # special-case code for this attr, a list of gamessParms objects
                # (those objects, and the list itself, are mutable and need to be de-shared)
                val = getattr(self, attr)
                assert type(val) == type([])
                newval = [item.deepcopy() for item in val]
                setattr(self, attr, newval)
            else:
                print "bug: don't know how to copy attr %r in %r", attr, self
            pass
        return

    def cm_duplicate(self): #bruce 050704.
        "Make a sibling node in the MT which has the same atoms, and a copy of the params, of this jig."
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
        self.assy.w.history.message( "Made duplicate Gamess jig on same atoms: [%s]" % copy.name )
            # note: the wire cubes from multiple jigs on the sme atoms get overdrawn,
            # which will mess up the selection coloring of those wirecubes
            # since the order of drawing them is unrelated to which one is selected
            # (and since the OpenGL behavior seems a bit unpredictable anyway).
            ##e Should fix this to only draw one wirecube, of the "maximal color", I guess...
        self.assy.w.win_update() # MT and glpane both might need update
        return
    
    pass # end of class Gamess

class gamessParms:
    def __init__(self, name):
        '''A GAMESS parameter set contains all the parameters for a Gamess Jig.
        '''
        self.name = name or "" # Parms set name, assumed to be a string by some code
        self.ui = ctlRec('UI', ui)
        self.contrl = ctlRec('CONTRL',contrl)
        self.scf = ctlRec('SCF',scf)
        self.system = ctlRec('SYSTEM',system)
        self.mp2 = ctlRec('MP2',mp2)
        self.dft = ctlRec('DFT',dft)
        self.guess = ctlRec('GUESS',guess)
        self.statpt = ctlRec('STATPT',statpt)
        self.basis = ctlRec('BASIS',basis)

    def prin1(self, f=None):
        'Write all parms to input file'
        self.contrl.prin1(f)
        self.scf.prin1(f)
        self.system.prin1(f)
        self.mp2.prin1(f)
        self.dft.prin1(f)
        self.guess.prin1(f)
        self.statpt.prin1(f)
#        self.force.prin1()
        self.basis.prin1(f)

    def param_names_and_valstrings(self): #bruce 050701; extended by Mark 050704 to return the proper set of params
        """Return a list of pairs of (<param name>, <param value printable by %s>) for all
        gamess params we want to write to an mmp file from this set.
           These names and value-strings need to be recognized and decoded by the
        info_gamess_setitem method of this class, and they need to strictly follow certain rules
        documented in comments in the self.writemmp() method.
           Note: If we implement a "duplicate" context menu command for gamess jigs,
        it should work by generating this same set of items, and feeding them to that
        same info_gamess_setitem method (or an appropriate subroutine it calls)
        of the new jig being made as a copy.
        """
        items = []
        items = self.ui.get_mmp_parms()
        return items

    def deepcopy(self): #bruce 050704; don't know whether this is complete [needs review by Mark; is it ok it only sets .ui? #####@@@@@]
        "Make a copy of self (a gamessParms object), which shares no mutable state with self. (Used to copy a Gamess Jig containing self.)"
        newname = self.name + " copy" # copy needs a different name #e could improve this -- see the code used to rename chunk copies
        new = self.__class__(newname)
        from files_mmp import mmp_interp_just_for_decode_methods
        interp = mmp_interp_just_for_decode_methods() #kluge
        for name, valstring in self.param_names_and_valstrings():
            valstring = "%s" % (valstring,)
            valstring = valstring.strip()
            # we're too lazy to also check whether valstring is multiline or too long, like writemmp does;
            # result of this is only that some bugs will show up in writemmp but not in deepcopy (used to copy this kind of jig).
            new.info_gamess_setitem( name, valstring, interp, error_if_name_not_known = True )
        return new

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
                print msg
                history.message( redmsg( "Error: " + msg) )
                mapping.write("# didn't write too-long valstring for info gamess %s %s = ...\n" % (pset_index, name))
            else:
                mapping.write(line)
        mapping.write("# end of gamess parameter set %s\n" % pset_index)
        return

    def info_gamess_setitem(self, name, val, interp, error_if_name_not_known = False):
        #bruce 050701; extended by Mark 050704 to read and set the actual params; bruce 050704 added error_if_name_not_known
        """This must set the parameter in self with the given name
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
            p = interp.decode_bool(val) 
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
            elif platform.atom_debug:
                print "atom_debug: fyi: info gamess with unrecognized parameter name %r (not an error)" % (name,)
            # this is not an error, since old code might read newer mmp files which know about more gamess params;
            # it's better (in general) to ignore those than for this to make it impossible to read the mmp file.
            # If non-debug warnings were added, that might be ok in this case since not many lines per file will trigger them.
        
        return # from info_gamess_setitem

    pass # end of class gamessParms

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
        'Write parms group to input file'
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

    def get_mmp_parms(self):
        '''Return a list of all the Gamess jig parms (and their values) to be stored in the 
        MMP file.
        '''
        items = []
        
        for p in self.parms:
#            print p, self.__dict__[p]
            items.append((p, str(self.__dict__[p])))
      
        return items
        
    pass # end of class ctlRec

# end