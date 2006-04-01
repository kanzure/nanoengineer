# This file is part of a mitigation of bug 1724;
# it is partly handmade and partly automatically generated.
# Developers: don't commit any changes unless you have full understanding of bug 1724.
# [wware circa 060320 & bruce 060327] 

'''
all_mac_imports.py

$Id$
'''

import sys, os

sys.path = sys.argv[1].split(":")

# do the same thing py2app site.py does: (don't know if this is required or if it helps)
sys.argv[0] = os.path.abspath(sys.argv[0])

try:
    debug_1724 = int(os.environ['debug_1724']) # sometimes passed in from parent process
except:
    debug_1724 = False

if debug_1724:
    # either this arg is not working, or the prints aren't
    print >>sys.stderr, "printing debug_1724 info from all_mac_imports subprocess to stderr"
    _old_import = __import__
    def __import__(*args, **kws):
        arg = args[0]
        print >>sys.stderr, "about to import " + arg # helps determine which module had the problem
        return _old_import(*args, **kws)
    __builtins__.__import__ = __import__ # this is required, else no effect.

import qt

print "QT IMPORT WORKED" # this string is detected in our output by the parent process, atom.py
sys.stdout.flush() #k needed?

import multiarray   # this has the problem

if "we should be faster": 
    # for speed; the above might be enough to test, and this saves 4-5 seconds [bruce 060327]
    # (it would be good to figure out which of the other ones are slow)
    print "ALL IMPORTS COMPLETED" # this string is detected in our output by the parent process, atom.py
    
    sys.exit(0)    # # # 

import time
import types
import sip
import cPickle
import copy_reg
import __builtin__
import cStringIO
import Numeric
import numeric_version
import _numpy
import umath
import Precision
import string
import strop
import math
import ArrayPrinter
import pickle
import marshal
import struct
import re
import sre
import sre_compile
import _sre
import sre_constants
import sre_parse
import warnings
import binascii
import copy
import StringIO
import errno
import __main__
import OpenGL.GL
import os.path
import operator
import OpenGL.GLU
import OpenGL.GLUT
import OpenGL.GLE
import LinearAlgebra
import lapack_lite
import MLab
import RandomArray
import ranlib
import commands
import thread
import shelve
import UserDict
import anydbm
import dbm
import dumbdbm
import whichdb
import idlelib.Delegator
import Image
import FixTk
import _imaging
import ImagePalette
import array
import ImageOps
import PngImagePlugin
import ImageFile
import traceback
import linecache
import webbrowser
import ic
import icglue
import Carbon
import _Res
import Carbon.File
import _File
import macostools
import MacOS
import unittest

print "ALL IMPORTS COMPLETED"
# warning: this line might not run, instead there might be a duplicate of it above
# with an early exit, which runs.

# end
