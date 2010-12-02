#!/bin/sh

# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
# A little utility for figuring out what order python files are
# loaded.  Run this on all .py files you're interested in.
#
# Try: 
#  AddImportPrint `find . -name \*.py -print`
#
# Then run them.  They'll print the order that they're loaded.
#
# Best done in a seperate cvs working tree that you can just throw away.

for i in $*; do
	echo $i
	sed '2,$d' < $i > tmp$$
	echo print '"now importing' $i '"' >> tmp$$
	sed '1d' < $i >> tmp$$
	mv tmp$$ $i
done
