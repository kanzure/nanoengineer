"""
Minimal setup.py example, run with:
% python setup.py py2app
"""

import sys
print "running Distribution/setup.py, sys.argv is %r" % (sys.argv,)

from distutils.core import setup
import py2app
setup(
    
    app = ['NanoEngineer-1.py'],
)
