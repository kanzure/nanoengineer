#!/bin/sh -x

# Usage: ./runNightlyBuild.sh &>NightlyBuild.log

NE1_VERSION=0.9.2

echo `date +"%a %b %e %T EDT %Y"` > NightlyBuild.timestamp

pushd SVN-D

# Bootstrap
rm -f configure
export PATH=/usr/local/bin:$PATH
./bootstrap
if [ ! -e configure ]; then
  popd
  echo "<font color=red>Failed</font>" > NightlyBuild.result
  exit
fi

# Configure
rm -f Makefile
export PKG_CONFIG_PATH=/usr/local/Trolltech/Qt-4.2.3/lib
./configure
if [ ! -e Makefile ]; then
  popd
  echo "<font color=red>Failed</font>" > NightlyBuild.result
  exit
fi

# Make distribution
rm -f NanoEngineer-1_*.tar.gz
make dist
if [ ! -e NanoEngineer-1_${NE1_VERSION}.tar.gz ]; then
  popd
  echo "<font color=red>Failed</font>" > NightlyBuild.result
  exit
fi

# Archive distribution
SERIAL_NUMBER=`date +"%y%m%da"`
BUILD_FILENAME=`echo NanoEngineer-1_${NE1_VERSION}.tar.gz | sed "s/${NE1_VERSION}/${NE1_VERSION}_${SERIAL_NUMBER}/"`
mv NanoEngineer-1_${NE1_VERSION}.tar.gz ../NE1_Builds/${BUILD_FILENAME}

popd

# Create build descriptions
BUILD_FILESIZE=`du -h NE1_Builds/${BUILD_FILENAME} | sed 's/\([0-9a-zA-Z\.]*\).*/\1/'`
echo "<td><span class=\"summary-name\"><a href=\"/Engineering/NE1_Builds/${BUILD_FILENAME}\">tar.gz</a>&nbsp;&nbsp;</span></td><td><span class=\"summary-name\">[${BUILD_FILESIZE}]</span></td>" > tar.gz.frag
echo "NanoEngineer-1${NE1_VERSION}_${SERIAL_NUMBER}" > NightlyBuild.filename

# Create archive entry
echo "        <tr><td>NanoEngineer-1_${NE1_VERSION}_${SERIAL_NUMBER}</td><td><a href=\"/Engineering/NE1_Builds/${BUILD_FILENAME}\">tar.gz</a></td><td>| <a href=\"#\">dmg</a></td><td>| <a href=\"#\">rpm</a></td></tr>" > archives.frag.tmp
cat archives.frag >> archives.frag.tmp
mv archives.frag.tmp archives.frag

echo "Success" > NightlyBuild.result

