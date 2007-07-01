#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
   PackageDependency.py

   Takes a list of python files as arguments, writes a list of
   packages that each imports on stdout.  This information is in a
   format suitable for use with the GraphViz package.

   To use, start by removing all of the module names in pruneModules,
   unreferencedModules, and externalModules.  Run this on a list of
   all python files you're interested in, redirecting stdout to a file
   like depend.dot.

   It will spit out three lists on stderr:

   The pruneModules list are those modules which didn't import any
   modules excluded in any of the module lists.  Add these lines to
   the pruneModules set before running the program again.  These are
   the leaves of the dependency tree.  At each stage, you prune off
   the leaves and expose a new layer of modules which no longer import
   any non-excluded modules.

   The unreferencedModules list are those which none of the
   non-excluded modules import.  These are roots of the dependency
   tree.  Add these lines to the unreferencedModules set and run again
   until there are no new exclusions from a run.

   The externalModules list are those which are referenced, but are
   not in the set of arguments.  Add these to the externalModules set
   like the above exclusions.

   When no new exclusions are produced by a run, the output consists
   of only the cycles in the dependency graph.  This can be plotted
   with the dot program from the GraphViz package.
"""

import sys
import re

fromImportLineRegex = re.compile(r'^\s*from\s+(\S+)\s+import\s')
importLineRegex = re.compile(r'^\s*import\s+([^#]+)')
asRegex = re.compile(r'^(\S+)\s+as\s+')

pruneModules = set([
    ])

unreferencedModules = set([
    ])

externalModules = set([
    ])

allProcessedModules = set([])
referencedModules = set([])

def fileNameToModuleName(fileName):
    if (fileName.startswith("./")):
        fileName = fileName[2:]
    if (fileName.startswith("src/")):
        fileName = fileName[4:]
    if (fileName.endswith(".py")):
        fileName = fileName[:-3]
    fileName = fileName.replace("/", ".")
    return fileName

def dependenciesInFile(fileName):
    importSet = set([])
    fromModuleName = fileNameToModuleName(fileName)
    fromModuleName = fromModuleName.replace("-", "_")
    if (fromModuleName in pruneModules or fromModuleName in unreferencedModules):
        return
    allProcessedModules.add(fromModuleName)
    f = open(fileName)
    for line in f:
        m = fromImportLineRegex.match(line)
        if (m):
            toModuleName = m.group(1)
            importSet.add(toModuleName)
            continue
        m = importLineRegex.match(line)
        if (m):
            toModuleList = m.group(1).strip().split(',')
            for toModuleName in toModuleList:
                toModuleName = toModuleName.strip()
                m = asRegex.match(toModuleName)
                if (m):
                    toModuleName = m.group(1)
                importSet.add(toModuleName)
    f.close()
    referencedModules.update(importSet)
    importList = list(importSet)
    importList.sort()
    outCount = 0
    for toModuleName in importList:
        if (toModuleName in externalModules or toModuleName in pruneModules or toModuleName in unreferencedModules):
            continue
        toModuleName = toModuleName.replace(".", "_")
        toModuleName = toModuleName.replace("-", "_")
        print "    %s -> %s;" % (fromModuleName, toModuleName)
        outCount = outCount + 1
    if (outCount < 2):
        print >>sys.stderr, '    "%s",' % fromModuleName

if (__name__ == '__main__'):
    print "digraph G {"
    print >>sys.stderr, "pruneModules:"
    for sourceFile in sys.argv[1:]:
        dependenciesInFile(sourceFile)
    print "}"
    unreferencedModulesList = allProcessedModules.difference(referencedModules)
    unrefList = list(unreferencedModulesList)
    unrefList.sort()
    print >>sys.stderr, "unreferencedModules:"
    for pkg in unrefList:
        print >>sys.stderr, '    "%s",' % pkg

    externalModulesList = referencedModules.difference(allProcessedModules)
    externalModulesList = externalModulesList.difference(externalModules)
    externalModulesList = externalModulesList.difference(pruneModules)
    extList = list(externalModulesList)
    extList.sort()
    print >>sys.stderr, "externalModules:"
    for pkg in extList:
        print >>sys.stderr, '    "%s",' % pkg
