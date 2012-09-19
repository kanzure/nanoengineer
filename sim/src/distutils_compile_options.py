# Copyright 2006 Nanorex, Inc.  See LICENSE file for details.
import sys
import distutils.sysconfig
import distutils.ccompiler

class FakeCompiler:
    def __init__(self):
        self.compiler_type = distutils.ccompiler.get_default_compiler()
    def set_executables(self, **kw):
        for k in kw: setattr(self, k, kw[k])

mcc = FakeCompiler()
distutils.sysconfig.customize_compiler(mcc)

if len(sys.argv) < 2:
    import pprint
    pprint.pprint(mcc.__dict__)
else:
    for arg in sys.argv[1:]:
        cmd = getattr(mcc, arg)
        if cmd.startswith("gcc ") or cmd.startswith("g++ "):
            cmd = cmd[4:]
        print cmd
