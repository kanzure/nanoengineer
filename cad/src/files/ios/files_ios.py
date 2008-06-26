"""
files_ios.py - provides functions to export a NE-1 model into IOS format as well
as import optimized sequences into NE-1

@version: 
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: This is only applicable to DNA/ RNA models (so is IOS)
"""
from xml.dom.minidom import DOMImplementation
from xml.dom import EMPTY_NAMESPACE, XML_NAMESPACE, XMLNS_NAMESPACE
from dna.model.DnaLadderRailChunk import DnaStrandChunk
from dna.model.DnaLadder import DnaLadder
from printFunc import PrettyPrint
import os, string
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError
from dna.model.DnaStrand import DnaStrand
from PyQt4.Qt import QMessageBox

def getAllLadders(assy):
    """
    get all the DNA ladders from the screen to figure out strand pairing info
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    @return: a list of DNA ladders
    """
    dnaSegmentList = []
         
    def func(node):
        if isinstance(node, assy.DnaSegment):
            dnaSegmentList.append(node)
            
    assy.part.topnode.apply2all(func)
    #get all ladders for each segment
    dnaLadderList = []
    for seg in dnaSegmentList:
        laddersWithinSegmentList = []
        laddersWithinSegmentList = seg.getDnaLadders()
        for ladder in laddersWithinSegmentList:
            dnaLadderList.append(ladder)
            
    return dnaLadderList

def getAllDnaStrands(assy):
    """
    get all the DNA strands from the screen to figure out strand info
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    @return: a list of DNA strands
    """
    dnaStrandList = []
         
    def func(node):
        if isinstance(node, assy.DnaStrand):
            dnaStrandList.append(node)
                    
    assy.part.topnode.apply2all(func)
        
    return dnaStrandList

def createTokenLibrary(doc,elemDoc):
    
    """
    create Token library in the IOS file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    
    """
   
    elemTokenLibrary = doc.createElement('TokenLibrary')
    elemAtomicToken = doc.createElement('AtomicTokens')
    #create element name and child text from key value pair
    elemAtomicTokenA = doc.createElement('AtomicToken')
    elemAtomicTokenA.appendChild(doc.createTextNode('A'))
    elemAtomicToken.appendChild(elemAtomicTokenA) 
    
    elemAtomicTokenC = doc.createElement('AtomicToken')
    elemAtomicTokenC.appendChild(doc.createTextNode('C'))
    elemAtomicToken.appendChild(elemAtomicTokenC) 

    elemAtomicTokenG = doc.createElement('AtomicToken')
    elemAtomicTokenG.appendChild(doc.createTextNode('G'))
    elemAtomicToken.appendChild(elemAtomicTokenG) 

    elemAtomicTokenT = doc.createElement('AtomicToken')
    elemAtomicTokenT.appendChild(doc.createTextNode('T'))
    elemAtomicToken.appendChild(elemAtomicTokenT) 

    elemTokenLibrary.appendChild(elemAtomicToken)

    # create wild card token
    elemWildcardTokens = doc.createElement('WildcardTokens')
    elemWildcardToken = doc.createElement('WildcardToken')
    
    elemTokenT = doc.createElement('Token')
    elemTokenT.appendChild(doc.createTextNode('N'))
    elemWildcardToken.appendChild(elemTokenT)
    
    elemAtomicEquivalentA = doc.createElement('AtomicEquivalent')
    elemAtomicEquivalentA.appendChild(doc.createTextNode('A'))
    elemWildcardToken.appendChild(elemAtomicEquivalentA)
    
    elemAtomicEquivalentT = doc.createElement('AtomicEquivalent')
    elemAtomicEquivalentT.appendChild(doc.createTextNode('T'))
    elemWildcardToken.appendChild(elemAtomicEquivalentT)
    
    elemAtomicEquivalentG = doc.createElement('AtomicEquivalent')
    elemAtomicEquivalentG.appendChild(doc.createTextNode('G'))
    elemWildcardToken.appendChild(elemAtomicEquivalentG)
    
    elemAtomicEquivalentC = doc.createElement('AtomicEquivalent')
    elemAtomicEquivalentC.appendChild(doc.createTextNode('C'))
    elemWildcardToken.appendChild(elemAtomicEquivalentC)
    
    elemWildcardTokens.appendChild(elemWildcardToken)
    elemTokenLibrary.appendChild(elemWildcardTokens)
    
    #append token library to the iso file
    elemDoc.appendChild(elemTokenLibrary)
    return
    
