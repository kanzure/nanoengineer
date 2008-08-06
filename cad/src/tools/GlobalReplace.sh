#!/bin/sh

# usage: GlobalReplace.sh [-n] searchRegex replaceString filelist...

# $Id$

# NOTE: it's a good idea to run this without any files to process to
# check that the quoting in the sed script is ok.

# WARNING: at least on the Mac, and judging by the diff output using -n,
# this also adds a newline at the end of every source file which lacks one.
# This is ok on the files that it needs to modify anyway,
# but not on the files it otherwise doesn't need to.
# To work around this problem, only run it on the necessary files,
# which can be found using a command like
#
# % fgrep -l <string> `tools/AllPyFiles.sh`  # to find only source files
#
# or
#
# % find . -name '*.py' -print | xargs fgrep -l <string>  # to find outtakes files, etc

# Example:
#
#   tools/GlobalReplace.sh "old\.symbol" "new.symbol" `tools/AllPyFiles.sh`

dryRun=false
if [ "x$1" = "x-n" ]; then
    dryRun=true
    shift
fi

searchRegex=`echo "$1" | sed 's:/:\\\\/:g'`
replaceString=`echo "$2" | sed 's:/:\\\\/:g'`
shift
shift

cat <<EOF > /tmp/sed$$
s/$searchRegex/$replaceString/g
EOF

cat /tmp/sed$$

for i in $*; do
    sed -f /tmp/sed$$ < $i > $i.tmp$$
    if cmp --silent $i $i.tmp$$; then
	rm $i.tmp$$
    else
	diff -u $i $i.tmp$$
	if $dryRun; then
	    rm $i.tmp$$
	else
	    mv $i.tmp$$ $i
	fi
    fi
done

rm /tmp/sed$$
