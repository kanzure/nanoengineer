# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
_import_roots.py - import all toplevel files in the import dependency hierarchy

$Id$

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

import extensions # a file optionally imported at runtime by NE1,
    # but which must not yet have an import statement in NE1
    # (since py2app/py2exe should not follow it for import dependencies,
    #  lest it get confused by the lack of the optional dll which
    #  this file tries to import)
    # [bruce 071008]

import setup # build script for the optional dlls loaded by extensions.py
    # (called from Makefile but not yet part of the NE1 build process)
    # [bruce 071008]

import setup2 # build script for samevals.c dll (experimental, optional)
    # [bruce 071008]

import graphics.drawables.Selobj as Selobj # a draft API file, soon to be renamed and imported from NE1
    # [bruce 071008]

# end
