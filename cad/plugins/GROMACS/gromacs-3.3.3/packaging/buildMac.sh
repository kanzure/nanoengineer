#!/bin/sh -x

# this build requires for there to be a copy of the gromacs source stored in
# ~/build_prereqs.  At current, it's stock gromacs source for the Mac with
# no modifications.  So, there's no point in storing it in the svn tree
# Also, this script has plenty of room for code cleanup as it now does the 
# job of 2 previous scripts and other manual work.  It's been put together with
# only minimal attention paid to streamlining the process

# accept command line argument for version number
if [ "$1" = "" ]
then
  GMX_VERSION="3.3.3"
else
  GMX_VERSION="$1"
fi

DIST_NAME="GROMACS_$GMX_VERSION"

# set up a directory to store pre-built stuff
if [ ! -e ~/MacOSX_Installers ]
then
  mkdir ~/MacOSX_Installers
fi

# See if the build tree is likely to make sense
pwd | grep "gromacs-$GMX_VERSION"
if [ "$?" != 0 -o ! -e MacOSX ]
then
  echo "incorrect build tree design"
  exit 1
fi

cd .. || exit 1
TOP_LEVEL=`pwd`
# Get rid of directoried from a previous build
sudo rm -rf install packaging/build src
# create the compile directory
mkdir src || exit 1
# create the directory to install into
mkdir install || exit 1
cd src || exit 1
# These are the two scripts that have now been included into this main script
#cp $TOP_LEVEL/packaging/MacOSX/dist_gromacs.sh . || exit 1
#cp $TOP_LEVEL/packaging/MacOSX/stitch_gromacs.sh . || exit 1

# Set up the build directories for the two archs
tar -xzvf ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz || exit 1
mv gromacs-$GMX_VERSION gromacs-$GMX_VERSION-ppc || exit 1
tar -xzvf ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz || exit 1
mv gromacs-$GMX_VERSION gromacs-$GMX_VERSION-i386 || exit 1

# Compile the ppc version

# Set up the environment variables
cd gromacs-$GMX_VERSION-ppc || exit 1
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export CFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export LDFLAGS="-arch ppc -Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib"
export CXXFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export FFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export MACOSX_DEPLOYMENT_TARGET=10.3

# Run configure for a double precision gromacs (ppc)
./configure --prefix=$TOP_LEVEL/install --disable-ia32-3dnow --disable-ia32-sse --x-includes=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include --x-libraries=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib --enable-double --program-suffix= || exit 1

# Start the actual compile (ppc)
sudo -v
make clean || exit 1

make || exit 1
sudo -v

cd .. || exit 1
sudo -v

# Compile the i386 version

# Set up the environment variables
cd gromacs-$GMX_VERSION-i386 || exit 1
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export CFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export LDFLAGS="-arch i386 -Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib"
export CXXFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export FFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export MACOSX_DEPLOYMENT_TARGET=10.3

# Run configure for a double precision gromacs (i386)
./configure --prefix=$TOP_LEVEL/install --disable-ia32-3dnow --disable-ia32-sse --x-includes=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include --x-libraries=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib --enable-double --program-suffix= || exit 1

# Start the actual compile (i386)
sudo -v
make clean || exit 1

make || exit 1
sudo -v
make install || exit 1
sudo -v

# Stitch gromacs together
cd $TOP_LEVEL/src || exit 1
# remove the joined directory if it exists
sudo rm -rf gromacs-$GMX_VERSION-joined
mkdir gromacs-$GMX_VERSION-joined || exit 1
# change into a compiled directory to work from
cd gromacs-$GMX_VERSION-i386 || exit 1
# recreate the compiled directory structure in joined
find . -type d -exec mkdir ../gromacs-$GMX_VERSION-joined/{} \; || exit 1
# copy all bibrary files and rename them with the -i386 extension
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{}-i386 \; || exit 1
# make a non-renamed copy to work from later
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{} \; || exit 1
sudo -v
# find all other files that have a Mach-O listing when doing file
# We want only binary files at this time
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk || exit 1
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-$GMX_VERSION-joined/$name-i386 || exit 1
      cp $name ../gromacs-$GMX_VERSION-joined/$name || exit 1
    fi
  fi
