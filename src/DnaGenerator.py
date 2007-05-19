# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif

Note: soon we may extend this to permit the following mixed-base code letters:

(reference: http://www.idtdna.com/InstantKB/article.aspx?id=13763 )

    The standard IUB codes for degenerate bases are:

    A = Adenosine;
    C = Cytosine; 
    G = Guanosine;
    T = Thymidine;
    B = C,G, or T;
    D = A,G, or T; 
    H = A,C, or T;
    V = A,C, or G;
    R = A or G (puRine);
    Y = C or T (pYrimidine);
    K = G or T (Keto);
    M = A or C (aMino);
    S = G or C (Strong -3H bonds);
    W = A or T (Weak - 2H bonds);
    N = aNy base.

Right now [070518] we just permit N, out of those.
"""

__author__ = "Will"

import sys
import os
import env
import re
from math import atan2, sin, cos, pi
from PyQt4 import QtCore
from PyQt4.Qt import QWhatsThis, QDialog, QWidget, SIGNAL, QTextCursor
from DnaGeneratorDialog import DnaPropMgr
from chem import Atom
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, dot, vlen
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from GeneratorBaseClass import GeneratorBaseClass, PluginBug, UserError
from fusechunksMode import fusechunksBase
from platform import find_plugin_dir
import random

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

END1 = '[' # these must be single characters, not used for base letters. 
END2 = ']'

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

DEBUG = False
DEBUG_SEQUENCE = False

class Dna:

    def make(self, assy, grp, sequence, doubleStrand, basesPerTurn, position,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine',
                        'N': 'unknown',
                        END1: 'end1',
                        END2: 'end2'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine',
                        'N': 'unknown',
                        END1: 'end1',
                        END2: 'end2'}):
        baseList = [ ]
        if DEBUG_SEQUENCE:
            print "making", sequence
        def insertmmp(filename, subgroup, tfm, position=position):
            try:
                grouplist  = _readmmp(assy, filename, isInsert=True)
            except IOError:
                raise PluginBug("Cannot read file: " + filename)
            if not grouplist:
                raise PluginBug("No atoms in DNA base? " + filename)
            viewdata, mainpart, shelf = grouplist
            for member in mainpart.members:
                for atm in member.atoms.values():
                    atm._posn = tfm(atm._posn) + position
            del viewdata
                   
            for member in mainpart.members:
                subgroup.addchild(member)
                baseList.append(member)
                
            shelf.kill()

        def rotateTranslate(v, theta, z):
            c, s = cos(theta), sin(theta)
            x = c * v[0] + s * v[1]
            y = -s * v[0] + c * v[1]
            return V(x, y, v[2] + z)

        # Calculate the twist per base in radians
        twistPerBase = (self.handedness * 2 * pi) / basesPerTurn
        
        if doubleStrand:
            subgroup = Group("strand 1", grp.assy, None)
            grp.addchild(subgroup)
        else:
            subgroup = grp
        subgroup.open = False

        if (sequence.isdigit()):
            baseCount = int(sequence)
            sequence = baseCount * "N"
        sequence = self.addEndCaps(sequence)
        theta = 0.0
        z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
        for i in range(len(sequence)):
            basefile, zoffset, thetaOffset = \
                      self.strandAinfo(basenameA[sequence[i]], i)
            def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                return rotateTranslate(v, theta, z1)
            if DEBUG: print basefile
            insertmmp(basefile, subgroup, tfm)
            theta -= twistPerBase
            z -= self.BASE_SPACING
        
        if doubleStrand:
            subgroup = Group("strand 2", grp.assy, None)
            subgroup.open = False
            grp.addchild(subgroup)
            theta = 0.0
            z = 0.5 * self.BASE_SPACING * (len(sequence) - 1)
            for i in range(len(sequence)):
                # The 3'-to-5' direction is reversed for strand B.
                basefile, zoffset, thetaOffset = \
                          self.strandBinfo(basenameB[sequence[i]], i)
                def tfm(v, theta=theta+thetaOffset, z1=z+zoffset):
                    # Flip theta, flip z
                    # Cheesy hack: flip theta by reversing the sign of y,
                    # since theta = atan2(y,x)
                    return rotateTranslate(V(v[0], -v[1], -v[2]), theta, z1)
                if DEBUG: print basefile
                insertmmp(basefile, subgroup, tfm)
                theta -= twistPerBase
                z -= self.BASE_SPACING

        # fuse the bases together into continuous strands
        fcb = fusechunksBase()
        fcb.tol = 1.5
        for i in range(len(baseList) - 1):
            fcb.find_bondable_pairs([baseList[i]], [baseList[i+1]])
            fcb.make_bonds(assy)
        
        from debug import print_compact_traceback
        try:
            self.postprocess(baseList)
        except:
            if env.debug():
                print_compact_traceback("debug: exception in %r.postprocess(baseList = %r) (reraising): " % (self, baseList,))
            raise
        return

    def addEndCaps(self, sequence):
        return sequence

    def postprocess(self, baseList):
        return
    pass

class A_Dna(Dna):
    """The geometry for A-DNA is very twisty and funky. I'd probably need to
    take a few days to research it. It's not a simple helix (like B) or an
    alternating helix (like Z).
    """
    geometry = "A-DNA"
    BASE_SPACING = 0    # WRONG
    handedness = -1     # right-handed
    
    def strandAinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
    def strandBinfo(self, sequence, i):
        raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");

class A_Dna_BasePseudoAtoms(A_Dna):
    pass

class B_Dna(Dna):
    geometry = "B-DNA"
    BASE_SPACING = 3.391    # angstroms
    handedness = -1         # right-handed

    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-bases', '%s.mmp' % basename)

    def strandAinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        zoffset = 0.0
        thetaOffset = 210 * (pi / 180)
        basefile = self.baseFileName(basename)
        return (basefile, zoffset, thetaOffset)

class B_Dna_BasePseudoAtoms(B_Dna):
    BASE_SPACING = 3.18 # angstroms
    handedness = -1     # right-handed
    fuseChunksTolerance = 1.0
    
    def baseFileName(self, basename):
        return os.path.join(basepath, 'bdna-pseudo-bases', '%s.mmp' % basename)
    def addEndCaps(self, sequence):
        if (len(sequence) > 1):
            return END1 + sequence[1:-1] + END2 #bruce 070518 replaced end-codes 'Y' and 'Z' with END1 and END2
        return sequence
    def postprocess(self, baseList): # bruce 070414
        # Figure out how to set bond direction on the backbone bonds of these strands.
        # This implem depends on the specifics of how the end-representations are terminated.
        # If that's changed, it might stop working or it might start giving wrong results.
        # In the current representation,
        # baseList[0] (a chunk) is called "end1" in MT, and has two bonds whose directions we should set,
        # which will determine the directions of their strands: Ss -> Sh, and Ss <- Pe.
        # Just find those bonds and set the strand directions
        # (until such time as they can be present to start with in the end1 mmp file).
        # (If we were instead passed all the atoms, we could be correct if we just did this
        #  to the first Pe and Sh we saw, or to both of each if setting the same direction twice
        #  is allowed.)
        atoms = baseList[0].atoms.values()
        Pe_list = filter( lambda atom: atom.element.symbol == 'Pe', atoms)
        Sh_list = filter( lambda atom: atom.element.symbol == 'Sh', atoms)
        if len(Pe_list) == len(Sh_list) == 1:
            for atom in Pe_list:
                assert len(atom.bonds) == 1
                atom.bonds[0].set_bond_direction_from(atom, 1, propogate = True)
            for atom in Sh_list:
                assert len(atom.bonds) == 1
                atom.bonds[0].set_bond_direction_from(atom, -1, propogate = True)
        else:
            raise PluginBug("error in setting strand bond direction; not set");
        return
    pass

class Z_Dna(Dna):
    geometry = "Z-DNA"
    BASE_SPACING = 3.715    # in angstroms
    handedness = 1          # left-handed

    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-bases', '%s-%s.mmp' % (basename, suffix))

    def strandAinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'outer'
            zoffset = 2.045
        else:
            suffix = 'inner'
            zoffset = 0.0
        thetaOffset = 0.0
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

    def strandBinfo(self, basename, i):
        if (i & 1) != 0:
            suffix = 'inner'
            zoffset = -0.055
        else:
            suffix = 'outer'
            zoffset = -2.1
        thetaOffset = 0.5 * pi
        basefile = self.baseFileName(basename, suffix)
        return (basefile, zoffset, thetaOffset)

class Z_Dna_BasePseudoAtoms(Z_Dna):
    def baseFileName(self, basename, suffix):
        return os.path.join(basepath, 'zdna-pseudo-bases', '%s-%s.mmp' % (basename, suffix))

###############################################################################

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class DnaGenerator(QDialog, GeneratorBaseClass, DnaPropMgr):

    cmd = greenmsg("Build DNA: ")
    sponsor_keyword = 'DNA'
    prefix = 'DNA-'   # used for gensym
    
    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        QDialog.__init__(self, win)
        DnaPropMgr.__init__(self)
        GeneratorBaseClass.__init__(self, win)
        self._random_data = []
    
    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def change_random_seed(self):
        if DEBUG_SEQUENCE:
            print "change random seed"
        self._random_data = []

    def _random_data_for_index(self, i):
        while len(self._random_data) < i+1:
            self._random_data.append( random.randrange(12) )
        return self._random_data[i]

    def gather_parameters(self):
        if not basepath_ok:
            raise PluginBug("The cad/plugins/DNA directory is missing.")
        dnatype = str(self.dnaConformation_combox.currentText())
        if dnatype == 'A-DNA':
            raise PluginBug("A-DNA is not yet implemented -- please try B- or Z-DNA");
        assert dnatype in ('B-DNA', 'Z-DNA')
        double = str(self.strandType_combox.currentText())

        # Bases per turn
        basesPerTurnString = str(self.basesPerTurn_combox.currentText())
        basesPerTurn = float(basesPerTurnString)
        if (basesPerTurn < 1) | (basesPerTurn > 100):
            basesPerTurn = 10.5
        
        representation = str(self.model_combox.currentText())
        if (representation == 'Reduced'):
            representation = 'BasePseudoAtom'
            chunkOption = str(self.dnaChunkOptions_combox.currentText())
            resolve_random = False # later this may depend on a new checkbox in that case;
                # for now it doesn't matter, since sequence info is discarded for reduced bases anyway
        if (representation == 'Atomistic'):
            representation = 'Atom'
            chunkOption = str(self.dnaChunkOptions_combox.currentText())
            resolve_random = True
                # if this flag was not set, for atomistic case, random base letters would cause error message below,
                # but the error message needs rewording for that... for now, it can't happen
            
        assert representation in ('Atom', 'BasePseudoAtom')

        (seq, allKnown) = self._get_sequence( resolve_random = resolve_random)

        if (representation == 'Atom' and not allKnown):
            raise UserError("Cannot use unknown bases (N) in Atomistic representation") # needs rewording (see above)

        if (representation == 'BasePseudoAtom' and dnatype == 'Z-DNA'):
            raise PluginBug("Z-DNA not implemented for 'Reduced model' representation.  Use B-DNA.")
        return (seq, dnatype, double, basesPerTurn, representation, chunkOption)
    
    def build_struct(self, name, params, position):
        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        seq, dnatype, double, basesPerTurn, representation, chunkOption = params

        if (representation == 'Atom'):
            doubleStrand = (double == 'Double')
            if dnatype == 'A-DNA':
                dna = A_Dna()
            elif dnatype == 'B-DNA':
                dna = B_Dna()
            elif dnatype == 'Z-DNA':
                dna = Z_Dna()

        elif (representation == 'BasePseudoAtom'):
            doubleStrand = False # a single pseudo strand creates two strands
            if dnatype == 'A-DNA':
                dna = A_Dna_BasePseudoAtoms()
            elif dnatype == 'B-DNA':
                dna = B_Dna_BasePseudoAtoms()
            elif dnatype == 'Z-DNA':
                dna = Z_Dna_BasePseudoAtoms()

        dna.double = doubleStrand
        self.dna = dna  # needed for done msg
        if len(seq) > 30:
            env.history.message(self.cmd + "This may take a moment...")
        grp = Group(self.name, self.win.assy,
                    self.win.assy.part.topnode)
        try:
            dna.make(self.win.assy, grp, seq, doubleStrand, basesPerTurn,
                     position)
            
            if self.dnaChunkOptions_combox.currentText() == 'Strand Chunks':
                if representation == 'Atom':
                    nodeForMT = self._makeSingleChunkStrands(grp,seq,representation,
                                             doubleStrand)
                    return nodeForMT
                elif representation == 'BasePseudoAtom':
                    nodeForMT = self._makeStrandAndAxisDna(grp,representation)
                    return nodeForMT
                    
            elif self.dnaChunkOptions_combox.currentText()=='DNA Chunk':
                nodeForMT = self._makeSingleChunkDna(grp,seq,representation,
                                         doubleStrand)                
                return nodeForMT
            
            return grp
        
        except (PluginBug, UserError):
            grp.kill()
            raise

    def _get_sequence(self, reverse = False, complement = False, resolve_random = False,
                     cdict = {'C':'G', 'G':'C', 'A':'T', 'T':'A', 'N':'N'}):
        """Return a tuple (seq, allKnown)
        where seq is a string in which each letter describes one base
        of the sequence currently described by the UI,
        as modified by the passed reverse, complement, and resolve_random flags,
        and allKnown is a boolean which says whether every base in the return value
        has a known identity.
           This method is not fully private. It's used repeatedly to get the same sequence
        when making the DNA (which means its return value should be deterministic,
        even when making sequences with randomly chosen bases [nim]),
        and it's also called from class DnaPropMgr (in DnaGeneratorDialog.py) to return data
        to be stored back into the UI, for implementing the reverse and complement buttons.
        (Ideally it would preserve whitespace and capitalization when used that way, but it doesn't.)
        """
        seq = ''
        allKnown = True
        # The current base sequence (or number of bases) in the PropMgr. Mark [070405]
        # (Note: I think this code implies that it can no longer be a number of bases. [bruce 070518 comment])
        pm_seq = str(self.base_textedit.toPlainText()).upper()
        #print "pm_seq =", pm_seq
        #match = numberPattern.match(pm_seq)
        #if (match):
        #    return(match.group(1), False)
        for ch in pm_seq:
            if ch in 'CGATN':
                if ch == 'N': ###e soon: or any other letter indicating a random base
                    if resolve_random: #bruce 070518 new feature
                        i = len(seq)
                        data = self._random_data_for_index(i) # a random int in range(12), in a lazily extended cache
                        ch = 'ACTG'[data%4]
                    else:
                        allKnown = False
                if complement:
                    ch = cdict[ch]
                seq += ch
            elif ch in '\ \t\r\n':
                pass
            else:
                raise UserError('Bogus DNA base: ' + ch + ' (should be C, G, A, T, or N)')
        assert len(seq) > 0, 'Please enter a valid sequence'
        if reverse:
            seq = list(seq)
            seq.reverse()
            seq = ''.join(seq)
        return (seq, allKnown)
    
    def _makeSingleChunkDna(self, grp, seq, representation, 
                            bool_doubleStrand):
        """Combine both strands into a single chunk.
        """
        
        from chunk import molecule
        
        self._makeSingleChunkStrands(grp,seq,representation, bool_doubleStrand)
        
        if not isinstance(grp.members[0], molecule):
            env.history.message(redmsg(
                "Internal error in creating a single chunk DNA"))
            return
        
        for m in grp.members[1:]:
            if isinstance(m, molecule):
                grp.members[0].merge(m)
                
        #rename the merged chunk 
        grp.members[0].name = grp.name
        
        nodeForMT = grp.members[0]
        #ungroup
        grp.ungroup()
        
        return nodeForMT
    
       
    def _makeSingleChunkStrands(self,grp,seq,representation, bool_doubleStrand):
        """Combine all bases of a single strand into a single chunk.
        """

        from chunk import molecule
                   
        if bool_doubleStrand:
            counter = 0
            for subgrp in grp.members:
                if isinstance(subgrp,Group):
                    #This is for a double stranded dna
                    mol = subgrp.members[0]
                    for m in subgrp.members[1:]:                           
                        mol.merge(m)
                    mol.name = self._renameSingleChunkStrands(counter)
                    #ungroup
                    subgrp.ungroup()
                else:
                    print "bug in merging DNA strand bases into a single chunk" 
                    return None
                
                counter +=1
        else:
            #single stranded DNA
            mol = grp.members[0]  
            
            if not isinstance(mol, molecule):
                env.history.message(
                    redmsg("Internal error in creating a single chunk DNA"))
                return 
                          
            for m in grp.members[1:]:
                if isinstance(m,molecule):
                    mol.merge(m)
            
            counter = 0
            mol.name = self._renameSingleChunkStrands(
                        counter,singleStrand = True) 
        
        return grp
    
    
    def _renameSingleChunkStrands(self,strandCounter, singleStrand = False):
        """Rename the strand as 'strand-n:first four characters of its
        base sequence. 
        Example: strand1: ATGC
        @return: strandName: returns the strand name string.
        """
        
        if strandCounter == 0:
            (seq, allKnown) = self._get_sequence()
        else:
            (seq, allKnown) = self._get_sequence(complement=True)
        
        if singleStrand:
            strandName = 'strand:' + seq[0:4]
        else:            
            strandName = 'strand-' + str(strandCounter +1) + ':' + seq[0:4]
        
        if len(seq) > 4:
            strandName = strandName + '...'
                          
        return strandName
    
    def _makeStrandAndAxisDna(self, grp,representation):
        """Create Chunks for individual strands and a chunk for the axis 
        in Pseudo-atom Dna representation.
        """
        
        #ninad070426: Implementation Notes: 
        # It takes one chunk from the supplied group
        # scans through the atoms of the chunk. If it finds a 'Sugar' or an 
        # 'Axis' element, it makes new chunk for set of atoms 'really connected'
        #to that 'Sugar element' or 'Axis Element' Thus we get three chunks. 
        # This may be optimized in future. Ok for now. 
        
        from chunk import molecule
        
        mol = grp.members[0]
        
        if not isinstance(mol, molecule):
                env.history.message(
                    redmsg(
                        "Internal error in creating a chunks for strands and axis"
                    ))
                return 
        
        axis_elements = ('Ax','Ae')   
        
        #ninad070426: Each strand will have a sugar element. So don't include Phosphates
        #in this list. This way the program will only stop at a sugar element 
        #(in the 5 atom psudo atom model), then get the list of 
        #'really connected atoms'and then create a new chunk from this list, and
        #assdin it the name (either strand1 or strand2) 
        
        strand_sugar_elements = ('Ss','Sj','Sh', 'Hp')
        
        #chunkCounter make sures to exit out of this method once all three 
        #chunks are created program 
        chunkCounter = 0 
        strandNumber = 1
        tempList = []
        for m in grp.members[1:]:
            ##if chunkCounter > 3:
                ##return
            if isinstance(m,molecule):
                for atm in m.atoms.values():  
                    if atm.element.symbol in axis_elements or \
                       atm.element.symbol in strand_sugar_elements:                        
                        tempList.append(atm)
                        atomList = self.win.assy.getConnectedAtoms(tempList)
                        numol = self._makeChunkFromAtomList(atomList)
                        tempList = []     
                        
                        if atm.element.symbol in axis_elements:
                            numol.name = 'Axis'
                        elif atm.element.symbol in strand_sugar_elements:
                            numol.name = 'Strand-' + str(strandNumber)
                            strandNumber +=1
                            
                        grp.addmember(numol)
                        chunkCounter +=1
                        
                if chunkCounter >3:
                    print "Dna Generator: internal error in generating strand-axis chunk dna"
                    return
                                    
                self.win.win_update()
                
                return grp
         
        
    def _makeChunkFromAtomList(self, atmList):
        """Creates a new chunk from the given atom list
        @return : numol:created molecule
        @params : atmList: List of atoms from which to create the chunk.
        """
        
        #ninad070426 : this may be moved to ops_rechunk.py
        
        #see also: ops_rechunk.makeChunkFromAtoms
        if not atmList:
            print "bug in creating chunks from the given atom list"
            return
        
        from chunk import molecule
        from chem import gensym    
        numol = molecule(self.win.assy, gensym("Chunk"))
        for a in atmList:            
            # leave the moved atoms picked, so still visible
            a.hopmol(numol)
        return numol   
                               
    def show(self):
        self.setSponsor()
        
        #Show it in Property Manager Tab ninad061207
        if not self.pw:            
            self.pw = self.win.activePartWindow()       #@@@ ninad061206  
            self.pw.updatePropertyManagerTab(self)
            self.pw.featureManager.setCurrentIndex(
                self.pw.featureManager.indexOf(self))
        else:
            self.pw.updatePropertyManagerTab(self)
            self.pw.featureManager.setCurrentIndex(
                self.pw.featureManager.indexOf(self))

    ###################################################
    # The done message

    def done_msg(self):
        dna = self.dna
        if dna.double:
            dbl = "double "
        else:
            dbl = ""
        return "Done creating a %sstrand of %s." % (dbl, dna.geometry)
    
    ###################################################
    # Restore defaults
    
    def restore_defaults_btn_clicked(self):
        """Slot for Restore Defaults button
        """
        self.model_combox.setCurrentIndex(0)
        self.length_spinbox.setValue(0)
