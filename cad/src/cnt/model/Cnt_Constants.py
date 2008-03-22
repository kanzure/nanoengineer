# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Cnt_Constants.py -- constants for (carbon and boron nitride) nanotubes.

@author: Mark Sims
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

- Mark, 2008-03-08 - Created using a copy of Dna_constants.py
"""

import foundation.env as env

# Common nanotube helper functions. ######################################

def getCntLength(type, numberOfUnits, cntRise = 0):
    """
    Returns the nanotube length (in Angstroms) given the type
    and number of bases.
    
    @param type: "Carbon" or "Boron Nitride"
    @type  type: str
    
    @param numberOfUnits: The number of units in the nanotube.
    @type  numberOfUnits: int
    
    @param cntRise: The nanotube rise (in Angstroms). If not provided, the 
                    user preference for DNA rise is used.
    
    @return: The length of the nanotube in Angstroms.
    @rtype: float
    """
    assert type in ("Carbon", "Boron Nitride")
    assert numberOfUnits >= 0
    assert cntRise >= 0
    if cntRise:
        cntLength = cntRise * (numberOfUnits - 1)
    else:
        cntLength = getCntRise(type) * (numberOfUnits - 1)
        
    return cntLength

def getCntRise(type = 'Carbon', n = 5, m = 5):
    """
    Returns the nanotube U{rise} specified in this function.
    
    @param type: Unused.
    @type  type: str
    
    @return: The rise in Angstroms.
    @rtype: float
    """
    # Need to create table, or better yet, a formula to return rise.
    # I'm sure this is doable, but I need to research it further to learn
    # how to compute rise from these params. --Mark 2008-03-12
    rise = 2.5 # default
    if m == 0:
        rise = 2.146
    if m == 5:
        rise = 2.457
        
    print "Type=", type, ", (n, m)=", n, m,", Rise=", rise
    
    return rise

def getNumberOfCellsFromCntLength(cntLength, cntType = "Carbon", cntRise = 2.5):
    """
    Returns the number of repeating cell units in the nantube given the type,  
    cnt length and cnt rise (optional). 
    
    The number of cnt units returned is NOT rounded to the nearest integer. 
    The rounding is intentionally not done. Example: While drawing a cnt line, 
    when user clicks on the screen to complete the second endpoint, the actual 
    dna axis endpoint might be trailing the clicked point because the total 
    dna length is not sufficient to complete the 'next step'. 
    Thus, by not rounding the number of bases, we make sure that the dna 
    consists of exactly same number of bases as displayed by the rubberband line    
    ( The dna rubberband line gives enough visual indication about this. 
    see draweRibbons.drawDnaRibbons() for more details on the visual indication )
    
    @param cntLength: The nanotube length (in Angstroms).
    @type  cntLength: float
    
    @param cntType: "Carbon" or "Boron Nitride"
    @type  cntType: str

    @param cntRise: The nanotube rise (in Angstroms). If not provided, the 
                       user preference for DNA rise is used.
    @type  cntRise: float
    
    @return:  The number of base-pairs in the nanotube.
    @rtype: int
    """
    assert cntType in ("Carbon", "Boron Nitride")
    assert cntLength >= 0
    assert cntRise >= 0
    if cntRise:
        numberOfCntUnits = 1.0005 + (cntLength / cntRise)
    else:
        numberOfCntUnits = 1.0005 + (cntLength / getCntRise(cntType))
    
    #Explanation on adding '1.0005':
    #The number of base-pairs returned is NOT rounded to the nearest integer.
    #See why its not done in this method's docstring. But why do we add 1.005
    #instead of '1' while computing the number of basepairs? As of 2008-03-05
    #there a bug observed in the number this method returns if we just add '1'
    #Suppose a print statement shows the the numberOfCntUnits computed
    #above as 5.0. But int(numberOfCntUnits) returns 4 and not 5! This happens 
    #sometime. I am not sure if in those cases the number of basepairs are
    #something like 4.99999......N which python rounds off to 5.0, but int of 
    #that number actually returns 4. This is just a guess. But some print
    #statements do show this happening! So a workaround is to add some tolerance
    #of 0.0005 to 1. This addition is unlikely to have any user visible effect.
    return int(numberOfCntUnits)

def getCntRiseFromNumberOfCells(numberOfCntUnits, cntLength):
    """
    Returns the cnt rise given the number of cnt cell units and the nanotube
    length.
    
    @param numberOfCntUnits: number of cnt units in the nanotube.
    @type numberOfCntUnits: int
    
    @param cntLength: The length of nanotube. 
    @type cntLength: double
    
    @return: The nanotube rise. 
    @rtype: double
    """
    cntRise = cntLength/ (numberOfCntUnits - 1)
    return cntRise