done
sudo -v
# do essentially the same thing for the ppc version
cd ../gromacs-$GMX_VERSION-ppc || exit 1
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{}-ppc \; || exit 1
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk || exit 1
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-$GMX_VERSION-joined/$name-ppc || exit 1
    fi
  fi
done
sudo -v
cd ../gromacs-$GMX_VERSION-joined || exit 1
echo "Starting joining process"

# Erase the non-type specific file and replace it with one sewn together with
# lipo.  Then remove the type specific versions leaving only a universal of
# the original file
for name in `find . -type f ! -name "*-i386" ! -name "*-ppc" -print`
do
  rm $name || exit 1
  lipo -create $name-i386 $name-ppc -output $name || exit 1
  rm $name-i386 $name-ppc || exit 1
done
sudo -v
# Make a directory to hold a universal version of the whole tree
mkdir ../gromacs-$GMX_VERSION-univ || exit 1
# Populate the universal version of the tree with a tree structure that looks
# like one of the ones we compiled with
cd gromacs-$GMX_VERSION-i386 || exit 1
find . -print | cpio -pudvm ../gromacs-$GMX_VERSION-univ || exit 1
# Now replace all binary versions with the universal versions
cd ../gromacs-$GMX_VERSION-joined || exit 1
find . -type f -print -exec cp {} ../gromacs-$GMX_VERSION-univ/{} \; || exit 1
cd $TOP_LEVEL/src || exit 1
sudo -v

# build distribution area for gromacs

# use another TOPLEVEL for this area since it was imported from another script
# originally.  This should maybe be changed later.
TOPLEVEL=`pwd`
echo "Top Level is $TOPLEVEL"
# recreate distribution directories
rm -rf dist dist2
mkdir dist || exit 1
mkdir dist2 || exit 1
# re-create the directory structure again for distribution.
cd $TOPLEVEL/gromacs-$GMX_VERSION-joined || exit 1
find . -type d -exec mkdir $TOPLEVEL/dist2/{} \; || exit 1
find . -name "*.a" -exec cp {} $TOPLEVEL/dist2/{} \; || exit 1
sudo -v
# Grab the binary files and put them into the temporary dist directory
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk || exit 1
    if [ "$?" == "0" ]
    then
      cp $name $TOPLEVEL/dist2/$name || exit 1
    fi
  fi
done
sudo -v
cd $TOPLEVEL/dist2 || exit 1
echo "Pruning .svn directories"
find . -name ".svn" -depth -print -exec rm -rf {} \; || exit 1
# removing empty directories if the directory is full, it will error, 
# so don't use exit 1
find . -depth -type d -exec rmdir {} \;
sudo -v
# create a final bin directory for the new temporary tree
mkdir bin || exit 1
# create the contents of the bin directory from the contents of the others
for direct in `ls`
do
  cd $direct || exit 1
  echo "Inspecting $direct"
  for name in `find . -type f`
  do
    if [ -x "$name" ]
    then
      cp $name $TOPLEVEL/dist2/bin || exit 1
    fi
  done
  cd ..
done
sudo -v

#set up the rest of the distribution directory to look like what we want in the 
# final package.
cd $TOPLEVEL/dist2 || exit 1