def createMappingLibrary(doc,elemDoc):
    """
    create mapping library section for the NE-1 model file in the ios file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    
    """
    
    elemMappingLibrary = doc.createElement('MappingLibrary')
    elemMapping = doc.createElement('Mapping')
    elemMapping.setAttribute('id', 'complement')
    # A to T
    elemTokenT = doc.createElement('Token')
    elemFrom = doc.createElement('From')
    elemFrom.appendChild(doc.createTextNode('A'))
    elemTokenT.appendChild(elemFrom)

    elemTo = doc.createElement('To')
    elemTo.appendChild(doc.createTextNode('T'))
    elemTokenT.appendChild(elemTo)
    elemMapping.appendChild(elemTokenT)

    # T to A
    elemTokenT = doc.createElement('Token')
    elemFrom = doc.createElement('From')
    elemFrom.appendChild(doc.createTextNode('T'))
    elemTokenT.appendChild(elemFrom)

    elemTo = doc.createElement('To')
    elemTo.appendChild(doc.createTextNode('A'))
    elemTokenT.appendChild(elemTo)
    elemMapping.appendChild(elemTokenT)

    # C to G
    elemTokenT = doc.createElement('Token')
    elemFrom = doc.createElement('From')
    elemFrom.appendChild(doc.createTextNode('C'))
    elemTokenT.appendChild(elemFrom)

    elemTo = doc.createElement('To')
    elemTo.appendChild(doc.createTextNode('G'))
    elemTokenT.appendChild(elemTo)
    elemMapping.appendChild(elemTokenT)

    # G to C
    elemTokenT = doc.createElement('Token')
    elemFrom = doc.createElement('From')
    elemFrom.appendChild(doc.createTextNode('G'))
    elemTokenT.appendChild(elemFrom)

    elemTo = doc.createElement('To')
    elemTo.appendChild(doc.createTextNode('C'))
    elemTokenT.appendChild(elemTo)
    elemMapping.appendChild(elemTokenT)
    
    elemMappingLibrary.appendChild(elemMapping)
    elemDoc.appendChild(elemMappingLibrary)

    return

def railImplementation(assy):
    strandList = getAllDnaStrands(assy)
    for strand in strandList:
        strandID = strand.name
        
        #Note: Ninad needs to look at this, what do the indices in 
        #wholechain_baseindex_range_for_rail(rail) for each rail of the wholechain
        #coresspond to? When you sort them, and arrange the corresponding basestrings
        #accordinly, it does not yield the original sequence. The error is, however
        #not obvious when a strand chunk base pairs with more than two other chunks
        #from one or more strands.
        #Also rails and chunks cannot be used since they are not in the same order
        #as the sequence string
        
        print "Strand Name =", strand.name
        strand_wholechain = strand.get_strand_wholechain()
        baseStringListInOrder = []
        indexTupleListInOrder = []
        if strand_wholechain:
            for rail in strand_wholechain.rails():
                #print "Rail baseatoms", rail.baseatoms
                baseList = []
                for a in rail.baseatoms:
                    bases = a.getDnaBaseName()
                    aComp = a.get_strand_atom_mate()
                    
                    if bases == 'X':
                        bases = 'N'
                      
                    baseList.append(bases)
                baseIndices = strand_wholechain.wholechain_baseindex_range_for_rail(rail)
                
                baseString = ''.join(baseList)
                
                
                if baseIndices[1] < baseIndices[0]:
                    baseStringFinal = baseString[::-1]
                    indexTuple = (baseIndices[1], baseIndices[0])
                else:
                    baseStringFinal = baseString
                    indexTuple = (baseIndices[0], baseIndices[1])
                #print "BaseString =", baseStringFinal
                #print "Index Tuple= ", indexTuple
                #for the first element
                if len(baseStringListInOrder) == 0:
                    baseStringListInOrder.append(baseStringFinal)
                    indexTupleListInOrder.append(indexTuple)
                else:
                    #locate place in the list where to insert basestring and index 
                    #tuple
                    for i in range(len(indexTupleListInOrder)):
                        if i == 0 and indexTuple[1] < indexTupleListInOrder[i][0]:
                            #insert this string at index 0
                            indexTupleListInOrder.insert(i, indexTuple)
                            baseStringListInOrder.insert(i,baseStringFinal)
                            
                        elif indexTuple[0] > indexTupleListInOrder[i-1][1] and indexTuple[1] < indexTupleListInOrder[i][0]:
                            indexTupleListInOrder.insert(i, indexTuple)
                            baseStringListInOrder.insert(i,baseStringFinal)
                        else:
                            continue
        print "BaseString List=", baseStringListInOrder
        print "Index Tuple List= ", indexTupleListInOrder
                
        print "Strand sequence= ", strand.getStrandSequence()
    return



#test Implementation: UM 20080624

