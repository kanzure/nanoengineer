#!/bin/sh

# $Id$

find . -name \*.py -print | sed '
/experimental/d
/scratch/d
/outtakes/d
/tools/d
/tests/d
/\/\./d
' | sort
