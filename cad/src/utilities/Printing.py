# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

"""
Utilities for formatting various data types as strings.

@author:    Eric Messick
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

def Vector3ToString(v):
    """
    Print a 3-vector surrounded by angle brackets:  '<1, 2, 3>'
    Used for povray colors.
    """
    return "<" + str(v[0]) + "," + str(v[1]) + "," + str(v[2]) + ">"    
