#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""This class should represent an MMP file as an abstract data object.
We can read it in from a conventional *.mmp text file, and if we wish,
write it out in some kind of XML format.

XML has many flaws, but it's got some big benefits. It's popular and
there are parsers and generators in every language. XML files are
unambiguous; once you have a DTD or schema their validity is never in
question. We might be smart to define a DTD or schema for the XML
version of the MMP file, and keep it under CVS control.
"""

import types

DEBUG = False

RecordTypes = ( )

class Mismatch(Exception):
    pass

class Record:

    def __init__(self):
        self.children = [ ]

    def __repr__(self, depth=0):
        r = self.__class__.__name__
        if hasattr(self, "name"):
            r += " " + self.name
        for c in self.children:
            r += "\n" + ((depth + 1) * "    ") + c.__repr__(depth+1)
        return r

    def matches(self, line, pattern):
        if not line.startswith(pattern):
            raise Mismatch, pattern + ":::" + line
        return line[len(pattern):]

    def processFirstLine(self, line):
        pass

    def read(self, lines, depth=0):
        lines = self.readFirstLine(lines, depth)
        if DEBUG:
            print (depth * "    ") + self.keyword
        if hasattr(self, "bairns"):
            return self.readRemainingLines(lines, depth)
        else:
            return lines

    def readFirstLine(self, lines, depth):
        #if DEBUG: print self, "FIRST LINE", lines[0][:-1]
        if len(lines) < 1:
            raise Mismatch, "no lines left"
        firstline = lines[0]
        firstline = self.matches(firstline,
                                 self.keyword + " ")
        self.processFirstLine(firstline)
        return lines[1:]

    def readRemainingLines(self, lines, depth):
        while lines:
            #if DEBUG: print self, "NEXT LINE", lines[0][:-1]
            if hasattr(self, "endline"):
                if lines[0].startswith(getattr(self, "endline")):
                    return lines[1:]
            found = False
            for rtype in self.bairns:
                try:
                    newRecord = rtype()
                    lines = newRecord.read(lines, depth+1)
                    self.children.append(newRecord)
                    found = True
                    break
                except Mismatch:
                    pass
            if not found:
                if depth == 0:
                    print "?", lines[0]
                    lines = lines[1:]
                else:
                    return lines

class TemperatureRecord(Record):
    keyword = "kelvin"
    pass

class GroupRecord(Record):
    keyword = "group"
    def processFirstLine(self, line):
        self.name = line.strip()
    pass

class InformationRecord(Record):
    keyword = "info"
    pass

class CoordinateSystemRecord(Record):
    keyword = "csys"
    pass

class MoleculeRecord(Record):
    keyword = "mol"
    def processFirstLine(self, line):
        self.name = line.strip()
    pass

class AtomRecord(Record):
    keyword = "atom"
    pass

class Bond1Record(Record):
    keyword = "bond1"
    pass


class MmpFile(Record):

    keyword = "mmpformat"


MmpFile.bairns = (TemperatureRecord,
                  GroupRecord)
MmpFile.endline = "end molecular machine part"
GroupRecord.bairns = (InformationRecord,
                      CoordinateSystemRecord,
                      MoleculeRecord)
GroupRecord.endline = "egroup"
MoleculeRecord.bairns = (AtomRecord,)
AtomRecord.bairns = (Bond1Record,)


examples = [
    "../../../partlib/bearings/BigBearing.mmp",
    "../../../partlib/bearings/BuckyBearing.mmp",
    "../../../partlib/bearings/HCBearing.mmp",
    "../../../partlib/bearings/SmallBearing.mmp",
    "../../../partlib/bearings/ThrustBearing.mmp"
    ]

for e in examples:
    print "#############"
    print e
    lines = open(e).readlines()
    m = MmpFile()
    m.read(lines)
    print m
