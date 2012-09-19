#!/usr/bin/env python

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
  FindPythonGlobals.py

  This is a standalone program for static analysis of python source
  files.  For each file given as an argument, it writes a list of all
  of the global symbols defined by the file, each accompanied by the
  name of the file.  The resulting list can be sorted and used to
  locate a source file given a symbol name.  Symbols which are defined
  in multiple files can be identified as well.

  The program relies on the internal python parser.  As such, it must
  be targeted to a specific version of python.  The initial code was
  written for the python2.5 parser.  Even a small change to the python
  grammar could change the way symbols in the parse tree need to be
  handled.  Turning on the verbose flag prints the complete parse tree
  of the input file, which can be used to determine how to search the
  tree for global definitions.

  To find global symbols, the search routine looks at top level
  statements, and inside of if, for, while, and try statements,
  recursively.  Within these contexts, it looks for def and class
  statements (which it does not look inside of).  It also looks for
  expressions of the form "NAME = ...".

  Note: this will not find globals defined in assignments with
  multiple =, like "a = b = False".  The global b would be missed
  in this case.

  @author: Eric Messick
  @version: $Id$
  @copyright: 2007 Nanorex, Inc.
  @license: GPL
"""

import sys
import string
import parser
import symbol
import token

verbose = False
#verbose = True
"""Set to true to print entire parse tree."""

s_fileName = ""
"""File currently being parsed."""

traverseTheseTokens = [
    symbol.encoding_decl,
    symbol.file_input,
    symbol.stmt,
    symbol.simple_stmt,
    symbol.small_stmt,
    symbol.compound_stmt,
    symbol.testlist,
    symbol.test,
    symbol.or_test,
    symbol.and_test,
    symbol.not_test,
    symbol.comparison,
    symbol.expr,
    symbol.xor_expr,
    symbol.and_expr,
    symbol.shift_expr,
    symbol.arith_expr,
    symbol.term,
    symbol.factor,
    symbol.power,
    ]
"""
   Parse tree nodes of these types should have their contents searched
   when they are encountered.  These are the intervening nodes that
   show up between the top level node in the parse tree (file_input)
   and the actual definition nodes that we're looking for.  They
   mostly describe components of expressions.
"""

suiteTokens = [
    symbol.if_stmt,
    symbol.for_stmt,
    symbol.while_stmt,
    symbol.try_stmt,
    ]
"""
   Parse tree nodes which contain suite nodes, each of which we wish
   to traverse.  These are generally the introducers of compound
   statements.
"""

def printToken(tok, level):
    """
       Print the symbolic name for a token or symbol from a python
       parse tree.

       @param tok: token to be printed.
       @type tok: integer, values defined in symbol or token modules

       @param level: recursion depth, specified as a string of spaces.
       @type level: string
    """
    if (token.ISTERMINAL(tok)):
        print level + token.tok_name[tok]
    else:
        print level + symbol.sym_name[tok]

def printParseTree(tree, level):
    """
       Print the whole parse tree beneath the current node.

       @param tree: the top level node being printed.
       @type tree: list, first elements of which are integer tokens

       @param level: recursion depth, specified as a string of spaces.
       @type level: string
    """
    printToken(tree[0], level)
    for element in tree[1:]:
        if (isinstance(element, list)):
            printParseTree(element, level + ".")
        else:
            print level + repr(element)
#    print level + "end"

def lookAt(tree):
    """
       Visit a node in the parse tree looking for a global symbol
       definition.

       @param tree: the parse node being visited.
       @type tree: list, first elements of which are integer tokens
    """
    nodeType = tree[0]
    if (verbose):
        printToken(nodeType, "looking at: ")

    # Look inside nodes of these types.
    if (nodeType in traverseTheseTokens):
        for element in tree[1:]:
            lookAt(element)

    # Look inside of assignment statements (name = ...).
    elif (nodeType == symbol.expr_stmt):
        if (len(tree) > 2):
            if (tree[2][0] == token.EQUAL):
                lookAt(tree[1])

    # Look inside suites of statements within block introducers like
    # if and while.
    elif (nodeType in suiteTokens):
        for outerElement in tree[1:]:
            if (outerElement[0] == symbol.suite):
                for suiteElement in outerElement[1:]:
                    if (suiteElement[0] == symbol.stmt):
                        lookAt(suiteElement)

    # What we're actually looking for: def, class, and atoms.
    elif (nodeType == symbol.funcdef):
        functionName = tree[2]
        print functionName[1] + ": " + s_fileName
    elif (nodeType == symbol.classdef):
        className = tree[2]
        print className[1] + ": " + s_fileName
    elif (nodeType == symbol.atom):
        atomName = tree[1]
        if (atomName[0] == token.NAME):
            print atomName[1] + ": " + s_fileName

    elif (verbose):
        printToken(nodeType, "ignoring: ")


def parsePythonFile(filename):
    """
       Read a python source file and print the global symbols defined
       in it.

       The named file is opened and read.  Newlines are canonicalized.
       The whole file is handed to the internal python parser, which
       generates an Abstract Syntax Tree.  This is converted into a
       list form which is then scanned by lookAt() for global symbol
       definitions.

       @param filename: name of a python source file.
       @type filename: string
    """
    file = open(filename)
    codeString = file.read()
    codeString = string.replace(codeString, "\r\n", "\n")
    codeString = string.replace(codeString, "\r", "\n")
    if codeString and codeString[-1] != '\n' :
        codeString = codeString + '\n'
#    print "file: %s" % codeString
    file.close()
    try:
        ast = parser.suite(codeString)
    except SyntaxError:
        return
    parseTree = parser.ast2list(ast)
    if (verbose):
        printParseTree(parseTree, "")
    lookAt(parseTree)

if (__name__ == '__main__'):
    for s_fileName in sys.argv[1:]:
#        print >>sys.stderr, "processing " + s_fileName
        parsePythonFile(s_fileName)
