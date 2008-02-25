#!/bin/sh

# run this in cad/src as tools/FindPatternInSource.sh
#
# reads patterns from stdin, and prints matches

while read line; do
    echo
    tools/AllPyFiles.sh | xargs grep "$line"
    echo .
    echo
done
