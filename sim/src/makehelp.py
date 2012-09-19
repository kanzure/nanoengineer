# Copyright 2006 Nanorex, Inc.  See LICENSE file for details.
import sys
import time
import os.path

if sys.platform == "darwin":
    extra_compile_args = [ "-O" ]
else:
    extra_compile_args = [ ]

DISTUTILS_FLAGS = None

if sys.platform != "win32":
    from distutils.core import setup
    from distutils.extension import Extension
    import Pyrex.Distutils

    class local_build_ext(Pyrex.Distutils.build_ext):
        def __init__(self, dist):
            Pyrex.Distutils.build_ext.__init__(self, dist)
            self.distn = dist
        def run(self):
            # Pieces of the distutils.command.build_ext.run() method
            global DISTUTILS_FLAGS
            from distutils.ccompiler import new_compiler
            from distutils.sysconfig import customize_compiler
            compiler = new_compiler(compiler=None,
                                    verbose=self.verbose,
                                    dry_run=self.dry_run,
                                    force=self.force)
            customize_compiler(compiler)
            DISTUTILS_FLAGS = (compiler.compiler_so +
                               self.distn.ext_modules[0].extra_compile_args)

    sys_argv = sys.argv
    sys.argv = ["setup.py", "build_ext"]
    setup(name = 'Simulator',
          ext_modules=[Extension("sim", [ ],
                                 extra_compile_args = extra_compile_args)],
          cmdclass = {'build_ext': local_build_ext})
    sys.argv = sys_argv

def hString(name, s, prefix=""):
    import string
    retval = "#define " + name + " \\\n\"" + prefix
    # replace double-quote with escaped-double-quote
    s = string.replace(s, "\"", "\\\"")
    # replace line terminations with end-of-last-line plus start-of-next-line
    s = string.replace(s, "\n", ("\\n\"\\\n\"") + prefix)
    return retval + s + "\\n\"\n"

#def cString(name, s, prefix=""):
#    import string
#    retval = "char " + name + "[] = \"\\\n" + prefix
#    # replace double-quote with escaped-double-quote
#    s = string.replace(s, "\"", "\\\"")
#    # replace line terminations with end-of-last-line plus start-of-next-line
#    s = string.replace(s, "\n", ("\\n\\\n") + prefix)
#    return retval + s + "\\n\";\n"

######################################

print hString("TRACE_PREFIX",
              "uname -a: " + sys.argv[3] + "\n",
              "# ")

print hString("TRACE_PREFIX_NON_DISTUTILS",
              "CFLAGS: " + sys.argv[1] + "\n" +
              "LDFLAGS: " + sys.argv[2] + "\n",
              "# ")

if DISTUTILS_FLAGS != None:
    distutils = " ".join(DISTUTILS_FLAGS)
else:
    distutils = "None"

print hString("TRACE_PREFIX_DISTUTILS",
              "Python " + sys.version.replace("\n", " ") + "\n" +
              distutils + "\n",
              "# ")