def getAtomList(strand):
    #for each strand read the whole chain
    rawAtomList = []
    for c in strand.members:
        if isinstance(c, DnaStrandChunk):
            rawAtomList.extend(c.atoms.itervalues())
            
    atomList = []           
    for atm in strand.get_strand_atoms_in_bond_direction(rawAtomList):
        if not atm.is_singlet():
            atomList.append(atm)
    return atomList            
    
def checkIfChunkExists(justChunks, name, startIndex, endIndex):
    #see if chunk already exists, then no need to insert it
    #to do so we have to scan the justChunks list and see if
    #any of the startIndex and endIndex match with that of 
    # the current one as well as the parent strand
    #remember that the just chunks format is that of
    #(chunkName, parent_strand, baseString, startIndex, endIndex, complementary_chunk)
    #since justChunks is assigned after strandChunkInfoList
    #no need to check if justChunks is empty
    #This situation will never arise
     
    for ck in justChunks:
        i = justChunks.index(ck)
        #print "In Match found", name, startIndex, endIndex, justChunks[i][1], justChunks[i][3], justChunks[i][4]
        if (justChunks[i][1] == name) and (justChunks[i][3] == startIndex and justChunks[i][4] == endIndex):
            #chunk already exists, no need to insert anything
            
            return 1
    return 0

def createCompChunkInfoInJustChunks(compStrand, compChunkName, atomAtStart, atomAtEnd, chunkName):
    import sys
    compAtomList = getAtomList(compStrand)  
    try:
        indexOfStartAtom = compAtomList.index(atomAtStart)
    except ValueError:
        return None
    try:    
        indexOfEndAtom = compAtomList.index(atomAtEnd)
    except ValueError:
        return None    
    basestring = ''
    for i in range(indexOfStartAtom, indexOfEndAtom + 1):
        basestring = basestring + str(compAtomList[i].getDnaBaseName())
    chunkTuple = (compChunkName, compStrand.name, basestring, indexOfStartAtom, indexOfEndAtom, chunkName)    
    
    return chunkTuple

def createNewChunk(startIndex, atomIndex, strandList, strand, strandChunkInfoList, 
                   justChunks, singleTon, atomList, chunkCount, baseString, atomMatePreviousParent, atomMate):
    # atom mate's parent strand has changed, this marks the 
    # beginning of a new chunk 
    
    #store all the previous chunk data in a list
    endIndex = startIndex + len(baseString) - 1
    #endIndex = atomIndex - 1
    chunkStartIndex = startIndex
    chunkEndIndex = endIndex
                    
    idx = strandList.index(strand)
    matchFound = 0
    chunkName = strand.name + '_chunk' + str(chunkCount)                
    #no chunks on the list as yet
    if strandChunkInfoList[idx] == []:
        # this list has never been touched
        strandChunkInfoList[idx] = [chunkName]
    else:
        matchFound = checkIfChunkExists(justChunks, strand.name, startIndex, endIndex)
                        
        if matchFound == 0:
            #need to insert chunk in the strandChunkInfoList
            strandChunkInfoList[idx].append(chunkName)
            
    #now update justChunks if no previous record on this chunk 
    #found    
    if matchFound == 0:
        #need to create complementary chunk info as well
        if singleTon:
            #previous section was a ss no need to create comp chunk info
            compChunkName = ''
        else:    
            compChunkName = atomMatePreviousParent + '_chunk' + str(chunkCount)
        
        chunkTuple = (chunkName, strand.name, baseString, startIndex, endIndex, compChunkName)
        justChunks.append(chunkTuple)
                        
                
        #the following only needs to be done if the previous chunk was
        # a ds region
        if singleTon == 0:
            # since complementary strand info does not exist either in 
            # strandChunkInfoList or in justChunks, we are going to
            # create it now
                    
            #first obtain the index of the parent strand, this chunk
            #belongs to 
            atomMate = atomList[endIndex].get_strand_atom_mate()
            if atomMate is None:
                print "Atom Mate is none for a ds region: should not be in this loop"
                print strand.name, chunkName, startIndex, endIndex
                print strandChunkInfoList
                print justChunks
                return strandChunkInfoList, justChunks
            
            indexComp = strandList.index(atomMate.getDnaStrand())
            strandChunkInfoList[indexComp].append(compChunkName)
    
            #updating justChunks list now
            #for that purpose we already have chunkName (compChunkName
            # in this case) and parent_strand and compChunkName (chunk
            # name in this case)
            #we simply need to obtain the baseString, start Index and
            # end Index for this chunk
                        
            compStrand = strandList[indexComp]    
            #get the atomMates in start and end indices, start and 
            # end wrt to comp sequence and hence flipped
            atomMateAtEndIndex = atomList[startIndex].get_strand_atom_mate()
            atomMateAtStartIndex = atomList[endIndex].get_strand_atom_mate()
            #may need more parameters    
            chunkTuple = createCompChunkInfoInJustChunks(compStrand, compChunkName, 
                                                         atomMateAtStartIndex, atomMateAtEndIndex, 
                                                         chunkName)  
            #debugging info
            if chunkTuple is None:
                print "Chunk tuple for the complementary region for a valid ds region cannot be None: something wrong"
                print strand.name, compStrand.name, startIndex, endIndex, atomMateAtStartIndex, atomMateAtEndIndex
                
            if chunkTuple is not None:
                justChunks.append(chunkTuple)
                        
                
    return strandChunkInfoList, justChunks

