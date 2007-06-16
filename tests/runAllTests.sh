#!/bin/sh

for test in *Test.py; do
  echo ======================================================================
  echo Executing tests in: $test
  PYTHONPATH=../src python $test -v
done

