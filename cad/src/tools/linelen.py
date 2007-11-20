#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
linelen.py - print max line length of each input file, assuming no tabs.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

import sys, os, time

# bruce 070304

def linelen(filename):
    file = open(filename, 'rU')
    lines = file.readlines()
    file.close()
    return max(map(len, lines)) - 1 # -1 is for the terminating newline
        ###BUG if file ends non-\n
        ###BUG if file contains tabs

# ==

filenames = sys.argv[1:]

program = os.path.basename(sys.argv[0])

if not filenames:
    msg = "usage: %s <files> [no stdin reading supported for now]" % (program,)
    print >> sys.stderr, msg
    sys.exit(1)
    
# not desirable (shell * sorts them, but user might want
# a different specific order): 
## filenames.sort()

for filename in filenames:
    if os.path.isfile(filename):
        print "linelen(%r) = %d" % (filename, linelen(filename))
    else:
        print "not found or not a plain file: %r" % filename
    continue

print "done"
sys.exit(0)

# end
