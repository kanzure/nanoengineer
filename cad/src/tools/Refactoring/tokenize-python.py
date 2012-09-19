#!/usr/bin/env python
"""
tokenize-python.py -- print tokenization of one or more input .py files

$Id$

History:

bruce 080616 drafted this from an old script I had at home, py-tokenize.py

russ 080617 Added options to format whitespace and to remove certain kinds of
output, to make it more useful for comparing source files for important changes
while ignoring unimportant changes.
"""
import sys

from os.path import basename
from getopt import getopt, GetoptError
from tokenize import generate_tokens, tok_name
from pprint import pprint

usageMsg = '''usage: %s [-t] [-a] [-l] [-c] [-d] [-s n] [-o] files...
    When multiple files are given, "======= file" separators are inserted.

    -t - Print raw token types and strings. (The default is to print
         tokens in an indented text form with generated whitespace.)

    -a - Suppress all, same as "-lcd".
    -l - Suppress printing line breaks within a statement (NL tokens.)
    -c - Suppress printing comments.
    -d - Suppress printing doc strings.

    -s n - Print just the "signature" of each line (the first n words.)
    -o - Suppress printing operators in the signature.

    Examples:
      To check on changes other than comments and file formatting, use the "-a"
      option on the before-and-after versions and diff them.  You can do a whole
      directory with *.py .
        cd before; %s -a *.py > ../before.pytok
        cd ../after; %s -a *.py > ../after.pytok
        cd ..; diff -C 1 before.pytok after.pytok > pytok.diffs

      Use "-aos 2" to concentrate more closely on statement indentation changes.

      indent-diff.gawk filters out *just* indentation changes from the diffs.
        indent-diff.gawk pytok.diffs > pytok.indent-diff
'''
def usage():
    pgm = basename(sys.argv[0])
    print >> sys.stderr, usageMsg % (3*(pgm,))
    return

# Option variables.
printToks = False
noNLs = False
noComments = False
noDocStrs = False
sigWords = 0
noOps = False
filenames = None

def doOpts():
    global printToks, noNLs, noComments, noDocStrs, sigWords, noOps, filenames
    try:
        opts, filenames = getopt(sys.argv[1:], "talcds:o")
    except GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
        pass
    for opt, val in opts:
        if opt == "-t":
            printToks = True
        elif opt == "-a":
            noNLs = noComments = noDocStrs = True
        elif opt == "-l":
            noNLs = True
        elif opt == "-c":
            noComments = True
        elif opt == "-d":
            noDocStrs = True
        elif opt == "-s":
            sigWords = int(val)
            pass
        elif opt == "-o":
            noOps = True
        else:
            usage()
        continue
    return

def improve(tup5):
    typ, text, s, t, line = tup5
    tokname = tok_name[typ]
    if tokname == 'INDENT':
        text = ''
    return (tokname, text)

def py_tokenize(filename_in, file_out):
    ## file_out = open(filename_out, "w")
    file_in = open(filename_in, 'rU')
    g = generate_tokens(file_in.readline)
    li = list(g)
    file_in.close()
    li2 = map(improve, li)
    if printToks:
        pprint(li2, file_out)
    else:
        doText(li2, file_out)
        pass
    return

def doText(tokStrs, file_out):
    prevTok = 'NEWLINE'                 # Start out at the beginning of a line.
    prevString = ''
    firstTok = True
    prevUnary = False
    nTok = 1                            # Token number in the line.
    nWords = 0                          # Number of words in the line.
    indent = 0
    nlIndent = 0                       # Second-level indent within a statement.
    commentIndent = 0
    lineBuff = ""

    nlToks = ('NEWLINE', 'NL', 'COMMENT') # Comments have a newline at the end.
    wordToks = ('NAME', 'NUMBER', 'STRING')
    noSpaceOps = ('.', ':', '(', '[', '{', '}', ']', ')')

    for (tok, tokString) in tokStrs:
        # Various things to ignore.
        if (tok == 'NL' and noNLs or
            tok == 'COMMENT' and noComments or
            prevTok == 'NEWLINE' and tok == 'STRING' and noDocStrs or
            tok != 'NEWLINE' and sigWords > 0 and nWords >= sigWords or
            tok == 'OP' and noOps):
            continue

        # Alter the indentation level.  (These may occur after a NEWLINE token.)
        if tok == 'INDENT':
            indent += 4
            continue
        if tok == 'DEDENT':
            indent -= 4
            continue

        # NEWLINE is the logical end of statement, as opposed to NL, which is
        # mere formatting whitespace.  Comments also end lines.
        if tok in nlToks:
            if not firstTok or tok == 'COMMENT':

                # Indentation for comments.
                if tok == 'COMMENT':
                    if nTok == 1:
                        lineBuff += (indent + commentIndent) * " "
                    else:
                        lineBuff += " "
                        pass
                    pass

                # Output the last token on the line, and then the line.
                lineBuff += tokString

                # Output the line.
                if not noNLs or lineBuff != "\n":
                    file_out.write(lineBuff)
                lineBuff = ""
                pass

                # Second-level indent within a statement, after a NL token
                # that isn't at the beginning of a line.
                if tok == 'NL' and nTok > 1:
                    nlIndent = 4
                else:
                    nlIndent = 0
                pass

            pass
        else:

            # Generate indentation at the beginning of a line.
            if lineBuff == "":
                lineBuff = (indent + nlIndent) * " "

            # Put spaces around word tokens, but not before commas, after unary
            # ops, or around some special binary ops.
            if (nTok > 1 and         # Never before the first token in the line.
                # When we might put out a space before this token.
                (prevTok in wordToks or tok in wordToks or tok == 'OP') and
                # When we wouldn't put out a space before this token.
                not ( prevUnary or
                      (prevTok == 'OP' and (prevString in noSpaceOps
                                            and tok != 'OP')) or
                      tok == 'OP' and (tokString == ','
                                       or tokString in noSpaceOps)) ):
                lineBuff += " "
                pass

            # Output the token.
            lineBuff += tokString
            pass

        # Carry over a little bit of context from the last two tokens.
        prevUnary = (tok == 'OP' and tokString != ',' and
                     tokString not in noSpaceOps and
                     prevTok == 'OP' and prevString not in noSpaceOps)
        # Bug: Comments tokens after a colon appear *before* the INDENT, and
        # similarly after pass, continue, and return, *before* the DEDENT.
        if tok in nlToks:
            if prevTok == 'OP' and prevString == ':':
                commentIndent = 4
            elif (prevTok == 'NAME' and
                  prevString in ('pass', 'continue', 'return')):
                commentIndent = -4
        else:
            commentIndent = 0
            pass

        # The current token becomes the previous.
        prevTok = tok
        prevString = tokString
        firstTok = False         # So we know there really was a previous token.

        # Reset the token and word counters after a newline.
        if tok in nlToks:
            nTok = 1
            nWords = 0
        else:
            nTok += 1
            if tok in wordToks:
                nWords += 1
            pass

        continue
    return

def dofiles(filenames):
    for filename in filenames:
        if len(filenames) > 1:
            print "\n======= [%s]\n" % (filename,)
        py_tokenize(filename, sys.stdout)
    return

def run():
    doOpts()
    if filenames:
        dofiles(filenames)
    else:
        usage()
    return

if __name__ == '__main__':
    run()

# end
