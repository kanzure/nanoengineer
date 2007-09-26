# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
'''
Dna_constants.py -- constants for Dna.

$Id: $

@see: References:
      - U{The Standard IUB codes used in NanoEngineer-1
        <http://www.idtdna.com/InstantKB/article.aspx?id=13763>}
      - U{http://en.wikipedia.org/wiki/DNA}
      - U{http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif}

History:

2007-08-19 - Started out as part of Dna.py.
'''
__author__ = 'mark'

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
 
# PAM5_AtomList contains the all PAM-5 base-pair atoms needed to construct any
# DNA structure. The four sets are:
#  -  startBasePair: The 5' set.
#  -    midBasePair: The middle set.
#  -    endBasePair: The 3' set.
#  - singleBasePair: A single set (properly terminated).
#
# The format:
#  - PAM5 Symbol, atom position, a_or_b (i.e. which strand the atom belongs to).
#
# Problems:
#  - Singlets must be added. These are needed to properly orient bondpoints 
#    between basepairs.
#  - Need bond pair list. Cannot create proper bonds between atoms with it.
#
# Special note:
#  This is a work in progress. I started this assuming it would be much
#  faster to make large PAM5 structures (like we have in origami) using 
#  constants like this rather than reading files. --Mark 2007-08-19

from VQT import V

PAM5_AtomList = {'PAM5BasePair':[ ("Pl5", V( 8.699,  2.638,  1.590), "a"),
                                  ("Ss5", V( 6.760,  0.0,    0.0  ), "a"),
                                  ("Ax5", V( 0.0,    0.0,    0.0  ), " "),
                                  ("Ss5", V(-4.610, -4.943,  0.0  ), "b"), 
                                  ("Pl5", V(-7.863, -4.562, -1.590), "b") ] }


# Common DNA helper functions. ######################################

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
