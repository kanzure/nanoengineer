# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGenerator.py

$Id$

@author: Will Ware
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.

History:

Jeff 2007-06-13:
- Moved Dna class (and subclasses) to file Dna.py.
Mark 2007-08-23:
- Heavily restructured and cleaned up.
"""

# To do:
# 1) Use two endpoints to create an arbitrarily positioned duplex.
# 2) Remove support for Atomistic DNA models.

__author__ = "Will"

import env
import os
import random

from Utility        import Group
from HistoryWidget  import redmsg, orangemsg, greenmsg
from VQT            import A, Q, V, angleBetween, cross, vlen, Veq
from Numeric        import dot
from math           import pi
from bonds          import inferBonds, bond_atoms
from chunk          import molecule
from constants      import gensym    
from files_mmp      import _readmmp
from fusechunksMode import fusechunksBase
from platform       import find_plugin_dir

from Dna_Constants  import basesDict
from Dna            import Dna
from Dna            import A_Dna, A_Dna_PAM5
from Dna            import B_Dna, B_Dna_PAM5
from Dna            import Z_Dna, Z_Dna_PAM5
from Dna            import DEBUG_SEQUENCE
from Dna            import basepath, basepath_ok

from GeneratorBaseClass import GeneratorBaseClass, CadBug, PluginBug, UserError
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
    
    # ##################################################
    # How to build this kind of structure, along with
    # any necessary helper functions.

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

        # Get bases per turn.
        basesPerTurnString = str(self.basesPerTurnComboBox.currentText())
        basesPerTurn = float(basesPerTurnString)
        
        #@dnaModel = str(self.modelComboBox.currentText())
        dnaModel = "PAM5"
        
        if (dnaModel == 'PAM5'):
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = False
                # Later this flag may depend on a new checkbox in that case;
                # for now it doesn't matter, since sequence info is 
                # discarded for reduced bases anyway.
                
        if (dnaModel == 'Atomistic'):
            chunkOption = str(self.createComboBox.currentText())
            resolve_random = True
                # If this flag was not set, for atomistic case, random base 
                # letters would cause error message below, but the error 
                # message needs rewording for that... for now, it can't 
                # happen.
            
        assert dnaModel in ('Atomistic', 'PAM5')

        (dnaSequence, allKnown) = self._getSequence( resolve_random = resolve_random)

        atcgnSequence  =  self.convertUnrecognized(dnaSequence)

        if (dnaModel == 'Atomistic' and not allKnown):
            raise UserError("Must use A,C,G or T only for Atomistic models.") # needs rewording (see above)

        if (dnaModel == 'PAM5' and dnaType == 'Z-DNA'):
            raise PluginBug("Z-DNA not implemented for 'PAM-5 reduced model'. Use B-DNA.")
        
        x1 = self.x1SpinBox.value()
        y1 = self.y1SpinBox.value()
        z1 = self.z1SpinBox.value()
        
        x2 = self.x2SpinBox.value()
        y2 = self.y2SpinBox.value()
        z2 = self.z2SpinBox.value()
        
        endpoint1 = V(x1, y1, z1)
        endpoint2 = V(x2, y2, z2)

        return (dnaSequence, 
                atcgnSequence,
                dnaType,
                basesPerTurn,
                dnaModel,
                chunkOption,
                endpoint1, 
                endpoint2)
    
    def checkParameters( self, inParams ):
        """
        Verify that the strand sequence contains no unknown/invalid bases.
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
        theSequence, \
        atcgnSequence, \
        dnaType, \
        basesPerTurn, \
        dnaModel, \
        chunkOption, \
        endpoint1, \
        endpoint2 = params
        
        if Veq(endpoint1, endpoint2):
            # Ask Bruce is there is a better/preferred way of checking this.
            # Works fine for now.  Mark 2007-08-28
            raise CadBug("Dna endpoints cannot be the same point.")
            return
        
        if len(theSequence) < 1: # Mark 2007-06-01
            msg = redmsg("You must enter a strand sequence to preview/insert DNA")
            self.MessageGroupBox.insertHtmlMessage(msg, setAsDefault=False)
            self.dna = None
            return None
            
        if (dnaModel == 'Atomistic') & (len(theSequence) > 30):
            # This message should appear in the PM message box, but it needs to be
            # flushed (reset) after the DNA is created.
            env.history.message(self.cmd + "This may take a moment...")

        # Instantiate the DNA subclass (based on dnaModel and conformation).
            
        if (dnaModel == 'Atomistic'):
            if dnaType == 'A-DNA':
                dna = A_Dna()
            elif dnaType == 'B-DNA':
                dna = B_Dna()
            elif dnaType == 'Z-DNA':
                dna = Z_Dna()

        elif (dnaModel == 'PAM5'):
            if dnaType == 'A-DNA':
                dna = A_Dna_PAM5()
            elif dnaType == 'B-DNA':
                dna = B_Dna_PAM5()
            elif dnaType == 'Z-DNA':
                dna = Z_Dna_PAM5()
        
        self.dna = dna  # needed for done msg
        
        # Create the model tree group node. 
        rawDnaGroup = Group(self.name, 
                            self.win.assy,
                            self.win.assy.part.topnode)
        try:
            # Make the DNA duplex. <rawDnaGroup> returns a different 
            # grouping arrangement for atomistic vs. PAM5. This 'issue'
            # is resolved when we regroup the atoms into strand chunks
            # below.
            dna.make(rawDnaGroup, theSequence, basesPerTurn, position)
             
            self._orientRawDnaGroup(rawDnaGroup, endpoint1, endpoint2)
        
            # Now group the DNA atoms based on the grouping option selected
            # (i.e. "Strand chunks" or "Single Chunk").
            # Note: We regroup <rawDnaGroup> so that both atomistic and PAM5
            # end up with atoms organized in a consistent manner (except that
            # the axis atoms in PAM5 models are placed in their own "Axis" 
            # group).
            if dnaModel == 'Atomistic':
                dnaGroup = self._makeAtomisticSingleChunkStrands(rawDnaGroup)
            elif dnaModel == 'PAM5':
                dnaGroup = self._makePAM5StrandAndAxisChunks(rawDnaGroup)
            else:
                raise PluginBug("Unknown model: %r" % (dnaModel))
                return None
            
            if chunkOption == 'Single chunk':
                return self._makeDuplexChunk(dnaGroup)
            
            return dnaGroup
        
        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            rawDnaGroup.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")
            return None
        
    def _orientRawDnaGroup(self, rawDnaGroup, pt1, pt2):
        """
        Orients the raw DNA group based on two endpoints.
        
        @param rawDnaGroup: The raw DNA group created by make().
        @type  rawDnaGroup: L{Group}
        
        @param pt1: The first endpoint of the DNA strand.
        @type  pt1: L{V}
        
        @param pt2: The second endpoint of the DNA strand.
        @type  pt2: L{V}
        
        @attention: Only works for PAM5 models.
        """
        
        a = V(0.0, 0.0, -1.0)
        # <a> is the unit vector pointing down the center axis of the default
        # rawDnaGroup structure which is aligned along the Z axis.
        bLine = pt2 - pt1
        bLength = vlen(bLine)
        b = bLine/bLength
        # <b> is the unit vector parallel to the line (i.e. pt1, pt2).
        axis = cross(a, b)
        # <axis> is the axis of rotation.
        theta = angleBetween(a, b)
        # <theta> is the angle (in degress) to rotate about <axis>.
        scalar = self.dna.getBaseRise() * self._getSequenceLength() * 0.5
        rawOffset = b * scalar
        
        if 0: # Debugging code.
            print ""
            print "uVector  a = ", a
            print "uVector  b = ", b
            print "cross(a,b) =", axis
            print "theta      =", theta
            print "baserise   =", self.dna.getBaseRise()
            print "seqLength  =", self._getSequenceLength()
            print "scalar     =", scalar
            print "rawOffset  =", rawOffset
        
        if theta == 0.0 or theta == 180.0:
            axis = V(0, 1, 0)
            # print "Now cross(a,b) =", axis
            
        rot =  (pi / 180.0) * theta  # Convert to radians
        qrot = Q(axis, rot) # Quat for rotation delta.
        
        # Move and rotate the base chunks into final orientation.
        for m in rawDnaGroup.members:
            m.move(qrot.rot(m.center) - m.center + rawOffset + pt1)
            m.rot(qrot)

    def _getSequenceLength(self):
        """
        Returns the number of bases of the current sequence
        (from the Property Manager).
        """
        (sequence, allKnown) = self._getSequence()
        return len(sequence)
    
    def _getSequence( self, 
                      reverse = False, 
                      complement = False, 
                      resolve_random = False, 
                      cdict = {} ):
        """
        Get the current DNA sequence from the Property Manager.
        
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
        
        sequence = ''
        allKnown = True
        
        cdict    =  basesDict
        
        # The current sequence (or number of bases) in the PropMgr. Mark [070405]
        # (Note: I think this code implies that it can no longer be a number of bases. [bruce 070518 comment])
        currentSequence  =  str(self.getPlainSequence(inOmitSymbols = True)) # :jbirac: 20070629

        for ch in currentSequence:
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
                        raise KeyError("DNA dictionary doesn't have a 'Complement' key for '%r'." % ch)
                        ch = 'N'
            elif ch in self.validSymbols: #'\ \t\r\n':
                ch  =  ''
            else:              
                allKnown  =  False

            sequence += ch

        if reverse: 
            sequence = self.getReverseSequence(sequence)
        
        return (sequence, allKnown)
    
    def getReverseSequence(self, inSequence):
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

    def _makeDuplexChunk(self, dnaGroup):
        """
        Returns a single DNA chunk given a dnaGroup containing multiple strand chunks.
        
        @param dnaGroup: The group object containing the DNA strand chunks.
        @type  dnaGroup: L{Group}
        
        @return: The DNA chunk.
        @rtype:  L{molecule} (i.e. a chunk)
        """
        
        if not isinstance(dnaGroup.members[0], molecule):
            env.history.message(redmsg(
                "Internal error in creating a single chunk DNA"))
            return
        
        for m in dnaGroup.members[1:]:
            if isinstance(m, molecule):
                dnaGroup.members[0].merge(m)
                
        # Rename the merged chunk 
        dnaGroup.members[0].name = dnaGroup.name
        
        dnaChunk = dnaGroup.members[0]
        dnaGroup.ungroup()
        
        return dnaChunk
       
    def _makeAtomisticSingleChunkStrands(self, rawDnaGroup):
        """
        Returns a group containing the two strand chunks I{StrandA},
        and I{StrandB} of the current DNA sequence.
        
        @param rawDnaGroup: The raw Dna group which contains two groups
                            "StrandA" and "StrandB". These subgroups contain
                            the individual base chunks for each strand.
        @type  rawDnaGroup: L{Group}
        
        @return: The merged DNA group that contains the two strand chunks
                 "StrandA" and "StrandB".
        @rtype:  L{Group}
        """
        
        counter = 0
        
        # Merge all the chunks in the two subgroups of rawDnaGroup into two
        # strand chunks "StrandA" and "StrandB".
        for subgroup in rawDnaGroup.members:
            if isinstance(subgroup, Group):
                # This is for a double stranded DNA.
                mol = subgroup.members[0]
                for m in subgroup.members[1:]:                           
                    mol.merge(m)
                
                # Ungroup and rename chunk
                subgroup.ungroup()
                mol.name = self._getStrandName(counter)
            else:
                print "Bug in merging DNA strand bases into a single chunk." 
                return None
            
            counter +=1
            
        return rawDnaGroup
    
    def _getStrandName(self, strandNumber, numberOfBasesToDisplay = 0):
        """
        Returns a strand name given a strand number and the number of base
        letters to display in the name.
        
        @param strandNumber: The strand number, where:
                             - 0 = Strand A
                             - 1 = Strand B
                             - 2 = Axis (PAM5 only)
        @type  strandNumber: int
        
        @param numberOfBasesToDisplay: The number of base letters to display
                                       in the name. The default is 0.
        @type  numberOfBasesToDisplay: int
        
        @return: The strand name. (i.e. "StrandA:ATCG...")
        @rtype:  str
        """
        assert (strandNumber >= 0) and (strandNumber <= 2), \
               "strandNumber is %d. It can only be 0, 1, or 2." % strandNumber
        
        if strandNumber == 0:
            (sequence, allKnown) = self._getSequence()
            strandName = 'StrandA'
        elif strandNumber == 1:
            (sequence, allKnown) = self._getSequence(complement=True)
            strandName = 'StrandB'
        else:
            strandName = "Axis"
            
        if numberOfBasesToDisplay: 
            # Add strand letters to MT node name.
            numberOfLetters = min(len(sequence), numberOfBasesToDisplay)
            strandName += ":" + sequence[0:numberOfLetters]
        
            if len(sequence) > numberOfBasesToDisplay:
                # Add "..." if the sequence is longer than <numberOfBasesToDisplay>.
                strandName += '...'
                          
        return strandName
    
    def _makePAM5StrandAndAxisChunks(self, rawDnaGroup):
        """
        Returns a group containing the three strand chunks I{StrandA},
        I{StrandB} and I{Axis} of the current DNA sequence.
        
        @param rawDnaGroup: The raw Dna group which contains the 
                            base-pair chunks representing the sequence.
        @type  grawDnaGrouprp: L{Group}
        
        @return: The new DNA group that contains the three strand chunks
                 I{StrandA}, I{StrandB} and I{Axis}.
        @rtype:  L{Group}
        """
        
        startBasePair = rawDnaGroup.members[0]
        
        if not isinstance(startBasePair, molecule):
            env.history.message(redmsg(
                "Internal error in creating a chunks for strands and axis"
                ))
            return rawDnaGroup
        
        # <startAtoms> are the PAM5 atoms that start StrandA, StrandB and Axis.
        # If the sequence is a single base, then we have 2 Pe atoms (one for 
        # strandA and one for StrandB.
        if self._getSequenceLength() == 1:
            startAtoms = ("Pe", "Ae")
        else:
            startAtoms = ("Pe", "Sh", "Ae")
        
        Pe_count = 0
        tempList      =  []
        
        for atm in startBasePair.atoms.values():  
            if atm.element.symbol in startAtoms:                        
                tempList.append(atm)
                atomList = self.win.assy.getConnectedAtoms(tempList)
                tempList = []
                if atm.element.symbol == "Pe":
                    Pe_count += 1
                    if Pe_count == 1:
                        strandAChunk = self._makeChunkFromAtomList(atomList)
                        strandAChunk.name = self._getStrandName(0)
                        first_Pe_found = True
                    else: # Pe_count == 2
                        # Only happens if the user entered a single letter
                        # for the sequence.
                        strandBChunk = self._makeChunkFromAtomList(atomList)
                        strandBChunk.name = self._getStrandName(1)
                elif atm.element.symbol == "Sh":
                    strandBChunk = self._makeChunkFromAtomList(atomList)
                    strandBChunk.name = self._getStrandName(1)
                elif atm.element.symbol == "Ae":
                    axisChunk = self._makeChunkFromAtomList(atomList)
                    axisChunk.name = self._getStrandName(2)
        
        # Place strand and axis chunks in this order: StrandA, StrandB, Axis.
        rawDnaGroup.addmember(strandAChunk)
        rawDnaGroup.addmember(strandBChunk)
        rawDnaGroup.addmember(axisChunk)
                
        self.win.win_update() # Needed?
                
        return rawDnaGroup
             
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
        
        newChunk = molecule(self.win.assy, gensym("Chunk"))
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

        return "Done creating a strand of %s." % (dna.form)
    

