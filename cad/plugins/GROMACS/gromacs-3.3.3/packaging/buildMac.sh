#!/bin/sh -x

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

cd ..
TOP_LEVEL=`pwd`
sudo rm -rf install packaging/build src
mkdir src
mkdir install
cd src
cp $TOP_LEVEL/packaging/MacOSX/dist_gromacs.sh .
cp $TOP_LEVEL/packaging/MacOSX/stitch_gromacs.sh .

tar -xzvf ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz || exit 1
mv gromacs-$GMX_VERSION gromacs-$GMX_VERSION-ppc || exit 1

cd gromacs-$GMX_VERSION-ppc || exit 1
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export CFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export LDFLAGS="-arch ppc -Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib"
export CXXFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export FFLAGS="-arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export MACOSX_DEPLOYMENT_TARGET=10.3

./configure --prefix=$TOP_LEVEL/install --disable-ia32-3dnow --disable-ia32-sse --x-includes=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include --x-libraries=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib --enable-double --program-suffix= || exit 1
sudo -v
make clean || exit 1

make || exit 1
sudo -v

cd .. || exit 1
tar -xzvf ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz || exit 1
mv gromacs-$GMX_VERSION gromacs-$GMX_VERSION-i386 || exit 1
sudo -v

cd gromacs-$GMX_VERSION-i386 || exit 1
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export CFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export LDFLAGS="-arch i386 -Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib"
export CXXFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export FFLAGS="-arch i386 -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export MACOSX_DEPLOYMENT_TARGET=10.3

./configure --prefix=$TOP_LEVEL/install --disable-ia32-3dnow --disable-ia32-sse --x-includes=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include --x-libraries=/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib --enable-double --program-suffix= || exit 1
sudo -v
make clean || exit 1

make || exit 1
sudo -v
make install || exit 1
sudo -v

# Stitch gromacs together
cd $TOP_LEVEL/src || exit 1
rm -rf gromacs-$GMX_VERSION-joined
mkdir gromacs-$GMX_VERSION-joined
cd gromacs-$GMX_VERSION-i386
find . -type d -exec mkdir ../gromacs-$GMX_VERSION-joined/{} \;
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{}-i386 \;
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{} \;
sudo -v
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-$GMX_VERSION-joined/$name-i386
      cp $name ../gromacs-$GMX_VERSION-joined/$name
    fi
  fi
done
sudo -v
cd ../gromacs-$GMX_VERSION-ppc
find . -name "*.a" -exec cp {} ../gromacs-$GMX_VERSION-joined/{}-ppc \;
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-$GMX_VERSION-joined/$name-ppc
    fi
  fi
done
sudo -v
cd ../gromacs-$GMX_VERSION-joined
echo "Starting joining process"
for name in `find . -type f ! -name "*-i386" ! -name "*-ppc" -print`
do
  rm $name
  echo $name
  lipo -create $name-i386 $name-ppc -output $name
  rm $name-i386 $name-ppc
done
sudo -v
mkdir ../gromacs-$GMX_VERSION-univ
cd gromacs-$GMX_VERSION-i386
find . -print | cpio -pudvm ../gromacs-$GMX_VERSION-univ
cd ../gromacs-$GMX_VERSION-joined
find . -type f -print -exec cp {} ../gromacs-$GMX_VERSION-univ/{} \;
cd $TOP_LEVEL/src
sudo -v

# build distribution area for gromacs

TOPLEVEL=`pwd`
echo "Top Level is $TOPLEVEL"
rm -rf dist
rm -rf dist2
mkdir dist
mkdir dist2
cd $TOPLEVEL/gromacs-$GMX_VERSION-joined || exit 1
find . -type d -exec mkdir $TOPLEVEL/dist2/{} \;
find . -name "*.a" -exec cp {} $TOPLEVEL/dist2/{} \;
sudo -v
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk
    if [ "$?" == "0" ]
    then
      cp $name $TOPLEVEL/dist2/$name
    fi
  fi
