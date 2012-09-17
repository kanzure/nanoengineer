# Copyright 2005-2006 Nanorex, Inc.  See LICENSE file for details.
'''
setup.py (for sim code)

Distutils setup file -- tells distutils how to rebuild our custom extension modules.

NOTE: very similar to cad/src/setup.py in the cad cvs module.
Some comments and docstrings (more relevant to cad than to sim)
appear only in that file; others occur in both files.

$Id$

One way to run this might be "make extensions" or "make pyx"; see Makefile in this directory.
A more direct way is to ask your shell to do

  python setup.py build_ext --inplace

For up to date info about how to do this (especially for Windows), see the wiki.

Running this makes some output files and subdirectories, and prints lots of output.
I think it only recompiles what needs to be recompiled (based on modtimes), but I\'m not sure.
(I\'ve had a hard time finding any documentation about the internal workings of distutils,
though it\'s easy to find basic instructions about how to use it.)

This is based on the Pyrex example file Pyrex-0.9.3/Demos/Setup.py.
'''
__author__ = ['bruce', 'will']

import sys

from distutils.core import setup
from distutils.extension import Extension
try:
    from Pyrex.Distutils import build_ext
except:
    print "Problem importing Pyrex. You need to install Pyrex before it makes sense to run this."
    print "For more info see cad/src/README-Pyrex and/or "
    print "  http://www.nanoengineer-1.net/mediawiki/index.php?title=Integrating_Pyrex_into_the_Build_System"
    print "(If you already installed Pyrex, there's a bug in your Pyrex installation or in setup.py, "
    print " since the import should have worked.)"
    sys.exit(1)

# Work around Mac compiler hang for -O3 with newtables.c
# (and perhaps other files, though problem didn't occur for the ones compiled before newtables).
# Ideally we'd do this only for that one file, but we don't yet know a non-klugy way to do that.
# If we can't find one, we can always build newtables.o separately (perhaps also using distutils)
# and then link newtables.o here by using the extra_objects distutils keyword,
# which was used for most .o files in a prior cvs revision of this file.
# [change by Will, commented by Bruce, 051230.]
# Oops, now we've seen this on Linux, so back off optimization on all platforms
# wware 060327, bug 1758
extra_compile_args = [ "-DDISTUTILS", "-O" ]

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
                             depends = ["simhelp.c",
                                        "version.h",
                                        "bends.gen",
                                        "bonds.gen"],
                             extra_compile_args = extra_compile_args
                             ),
                   ],
      cmdclass = {'build_ext': build_ext})

# this exit reminds people not to "import setup" from nE-1 itself!
print "setup.py finished; exiting."
sys.exit(0)

#end