def checkIfAtomMateAreAdjacent(atomMate, previousAtom, strandList):
    previousAtomMate = previousAtom.get_strand_atom_mate()
    atomMateParent = atomMate.getDnaStrand()
    index = strandList.index(atomMateParent)
    atomList = getAtomList(strandList[index])
    indexOfAtomMate = atomList.index(atomMate)
    indexOfPreviousAtomMate = atomList.index(previousAtomMate)
    if indexOfAtomMate == (indexOfPreviousAtomMate - 1):
        return True
    else:
        return False
    
def orderStrandChunkInfoList(strandChunkInfoList, justChunks):
    orderedList = []
    for i in range(0,len(strandChunkInfoList)):
        orderedList.append([])
    ChunkNameIndexDict = dict()
    for j in range(len(justChunks)):
        chunkName = justChunks[j][0]
        ChunkNameIndexDict[chunkName] = j
    for k in range(len(strandChunkInfoList)):
        #insert the first chunk
        orderedList[k].append(strandChunkInfoList[k][0])
        
        #sort the rest of the chunks by start base index
        for l in range(1,len(strandChunkInfoList[k])):
            currentChunk = strandChunkInfoList[k][l]
            startBaseIndexOfCurrentChunk = justChunks[ChunkNameIndexDict[currentChunk]][3]
            oldListLength = len(orderedList[k])
            for m in range(len(orderedList[k])):
                existingChunk = orderedList[k][m]
                startBaseIndexOfExistingChunk = justChunks[ChunkNameIndexDict[existingChunk]][3]
                if startBaseIndexOfCurrentChunk < startBaseIndexOfExistingChunk:
                    orderedList[k].insert(m, currentChunk)
                    break
            #if the element was not inserted, then put it at the end
            if oldListLength == len(orderedList[k]):
                orderedList[k].append(currentChunk)
                
    return orderedList, ChunkNameIndexDict

def createCompInfoDict(justChunks, chunkNameIndexDict):
    #instead of doing an explicit search we can explot the structure of justChunks
    #to not include copies of chunks and their complements in this dictionary
    compInfoDict = dict()
    for i in range(0,len(justChunks), 2):
        compInfoDict[justChunks[i][0]] = justChunks[i][5]
    return compInfoDict


