#!/bin/sh -x

# Usage: Run ./buildMac.sh from the packaging directory.

VERSION_NUM=1.1.1
DIST_VERSION=NanoEngineer-1_$VERSION_NUM
MAJOR=`echo $VERSION_NUM | cut -d "." -f 1`
MINOR=`echo $VERSION_NUM | cut -d "." -f 2`
TINY=`echo $VERSION_NUM | cut -d "." -f 3`

# Set up path variables
cd ..
TOP_LEVEL=`pwd`
DIST_ROOT=$TOP_LEVEL/cad/src/dist
DIST_CONTENTS=$DIST_ROOT/NanoEngineer-1.app/Contents

# Do required exports for building on MacOSX 10.5
export MACOSX_DEPLOYMENT_TARGET=10.3
export CFLAGS="-arch i386 -arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export LDFLAGS="-arch i386 -arch ppc -Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib"
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"
export CXXFLAGS="-arch i386 -arch ppc -isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include"


cd $TOP_LEVEL
# Modifying the foundation/preferences.py file for version
PREFS_VER=`echo $VERSION_NUM | sed -e "s:\.:-:g"`
#cat cad/src/foundation/preferences.py | sed -e "s:default_prefs_v.-.-..txt:default_prefs_v$PREFS_VER.txt:g" > cad/src/foundation/preferences.py.ptmp
#cp cad/src/foundation/preferences.py.ptmp cad/src/foundation/preferences.py || exit 1
DATECODE=`date "+%B %d, %Y"`

#Make modifications to the build constants file.
cat cad/src/NE1_Build_Constants.py | sed -e "s:NE1_RELEASE_VERSION = \\\".*\\\":NE1_RELEASE_VERSION = \\\"$VERSION_NUM\\\":" > cad/src/NE1_Build_Constants.ptmp
mv cad/src/NE1_Build_Constants.ptmp cad/src/NE1_Build_Constants.py || exit 1
cat cad/src/NE1_Build_Constants.py | sed -e "s:NE1_RELEASE_DATE = \\\".*\\\":NE1_RELEASE_DATE = \\\"$DATECODE\\\":" > cad/src/NE1_Build_Constants.ptmp
mv cad/src/NE1_Build_Constants.ptmp cad/src/NE1_Build_Constants.py || exit 1
cat cad/src/NE1_Build_Constants.py | sed -e "s:NE1_USE_bsddb3 = .*:NE1_USE_bsddb3 = True:" > cad/src/NE1_Build_Constants.ptmp
mv cad/src/NE1_Build_Constants.ptmp cad/src/NE1_Build_Constants.py || exit 1

#Modifying the welcome screen (to avoid manual editing)
cat packaging/MacOSX/Welcome_template.rtf | sed -e "s:VERSION_GOES_HERE:$VERSION_NUM:g" | sed -e "s:DATE_GOES_HERE:$DATECODE:g" > packaging/MacOSX/Welcome.rtf
cat packaging/Suite/MacOSX/Welcome_template.rtf | sed -e "s:VERSION_GOES_HERE:$VERSION_NUM:g" | sed -e "s:DATE_GOES_HERE:$DATECODE:g" > packaging/Suite/MacOSX/Welcome.rtf

