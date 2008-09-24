# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
B_Dna_Generator.py -- DNA duplex generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenHelper.py.
"""

import foundation.env as env
from platform_dependent.PlatformDependent import find_plugin_dir
from utilities.Log      import orangemsg
from dna.model.Dna_Constants import getDuplexBasesPerTurn
from model.elements import PeriodicTable

Element_Ae3 = PeriodicTable.getElement('Ae3')

from dna.model.Dna_Constants import  dnaDict

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1

from dna.generators.Dna_Generator import Dna_Generator

class B_Dna_Generator(Dna_Generator):
    """
    Provides an atomistic model of the B form of DNA.
    """
    form       =  "B-DNA"
    baseRise   =  dnaDict['B-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED

    basesPerTurn = getDuplexBasesPerTurn('B-DNA')   

    pass




