#!/bin/sh

# Usage: ./updateNV1_Documentation.sh &>NV1_Docs.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > NV1_Docs.timestamp

# Remove files used to check for command successes
rm -rf SVN-D/cad/plugins/NanoVision-1/docs/api/html

# Run doxygen
pushd SVN-D/cad/plugins/NanoVision-1/src/Documentation/
mkdir -p ../../docs/api
/usr/bin/doxygen doxygen.cfg
popd

# Check if doxygen was successful by checking for the existence of the file we
# deleted earlier.
if [ ! -e SVN-D/cad/plugins/NanoVision-1/docs/api/html/index.html ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > NV1_Docs.result

