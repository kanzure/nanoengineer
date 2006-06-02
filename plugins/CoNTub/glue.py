# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
glue.py -- Python glue for plugin API

$Id$

Stuff to make plugins work.

-------- KLUDGES (before I forget them) -----------

Where we build the commands, it will only work for Linux and Mac.

Massive amounts of this stuff will change or go away when Bruce
commits his Parameterized Dialog stuff.

"""

import os
import sys
from Plugins import Parameter, ParameterSet, File

name = "CoNTub"
version = 3.1416
author = ['S. Melchor', 'J. A. Dobado']
url = 'http://www.ugr.es/~gmdm/java/contub/contub.html'
email = 'smelchor@ugr.es'

citation = '''"CoNTub: an algorithm for connecting two arbitrary carbon nanotubes."
S. Melchor; J.A. Dobado. Journal of Chemical Information and Computer
Sciences, 44, 1639-1646 (2004)</cite>'''

description = [
    'CoNTub code',
    'Encyclopedic babble about what CoNTub is all about....'
    ]

# dependencies are optional
#
#dependencies = {
#    'jvm': '1.4.2',
#    'perl': '5.0.1'
#    }

sponsor = [
    'Nanotubes',   # keyword
    'Zyvex, Inc.',  # name
    'http://www.zyvex.com',  # url
    'Some words of glowing praise for our sponsor...'   # ad copy
    'iVBORw0KGgoAAAANSUhEUgAAAGsAAAA3CAIAAACEkSPXAAAABmJLR0QA/wD/AP+g...'  # logo
    ]

files = [
    # ('icon', 'CoNTub.png'),
    File('README', File.TEXT),
    File('SW', File.EXECUTABLE, os=File.LINUX | File.MAC),
    File('SW.exe', File.EXECUTABLE, os=File.WINDOWS),
    File('MW', File.EXECUTABLE, os=File.LINUX | File.MAC),
    File('MW.exe', File.EXECUTABLE, os=File.WINDOWS),
    File('HJ', File.EXECUTABLE, os=File.LINUX | File.MAC),
    File('HJ.exe', File.EXECUTABLE, os=File.WINDOWS),
    ]

## class Sequence(Parameter):
##     def valid(self):
##         assert len(self.value) > 0, 'Zero-length sequence'
##         for ch in self.value:
##             assert ch in 'ACGT \t\r\n', 'Bogus base: ' + ch
##     def complement(self):
##         self.value = map(lambda ch: {'A':'T', 'T':'A', 'C':'G', 'G':'C'}[ch],
##                          self.value)
##     def reverse(self):
##         v = list(self.value)
##         v.reverse()
##         self.value = ''.join(v)

## extraControls = [
##     # The stuff in the "Parameterized UI Dialogs" page has a lot of
##     # ideas about this, including a hierarchical description.
##     ('click', 'Complement',
##      lambda parameters=parameters: parameters.Sequence.complement()),
##     ('click', 'Reverse',
##      lambda parameters=parameters: parameters.Sequence.reverse()),
##     ]

################################################################
#
# Here's what I'd like for the Parameterized UI Dialog. I would
# like to hand it my ParameterSet, which is pretty thoroughly
# self-describing. It carries the current values of the parameters
# as well as the descriptiions of their types and validation tests.
#
# Then I also want to be able to specify extra controls. If this
# were a DNA generator, I would want two pushbuttons to reverse and
# to complement the base sequence.
#

parameters = ParameterSet()
parameters.add('Flavor', Parameter.ENUM, ['Single-wall', 'Multi-Wall', 'Heterojunction'])
parameters.add('Termination', Parameter.ENUM, ['None', 'H', 'N'])
parameters.add('N1', Parameter.INT)
parameters.add('M1', Parameter.INT)
parameters.add('Length1', Parameter.FLOAT)
parameters.add('NumShells', Parameter.INT)
parameters.add('Clearance', Parameter.FLOAT)
parameters.add('N2', Parameter.INT)
parameters.add('M2', Parameter.INT)
parameters.add('Length2', Parameter.FLOAT)

def validate_parameters():
    parameters.valid('Flavor', 'Termination', 'N1', 'M1', 'Length1')
    flavor = parameters.Flavor.value
    n1 = parameters.N1.value
    m1 = parameters.M1.value
    len1 = parameters.Length1.value
    assert n1 > 0
    assert n1 >= m1 >= 0
    assert len1 > 0.0
    if flavor == 'Single-wall':
        pass
    elif flavor == 'Multi-wall':
        parameters.valid('NumShells', 'Clearance')
    elif flavor == 'Heterojunction':
        parameters.valid('N2', 'M2', 'Length2')
        n2 = parameters.N2.value
        m2 = parameters.M2.value
        len2 = parameters.Length2.value
        assert n2 > 0
        assert n2 >= m2 >= 0
        assert len2 > 0.0

def build_struct(index):
    flavor = parameters.Flavor.value
    term = {
        'None': 0,
        'H': 1,
        'N': 7
        }[parameters.Termination.value]
    if sys.platform == 'win32':
        ending = '.exe'
    else:
        ending = ''
    if flavor == 'Single-wall':
        cmd = './SW%s %d %d %f %d' % (
            ending,
            parameters.N1.value,
            parameters.M1.value,
            parameters.Length1.value,
            term)
    elif flavor == 'Multi-wall':
        cmd = './MW%s %d %d %f %d %f %d' % (
            ending,
            parameters.N1.value,
            parameters.M1.value,
            parameters.Length1.value,
            parameters.NumShells.value,
            parameters.Clearance.value,
            term)
    elif flavor == 'Heterojunction':
        cmd = './HJ%s %d %d %f %d %d %f %d' % (
            ending,
            parameters.N1.value,
            parameters.M1.value,
            parameters.Length1.value,
            parameters.N2.value,
            parameters.M2.value,
            parameters.Length2.value,
            term)
    cmd += ' %d > /tmp/nt.mmp' % index
    print cmd
    os.system(cmd)
    return '/tmp/nt.mmp'
