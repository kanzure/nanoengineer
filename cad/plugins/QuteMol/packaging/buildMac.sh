#!/bin/sh -x
# This build depends on pre-requisite files that are stored in ~/QMX_support.
# These files are also backed up on the nanoengineer-1.com server

QUTEMOLX_VERSION="0.5.1"

cd ..
TOP_LEVEL=`pwd`
if [ ! -e "qutemol/src/osx-build" ]
  echo "Improper build environment"
  exit 1
fi
cd qutemol
tar -xzf ~/QMX_support/glew.tar.gz
cd src
tar -xzf ~/QMX_support/wrap.tar.gz
tar -xzf ~/QMX_support/vcg.tar.gz
cat MyTab.cpp | sed -e "s:Version [0-9]*\.[0-9]*\.[0-9]*:Version $QUTEMOLX_VERSION:" > MyTab.cpp.btmp
mv MyTab.cpp.btmp MyTab.cpp
cd osx-build
mkdir local
cp $TOP_LEVEL/packaging/MacOSX/Makefile .
make clean
make

 Next step is to build the package
