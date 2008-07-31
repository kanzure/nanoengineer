#!/bin/sh
# This should be run from the packaging directory

# Set up some necessary variables
GMX_VERSION="3.3.3"
QMX_VERSION="0.5.1"
NE1_VERSION="1.1.1"
TAR_DIR="/tmp/dist_tars"
FORCE_REMOVE=0
cd .. || exit 1
TOP_LEVEL=`pwd`

# See if we are being run from somwhere that makes sense
if [ ! -e cad/src -o ! -e packaging ]
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

# Create the Suite tar file
echo "Creating $TAR_DIR/NanoEngineer-1_Suite_v$NE1_VERSION.tar.gz"
tar -cz --exclude "*packaging/*" --exclude "*packaging" --exclude "*/\.svn/*" --exclude "*\.svn" -f /tmp/dist_tars/NanoEngineer-1_Suite_v1.1.1.tar.gz * || exit 1

# Create the NE1 tar file
echo "Creating $TAR_DIR/NanoEngineer-1_v$NE1_VERSION.tar.gz"
tar -cz --exclude "*packaging/*" --exclude "*packaging" --exclude "*/\.svn/*" --exclude "*\.svn" -X packaging/Win32/exclude_files.txt -f /tmp/dist_tars/NanoEngineer-1_v1.1.1.tar.gz * || exit 1

# Create the GROMACS tar file
echo "Creating GROMACS_$GMX_VERSION.tar.gz"
echo "GROMACS is a stock $GMX_VERSION - skipping" || exit 1

# Create the QuteMolX tar file
echo "Creating $TAR_DIR/QuteMolX_$QMX_VERSION.tar.gz"
cd $TOP_LEVEL/cad/plugins/QuteMol || exit 1
tar -cz --exclude "*packaging/*" --exclude "*packaging" --exclude "*/\.svn/*" --exclude "*\.svn" -f $TAR_DIR/QuteMolX_$QMX_VERSION.tar.gz qutemol || exit 1

# Create the HDF5_SimResults tar file
echo "Creating $TAR_DIR/HDF5_SimResults_0.1.0.tar.gz"
cd $TOP_LEVEL/cad/plugins || exit 1
tar -cz --exclude "*packaging/*" --exclude "*packaging" --exclude "*/\.svn/*" --exclude "*\.svn" -f $TAR_DIR/HDF5_SimResults_0.1.0.tar.gz HDF5_SimResults || exit 1
