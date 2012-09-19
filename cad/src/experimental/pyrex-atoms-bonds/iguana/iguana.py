#!/usr/bin/python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
# $Id$

import string, types, sys, re
from ighelp import *

####################################################

class Program:
    def __init__(self):
        self.opcodes = [ ]
        self.symtab = { }
    def run(self):
        while active_threads() > 0:
            step(1000)
    def __len__(self):
        return len(self.opcodes)
    def __getitem__(self, i):
        return self.opcodes[i]
    def __setitem__(self, i, v):
        self.opcodes[i] = v
    def append(self, x):
        self.opcodes.append(x)
    def setSymbol(self, k, v):
        self.symtab[k] = v
    def getSymbol(self, k):
        return self.symtab[k]
    def hasSymbol(self, k):
        return self.symtab.has_key(k)
    def thread(self, func, mem=None):
        T = thread(self.opcodes, mem)
        T.pc = self.symtab[func]
        return T
    def compile(self, str):
        def is_a_number(str):
            try: string.atof(str); return 1
            except ValueError: return 0
        my_stack = [ ]
        M = string.split(str)
        start = len(self)
        i = 0
        while i < len(M):
            x = M[i]
            if x == '/*':
                # handle comments, no rocket science here
                while M[i] != '*/':
                    i = i + 1

            elif x == 'spawn':
                i = i + 1
                spawned = M[i]
                if self.hasSymbol(spawned):
                    # spawn a thread running an existing definition
                    self.append(verbs['spawn'])
                    self.append(self.getSymbol(spawned))
                else:
                    # set up a forward reference
                    self.append('spawn:' + spawned)
                    self.append(None)

            elif x == 'if':
                # build unresolved forward branch
                my_stack.append(len(self))
                self.append(verbs['zjump'])
                self.append(0)
            elif x == 'else':
                x = my_stack.pop()
                # build unresolved forward branch
                my_stack.append(len(self))
                self.append(verbs['jump'])
                self.append(0)
                # resolve forward branch
                self[x+1] = len(self)
            elif x == 'endif':
                # resolve forward branch
                x = my_stack.pop()
                self[x+1] = len(self)

            elif x == 'begin':
                # set up destination for future backward jump
                my_stack.append(len(self))
            elif x == 'until':
                # build and resolve backward branch
                self.append(verbs['zjump'])
                self.append(my_stack.pop())
            elif x == 'forever':
                # like 'until' except unconditional
                self.append(verbs['jump'])
                self.append(my_stack.pop())

            elif x == 'do':
                # like 'until' except unconditional
                self.append(verbs['do'])
                my_stack.append(len(self))

            elif x == 'loop':
                # like 'until' except unconditional
                self.append(verbs['loop'])
                self.append(my_stack.pop())

            elif x[-1:] == ':':
                # the start of a definition, put it in the symbol table
                self.setSymbol(x[:-1], len(self))
            elif verbs.has_key(x):
                # a primitive
                self.append(verbs[x])
            elif self.hasSymbol(x):
                # calling an existing definition
                self.append(verbs['call'])
                self.append(self.getSymbol(x))
            elif is_a_number(x):
                # a number
                self.append(verbs['lit'])
                self.append(string.atof(x))
            else:
                # if we can't identify it, assume it's a forward
                # reference, which we represent as a string followed by a
                # don't-care
                self.append(x)
                self.append(None)
            i = i + 1
        finish = len(self)
        i = start
        # clean up the forward references
        while i < finish:
            x = self[i]
            # there are two kinds of forward references, calls and spawns
            if type(x) == types.StringType:
                if x[:6] == 'spawn:':
                    self[i] = verbs['spawn']
                    self[i+1] = self.getSymbol(x[6:])
                else:
                    self[i] = verbs['call']
                    self[i+1] = self.getSymbol(x)
            i = i + 1
    def explain(self):
        def reverseDict(d):
            v = { }
            for k in d.keys():
                v[d[k]] = k
            return v
        v = reverseDict(verbs)
        s = reverseDict(self.symtab)
        i = 0
        r = ''
        for x in self.opcodes:
            try:
                u = s[i]
                r = r + u + ':\n'
            except KeyError:
                pass
            try:
                u = v[x]
                r = r + '    ' + `i` + ' ' + u + '\n'
            except KeyError:
                try:
                    g = ' (' + s[x] + ')'
                except KeyError:
                    g = ''
                r = r + '    ' + `i` + ' ' + `x` + g + '\n'
            i = i + 1
        print r
