# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
gpl_only.py

This module contains code which is only distributed in the GPL version,
since providing this code might violate the commercial-version licenses of
Qt and/or PyQt. Specifically (as I understand it -- bruce 041217), those
licenses require anyone who writes new code which uses the Qt or PyQt APIs
(to connect to the commercial versions of PyQt or Qt) to purchase a
commercial license for those packages. This generally affects only
developers, but if our product lets users run arbitrary Python code (which
might include general use of Qt, via PyQt), it affects users too; so
functions that permit users to run arbitrary Python code can't be
distributed as part of the commercial version.

In the future we might permit all users to run Python code provided it
doesn't use any functions imported from PyQt; but it's hard to do that well
enough, and for now these functions are only provided for debugging, so it's
easiest to just leave them out of the commercial version. When we later add
a scripting ability, we'll have to revisit this issue.

Other modules which import functions from this one must deal with the
absence of this module. Generally, for any function in this module, most
other code should not call it directly, but call some wrapper function, in a
module appropriate to the function's purpose, where the wrapper function's
only job is to handle the case where this module gpl_only is not available.

$Id$
'''

import sys, os

# note: as of 12/3/04 I am told that sys.platform is always one of the
# following, on our supported systems:
#
# - "linux2" (on Mandrake 10.x) (GPL)
# - "darwin" (on Mac OS X 10.3) (GPL)
# - "win32" (on WindowsXP)      (non-GPL)

if sys.platform not in ['darwin','linux2']:
    print "sys.platform == %r; this is not known to be a GPL version." % (sys.platform,)
    try:
        fname = os.path.basename(__file__)
    except:
        fname = ""
    msg = "This file %r should not have been distributed with your version!!! Exiting." % (fname,)
    print msg
    #e dialog?
    sys.exit(1)

def _execfile_in_globals(filename, globals):
    execfile(filename, globals)

def _exec_command_in_globals( command, globals):
    exec command in globals

# end
