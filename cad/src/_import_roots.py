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

import main # the NE1 main program file

import ExecSubDir # a Python script which needs to remain in cad/src
    # [bruce 071008]

# end
