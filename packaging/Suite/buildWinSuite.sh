#!/bin/sh -x

# Usage: Run ./buildWinSuite.sh from the Suite directory in packaging.


# Set control variable to build packages if they are not build already
# This will probably be removed later as it was only added for testing
BUILD_IF_UNBUILT=1

# Set up path variables
cd ../..
TOP_LEVEL=`pwd`
DIST_ROOT=$TOP_LEVEL/cad/src/dist
DIST_CONTENTS=$DIST_ROOT

# Set up version information
VERSION_NUM="1.1.1.2"
RC_NUMBER="0"
GROMACS_VERSION="3.3.3"
QUTEMOLX_VERSION="0.5.1"

# Do a basic check for sanity in the build area.
if [ ! -e "$TOP_LEVEL/cad/src" ]
then
  echo "The build directories are not valid"
  exit 1
fi

# Check to see if the smaller packages are built

# Start with Pref_Mod since it's easy to build
cd $TOP_LEVEL
# this check is to see if we've already run Pref_Mod for this tree
if [ ! -e "$TOP_LEVEL/packaging/Pref_Mod/dist" ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
#   All clear to do the build
    cd packaging/Pref_Mod
    ./buildWin.sh || exit 1
  else
    echo "Build Pref_Mod before continuing"
    exit 1
  fi
fi


# Build section for QuteMolX

if [ ! -e "/c/QMX_Install" ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
    cd $TOP_LEVEL/cad/plugins/QuteMol/packaging
    ./buildWin.sh QUTEMOLX_VERSION
    if [ "$?" != "0" ]
    then
      echo "Error in the QuteMolX build, investigate."
      exit 1
    fi
  fi
fi
# The build will normally handle this, but if the files used are pre-builds,
# the build does not store the readme and license.  (Needed for Suite)
cp $TOP_LEVEL/cad/plugins/QuteMol/packaging/Win32/License.txt /c/QMX_Install || exit 1
cp $TOP_LEVEL/cad/plugins/QuteMol/packaging/ReadMe.html /c/QMX_Install || exit 1

# End of build section for QuteMolX

cd $TOP_LEVEL

# Build section for GROMACS

if [ ! -e "/c/GMX_Install" ]
then
  if [ $BUILD_IF_UNBUILT -ne 0 ]
  then
    cd $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging
    ./buildWin.sh $GROMACS_VERSION
    if [ "$?" != "0" ]
    then
      echo "Error in the GROMACS build, investigate."
      exit 1
    fi
  fi
fi
# The build will normally handle this, but if the files used are pre-builds,
# the build does not store the readme and license.  (Needed for Suite)
cp $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging/Win32/License.txt /c/GMX_Install
cp $TOP_LEVEL/cad/plugins/GROMACS/gromacs-$GROMACS_VERSION/packaging/ReadMe.html /c/GMX_Install

# End of GROMACS build section

cd $TOP_LEVEL

# Build section for NE1

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
    ./buildWin.sh
    if [ "$?" != "0" ]
    then
      echo "Error in the NE1 Build, investigate"
      exit 1
    fi
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


# Clean up time
rm -f /c/GMX_Install/License.txt /c/GMX_Install/ReadMe.html
rm -f /c/QMX_Install/License.txt /c/QMX_Install/ReadMe.html
