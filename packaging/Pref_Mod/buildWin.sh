#!/bin/sh -x

rm -rf build dist
cp ../../cad/src/NE1_Build_Constants.py .
/c/python24/python setup_win.py py2exe
# There's no installer for this since it's not released with anything other
# than the suite installer.
