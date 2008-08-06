#!/bin/sh -x
# This build depends on pre-requisite files that are stored in ~/build_prereqs.
# These files are also backed up on the nanoengineer-1.com server

# Set version information
if [ "$1" = "" ]
then
  QUTEMOLX_VERSION="0.5.1"
else
  QUTEMOLX_VERSION="$1"
fi
DIST_NAME="QuteMolX_$QUTEMOLX_VERSION"

# Figure out where the root of the tree is
cd .. || exit 1
TOP_LEVEL=`pwd`

if [ ! -e qutemol/src/osx-build ]
then
  echo "Improper build environment"
  exit 1
fi

# set up a directory to store pre-built stuff
if [ ! -e ~/MacOSX_Installers ]
then
  mkdir ~/MacOSX_Installers
fi

# if it looks like there was already a build in this tree, clean it out
if [ -e qutemol/src/osx-build/local ]
then
  cd qutemol/src/osx-build
  sudo make clean
  cd $TOP_LEVEL
  cd qutemol
  rm -rf glew
  cd src
  rm -rf wrap
  rm -rf vcg
fi
DATECODE=`date "+%B %d, %Y"`
cd $TOP_LEVEL/packaging/MacOSX || exit 1
# remove any oyher previously built versions
sudo rm -rf install build

# create directories to store the new build
mkdir $TOP_LEVEL/packaging/MacOSX/install || exit 1
mkdir $TOP_LEVEL/packaging/MacOSX/install/$DIST_NAME || exit 1
cd $TOP_LEVEL || exit 1

# Modify the Welcome screen information
cat packaging/MacOSX/Welcome_template.rtf | sed -e "s:VERSION_GOES_HERE:$QUTEMOLX_VERSION:g" | sed -e "s:DATE_GOES_HERE:$DATECODE:g" > packaging/MacOSX/Welcome.rtf

# create the tarball of the source tree
cp -R qutemol $TOP_LEVEL/packaging/MacOSX/install || exit 1
cd  $TOP_LEVEL/packaging/MacOSX/install/qutemol || exit 1
find . -depth -type d -name ".svn" -print -exec rm -rf {} \;
cd .. || exit 1
tar -czf $DIST_NAME/QuteMolX.tar.gz qutemol || exit 1
rm -rf qutemol
cd $TOP_LEVEL/qutemol || exit 1

# extract the libraries needed to do the build
tar -xzf ~/build_prereqs/glew.tar.gz || exit 1
cd src || exit 1
tar -xzf ~/build_prereqs/wrap.tar.gz || exit 1
tar -xzf ~/build_prereqs/vcg.tar.gz || exit 1

# change the version information compiled into QuteMolX
cat MyTab.cpp | sed -e "s:Version [0-9]*\.[0-9]*\.[0-9]*:Version $QUTEMOLX_VERSION:" > MyTab.cpp.btmp
mv -f MyTab.cpp.btmp MyTab.cpp || exit 1

# Do the actual build
cd osx-build || exit 1
mkdir local
cp $TOP_LEVEL/packaging/MacOSX/Makefile . || exit 1
sudo make clean
sudo rm -rf QuteMolX.app
make || exit 1

# create the directory structure needed for the build
cd $TOP_LEVEL/qutemol/src/osx-build || exit 1
cp -R QuteMolX.app $TOP_LEVEL/packaging/MacOSX/install/$DIST_NAME || exit 1
cd $TOP_LEVEL/packaging/MacOSX || exit 1
cp License.txt install/$DIST_NAME || exit 1
sudo find install -exec chown root:admin {} \;

# Next step is to build the package
mkdir -p build/QuteMolX || exit 1
cat QMX-info.plist | sed -e "s:/Applications/Nanorex/QuteMolX:/Applications/Nanorex/QuteMolX $QUTEMOLX_VERSION:" > QMX-info.plist.tmp
# The previous replace is done this way so that if you run the package builder
# separately, you will still get something that will still make a viable
# package.
mv QMX-info.plist.tmp QMX-info.plist || exit 1
sudo rm -rf rec
mkdir rec
cp background.jpg rec
cp Welcome.rtf rec
cp License.txt rec
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o $TOP_LEVEL/packaging/MacOSX/build/QuteMolX/QuteMolX_$QUTEMOLX_VERSION.pkg -r ./install/QuteMolX_0.5.1 -t "QuteMolX $QUTEMOLX_VERSION" -v -e $TOP_LEVEL/packaging/MacOSX/rec -f QMX-info.plist || exit 1

# Build the dmg file
sleep 10
sudo sync
sleep 10
sudo hdiutil create -srcfolder $TOP_LEVEL/packaging/MacOSX/build/QuteMolX -fs HFS+ -format UDZO $TOP_LEVEL/packaging/MacOSX/build/${DIST_NAME}.dmg || exit 1

if [ ! -e ~/MacOSX_Installers/$DIST_NAME.pkg ]
then
  sudo cp -R $TOP_LEVEL/packaging/MacOSX/build/QuteMolX/$DIST_NAME.pkg ~/MacOSX_Installers
  cp $TOP_LEVEL/packaging/MacOSX/build/$DIST_NAME.dmg ~/MacOSX_Installers
fi
