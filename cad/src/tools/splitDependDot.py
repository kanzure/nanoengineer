#!/usr/bin/env python
# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note: this produces several disconnected graphs in GraphViz
format. I don't know if the entire output
(when it contains more than one graph) is legal GraphViz input.
"""

_DEBUG = False

import sys
import os

def transclose( toscan, collector):
    """
    This is a copy of def transclose from cad/src/state_utils.py as of 071028,
    with unused options removed. See that version for documentation.
    It's copied here so this script is self-contained and doesn't need to
    fiddle with sys.path to run.
    """
    seen = dict(toscan)
    while toscan:
        found = {}
        len1 = len(toscan)
        for obj in toscan.itervalues():
            collector(obj, found)
        len2 = len(toscan)
        if len1 != len2:
            print >> sys.stderr, \
                  "bug: transclose's collector %r modified dict toscan (id %#x, length %d -> %d)" % \
                  (collector, id(toscan), len1, len2)
        # now "subtract seen from found"
        new = {}
        for key, obj in found.iteritems():
            if not seen.has_key(key):
                new[key] = obj
        seen.update(new)
        toscan = new
        continue
    return seen

def readDependDot_as_pairs(filename):
    """
    Return a list of pairs (module1, module2)
    for the dependency lines in the format "   module1 -> module2;"
    in the named file.
    (Note: this is the format output by PackageDependency.py
     into a file often called "depend.dot".)
    """
    file = open(filename, "rU")
    lines = file.readlines()
    file.close()
    res = []
    for line in lines:
        if '->' in line:
            # assume line looks like "   module1 -> module2;" plus optional whitespace
            line = line.strip()
            words = line.split()
            module1 = words[0]
            assert words[1] == '->'
            assert words[2].endswith(';')
            module2 = words[2][:-1]
            if _DEBUG:
                print "got %r -> %r" % (module1, module2)
            res.append((module1,module2))
    return res

def import_pairs_to_imports_dict(import_pairs):
    imports_dict = {}
    for (module1, module2) in import_pairs:
        module2list = imports_dict.setdefault(module1, [])
        module2list.append(module2)
    return imports_dict

def extract_connected_set(dict1, module1):
    """
    Assume dict1 maps modules to lists of modules they import,
    and module1 is a key in dict1.
    Find all modules reachable from module1 in dict1
    and remove them from dict1
    and return them in a list.
    """
    def collector( module_x, dict_to_store_into):
        module2list = dict1.pop(module_x)
        for m2 in module2list:
            dict_to_store_into[m2] = m2
        return
    seen = transclose(  {module1: module1}, collector )
    return seen.keys()

def sorted(list1):
    copy = list(list1)
    copy.sort()
    return copy

def doit(filename):
    import_pairs = readDependDot_as_pairs(filename)
    imports_dict = import_pairs_to_imports_dict(import_pairs)
    imports_dict_orig = dict(imports_dict)
    # we now destructively extract maximal connected subsets from imports_dict
    # (assuming it only contains cycles, so it's enough to follow imports
    #  in only one direction) and print them, until none are left
    while imports_dict:
        first_key = sorted(imports_dict.keys())[0]
        cyclic_set = extract_connected_set( imports_dict, first_key) # a list
        modules = sorted(cyclic_set)
        # print this cyclic set
        # I don't know if '#' starts a comment line in GraphViz input...
        # and these lines are not that useful, so don't bother:
        ## print "# " + " ".join(modules)
        print "digraph G_%s {" % first_key
        for module1 in modules:
            for module2 in sorted(imports_dict_orig[module1]):
                print "    %s -> %s;" % (module1, module2)
            if module1 != modules[-1]:
                print
        print "}\n"
    return

def print_usage():
    program = sys.argv[0]
    print >>sys.stderr, "Usage: %s [depend.dot-filename]  ==> prints cyclic sets as separate digraphs"
    return

def main(argv):
    argc = len(argv)
    if argc == 2:
        filename = argv[1]
    elif argc == 1:
        filename = "depend.dot"
    else:
        print_usage()
        sys.exit(1)
    if not os.path.isfile(filename):
        print_usage()
        sys.exit(1)
    doit(filename)
    return

if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)

# end

        