done
sudo -v
cd $TOPLEVEL/dist2
echo "Pruning .svn directories"
find . -name ".svn" -depth -print -exec rm -rf {} \;
find . -depth -type d -exec rmdir {} \;
sudo -v
mkdir bin
for direct in `ls`
do
  cd $direct
  echo "Inspecting $direct"
  for name in `find . -type f`
  do
    if [ -x "$name" ]
    then
      echo "copying $name to $TOPLEVEL/dist2/bin"
      cp $name $TOPLEVEL/dist2/bin
    fi
  done
  cd ..
done
sudo -v
cd $TOPLEVEL/dist2
mkdir include
cp -r $TOP_LEVEL/install/include/gromacs/* include
mkdir lib
find . -name "*.a" -exec cp {}  $TOPLEVEL/dist2/lib \;
find . -name "*.dylib" -exec cp {} $TOPLEVEL/dist2/lib \;
mkdir share
cp -r $TOP_LEVEL/install/share/gromacs/* share
cd $TOP_LEVEL/install/lib
#tar -cvzf $TOPLEVEL/dist2/lib/HDF5.tar.gz libHDF5_SimResults.*
#tar -cvzf $TOPLEVEL/dist2/lib/hdf5.tar.gz libhdf5.*
cd $TOPLEVEL/dist2/lib
#tar -xzf HDF5.tar.gz
#tar -xzf hdf5.tar.gz
#rm HDF5.tar.gz
#rm hdf5.tar.gz
sudo -v
cd $TOPLEVEL/dist2/bin
cd $TOPLEVEL/dist2
cp ~/build_prereqs/gromacs-$GMX_VERSION.tar.gz .
mv bin $TOPLEVEL/dist/bin
mv lib $TOPLEVEL/dist/lib
mv share $TOPLEVEL/dist/share
mv include $TOPLEVEL/dist/include
mv gromacs-$GMX_VERSION.tar.gz $TOPLEVEL/dist
cd $TOPLEVEL
sudo -v
rm -rf $TOPLEVEL/dist2

mkdir $TOP_LEVEL/packaging/build
mkdir $TOP_LEVEL/packaging/build/GROMACS
cd $TOP_LEVEL/src/dist
cp -R * $TOP_LEVEL/packaging/build/GROMACS
sudo -v
cd $TOP_LEVEL/packaging/build/GROMACS
mkdir mcpp
cd mcpp
tar -xzvf ~/build_prereqs/mcpp.tar.gz
sudo touch /tmp/junk_alive.txt
cd $TOP_LEVEL/packaging
sudo find build/GROMACS -exec chown root:admin {} \;

#Next step is to build the package and the dmg
rm -rf rec
mkdir build/rec
cp MacOSX/background.jpg build/rec
cp MacOSX/License.txt build/rec

sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o $TOP_LEVEL/packaging/build/GROMACS_$GMX_VERSION.pkg -r ./build/GROMACS -v -e $TOP_LEVEL/packaging/build/rec -f MacOSX/GMX-info.plist || exit 1
sudo mv build/GROMACS build/$DIST_NAME
sudo mkdir build/GROMACS
sudo mv build/$DIST_NAME.pkg build/GROMACS

# Build the dmg file
sudo sync
sudo hdiutil create -srcfolder $TOP_LEVEL/packaging/build/GROMACS -fs HFS+ -format UDZO $TOP_LEVEL/packaging/build/${DIST_NAME}.dmg || exit 1

if [ ! -e ~/MacOSX_Installers/$DIST_NAME.pkg ]
then
  sudo cp -R $TOP_LEVEL/packaging/build/GROMACS/$DIST_NAME.pkg ~/MacOSX_Installers
  cp $TOP_LEVEL/packaging/build/$DIST_NAME.dmg ~/MacOSX_Installers
fi

