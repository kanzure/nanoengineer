#!/bin/sh

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
tar cf ../pref_modifier.app_0.0.1.tar pref_modifier.app
gzip -9 ../pref_modifier.app_0.0.1.tar
cd ..
sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o ./pref_modifier.pkg -r ./dist -v -f ./PrefMod_info.plist

if [ ! -e ~/MacOSX_Installers/pref_modifier.pkg ]
then
  sudo cp -R pref_modifier.pkg ~/MacOSX_Installers
fi

