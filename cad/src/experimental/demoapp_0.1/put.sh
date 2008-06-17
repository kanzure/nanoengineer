#!/bin/sh
# usage: ./put.sh module.py subdir 
#  moves module.py from where it is to demoapp/subdir
#  after rewriting imports using $W/tools/Refactoring/RenameModule.py.
#  WARNING: does no error checking (except whatever RenameModule does).

$W/tools/Refactoring/RenameModule.py $1 demoapp/$2/
mv $1 demoapp/$2/
