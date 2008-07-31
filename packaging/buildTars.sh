#!/bin/sh
# WARNING: once you run this command, this trunk is completely useless for
# doing anything with subversion tree or any other builds.  Also, it doesn't 
# need root privilages, so do not run as root.
# You have been warned!!!

# Set up some necessary variables
GMX_VERSION="3.3.3"
QMX_VERSION="0.5.1"
NE1_VERSION="1.1.1"
TAR_DIR="/tmp/dist_tars"
FORCE_REMOVE=0
FORCE_CONTINUE=0
cd .. || exit 1
TOP_LEVEL=`pwd`

# See if we are being run from somwhere that makes sense
if [ ! -e cad/src ]
then
  echo "Error in directory structure"
  exit 1
fi

# This is a one last chance to not delete stuff.  So, don't remove this.
# The it can be bypassed, but that should only be done by a tested automated
# script used for building.
if [ $FORCE_CONTINUE -ne 1 ]
then
  ans="n"
  echo "This will completely remove all .svn and packaging directories from this source tree.  Are you absolutely positive you want to do that? (y/N)"
  read ans
  if [ "$ans" != "y" -a "$ans" != "Y" ]
  then
    exit 1
  fi
fi

# Check to figure out if the tars directory exists and what to do about it.
if [ -e $TAR_DIR ]
then
  answer="n"
  if [ $FORCE_REMOVE -eq 0 ]
  then
    echo "Remove the old tars directory: $TAR_DIR? (y/N)"
    read answer
  fi
  if [ $FORCE_REMOVE -ne 0 -o "$answer" = "y" -o "$answer" = "Y" ]
  then
    rm -rf $TAR_DIR
  else
    echo "Remove the old tars directory manually please."
    exit 1
  fi
fi

# Create the output directory for the tar files
mkdir $TAR_DIR

# about do delete the packaging and svn directories, copy what might be needed
cp packaging/buildTars.sh . || exit 1
cp packaging/buildTars.sh ~ || exit 1
cp packaging/Win32/exclude_files.txt . || exit 1

# Remove the .svn and packaging directories
echo "Running: find . -name ".svn" -depth -type d -exec rm -rf {} \;"
find . -name ".svn" -depth -type d -exec rm -rf {} \;
echo "Running: find . -name "packaging" -depth -type d -exec rm -rf {} \;"
find . -name "packaging" -depth -type d -exec rm -rf {} \;

# Create the Suite tar file
echo "Creating $TAR_DIR/NanoEngineer-1_Suite_v$NE1_VERSION.tar.gz"
tar -czf $TAR_DIR/NanoEngineer-1_Suite_v$NE1_VERSION.tar.gz * || exit 1

# Create the NE1 tar file
echo "Creating $TAR_DIR/NanoEngineer-1_v$NE1_VERSION.tar.gz"
tar -cz -X exclude_files.txt -f $TAR_DIR/NanoEngineer-1_v$NE1_VERSION.tar.gz * || exit 1

# Create the GROMACS tar file
echo "Creating GROMACS_$GMX_VERSION.tar.gz"
echo "GROMACS is a stock $GMX_VERSION - skipping" || exit 1

# Create the QuteMolX tar file
echo "Creating $TAR_DIR/QuteMolX_$QMX_VERSION.tar.gz"
cd $TOP_LEVEL/cad/plugins/QuteMol || exit 1
tar -czf $TAR_DIR/QuteMolX_$QMX_VERSION.tar.gz qutemol || exit 1

# Create the HDF5_SimResults tar file
echo "Creating _DIR/HDF5_SimResults_0.1.0.tar.gz"
cd $TOP_LEVEL/cad/plugins || exit 1
tar -czf $TAR_DIR/HDF5_SimResults_0.1.0.tar.gz HDF5_SimResults || exit 1
