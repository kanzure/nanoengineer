#!/bin/sh

# Usage: ./runSEMBot.sh &> SEMBot.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > SEMBot.timestamp

# Remove files used to check for command successes
rm -f SVN-D/cad/src/epydoc.config

# Update codebase
svn update
svn update SVN-D/cad/src

# Check if the codebase update was successfull by checking for the existence of
# the file we deleted earlier.
if [ ! -e SVN-D/cad/src/epydoc.config ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > NE1_Docs.result

# Run API documentation generation
./updateNE1_Documentation.sh &>NE1_Docs.log

