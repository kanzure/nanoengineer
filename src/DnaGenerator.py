# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGenerator.py

$Id$

@author: Will Ware
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif

Note: soon we may extend this to permit the following 
mixed-base code letters:

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

History:
Jeff 2007-06-13
- Moved Dna class (and subclasses) to file Dna.py.

"""

__author__ = "Will"

import os
import random

from PyQt4.Qt import QDialog

import env
from DnaGeneratorDialog import DnaPropertyManager
from GeneratorBaseClass import GeneratorBaseClass, PluginBug, UserError
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, vlen
from Numeric import dot
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from fusechunksMode import fusechunksBase
from platform import find_plugin_dir

from Dna import Dna
from Dna import A_Dna, A_Dna_BasePseudoAtoms
from Dna import B_Dna, B_Dna_BasePseudoAtoms
from Dna import Z_Dna, Z_Dna_BasePseudoAtoms
from Dna import DEBUG, DEBUG_SEQUENCE
from Dna import basepath, basepath_ok

############################################################################

# DnaPropertyManager must come BEFORE GeneratorBaseClass in this list
class DnaGenerator(QDialog, DnaPropertyManager, GeneratorBaseClass):

    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'DNA-'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        QDialog.__init__(self, win)
        DnaPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)
        self._random_data = []
    
    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def change_random_seed(self):
        if DEBUG_SEQUENCE:
            print "change random seed"
        self._random_data  =  []

    def _random_data_for_index(self, inIndex):
        while len( self._random_data ) < (inIndex + 1):
            self._random_data.append( random.randrange(12) )
        return self._random_data[inIndex]

    def gather_parameters(self):
        if not basepath_ok:
            raise PluginBug("The cad/plugins/DNA directory is missing.")
        dnatype = str(self.conformationComboBox.currentText())
        if dnatype == 'A-DNA':
            raise PluginBug("""A-DNA is not yet implemented -- please try 
            B- or Z-DNA""");
        assert dnatype in ('B-DNA', 'Z-DNA')


        double  =  str( self.strandTypeComboBox.currentText() )

        # Get bases per turn
        basesPerTurnString = str(self.basesPerTurnComboBox.currentText())
        basesPerTurn = float(basesPerTurnString)
        if (basesPerTurn < 1) | (basesPerTurn > 100):
            basesPerTurn = 10.5
        
        representation = str(self.modelComboBox.currentText())
        if (representation == 'Reduced'):
            representation = 'BasePseudoAtom'
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = False
                # Later this flag may depend on a new checkbox in that case;
                # for now it doesn't matter, since sequence info is 
                # discarded for reduced bases anyway.
        if (representation == 'Atomistic'):
            representation = 'Atom'
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = True
                # If this flag was not set, for atomistic case, random base 
                # letters would cause error message below, but the error 
                # message needs rewording for that... for now, it can't 
                # happen.
            
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

        # Instantiate the DNA subclass 
        # (based on representation and conformation)
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
        
        if len(seq) < 1: # Mark 2007-06-01
            msg = redmsg("You must enter a strand sequence to preview/insert DNA")
            self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
            env.history.message(msg)
            self.dna = None
            return None
            
        if len(seq) > 30:
            env.history.message(self.cmd + "This may take a moment...")

        # Create node in model tree.        
        grp = Group(self.name, self.win.assy,
                    self.win.assy.part.topnode)
        try:
            dna.make(self.win.assy, grp, seq, doubleStrand, basesPerTurn,
                     position)
            
            if self.createComboBox.currentText() == 'Strand chunks':
                if representation == 'Atom':
                    nodeForMT = self._makeSingleChunkStrands(grp,seq,representation,
                                             doubleStrand)
                    return nodeForMT
                elif representation == 'BasePseudoAtom':
                    nodeForMT = self._makeStrandAndAxisDna(grp,representation)
                    return nodeForMT
                    
            elif self.createComboBox.currentText()=='Single chunk':
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
        where seq is a string in which each letter describes one base of the 
        sequence currently described by the UI, as modified by the passed 
        reverse, complement, and resolve_random flags, and allKnown is a 
        boolean which says whether every base in the return value has a 
        known identity.
           This method is not fully private. It's used repeatedly to get the 
        same sequence when making the DNA (which means its return value 
        should be deterministic, even when making sequences with randomly 
        chosen bases [nim]), and it's also called from class DnaPropMgr 
        (in DnaGeneratorDialog.py) to return data to be stored back into the 
        UI, for implementing the reverse and complement buttons.  
        (Ideally it would preserve whitespace and capitalization when used 
        that way, but it doesn't.)
        """
        seq = ''
        allKnown = True
        # The current base sequence (or number of bases) in the PropMgr. Mark [070405]
        # (Note: I think this code implies that it can no longer be a number of bases. [bruce 070518 comment])
        pm_seq = str(self.strandSeqTextEdit.toPlainText()).upper()
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
        
        # Marked for removal. Mark 2007-06-01
        #@assert len(seq) > 0, 'Please enter a valid sequence'
            
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
        from constants import gensym    
        numol = molecule(self.win.assy, gensym("Chunk"))
        for a in atmList:            
            # leave the moved atoms picked, so still visible
            a.hopmol(numol)
        return numol   
                               
    ###################################################
    # The done message

    def done_msg(self):
        dna = self.dna
        
        if not dna: # Mark 2007-06-01
            return "No DNA added."
        
        if dna.double:
            dbl = "double "
        else:
            dbl = ""
        return "Done creating a %sstrand of %s." % (dbl, dna.geometry)
    

