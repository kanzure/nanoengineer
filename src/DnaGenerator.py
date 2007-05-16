# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGenerator.py

$Id$

http://en.wikipedia.org/wiki/DNA
http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif
"""

__author__ = "Will"

import sys
import os
import env
import re
from math import atan2, sin, cos, pi
from PyQt4 import QtCore
from PyQt4.Qt import QWhatsThis, QDialog, SIGNAL, QTextCursor
from DnaGeneratorDialog import Ui_dna_dialog
from chem import Atom
from Utility import Group
from HistoryWidget import redmsg, orangemsg, greenmsg
from VQT import A, V, dot, vlen
from bonds import inferBonds, bond_atoms
from files_mmp import _readmmp
from GeneratorBaseClass import GeneratorBaseClass, PluginBug, UserError
from fusechunksMode import fusechunksBase
from platform import find_plugin_dir

atompat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
numberPattern = re.compile(r"^\s*(\d+)\s*$")

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    # env.history.message(orangemsg("The DNA generator is not available."))
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

DEBUG = False

class Dna:

    def make(self, assy, grp, sequence, doubleStrand, basesPerTurn, position,
             basenameA={'C': 'cytosine',
                        'G': 'guanine',
                        'A': 'adenine',
                        'T': 'thymine',
                        'N': 'unknown',
                        'Y': 'end1',
                        'Z': 'end2'},
             basenameB={'G': 'cytosine',
                        'C': 'guanine',
                        'T': 'adenine',
                        'A': 'thymine',
                        'N': 'unknown',
                        'Y': 'end1',
                        'Z': 'end2'}):
        baseList = [ ]
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
                #bruce 060714 don't call this the "3' strand" -- there is no such thing.
                # When we look up whether its bases are oriented in 3' to 5' or 5' to 3' direction,
                # maybe we can call it something like "3' to 5'" or "5' to 3'",
                # in order to indicate its direction.
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
            subgroup = Group("strand 2", grp.assy, None) #bruce 060714 don't call this the "5' strand" (more info above)
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
            self.postprocess(baseList) #bruce 070414
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
            return 'Y' + sequence[1:-1] + 'Z'
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

# DNA model type variables.
REDUCED_MODEL=0
ATOMISTIC_MODEL=1
BDNA=0
ZDNA=1

# GeneratorBaseClass must come BEFORE the dialog in the list of parents
class DnaGenerator(QDialog, GeneratorBaseClass, Ui_dna_dialog):

    cmd = greenmsg("Build DNA: ")
    sponsor_keyword = 'DNA'
    prefix = 'DNA-'   # used for gensym
    valid_base_letters = "NATCG" # Reduced model letters.

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        QDialog.__init__(self, win) # win is parent.  Fixes bug 1089.  Mark 051119.
        self.setupUi(self)
        GeneratorBaseClass.__init__(self, win)
        self._connect_or_disconnect_signals(connect=True)
        self._add_whats_this_text()
    
    def _connect_or_disconnect_signals(self, connect=True):
        """Connect this pmgr's widgets signals to their slots.
        """
        if connect:
            contype = self.connect
        else:
            contype = self.disconnect
        
        # Sponsor button
        contype(self.sponsor_btn,SIGNAL("clicked()"),
                self.open_sponsor_homepage)
        
        # Top Button Row (OK, Cancel, Preview, What's This).
        contype(self.done_btn,SIGNAL("clicked()"),
                self.ok_btn_clicked)
        contype(self.abort_btn,SIGNAL("clicked()"),
                self.abort_btn_clicked)
        contype(self.preview_btn,SIGNAL("clicked()"),
                self.preview_btn_clicked)
        contype(self.whatsthis_btn,SIGNAL("clicked()"),
                self.enter_WhatsThisMode)
        
        # Groupbox Title Buttons.
        contype(self.pmMsgGroupBoxBtn,SIGNAL("clicked()"),
                self.toggle_pmMsgGroupBox)
        contype(self.pmGroupBoxBtn1,SIGNAL("clicked()"),
                self.toggle_pmGroupBox1)
        contype(self.pmGroupBoxBtn2, SIGNAL("clicked()"), 
                self.toggle_pmGroupBox2) 
        contype(self.pmGroupBoxBtn3,SIGNAL("clicked()"),
                self.toggle_pmGroupBox3)
       
        # Groupbox1.
        contype(self.dnaConformation_combox,
                SIGNAL("currentIndexChanged(int)"),
                self.dnaConformation_combox_changed)
        
        # Groupbox2.
        contype(self.model_combox,SIGNAL("currentIndexChanged(int)"),
                self.model_combox_changed)
        
        # Groupbox3.
        contype(self.length_spinbox,SIGNAL("valueChanged(int)"),
                self.length_changed)
        contype(self.base_textedit,SIGNAL("textChanged()"),
                self.sequence_changed)
        contype(self.base_textedit,SIGNAL("cursorPositionChanged()"),
                self.cursorpos_changed)
        contype(self.complement_btn,SIGNAL("clicked()"),
                self.complement_btn_clicked)
        contype(self.reverse_btn,SIGNAL("clicked()"),
                self.reverse_btn_clicked)
    
    def _add_whats_this_text(self):
        """What's This text for all widgets the the DNA generator's property manager.
        """
        
        self.dnaConformation_combox.setWhatsThis("""<b>Conformation</b>
        <p>There are three DNA geometries, A-DNA, B-DNA,
        and Z-DNA. Only B-DNA and Z-DNA are currently supported.</p>""")
        
        self.strandType_combox.setWhatsThis("""<b>Strand Type</b>
        <p>DNA strands can be single or double.</p>""")
        
        self.base_textedit.setWhatsThis("""<b>Strand Sequence</b>
        <p>Type in the strand sequence you want to generate here (5' => 3')
        </p>""")
        
        self.complement_btn.setWhatsThis("""<b>Complement</b>
        <p>Change the current strand sequence to the complement strand 
        sequence.</p>""")
        
        self.reverse_btn.setWhatsThis("""<b>Reverse</b>
        <p>Reverse the strand sequence that has been entered.</p>""")
        
        self.model_combox.setWhatsThis("""<b>Model</b>
        <p>Determines the type of DNA model that is generated.</p> """)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters(self):
        if not basepath_ok:
            raise PluginBug("The cad/plugins/DNA directory is missing.")
        (seq, allKnown) = self._get_sequence()
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
        if (representation == 'Atomistic'):
            representation = 'Atom'
            chunkOption = str(self.dnaChunkOptions_combox.currentText())
            
        assert representation in ('Atom', 'BasePseudoAtom')
        if (representation == 'Atom' and not allKnown):
            raise UserError("Cannot use unknown bases (N) in Atomistic representation")

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

    def _get_sequence(self, reverse=False, complement=False,
                     cdict={'C':'G', 'G':'C', 'A':'T', 'T':'A', 'N':'N'}):
        seq = ''
        allKnown = True
        # The current base sequence (or number of bases) in the PropMgr. Mark [070405]
        pm_seq = str(self.base_textedit.toPlainText()).upper()
        #print "pm_seq =", pm_seq
        #match = numberPattern.match(pm_seq)
        #if (match):
        #    return(match.group(1), False)
        for ch in pm_seq:
            if ch in 'CGATN':
                if ch == 'N':
                    allKnown = False
                if complement:
                    ch = cdict[ch]
                seq += ch
            elif ch in '\ \t\r\n':
                pass
            else:
                raise UserError('Bogus DNA base: ' + ch + ' (should be C, G, A, or T)')
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
    # Any special controls for this kind of structure
    
    # Methods for handling the Strand Sequence groupbox. ###############
    
    def length_changed(self, length):
        """Slot for the length spinbox.
        """
        #print "New length = ", length, ", Current length =", self.get_sequence_length()
        if length < 0: return # Should never happen.
        
        if length < self.get_sequence_length():
            # If length is less than the previous length, simply truncate the current sequence to "length".
            if length < 0: return # Should never happen.
            for p in range(self.get_sequence_length()-length):
                self.base_textedit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
            self.base_textedit.cut()
            return
        else:
            # If length has increased, add the correct number of base letters to the current strand sequence.
            numNewBases = length - self.get_sequence_length()
            # print "Number of new bases = ", numNewBases
            bases = ''
            base = str(self.newBaseOptions_combox.currentText()) # Current base selected in combobox.
            bases = base[0] * numNewBases
            self.base_textedit.insertPlainText(bases)
        
    def update_length(self):
        """Update the Length spinbox; always the length of the strand sequence.
        """
        self.disconnect(self.length_spinbox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
        self.length_spinbox.setValue(self.get_sequence_length())
        self.connect(self.length_spinbox,SIGNAL("valueChanged(int)"),
                     self.length_changed)
    
    def sequence_changed(self):       
        """Slot for the strand sequence textedit widget.
        Make sure only A, T, C or G (and N for reduced model) are allowed.
        """
        
        pm_seq = str(self.base_textedit.toPlainText()).upper()
        curpos = self.get_cursorpos()
        
        if curpos == 0:
            # User deleted all text in sequence widget.
            self.update_length()
            return
        
        ch = pm_seq[curpos-1] # This is the character the user typed.
        #print "Cursor pos=", curpos, ", Char typed was: ", ch
        
        # Disconnect while we edit the sequence.
        self.disconnect(self.base_textedit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        # Delete the character the user just typed in. We'll replace it in upper case (if legal) or not (if not legal).
        self.base_textedit.moveCursor(QTextCursor.Left, QTextCursor.KeepAnchor) # Move the cursor one position to the left. 
        self.base_textedit.cut() # Delete (cut) single character user typed in.

        if ch in self.valid_base_letters: # Remove "N: if atomistic model is selected. (later)
            self.base_textedit.insertPlainText(ch.upper()) # Change to upper case.
        
        self.connect(self.base_textedit,SIGNAL("textChanged()"),
                     self.sequence_changed)
        
        self.update_length() # Update Length spinbox.
    
    def get_sequence_length(self):
        """Returns the number of characters in the strand sequence textedit widget.
        """
        #print "get_sequence_length(): strand length =", len(self.base_textedit.toPlainText())   
        return len(self.base_textedit.toPlainText())
        
    def get_cursorpos(self):
        """Returns the cursor position in the strand sequence textedit widget.
        """
        cursor = self.base_textedit.textCursor()
        return cursor.position()

    def cursorpos_changed(self):
        """Slot called when the cursor position changes.
        """
        # Useful for debugging. mark 2007-05-09.
        # print "cursorpos_changed(): Cursor at position ", self.get_cursorpos()
        return
    
    def dnaConformation_combox_changed(self, idx):
        """Slot for the Conformation combobox.
        """
        self.basesPerTurn_combox.clear()
        
        if idx == BDNA:
            self.basesPerTurn_combox.insertItem(0, "10.0")
            self.basesPerTurn_combox.insertItem(1, "10.5")
            self.basesPerTurn_combox.insertItem(2, "10.67")
        
            #10.5 is the default value for Bases per turn. 
            #So set the current index to 1
            self.basesPerTurn_combox.setCurrentIndex(1) 
        
        elif idx == ZDNA:
            self.basesPerTurn_combox.insertItem(0, "12.0")
            
        else:
            print "dnaConformation_combox_changed(): Error - unknown DNA conformation. Index =", idx
            return
        
    def model_combox_changed(self, idx):
        """Slot for the Model combobox.
        """
        
        seqlen = self.get_sequence_length()
        self.base_textedit.clear()
        
        self.disconnect(self.dnaConformation_combox,SIGNAL("currentIndexChanged(int)"),
                     self.dnaConformation_combox_changed)
        
        self.newBaseOptions_combox.clear() # Generates signal!
        self.dnaConformation_combox.clear() # Generates signal!
        self.strandType_combox.clear() # Generates signal!
        
        if idx == REDUCED_MODEL:
            self.newBaseOptions_combox.addItem("N (undefined)")
            self.newBaseOptions_combox.addItem("A")
            self.newBaseOptions_combox.addItem("T")  
            self.newBaseOptions_combox.addItem("C")
            self.newBaseOptions_combox.addItem("G") 
            
            seq = "N" * seqlen
            self.base_textedit.insertPlainText(seq)
            self.valid_base_letters = "NATCG"
            
            self.dnaConformation_combox.addItem("B-DNA")
            
            self.strandType_combox.addItem("Double")
            
        elif idx == ATOMISTIC_MODEL:
            self.newBaseOptions_combox.addItem("A")
            self.newBaseOptions_combox.addItem("T")  
            self.newBaseOptions_combox.addItem("C")
            self.newBaseOptions_combox.addItem("G")
            self.valid_base_letters = "ATCG"
            
            self.dnaConformation_combox.addItem("B-DNA")
            self.dnaConformation_combox.addItem("Z-DNA")
            
            self.strandType_combox.addItem("Double")
            self.strandType_combox.addItem("Single")
            
        else:
            print "model_combox_changed(): Error - unknown model representation. Index =", idx
        
        self.connect(self.dnaConformation_combox,SIGNAL("currentIndexChanged(int)"),
                     self.dnaConformation_combox_changed)

    ############################
        
    def complement_btn_clicked(self):
        """Slot for the Complement button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(complement=True)
            self.base_textedit.setPlainText(seq)
        self.handlePluginExceptions(thunk)

    def reverse_btn_clicked(self):
        """Slot for the Reverse button.
        """
        def thunk():
            (seq, allKnown) = self._get_sequence(reverse=True)
            self.base_textedit.setPlainText(seq)
        self.handlePluginExceptions(thunk)

    def toggle_pmMsgGroupBox(self): # Message groupbox
        self.toggle_groupbox(self.pmMsgGroupBoxBtn, 
                             self.pmMsgTextEdit)
        
    def toggle_pmGroupBox1(self): # DNA Parameters groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn1, 
                             self.dnaConformation_lbl, self.dnaConformation_combox,
                             self.strandType_lbl, self.strandType_combox,
                             self.basesPerTurn_lbl, self.basesPerTurn_combox)

    def toggle_pmGroupBox2(self): # Represenation groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn2, 
                             self.model_combox_lbl, self.model_combox,
                             self.dnaChunkOptions_lbl, self.dnaChunkOptions_combox )
    
    def toggle_pmGroupBox3(self): # Strand Sequence groupbox
        self.toggle_groupbox(self.pmGroupBoxBtn3, 
                             self.length_lbl, self.length_spinbox,
                             self.newBaseOptions_lbl, self.newBaseOptions_combox,
                             self.base_textedit,
                             self.complement_btn, self.reverse_btn)