# grab all the includes
mkdir include || exit 1
cp -r $TOP_LEVEL/install/include/gromacs/* include || exit 1
# get all the libraries
mkdir lib || exit 1
find . -name "*.a" -exec cp {}  $TOPLEVEL/dist2/lib \; || exit 1
find . -name "*.dylib" -exec cp {} $TOPLEVEL/dist2/lib \; || exit 1
# Create the share directories that have examples, docs, etc.
mkdir share || exit 1
cp -r $TOP_LEVEL/install/share/gromacs/* share || exit 1
# This next section is for the hdf5 implementations which may be put back later
cd $TOP_LEVEL/install/lib || exit 1
#tar -cvzf $TOPLEVEL/dist2/lib/HDF5.tar.gz libHDF5_SimResults.*
#tar -cvzf $TOPLEVEL/dist2/lib/hdf5.tar.gz libhdf5.*
cd $TOPLEVEL/dist2/lib || exit 1
#tar -xzf HDF5.tar.gz
#tar -xzf hdf5.tar.gz
#rm HDF5.tar.gz
#rm hdf5.tar.gz
sudo -v
cd $TOPLEVEL/dist2/bin || exit 1
cd $TOPLEVEL/dist2 || exit 1
# grab a copy of the source code for packaging
cp ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz . || exit 1
# move the contents of the temporary tree into the final one
mv bin $TOPLEVEL/dist/bin || exit 1
mv lib $TOPLEVEL/dist/lib || exit 1
mv share $TOPLEVEL/dist/share || exit 1
mv include $TOPLEVEL/dist/include || exit 1
mv gromacs-$GMX_VERSION.tar.gz $TOPLEVEL/dist || exit 1
cd $TOPLEVEL || exit 1
sudo -v
# remove the temporary tree
rm -rf $TOPLEVEL/dist2

# final setup before the packaging
mkdir $TOP_LEVEL/packaging/build || exit 1
mkdir $TOP_LEVEL/packaging/build/GROMACS || exit 1
# copy everything from inside the dist into the pkg build area
cd $TOP_LEVEL/src/dist || exit 1
cp -R * $TOP_LEVEL/packaging/build/GROMACS || exit 1
sudo -v
# put the mcpp into the final package area
cd $TOP_LEVEL/packaging/build/GROMACS || exit 1
mkdir mcpp || exit 1
cd mcpp || exit 1
sudo -v
tar -xzvf ~/build_prereqs/mcpp.tar.gz || exit 1
sudo -v

# Make all permissions be root:admin for final packaging
cd $TOP_LEVEL/packaging
sudo find build/GROMACS -exec chown root:admin {} \; || exit 1

#Next step is to build the package and the dmg
rm -rf rec
# create the resources directory
mkdir build/rec || exit 1
cp MacOSX/background.jpg build/rec || exit 1
cp MacOSX/License.txt build/rec || exit 1

# Run the package maker program
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o $TOP_LEVEL/packaging/build/GROMACS_$GMX_VERSION.pkg -r ./build/GROMACS -v -e $TOP_LEVEL/packaging/build/rec -f MacOSX/GMX-info.plist || exit 1
# swap things around so the installer says GROMACS for the dmg file and insaller
sudo mv build/GROMACS build/$DIST_NAME || exit 1
sudo mkdir build/GROMACS || exit 1
sudo mv build/$DIST_NAME.pkg build/GROMACS || exit 1

# Build the dmg file
sleep 10
# code to get around a strange race condition where hdiutil doesn't see the
# the srcfolder if it's not completely sync'd up.
sudo sync
sleep 10

# Try building the final dmg file
sudo hdiutil create -srcfolder $TOP_LEVEL/packaging/build/GROMACS -fs HFS+ -format UDZO $TOP_LEVEL/packaging/build/${DIST_NAME}.dmg || exit 1

# make a copy of all this stuff so the suite builder can use it later.
if [ ! -e ~/MacOSX_Installers/$DIST_NAME.pkg ]
then
  sudo cp -R $TOP_LEVEL/packaging/build/GROMACS/$DIST_NAME.pkg ~/MacOSX_Installers
  cp $TOP_LEVEL/packaging/build/$DIST_NAME.dmg ~/MacOSX_Installers
fi

