#!/usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
# $Id$

import string, os, sys, re

variableName = re.compile("^[_a-zA-Z][_a-zA-Z0-9]*$")

class Op:

    def __init__(self, str):
        lst = string.split(str, '#')

        self.name = string.split(lst.pop(0))
        self.cname = self.name[0]
        self.name = self.name[len(self.name) - 1]

        self.inputs = string.split(lst.pop(0))
        self.inputs.reverse()   # because we're popping them
        self.outputs = string.split(lst.pop(0))
        self.tests = ""
        if lst:
            blanks = ' \t\r\n'
            tests = lst.pop(0)
            while tests[:1] in blanks:
                tests = tests[1:]
            while tests[-1:] in blanks:
                tests = tests[:-1]
            self.tests = tests
        assert len(lst) == 0

    def cfunction(self):
        r = (("static int igverb_%s (iguana_thread_object" +
              " *self, int pc)\n{\n") % self.cname)
        vars = [ ]
        for x in self.inputs + self.outputs:
            if variableName.search(x) and x not in vars:
                vars.append(x)
        for x in vars:
            r = r + "    double %s;\n" % x
        if self.inputs:
            r = r + "    CHECK_UNDERFLOW(%d);\n" % len(self.inputs)
        if self.outputs:
            r = r + "    CHECK_OVERFLOW(%d);\n" % len(self.outputs)
        for x in self.inputs:
            r = r + "    self->dspointer--;\n"
            r = r + "    %s = self->data_stack[self->dspointer];\n" % x
        if self.tests:
            r = r + "    " + self.tests + "\n"
        for x in self.outputs:
            r = r + "    self->data_stack[self->dspointer] = %s;\n" % x
            r = r + "    self->dspointer++;\n"
        return r + "    return pc;\n}\n\n"

print """#include "Python.h"
#include "ighelp.h"
#define EVILRETURN -1
extern PyObject *IguanaError;
"""

oplist = [ ]

for L in open("ops.b").readlines():
    if len(string.split(L, '#')) > 1:
        op = Op(L)
        oplist.append(op)
        print op.cfunction()

print """
void add_more_verbs(PyObject *verb_dict)
{"""

for op in oplist:
    print ("""    PyDict_SetItemString(verb_dict, "%s",
                         PyInt_FromLong((long) igverb_%s));"""
           % (op.name, op.cname))

print "}"
