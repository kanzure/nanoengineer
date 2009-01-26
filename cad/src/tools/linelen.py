#!/usr/bin/env python
"""
linelen.py - print max line length of each input file, assuming no tabs.
Also print line number of at least one line which is that long.

@author: Bruce
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
"""

import sys, os, time

# bruce 070304, added lineno 090126

def linelen(fn):
    """
    Given filename fn,
    return max line length (assuming no tabs and all lines \n-terminated),
    and one of the line numbers it occurs on (the first one, in current implem).
    """
    file = open(fn, 'rU')
    lines = file.readlines()
    file.close()
    if not lines:
        return 0, 0
    rawlengths = map(len, lines)
    maxlen = max(rawlengths) - 1 # -1 is for the terminating newline
        ###BUG if file ends non-\n
        ###BUG if file contains tabs
    lineno = 1 + rawlengths.index(maxlen + 1)
    return maxlen, lineno

# ==

if __name__ == '__main__':
    filenames = sys.argv[1:]

    program = os.path.basename(sys.argv[0])

    if not filenames:
        msg = "usage: %s <files> [no stdin reading supported for now]" % (program,)
        print >> sys.stderr, msg
        sys.exit(1)

    for fn in filenames:
        if os.path.isfile(fn):
            maxlen, lineno = linelen(fn)
            print "linelen(%r) = %d (line %d)" % (fn, maxlen, lineno)
        else:
            print "not found or not a plain file: %r" % fn
        continue

    print "done"

# end
