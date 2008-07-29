#!/bin/sh -x
# This build depends on pre-requisite files that are stored in ~/QMX_support.
# These files are also backed up on the nanoengineer-1.com server

QUTEMOLX_VERSION="0.5.1"

cd ..
TOP_LEVEL=`pwd`
if [ ! -e "qutemol/src/osx-build" ]
then
  echo "Improper build environment"
  exit 1
fi
if [ -e "qutemol/src/osx-build/local" ]
then
  cd qutemol/src/osx-build
  make clean
  cd $TOP_LEVEL
  cd qutemol
  rm -rf glew
  cd src
  rm -rf wrap
  rm -rf vcg
fi
cd $TOP_LEVEL/packaging/MacOSX
rm -rf install
mkdir $TOP_LEVEL/packaging/MacOSX/install
cd $TOP_LEVEL
cp -R qutemol $TOP_LEVEL/packaging/MacOSX/install
cd  $TOP_LEVEL/packaging/MacOSX/install/qutemol
find . -depth -type d -name ".svn" -print -exec rm -rf {} \;
cd ..
tar -czf QuteMolX.tar.gz qutemol
rm -rf qutemol
cd $TOP_LEVEL/qutemol

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

cd $TOP_LEVEL/qutemol/src/osx-build
cp -R QuteMolX.app $TOP_LEVEL/packaging/MacOSX/install
cd $TOP_LEVEL
cp packaging/MacOSX/License.txt packaging/MacOSX/install

# Next step is to build the package
