# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
_import_roots.py - import all toplevel files in the import dependency hierarchy

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details. 

Note: most of the files we import here are for separate main programs, never
normally imported into one process; this file exists for the use of import
dependency analysis tools, especially so they will not think these files
are no longer needed in cad/src, and so text searches for references to
these files (e.g. when renaming them) will find their entries in this list.

Note: all entries in this file should be signed and dated by whoever adds
or maintains them (the entries, not the imported files),
with a comment which mentions why they are needed
(except when it's obvious, like for main.py).
When no longer needed, they should be removed.
"""

# Note: our toplevel package 'commands'
# has the same name as a module in the Python 2.3 library.
# ('commands' is Unix only (including Mac), and probably old.)
#
# This is a potential problem for anything which might want to
# import both our package and the Python library module with
# the same name, and it has impacts on ordering of sys.path
# for something which wants to import either one (e.g. NE1,
# or any script which imports anything from NE1, such as certain
# build scripts).
#
# In the long run, this ought to be cleaned up, perhaps by renaming
# our toplevel packages to avoid those conflicts, and/or making use
# of new import features in later versions of Python, e.g. the new
# more precise kinds of relative imports like "from .. import x".
#
# In the meantime, this situation needs to be monitored as we port
# to newer versions of Python.

# (It got a lot better as of 080708, when we renamed 'platform'
#  to 'platform_dependent'.)
#
# [bruce 080602 comment, revised 080710]

import main # the NE1 main program file

import ExecSubDir # a Python script which needs to remain in cad/src
    # [bruce 071008]

# end
