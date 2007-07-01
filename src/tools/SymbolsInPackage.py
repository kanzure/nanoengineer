#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
   SymbolsInPackage.py

   Reads a list of package names from stdin, and writes to stdout a
   list of all of the symbols defined in that package in the same
   format as FindPythonGlobals.py does.
"""

import sys

if (__name__ == '__main__'):
    for line in sys.stdin:
        package = line.strip()
        try:
            exec "import " + package
            globalSymbols = eval("dir(%s)" % package)
            for sym in globalSymbols:
                if (not sym.startswith("_")):
                    print "%s: %s" % (sym, package)
        except:
            print >>sys.stderr, "Failed to process " + package
