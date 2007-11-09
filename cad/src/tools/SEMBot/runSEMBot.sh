#!/bin/sh

# Usage: ./runSEMBot.sh &> SEMBot.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > SEMBot.timestamp

# Remove files used to check for command successes
rm -f SVN-D/cad/src/epydoc.config

# Update codebase
svn update
svn update SVN-D/cad/doc
svn update SVN-D/cad/licenses-common
svn update SVN-D/cad/partlib
svn update SVN-D/cad/plugins/DNA
svn update SVN-D/cad/src
svn update SVN-D/sim/src

# Check if the codebase update was successful by checking for the existence of
# the file we deleted earlier.
if [ ! -e SVN-D/cad/src/epydoc.config ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > NE1_Docs.result

# Run API documentation generation
echo "Running updateNE1_Documentation.sh, output in NE1_Docs.log"
./updateNE1_Documentation.sh &>NE1_Docs.log


#
# QA Test Harness
#
# Create the QA Test Harness timestamp
echo `date +"%a %b %e %T EDT %Y"` > QA_TestHarness.timestamp

# Run Pylint
echo "Running runPylint.sh, output in Pylint.log"
./runPylint.sh &> Pylint.log
if [ `grep -c Traceback Pylint.log` != 0 ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > QA_TestHarness.result

# Run dependency cycles discovery script
./updateDependencyGraphs.sh &> DependencyCycles.log

# Run nightly build
#./runNightlyBuild.sh &>NightlyBuild.log

