#!/usr/bin/env python
# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
packageData_checker.py - script for checking and reporting on packageData.py

Note: some of this code might be moved into packageData
if all users of that data should use this code to canonicalize it
before making other use of it (eg for import graphing).

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

import sys
import os

LIST_UNCLASSIFIED_FILES = True


#bruce 080107 temporary debug prints to find out why SEMBot run of this seems to do nothing
# print >> sys.stderr, "packageData_checker.py debug: starting import"

from packageData import packageMapping, layer_aliases, topic_mapping
from packageData import packageMapping_for_files
from packageData import packageMapping_for_packages

from packageData import needs_renaming_for_clarity
from packageData import needs_refactoring # use this someday?
from packageData import listing_order # use this? (it's not yet well ordered as of 080104)
from packageData import subdir_notes


# utils for looking at output of AllPyFiles, not yet used within this file

def source_path_parts(path):
    p1 = path.split('/')
    assert p1[0] == '.'
    return p1[1:]

def topmodule(pathparts):
    if not len(pathparts) == 1:
        return None
    module = pathparts[0]
    assert module.endswith('.py')
    return module[:-3]

#e should add routine to look for toplevel files not present in packageMapping

# ==

# flags for packageClassification
LAYER_ONLY = 'LAYER_ONLY'
TOPIC_ONLY = 'TOPIC_ONLY'
LAYER_AND_TOPIC = 'LAYER_AND_TOPIC'

def packageClassification(value, flags):
    """
    @param value: a string value from the packageMapping global variable,
                  e.g. "ui/propmgr|commands/BuildSomething" or "widget" or ...
                  which has a layer and an optional |topic
                  both of which might be word or word/word etc
    """
    parts = value.split('|')
    assert len(parts) in (1,2)
    if len(parts) == 1:
        layer = parts[0]
        topic = None
    else:
        layer, topic = parts
    layer = canonicalize(layer, layer_aliases)
    if topic is None:
        topic = layer # or, "dflt_" + layer??
    topic = canonicalize(topic, topic_mapping)
    if flags == LAYER_ONLY:
        return layer
    elif flags == TOPIC_ONLY:
        return topic
    else:
        # LAYER_AND_TOPIC
        if layer == topic:
            return layer
        return layer + "|" + topic
    pass

def canonicalize(value, dict1):
    """
    Canonicalize value by repeatedly doing value = dict1[value],
    but if this enters a cycle, report error and return original value.
    """
    orig_value = value
    prior_values = [value]
    while dict1.has_key(value):
        value = dict1[value]
        if value in prior_values:
            print >> sys.stderr, "error: canonicalize loop: %r" % (prior_values + [value])
            return orig_value
        prior_values.append(value)
    return value

def check_basename(basename):
    """
    Return an improved basename; fix and report errors.
    """
    if ' ' in basename:
        print >> sys.stderr, "error: basename should not contain %r: %r" % (' ', basename,)
        assert 0 # can't handle this error
    for suffix in (".py", "/"):
        if basename.endswith( suffix):
            print >> sys.stderr, "error: basename should not end with %r: %r" % (suffix, basename,)
            basename = basename[:-len(suffix)]
            print >> sys.stderr, " (using %r instead)" % basename
    return basename

def summarize_packageMapping( flags):

    counts = {}

    for basename, value in packageMapping.items():
        basename = check_basename(basename)
        classification = packageClassification(value, flags)
        countnow = counts.setdefault(classification, 0)
        countnow += 1
        counts[classification] = countnow

    items = counts.items()
    items.sort() # by classification

    print
    print "classication: count (for %s)" % (flags,)
    print
    for classification, count in items:
        print "%s: %d" % (classification, count)
    return

def summarize_packageMapping_using_default_flags():
    ## summarize_packageMapping( LAYER_ONLY)
    summarize_packageMapping( TOPIC_ONLY)
    return

# ==

T_MODULE = "module"
T_PACKAGE = "package"
T_SUBDIR_NOTE = "subdir note"

# sortorder values
ORDER_ERROR = -2
ORDER_SUBDIR_NOTE = -1
ORDER_INLINE_NOTE = 0
ORDER_MODULE = 1
ORDER_NEW_SUBPACKAGE = 2

class _VirtualSubdir(type({})):

    def __init__(self, basename):
        self.__basename = basename
        super(_VirtualSubdir, self).__init__()

    def print_listing(self, indent = "", skip_toplevel_indent = False):
        if not skip_toplevel_indent:
            print indent + self.__basename + "/" + "   (%d)" % len(self)
            subindent = indent + "    "
        else:
            print indent + self.__basename + "/" + "   (%d)" % len(self) + " contains:"
            print
            subindent = indent
        items = [(sortorder, basename.lower(), basename, explan) for (basename, (sortorder, explan)) in self.items()]
        items.sort()
        last_sortorder = None
        for sortorder, basename_tolower, basename, explan in items:
            ## if last_sortorder is not None and ...
            if (sortorder != last_sortorder or sortorder == ORDER_NEW_SUBPACKAGE):
                print subindent # blank line before subdirs or between types of item
            last_sortorder = sortorder
            if type(explan) == type(""):
                print_with_word_wrapping(subindent, explan, 80)
            else:
                child = explan
                # assert isinstance(child, _VirtualSubdir)
                child.print_listing(subindent)
    pass

