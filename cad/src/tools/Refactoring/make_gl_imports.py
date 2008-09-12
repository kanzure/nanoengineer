#!/usr/bin/env python
# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
make_gl_imports.py - make import statements for OpenGL identifiers,
which look like:

  from OpenGL.GL import GL_MODELVIEW_MATRIX
  from OpenGL.GLU import gluUnProject

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

Algorithm:

tokenize the input, and for each unique identifier
matching gl* or GL*, make an import statement based on its initial
characters, handling gl vs glu appropriately.

BUGS:

It thinks identifiers in import statements are in code,
so it will never remove imports when run on an entire file,
and it can get confused and suggest unnecessary ones
such as "from OpenGL.GL import GL" (from seeing the "GL"
in "OpenGL.GL" in an existing import statement).

It doesn't verify the symbol is available in the module
it proposes to import, so it will get confused by local
variables that start with 'gl' or classnames that
start with 'GL' (e.g. "GLPane"), for example.

TODO:

generalize to a tool which fixes up all toplevel imports
after you move some code around among several files,
by copying or moving imports to new files as needed,
and removing old ones, and warning if anything suspicious
might need manual checking (like a runtime import).

History:

bruce 080912 made this from tools/Refactoring/tokenize-python.py.
"""
import sys

from os.path import basename
from getopt import getopt, GetoptError
from tokenize import generate_tokens, tok_name
from pprint import pprint

_found = None

_PREFIX_FOR_KIND = {
    'glu':  'from OpenGL.GLU import',
    'gl':   'from OpenGL.GL import',
}

def process_token(tup5):
    typ, text, s, t, line = tup5
    tokname = tok_name[typ]
    if tokname == 'NAME':
        # keyword or identifier
        if text[:2] in ('gl', 'GL'):
            if text == 'global':
                return
            kind = 'gl' # might be modified
            if text[:3] in ('glu', 'GLU'):
                kind = 'glu'
            _found[text] = kind
    return

def process_found(found):
    """
    @type found: dict mapping identifier names to their kind
    """
    items = found.items()
    items.sort()
    for name, kind in items:
        print _PREFIX_FOR_KIND[kind], name
    return

def py_tokenize(filename_in):
    if filename_in is None:
        file_in = sys.stdin
    else:
        file_in = open(filename_in, 'rU')
    g = generate_tokens(file_in.readline)
    li = list(g)
    file_in.close()
    li2 = map(process_token, li)
    del li2
    return

def dofiles(filenames):
    for filename in filenames:
        py_tokenize(filename)
    return

def run():
    global _found
    _found = {}
    filenames = sys.argv[1:]
    if filenames:
        dofiles(filenames)
    else:
        dofiles([None]) # None means use stdin
    print
    process_found(_found)
    _found = None
    return

if __name__ == '__main__':
    run()

# end
