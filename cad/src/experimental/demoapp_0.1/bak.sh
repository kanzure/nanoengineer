#!/bin/sh
mkdir ../demoapp-baks/bak-$1
find . -name \*.py -exec cp -pi '{}' ../demoapp-baks/bak-$1 \;
cp -pi *.sh *.txt Makefile ../demoapp-baks/bak-$1
cd ../demoapp-baks/bak-$1
zip /tmp/bak-$1 *
ls -l /tmp/bak-$1.zip
