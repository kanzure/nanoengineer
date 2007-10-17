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
from exprs import b, c as q, d # with a comment
"""

import sys
import re
import os.path

fromImportLineRegex = re.compile(r'^\s*from\s+(\S+)\s+import\s+([^#]*)')
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

rootsToKeep = set([
    "_import_roots",
    ])

filesToProcess = []
optionPrintUnreferenced = False
optionPrintTables = False
optionJustCycles = False
optionDontPrune = False

moduleNameToImportList = {}

# these four are set in initializeGlobals()
allProcessedModules = None
referencedModules = None
fromModuleCount = None
toModuleCount = None

def isPackage(moduleName):
    possiblePackageName = moduleName.replace(".", "/")
    if (os.path.isdir(possiblePackageName)):
        return True
    return False

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

def importsInFile(fileName):
    importSet = set([])
    fromModuleName = moduleToDotNode(fileNameToModuleName(fileName))
    f = open(fileName)
    for line in f:
        m = fromImportLineRegex.match(line)
        if (m):
            if (isPackage(m.group(1))):
                packageName = m.group(1)
                moduleImportList = m.group(2).strip().split(',')
                for toModuleName in moduleImportList:
                    toModuleName = toModuleName.strip()
                    m = asRegex.match(toModuleName)
                    if (m):
                        toModuleName = m.group(1)
                    toModuleName = moduleToDotNode(packageName + "." + toModuleName)
                    if (toModuleName != fromModuleName):
                        importSet.add(toModuleName)
            else:
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
    importList = list(importSet)
    importList.sort()
    moduleNameToImportList[fromModuleName] = importList

def dependenciesInFile(fileName, printing):
    fromModuleName = moduleToDotNode(fileNameToModuleName(fileName))
    if (fromModuleName in pruneModules or fromModuleName in unreferencedModules):
        return None
    allProcessedModules.add(fromModuleName)
    importList = moduleNameToImportList[fromModuleName]
    referencedModules.update(importList)
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
    if (outCount < 1):
        return fromModuleName
    return None

def scanForImports():
    for sourceFile in filesToProcess:
        importsInFile(sourceFile)

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

    for sourceFile in filesToProcess:
        prunedModule = dependenciesInFile(sourceFile, False)
        if (prunedModule):
            prunedModuleList += [prunedModule]
    pruneModules += prunedModuleList
    pruneCount += len(prunedModuleList)
    
    unreferencedModulesList = allProcessedModules.difference(referencedModules)
    if (optionPrintUnreferenced):
        unreferencedModulesList = unreferencedModulesList.difference(rootsToKeep)
    unreferencedModules += unreferencedModulesList
    pruneCount += len(unreferencedModulesList)

    externalModulesList = referencedModules.difference(allProcessedModules)
    externalModulesList = externalModulesList.difference(externalModules)
    externalModulesList = externalModulesList.difference(pruneModules)
    externalModules += externalModulesList
    pruneCount += len(externalModulesList)

    return pruneCount

inThisCycle = set([])
inAnyCycle = set([])
visited = {}

def isInCycle(moduleName, cycleRoot):
    global visited

    if (moduleName == cycleRoot):
        return True
    if (visited.has_key(moduleName)):
        return visited[moduleName]
    if (moduleName in pruneModules or moduleName in unreferencedModules or moduleName in externalModules):
        return False
    importList = moduleNameToImportList[moduleName]
    visited[moduleName] = False
    for toModuleName in importList:
        if (isInCycle(toModuleName, cycleRoot)):
            visited[moduleName] = True
            return True
    return False

def scanForCycles(cycleRoot):
    global visited

    if (moduleName in pruneModules or moduleName in unreferencedModules or moduleName in externalModules):
        return
    visited = {}
    removeArcs = []
    importList = moduleNameToImportList[cycleRoot]
    for toModuleName in importList:
        if (isInCycle(toModuleName, cycleRoot)):
            pass
        else:
            removeArcs += [toModuleName]
    for toModuleName in removeArcs:
        importList.remove(toModuleName)
    moduleNameToImportList[moduleName] = importList
    return

def printTree():
    initializeGlobals()
    print "digraph G {"
    for sourceFile in filesToProcess:
        dependenciesInFile(sourceFile, True)
    print "}"
    for key in fromModuleCount.keys():
        if (not toModuleCount.has_key(key)):
            toModuleCount[key] = 0
        print >>sys.stderr, "%06d %06d %s" % (toModuleCount[key], fromModuleCount[key], key)

if (__name__ == '__main__'):
    for opt in sys.argv[1:]:
        if (opt == "--noPrune"):
            optionDontPrune = True
        elif (opt == "--printUnreferenced"):
            optionPrintUnreferenced = True
        elif (opt == "--printTables"):
            optionPrintTables = True
        elif (opt == "--justCycles"):
            optionJustCycles = True
        else:
            filesToProcess += [opt]
    scanForImports()
    if (not optionDontPrune):
        while (pruneTree()):
            pass
    if (optionPrintUnreferenced):
        unreferencedModules.sort()
        for module in unreferencedModules:
            if (not module.endswith("__init__")):
                print module
    elif (optionPrintTables):
        print "\n   Prune\n"
        pruneModules.sort()
        for module in pruneModules:
            print module
        print "\n   Unreferenced\n"
        unreferencedModules.sort()
        for module in unreferencedModules:
            print module
        print "\n   External\n"
        externalModules.sort()
        for module in externalModules:
            print module
    else:
        if (optionJustCycles):
            for sourceFile in filesToProcess:
                moduleName = moduleToDotNode(fileNameToModuleName(sourceFile))
                scanForCycles(moduleName)
            while (pruneTree()):
                pass
        printTree()
