#!/usr/bin/env python

"""
ParseINI.py

Implements a rudimentary parser for config files used by GROMACS to
define force fields, such as the AMBER force field.

Comments start with ; and can appear anywhere.

These files are designed to be processed through cpp, so they may
include #define statements.  For the intended use of this module, we
will treat these as comments.

Blank lines are ignored.

Sections are introduced with '[ section_name ]'.  Indendation of this
indicates nesting of sections in .rtp files.

Data lines within a section consist of a set of whitespace delimited
fields, the interpretation of which varies depending on the section.

This module parses a single file, and returns a data structure
representing the top level of the file.  Each Section is a list of
Elements, each of which could be either another Section, or an Entry.

"""

class INIElement(object):
    pass

class Section(INIElement):
    def __init__(self, name):
        self.name = name
        self.elements = []

    def addElement(self, element):
        self.elements.append(element)

    def getElements(self):
        return self.elements

    def get(self, index):
        return self.elements[index]

    def write(self, indent):
        print "%s[ %s ]" % (indent, self.name)
        for element in self.elements:
            element.write(indent + " ")

class Entry(INIElement):
    def __init__(self, columns):
        self.columns = columns

    def getColumn(self, col):
        return self.columns[col]

    def getColumnCount(self):
        return len(self.columns)

    def write(self, indent):
        print "%s%s" % (indent, " ".join(self.columns))

class ParseINI(object):
    def __init__(self, filename):
        f = open(filename)
        self._lines = f.readlines()
        f.close()
        self._lineNumber = -1
        self._sectionIndent = -1
        self._sectionName = "default"
        self._nextLine()

    def _nextLine(self):
        self._lineNumber = self._lineNumber + 1
        while (self._lineNumber < len(self._lines)):
            line = self._lines[self._lineNumber]
            semi = line.find(";")
            if (semi >= 0):
                line = line[:semi]
            oct = line.find("#")
            if (oct >= 0):
                line = line[:oct]
            line = line.strip()
            if (len(line) == 0):
                self._lineNumber = self._lineNumber + 1
                continue
            self._columns = line.split()
            return
        self._columns = None

    def _parseSectionHeader(self):
        cols = self._columns
        if (cols != None and cols[0] == "[" and cols[-1] == "]"):
            sectionName = " ".join(cols[1:-1])
        else:
            sectionName = "default"
        line = self._lines[self._lineNumber]
        spaces = 0
        while (line[0] == " "):
            line = line[1:]
            spaces = spaces + 1
        self._sectionIndent = spaces
        self._sectionName = sectionName


    def parse(self):
        sectionName = self._sectionName
        indent = self._sectionIndent
        contents = Section(sectionName)
        while (self._columns != None):
            cols = self._columns
            if (cols[0] == "["):
                self._parseSectionHeader()
                while (self._columns != None and self._sectionIndent > indent):
                    self._nextLine()
                    nestedSection = self.parse()
                    contents.addElement(nestedSection)
                return contents
            else:
                thisRecord = Entry(cols)
                contents.addElement(thisRecord)
            self._nextLine()
        return contents

if (__name__ == '__main__'):
    import sys
    parser = ParseINI(sys.argv[1])
    tree = parser.parse()
    tree.write("")