def atomByAtomImplementation(assy):
    strandList = getAllDnaStrands(assy)
    #initialize list to contain chunk info:
    strandChunkInfoList = [[]]
    for i in range(1, len(strandList)):
        #each strand is a list of chunk names
        strandChunkInfoList.append([])
        
    #also initialize just chunks list
    #has chunkName, baseString, startIndex, endIndex, who is it paired with
    justChunks = []
    chunkCount = 1
    for strand in strandList:
        #Alorithgm: inspect the whole chain, atom by atom and whenever, the
        #parent strand of the atom mate changes, that indicates the beginning of
        # a new chunk.
        atomList = getAtomList(strand)
        atomMatePreviousParent = '' 
        startIndex = 0
        endIndex = 0
        chunkBaseString = ''
        atomMateNil = False
        #flag that indicates that atom does not have a mate, this is used
        # figure out end of singleTon state and assign chunks
        singleTon = 0
        
        for atm in atomList:   
            atomIndex = atomList.index(atm)  
            atomMate = atm.get_strand_atom_mate()
            if atomMate is None:
                #no need to worry about writing complementary chunk info
                atomMateNil = True
            else:
                atomMateNil = False       
            baseName = str(atm.getDnaBaseName())
            # processing ds region
            if atomMateNil == False:
                if atomIndex == 0:
                    #for the first atom, the atomMate's parent strand needs to be assigned
                    # and cannot be compared, for the remainder, it can be
                    atomMatePreviousParent = atomMate.getDnaStrand().name
                    chunkBaseString = baseName
                else:
                    if singleTon:
                        #marks the end of single stranded region
                        #need to write the single stranded region
                        strandChunkInfoList, justChunks = createNewChunk(startIndex, atomIndex, strandList, strand, 
                                                                         strandChunkInfoList, justChunks, singleTon, atomList, 
                                                                         chunkCount, chunkBaseString, atomMatePreviousParent,atomMate)
                        #reset all the parameters for the new chunk
                        atomMatePreviousParent = atomMate.getDnaStrand().name
                        chunkBaseString = baseName
                        startIndex = atomIndex
                        chunkCount = chunkCount + 1
                        #reset singleTon, since no longer dealing with ss 
                        singleTon = 0
                    else:    
                        #double strand case
                        atomMateCurrentParent = atomMate.getDnaStrand().name
                        # same chunk continuing
                        if atomMateCurrentParent == atomMatePreviousParent:
                            #there are two distinctive cases here:
                            #one when although the original strand is still base
                            #pairing with this second strand, it may or may not
                            # be contiguous and we need to check for that. In case
                            # it is not we need to call createNewChunk
                            contiguousAtomMates = checkIfAtomMateAreAdjacent(atomMate, atomList[atomIndex - 1], strandList)
                            if contiguousAtomMates:
                                chunkBaseString = chunkBaseString + baseName
                            else:
                                strandChunkInfoList, justChunks = createNewChunk(startIndex, atomIndex, strandList, strand, 
                                                                             strandChunkInfoList, justChunks, singleTon, atomList, 
                                                                             chunkCount, chunkBaseString, atomMatePreviousParent, atomMate)
                                #reset all the parameters for the new chunk
                                atomMatePreviousParent = atomMate.getDnaStrand().name
                                chunkBaseString = baseName
                                startIndex = atomIndex
                                chunkCount = chunkCount + 1
                        else:
                            
                            strandChunkInfoList, justChunks = createNewChunk(startIndex, atomIndex, strandList, strand, 
                                                                             strandChunkInfoList, justChunks, singleTon, atomList, 
                                                                             chunkCount, chunkBaseString, atomMatePreviousParent, atomMate)
                            #reset all the parameters for the new chunk
                            atomMatePreviousParent = atomMate.getDnaStrand().name
                            chunkBaseString = baseName
                            startIndex = atomIndex
                            chunkCount = chunkCount + 1
            else:
                #single stranded case
                # if the single stranded region comes after ds region
                if atomIndex == 0:
                    chunkBaseString = baseName
                    singleTon = 1
                else:
                    #this portion may come after a double stranded region if 
                    #the singleTon flag is not set
                    if singleTon:
                        #if it is set then its still within the ss region
                        #nothing to do, other than remember the base string
                        chunkBaseString = chunkBaseString + baseName
                    else:
                        #need to write the previous ds region
                        
                        strandChunkInfoList, justChunks = createNewChunk(startIndex, atomIndex, strandList, strand, 
                                                                         strandChunkInfoList, justChunks, singleTon, atomList, 
                                                                         chunkCount, chunkBaseString, atomMatePreviousParent, atomMate)
                        #reset all the parameters for the new chunk which is ss
                        #hence no atom mate info maintained
                        chunkBaseString = baseName
                        singleTon = 1
                        startIndex = atomIndex
                        chunkCount = chunkCount + 1
                        
        #final chunk written when we hit the end of the list            
        strandChunkInfoList, justChunks = createNewChunk(startIndex, atomIndex, strandList, strand, 
                                                     strandChunkInfoList, justChunks, singleTon, atomList, 
                                                     chunkCount, chunkBaseString, atomMatePreviousParent, atomMate) 
        chunkCount = chunkCount + 1
    """    
    print "Chunk list for each strand"                
    for strand in strandList:
        idx = strandList.index(strand)
        print strand.name, strandChunkInfoList[idx]
    """    
    print "Chunk information"    
    for i in range(len(justChunks)):    
        print justChunks[i]    
        
    #order strandChunkInfoList by startIndices of chunks; this list will be used
    #to write the chunks in order.
    orderedList, chunkNameIndexDict = orderStrandChunkInfoList(strandChunkInfoList, justChunks)
    print "Ordered Chunk List for strands"
    for strand in strandList:
        idx = strandList.index(strand)
        print strand.name, orderedList[idx]
    
    #print chunkNameIndexDict
    
    #with ChunkNameIndexDict, we can create complementary info dictionary
    compInfoDict = createCompInfoDict(justChunks, chunkNameIndexDict)
    print "Complementary info Dictionary"
    print compInfoDict
    return

