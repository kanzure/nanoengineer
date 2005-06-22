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
from SimServer import SimServer

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
        self.psets = [] # list of parms set objects
        self.psets.append(gamessParms('Parameter Set 1'))
        self.gmsjob = GamessJob(Gamess.job_parms, jig=self)
        self.gmsjob.edit()
        

    def edit(self):
        self.gmsjob.edit()
        
    def add_pset(self):
        '''Add a new parameter set to this jig.
        '''
        name = "Parameter Set " + str(len(self.psets) + 1)
        self.psets.insert(0, gamessParms(name))
        return self.psets[0]
        
    def get_pset_names(self):
        '''Return a list of the parm set names for this jig.  The list is in reverse order.
        '''
        names = []
        # I want to talk to Bruce about this reversal thing.  Mark 050530.
        for p in self.psets:
            names.append(p.name)
        return names
    
#    def pset_number(self, i):
#        return self.psets[i]
        
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
        return "[Object: GAMESS] [Name: " + str(self.name) + "] [Total Atoms: " + str(len(self.atoms)) + "]"

    def getstatistics(self, stats):
        stats.ngamess += 1
        
    def __CM_Calculate_Energy(self):
        
        final_energy = self.gmsjob.get_gamess_energy()

        if final_energy:
            msg = "GAMESS finished.  The final energy is: " + str(final_energy)
        else:
            msg = redmsg("Final energy value not found.")
        self.assy.w.history.message(msg)
        
        return

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