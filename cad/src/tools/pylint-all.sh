#!/bin/sh

# $Id$

# usage: 
# % cd cad/src
# % ./tools/pylint-all.sh
# now examine pylint-output and/or pylint-messages/*.txt



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


pylint --reports=n \
    --include-ids=yes \
    --files-output=n \
    --output-format=parseable \
    --disable-msg=C0103,W0107,W0603,W0142,C0301,C0322,C0323,C0324 \
    --rcfile=tools/SEMBot/Pylint.rcfile \
    `tools/AllPyFiles.sh` > pylint-output

rm -rf pylint-messages
mkdir pylint-messages
cd pylint-messages
../tools/pylint-sort-msgs.py < ../pylint-output

# end
