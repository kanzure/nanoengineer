#!/bin/sh

# $Id$

# usage: 
# % cd cad/src
# % ./tools/pylint-some.sh <specific source files...>
# now examine pylint-output

# WARNING: has some duplicated code with pylint-all.sh.

# Disable the message(s) with the given id(s).
# C0103 = ...?
# W0107 = Unnecessary pass statement [bruce 071106]
# W0603 = Using the global statement [bruce 071106]
# W0142 = Used * or ** magic [bruce 071106]
# 
# the above are disabled in Pylint.rcfile, but to keep the output smaller
# we'll disable more in this script:
#
# C0301 = Line too long (since so common in our files)
# C0322 = Operator not preceded by a space (only because of its verbose output)
# C0323 = Operator not followed by a space
# C0324 = Comma not followed by a space
# 
# And these are in addition to the ones above from pylint-all,
# to make this more useful when splitting files:
# 
# W0511 = TODO
# C0302 = Too many lines in module
# R0901 = Too many ancestors
# R0902 = Too many instance attributes
# R0904 = Too many public methods
# R0912 = Too many branches 
# R0913 = Too many arguments
# R0914 = Too many local variables
# R0915 = Too many statements
# C0111 = Missing docstring
# C0112 = Empty docstring
#
# We also remove 'Access to a protected member' warnings (including W0212) when they
# are about attributes starting with _f_, since that is our convention for 
# friend methods/attrs for which some external access is legitimate.

### todo: error if no arguments provided to this script

pylint --reports=n \
    --include-ids=yes \
    --files-output=n \
    --output-format=parseable \
    --disable-msg=C0103,W0107,W0603,W0142,C0301,C0322,C0323,C0324,W0511,C0302,R0901,R0902,R0904,R0912,R0913,R0914,R0915,C0111,C0112 \
    --rcfile=tools/SEMBot/Pylint.rcfile \
    $* | fgrep -v 'Access to a protected member _f_' > pylint-output

echo "produced pylint-output (presumably); here are its import-related warnings (if any):"

egrep 'W0403|W0611|E0602' pylint-output

echo "done"

# end
