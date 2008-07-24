#!/bin/sh -x

# Usage: Run ./buildWin.sh from the packaging directory.

# This build requires the existance of a QuteMolX-prereqs.tar.gz which must
# reside in c:\build_prereqs.  The contents of the file are source directories
# for vcg and glew, plus a libpng-3.dll file that is also needed for build.
cd ..
TOP_LEVEL=`pwd`

rm -rf $TOP_LEVEL/packaging/Win32/install

if [ ! -e "/c/QMX_Install" ]
then
# Make a tarball of the uncompiled source for later.
  tar -cz -X ../../../packaging/Win32/exclude_files.txt -f /c/QMX_source.tar.gz qutemol || exit 1

#  Do a basic check on the directory structure
  if [ ! -e "$TOP_LEVEL/qutemol/src" ]; then
    echo "Incompatible directory structure."
    exit 1
  fi


# Start with the main build
# Build the base .exe and directory contents
  rm -rf $TOP_LEVEL/qutemol/src/Default\ Profile
  tar -xzf /c/build_prereqs/QuteMolX-prereqs.tar.gz || exit 1
  cd $TOP_LEVEL/qutemol/src || exit 1
  cp ../../packaging/Win32/Makefile . || exit 1
  make clean || exit 1
  mkdir $TOP_LEVEL/qutemol/src/Default\ Profile || exit 1
  cp ../../packaging/Win32/main.rc Default\ Profile || exit 1
  #cp ../../packaging/Win32/qutemol_private.rc Default\ Profile || exit 1
  make || exit 1

  mkdir $TOP_LEVEL/packaging/Win32/install || exit 1
  mkdir $TOP_LEVEL/packaging/Win32/install/build || exit 1
  mkdir $TOP_LEVEL/packaging/Win32/install/source || exit 1
  cd Default\ Profile || exit 1
  cp -R ../image . || exit 1 
  cp -R ../presets . || exit 1
  find . -depth -type d -name ".svn" -print -exec rm -rf {} \; 
  cp -R * $TOP_LEVEL/packaging/Win32/install/build || exit 1
  cd $TOP_LEVEL/packaging/Win32/install/source || exit 1
  tar -xzf /c/QMX_source.tar.gz || exit 1

  cd $TOP_LEVEL
  cp $TOP_LEVEL/libpng-3.dll $TOP_LEVEL/packaging/Win32/install/build || exit 1
  cd $TOP_LEVEL/packaging/Win32/install
  find . -depth -type d -name ".svn" -print -exec rm -rf {} \; 
  mkdir /c/QMX_Install
  if [ "$?" = "0" ]
  then
    cp -R build /c/QMX_Install
    cp -r source /c/QMX_Install
  else
    echo "Problem creating binary storage directory"
    echo "Fix this or you will rebuild QuteMolX every time"
  fi
else
  mkdir $TOP_LEVEL/packaging/Win32/install || exit 1
  cd /c/QMX_Install
  cp -R build $TOP_LEVEL/packaging/Win32/install
  cp -R source $TOP_LEVEL/packaging/Win32/install
fi
cd $TOP_LEVEL/packaging/Win32
for name in `echo install.ico install-header.bmp License.txt uninstall.ico wizard-sidebar.bmp QMX_installer.nsi ../ReadMe.html`
do
  cp $name install
done


# Create the installer
cd $TOP_LEVEL/packaging/Win32/install
"c:/program files/nsis/makensis.exe" QMX_installer.nsi

