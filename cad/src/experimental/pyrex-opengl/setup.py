# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
import sys

from distutils.core import setup
from distutils.extension import Extension
try:
    from Pyrex.Distutils import build_ext
except:
    print "Problem importing Pyrex"
    sys.exit(1)

if sys.platform == "darwin":
    extra_compile_args = [ "-O", "-DMACOSX",
        "-I/System/Library/Frameworks/AGL.Framework/Headers" ]
    extra_link_args = [
        # the "-L" appears to not help with the bus error
        "-L/System/Library/Frameworks/OpenGL.framework/Versions/A/Libraries",
        "-lGL" ]
else:
    extra_compile_args = [
        # "-I/usr/share/doc/nvidia-7676/GL",   # Will's box
        "-I/usr/X11R6/include/GL",
        ]
    extra_link_args = [ "-L/usr/X11R6/lib", "-lGL" ]

setup(name = 'quux',
      ext_modules=[Extension("quux", ["quux.pyx", "bradg.cpp", "vector.c", "glextensions.cpp"],
                             depends = ["quux_help.c"],
                             extra_compile_args = extra_compile_args,
                             extra_link_args = extra_link_args
                             ),
                   ],
      cmdclass = {'build_ext': build_ext})
