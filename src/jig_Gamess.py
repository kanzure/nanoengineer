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
        self.psets = [] # list of parms set objects
        self.psets.append(gamessParms('Parameter Set 1'))
        self.gmsjob = GamessJob(Gamess.job_parms, jig=self)
        self.gmsjob.edit()
        self.outputfile = '' # Name of jig's most recent output file.

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

    def writemmp(self, mapping):
        "[extends Jig method]"
        super = Jig
        super.writemmp(self, mapping) # this writes the main gamess record, and some general info leaf records valid for all nodes
        pset = self.psets[0]
        pset.writemmp(mapping, 0)
            # this writes the pset's info, as a series of "info gamess" records which modify the last gamess jig; (or any jig??)###@@@
            # in case we ever want to extend this to permit more than one pset per jig in the mmp file,
            # each of those records has a "pset index" which we pass here as 0 (and which is written using %s).
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
        except:
            print_compact_traceback("bug: exception (ignored) in pset.info_gamess_setitem( %r, %r, interp ): " % (name,val) )
            return
        pass
    
    pass # end of class Gamess

class gamessParms:
    def __init__(self, name):
        
        self.name = name or "" # Parms set name, assumed to be a string by some code
        self.ui = ctlRec('UI', ui)
        self.contrl = ctlRec('CONTRL',contrl)
        self.scf = ctlRec('SCF',scf)
        self.system = ctlRec('SYSTEM',system)
        self.mp2 = ctlRec('MP2',mp2)
        self.dft = ctlRec('DFT',dft)
        self.guess = ctlRec('GUESS',guess)
        self.statpt = ctlRec('STATPT',statpt)
#        self.force = ctlRec('FORCE',force)
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

    def param_names_and_valstrings(self):
        """Return a list of pairs of (<param name>, <param value printable by %s>) for all
        gamess params we want to write to an mmp file from this set.
           These names and value-strings need to be recognized and decoded by the #####@@@@@ method
        of the jig_Gamess class, and they need to strictly follow certain rules
        documented in comments in the self.writemmp() method.
           Note: If we implement a "duplicate" context menu command for gamess jigs,
        it should work by generating this same set of items, and feeding them to that
        same #####@@@@@ method (or an appropriate subroutine it calls) of the new jig being made as a copy.
        """
        items = []
        items.append(('param1', 'val1'   ))
        items.append(('param2', 'v2a v2b'))
        items.append(('param3', 3        ))
        items.append(('param4', True     ))
        items.append(('param5', (1,2,3)  ))
        items.append(('param6', [1,2,3]  ))
        items.append(('param7', None     ))
            # that code results in these lines in the mmp file:
            ## gamess (Gamess.4) (0, 0, 0) 1 6
            ## # gamess parameter set 0 for preceding jig
            ## info gamess 0 param1 = val1
            ## info gamess 0 param2 = v2a v2b
            ## info gamess 0 param3 = 3
            ## info gamess 0 param4 = True
            ## info gamess 0 param5 = (1, 2, 3)
            ## info gamess 0 param6 = [1, 2, 3]
            ## info gamess 0 param7 = None
            ## # end of gamess parameter set 0
            
            ###@@@ replace the above list of items with the actual names and value-strings to write.
            # it's ok for the valstrings to be non-strings as long as "%s" will format them correctly
            # in a way which your #####@@@@@ method can interpret them.
            # (e.g. ints are ok)
            ###@@@ see comments in self.writemmp() about the rules those must follow.
        return items

    def writemmp(self, mapping, pset_index):
        mapping.write("# gamess parameter set %s for preceding jig\n" % pset_index)
            # you can write any comment starting "# " into an mmp file (if length < 512).
            # You always have to explicitly write the newline at the end (when using mapping.write).
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
            line = "info gamess %s %s = %s\n" % (pset_index, name, valstring)
            if valstring.strip() != valstring or '\n' in valstring or len(line) > 511:
                msg = "illegal valstring, can't write this mmp line: " + line
                print msg
                history.message( redmsg( "Error: " + msg) )
                mapping.write("# didn't write illegal valstring for info gamess %s %s = ...\n" % (pset_index, name))
            else:
                mapping.write(line)
        mapping.write("# end of gamess parameter set %s\n" % pset_index)
        return

    def info_gamess_setitem(self, name, val, interp ): #bruce 050701; needs to be extended by Mark to handle the actual params
        """This must set the parameter in self with the given name
        to the value encoded by the string val
        (read from an mmp file from which this parameter set and its gamess jig is being read).
           If it doesn't recognize name or can't parse val,
        it should do nothing (except possibly print a message if atom_debug is set).
           (If it's too tedious to avoid exceptions in parsing val,
        change the caller (which already ignores those exceptions, but always prints a message calling them bugs)
        to classify those exceptions as not being bugs (and to only print a message when atom_debug is set).
           [See also the docstring of Gamess.readmmp_info_gamess_setitem, which calls this.]
        """
        if name == 'param1':
            self.param1 = val ###@@@ change all this code to properly set this param to val; it has to decode val, which is a string
        elif name == 'param2':
            self.param2 = val.split() # always legal for strings
        elif name == 'param3':
            try:
                self.param3 = int(val)
            except:
                if platform.atom_debug:
                    print "atom_debug: fyi: info gamess %r with non-int value %r (not an error)" % (name,val)
                    # btw, the reason it's not an error is that the mmp file format might be extended to permit it.
                pass
        else:
            if platform.atom_debug:
                print "atom_debug: fyi: info gamess with unrecognized parameter name %r (not an error)" % (name,)
        return

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

    pass # end of class ctlRec

# end

