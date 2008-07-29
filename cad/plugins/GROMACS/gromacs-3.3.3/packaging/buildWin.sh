#!/bin/sh -x

# This script must be run from the packaging directory under the gromacs
# plugins area of the source tree

if [ "$1" = "" ]
then
  GROMACS_VERSION="3.3.3"
else
  GROMACS_VERSION="$1"
fi

TOP_LEVEL=`pwd`

# do a quick check to see if I'm running from somewhere that might make sense
if [ ! -e "$TOP_LEVEL/Win32" ]
then
  echo "incorrect directory structure, cannot continue"
  exit 1
fi

# Get rid of any build stuff from before.
rm -rf Win32/build Win32/dist Win32/install

# If there isn't a pre-built version cached
if [ ! -e "/c/GMX_Install" ]
then
# do the build, so grab the Win modified sources.
  if [ ! -e "/c/build_prereqs/gromacs-$GROMACS_VERSION-modified.tar.gz" ]
  then
    echo "This compile cannot continue until the correct sources are installed."
    cat Win32/installer_build_notes.txt
    exit 1
  fi
# Make sure the mcpp.zip exists for the packager later.
  if [ ! -e "/c/build_prereqs/mcpp.zip" ]
  then
    echo "You need a version of mcpp and renamed properly."
    echo "check the installer nsi file for the correct directory structure"
    exit 1
  fi
  mkdir Win32/install || exit 1
  cd Win32/install
  unzip /c/build_prereqs/mcpp.zip || exit 1
  cd $TOP_LEVEL
  mkdir Win32/build || exit 1
  cd Win32/build || exit 1
  mkdir tmpbuild || exit 1
# expand the gromacs Win source into the build directory
  tar -xzvf /c/build_prereqs/gromacs-$GROMACS_VERSION-modified.tar.gz || exit 1

# Build gromacs phase
  cd gromacs-$GROMACS_VERSION || exit 1
  CPPFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure --prefix=$TOP_LEVEL/Win32/build/tmpbuild --enable-double --program-suffix= || exit 1
  make || exit 1
  make install || exit 1
# end of gromacs build

  cd $TOP_LEVEL/Win32 || exit 1
# Make and fill the final distribution directories
  mkdir dist || exit 1
  mkdir dist/src || exit 1
  cd dist/src || exit 1
# extract the stock source into it
  tar -xzvf /c/build_prereqs/gromacs-$GROMACS_VERSION.tar.gz || exit 1
  cd $TOP_LEVEL/Win32/build/tmpbuild || exit 1
# move the built binaries into the distribution directory
  mv bin $TOP_LEVEL/Win32/dist || exit 1
  mv include $TOP_LEVEL/Win32/dist || exit 1
  mv share $TOP_LEVEL/Win32/dist || exit 1
  mv lib $TOP_LEVEL/Win32/dist || exit 1

# move the gromacs distribution to where it needs to be for the installer
# this is in a shared directory with mcpp
  cd $TOP_LEVEL/Win32 || exit 1
  mv dist install || exit 1
# move the other files needed for the installer
  for name in `echo License.txt install-header.bmp install.ico uninstall.ico wizard-sidebar.bmp GMX-installer.nsi`
  do
    cp $name install || exit 1
  done
  cp $TOP_LEVEL/ReadMe.html install || exit 1
  cd install || exit 1
  find . -depth -type d -name ".svn" -print -exec rm -rf {} \;

# Do the backup, but we don't care if it succeeds
  mkdir /c/GMX_Install
  if [ "$?" = "0" ]
  then
    cd install
    cp -R dist /c/GMX_Install
    cp -R mcpp /c/GMX_Install
  else
    echo "Unable to create pre-compiled directory c:\GMX_Install"
    echo "Fix this or you will always have to compile gromacs every time"
  fi
else
# There's already pre-built binaries in the cache location, use them
  cd $TOP_LEVEL/Win32
  mkdir install
  for name in `echo License.txt install-header.bmp install.ico uninstall.ico wizard-sidebar.bmp GMX-installer.nsi`
  do
    cp $name install
  done
  cp $TOP_LEVEL/ReadMe.html install
  cd /c/GMX_Install
  cp -R dist $TOP_LEVEL/Win32/install
  cp -r mcpp $TOP_LEVEL/Win32/install
fi

cd $TOP_LEVEL/Win32 || exit 1

# Change the version information for the installer script
cat GMX-installer.nsi | sed -e "s:^!define PRODUCT_VERSION .*:!define PRODUCT_VERSION \\\"$GROMACS_VERSION\\\":" > GMX-installer.nsi.btmp
mv GMX-installer.nsi.btmp GMX-installer.nsi || exit 1

Run the installer
cd $TOP_LEVEL/Win32/install
"c:/program files/nsis/makensis.exe" GMX-installer.nsi
