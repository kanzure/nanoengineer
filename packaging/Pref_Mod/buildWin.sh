#!/bin/sh -x

# The same checks for a stored version in /c/<something> are not in Pref_Mod 
# as they are for gromacs and qutemol.  This is because pref_modifier changes
# with every version number.  Plus, it only adds about two minutes to the build
# time.  Also, this file uses the NE1_Build_Constants for the version number.
# The NE1 and Suite Installers modify this, so if this script is run manually,
# Make sure to make the necessary changes.

if [ "$1" = "" ]
then
  PREF_VERSION="0.0.1"
else
  PREF_VERSION="$1"
fi

TOP_LEVEL=`pwd`
echo $TOP_LEVEL | grep "Pref_Mod"
if [ "$?" != "0" ]
then
  echo "This is not a valid build area"
  exit 1
fi

rm -rf build dist
cp ../../cad/src/NE1_Build_Constants.py .
/c/python24/python setup_win.py py2exe
# There's no installer for this since it's not released with anything other
# than the suite installer.
