#!/bin/sh
TOPLEVEL=`pwd`
echo "Top Level is $TOPLEVEL"
rm -rf dist
rm -rf dist2
mkdir dist
mkdir dist2
cd $TOPLEVEL/gromacs-3.3.2-joined || exit 1
find . -type d -exec mkdir $TOPLEVEL/dist2/{} \;
find . -name "*.a" -exec cp {} $TOPLEVEL/dist2/{} \;
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
cd $TOPLEVEL/dist2
echo "Pruning .svn directories"
find . -name ".svn" -depth -print -exec rm -rf {} \;
find . -depth -type d -exec rmdir {} \;
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
cd $TOPLEVEL/dist2
mkdir include
cp -r /usr/local/include/gromacs/* include
mkdir lib
find . -name "*.a" -exec cp {}  $TOPLEVEL/dist2/lib \;
find . -name "*.dylib" -exec cp {} $TOPLEVEL/dist2/lib \;
mkdir share
cp -r /usr/local/share/gromacs/* share
cd /usr/local/lib
tar -cvzf $TOPLEVEL/dist2/lib/HDF5.tar.gz libHDF5_SimResults.*
tar -cvzf $TOPLEVEL/dist2/lib/hdf5.tar.gz libhdf5.*
cd $TOPLEVEL/dist2/lib
tar -xzf HDF5.tar.gz
tar -xzf hdf5.tar.gz
rm HDF5.tar.gz
rm hdf5.tar.gz
cd $TOPLEVEL/dist2/bin
#for name in `ls`
#do
#  otool -L $name | grep HDF5 > /tmp/gmx_install_junk
#  if [ "$?" == "0" ]
#  then
#    install_name_tool -change /usr/local/lib/libHDF5_SimResults.1.dylib @executable_path/../lib/libHDF5_SimResults.1.dylib $name
#  fi
#  otool -L $name | grep hdf5 > /tmp/gmx_install_junk
#  if [ "$?" == "0" ]
#  then
#    install_name_tool -change /usr/local/lib/libhdf5.0.dylib @executable_path/../lib/libhdf5.0.dylib $name
#  fi
#done
cd $TOPLEVEL/dist2
cp $TOPLEVEL/gromacs-3.3.2.tar.gz .
mv bin $TOPLEVEL/dist/bin
mv lib $TOPLEVEL/dist/lib
mv share $TOPLEVEL/dist/share
mv include $TOPLEVEL/dist/include
mv gromacs-3.3.2.tar.gz $TOPLEVEL/dist
cd $TOPLEVEL
rm -rf $TOPLEVEL/dist2

