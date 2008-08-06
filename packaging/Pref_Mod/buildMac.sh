#!/bin/sh -x

# The same checks for a stored version in ~/MacOSX_Installers/<something> are
# not in Pref_Mod as they are for gromacs and qutemol.  This is because 
# pref_modifier changes with every version number.  Plus, it only adds about 
# two minutes to the build time.  Also, this file uses the NE1_Build_Constants
# for the version number.  The NE1 and Suite Installers modify this, so if 
# this script is run manually, make sure to make the necessary changes.

PREF_VERSION="0.0.1"

# set up a directory to store pre-built stuff
if [ ! -e ~/MacOSX_Installers ]
then
  mkdir ~/MacOSX_Installers
fi

rm -rf build dist pref_modifier.app_*.tar.gz
cp ../../cad/src/NE1_Build_Constants.py .
python setup_mac.py py2app --frameworks=/usr/local/BerkeleyDB.4.5/lib/libdb-4.5.dylib --packages=bsddb3
cp py2app-Info.plist dist/pref_modifier.app/Contents/Info.plist 
cd dist
tar cf ../pref_modifier.app_$PREF_VERSION.tar pref_modifier.app
gzip -9 ../pref_modifier.app_$PREF_VERSION.tar
cd ..
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o ./pref_modifier.pkg -r ./dist -v -f ./PrefMod_info.plist

if [ ! -e ~/MacOSX_Installers/pref_modifier.pkg ]
then
  sudo cp -R pref_modifier.pkg ~/MacOSX_Installers
fi

