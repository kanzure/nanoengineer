# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
Dna_Constants.py -- constants for Dna.

Note: these are used both by the newer DnaDuplex.py,
and the older DnaGenHelper.py which it supersedes
(and their associated files).

@author: Mark Sims
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

@see: References:
      - U{The Standard IUB codes used in NanoEngineer-1
        <http://www.idtdna.com/InstantKB/article.aspx?id=13763>}
      - U{http://en.wikipedia.org/wiki/DNA}
      - U{http://en.wikipedia.org/wiki/Image:Dna_pairing_aa.gif}

History:

2007-08-19 - Started out as part of DnaGenHelper.py
"""

import foundation.env as env
from utilities.constants import purple, brass, steelblue, lightgreen, darkgray, lightblue
from utilities.constants import darkorange, violet, copper, olive, gray
from utilities.prefs_constants import adnaBasesPerTurn_prefs_key, adnaRise_prefs_key
from utilities.prefs_constants import bdnaBasesPerTurn_prefs_key, bdnaRise_prefs_key
from utilities.prefs_constants import zdnaBasesPerTurn_prefs_key, zdnaRise_prefs_key
from PyQt4.Qt import QString

basesDict = \
          { 'A':{'Name':'Adenine',  'Complement':'T', 'Color':'darkorange' },
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
            'W':{'Name':'A or T (Weak - 2H bonds)',    'Complement':'S', 'Color':'dimgrey'}
        }

# I'd like to suggest that we change the name of key 'DuplexRise' to 'Rise'.
# Need to run this by Bruce and Ninad first. Mark 2008-01-31.
dnaDict = \
        { 'A-DNA':{'BasesPerTurn': env.prefs[adnaBasesPerTurn_prefs_key],
                   'DuplexRise':   env.prefs[adnaRise_prefs_key]},
          'B-DNA':{'BasesPerTurn': env.prefs[bdnaBasesPerTurn_prefs_key],
                   'DuplexRise':   env.prefs[bdnaRise_prefs_key]},
          'Z-DNA':{'BasesPerTurn': env.prefs[zdnaBasesPerTurn_prefs_key],
                   'DuplexRise':   env.prefs[zdnaRise_prefs_key]}
               }

#If the qiven strand atom doesn't have a compelmentary strand base atom,
#the sequence editor will show a specific character in the 'complement sequence
#text field (i.e. in self.sequenceTextEdit_mate) indicating that the
#complement is missing.
#@see: DnaSequenceEditor._determine_complementSequence()
#@see: DnaStrand.getStrandSequenceAndItsComplement()
MISSING_COMPLEMENTARY_STRAND_ATOM_SYMBOL = '*'


# Common DNA helper functions. ######################################

# for getNextStrandColor:

# _strandColorList is used for assigning a color to a new strand created
# by breaking an existing strand.
# Do not use the following colors in _strandColorList:
#   - white/lightgray (reserved for axis)
#   - black (reserved as a default color for scaffold strand;
#      also used for dna updater duplex errors (subject to change)
#      [bruce 080206])
#   - yellow (used for hover highlighting)
#   - red (used as delete highlight color)
#   - green (reserved for selection color)
#   - orange (reserved for dna updater errors on atoms and bonds [bruce 080206]
#              (subject to change))
#     (update [bruce 080406]: orange is no longer used that way, but might
#      still be, or in future be, used for other warnings, so is still
#      left out of this list)
_strandColorList = [ purple, brass, steelblue, lightgreen, darkgray, lightblue,
                    darkorange, violet, copper, olive, gray]

_strand_color_counter = 0

def getNextStrandColor(currentColor = None):
    """
    Return a color to assign to a strand
    which is guaranteed to be different than
    currentColor (which is typically that strand's
    current color).

    @param currentColor: The color to avoid returning,
                         or None if the next color is ok.
    @type  currentColor: RGB tuple

    @return: New color.
    @rtype: RGB tuple
    """
    global _strand_color_counter
    _new_color = _strandColorList[_strand_color_counter % len(_strandColorList)]
    _strand_color_counter += 1
    if _new_color == currentColor:
        return getNextStrandColor()
        # Note: this won't equal currentColor, since successive colors
        # in _strandColorList are always different.
    return _new_color

def getDuplexBasesPerTurn(conformation):
    """
    Returns the number of U{bases per turn} specified in the user preferences.

    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str

    @return: The number of bases per turn.
    @rtype: float
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    return dnaDict[str(conformation)]['BasesPerTurn']

def getDuplexRise(conformation):
    """
    Returns the duplex U{rise} specified in the user preferences.

    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str

    @return: The rise in Angstroms.
    @rtype: float
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    return dnaDict[str(conformation)]['DuplexRise']

def getDuplexLength(conformation, numberOfBases, duplexRise = 0):
    """
    Returns the duplex length (in Angstroms) given the conformation
    and number of bases.

    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str

    @param numberOfBases: The number of base-pairs in the duplex.
    @type  numberOfBases: int

    @param duplexRise: The duplex rise (in Angstroms). If not provided, the
                       user preference for DNA rise is used.

    @return: The length of the duplex in Angstroms.
    @rtype: float
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    assert numberOfBases >= 0
    assert duplexRise >= 0
    if duplexRise:
        duplexLength = duplexRise * (numberOfBases - 1)
    else:
        duplexLength = getDuplexRise(conformation) * (numberOfBases - 1)

    return duplexLength

def getNumberOfBasePairsFromDuplexLength(conformation, duplexLength, duplexRise = 0):
    """
    Returns the number of base-pairs in the duplex given the conformation,
    duplex length and duplex rise (optional).

    The number of base-pairs returned is NOT rounded to the nearest integer.
    The rounding is intentionally not done. Example: While drawing a dna line,
    when user clicks on the screen to complete the second endpoint, the actual
    dna axis endpoint might be trailing the clicked point because the total
    dna length is not sufficient to complete the 'next step'.
    Thus, by not rounding the number of bases, we make sure that the dna
    consists of exactly same number of bases as displayed by the rubberband line
    ( The dna rubberband line gives enough visual indication about this.
    see draweRibbons.drawDnaRibbons() for more details on the visual indication )

    @param conformation: "A-DNA", "B-DNA", or "Z-DNA"
    @type  conformation: str

    @param duplexLength: The duplex length (in Angstroms).
    @type  duplexLength: float

    @param duplexRise: The duplex rise (in Angstroms). If not provided, the
                       user preference for DNA rise is used.
    @type  duplexRise: float

    @return:  The number of base-pairs in the duplex.
    @rtype: int
    """
    assert conformation in ("A-DNA", "B-DNA", "Z-DNA")
    assert duplexLength >= 0
    assert duplexRise >= 0
    if duplexRise:
        numberOfBasePairs = 1.0005 + (duplexLength / duplexRise)
    else:
        numberOfBasePairs = 1.0005 + (duplexLength / getDuplexRise(conformation))

    #Explanation on adding '1.0005':
    #The number of base-pairs returned is NOT rounded to the nearest integer.
    #See why its not done in this method's docstring. But why do we add 1.005
    #instead of '1' while computing the number of basepairs? As of 2008-03-05
    #there a bug observed in the number this method returns if we just add '1'
    #Suppose a print statement shows the the numberOfBasePairs computed
    #above as 5.0. But int(numberOfBasePairs) returns 4 and not 5! This happens
    #sometime. I am not sure if in those cases the number of basepairs are
    #something like 4.99999......N which python rounds off to 5.0, but int of
    #that number actually returns 4. This is just a guess. But some print
    #statements do show this happening! So a workaround is to add some tolerance
    #of 0.0005 to 1. This addition is unlikely to have any user visible effect.
    return int(numberOfBasePairs)



def getDuplexRiseFromNumberOfBasePairs(numberOfBasePairs, duplexLength):
    """
    Returns the duplex rise from the number of base pairs and the duplex length
    @param numberOfBasePairs: number of base pairs in the duplx
    @type numberOfBasePairs: int
    @param duplexLength: The length of duplex.
    @type duplexLength: double
    @return: The duplex rise.
    @rtype: double
    """
    duplexRise = duplexLength/ (numberOfBasePairs - 1)
    return duplexRise


def getComplementSequence(inSequence):
    """
    Returns the complement of the DNA sequence I{inSequence}.

    @param inSequence: The original DNA sequence.
    @type  inSequence: str (possible error: the code looks more like it
                       requires a QString [bruce 080101 comment])

    @return: The complement DNA sequence.
    @rtype:  str (possible error: the code looks more like it
                  might return a QString [bruce 080101 comment])
    """
    #If user enters an empty 'space' or 'tab key', treat it as an empty space
    #in the complement sequence. (don't convert it to 'N' base)
    #This is needed in B{DnaSequenceEditor} where , if user enters an empty space
    #in the 'Strand' Sequence, its 'Mate' also enters an empty space.
    validSpaceSymbol  =  QString(' ')
    validTabSymbol = QString('\t')
    assert isinstance(inSequence, str)
    outSequence = ""
    for baseLetter in inSequence:
        if baseLetter not in basesDict.keys():
            if baseLetter in validSpaceSymbol:
                pass
            elif baseLetter in validTabSymbol:
                baseLetter = '\t'
            else:
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
