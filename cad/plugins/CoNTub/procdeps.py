#!/usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
# $Id$
# This is used only for "make deps"

import sys, re

srcdir = sys.argv[1]
objdir = sys.argv[2]
substitution = sys.argv[3]
objs = sys.argv[4:]

# This is a little kludgey. The idea is to allow either C files (with
# ".o:.c") or C++ files (with ".o:.cpp") and ideally as many other
# filetypes as possible. For instance, Java could use ".class:.java".
# But there will likely be reasonable situations for which this won't
# work.
obj_ending, src_ending = substitution.split(':')

# Perform a pattern find-and-replace for all occurrences in a string.
def subAll(pattern, repl, str):
    while True:
        s = re.sub(pattern, repl, str)
        if s == str:
            return str
        str = s

print '# Automatically generated dependencies from procdeps.py'

for obj in objs:
    # Generate the source file for this object file, and put it in SRCDIR.
    src = re.sub(obj_ending + '$', src_ending, obj)
    src = re.sub(objdir + '/', '$(SRCDIR)/', src)
    # Put this object file in OBJDIR.
    obj = re.sub(objdir + '/', '$(OBJDIR)/', obj)
    # Print a dependency line.
    print obj + ': ' + src
    print '\t$(CXX) $(CXXFLAGS) -c -o %s %s' % (obj, src)

for L in sys.stdin.readlines():
    L = L.rstrip()
    # Remove all absolute header files, like /usr/include stuff.
    L = subAll(' /[^ ]*\.h', '', L)
    if L and not L.startswith('#') and not L.rstrip().endswith(':'):
        obj, hfiles = L.split(':')
        # Put this object file in OBJDIR.
        obj = re.sub(srcdir + '/', '$(OBJDIR)/', obj)
        # Put the header files in SRCDIR.
        hfiles = subAll(srcdir + '/', '$(SRCDIR)/', hfiles)
        # Print the modified dependency line.
        print obj + ':' + hfiles
