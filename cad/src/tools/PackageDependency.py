#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
   PackageDependency.py

   Takes a list of python files as arguments, writes a list of
   packages that each imports on stdout.  This information is in a
   format suitable for use with the GraphViz package.

   To use, run this on a list of all python files you're interested
   in, redirecting stdout to a file like depend.dot.  Stderr will
   recieve a list of modules with in and out arc counts for that node
   in the final graph.

   The program first reduces the tree to the graph of cycles.  It does
   this by removing nodes with either no incoming arcs, or no outgoing
   arcs, or those which only reference modules not in the argument
   list.  It performs this pruning repeatedly until no new exclusions
   are produced by an iteration.

   At that point, the output consists of only the cycles in the
   dependency graph.  This can be plotted with the dot program from
   the GraphViz package.

   To see the entire graph, comment out the pruneTree() loop.
"""

import sys
import re

fromImportLineRegex = re.compile(r'^\s*from\s+(\S+)\s+import\s')
importLineRegex = re.compile(r'^\s*import\s+([^#]+)')
asRegex = re.compile(r'^(\S+)\s+as\s+')

pruneModules = []
"""
   The pruneModules list are those modules which didn't import any
   modules excluded in any of the module lists.  These are
   the leaves of the dependency tree.  At each stage, you prune off
   the leaves and expose a new layer of modules which no longer import
   any non-excluded modules.
"""

unreferencedModules = []
"""
   The unreferencedModules list are those which none of the
   non-excluded modules import.  These are roots of the dependency
   tree.
"""

externalModules = []
"""
   The externalModules list are those which are referenced, but are
   not in the set of arguments.
"""

# these four are set in initializeGlobals()
allProcessedModules = None
referencedModules = None
fromModuleCount = None
toModuleCount = None

def fileNameToModuleName(fileName):
    if (fileName.startswith("./")):
        fileName = fileName[2:]
    if (fileName.startswith("src/")):
        fileName = fileName[4:]
    if (fileName.endswith(".py")):
        fileName = fileName[:-3]
    fileName = fileName.replace("/", ".")
    return fileName

def moduleToDotNode(moduleName):
    ret = moduleName.replace(".", "_")
    ret = ret.replace("-", "_")
    return ret

def dependenciesInFile(fileName, printing):
    importSet = set([])
    fromModuleName = moduleToDotNode(fileNameToModuleName(fileName))
    if (fromModuleName in pruneModules or fromModuleName in unreferencedModules):
        return None
    allProcessedModules.add(fromModuleName)
    f = open(fileName)
    for line in f:
        m = fromImportLineRegex.match(line)
        if (m):
            toModuleName = moduleToDotNode(m.group(1))
            if (toModuleName != fromModuleName):
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
                toModuleName = moduleToDotNode(toModuleName)
                if (toModuleName != fromModuleName):
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

        if (printing):
            print "    %s -> %s;" % (fromModuleName, toModuleName)

        if (fromModuleCount.has_key(fromModuleName)):
            fromModuleCount[fromModuleName] += 1
        else:
            fromModuleCount[fromModuleName] = 1
        if (toModuleCount.has_key(toModuleName)):
            toModuleCount[toModuleName] += 1
        else:
            toModuleCount[toModuleName] = 1
        outCount = outCount + 1
    if (outCount < 2):
        return fromModuleName
    return None

def initializeGlobals():
    global allProcessedModules
    global referencedModules
    global fromModuleCount
    global toModuleCount
    
    allProcessedModules = set([])
    referencedModules = set([])

    fromModuleCount = {}
    toModuleCount = {}
    

def pruneTree():
    global pruneModules
    global unreferencedModules
    global externalModules

    initializeGlobals()
    pruneCount = 0
    pruneModulesLen = 0
    prunedModuleList = []

    for sourceFile in sys.argv[1:]:
        prunedModule = dependenciesInFile(sourceFile, False)
        if (prunedModule):
            prunedModuleList += [prunedModule]
    pruneModules += prunedModuleList
    pruneCount += len(prunedModuleList)
    
    unreferencedModulesList = allProcessedModules.difference(referencedModules)
    unreferencedModules += unreferencedModulesList
    pruneCount += len(unreferencedModulesList)

    externalModulesList = referencedModules.difference(allProcessedModules)
    externalModulesList = externalModulesList.difference(externalModules)
    externalModulesList = externalModulesList.difference(pruneModules)
    externalModules += externalModulesList
    pruneCount += len(externalModulesList)

    return pruneCount

def printTree():
    initializeGlobals()
    print "digraph G {"
    for sourceFile in sys.argv[1:]:
        dependenciesInFile(sourceFile, True)
    print "}"
    for key in fromModuleCount.keys():
        print >>sys.stderr, "%06d %06d %s" % (toModuleCount[key], fromModuleCount[key], key)

if (__name__ == '__main__'):
    while (pruneTree()):
        pass
    printTree()