# Build the base .app directory contents
if [ ! -e "$TOP_LEVEL/cad/src" ]; then exit; fi
cd $TOP_LEVEL/cad/src
sudo rm -rf dist build
cp $TOP_LEVEL/packaging/MacOSX/setup.py .
python setup.py py2app --frameworks=/usr/local/BerkeleyDB.4.5/lib/libdb-4.5.dylib,/usr/local/lib/libopenbabel.1.0.2.dylib,/usr/local/lib/openbabel/APIInterface.so,/usr/local/lib/openbabel/CSRformat.so,/usr/local/lib/openbabel/PQSformat.so,/usr/local/lib/openbabel/alchemyformat.so,/usr/local/lib/openbabel/amberformat.so,/usr/local/lib/openbabel/balstformat.so,/usr/local/lib/openbabel/bgfformat.so,/usr/local/lib/openbabel/boxformat.so,/usr/local/lib/openbabel/cacaoformat.so,/usr/local/lib/openbabel/cacheformat.so,/usr/local/lib/openbabel/carformat.so,/usr/local/lib/openbabel/cccformat.so,/usr/local/lib/openbabel/chem3dformat.so,/usr/local/lib/openbabel/chemdrawformat.so,/usr/local/lib/openbabel/chemtoolformat.so,/usr/local/lib/openbabel/cmlreactlformat.so,/usr/local/lib/openbabel/copyformat.so,/usr/local/lib/openbabel/crkformat.so,/usr/local/lib/openbabel/cssrformat.so,/usr/local/lib/openbabel/dmolformat.so,/usr/local/lib/openbabel/fastsearchformat.so,/usr/local/lib/openbabel/featformat.so,/usr/local/lib/openbabel/fhformat.so,/usr/local/lib/openbabel/fingerprintformat.so,/usr/local/lib/openbabel/freefracformat.so,/usr/local/lib/openbabel/gamessformat.so,/usr/local/lib/openbabel/gaussformat.so,/usr/local/lib/openbabel/ghemicalformat.so,/usr/local/lib/openbabel/gromos96format.so,/usr/local/lib/openbabel/hinformat.so,/usr/local/lib/openbabel/inchiformat.so,/usr/local/lib/openbabel/jaguarformat.so,/usr/local/lib/openbabel/mdlformat.so,/usr/local/lib/openbabel/mmodformat.so,/usr/local/lib/openbabel/mmpformat.so,/usr/local/lib/openbabel/mol2format.so,/usr/local/lib/openbabel/mopacformat.so,/usr/local/lib/openbabel/mpdformat.so,/usr/local/lib/openbabel/mpqcformat.so,/usr/local/lib/openbabel/nwchemformat.so,/usr/local/lib/openbabel/pcmodelformat.so,/usr/local/lib/openbabel/pdbformat.so,/usr/local/lib/openbabel/povrayformat.so,/usr/local/lib/openbabel/pubchem.so,/usr/local/lib/openbabel/qchemformat.so,/usr/local/lib/openbabel/reportformat.so,/usr/local/lib/openbabel/rxnformat.so,/usr/local/lib/openbabel/shelxformat.so,/usr/local/lib/openbabel/smilesformat.so,/usr/local/lib/openbabel/tinkerformat.so,/usr/local/lib/openbabel/turbomoleformat.so,/usr/local/lib/openbabel/unichemformat.so,/usr/local/lib/openbabel/viewmolformat.so,/usr/local/lib/openbabel/xcmlformat.so,/usr/local/lib/openbabel/xedformat.so,/usr/local/lib/openbabel/xmlformat.so,/usr/local/lib/openbabel/xyzformat.so,/usr/local/lib/openbabel/yasaraformat.so,/usr/local/lib/openbabel/zindoformat.so --includes=sip --packages=ctypes,bsddb3 --iconfile ../../packaging/MacOSX/nanorex.icns || exit 1
if [ ! -e "$DIST_CONTENTS/Resources/lib/python2.4/lib-dynload/PyQt4/QtOpenGL.so" ]; then
  cp /Library/Python/2.4/site-packages/PyQt4/QtOpenGL.so $DIST_CONTENTS/Resources/lib/python2.4/lib-dynload/PyQt4/QtOpenGL.so
  strip $DIST_CONTENTS/Resources/lib/python2.4/lib-dynload/PyQt4/QtOpenGL.so
fi
cp $TOP_LEVEL/packaging/MacOSX/py2app-Info.plist $DIST_CONTENTS/Info.plist
cd $TOP_LEVEL

mkdir $DIST_CONTENTS/bin

# Copy the GAMESS helper script
#cp $TOP_LEVEL/cad/src/rungms $DIST_CONTENTS/bin/
#if [ ! -e "$DIST_CONTENTS/bin/rungms" ]; then exit; fi

# Build atombase.so and samevals.so (some native binary NE1 optimizations)
cd $TOP_LEVEL/cad/src
cp ../../packaging/MacOSX/SV_AB_Makefile Makefile
make clean || exit 1
make shared || exit 1
cp atombase.so $DIST_CONTENTS/bin/
cp samevals.so $DIST_CONTENTS/bin/
if [ ! -e "$DIST_CONTENTS/bin/samevals.so" ]; then exit; fi
cd $TOP_LEVEL

# Build and copy NanoDynamics-1
cd $TOP_LEVEL/sim/src
cp $TOP_LEVEL/packaging/MacOSX/ND1-Makefile ./Makefile
make clean || exit 1
make || exit 1
make pyx || exit 1
sudo install_name_tool -change /Library/Frameworks/Python.framework/Versions/2.4/Python @executable_path/../Frameworks/Python.framework/Versions/2.4/Python sim.so || exit 1
cp sim.so $DIST_CONTENTS/bin/ || exit 1
if [ ! -e "$DIST_CONTENTS/bin/sim.so" ]; then exit; fi
cd $TOP_LEVEL

# Copy the gnuplot and AquaTerm binaries
cp /usr/local/bin/gnuplot $DIST_CONTENTS/bin/
cp -R /Applications/AquaTerm.app $DIST_CONTENTS/bin/
cp -R /Library/Frameworks/AquaTerm.framework $DIST_CONTENTS/Frameworks/
if [ ! -e "$DIST_CONTENTS/Frameworks/AquaTerm.framework" ]; then exit; fi