def print_with_word_wrapping(indent, line, limit):
    words = line.split()
    sofar = indent # print this, or more
    while words:
        nextword = words[0]
        words = words[1:]
        # construct trial line
        trial = sofar
        if trial != indent:
            trial += ' '
        trial += nextword
        if len(trial) > limit:
            # nextword won't fit, print prior line and use nextword to start next line
            print sofar
            sofar = indent + nextword
        else:
            sofar = trial
        continue
    if sofar != indent:
        print sofar
    return

_toplevel_virtual_subdir = _VirtualSubdir("cad/src")

def get_virtual_subdir(parts, assert_already_there = False): # should be a method in _toplevel_virtual_subdir
    """
    @param parts: list of 1 or more pathname components
    """
    if len(parts) > 1:
        parent = get_virtual_subdir(parts[:-1])
        basename = parts[-1]
    else:
        parent = _toplevel_virtual_subdir
        basename = parts[-1]
    if parent.has_key(basename):
        sortorder, child = parent[basename]
        assert sortorder == ORDER_NEW_SUBPACKAGE
        assert isinstance(child, _VirtualSubdir)
    else:
        assert not assert_already_there, "missing subdir: %r" % (parts,)
        child = _VirtualSubdir(basename)
        sortorder = ORDER_NEW_SUBPACKAGE
        explan = child ### an object; for other sortorders, a string
        parent[basename] = (sortorder, explan)
        assert parent.has_key(basename)
    return child

def collect_virtual_listing( packageDict, ftype ):
    """
    @param packageDict: packageMapping_for_files or packageMapping_for_packages
    @param ftype: T_MODULE or T_PACKAGE
    """
    for basename, value in packageDict.items():
        basename = check_basename(basename)
        subdirname = packageClassification(value, TOPIC_ONLY)
        parts = subdirname.split('/')
        dir1 = get_virtual_subdir(parts) # also adds items for subdir into its parent dirs
        if ftype == T_MODULE:
            explan = "%s.py" % basename
            if basename in needs_renaming_for_clarity:
                explan += " (rename to %s)" % needs_renaming_for_clarity[basename]
            sortorder = ORDER_MODULE
        elif ftype == T_PACKAGE: # preexisting package
            explan = " [ inlined contents of %s/ ]" % basename
            # someday: add number of files in there, or even list the first 5 files as children
            sortorder = ORDER_INLINE_NOTE
        else:
            explan = " [ error: unrecognized ftype %r, basename = %r]" % (ftype, basename)
            sortorder = ORDER_ERROR
            print >>sys.stderr, explan
        assert not dir1.has_key(basename), "duplicate basename: %r" % (basename,)
        dir1[basename] = (sortorder, explan)
    return

def print_listings():
    """
    """

    global packageMapping_for_files

    if LIST_UNCLASSIFIED_FILES: #bruce 080223; usage: pass cad/src/*.py == ../*.py as arguments
        packageMapping_for_files = dict(packageMapping_for_files)
        for pyfile in sys.argv[1:]:
            if pyfile.endswith('.py'):
                basename_ext = os.path.basename(pyfile)
                basename, ext = os.path.splitext(basename_ext)
                if not packageMapping_for_files.has_key(basename):
                    packageMapping_for_files[basename] = " NOT YET CLASSIFIED: "
                    # print "missing file:", basename
            else:
                print "unrecognized argument: %r" % (pyfile,)
            continue

    collect_virtual_listing( packageMapping_for_files, T_MODULE)
    collect_virtual_listing( packageMapping_for_packages, T_PACKAGE)

    for subdirname, note in subdir_notes.items():
        parts = subdirname.split('/')
        dir1 = get_virtual_subdir(parts, assert_already_there = True)
        FAKENAME_NOTE = " FAKENAME_NOTE " # not a valid basename, but a string (since .lower() gets called on it)
        sort_order = ORDER_SUBDIR_NOTE
        dir1[FAKENAME_NOTE] = (sort_order, note)

    _toplevel_virtual_subdir.print_listing(skip_toplevel_indent = True)
    return

# print >> sys.stderr, "packageData_checker.py debug: done with most of import"

if __name__ == '__main__':
    # print >> sys.stderr, "packageData_checker.py debug: starting __main__ section"
    ## summarize_packageMapping_using_default_flags()
    print_listings()
    print
    print "[end]"
    # print >> sys.stderr, "packageData_checker.py debug: ending __main__ section"

# print >> sys.stderr, "packageData_checker.py debug: done with all of import"

# end
