#!/bin/bash
# this is a script shell for setting up the application bundle for the mac
# it should be run in the qutemol/src/osx-install dir.
# it moves needed dynlib into the package and runs the 
# install_tool on them to change the linking paths
FMPATH="/Library/Frameworks"
APPNAME="QuteMol.app"

BUNDLE="QuteMolBundle"
DYLIB_PATH="/sw/lib"
DYLIB="/sw/lib/libpng.3.dylib /sw/lib/libiconv.2.dylib /sw/lib/libgif.4.dylib /usr/X11R6/lib/libSM.6.dylib /usr/X11R6/lib/libICE.6.dylib /usr/X11R6/lib/libX11.6.dylib"

if [ -e $APPNAME -a -d $APPNAME ]
then
  echo "------------------"
else
  echo "Started in the wrong dir"
  exit 0
fi

echo "Starting to copying stuff in the bundle"

rm -r -f $BUNDLE

mkdir $BUNDLE
cp -r $APPNAME $BUNDLE

mkdir $BUNDLE/$APPNAME/Contents/plugins   

cp ../install/citeware.txt $BUNDLE
cp ../install/readme.txt $BUNDLE
cp ../install/whatsnew.txt $BUNDLE

mkdir $BUNDLE/sample

cp ../sample/formicacid.pdb $BUNDLE/sample
cp ../sample/nanostuff.pdb $BUNDLE/sample
cp ../sample/nanostuff.art $BUNDLE/sample
cp ../sample/testosterone.pdb $BUNDLE/sample
cp ../sample/porin.pdb $BUNDLE/sample

for x in $DYLIB
do
 cp $x $BUNDLE/$APPNAME/Contents/plugins
done

echo "now trying to change the paths in the meshlab executable"

    
install_name_tool -id  @executable_path/../plugins/libpng.3.dylib    $BUNDLE/$APPNAME/Contents/plugins/libpng.3.dylib
install_name_tool -id  @executable_path/../plugins/libiconv.2.dylib  $BUNDLE/$APPNAME/Contents/plugins/libiconv.2.dylib
install_name_tool -id  @executable_path/../plugins/libgif.4.dylib    $BUNDLE/$APPNAME/Contents/plugins/libgif.4.dylib
install_name_tool -id  @executable_path/../plugins/libSM.6.dylib    $BUNDLE/$APPNAME/Contents/plugins/libSM.6.dylib
install_name_tool -id  @executable_path/../plugins/libX11.6.dylib   $BUNDLE/$APPNAME/Contents/plugins/libX11.6.dylib
install_name_tool -id  @executable_path/../plugins/libICE.6.dylib   $BUNDLE/$APPNAME/Contents/plugins/libICE.6.dylib
    
install_name_tool -change /sw/lib/libpng.3.dylib          @executable_path/../plugins/libpng.3.dylib   $BUNDLE/$APPNAME/Contents/MacOS/qutemol 
install_name_tool -change /sw/lib/libiconv.2.dylib        @executable_path/../plugins/libiconv.2.dylib $BUNDLE/$APPNAME/Contents/MacOS/qutemol 
install_name_tool -change /sw/lib/libgif.4.dylib          @executable_path/../plugins/libgif.4.dylib   $BUNDLE/$APPNAME/Contents/MacOS/qutemol 
install_name_tool -change /usr/X11R6/lib/libSM.6.dylib    @executable_path/../plugins/libSM.6.dylib    $BUNDLE/$APPNAME/Contents/MacOS/qutemol 
install_name_tool -change /usr/X11R6/lib/libICE.6.dylib   @executable_path/../plugins/libICE.6.dylib   $BUNDLE/$APPNAME/Contents/MacOS/qutemol 
install_name_tool -change /usr/X11R6/lib/libX11.6.dylib   @executable_path/../plugins/libX11.6.dylib   $BUNDLE/$APPNAME/Contents/MacOS/qutemol 

install_name_tool -change /usr/X11R6/lib/libICE.6.dylib   @executable_path/../plugins/libICE.6.dylib  $BUNDLE/$APPNAME/Contents/plugins/libgif.4.dylib
install_name_tool -change /usr/X11R6/lib/libSM.6.dylib    @executable_path/../plugins/libSM.6.dylib   $BUNDLE/$APPNAME/Contents/plugins/libgif.4.dylib
install_name_tool -change /usr/X11R6/lib/libX11.6.dylib   @executable_path/../plugins/libX11.6.dylib  $BUNDLE/$APPNAME/Contents/plugins/libgif.4.dylib
install_name_tool -change /usr/X11R6/lib/libICE.6.dylib   @executable_path/../plugins/libICE.6.dylib  $BUNDLE/$APPNAME/Contents/plugins/libSM.6.dylib

