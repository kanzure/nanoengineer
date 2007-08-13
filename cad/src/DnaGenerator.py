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

    A = Adenine;
    C = Cytosine; 
    G = Guanine;
    T = Thymine;
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

Jeff 2007-06-13:
- Moved Dna class (and subclasses) to file Dna.py.
"""

__author__ = "Will"

import env
import os
import random

from Utility        import Group
from HistoryWidget  import redmsg, orangemsg, greenmsg
from VQT            import A, V, vlen
from Numeric        import dot
from bonds          import inferBonds, bond_atoms
from chunk          import molecule
from constants      import gensym    
from files_mmp      import _readmmp
from fusechunksMode import fusechunksBase
from platform       import find_plugin_dir

from Dna import Dna
from Dna import A_Dna, A_Dna_PAM5
from Dna import B_Dna, B_Dna_PAM5
from Dna import Z_Dna, Z_Dna_PAM5
from Dna import DEBUG, DEBUG_SEQUENCE
from Dna import basepath, basepath_ok

from GeneratorBaseClass          import GeneratorBaseClass, PluginBug, UserError
from DnaGeneratorPropertyManager import DnaGeneratorPropertyManager

############################################################################

# DnaGeneratorPropertyManager must come BEFORE GeneratorBaseClass in this list
class DnaGenerator(DnaGeneratorPropertyManager, GeneratorBaseClass):

    cmd              =  greenmsg("Build DNA: ")
    sponsor_keyword  =  'DNA'
    prefix           =  'DNA-'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        DnaGeneratorPropertyManager.__init__(self)
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
        """
        Return the parameters from the property manager UI.
        
        @return: All the parameters:
                 - dnaSequence
                 - dnaType
                 - strandType
                 - basesPerTurn
                 - dnaModel
                 - chunkOption
        @rtype:  tuple
        """
        if not basepath_ok:
            raise PluginBug("The cad/plugins/DNA directory is missing.")
        dnaType = str(self.conformationComboBox.currentText())
        if dnaType == 'A-DNA':
            raise PluginBug("""A-DNA is not yet implemented -- please try 
            B- or Z-DNA""");
        assert dnaType in ('B-DNA', 'Z-DNA')

        strandType  =  str( self.strandTypeComboBox.currentText() )

        # Get bases per turn.
        basesPerTurnString = str(self.basesPerTurnComboBox.currentText())
        basesPerTurn = float(basesPerTurnString)
        
        dnaModel = str(self.modelComboBox.currentText())
        
        if (dnaModel == 'Reduced'):
            dnaModel = 'PAM5'
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = False
                # Later this flag may depend on a new checkbox in that case;
                # for now it doesn't matter, since sequence info is 
                # discarded for reduced bases anyway.
                
        if (dnaModel == 'Atomistic'):
            dnaModel = 'Atom'
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = True
                # If this flag was not set, for atomistic case, random base 
                # letters would cause error message below, but the error 
                # message needs rewording for that... for now, it can't 
                # happen.
            
        assert dnaModel in ('Atom', 'PAM5')

        (dnaSequence, allKnown) = self._getSequence( resolve_random = resolve_random)

        if allKnown == False:
            dnaSequence  =  self.convertUnrecognized(dnaSequence)

        if (dnaModel == 'Atom' and not allKnown):
            raise UserError("Cannot use unknown bases (N) in Atomistic model") # needs rewording (see above)

        if (dnaModel == 'PAM5' and dnaType == 'Z-DNA'):
            raise PluginBug("Z-DNA not implemented for 'PAM-5 reduced model'. Use B-DNA.")

        return (dnaSequence, 
                dnaType,
                strandType,
                basesPerTurn,
                dnaModel,
                chunkOption)
    
    def checkParameters( self, inParams ):
        """
        Verify that the strand sequence 
        contains no unknown/invalid bases.
        """
        theSequence, isValid  =  self._getSequence()
        
        return isValid
    
    def correctParameters( self, inParams):
        """
        Alert the user that the entered sequence is invalid. Give them
        some options for how to correct the sequence.
        """
        #theDialog  =  Ui_InvalidSequenceDialog()
        
        #optionsButtonGroup  =  theDialog.findChild( 'buttonbox_options' )
        #result  =  theDialog.exec()
        #choice  =  optionsButtonGroup.checkedid()
        
        if result == QDialog.Accepted:
            print 'choice: ', choice

        return inParams
    
    def build_struct(self, name, params, position):
        """
        Build the DNA helix based on parameters in the UI.
        
        @param name: The name to assign the node in the model tree.
        @type  name: str
        
        @param params: The list of parameters gathered from the PM.
        @type  params: tuple
        
        @param position: The position in 3d model space at which to
                         create the DNA strand. This is always 0, 0, 0.
        @type position:  position
        """
        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        theSequence, dnaType, strandType, basesPerTurn, dnaModel, chunkOption = params
        
        if len(theSequence) < 1: # Mark 2007-06-01
            msg = redmsg("You must enter a strand sequence to preview/insert DNA")
            self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
            env.history.message(msg)
            self.dna = None
            return None
            
        if (dnaModel == 'Atom') & (len(theSequence) > 30):
            # This message should appear in the PM message box, but it needs to be
            # flushed (reset) after the DNA is created.
            env.history.message(self.cmd + "This may take a moment...")
            
        # Instantiate the DNA subclass 
        # (based on dnaModel and conformation)
        if (dnaModel == 'Atom'):
            doubleStrand = (strandType == 'Double')
            if dnaType == 'A-DNA':
                dna = A_Dna()
            elif dnaType == 'B-DNA':
                dna = B_Dna()
            elif dnaType == 'Z-DNA':
                dna = Z_Dna()

        elif (dnaModel == 'PAM5'):
            doubleStrand = False # a single pseudo strand creates two strands.
            if dnaType == 'A-DNA':
                dna = A_Dna_PAM5()
            elif dnaType == 'B-DNA':
                dna = B_Dna_PAM5()
            elif dnaType == 'Z-DNA':
                dna = Z_Dna_PAM5()

        # Set critical dna instance variables.
        dna.doubleStrand = doubleStrand
        dna.sequence     = theSequence
        
        self.dna = dna  # needed for done msg
        
        # Create node in model tree.        
        grp = Group(self.name, 
                    self.win.assy,
                    self.win.assy.part.topnode)
        try:
            dna.make(self.win.assy, grp, basesPerTurn, position)
            
            if self.createComboBox.currentText() == 'Strand chunks':
                if dnaModel == 'Atom':
                    nodeForMT = self._makeSingleChunkStrands(grp,
                                                             theSequence,
                                                             dnaModel,
                                                             doubleStrand)
                    return nodeForMT
                
                elif dnaModel == 'PAM5':
                    nodeForMT = self._makePAM5StrandAndAxisChunks(grp, dnaModel)
                    return nodeForMT
                    
            elif self.createComboBox.currentText()=='Single chunk':
                nodeForMT = self._makeSingleChunkDna(grp, 
                                                     theSequence, 
                                                     dnaModel,
                                                     doubleStrand)                
                return nodeForMT
            
            return grp
        
        except (PluginBug, UserError):
            grp.kill()
            raise

    def _getSequence( self, 
                       reverse = False, 
                       complement = False, 
                       resolve_random = False, 
                       cdict = {} ):
        """
        Get the current sequence from the Property Manager.
        
        This method is not fully private. It's used repeatedly to get the 
        same sequence when making the DNA (which means its return value 
        should be deterministic, even when making sequences with randomly 
        chosen bases [nim]), and it's also called from class 
        DnaGeneratorPropertyManager to return data to be stored back into the 
        Property Manager, for implementing the reverse and complement actions.
        (Ideally it would preserve whitespace and capitalization when used 
        that way, but it doesn't.)
        
        @param reverse: If true, returns the reverse sequence.
        @type  reverse: bool
        
        @param complement: If true, returns the complement sequence.
        @type  complement: bool
        
        @param resolve_random:
        @type  resolve_random: True
        
        @param cdict:
        @type  cdict: dictionary
        
        @return: (sequence, allKnown) where I{sequence} is a string in which 
                 each letter describes one base of the sequence currently
                 described by the UI, as modified by the passed reverse, 
                 complement, and resolve_random flags, and I{allKnown} is a 
                 boolean which says whether every base in the return value 
                 has a known identity.
        @rtype:  tuple
        
        @note: All punctuation/symbols are purged from the sequence and
               any bogus/unknown bases are substituted as 'N' (unknown).
        """
        
        cdict    =  Dna.basesDict
        sequence = ''
        allKnown = True
        
        # The current sequence (or number of bases) in the PropMgr. Mark [070405]
        # (Note: I think this code implies that it can no longer be a number of bases. [bruce 070518 comment])
        pm_seq  =  str(self.getPlainSequence(inOmitSymbols = True)) # :jbirac: 20070629
        #print "pm_seq =", pm_seq
        #match = numberPattern.match(pm_seq)
        #if (match):
        #    return(match.group(1), False)
        for ch in pm_seq:
            if ch in cdict.keys():  #'CGATN':
                properties = cdict[ch]
                if ch == 'N': ###e soon: or any other letter indicating a random base
                    if resolve_random: #bruce 070518 new feature
                        i    = len(sequence)
                        data = self._random_data_for_index(i) # a random int in range(12), in a lazily extended cache
                        ch   = list(cdict)[data%4]  # modulus must agree with number of valid entries in cdict.
                    else:
                        allKnown = False
                if complement:
                    try:
                        ch = properties['Complement']
                    except (KeyError):
                        ch = 'N'
                        raise KeyError("DNA dictionary entry must include a 'Complement' key.")
            elif ch in self.validSymbols: #'\ \t\r\n':
                ch  =  ''
            else:
                #raise UserError('Bogus DNA base: ' + ch + ' (should be ' + str(cdict.keys()) + ')')
                ch        =  'N'                
                allKnown  =  False

            sequence += ch

        if reverse: 
            sequence = self.reverseSequence(sequence)
        
        return (sequence, allKnown)
    
    def reverseSequence(self, inSequence):
        """
        Reverses the order of the DNA sequence I{inSequence}.
        
        @param inSequence: DNA sequence.
        @type  inSequence: str
        
        @return: The reversed sequence.
        @rtype:  str
        """
        outSequence = list(inSequence)
        outSequence.reverse()
        outSequence = ''.join(outSequence)
        return outSequence

    def _makeSingleChunkDna(self, grp, sequence, dnaModel, 
                            doubleStrand):
        """
        Combine both strands into a single chunk.
        """
        
        self._makeSingleChunkStrands(grp, sequence, dnaModel, doubleStrand)
        
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
       
    def _makeSingleChunkStrands(self, grp, sequence, dnaModel, doubleStrand):
        """
        Combine all bases of a single strand into a single chunk.
        """
                   
        if doubleStrand:
            counter = 0
            for subgrp in grp.members:
                if isinstance(subgrp, Group):
                    # This is for a double stranded DNA.
                    mol = subgrp.members[0]
                    for m in subgrp.members[1:]:                           
                        mol.merge(m)
                    mol.name = self._renameSingleChunkStrands(counter)
                    # Ungroup.
                    subgrp.ungroup()
                else:
                    print "Bug in merging DNA strand bases into a single chunk." 
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
    
    def _renameSingleChunkStrands(self, strandCounter, singleStrand = False):
        """
        Rename the strand as 'strand-n:first four characters of its
        base sequence. 
        Example: strand1: ATGC
        
        @return: strandName: returns the strand name string.
        """
        
        if strandCounter == 0:
            (sequence, allKnown) = self._getSequence()
        else:
            (sequence, allKnown) = self._getSequence(complement=True)
        
        if singleStrand:
            strandName = 'strand:' + sequence[0:4]
        else:            
            strandName = 'strand-' + str(strandCounter +1) + ':' + sequence[0:4]
        
        if len(sequence) > 4:
            strandName = strandName + '...'
                          
        return strandName
    
    def _makePAM5StrandAndAxisChunks(self, grp, dnaModel):
        """
        Creates 2 strand and 1 axis chunk for PAM-5 model.
        
        @param grp:
        @type  grp: Group
        
        @param dnaModel: DNA model representation (i.e. "Atom" or "PAM5").
        @type  dnaModel: str
        """
        
        # ninad070426: Implementation Notes: 
        # It takes one chunk from the supplied group and
        # scans through the atoms of that chunk. If it finds a 'Sugar' or an 
        # 'Axis' element, it makes new chunk for set of atoms 'really connected'
        # to that 'Sugar element' or 'Axis Element'. Thus we get three chunks. 
        # This may be optimized in future. Ok for now. 
                
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
                        newChunk = self._makeChunkFromAtomList(atomList)
                        tempList = []     
                        
                        if atm.element.symbol in axis_elements:
                            newChunk.name = 'Axis'
                        elif atm.element.symbol in strand_sugar_elements:
                            newChunk.name = 'Strand-' + str(strandNumber)
                            strandNumber +=1
                            
                        grp.addmember(newChunk)
                        chunkCounter +=1
                        
                if chunkCounter >3:
                    print "Dna Generator: internal error in generating strand-axis chunk dna"
                    return
                                    
                self.win.win_update()
                
                return grp
             
    def _makeChunkFromAtomList(self, atomList):
        """
        Creates a new chunk from the given atom list.
        
        @param atomList: List of atoms from which to create the chunk.
        @type  atomList: list
        
        @return: The new chunk.
        @rtype:  L{molecule}
        
        """
        
        # ninad070426 : this may be moved to ops_rechunk.py
        
        # see also: ops_rechunk.makeChunkFromAtoms
        if not atomList:
            print "bug in creating chunks from the given atom list"
            return
        
        newChuck = molecule(self.win.assy, gensym("Chunk"))
        for a in atomList:            
            # leave the moved atoms picked, so still visible
            a.hopmol(newChunk)
        return newChunk   
                               
    ###################################################
    # The done message

    def done_msg(self):
        dna = self.dna
        
        if not dna: # Mark 2007-06-01
            return "No DNA added."
        
        if dna.doubleStrand:
            dbl = "double "
        else:
            dbl = ""
        return "Done creating a %sstrand of %s." % (dbl, dna.geometry)
    

