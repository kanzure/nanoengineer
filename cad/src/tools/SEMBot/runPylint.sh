#!/bin/sh

# Usage: ./runPylint.sh &>Pylint.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > Pylint.timestamp

# Remove files used to check for command successes
#rm -f NE1_Documentation/api-objects.txt

# Run Pylint 
pushd SVN-D/cad/src
/usr/local/bin/pylint --rcfile=../../../Pylint.rcfile a*.py A*.py PM/*.py
popd

# Post process results
./pylint_global.pl SVN-D/cad/src/pylint_global.txt Pylint.result > SVN-D/cad/src/pylint_global.html

# Check if Epydoc was successfull by checking for the existence of the file we
# deleted earlier.
#if [ ! -e NE1_Documentation/api-objects.txt ]; then
#  RESULT="<font color=red>Failed</font>"
#else
#  RESULT=Success
#fi
#echo ${RESULT} > NE1_Docs.result

