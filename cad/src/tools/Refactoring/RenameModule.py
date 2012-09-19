#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
Update imports to reflect the renaming of a module.

Usage::

  tools/Refactoring/RenameModule.py [options] old/path.py new/pathname.py

  or

  tools/Refactoring/RenameModule.py old/path.py new/

Finds all instances where a module is imported and changes them to
reference the module at it's new location.  The caller needs to
arrange for the module to be found at the new location, and for any
edits to the module itself.

The --dry-run option reports warnings, but does not change any files.

The --ignore-bare-module option disables substitution of oldModule
where it is not preceded by oldPackage.  This option has no effect if
oldPackage is empty.

Warnings are in a format that can be processed by M-x compile in
emacs.

The following remappings are done::

# import oldname                     --> import newdir.newname as oldname
# import olddir.oldname as othername --> import newdir.newname as othername
# from olddir.oldname import symbol  --> from newdir.newname import symbol
# from olddir import oldname         --> from newdir import newname as oldname
# from olddir.oldname import symbol as othername
#                            --> from newdir.newname import symbol as othername
# from olddir import oldname as othername
#                            --> from newdir import newname as othername

Where either 'olddir.' or 'newdir.' appear (note the dots), either may
be empty.  In the some cases, an empty newdir would remove the entire
from clause.

Note that python considers::

# import a.b as c.d

to be a syntax error, so::

# import olddir.oldname  --> import newdir.newname

with all occurrences of olddir.oldname in the program text being
changed to newdir.newname.  This is a specific enough change to be
unlikely to introduce errors, while simply changing oldname to newname
everywhere could change some unrelated variables.

Where an 'import as' remains after this refactoring, a further
refactoring should be done to remove the 'as' clause.

Steps for moving a module:

1) make the new location, if necessary:

$ svn mkdir newpackage

2) update the imports:

$ tools/Refactoring/RenameModule.py path.py newpackage

3) actually move the module:

$ svn mv path.py newpackage/path.py
$ rm path.pyc

4) check to see that everything works.

