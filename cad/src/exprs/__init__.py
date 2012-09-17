# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
__init__.py -- control initial import order and side effects,
whenever any submodule of this exprs package is used.

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

# Note: I don't know whether the following imports need to be relative
# to this package (as they are now). Until I know this, I will leave
# them relative. [bruce 080130]

# print "fyi: start of exprs.__init__.py"

# control initial import order:

import Exprs # probably not needed at present, but might be needed
    # if we revise __Symbols__.py to not import Exprs, or vice versa

# try to tell Pylint that we needed to do that import: [bruce 071023]
Exprs

# initialize some symbols using side effects
# [moved here from ExprsConstants.py, bruce 070914]

from __Symbols__ import Anything #070115
from __Symbols__ import Automatic, Something #070131

# Symbol docstrings -- for now, just tack them on (not yet used AFAIK):

Anything.__doc__ = """Anything is a legitimate type to coerce to which means 'don't change the value at all'. """
Anything._e_sym_constant = True

Automatic.__doc__ = """Automatic [###NIM] can be coerced to most types to produce a default value.
By convention, when constructing certain classes of exprs, it can be passed as an arg or option value
to specify that a reasonable value should be chosen which might depend on the values provided for other
args or options. """
    ###e implem of that:
    #  probably the type should say "or Automatic" if it wants to let a later stage use other args to interpret it,
    #  or maybe the typedecl could give the specific rule for replacing Automatic, using a syntax not specific to Automatic.
Automatic._e_sym_constant = True

Something.__doc__ = """Something is a stub for when we don't yet know a type or value or formula,
but plan to replace it with something specific (by editing the source code later). """
Something._e_eval_forward_to = Anything

# print "fyi: end of exprs.__init__.py"

# end
