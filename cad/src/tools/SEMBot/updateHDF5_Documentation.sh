#!/bin/sh

# Usage: ./updateHDF5_Documentation.sh &>HDF5_Docs.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > HDF5_Docs.timestamp

# Remove files used to check for command successes
rm -rf SVN-D/cad/plugins/HDF5_SimResults/docs/api/html

# Run doxygen
pushd SVN-D/cad/plugins/HDF5_SimResults/src/Documentation/
mkdir -p ../../docs/api
/usr/bin/doxygen doxygen.cfg
popd

# Check if doxygen was successful by checking for the existence of the file we
# deleted earlier.
if [ ! -e SVN-D/cad/plugins/HDF5_SimResults/docs/api/html/index.html ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > HDF5_Docs.result

