#!/bin/sh -x
# WARNING: once you run this command, this trunk is completely useless for
# doing anything with subversion tree or any other builds.
# You have been warned!!!

# Set up some necessary variables
GMX_VERSION="3.3.3"
QMX_VERSION="0.5.1"
NE1_VERSION="1.1.1"
TAR_DIR="/tmp/dist_tars"
FORCE_REMOVE=0
cd ..
TOP_LEVEL=`pwd`

# See if we are being run from somwhere that makes sense
if [ ! -e cad/src ]
then
  echo "Error in directory structure"
  exit 1
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
cp packaging/buildTars.sh .
cp packaging/buildTars.sh ~
cp packaging/Win32/exclude_files.txt .

# Remove the .svn and packaging directories
find . -name ".svn" -depth -type d -exec rm -rf {} \;
find . -name "packaging" -depth -type d -exec rm -rf {} \;

# Create the Suite tar file
tar -czf $TAR_DIR/NanoEngineer-1_Suite_v$NE1_VERSION.tar.gz *

# Create the NE1 tar file
tar -cz -X exclude_files.txt -f $TAR_DIR/NanoEngineer-1_v$NE1_VERSION.tar.gz *

# Create the GROMACS tar file
echo "GROMACS is a stock $GMX_VERSION - skipping"

# Create the QuteMolX tar file
cd $TOP_LEVEL/cad/plugins/QuteMol
tar -czf $TAR_DIR/QuteMolX_$QMX_VERSION.tar.gz qutemol

# Create the HDF5_SimResults tar file
cd $TOP_LEVEL/cad/plugins
tar -czf $TAR_DIR/HDF5_SimResults_0.1.0.tar.gz HDF5_SimResults
