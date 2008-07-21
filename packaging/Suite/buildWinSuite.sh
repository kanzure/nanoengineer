#!/bin/sh -x

# Usage: Run ./buildWinSuite.sh from the Suite directory in packaging.


# Set control variable to build packages if they are not build already
BUILD_IF_UNBUILT=1

# Set up path variables
cd ../..
TOP_LEVEL=`pwd`
DIST_ROOT=$TOP_LEVEL/cad/src/dist
DIST_CONTENTS=$DIST_ROOT

# Set up version information
VERSION_NUM="1.1.1"
RC_NUMBER="0"

# Do a basic check for sanity in the build area.
if [ ! -e "$TOP_LEVEL/cad/src" ]
then
  echo "The build directories are not valid"
  exit 1
fi

# Check to see if the smaller packages are built

# Start with Pref_Mod since it's easy to build
cd $TOP_LEVEL
if [ ! -e "$TOP_LEVEL/packaging/Pref_Mod/build" ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
    cd packaging/Pref_Mod
    ./buildWin.sh || exit 1
  else
    echo "Build Pref_Mod before continuing"
    exit 1
  fi
fi

# insert gromacs and qutemolx in here when they are ready.

#Check for an NE1 build
cd $TOP_LEVEL
if [ ! -e "$TOP_LEVEL/cad/src/build" ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
#   Set version information for NE1
    cat packaging/buildWin.sh | sed -e "s:^VERSION_NUM=.*:VERSION_NUM=\\\"$VERSION_NUM\\\":" | sed -e "s:^RC_NUMBER=.*:RC_NUMBER=\\\"$RC_NUMBER\\\":" > packaging/buildWin.sh.tmp
    mv packaging/buildWin.sh.tmp packaging/buildWin.sh || exit 1
    cd packaging
    ./buildWin.sh || exit 1
  else
    echo "Build NE1 before continuing"
    exit 1
  fi
fi  

cd $TOP_LEVEL

# Made it this far, continue building the suite.  Mod the suite installer files
cat packaging/Suite/Win32/suite_installer.nsi | sed -e "s:^!define PRODUCT_VERSION .*:!define PRODUCT_VERSION \\\"$VERSION_NUM\\\":" > packaging/Suite/Win32/suite_installer.nsi.btmp
mv packaging/Suite/Win32/suite_installer.nsi.btmp packaging/Suite/Win32/suite_installer.nsi || exit 1

# Create the installer
"c:/program files/nsis/makensis.exe" packaging/Suite/Win32/suite_installer.nsi

