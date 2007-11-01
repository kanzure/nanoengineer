# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Dna_Constants.py -- constants for Dna.

Note: these are used both by the newer DnaDuplex.py,
and the older Dna.py which it supersedes (and their
associated files).

@author: Mark Sims
@version: $Id$
@copyright: Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.

@see: References:
      - U{The Standard IUB codes used in NanoEngineer-1
        <http://www.idtdna.com/InstantKB/article.aspx?id=13763>}
      - U{http://en.wikipedia.org/wiki/DNA}
      - U{http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif}

History:

2007-08-19 - Started out as part of Dna.py.
"""
__author__ = 'mark'

import math
from constants import strandColorList

basesDict = { 'A':{'Name':'Adenine',  'Complement':'T', 'Color':'darkorange' },
              'C':{'Name':'Cytosine', 'Complement':'G', 'Color':'cyan'       },
              'G':{'Name':'Guanine',  'Complement':'C', 'Color':'green'      },
              'T':{'Name':'Thymine',  'Complement':'A', 'Color':'teal'       },
              'U':{'Name':'Uracil',   'Complement':'A', 'Color':'darkblue'   },
              
              'X':{'Name':'Undefined', 'Complement':'X', 'Color':'darkred' },
              'N':{'Name':'aNy base',  'Complement':'N', 'Color':'orchid'  },
              
              'B':{'Name':'C,G or T', 'Complement':'V', 'Color':'dimgrey' },
              'V':{'Name':'A,C or G', 'Complement':'B', 'Color':'dimgrey' },
              'D':{'Name':'A,G or T', 'Complement':'H', 'Color':'dimgrey' },
              'H':{'Name':'A,C or T', 'Complement':'D', 'Color':'dimgrey' },
              
              'R':{'Name':'A or G (puRine)',     'Complement':'Y', 'Color':'dimgrey'},
              'Y':{'Name':'C or T (pYrimidine)', 'Complement':'R', 'Color':'dimgrey'},
              'K':{'Name':'G or T (Keto)',       'Complement':'M', 'Color':'dimgrey'},
              'M':{'Name':'A or C (aMino)',      'Complement':'K', 'Color':'dimgrey'},
              
              'S':{'Name':'G or C (Strong - 3H bonds)',  'Complement':'W', 'Color':'dimgrey'},
              'W':{'Name':'A or T (Weak - 2H bonds)',    'Complement':'S', 'Color':'dimgrey'} }

dnaDict = { 'A-DNA':{'DuplexRise':3.391},
            'B-DNA':{'DuplexRise':3.180},
            'Z-DNA':{'DuplexRise':3.715} }

strand_color_counter = 0

# Common DNA helper functions. ######################################

def getNextStrandColor(currentColor = None):
    """
    Return a color to assign a strand guaranteed to be different than
    its current color.
    
    @param currentColor: The current color of the strand.
    @type  currentColor: RGB tuple
    
    @return: New color.
    @rtype: RGB tuple
    """
    global strand_color_counter
    _clist_length = len(strandColorList)
    r, i = math.modf(strand_color_counter / _clist_length)
    _strand_color_index = int(strand_color_counter - (i * _clist_length))
    _new_color = strandColorList[_strand_color_index]
    strand_color_counter += 1
    if _new_color == currentColor:
        return getNextStrandColor()
    return _new_color

def getDuplexRise(conformation):
    """
    Return the 'rise' between base pairs of the 
    specified DNA type (conformation).
    
    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str
    
    @return: The rise in Angstroms.
    @rtype: float
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    return dnaDict[str(conformation)]['DuplexRise']

def getDuplexLength(conformation, numberOfBases):
    """
    Returns the duplex length (in Angstroms) given the conformation
    and number of bases.
    
    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str
    
    @param numberOfBases: The number of base-pairs in the duplex.
    @type  numberOfBases: int
    
    @return: The length of the duplex in Angstroms.
    @rtype: float
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    assert numberOfBases >= 0
    return getDuplexRise(conformation) * numberOfBases

def getNumberOfBasePairsFromDuplexLength(conformation, duplexLength):
    """
    Returns the number of base-pairs in the duplex given the conformation  
    and the duplex length. This number is rounded to the nearest integer. 
    
    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str
    
    @param duplexLength: The duplex length in Angstroms. (0 or positive value)
    @type  duplexLength: float
    
    @return:  The number of base-pairs in the duplex
    @rtype: int
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    assert duplexLength >= 0
    numberOfBasePairs = 1 + (duplexLength / getDuplexRise(conformation))
    return round(numberOfBasePairs)


def getComplementSequence(inSequence):
    """
    Returns the complement of the DNA sequence I{inSequence}.
    
    @param inSequence: The original DNA sequence.
    @type  inSequence: str
    
    @return: The complement DNA sequence.
    @rtype:  str
    """
    assert isinstance(inSequence, str)
    outSequence = ""
    for baseLetter in inSequence:
        if baseLetter not in basesDict.keys():
            baseLetter = "N"
        else:
            baseLetter = basesDict[baseLetter]['Complement']
        outSequence += baseLetter
    return outSequence
    
def getReverseSequence(inSequence):
    """
    Returns the reverse order of the DNA sequence I{inSequence}.
    
    @param inSequence: The original DNA sequence.
    @type  inSequence: str
    
    @return: The reversed sequence.
    @rtype:  str
    """
    assert isinstance(inSequence, str)
    outSequence = list(inSequence)
    outSequence.reverse()
    outSequence = ''.join(outSequence)
    return outSequence

def replaceUnrecognized(inSequence, replaceBase = "N"):
    """
    Replaces any unrecognized/invalid characters (alphanumeric or
    symbolic) from the DNA sequence and replaces them with I{replaceBase}.
    
    This can also be used to remove all unrecognized bases by setting
    I{replaceBase} to an empty string.
    
    @param inSequence: The original DNA sequence.
    @type  inSequence: str
    
    @param replaceBase: The base letter to put in place of an unrecognized base.
                        The default is "N".
    @type  replaceBase: str
    
    @return: The sequence.
    @rtype:  str
    """
    assert isinstance(inSequence, str)
    assert isinstance(replaceBase, str)
    
    outSequence = ""
    for baseLetter in inSequence:
        if baseLetter not in basesDict.keys():
            baseLetter = replaceBase
        outSequence += baseLetter
    if 0:
        print " inSequence:", inSequence
        print "outSequence:", outSequence
    return outSequence
