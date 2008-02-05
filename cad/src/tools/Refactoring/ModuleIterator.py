#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
Iterate over all modules in source tree.

Useful as a framework for any portions of a refactoring which need to
be executed for every module.  The iterator created by
ModuleIterator() produces (fileName, moduleName) pairs for each python
source file in or below the current working directory.  Tools using
this should generally run in cad/src.

Typical usage::

  for (fileName, moduleName) in ModuleIterator():
      code for each module...

The fileNames produced look like "./directory/Module.py", with a
corresponding moduleName of "directory.Module".

@author: Eric Messick
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$
"""

import os

_dirsToExclude = set([
    "experimental",
    "outtakes",
    "scratch",
    ])
"""
Directory names which will be excluded from the search.  These are
simple directory names, not full path names.  Any directory with any
of these names will not be descended into during the iteration.
"""

class ModuleIterator(object):
    """
    Scan the current directory and its subdirectories for python
    source files.  The list of files is frozen in place when the
    object is created.  Multiple iteration runs can be started from
    this same object, and will cover the same set of files, even if
    files are added or removed between runs.

    Typical usage::

      for (fileName, moduleName) in ModuleIterator():
          code for each module...
    """
    def __init__(self, doExclude=False):
        self._fileList = []
        for (dirpath, dirnames, filenames) in os.walk("."):
            i = len(dirnames)
            while (i>0):
                i = i - 1
                if (dirnames[i].startswith(".") or
                    (doExclude and dirnames[i] in _dirsToExclude)):
                    del dirnames[i]
            for s in filenames:
                if (s.lower().endswith(".py")):
                    path = dirpath + os.sep + s
                    self._fileList = self._fileList + [path]
        self._fileList.sort()

    def __iter__(self):
        return _Iterator(self._fileList)

class _Iterator(object):
    def __init__(self, initialList):
        self._remaining = initialList

    def next(self):
        if (len(self._remaining) > 0):
            path = self._remaining[0]
            self._remaining = self._remaining[1:]
            mod = path
            if (mod.startswith("." + os.sep)):
                mod = mod[2:]
            if (mod.lower().endswith(".py")):
                mod = mod[:-3]
            mod = mod.replace(os.sep, ".")
            return (path, mod)
        raise StopIteration

if (__name__ == '__main__'):
    for (fileName, moduleName) in ModuleIterator():
        print "file: %s, module: %s" % (fileName, moduleName)
