#!/usr/bin/env python
"""
tokenize-python.py -- print tokenization of one or more input .py files

$Id$

History:

bruce 080616 drafted this from an old script I had at home, py-tokenize.py

TODO:

add options to remove certain kinds of output,
to make it more useful for comparing source files for important changes
while ignoring some kinds of changes.
"""
import sys

from tokenize import generate_tokens, tok_name
from pprint import pprint

def improve(tup5):
    typ, text, s, t, line = tup5
    tokname = tok_name[typ]
    if tokname == 'INDENT':
        text = ''
    return (tokname, text)

def py_tokenize(filename_in, file_out):
    ## file_out = open(filename_out, "w")
    file_in = open(filename_in, 'rU')
    g = generate_tokens(file_in.readline)
    li = list(g)
    file_in.close()
    li2 = map(improve, li)
    pprint(li2, file_out)

def dofiles(filenames):
    for filename in filenames:
        if len(filenames) > 1:
            print "\n======= [%s]\n" % (filename,)
        py_tokenize(filename, sys.stdout)
    return

def run():
    filenames = sys.argv[1:]
    if filenames:
        dofiles(filenames)
    else:
        print >> sys.stderr, "usage: ..."
    return

if __name__ == '__main__':
    run()

# end
