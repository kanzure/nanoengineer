#!/bin/sh

# run regression tests
#
# how to make a regression test:
#
# Inside one of the directories listed below, you need to create three files.
# I'm going to call them test_000X.* here.  Just number them sequentially
# although that doesn't really matter.
#
# The first file is the input data file for the test run.  It will
# usually be called test_000X.mmp.  If it's called something else, or
# there are more than one of them (or zero of them), you can specify
# that using the INPUT directive in the .test file.
#
# The second file is the test description file: test_000X.test.
# This file describes the inputs, outputs, and program arguments
# for the test.  The default values should be fine for minimizer tests.
# For dynamics runs you'll need to specify the program arguments:
#
# PROGRAM simulator -f900 -x test_000X.mmp
#
# See runtest.sh for a complete description.
#
# The third file is the expected output.  Generate this using
# runtest.sh like this (in the test directory):
#
# ../../runtest.sh test_000X.test > test_000X.out
#
# You can change the list of output files to be included
# using the OUTPUT directive in the .test file.
#
# Check this file to make sure the output looks reasonable, then
# rerun regression.sh before checking in the test_000X.* files.

TESTDIRS="tests/minimize tests/dynamics tests/rigid_organics"

RET=0
GEN=0
if [ "x$1" = "x--generate" ]; then
    GEN=1
fi

rm -f /tmp/testsimulator
ln -s $PWD/simulator /tmp/testsimulator

for dir in $TESTDIRS; do
    for i in $dir/*.test; do
	echo Running $i
	base=`basename $i .test`
	out=$dir/$base.out
	./runtest.sh $i > $out.new
	if [ ! -f $out -a $GEN -ne 0 ]; then
	    echo Generated new $out
	    cp $out.new $out
	fi
	if cmp -s $out $out.new ; then
	    rm $out.new
	else
	    echo Test failed: $i 1>&2
	    diff $out $out.new > $out.diff
	    RET=1
	fi
    done
done

rm -f /tmp/testsimulator

exit $RET