# Copy and arrange the OpenBabel binaries
cp /usr/local/bin/babel $DIST_CONTENTS/bin/ || exit 1
#sudo install_name_tool -change /usr/local/lib/libopenbabel.1.dylib @executable_path/../Frameworks/libopenbabel.1.dylib $DIST_CONTENTS/bin/babel || exit 1
cd $DIST_CONTENTS/Frameworks
ln -s libopenbabel.1.0.2.dylib libopenbabel.1.dylib
mkdir openbabel || exit 1
mv *format.so openbabel/
mv APIInterface.so openbabel/
mv pubchem.so openbabel/
cd $TOP_LEVEL

# Copy the doc/ files
mkdir $DIST_CONTENTS/doc
cp cad/doc/keyboardshortcuts-mac.htm $DIST_CONTENTS/doc/
cp cad/doc/mousecontrols-mac.htm $DIST_CONTENTS/doc/

# Copy partlib tree to a user-visible location and make a symbolic link to it
# for NE1 to use.
cp -R $TOP_LEVEL/cad/partlib $DIST_ROOT/
cd $DIST_CONTENTS
ln -s ../../partlib partlib
if [ ! -e "$DIST_CONTENTS/partlib" ]; then exit; fi
cd $TOP_LEVEL

# Copy images
cd $TOP_LEVEL
DIST_IMAGES_DIR=$DIST_CONTENTS/src/ui/
mkdir -p $DIST_IMAGES_DIR/actions
cp -R cad/src/ui $DIST_CONTENTS/src/
#cp -R cad/src/ui/actions/Edit $DIST_IMAGES_DIR/actions/ 
#cp -R cad/src/ui/actions/File $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Help $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Insert $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Properties\ Manager $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Simulation $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Toolbars $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/Tools $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/actions/View $DIST_IMAGES_DIR/actions/
#cp -R cad/src/ui/border $DIST_IMAGES_DIR
#cp -R cad/src/ui/confcorner $DIST_IMAGES_DIR
#cp -R cad/src/ui/cursors $DIST_IMAGES_DIR
#cp -R cad/src/ui/dialogs $DIST_IMAGES_DIR
#cp -R cad/src/ui/exprs $DIST_IMAGES_DIR
#cp -R cad/src/ui/images $DIST_IMAGES_DIR
#cp -R cad/src/ui/modeltree $DIST_IMAGES_DIR
cd $TOP_LEVEL

# Copy the ReadeMe.html file and Licenses/ files
cp $TOP_LEVEL/cad/src/ReadMe.html $DIST_ROOT/
mkdir $DIST_ROOT/Licenses
cp $TOP_LEVEL/cad/src/LICENSE $DIST_ROOT/Licenses/NanoEngineer-1_License.txt
cp $TOP_LEVEL/cad/licenses-common/Gnuplot_License $DIST_ROOT/Licenses/Gnuplot_License.txt
cp $TOP_LEVEL/cad/licenses-common/NanoKids_Attribution $DIST_ROOT/Licenses/NanoKids_Attribution.txt
cp $TOP_LEVEL/cad/licenses-common/OpenGL_License.doc $DIST_ROOT/Licenses/
cp $TOP_LEVEL/cad/licenses-common/OpenGL_LicenseOverview $DIST_ROOT/Licenses/OpenGL_LicenseOverview.txt
cp $TOP_LEVEL/cad/licenses-common/PyOpenGL_License $DIST_ROOT/Licenses/PyOpenGL_License.txt
cp $TOP_LEVEL/cad/licenses-common/Python_License $DIST_ROOT/Licenses/Python_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/AquaTerm_License $DIST_ROOT/Licenses/AquaTerm_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/PyQt_License $DIST_ROOT/Licenses/PyQt_License.txt
cp $TOP_LEVEL/cad/licenses-Mac/Qt_License $DIST_ROOT/Licenses/Qt_License.txt
cp $TOP_LEVEL/packaging/MacOSX/ctypes_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/numarray_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/NumPy_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/PythonImagingLibrary_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/OracleBerkeleyDB_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/bsddb3_License.txt $DIST_ROOT/Licenses/
cp $TOP_LEVEL/packaging/MacOSX/OpenBabel_License.txt $DIST_ROOT/Licenses/

# Plugins
#
mkdir $DIST_CONTENTS/plugins

# Build and copy the CoNTub plugin
#cd $TOP_LEVEL/cad/plugins/CoNTub
#make
#cp -R ../CoNTub $DIST_CONTENTS/plugins/
#if [ ! -e "$DIST_CONTENTS/plugins/CoNTub/bin/HJ" ]; then exit; fi
#cd $TOP_LEVEL

