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
    
    #create strands
    elemStrands = doc.createElement('Strands')
    strandList = getAllDnaStrands(assy)
    for strand in strandList:
        strandID = strand.name
        elemStrand = doc.createElement('Strand')
        elemStrand.setAttribute('id',strandID)
        
        strandChunkList = strand.getStrandChunks()
        for chunk in strandChunkList:
            chunkID = chunk.name
            atoms = chunk.get_baseatoms()
            baseList = []
            for a in atoms:
                bases = a.getDnaBaseName()
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
    """
    part = assy.part
    strandsOnScreen = checkStrandsOnNE_1Window(assy)
    if strandsOnScreen == False:
        print "Cannot import since currently IOS import is supported only for \
        DNA strands and there are no DNA strands on the screen"
        return False
        
    fileName2 = doInitialProcessingOnXMLFile(fileName1)
    strandBasesDict, compInfoDict, strandNameSeqDict = getHybridizationInfo(fileName2)
    if strandBasesDict is None or strandNameSeqDict is None:
        # Can remove the temp file
        if os.path.exists(fileName2):
            os.remove(fileName2)
        return False
    if compInfoDict is None:
        print "All single strands to import"
    
    #make sure that the file you are reading into the system has information
    #that corresponds to the current structure in the NE-1 window.
    infoCorrect = verifyStructureInfo(assy, strandBasesDict, compInfoDict)
    
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
                for nodeChild in node.members:
                    if isinstance(nodeChild, assy.DnaStrand):
                        count = count +1
            else:
                if isinstance(node, DnaStrand):
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
    part = assy.part
    
    def func(node):
        if isinstance(node, assy.DnaStrand):
            #retrive its name and see if it exists in the dictionary, if yes 
            # then assign the base sequence
            try:
                seq = strandNameSeqDict[node.name]
                node.setStrandSequence(seq)
            except KeyError:
                print "Cannot import since strand %s does not exist \
                in the IOS file" % node.name
                return
                    
    assy.part.topnode.apply2all(func)
    win = assy.win
    #if we are in the Build DNA mode, update the LineEdit that displays the 
    # sequences 
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
    strandChunkListFromNE_1 = []
    baseStringListFromNE_1 = []
    
    for strand in strandList:
        strandChunkList = strand.getStrandChunks()
        for chunk in strandChunkList:
            chunkID = chunk.name
            #just get the name of the strand
            strandChunkListFromNE_1.append(chunkID)
            atoms = chunk.get_baseatoms()
            baseList = []
            for a in atoms:
                bases = a.getDnaBaseName()
                baseList.append(bases)
            baseString = ''.join(baseList)
            # base string needed for length info
            baseStringListFromNE_1.append(baseString) 
    return strandChunkListFromNE_1, baseStringListFromNE_1
    
def verifyStrandInfo(assy, strandBasesDict):
    """
    Verify strand info from NE-1 part and IOS file match
    @param part: the NE1 part.
    @type  part: L{assembly}
    @param strandBasesDict: the dictionary containing the strand names and 
                              sequences from the IOS import file

    @type strandBasesDict: dict   
    @return: True or False based on whether strands in the NE-1 and that in the 
             IOS file match up.
    """
    strandChunkListFromNE_1, baseStringListFromNE_1 = getStrandsBaseInfoFromNE_1(assy)
    
    # Once strand chunks name and base string info have been obtained from NE-1
    #check first of all such a chunk exists in the strand dictionary and if yes
    # the base string lengths match
    
    #check their lengths first
    dictLength = len(strandBasesDict)
    strandChunkListFromNE_1Length = len(strandChunkListFromNE_1)
    if dictLength != strandChunkListFromNE_1Length:
        print "Cannot import IOS file since number of strand chunks in the import file and \
               one in NE-1 window does not match"
        return False
    
    #check if all the strand chunks exist
    for chunks in strandChunkListFromNE_1:
        try:
            baseString = strandBasesDict[chunks]
        except KeyError:
            print "Cannot import IOS file since strand chunk %s in the NE-1 window \
               cannot be found in the IOS file" % (chunks)
            return False
     
    #check if all the basestring lengths match or not
    k = 0
    for chunks in strandChunkListFromNE_1:
        baseString = strandBasesDict[chunks]
        baseStringFromNE_1 = baseStringListFromNE_1[k]
        
        #print baseStringFromNE_1, baseString, k, len(baseStringFromNE_1),len(baseString)
        if len(baseStringFromNE_1) != len(baseString):
            print "Cannot import IOS file since base string length %d of \
            chunk %s in the NE-1 window does not match with the one found in \
            the IOS file %d" % (len(baseStringFromNE_1), chunks, len(baseString))
            return False
        k = k + 1
        
    
    return True

def getChunkAndComplFromNE_1(assy):
    """
    Obtain strand chunk and their corresponding complementary chunk for NE-1 part.
    @param part: the NE1 part.
    @type  part: L{assembly}
    @return: Two lists containing strand chunks and their complements respectively
    """
    ladderList = getAllLadders(assy)
    strandChunkList = []
    strandChunkComplList = []
    for ladder in ladderList:
        strandChunks = ladder.strand_chunks()
        if ladder.num_strands() == 2:
            chunk1 = strandChunks[0].name
            chunk2 = strandChunks[1].name    
            strandChunkList.append(chunk1)
            strandChunkComplList.append(chunk2)
            
    return strandChunkList, strandChunkComplList

def verifyComplementInfo(assy, compInfoDict):
    """
    Verify that the complementary strand info from the IOS file macthes with 
    that from the NE-1 part.
    
    @param part: the NE1 part.
    @type  part: L{assembly}
    @param compInfoDict: dictionary containing strand and their complementary 
                         strands from the IOS file
    @type compInfoDict: dict
    @return: True or False based on whether the pairing info in the IOS file matches
             with that in the NE-1 assembly
    """
    strandChunkList, strandChunkComplList = getChunkAndComplFromNE_1(assy)
    if strandChunkList != '' and compInfoDict is None:
        print "Cannot import IOS file since no pairing info in the IOS file, but\
        NE-1 structure has doublestranded regions"
        return False
    if strandChunkList == '' and compInfoDict is None:
        #no harm having single strands info, so long they match
        return True
    
    # as with strands verify the number of double stranded regions are equal
    if len(strandChunkList) != len(compInfoDict):
        print "Cannot do IOS import since number of double stranded regions \
        are not equal"
        return False
    
    #verify complementary strands are same in IOS file and in NE-1 window
    k = 0
    for chunk in strandChunkList:
        # no need to check if the chunk exists in the dictionary since if it
        # does not, it has already returned False from the verifyStrandInfo() 
        # function
        
        complFromIOS = compInfoDict[chunk]
        if complFromIOS != strandChunkComplList[k]:
            print "Cannot import IOS file since matching info for %s not found" % chunk
            return False
        k = k + 1
    return True

def verifyStructureInfo(assy, strandBasesDict, compInfoDict):
    """
    Verify that the structure info in the IOS file matches with that of the NE-1 part.
    @param part: the NE1 part.
    @type  part: L{assembly}
    @param strandBasesDict: dictionary containing strand and their corresponding
                            base string from IOS file
    @type strandBasesDict: dict
    @param compInfoDict: dictionary containing strand and their complementary 
                         strands from the IOS file
    @type compInfoDict: dict
    @return: True or False based on if the structure in the IOS file matches up 
             with the structure in the NE-1 window.
    """
    strandInfoCorrect = verifyStrandInfo(assy, strandBasesDict)
    if strandInfoCorrect == False:
        return False
    compInfoCorrect = verifyComplementInfo(assy, compInfoDict)     
    if compInfoCorrect:
        return True
    else: 
        return False

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
    @return: 3 dictionaries containing (strand, Bases), (strand, complements), 
            and (strand, sequence)
    """
    
    try:
        doc = parse(fileName2)
    except ExpatError:
        print "Cannot import IOS file, since its not in correct XML format"
        return None, None, None
    
    #need to distinguish between regions for mapping and simple strand regions
    # hence get strand
    strandList = doc.getElementsByTagName("Strand")
    if len(strandList) == 0:
        print "Cannot import IOS file since no strands to import"
        return None, None, None
    
    strandNameList = []
    strandChunkList = []
    basesForStrandChunkList = []
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
            print "Cannot import IOS file: strand does not have any region, not \
            a correct IOS file format"
            return None, None, None
        
        tempStrandSeq = ''
        for j in range(len(regionList)):
            #get list of strand chunks
            strandChunkList.append(str(regionList.item(j).getAttribute("id")))
            #get new base sequence after IOS optimization
            tempBaseString = ''
            if regionList.item(j).childNodes.item(0) is not None:
                tempBaseString = str(regionList.item(j).childNodes.item(0).toxml())
            
            #if the base string is empty, there's no point of analyzing any 
            #further either
            if tempBaseString== '':
                print "Cannot import IOS file: strand chunk does not have any bases, \
                not a correct IOS file format"
                return None, None, None
            
            basesForStrandChunkList.append(tempBaseString)
            tempStrandSeq = tempStrandSeq + tempBaseString
        strandSeqList.append(tempStrandSeq) 
        
    strandBasesDict = dict(zip(strandChunkList, basesForStrandChunkList))
    strandNameSeqDict = dict(zip(strandNameList, strandSeqList)) 
    
    #would also need the constraints region to verify the pairing info
    strand1List = []
    strand2List = []
    
    matchingList = doc.getElementsByTagName("Match")
    if len(matchingList) == 0:
        return strandBasesDict, None, strandNameSeqDict
    
    #Within each matching access the pairs individually and store them in a tuple
    for i in range(len(matchingList)):
        compPairs = matchingList.item(i).getElementsByTagName("Region")
        
        #get the names of complementary chunks
        strand1List.append(str(compPairs.item(0).getAttribute("ref")))
        strand2List.append(str(compPairs.item(1).getAttribute("ref"))) 
        
    compInfoDict = dict(zip(strand1List, strand2List))
    
    return strandBasesDict, compInfoDict, strandNameSeqDict