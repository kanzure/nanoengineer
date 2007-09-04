#!/bin/sh

# usage: GlobalReplace.sh searchRegex replaceString filelist...

# NOTE: it's a good idea to run this without any files to process to
# check that the quoting in the sed script is ok.

# Example:
#
#   tools/GlobalReplace.sh "old\.symbol" "new.symbol" `cat allpyfiles`

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
	echo $i
	diff $i $i.tmp$$
	mv $i.tmp$$ $i
    fi
done

rm /tmp/sed$$
