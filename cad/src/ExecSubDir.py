#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
ExecSubDir.py

This is an odd little utility that might appear to do absolutely nothing.
All it does is call execfile() on its first argument.  It puts more
effort into validating that it has an argument than what it does to
that argument.

So, what is this good for?

Its entire purpose is to fiddle with the module search path.  All of
the python source files in the program expect to be imported with the
cad/src directory on the search path.  If you were to load a file from
a subdirectory using: python subdir/module.py, for example, then
subdir would be on the search path, but its parent directory
wouldn't. This would make imports of main directory modules fail
(or worse, get the wrong files, if we ever permit non-unique
module basenames). Instead, you can say: ./ExecSubDir.py subdir/module.py,
and it will get it right.

@author: Eric Messick
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details. 
"""

import sys

if (__name__ == '__main__'):
    if (len(sys.argv) < 2):
        print >> sys.stderr, "usage: %s fileToRun.py" % sys.argv[0]
        sys.exit(1)

    execfile(sys.argv[1])
