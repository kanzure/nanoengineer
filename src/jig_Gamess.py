
from jigs import Jig
from drawer import drawwirecube
from GamessProp import *

# == GAMESS

class Gamess(Jig):
    '''a Gamess jig has a list of atoms with one or more parameter sets used to run a GAMESS calcuation.'''

    sym = "Gamess"
    icon_names = ["gamess.png", "gamess-hide.png"]

    # create a blank Gamess jig with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        self.color = (0.0, 0.0, 0.0)
        self.normcolor = (0.0, 0.0, 0.0) # set default color of ground to black
        self.psets = [] # list of parms set objects
        self.psets.append(gamessParms('Parameter Set 1'))
        self.cntl = GamessProp(self, assy.o)

    def edit(self):
        self.cntl.setup(0)
        self.cntl.exec_loop()
        
    def add_pset(self):
        name = "Parameter Set " + str(len(self.psets) + 1)
        self.psets.append(gamessParms(name))
        return self.psets[len(self.psets)-1]
    
    def pset_number(self, i):
#        npsets = len(self.psets)
#        print "num psets =",npsets, ", pset index =", i, ", returned index = ",npsets - i - 1
        return self.psets[len(self.psets)-i-1]
        
    # it's drawn as a wire cube around each atom (default color = black)
    def _draw(self, win, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "gamess" record to POV-Ray file in the format:
    # gamess(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "gamess(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def _getinfo(self):
        return "[Object: GAMESS] [Name: " + str(self.name) + "] [Total Atoms: " + str(len(self.atoms)) + "]"

    def getstatistics(self, stats):
        stats.ngamess += len(self.atoms)

    mmp_record_name = "gamess"
    def mmp_record_jigspecific_midpart(self): # see also fake_Ground_mmp_record [bruce 050404]
        return ""

    def anchors_atom(self, atm): #bruce 050321; revised 050423 (warning: quadratic time for large ground jigs in Minimize)
        "does this jig hold this atom fixed in space? [overrides Jig method]"
        return (atm in self.atoms) and not self.is_disabled()
    
    pass # end of class Gamess

class gamessParms:
    def __init__(self, name):
        
        self.name = name or "" # assumed to be a string by some code
        self.contrl = ctlRec('CONTRL',contrl)
        self.scf = ctlRec('SCF',scf)
        self.system = ctlRec('SYSTEM',system)
        self.mp2 = ctlRec('MP2',mp2)
        self.dft = ctlRec('DFT',dft)
        self.guess = ctlRec('GUESS',guess)
        self.statpt = ctlRec('STATPT',statpt)
        self.force = ctlRec('FORCE',force)
        self.basis = ctlRec('BASIS',basis)

    def prin1(self, f=None):
        'Write all parms to input file'
        self.contrl.prin1(f)
        self.scf.prin1(f)
        self.system.prin1(f)
        self.mp2.prin1(f)
        if sys.platform != 'win32': # PC-GAMESS does not support DFT section records. Mark 052105
            self.dft.prin1(f)
        self.guess.prin1(f)
        self.statpt.prin1(f)
#        self.force.prin1()
        self.basis.prin1(f)

class ctlRec:
    def __init__(self, name, parms):
        self.name = name
        self.parms = parms.keys()
        for k in self.parms:
            self.__dict__[k] = parms[k]

    def prin1(self, f):
        'Write parms group to input file'
        f.write (" $"  + self.name + ' ')
        col = len(self.name)+2
        for k in self.parms:
            if not self.__dict__[k]: continue # Do not print null parms.
            phrase = k + '=' + str(self.__dict__[k])
            col += 1 + len(phrase)
            if col > 70: 
                col = len(phrase)
                f.write ('\n')
            f.write (phrase + ' ')
        f.write('$END\n')