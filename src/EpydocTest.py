# Copyright (c) 2007 Nanorex, Inc.  All rights reserved.
"""
EpydocTest.py Tests to see if a module is being imported by epydoc in
order to document it, rather than for actual use.

To use:

import EpydocTest

if (EpydocTest.documenting()):
    ... documentation behavior
else:
    ... actual run behavior

$Id$
"""

__author__ = "EricM"

import sys

def documenting():
    if ('epydoc' in sys.modules):
        return True
    return False
