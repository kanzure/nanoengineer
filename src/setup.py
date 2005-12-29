# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
setup.py

Distutils setup file -- tells distutils how to rebuild our custom extension modules.

$Id$

This file is NOT meant to be imported directly by nE-1.

One way to run it might be "make extensions"; see Makefile in this directory.
A more direct way is to ask your shell to do

  python setup.py build_ext --inplace
  
(I don't know if that works on Windows.)

Running this makes some output files and subdirectories, and prints lots of output.
I think it only recompiles what needs to be recompiled (based on modtimes), but I'm not sure.
(I've had a hard time finding any documentation about the internal workings of distutils,
though it's easy to find basic instructions about how to use it.)

==

For now [051202], all our custom extension modules are written in Pyrex, and we have exactly one,
which is just for testing our use of Pyrex and our integration of Pyrex code into our release-building system.

For plans and status related to our use of Pyrex, see:

  http://www.nanoengineer-1.net/mediawiki/index.php?title=Integrating_Pyrex_into_the_Build_System

See README-Pyrex for the list of related files and their roles.

This is based on the Pyrex example file Pyrex-0.9.3/Demos/Setup.py.

'''
__author__ = 'bruce'

import sys

from distutils.core import setup
from distutils.extension import Extension
try:
    from Pyrex.Distutils import build_ext
except:
    print "Problem importing Pyrex. You need to install Pyrex before it makes sense to run this."
    print "For more info see README-Pyrex and/or "
    print "  http://www.nanoengineer-1.net/mediawiki/index.php?title=Integrating_Pyrex_into_the_Build_System"
    print "(If you already installed Pyrex, there's a bug in your Pyrex installation or in setup.py, "
    print " since the import should have worked.)"
    sys.exit(1)

setup(name = 'Simulator',
      ext_modules=[Extension("sim", ["sim.pyx",
                                     "allocate.c",
                                     "dynamics.c",
                                     "globals.c",
                                     "hashtable.c",
                                     "interpolate.c",
                                     "jigs.c",
                                     "lin-alg.c",
                                     "minimize.c",
                                     "minstructure.c",
                                     "newtables.c",
                                     "part.c",
                                     "potential.c",
                                     "printers.c",
                                     "readmmp.c",
                                     "readxyz.c",
                                     "structcompare.c",
                                     "writemovie.c"],
                             ),
                   ],
      cmdclass = {'build_ext': build_ext})

# this exit reminds people not to "import setup" from nE-1 itself!
print "setup.py finished; exiting."
sys.exit(0)

#end