def createStrands(doc,elemDoc, assy):
    """
    create strand section for the NE-1 model file in the ios file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    """
    
    #Run by Ninad/Bruce: UM 20080624
    #railImplementation(assy)
    atomByAtomImplementation(assy)
    
    """ 
    #old implementation for getting strand information
    #create strands
    elemStrands = doc.createElement('Strands')
    strandList = getAllDnaStrands(assy)
   
         
    for strand in strandList:
        strandID = strand.name
        elemStrand = doc.createElement('Strand')
        elemStrand.setAttribute('id',strandID)
        
        strandChunkList = strand.getStrandChunks()
        for chunk in strand.members:
            if isinstance(chunk, DnaStrandChunk):
                
        #for chunk in strandChunkList:
                chunkID = chunk.name
                atoms = chunk.get_baseatoms()
                baseList = []
                for a in atoms:
                    bases = a.getDnaBaseName()
                    aComp = a.get_strand_atom_mate()
                    compStrand = aComp.element.name
                    #print "Comp Strand =",compStrand
                    if bases == 'X':
                        bases = 'N'
                
                    baseList.append(bases)
                baseString = ''.join(baseList)
                elemRegion = doc.createElement('Region')
                elemRegion.setAttribute('id', chunkID)
                elemRegion.appendChild(doc.createTextNode(baseString))
                elemStrand.appendChild(elemRegion) 
        
        elemStrands.appendChild(elemStrand)
        
    elemDoc.appendChild(elemStrands)
    """
    return

def createConstraints(doc,elemDoc, assy):
    """
    create constraints section for the NE-1 model file in the ios file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    
    """
    # write the constraints
    elemConstraints = doc.createElement('Constraints')
    elemConstraintGroup = doc.createElement('ios:ConstraintGroup')
    elemConstraintGroup.setAttribute('strict', '1')
    
    ladderList = getAllLadders(assy)
    
    for ladder in ladderList:
        strandChunks = ladder.strand_chunks()
        if ladder.num_strands() == 2:
            chunk1 = strandChunks[0].name
            chunk2 = strandChunks[1].name
            elemMatch = doc.createElement('ios:Match')
            elemMatch.setAttribute('mapping', 'complement')
            elemConstraintRegion = doc.createElement('Region')
            elemConstraintRegion.setAttribute('ref',chunk1)
            elemMatch.appendChild(elemConstraintRegion)

            elemConstraintRegion = doc.createElement('Region')
            elemConstraintRegion.setAttribute('ref',chunk2)
            elemConstraintRegion.setAttribute('reverse', '1')
            elemMatch.appendChild(elemConstraintRegion)  
            elemConstraintGroup.appendChild(elemMatch) 
            
        else:
            chunk1 = strandChunks[0].name
            
            
    elemConstraints.appendChild(elemConstraintGroup)
    elemDoc.appendChild(elemConstraints) 
    return

