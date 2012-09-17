# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
A_Dna_PAM3_Generator.py -- DNA duplex generator helper class, based on empirical data.

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

basepath_ok, basepath = find_plugin_dir("DNA")
if not basepath_ok:
    env.history.message(orangemsg("The cad/plugins/DNA directory is missing."))


from dna.generators.A_Dna_Generator import A_Dna_Generator

class A_Dna_PAM3_Generator(A_Dna_Generator):
    """
    Provides a PAM5 reduced model of the B form of DNA.

    @attention: This class is not implemented yet.
    """
    model = "PAM3"
