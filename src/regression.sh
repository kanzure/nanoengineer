#!/bin/sh

RET=0
TMPDIR=/tmp/regress$$

trap 'rm -rf $TMPDIR' 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 18 19 20 21 22 23 24 25 26 27 28 29 30 31

for i in tests/minimize/*.mmp; do
    base=`basename $i .mmp`
    rm -rf $TMPDIR
    mkdir $TMPDIR
    cp $i $TMPDIR
    ./simulator -m -x $TMPDIR/$base.mmp > $TMPDIR/$base.stdout 2> $TMPDIR/$base.stderr
    for j in tests/minimize/$base.*; do
	file=`basename $j`
	if cmp -s tests/minimize/$file $TMPDIR/$file; then
	    true
	else
	    echo Test failed: $file
	    diff tests/minimize/$file $TMPDIR/$file
	    RET=1
	fi
    done
done

exit $RET
