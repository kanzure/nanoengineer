"""
files_ios.py - provides functions to export a NE-1 model into IOS format as well
as import optimized sequences into NE-1

@version: $Id$: 
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@author: Urmi

Note: This is only applicable to DNA/ RNA models (so is IOS)
"""
from xml.dom.minidom import DOMImplementation
from xml.dom import EMPTY_NAMESPACE, XML_NAMESPACE, XMLNS_NAMESPACE
from dna.model.DnaLadderRailChunk import DnaStrandChunk
from dna.model.DnaLadder import DnaLadder
from printFunc import PrettyPrint
import os, string, sys
from xml.dom.minidom import parse
from xml.parsers.expat import ExpatError
from dna.model.DnaStrand import DnaStrand
from PyQt4.Qt import QMessageBox



def getAllDnaStrands(assy):
    """
    get all the DNA strands from the NE-1 part to figure out strand info
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

def createMapping(startIndex, endIndex):
    dictionary = dict()
    if startIndex < endIndex:
        j=0
        i = startIndex
        while i <= endIndex : 
            dictionary[i] = j
            j = j + 1
            i = i + 1
    else:
        j=0
        i = startIndex
        while i >= endIndex : 
            dictionary[i] = j
            j = j + 1
            i = i - 1
            
    return dictionary

def createComplementaryChunkInformation(strandList, chunkNameListInOrder, indexTupleListInOrder):
    
    chunkAndComplementDict = dict()
    
    #visited array for all strands so that chunk info do not get written twice
    indexMappingList = []
    visitedArray = []
    for i in range(len(strandList)):
        strand = strandList[i]
        startIndex = indexTupleListInOrder[i][0][0]
        endIndex = indexTupleListInOrder[i][len(indexTupleListInOrder[i])-1][1]
        seqLen = len(strand.getStrandSequence())
        indexMappingList.append(createMapping(startIndex, endIndex))
        tempList = []
        for j in range(seqLen):
            tempList.append(0)
        visitedArray.append(tempList)
        
    
        
    #create complementary info 
    for strand in strandList:
        strand_wholechain = strand.get_strand_wholechain()
        for rail in strand_wholechain.rails():    
            atom = rail.baseatoms[0]
            atomMate = atom.get_strand_atom_mate()
            # do this only for double stranded DNA
            if atomMate is not None:
                #check visited array to see if complementary info has already been written
                baseIndices = strand_wholechain.wholechain_baseindex_range_for_rail(rail)
                index = strandList.index(strand)
                tempList = []
                tempList = [x[0] for x in indexTupleListInOrder[index]]
                try:
                    index1 = tempList.index(baseIndices[0])
                    startIndex = baseIndices[0]
                    endIndex = baseIndices[1]
                except ValueError:
                    index1 = tempList.index(baseIndices[1])
                    startIndex = baseIndices[1]
                    endIndex = baseIndices[0]
                    
                startIndexInVA = indexMappingList[index][startIndex]    
                endIndexInVA = indexMappingList[index][endIndex]   
                
                exist = 0
                m = startIndexInVA
                while m <= endIndexInVA:
                    if visitedArray[index][m] == 0:
                        exist = 0
                        break
                    else:
                        exist = 1
                    m = m + 1    
                        
                if exist == 1:
                    #entry already exists
                    continue
                else:
                    #need to create chunk and complementary chunk info
                    chunkName = chunkNameListInOrder[index][index1 + 1]
                    #mark visited array to be 1
                    m = startIndexInVA
                    while m <= endIndexInVA:
                        visitedArray[index][m] = 1
                        m = m + 1
                    #find complementary chunk Name
                    
                    atomMateParent = atomMate.getDnaStrand()
                    strandRails = atom.molecule.ladder.strand_rails
                    assert len(strandRails) ==  2
                    if rail == strandRails[0]:
                        complementaryRail = strandRails[1]       
                    else:
                        complementaryRail = strandRails[0]
                    baseIndicesForComp = atomMateParent.get_strand_wholechain().wholechain_baseindex_range_for_rail(complementaryRail)  
                    
                    tempList = []
                    indexComp = strandList.index(atomMateParent)
                    tempList = [x[0] for x in indexTupleListInOrder[indexComp]]
                    try:
                        index1 = tempList.index(baseIndicesForComp[0])
                        startIndex = baseIndicesForComp[0]
                        endIndex = baseIndicesForComp[1]
                    except ValueError:
                        index1 = tempList.index(baseIndicesForComp[1])
                        startIndex = baseIndicesForComp[1]
                        endIndex = baseIndicesForComp[0]
                    
                    startIndexInVA = indexMappingList[indexComp][startIndex]    
                    endIndexInVA = indexMappingList[indexComp][endIndex]
                    compChunkName = chunkNameListInOrder[indexComp][index1 + 1]
                    m = startIndexInVA
                    while m <= endIndexInVA:
                        visitedArray[indexComp][m] = 1
                        m = m + 1
                        
                    chunkAndComplementDict[chunkName] = compChunkName
            

    return chunkAndComplementDict


def railImplementation(assy):
    
    strandList = getAllDnaStrands(assy)
    
    baseStringListInOrder = []
    indexTupleListInOrder = []
    chunkNameListInOrder = []
    
    #initialization
    for i in range(len(strandList)):
        baseStringListInOrder.append([])
        indexTupleListInOrder.append([])
        chunkNameListInOrder.append([])
        
        
    for strand in strandList:
        strandID = strand.name
        strandIndex = strandList.index(strand)
        #wholechain_baseindex_range_for_rail(rail) can return sequences either
        #in 3' or 5' sequences. Hence the final sequence should be compared with
        # that of atoms in the bond direction and their corresponding basenames
        # to figure out its directionality.
        strand_wholechain = strand.get_strand_wholechain()
        
        someList = []
        if strand_wholechain:
            for rail in strand_wholechain.rails():
                baseList = []
                for a in rail.baseatoms:
                    bases = a.getDnaBaseName()
                    aComp = a.get_strand_atom_mate() 
                    parent = a.getDnaStrand()
                    if bases == 'X':
                        bases = 'N'  
                    baseList.append(bases)
                baseIndices = strand_wholechain.wholechain_baseindex_range_for_rail(rail)
                
                
                baseString = ''.join(baseList)
                if baseIndices[1] < baseIndices[0]:
                    baseStringFinal = baseString[::-1]
                    indexTuple = [baseIndices[1], baseIndices[0]]
                else:
                    baseStringFinal = baseString
                    indexTuple = [baseIndices[0], baseIndices[1]]
                someList.append( (indexTuple, baseStringFinal) )     
                
        someList.sort()
        indexTupleListInOrder[strandIndex] =  [x[0] for x in someList]  
        baseStringListInOrder[strandIndex] = [x[1] for x in someList] 
        checkStrandSequence = ''.join(baseStringListInOrder[strandIndex])
        
        strandSeq = strand.getStrandSequence()
        if strandSeq == checkStrandSequence[::-1]:
            baseStringListInOrder[strandIndex].reverse()
            indexTupleListInOrder[strandIndex].reverse()
            #we also need to flip the order of the individual element in the tuple
            for l in range(len(indexTupleListInOrder[strandIndex])):
                indexTupleListInOrder[strandIndex][l].reverse()
        
        #create names for each chunk within each strand
        someList = []
        for l in range(len(baseStringListInOrder[strandIndex])):
            chunkName = strandID + '_chunk_' + str(l)
            someList.append(chunkName)
        chunkNameListInOrder[strandIndex] = someList
        chunkNameListInOrder[strandIndex].insert(0, strandID)
    
    
    chunkAndComplementDict = createComplementaryChunkInformation(strandList, chunkNameListInOrder, indexTupleListInOrder)    
    return chunkNameListInOrder, baseStringListInOrder, chunkAndComplementDict


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
    
    
    chunkNameListInOrder, baseStringListInOrder, chunkAndComplementDict = railImplementation(assy)
    
    #write the strands to the IOS export file
    elemStrands = doc.createElement('Strands')
    i = 0
    while i < len(chunkNameListInOrder):
        strandID = chunkNameListInOrder[i][0]
        elemStrand = doc.createElement('Strand')
        elemStrand.setAttribute('id',strandID)
        for j in range(0, len(chunkNameListInOrder[i])-1):
            chunkID = chunkNameListInOrder[i][j+1]
            
            baseString = baseStringListInOrder[i][j]
            baseString.replace('X','N')
            elemRegion = doc.createElement('Region')
            elemRegion.setAttribute('id', chunkID)
            elemRegion.appendChild(doc.createTextNode(baseString))
            elemStrand.appendChild(elemRegion) 
        i = i + 1    
        elemStrands.appendChild(elemStrand)
        
    elemDoc.appendChild(elemStrands)
    
    return chunkAndComplementDict
   

def createConstraints(doc,elemDoc, assy, compInfoDict):
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
    
    for key in compInfoDict:
        elemMatch = doc.createElement('ios:Match')
        elemMatch.setAttribute('mapping', 'complement')
        elemConstraintRegion = doc.createElement('Region')
        elemConstraintRegion.setAttribute('ref',key)
        elemMatch.appendChild(elemConstraintRegion)

        elemConstraintRegion = doc.createElement('Region')
        elemConstraintRegion.setAttribute('ref',compInfoDict[key])
        elemConstraintRegion.setAttribute('reverse', '1')
        elemMatch.appendChild(elemConstraintRegion)  
        elemConstraintGroup.appendChild(elemMatch) 
            
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
    compInfoDict = createStrands(doc, elemDoc, assy)
    createConstraints(doc, elemDoc, assy, compInfoDict)
    
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
                
                for node in assy.part.topnode.members:
                    for nodeChild in node.members:
                        if isinstance(nodeChild, assy.DnaStrand):
                            seq = nodeChild.getStrandSequence()
                            
            
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