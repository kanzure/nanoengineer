# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
gl_Scale.py - Details of loading the glScale functions.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

russ 080523: Factored out duplicate code from CS_workers.py and drawers.py .
"""

try:
    from OpenGL.GL import glScale
except:
    # The installed version of OpenGL requires argument-typed glScale calls.
    from OpenGL.GL import glScalef as glScale

from OpenGL.GL import glScalef
    # Note: this is NOT redundant with the above import of glScale --
    # without it, displaying an ESP Image gives a NameError traceback
    # and doesn't work. [Fixed by bruce 070703; bug caught by Eric M using
    # PyChecker; bug introduced sometime after A9.1 went out.]
