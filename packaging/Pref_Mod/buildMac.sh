#!/bin/sh

rm -rf build dist
python setup_mac.py py2app --frameworks=/usr/local/BerkeleyDB.4.5/lib/libdb-4.5.dylib --packages=bsddb3
cp py2app-Info.plist dist/pref_modifier.app/Contents/Info.plist 
cd dist
tar cf pref_modifier.app.tar pref_modifier.app
gzip -9 pref_modifier.app.tar

