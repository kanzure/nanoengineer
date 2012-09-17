# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
A_Dna_Generator.py -- DNA duplex generator helper class, based on empirical data.

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

from dna.model.Dna_Constants import dnaDict
basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))

RIGHT_HANDED = -1

from dna.generators.Dna_Generator import Dna_Generator


class A_Dna_Generator(Dna_Generator):
    """
    Provides an atomistic model of the A form of DNA.

    The geometry for A-DNA is very twisty and funky. We need to to research
    the A form since it's not a simple helix (like B) or an alternating helix
    (like Z).

    @attention: This class is not implemented yet.
    """
    form       =  "A-DNA"
    baseRise   =  dnaDict['A-DNA']['DuplexRise']
    handedness =  RIGHT_HANDED