@author: Eric Messick
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$
"""

import sys
import os
import os.path
import re

from ModuleIterator import ModuleIterator

importStatementRegex = re.compile(r'^(\s*)(from\s+(\S+)\s+)?import\s')
importClauseRegex = re.compile(r'\s*([\w_.]+)(\s+as\s+([\w_.]+))?')

SubstituteBareModule = True

def pathToModule(path):
    """
    Convert a string representing a file path name into a module path.
    Removes a trailing .py, and changes os.sep into dot.
    """
    mod = path
    if (mod.startswith("." + os.sep)):
        mod = mod[2:]
    if (mod.lower().endswith(".py")):
        mod = mod[:-3]
    mod = mod.replace(os.sep, ".")
    return mod

def moduleToPath(mod):
    """
    Convert a string representing a module path into a file path name.
    Used to check for directories, so doesn't add .py to the end, just
    replaces dot with os.sep.
    """
    path = mod
    path = path.replace(".", os.sep)
    return path

def separatePath(whole):
    """
    Converts a whole module path name into it's package and module
    components, returning them as a tuple.
    """
    index = whole.rfind(".")
    if (index < 0):
        package = ""
        module = whole
    else:
        if (index < 1):
            package = ""
        else:
            package = whole[:index]
        module = whole[index+1:]
    return (package, module)

class _OutputStream(object):
    """
    Accumulates the text of a file being processed.  Lines that are to
    be passed through unchanged are written via writeLine().  Import
    statements, which may or may not end up changing are collected in
    pieces.

    The collected contents are stored in a string, and the whole file
    is rewritten only if it different from the original file.
    """
    def __init__(self, fileName):
        self._fileName = fileName
        self._fileChanged = False
        self._contents = ""
        self._lineNumber = 1

    def error(self, message):
        """
        Identifies the file and line number where the message occurred.
        """
        print "%s:%d: %s" % (self._fileName, self._lineNumber, message)

    def fileChanged(self):
        """
        Sets the file modification flag, so it will be written on close.
        """
        self._fileChanged = True

    def _write(self, line):
        self._contents = self._contents + line
        self._lineNumber += 1

    def writeLine(self, line):
        """
        Output one line of text without any modifications.
        """
        self._write(line)

    def startImportLine(self, prefixFromImport, prefixOriginalFromImport):
        """
        Start collecting data for an import statement.  Arguments
        consist of all characters though the first whitespace
        character after the word import.  First argument is the
        modified from clause, second is the original from clause.
        Both are needed in case the line must be split into two
        because some of the import clauses need to be changed, while
        others do not.
        """
        self._newLineOne = prefixFromImport
        self._newLineTwo = prefixOriginalFromImport
        self._changedOne = False
        self._changedTwo = False
        self._commaOne = ""
        self._commaTwo = ""
        self._bothSame = (prefixFromImport == prefixOriginalFromImport)

    def collectImportClause(self, moduleName, asModuleName = "",
                            originalFrom = False, isEdit = True):
        """
        Handle one import clause.  Set originalFrom if this clause
        should be associated with the original from clause.  Clear
        isEdit if this clause by itself would not result in any change
        to the file.
        """
        if (asModuleName != "" and moduleName != asModuleName):
            clause = moduleName + " as " + asModuleName
        else:
            clause = moduleName

        if (self._bothSame):
            originalFrom = False
        if (originalFrom):
            self._newLineTwo += self._commaTwo + clause
            if (isEdit):
                self._changedTwo = True
            self._commaTwo = ", "
        else:
            self._newLineOne += self._commaOne + clause
            if (isEdit):
                self._changedOne = True
            self._commaOne = ", "

    def endImportLine(self, trailer, originalLine):
        """
        After the last import clause, handle any remaining characters
        on the line (usually a comment).  We need the original line as
        well, in case no modifications were made to any of the import
        clauses.
        """
        if (self._commaOne != "" and self._commaTwo != ""):
            self._changedOne = True
            self._changedTwo = True

        if (self._changedTwo):
            if (self._commaOne != ""):
                self._write(self._newLineOne + "\n")
                print self._newLineOne
                if (DryRun):
                    self._lineNumber = self._lineNumber - 1
            self._write(self._newLineTwo + trailer)
            print self._newLineTwo + trailer
            self.fileChanged()
        else:
            if (self._changedOne):
                self._write(self._newLineOne + trailer)
                print self._newLineOne + trailer
                self.fileChanged()
            else:
                self.writeLine(originalLine)

    def close(self, whichAction):
        """
        Write the file if it has changed.  Report if a file is being
        written, tagged by whichAction.
        """
        if (self._fileChanged):
            print "%s: changed renaming %s" % (self._fileName, whichAction)
            if (not DryRun):
                newFile = open(self._fileName, 'w')
                newFile.write(self._contents)
                newFile.close()


def renameModule(oldPackage, oldModule, newPackage, newModule):
    """
    Iterate through all files in the current directory (recursively),
    renaming oldPackage.oldModule to newPackage.newModule.
    """
    if (oldPackage == ""):
        oldPackageDot = ""
    else:
        oldPackageDot = oldPackage + "."
    oldPath = oldPackageDot + oldModule

    if (newPackage == ""):
        newPackageDot = ""
    else:
        newPackageDot = newPackage + "."
    newPath = newPackageDot + newModule

    whichAction = "%s -> %s" % (oldPath, newPath)

    # oldPath surrounded by something that can't be in an identifier:
    oldPathRegex = re.compile(r'(^|[^\w_])' +
                              re.escape(oldPath) + r'($|[^\w_])')
    oldPathSubstitution = r'\1' + newPath + r'\2'

    newPathRegex = re.compile(r'(^|[^\w_])' +
                              re.escape(newPath) + r'($|[^\w_])')

    for (fileName, moduleName) in ModuleIterator():
        f = open(fileName)
        out = _OutputStream(fileName)

        # Set to True when we encounter "import oldPackage.oldModule"
        # Triggers substitution of the full path wherever it occurs in
        # the file.
        globalSubstitute = False

        for line in f:
            m = newPathRegex.search(line)
            if (m):
                out.error("%s in original, replacement could be ambiguous"
                          % newPath)

            m = importStatementRegex.match(line)
            if (m):
                gotFrom = "None"
                groups = m.groups()
                prefixFromImport = groups[0]
                fromPath = ""
                if (groups[2]):
                    fromPath = groups[2]
                    gotFrom = "Other"
                if (oldPackage != ""):
                    if (fromPath == oldPackage):
                        if (newPackage != ""):
                            prefixFromImport += "from " + newPackage + " "
                        gotFrom = "Package"
                    elif (fromPath == oldPath):
                        prefixFromImport += "from " + newPath + " "
                        gotFrom = "Path"
                    elif (fromPath == oldModule and SubstituteBareModule):
                        prefixFromImport += "from " + newPath + " "
                        gotFrom = "Path"
                else:
                    if (fromPath == oldModule):
                        prefixFromImport += "from " + newPath + " "
                        gotFrom = "Path"

                if (gotFrom == "Other"):
                    # The from clause we've seen cannot result in any
                    # substitutions.
                    out.writeLine(line)
                    continue

                prefixFromImport = prefixFromImport + "import "
                # At this point, prefixFromImport has accumulated any
                # leading spaces, an optional from clause, and always
                # the word import.

                prefixOriginalFromImport = line[m.start():m.end()]
                # Same as prefixFromImport, but with the original from
                # clause intact.

                out.startImportLine(prefixFromImport, prefixOriginalFromImport)

                importList = line[m.end():]
                while (True):
                    m = importClauseRegex.match(importList)
                    if (m):
                        groups = m.groups()
                        importPath = groups[0]
                        asClause = ""
                        if (groups[2]):
                            asClause = groups[2]

                        if (gotFrom == "None"):
                            if (importPath == oldModule
                                and SubstituteBareModule):

                                if (asClause == ""):
                                    # import oldModule
                                    out.collectImportClause(newPath, oldModule)
                                else:
                                    # import oldModule as asClause
                                    out.collectImportClause(newPath, asClause)
                            elif (importPath == oldPath):
                                if (asClause == ""):
                                    # import oldPath
                                    out.collectImportClause(newPath)
                                    globalSubstitute = True
                                else:
                                    # import oldPath as asClause
                                    out.collectImportClause(newPath, asClause)
                            else:
                                # import other (as asClause)
                                out.collectImportClause(importPath,
                                                        asClause,
                                                        originalFrom = True,
                                                        isEdit = False)
                        elif (gotFrom == "Package"):
                            if (importPath == oldModule):
                                if (asClause == ""):
                                    # from oldPackage import oldModule
                                    out.collectImportClause(newModule,
                                                            oldModule)
                                else:
                                    # from oldPackage import oldMod as asClause
                                    out.collectImportClause(newModule, asClause)
                            else:
                                # from oldPackage import other (as asClause)
                                out.collectImportClause(importPath,
                                                        asClause,
                                                        originalFrom = True,
                                                        isEdit = False)

                        elif (gotFrom == "Path"):
                            # from oldPath import symbol (as asClause)
                            out.collectImportClause(importPath, asClause)

                        importList = importList[m.end():]
                        if (len(importList) > 0 and importList[0] == ","):
                            importList = importList[1:]
                        else:
                            break
                    else:
                        break
                out.endImportLine(importList, line)

            else: # not an import statement
                if (oldPackage != ""):
                    m = oldPathRegex.search(line)
                    if (m):
                        (newLine, substitutionCount) = re.subn(
                            oldPathRegex, oldPathSubstitution, line)
                        if (substitutionCount > 0):
                            if (globalSubstitute):
                                out.writeLine(newLine)
                                out.fileChanged()
                            else:
                                out.error("%s referenced before import"
                                          % oldPath)
                                out.writeLine(line)
                    else:
                        out.writeLine(line)
                else:
                    out.writeLine(line)
        out.close(whichAction)

def usage():
    print >>sys.stderr, "usage: %s old/path.py new/pathname.py" % sys.argv[0]
    print >>sys.stderr, " --dry-run disables writing changed files"
    print >>sys.stderr, " --ignore-bare-module disables substituting a module"
    print >>sys.stderr, "      without accompanying package name"
    sys.exit(1)

def findOption(optionString):
    """
    Return a boolean indicating weather or not optionString is one of
    the elements of sys.argv.  It's removed from the argument list
    wherever it is found.
    """
    ret = False
    # Run the loop backwards so we can look at earlier indicies after
    # deleting a later one.
    for i in range(len(sys.argv)-1, 0, -1):
        if (optionString == sys.argv[i]):
            ret = True
            del sys.argv[i]
    return ret

if (__name__ == '__main__'):

    DryRun = findOption("--dry-run")
    SubstituteBareModule = not findOption("--ignore-bare-module")

    if (len(sys.argv) != 3):
        print "len(sys.argv): %d" % len(sys.argv)
        usage()
    oldPath = sys.argv[1]
    newPath = sys.argv[2]
    (oldPackage, oldModule) = separatePath(pathToModule(oldPath))
    (newPackage, newModule) = separatePath(pathToModule(newPath))

    if (oldModule == ""):
        print >>sys.stderr, "old module name is missing"
        usage()
    if (oldPackage == ""):
        pass
        #if (os.path.isdir(moduleToPath(oldModule))):
            #print >>sys.stderr, "old module name is a package"
            #usage()
    else:
        if (os.path.isdir(moduleToPath(oldPackage + "." + oldModule))):
            print >>sys.stderr, "old module path is a package"
            usage()

    if (newPackage == ""):
        if (os.path.isdir(moduleToPath(newModule))):
            newPackage = newModule
            newModule = oldModule
    else:
        if (newModule != ""):
            if (os.path.isdir(moduleToPath(newPackage + "." + newModule))):
                newPackage = newPackage + "." + newModule
                newModule = oldModule
        else:
            newModule = oldModule

    if (oldPackage == newPackage and oldModule == newModule):
        print >>sys.stderr, "old and new modules are the same"
        usage()

    renameModule(oldPackage, oldModule, newPackage, newModule)

