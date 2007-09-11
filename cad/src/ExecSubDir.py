#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
ExecSubDir.py

This is an odd little utility that appears to do absolutely nothing.
All it does is call execfile() on it's first argument.  It puts more
effort into validating that it has an argument than what it does to
that argument.

So, what is this good for?

It's entire purpose is to fiddle with the module search path.  All of
the python source files in the program expect to be imported with the
cad/src directory on the search path.  If you were to load a file from
a subdirectory using: python subdir/module.py, for example, then
subdir would be on the search path, but it's parent directory
wouldn't.  Instead, you can say: ./ExecSubDir.py subdir/module.py, and
it will get it right.

@author: Eric Messick
@version: $Id$
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""


import sys

if (__name__ == '__main__'):
    if (len(sys.argv) < 2):
        print >>sys.stderr, "usage: %s fileToRun.py" % sys.argv[0]
        sys.exit(1)

    execfile(sys.argv[1])
