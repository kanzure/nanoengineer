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
if [ ! -e "$TOP_LEVEL/Win32" ]
then
  echo "incorrect directory structure, cannot continue"
  exit 1
fi

rm -rf Win32/build Win32/dist Win32/install

if [ ! -e "/c/GMX_Install" ]
then
  if [ ! -e "/c/build_prereqs/gromacs-$GROMACS_VERSION-modified.tar.gz" ]
  then
    echo "This compile cannot continue until the correct sources are installed."
    cat Win32/installer_build_notes.txt
    exit 1
  fi
  if [ ! -e "/c/build_prereqs/mcpp.zip" ]
  then
    echo "You need a version of mcpp and renamed properly."
    echo "check the installer nsi file for the correct directory structure"
    exit 1
  fi
  mkdir Win32/install
  cd Win32/install
  unzip /c/build_prereqs/mcpp.zip
  cd $TOP_LEVEL
  mkdir Win32/build
  cd Win32/build
  mkdir tmpbuild
  tar -xzvf /c/build_prereqs/gromacs-$GROMACS_VERSION-modified.tar.gz || exit 1
  cd gromacs-$GROMACS_VERSION
  CPPFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure --prefix=$TOP_LEVEL/Win32/build/tmpbuild --enable-double --program-suffix= || exit 1
  make || exit 1
  make install || exit 1
  cd $TOP_LEVEL/Win32
  mkdir dist
  mkdir dist/src
  cd dist/src
  tar -xzvf /c/build_prereqs/gromacs-$GROMACS_VERSION.tar.gz || exit 1
  cd $TOP_LEVEL/Win32/build/tmpbuild
  mv bin $TOP_LEVEL/Win32/dist
  mv include $TOP_LEVEL/Win32/dist
  mv share $TOP_LEVEL/Win32/dist
  mv lib $TOP_LEVEL/Win32/dist
  cd $TOP_LEVEL/Win32
  mv dist install
  for name in `echo License.txt install-header.bmp install.ico uninstall.ico wizard-sidebar.bmp GMX-installer.nsi`
  do
    cp $name install
  done
  cp $TOP_LEVEL/ReadMe.html install
  cd install
  find . -depth -type d -name ".svn" -print -exec rm -rf {} \;
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

cd $TOP_LEVEL/Win32/install
"c:/program files/nsis/makensis.exe" GMX-installer.nsi
