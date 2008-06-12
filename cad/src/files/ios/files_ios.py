"""
files_ios.py - provides functions to export a NE-1 model into IOS format

@version: 
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: This is only applicable to DNA/ RNA models (so is IOS)
"""
from xml.dom.minidom import DOMImplementation
from xml.dom import EMPTY_NAMESPACE, XML_NAMESPACE, XMLNS_NAMESPACE
from dna.model.DnaLadderRailChunk import DnaStrandChunk
from dna.model.DnaLadder import DnaLadder
from dna.model.DnaSegment import DnaSegment
from dna.model.DnaStrand import DnaStrand
from printFunc import PrettyPrint



def getAllLadders(part):
    """
    get all the DNA ladders from the screen to figure out strand pairing info
    @param: part
    @type: 
    @return: a list of DNA ladders
    """
    dnaSegmentList = []
         
    def func(node):
        if isinstance(node, DnaSegment):
            dnaSegmentList.append(node)
            
    part.topnode.apply2all(func)
    #get all ladders for each segment
    dnaLadderList = []
    for seg in dnaSegmentList:
        laddersWithinSegmentList = []
        laddersWithinSegmentList = seg.getDnaLadders()
        for ladder in laddersWithinSegmentList:
            dnaLadderList.append(ladder)
            
    return dnaLadderList

def getAllDnaStrands(part):
    """
    get all the DNA strands from the screen to figure out strand info
    @param: part
    @type: 
    @return: a list of DNA strands
    """
    dnaStrandList = []
         
    def func(node):
        if isinstance(node, DnaStrand):
            dnaStrandList.append(node)
                    
    part.topnode.apply2all(func)
        
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

def createStrands(doc,elemDoc, part):
    """
    create strand section for the NE-1 model file in the ios file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    
    """
    
    #create strands
    elemStrands = doc.createElement('Strands')
    strandList = getAllDnaStrands(part)
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

def createConstraints(doc,elemDoc, part):
    """
    create constraints section for the NE-1 model file in the ios file
    @param: doc
    @type: DOM Document
    @param: elemDoc
    @type: root element
    
    """
    # write the constraints
    elemConstraints = doc.createElement('Constraints')
    elemConstraintGroup = doc.createElement('ios:ConstraintGroup')
    elemConstraintGroup.setAttribute('strict', '1')
    
    ladderList = getAllLadders(part)
    
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
def exportToIOSFormat(part, fileName):
    """
    Writes the IOS file 
    @param: part
    @type:
    
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
    createStrands(doc, elemDoc, part)
    createConstraints(doc, elemDoc, part)
    
    #print doc to file
    f = open(fileName,'w')
    PrettyPrint(doc,f)
    f.close()
    # don't know how to set the IOS prefix, so processing text to
    # include that
    f = open(fileName,'r')
    allLines=f.readlines()
    print allLines[1], allLines[len(allLines)-1]
    allLines[1] = "<ios:IOS xmlns:xsi='http://www.w3.org/2001/XMLSchema-instance' xmlns:ios='http://www.parabon.com/namespaces/inSeqioOptimizationSpecification'>\n"
    allLines[len(allLines)-1] = "</ios:IOS>\n"
    f.close()
    #write the document all over to reflect the changes
    f = open(fileName,'w') 
    f.writelines(allLines)
    f.close()
    return
