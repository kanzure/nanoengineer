#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
   FindExternalImports.py

   Takes a list of python files as arguments, writes a list of
   packages that any of them import outside of the input list.

   Suitable for feeding to SymbolsInPackage.py to create an expanded
   global symbol list for use by ResolveGlobals.py.
"""

import sys
import re

fromImportLineRegex = re.compile(r'^\s*from\s+(\S+)\s+import\s')
importLineRegex = re.compile(r'^\s*import\s+([^#]+)')
asRegex = re.compile(r'^(\S+)\s+as\s+')

allProcessedModules = set([])
importedModules = set([])

def fileNameToModuleName(fileName):
    if (fileName.startswith("./")):
        fileName = fileName[2:]
    if (fileName.startswith("src/")):
        fileName = fileName[4:]
    if (fileName.endswith(".py")):
        fileName = fileName[:-3]
    fileName = fileName.replace("/", ".")
    return fileName

def collectImportedModules(fileName):
    importSet = set([])
    fromModuleName = fileNameToModuleName(fileName)
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
    importedModules.update(importSet)

if (__name__ == '__main__'):
    for sourceFile in sys.argv[1:]:
        collectImportedModules(sourceFile)
    externalImports = importedModules.difference(allProcessedModules)
    importList = list(externalImports)
    importList.sort()
    for moduleName in importList:
        print moduleName
