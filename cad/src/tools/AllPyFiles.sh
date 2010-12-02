#!/bin/sh

find . -name \*.py -print | sed '
/experimental/d
/atombasetests\.py/d
/canvas-b-3\.py/d
/TreeView\.py/d
/TreeWidget\.py/d
' | sort
