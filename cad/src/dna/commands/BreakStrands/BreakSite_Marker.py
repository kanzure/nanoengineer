# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BreakSite_Marker object wraps the functionality of identifying
the potential break sites within a DnaStrand.

NOTE: This class has nothing to do with DnaMarker class.
    
@author: Ninad
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

History:
July 2008: created. 
"""
from model.bond_constants import find_bond
DEBUG_DRAW_SPHERES_AROUND_ATOMS_AT_BREAK_SITES = False
import time
class BreakSite_Marker(object):
    """
    BreakSite_Marker object wraps the functionality of identifying
    the potential break sites within a DnaStrand.
    @see: BreakStrands_GraphicsMode
    @NOTE: This class has nothing to do with DnaMarker class.
    """

    def __init__(self, graphicsMode):
        self.graphicsMode = graphicsMode
        self.command = self.graphicsMode.command
        self.win = self.graphicsMode.win
        self.glpane = self.graphicsMode.glpane

        self._breakSitesDict = {}       
        self._breakSites_atomPairs_dict = {}
        self._startAtoms_dict = {}
        self._endAtoms_dict = {}
        
    def getBreakSitesDict(self):
        return self._breakSitesDict
    
    def getStartAtomsDict(self):
        return self._startAtoms_dict
    
    def getEndAtomsDict(self):
        return self._endAtoms_dict
    
    def getBreakSites_atomPairsDict(self):        
        return self._breakSites_atomPairs_dict
    
    def full_update(self):
        self._startAtoms_dict = {}
        self._endAtoms_dict = {}
        self.update()
        
    def update(self):
        self.clearDictionaries()       
        self._updateBreakSites()
    
    def clearDictionaries(self):
        self._breakSitesDict = {}
        self._breakSites_atomPairs_dict = {}
        ##self._startAtoms_dict = {}
        ##self._endAtoms_dict = {}
        
    def updateStartAtomsDict(self, atm):
        strand = atm.getDnaStrand() 
        
        if strand in self.command.getStrandList():
            self._startAtoms_dict[strand] = atm
            self._updateBreakSitesForStrand(strand)
            
    def updateEndAtomsDict(self, atm):
        strand = atm.getStrand() 
        if strand in self.command.getStrandList():
            self._endAtoms_dict[strand] = atm
            self._updateBreakSitesForStrand(strand)
            
    def _updateBreakSites(self):  
        ##print "***BEFORE updating the breaksites:", time.clock()
        strands_to_be_searched = self.command.getStrandList()  
        
        basesBeforeNextBreak = self.command.getNumberOfBasesBeforeNextBreak()  
        if basesBeforeNextBreak == 0:
            return #not possible
        
        for strand in strands_to_be_searched:
            self._updateBreakSitesForStrand(strand)
        
        ##print "***AFTER updating the breaksites:", time.clock()
            
    def _updateBreakSitesForStrand(self, strand):
        """
        """       
        basesBeforeNextBreak = self.command.getNumberOfBasesBeforeNextBreak()         
        rawStrandAtomList = strand.get_strand_atoms_in_bond_direction()
        strandAtomList = filter(lambda atm: not atm.is_singlet(), 
                                rawStrandAtomList)             
        
        if len(strandAtomList) < 3:
            return #skip this strand. It doesn't have enough bases
        
        if len(strandAtomList) < basesBeforeNextBreak:
            return
        
        #First create a dict to store the information about the bond 
        #that will be stored in the atom pairs. 
        atomPair_dict = {}
        
        # =============================================
        #If start and end atoms are specified between which the break sites 
        #need to be computed --
        startAtom = None
        endAtom = None
        startAtomIndex = 0
        endAtomIndex = len(strandAtomList) - 1

        if self._startAtoms_dict.has_key(strand):                   
            startAtom = self._startAtoms_dict[strand]
            #@@BUG METHOD NOT FINISHED YET
            #-- sometimes it gives error x not in list after breaking 
            #a strand etc. CHECK this -- Ninad 2008-07-02
            startAtomIndex = strandAtomList.index(startAtom)
                            
        if self._endAtoms_dict.has_key(strand):                
            endAtom = self._endAtoms_dict.index(endAtom)
            
            endAtomIndex = strandAtomList.index(endAtom)                
        
        if startAtom and endAtom:
            if startAtomIndex > endAtomIndex:
                strandAtomList.reverse()
                startAtomIndex = strandAtomList.index(startAtom)
                endAtomIndex = strandAtomList.index(endAtom)
                
        # =============================================
        i = 1      
        listLength = len(strandAtomList[startAtomIndex: endAtomIndex + 1])
        
        for atm in strandAtomList[startAtomIndex: endAtomIndex + 1]:
            
            #Add '1' to the following actual atom index within the list. 
            #This is done because the start atom itself will be counted 
            #as '1st base atom to start with -- INCLUDING THAT ATOM when we
            #mark the break sites. 
            #Example: User want to create a break after every 1 base. 
            #So, if we start at 5' end, the 5' end atom will be considred 
            #the first base, and a bond between the 5'end atom and the next 
            #strand atom will be a 'break site'. Then the next break site 
            #will be the bond '1 base after that strand atom and like that

            idx = strandAtomList.index(atm)
        
            if (i%basesBeforeNextBreak) == 0 and i < listLength:
                next_atom = strandAtomList[idx + 1]
                bond = find_bond(atm, next_atom)
                
                if not atomPair_dict.has_key(bond):
                    atomPair_dict[bond] = (atm, next_atom)
                    
                if DEBUG_DRAW_SPHERES_AROUND_ATOMS_AT_BREAK_SITES:
                    for a in (atm, next_atom):                        
                        if not self._breakSitesDict.has_key(id(a)):
                            self._breakSitesDict[id(a)] = a
                        
            i += 1
            
        self._breakSites_atomPairs_dict[strand] = atomPair_dict
            
    def _updateBreakSitesForStrand_ORIG(self, strand):
        """
        """
        basesBeforeNextBreak = self.command.getNumberOfBasesBeforeNextBreak() 
        
        rawStrandAtomList = strand.get_strand_atoms_in_bond_direction()
        strandAtomList = filter(lambda atm: not atm.is_singlet(), 
                                rawStrandAtomList)             
        
        if len(strandAtomList) < 3:
            return #skip this strand. It doesn't have enough bases
        
        if len(strandAtomList) < basesBeforeNextBreak:
            return
        # =============================================
        #If start and end atoms are specified between which the break sites 
        #need to be computed --
        startAtom = None
        endAtom = None
        startAtomIndex = 0
        endAtomIndex = len(strandAtomList) - 1

        if self._startAtoms_dict.has_key(strand):                   
            startAtom = self._startAtoms_dict[strand]
            #@@BUG METHOD NOT FINISHED YET
            #-- sometimes it gives error x not in list after breaking 
            #a strand etc. CHECK this -- Ninad 2008-07-02
            startAtomIndex = strandAtomList.index(startAtom)
                            
        if self._endAtoms_dict.has_key(strand):                
            endAtom = self._endAtoms_dict.index(endAtom)
            
            endAtomIndex = strandAtomList.index(endAtom)                
        
        if startAtom and endAtom:
            if startAtomIndex > endAtomIndex:
                strandAtomList.reverse()
                startAtomIndex = strandAtomList.index(startAtom)
                endAtomIndex = strandAtomList.index(endAtom)
                
        # =============================================
        i = 1      
        listLength = len(strandAtomList[startAtomIndex: endAtomIndex + 1])
        
        for atm in strandAtomList[startAtomIndex: endAtomIndex + 1]:
            
            #Add '1' to the following actual atom index within the list. 
            #This is done because the start atom itself will be counted 
            #as '1st base atom to start with -- INCLUDING THAT ATOM when we
            #mark the break sites. 
            #Example: User want to create a break after every 1 base. 
            #So, if we start at 5' end, the 5' end atom will be considred 
            #the first base, and a bond between the 5'end atom and the next 
            #strand atom will be a 'break site'. Then the next break site 
            #will be the bond '1 base after that strand atom and like that
            ##idx = strandAtomList.index(atm) + 1    
            
            idx = strandAtomList.index(atm)
            
            ##if (idx%basesBeforeNextBreak) == 0 and idx < len(strandAtomList):
            if (i%basesBeforeNextBreak) == 0 and i < listLength:
                next_atom = strandAtomList[idx + 1]
                bond = find_bond(atm, next_atom)
                
                if not self._breakSites_atomPairs_dict.has_key(bond):
                    self._breakSites_atomPairs_dict[bond] = (atm, next_atom)
                
                for a in (atm, next_atom):                        
                    if not self._breakSitesDict.has_key(id(a)):
                        self._breakSitesDict[id(a)] = a
                        
            i += 1
