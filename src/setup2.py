# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
__author__ = 'Will'

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

# Hack to prevent -O2/-O3 problems on the Mac
#if sys.platform == "darwin":
#    extra_compile_args = [ "-DDISTUTILS", "-O" ]

extra_compile_args = [ "-DDISTUTILS", "-g" ]

setup(name = 'Simulator',
      ext_modules=[Extension("samevals", ["samevals.c"],
                             extra_compile_args = extra_compile_args
                             ),
                   ],
      cmdclass = {'build_ext': build_ext})
