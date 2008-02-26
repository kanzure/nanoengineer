#!/bin/sh

tools/Refactoring/RenameModule.py $1 $2
svn mv --force $1 $2
