import sys

from distutils.core import setup
from distutils.extension import Extension
try:
    from Pyrex.Distutils import build_ext
except:
    print "Problem importing Pyrex"
    sys.exit(1)

if sys.platform == "darwin":
    extra_compile_args = [ "-O" ]
    extra_link_args = [ "-L/usr/X11R6/lib", "-lGL" ]
else:
    extra_compile_args = [ ]
    extra_link_args = [ "-L/usr/X11R6/lib", "-lGL" ]

setup(name = 'quux',
      ext_modules=[Extension("quux", ["quux.pyx", "bradg.c"],
                             depends = ["quux_help.c"],
                             extra_compile_args = extra_compile_args,
                             extra_link_args = extra_link_args
                             ),
                   ],
      cmdclass = {'build_ext': build_ext})
