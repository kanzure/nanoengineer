#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

# First argument is file containing output of FindPythonGlobals.py
#
# If second argument is --duplicates, prints a list of duplicate
# globals definitions found in the above file.
#
# If second argument is --check-import, takes a list of from...import
# statements and verifies that they are importing symbols from the
# locations they are actually defined at.
#
# Otherwise, reads the output of pychecker from stdin and prints a set
# of import statements which will resolve the globals it complains
# about.

import sys
import re

pycheckerNoGlobalRegex = re.compile(r'No global \((.*)\) found')
importLineRegex = re.compile(r'^([^:]+):\s*from\s+(\S+)\s+import\s+([^#]+)')

filesToIgnore = [
    "./src/testdraw.py",
    "./plugins/DNA/bdna-bases/prepare.py",
    "./plugins/DNA/zdna-bases/prepare.py",
    ]

symbolsToIgnore = [
    "retranslateUi",
    "setupUi",
    "do_what_MainWindowUI_should_do",
    ]

def readGlobalsFile(filename, changeToPackageFormat):
    file = open(filename)
    ret = {}
    for line in file:
        line = line.strip()
        (globalSymbol, definitionFile) = line.split(": ", 1)
        if (definitionFile.startswith("./src/experimental")):
            continue
        if (definitionFile.startswith("./tests")):
            continue
        if (definitionFile in filesToIgnore):
            continue
        if (ret.has_key(globalSymbol)):
            fileSet = ret[globalSymbol]
        else:
            fileSet = set([])
            ret[globalSymbol] = fileSet
        if (changeToPackageFormat):
            if (definitionFile.startswith("./")):
                definitionFile = definitionFile[2:]
            if (definitionFile.startswith("src/")):
                definitionFile = definitionFile[4:]
            if (definitionFile.startswith("plugins/")):
                definitionFile = definitionFile[8:]
            if (definitionFile.endswith(".py")):
                definitionFile = definitionFile[:-3]
            definitionFile = definitionFile.replace("/", ".")
        fileSet.add(definitionFile)
    return ret

def printDuplicateGlobals(globalsDict):
    keys = globalsDict.keys()
    keys.sort()
    for key in keys:
        if (key.startswith("_")):
            continue
        if (key in symbolsToIgnore):
            continue
        fileSet = globalsDict[key]
        if (len(fileSet) > 1):
            fileList = list(fileSet)
            fileList.sort()
            print "\n%s\n" % key
            for filename in fileList:
                print "  %s \\" % filename

def toModule(filename):
    if (filename.startswith("./src/")):
        filename = filename[6:]
    if (filename.startswith("./")):
        filename = filename[2:]
    if (filename.endswith(".py")):
        filename = filename[:-3]
    filename = filename.replace("/", ".")
    return filename

def resolveSymbol(sym):
    if (globalsDict.has_key(sym)):
        fileSet = globalsDict[sym]
        fileList = list(fileSet)
        if (len(fileList) > 1):
            print "ambiguous definitions of symbol %s:" % sym
            fileList.sort()
            for filename in fileList:
                print "  " + filename
        else:
            print "from %s import %s" % (toModule(fileList[0]), sym)
    else:
        print "import " + sym

def findPycheckerGlobals():
    for line in sys.stdin:
        m = pycheckerNoGlobalRegex.search(line)
        if (m):
            symbol = m.group(1)
            resolveSymbol(symbol)

_s_symbolToModule = {}
_s_ignoreModuleSet = set([
    "atombase",
    "sim",
    "qt_debug_hacks",
    "MMKit",
    "testmode",
    "bearing_data",
    "samevals",
    "exprs",
    "TreeView",
    ])

def checkOneImport(fileName, moduleName, symbolName, globalsDict):
    if (symbolName == '*'):
        print "import * in " + fileName
        return
    if (symbolName == '\\'):
        print "import \\ in " + fileName
        return
    if (_s_symbolToModule.has_key(symbolName)):
        previousModule = _s_symbolToModule[symbolName]
        if (previousModule != moduleName):
            if ((previousModule == "math" and moduleName == "Numeric") or
                (previousModule == "Numeric" and moduleName == "math")):
                pass
            else:
                print "%s importing %s from %s, elsewhere imported from %s" % (fileName, symbolName, moduleName, previousModule)
    if (moduleName in _s_ignoreModuleSet):
        return
    _s_symbolToModule[symbolName] = moduleName
    if (globalsDict.has_key(symbolName)):
        moduleSet = globalsDict[symbolName]
        if (not moduleName in moduleSet):
            print "%s importing %s from %s, not defined there" % (fileName, symbolName, moduleName)
        if (len(moduleSet) > 1):
            if (len(moduleSet) == 2 and "math" in moduleSet and "Numeric" in moduleSet):
                return
            print "%s importing %s from %s, is available from:" % (fileName, symbolName, moduleName)
            for mod in moduleSet:
                print "    " + mod
    else:
        print "can't check up on file %s symbol %s module %s" % (fileName, symbolName, moduleName)

def checkImportStatements(globalsDict):
    """
    grep '^[[:space:]]*from.*import' *.py | tools/ResolveGlobals.py ../allglobalsymbols --check-import
    """
    for line in sys.stdin:
        m = importLineRegex.match(line)
        if (m):
            fileName = m.group(1)
            moduleName = m.group(2)
            symbolList = m.group(3).strip().split(',')
            for symbolName in symbolList:
                symbolName = symbolName.strip()
                checkOneImport(fileName, moduleName, symbolName, globalsDict)

if (__name__ == '__main__'):
    globalsFilename = sys.argv[1]
    printDuplicates = False
    checkImports = False
    if (len(sys.argv) > 2 and sys.argv[2] == '--duplicates'):
        printDuplicates = True
    elif (len(sys.argv) > 2 and sys.argv[2] == '--check-import'):
        checkImports = True
    globalsDict = readGlobalsFile(globalsFilename, checkImports)
    if (printDuplicates):
        printDuplicateGlobals(globalsDict)
    elif (checkImports):
        checkImportStatements(globalsDict)
    else:
        findPycheckerGlobals()
