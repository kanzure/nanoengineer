#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
fixNewlines.py - standardize newlines in each input file, nondestructively
(by producing differently named output files). Also print details of
what kind of newlines were found.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

Usage: fixNewlines <filename>...

1. prints a table of counts of the different kinds of line-endings (\n, \r, etc)
OR SEQUENCES OF LINE-ENDINGS in the file. I.e. a unix blank line, \n\n, is treated as a
different kind of line-ending-sequence, so the program needs no knowledge or ability
to parse \r\n into one lineending but \n\r into two.

2. replaces \r with \n and makes a new file with a modified name.
"""

import sys, os

def process(pat, found):
    n = found.get(pat,0)
    found[pat] = n+1
    pass

def printres(found):
    items_to_sort = []
    for pat, count in found.items():
        items_to_sort += [(len(pat), pat, count),]
    items_to_sort.sort()
    for len1, pat, count in items_to_sort:
        print "%d       %s" % (count,pat)
    if len(items_to_sort) == 0:
        # nothing was printed above, so...
        print("no \\n or \\r found in that file!")
    pass


def dofile1(file):
    found = {}
    pat = ""
    while 1:
        char1 = file.read(1)
        if len(char1) < 1:
            break
        if char1 == "\r":
            pat += '\\r' # this is two chars, \ and r, so it prints like \r
        elif char1 == "\n":
            pat += '\\n'
        else:
            if pat:
                process(pat,found)
            pat = ""
    if pat:
        process(pat,found)
    printres(found)


def dofile2(file, fileoutname, bakname = None, fileinname = None):
    """
    turn any kind of newline (incl \r\n) into \n,
    and if there were any changes,
    write modified file to new file
    """
    output = ""
    char1 = ""
    fixed = 0
    while 1:
        if output and (len(output) % 100000 == 0):
            print "did %d so far" % len(output)
        char0 = char1
        char1 = file.read(1)
        # Note: this seems to be fast enough -- it must be more buffered
        # than it looks. But the accumulation of output by string concat
        # is quadratic time (I guess), so for 10^5 chars it took a minute
        # or so. (It does this even if dofile1 found no \rs -- we should
        # fix that too.)
        if len(char1) < 1:
            break
        if char1 == "\r": # might be lone \r or start of \r\n
            output += '\n' # either way, we have a newline here, and we're changing the file
            fixed = 1
        elif char1 == "\n":
            if char0 != '\r':
                output += char1 # lone \n
            else:
                fixed = 1 # \n after \r; skip it, thus output differs from file here
        else:
            output += char1 # most chars get included unchanged
    # (it doesn't matter whether the last char in the file was \r or not)
    if (fixed):
        print("writing to \"%s\"\n" % fileoutname)
        fileout = open(fileoutname, 'wb')
        fileout.write(output)
        fileout.close()
        if (bakname):
            print("moving that over original file \"%s\", backed up into \"%s\"\n" % (fileinname,bakname))
            # caller still has it open for reading, but that should not matter provided it immediately closes it
            os.rename(fileinname, bakname)
            os.rename(fileoutname, fileinname)
    else:
        print("not writing to \"%s\"\n" % fileoutname)
    pass


table_header_line = "count   newline-sequence-type\n-----   ----------" # only for dofile1()

# following code calls dofile1 and dofile2 on named files

def do_filename(filename):
    print('\nfile: "%s"' % filename)
    print(table_header_line)
    try:
        file = open(filename, 'rb')
        dofile1(file)
        file.close()
    except:
        print "exception while doing1 that file:", \
            sys.exc_info()[0], sys.exc_info()[1]
    sys.stdout.flush()
    try:
        file = open(filename, 'rb')
        dofile2(file, filename + "-fixed", bakname = filename + "-badnls", fileinname = filename)
        file.close()
    except:
        print "exception while doing2 that file:", \
            sys.exc_info()[0], sys.exc_info()[1]
    sys.stdout.flush()
    pass

##def do_stdin():
##    print("\nsys.stdin:")
##    try:
##        file = sys.stdin
##        dofile2(file, "stdin" + "-fixed")
##    except:
##        print "exception while doing2 sys.stdin:", \
##            sys.exc_info()[0], sys.exc_info()[1]
##    sys.stdout.flush()
##    pass

if __name__ == "__main__":

    filenames = sys.argv[1:]

    program = os.path.basename(sys.argv[0])

    if not filenames:
        msg = "usage: %s <files> [no stdin reading supported for now]" % (program,)
        print >> sys.stderr, msg
        sys.exit(1)

    for filename in filenames:
        do_filename(filename)

    pass

# end
