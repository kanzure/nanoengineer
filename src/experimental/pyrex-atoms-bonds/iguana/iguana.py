#!/usr/bin/python

import string, types, sys, re
import ighelp

####################################################

def compile(str):
    global program, symbol_table
    def is_a_number(str):
        try: string.atof(str); return 1
        except ValueError: return 0
    my_stack = [ ]
    symbol_table = { }
    program = [ ]
    M = string.split(str)
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
            if symbol_table.has_key(spawned):
                # spawn a thread running an existing definition
                program.append(ighelp.verbs['spawn'])
                program.append(symbol_table[spawned])
            else:
                # set up a forward reference
                program.append('spawn:' + spawned)
                program.append(None)

        elif x == 'if':
            # build unresolved forward branch
            my_stack.append(len(program))
            program.append(ighelp.verbs['zjump'])
            program.append(0)
        elif x == 'else':
            x = my_stack.pop()
            # build unresolved forward branch
            my_stack.append(len(program))
            program.append(ighelp.verbs['jump'])
            program.append(0)
            # resolve forward branch
            program[x+1] = len(program)
        elif x == 'endif':
            # resolve forward branch
            x = my_stack.pop()
            program[x+1] = len(program)

        elif x == 'begin':
            # set up destination for future backward jump
            my_stack.append(len(program))
        elif x == 'until':
            # build and resolve backward branch
            program.append(ighelp.verbs['zjump'])
            program.append(my_stack.pop())
        elif x == 'forever':
            # like 'until' except unconditional
            program.append(ighelp.verbs['jump'])
            program.append(my_stack.pop())

        elif x == 'do':
            # like 'until' except unconditional
            program.append(ighelp.verbs['do'])
            my_stack.append(len(program))

        elif x == 'loop':
            # like 'until' except unconditional
            program.append(ighelp.verbs['loop'])
            program.append(my_stack.pop())

        elif x[-1:] == ':':
            # the start of a definition, put it in the symbol table
            symbol_table[x[:-1]] = len(program)
        elif ighelp.verbs.has_key(x):
            # a primitive
            program.append(ighelp.verbs[x])
        elif symbol_table.has_key(x):
            # calling an existing definition
            program.append(ighelp.verbs['call'])
            program.append(symbol_table[x])
        elif is_a_number(x):
            # a number
            program.append(ighelp.verbs['lit'])
            program.append(string.atof(x))
        else:
            # if we can't identify it, assume it's a forward
            # reference, which we represent as a string followed by a
            # don't-care
            program.append(x)
            program.append(None)
        i = i + 1
    i = 0
    # clean up the forward references
    while i < len(program):
        x = program[i]
        # there are two kinds of forward references, calls and spawns
        if type(x) == types.StringType:
            if x[:6] == 'spawn:':
                program[i] = ighelp.verbs['spawn']
                program[i+1] = symbol_table[x[6:]]
            else:
                program[i] = ighelp.verbs['call']
                program[i+1] = symbol_table[x]
        i = i + 1
    symbol_table = symbol_table

def explain():
    def reverseDict(d):
        v = { }
        for k in d.keys():
            v[d[k]] = k
        return v
    v = reverseDict(ighelp.verbs)
    s = reverseDict(symbol_table)
    i = 0
    r = ''
    for x in program:
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
    return r


def thread(func, mem=None):
    T = ighelp.thread(program, mem)
    T.pc = symbol_table[func]
    return T


class Node:

    def __init__(self, function, mem=None):
        if mem == None:
            mem = self
        self.memory = mem
        thread(function, mem)

    def thread(self):
        return ighelp.thread(program, self.memory)


def step(n=1):
    ighelp.step(n)

def run():
    while ighelp.active_threads() > 0:
        ighelp.step(1000)

################################################

if __name__ == '__main__':

    class SharedMemoryNode(Node):

        SHMEMSIZE = 1000
        INDMEMSIZE = 1000
        shared_memory = SHMEMSIZE * [ 0.0 ]

        def __init__(self, function):
            Node.__init__(self, function, self)
            self.individual_memory = self.INDMEMSIZE * [ 0.0 ]

        # Here is an easy way to define memory-mapped I/O for
        # our threads.

        def __setitem__(self, n, x):
            try:
                self.individual_memory[n] = x
                return
            except IndexError:
                n = n - self.INDMEMSIZE
            self.shared_memory[n] = x

        def __getitem__(self, n):
            try:
                return self.individual_memory[n]
            except IndexError:
                n = n - self.INDMEMSIZE
            return self.shared_memory[n]

    P = """
    main:
        tryloop exit

    +!:
        <atomic dup @ rot + swap ! atomic> exit

    foo:
        rand println exit

    bar:
        2.718 println exit

    quux:
        ouch exit

    tryloop:
        600 0 do
            i 1000 +!
        loop
        exit

    quickloop:
        600 0 do
            /* Do nothing in the loop. It turns out
             * "@" and "!" are really pretty slow.
             */
        loop
        exit
    """

    compile(P)
    nodelist = [ ]

    N = 10
    for i in range(N):
        node = SharedMemoryNode('main')
        nodelist.append(node)

    run()

    print SharedMemoryNode.shared_memory[:5]
    print N * (600 * 599) / 2