#export to IOS format
def exportToIOSFormat(assy, fileName):
    """
    Writes the IOS file 
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    @param: IOS output file in XML
    @type: string
    """
    
    if fileName == '':
        print "No file selected to export"
        return
    d = DOMImplementation()
    #create doctype
    doctype = DOMImplementation.createDocumentType(d,'ios', None, None)
    
    #create empty DOM Document and get root element
    doc = DOMImplementation.createDocument(d, EMPTY_NAMESPACE,'ios', doctype)
    elemDoc = doc.documentElement

    elemDoc.setAttributeNS(XMLNS_NAMESPACE, "xmlns:ios", "http://www.parabon.com/namespaces/inSeqioOptimizationSpecification")
    elemDoc.setAttributeNS(XMLNS_NAMESPACE, "xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    
    createTokenLibrary(doc, elemDoc)
    createMappingLibrary(doc,elemDoc)
    createStrands(doc, elemDoc, assy)
    createConstraints(doc, elemDoc, assy)
    
    #print doc to file
    f = open(fileName,'w')
    PrettyPrint(doc,f)
    f.close()
    # don't know how to set the IOS prefix, so processing text to
    # include that
    f = open(fileName,'r')
    allLines=f.readlines()
    allLines[1] = "<ios:IOS xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:ios='http://www.parabon.com/namespaces/inSeqioOptimizationSpecification'>\n"
    allLines[len(allLines)-1] = "</ios:IOS>\n"
    f.close()
    #write the document all over to reflect the changes
    f = open(fileName,'w') 
    f.writelines(allLines)
    f.close()
    
    return






# UM 20080618: IOS IMPORT FUNCTIONS

def importFromIOSFile(assy, fileName1):
    """
    Imports optimized sequences to NE-1 from IOS file
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    
    @param fileName1: IOS Import file
    @type fileName1: string
    @return: Returns True or False based on whether import was successful
    
    @note: Since DNA Strand Chunks do not get stored in the mmp file, there's no
           way, chunk by chunk info can be verified between the structure on the
           NE-1 window and that in the IOS file. The most that can be done is to 
           verify the name of the strand Name info and their lengths. For instance
           if two NE-1 structures have the same name and number of strands,each
           of same length, but their pairing info is different, there's no way 
           to check that and the sequences will get imported anyways. There IOS 
           import happens at the user's risk.
    """
    
    strandsOnScreen = checkStrandsOnNE_1Window(assy)
    if strandsOnScreen == False:
        msg = "Cannot import since currently IOS import is supported only for DNA strands and there are no DNA strands on the screen. There is also no support for importing into clipboard."
        QMessageBox.warning(assy.win, "Warning!", msg)
        return False
        
    fileName2 = doInitialProcessingOnXMLFile(fileName1)
    strandNameSeqDict = getHybridizationInfo(fileName2)
    
    if strandNameSeqDict is None:
        # Can remove the temp file
        if os.path.exists(fileName2):
            os.remove(fileName2)
        return False
    
    infoCorrect = verifyStructureInfo(assy, strandNameSeqDict)
    
    if infoCorrect:
        #import optimized bases from the IOS file
        importBases(assy, strandNameSeqDict)
    else:
        if os.path.exists(fileName2):
            os.remove(fileName2)
        return False
        
    if os.path.exists(fileName2):
        os.remove(fileName2)
    
    return True

def checkStrandsOnNE_1Window(assy):
    """
    Checks to see if at least one DNA strand exists on the NE-1 window
    @param part: the NE1 part.
    @type  part: L{assembly}
    @return: True or False depending on whether there are DNA strands on the 
    NE-1 window
    """
   
    count = 0
    part = assy.part
    if hasattr(part.topnode, 'members'):
        for node in part.topnode.members:
            
            if hasattr(node,'members'):
                if node.members is None:
                    return False
                for nodeChild in node.members:
                    if isinstance(nodeChild, assy.DnaStrand):
                        count = count +1
            else:
                if isinstance(node, assy.DnaStrand):
                        count = count +1
            
    if count >= 1:   
        return True
    else:
        return False

def importBases(assy, strandNameSeqDict):
    """
    Imports optimized bases, currently stored in strandNameSeqDict dictionary
    @param assy: the NE1 assy.
    @type  assy: L{assembly}
    
    @param strandNameSeqDict: the dictionary containing the strand names and 
                              sequences from the IOS import file

    @type strandNameSeqDict: dict                              
    """
    
    def func(node):
        if isinstance(node, assy.DnaStrand):
            #retrive its name and see if it exists in the dictionary, if yes 
            # then assign the base sequence
            try:
                seq = strandNameSeqDict[node.name]
                node.setStrandSequence(seq, False)
                #print "In seq assignment:", node.name, seq
                
                # print sequences until now,
                #print "List of sequences in this run"
                for node in assy.part.topnode.members:
                    for nodeChild in node.members:
                        if isinstance(nodeChild, assy.DnaStrand):
                            seq = nodeChild.getStrandSequence()
                            #print nodeChild.name, seq
            
            except KeyError:
                msg = "Cannot import IOS file since strand %s does not exist in the IOS file" % node.name
                QMessageBox.warning(assy.win, "Warning!", msg)
                return
                    
    assy.part.topnode.apply2all(func)
    
    #if we are in the Build DNA mode, update the LineEdit that displays the 
    # sequences 
    
    win = assy.win
    
    if win.commandSequencer.currentCommand.commandName == 'DNA_STRAND':
        win.commandSequencer.currentCommand.updateSequence()
            
     
    return

def getStrandsBaseInfoFromNE_1(assy):
    """
    Obtains the strand chunk names and their corresponding base string of the 
    NE-1 part
    @param part: the NE1 part.
    @type  part: L{assembly}
    @return: strand list and basestring list from NE-1
    """
    strandList = getAllDnaStrands(assy)
    strandListFromNE_1 = []
    baseStringListFromNE_1 = []
    
    for strand in strandList:
        strandID = strand.name
        #just get the name of the strand
        strandListFromNE_1.append(strandID)
        baseString = strand.getStrandSequence()
        baseStringListFromNE_1.append(baseString) 
    return strandListFromNE_1, baseStringListFromNE_1
    


def verifyStructureInfo(assy, iosSeqNameDict):
    """
    Verify that the structure info in the IOS file matches with that of the NE-1 part.
    @param part: the NE1 part.
    @type  part: L{assembly}
    
    @param iosSeqNameDict: dictionary containing strand and basestring 
                           from the IOS file
    @type compInfoDict: dict
    @return: True or False based on if the structure in the IOS file matches up 
             with the structure in the NE-1 window.
    """
    strandListFromNE_1, baseStringListFromNE_1 = getStrandsBaseInfoFromNE_1(assy)
    #check their lengths first
    dictLength = len(iosSeqNameDict)
    strandListFromNE_1Length = len(strandListFromNE_1)
    if dictLength != strandListFromNE_1Length:
        msg = "Cannot import IOS file since number of strands in the import file and one in NE-1 window does not match"
        QMessageBox.warning(assy.win, "Warning!", msg)
        return False  
    
    for strand in iosSeqNameDict:
        
        baseString = iosSeqNameDict[strand]
        try:
            index = strandListFromNE_1.index(strand)
            baseStringFromNE_1 = baseStringListFromNE_1[index]
        except ValueError:
            msg = "Cannot import IOS file since strand %s in IOS file does not exist in NE-1 windows" % strand
            QMessageBox.warning(assy.win, "Warning!", msg)
            return False
        
        if len(baseStringFromNE_1) != len(baseString):
            msg = "Cannot import IOS file since base string length %d of strand %s in the NE-1 window does not match with the one found in the IOS file (%s, %d)" % (len(baseStringFromNE_1), strandListFromNE_1[index], strand, len(baseString))
            QMessageBox.warning(assy.win, "Warning!", msg)
            return False
    return True    
    
def doInitialProcessingOnXMLFile(fileName1):
    """
    do initial preprocessing on the file so that its acceptable by the parser 
    from xml.dom.minidom
    @param fileName2: IOS import file
    @type fileName2: string   
    @retun: Temporary file that is read by the xml.dom.minidom
    """
    #its wierd, sometimes even with the prefix, the ExpatError exception does not
    #show up. Do n't know what's going on! Anyways the prefix ios is not needed
    #for any of the NE-1 processing and so it's better to be on the safe side!
    
    f1 = open(fileName1, 'r')
    allLines=f1.readlines()
    f1.close()
    #create a temporary file with the prefixes removed, make sure that you remove
    #this file at the end of processing
    fileName2 = "temp.xml"
    f2 = open(fileName2, 'w')
    
    
    for line in allLines:
        if line.find("<ios:")!= -1:
            line = line.replace("<ios:","<")
        if line.find("</ios:")!= -1:
            line = line.replace("</ios:","</")
        f2.writelines(line)
    f2.close() 
    
    return fileName2



def getHybridizationInfo(fileName2):
    """
    Process this temporary file for strand chunk info. At the same time, we 
    check whether its a proper IOS file.
    
    @param fileName2: IOS import file
    @type fileName2: string
    @return: a dictionary containing (strand, sequence)
    """
    
    try:
        doc = parse(fileName2)
    except ExpatError:
        msg = "Cannot import IOS file, since its not in correct XML format"
        QMessageBox.warning(assy.win, "Warning!", msg)
        return None
    
    #need to distinguish between regions for mapping and simple strand regions
    # hence get strand
    strandList = doc.getElementsByTagName("Strand")
    if len(strandList) == 0:
        msg = "Cannot import IOS file since no strands to import"
        QMessageBox.warning(assy.win, "Warning!", msg)
        return None
    
    strandNameList = []
    strandSeqList = []
    
    #Within each strand access all regions
    for i in range(len(strandList)):
        strandNameList.append(str(strandList.item(i).getAttribute("id")))
        regionList = strandList.item(i).getElementsByTagName("Region")

        #each strand needs to have at least one region and so if one of them 
        #does not have it, then it is not a correct IOS file and you should return
        # without bothering to process the rest of the file. 
        # So far IOS file format is concerned, single strand chunks do not neeed
        # to be in a Region node. However, without the ID of the region, we have 
        # no way to read it into NE-1 and hence this import is invalid.
        
        if len(regionList) == 0:
            msg = "Cannot import IOS file: strand does not have any region, not a correct IOS file format"
            QMessageBox.warning(assy.win, "Warning!", msg)
            return None
        
        tempStrandSeq = ''
        for j in range(len(regionList)):
            
            #get new base sequence after IOS optimization
            tempBaseString = ''
            if regionList.item(j).childNodes.item(0) is not None:
                tempBaseString = str(regionList.item(j).childNodes.item(0).toxml())
            
            #if the base string is empty, there's no point of analyzing any 
            #further either
            if tempBaseString== '':
                msg = "Cannot import IOS file: strand region does not have any bases, not a correct IOS file format"
                QMessageBox.warning(assy.win, "Warning!", msg)
                return None
            
            
            tempStrandSeq = tempStrandSeq + tempBaseString
        strandSeqList.append(tempStrandSeq) 
     
    strandNameSeqDict = dict(zip(strandNameList, strandSeqList)) 
    
    return strandNameSeqDict