cp -R $TOP_LEVEL/cad/plugins/DNA $DIST_CONTENTS/plugins/
cp -R $TOP_LEVEL/cad/plugins/NanoDynamics-1 $DIST_CONTENTS/plugins/
mkdir $DIST_CONTENTS/plugins/GROMACS
cp -R $TOP_LEVEL/cad/plugins/GROMACS/Pam5Potential.xvg $DIST_CONTENTS/plugins/GROMACS/
cp -R $TOP_LEVEL/cad/plugins/GROMACS/mdrunner.sh $DIST_CONTENTS/plugins/GROMACS/
cp -R $TOP_LEVEL/cad/plugins/Nanotube $DIST_CONTENTS/plugins/

cd $TOP_LEVEL
#
# End Plugins

# Remove cruft
rm -rf `find $DIST_ROOT -name CVS`
rm -rf $DIST_ROOT/partlib/*/CVS
rm -rf $DIST_ROOT/partlib/*/*/CVS
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/bsddb3/tests || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/ctypes/test || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/doc || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/testing || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/numpy/tests || exit 1
#rm -rf $DIST_CONTENTS/Resources/lib/python2.3/OpenGL/tests || exit 1
for file in `find $DIST_ROOT -name *.py`; do
  if [ -e ${file}c ]; then
    rm $file
  fi
done

# Prepare package hierarchy
cd $TOP_LEVEL/packaging/MacOSX
tar xf NE1-folder.tar
cd $TOP_LEVEL
ditto --rsrc $TOP_LEVEL/packaging/MacOSX/NE1-folder $DIST_ROOT/$DIST_VERSION
mv $DIST_ROOT/Licenses $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/NanoEngineer-1.app $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/partlib $DIST_ROOT/$DIST_VERSION/
mv $DIST_ROOT/ReadMe.html $DIST_ROOT/$DIST_VERSION/
cp $TOP_LEVEL/cad/src/LICENSE $TOP_LEVEL/packaging/MacOSX/License.txt
cp $TOP_LEVEL/packaging/MacOSX/background.jpg $DIST_ROOT/$DIST_VERSION/NanoEngineer-1.app/Contents/Resources/
chmod -R 775 $DIST_ROOT/$DIST_VERSION
chmod ugo-x $DIST_ROOT/$DIST_VERSION/partlib/*/*.mmp
chmod ugo-x $DIST_ROOT/$DIST_VERSION/partlib/*/*/*.mmp
chmod ugo-x $DIST_ROOT/$DIST_VERSION/Licenses/*
chmod ugo-x $DIST_ROOT/$DIST_VERSION/ReadMe.html
sudo chown -R root:admin $DIST_ROOT/$DIST_VERSION
sudo chmod -R g+w $DIST_ROOT/$DIST_VERSION
sudo chmod -R o+w $DIST_ROOT/$DIST_VERSION
cd $DIST_ROOT/$DIST_VERSION
echo "Removing:"
sudo find . -depth -type d -name ".svn" -print -exec rm -rf {} \;
cd $TOP_LEVEL
# Create package

sudo /Developer/Applications/Utilities/PackageMaker.app/Contents/MacOS/PackageMaker -o $TOP_LEVEL/cad/src/build/$DIST_VERSION.pkg -r $DIST_ROOT -v -e $TOP_LEVEL/packaging/MacOSX -f $TOP_LEVEL/packaging/MacOSX/NE1-package-info.plist

# Create the disk image
sudo mkdir $TOP_LEVEL/cad/src/build/$DIST_VERSION
sudo mv $TOP_LEVEL/cad/src/build/$DIST_VERSION.pkg $TOP_LEVEL/cad/src/build/$DIST_VERSION/
sudo hdiutil create -srcfolder $TOP_LEVEL/cad/src/build/$DIST_VERSION -fs HFS+ -format UDZO $TOP_LEVEL/cad/src/build/${DIST_VERSION}.dmg

cd $TOP_LEVEL/packaging

# Prepare the disk image (for drag-n-drop install)
#mkdir -p $DIST_ROOT/$DIST_VERSION/$DIST_VERSION
#mv $DIST_ROOT/Licenses $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/NanoEngineer-1.app $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/partlib $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#mv $DIST_ROOT/ReadMe.html $DIST_ROOT/$DIST_VERSION/$DIST_VERSION/
#ln -s /Applications $DIST_ROOT/$DIST_VERSION/Applications
#cp $TOP_LEVEL/packaging/MacOSX/install-background.png $DIST_ROOT/$DIST_VERSION/
#cp $TOP_LEVEL/cad/src/ReadMe.html $DIST_ROOT/$DIST_VERSION/
#cp $TOP_LEVEL/cad/src/LICENSE $DIST_ROOT/$DIST_VERSION/License.txt

# For the plain-Jane installer
#hdiutil create -srcfolder $DIST_ROOT/$DIST_VERSION -format UDZO $DIST_ROOT/${DIST_VERSION}.dmg

