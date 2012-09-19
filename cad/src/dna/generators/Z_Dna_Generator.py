# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaDuplex.py -- DNA duplex generator helper classes, based on empirical data.

@author: Mark Sims
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Mark 2007-10-18:
- Created. Major rewrite of DnaGenHelper.py.
"""

import foundation.env as env
import os

from math    import sin, cos, pi
from utilities.debug import print_compact_traceback, print_compact_stack
from platform_dependent.PlatformDependent import find_plugin_dir
from files.mmp.files_mmp import readmmp
from geometry.VQT import Q, V, angleBetween, cross, vlen
from utilities.Log      import orangemsg
from utilities.exception_classes import PluginBug
from utilities.constants import gensym
from utilities.prefs_constants import dnaDefaultStrand1Color_prefs_key
from utilities.prefs_constants import dnaDefaultStrand2Color_prefs_key
from utilities.prefs_constants import dnaDefaultSegmentColor_prefs_key

from dna.model.Dna_Constants import getDuplexBasesPerTurn

##from dna.updater.dna_updater_prefs import pref_dna_updater_convert_to_PAM3plus5

from simulation.sim_commandruns import adjustSinglet
from model.elements import PeriodicTable
from model.Line import Line

from model.chem import Atom_prekill_prep
Element_Ae3 = PeriodicTable.getElement('Ae3')

from dna.model.Dna_Constants import basesDict, dnaDict
from dna.model.dna_model_constants import LADDER_END0

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1
LEFT_HANDED  =  1


from geometry.VQT import V, Q, norm, cross  
from geometry.VQT import  vlen
from numpy.oldnumeric import dot

from utilities.debug import print_compact_stack
from model.bonds import bond_at_singlets

from dna.generators.Dna_Generator import Dna_Generator

class Z_Dna_Generator(Dna_Generator):
    """
    Provides an atomistic model of the Z form of DNA.
    """

    form       =  "Z-DNA"
    baseRise   =  dnaDict['Z-DNA']['DuplexRise']
    handedness =  LEFT_HANDED

