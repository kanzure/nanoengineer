#!/bin/sh -x

CUR_USER=`whoami`
WORK_AS=@INSERT_USER_NAME_HERE@
MAXSEND=5

# give a warning that some things may not work right if you're not root
if [ "$CUR_USER" != "root" ]
then
  echo "You really should be running this script as root."
  echo "You have 10 seconds to cancel."
  sleep 5
fi

# Set up home directory information.  The home directory has to be set up to 
# allow for a proper build of the software.  Check the individual build files 
#for information on what they require.
USERPATH=/Users/$WORK_AS
HOME=$USERPATH

# Change into the home directory
cd || exit 1
# Not needed, but left in for manual verification
pwd

#Wipe out everything from any old autobuilds
if [ ! -e ~/autobuilds ]
then
  mkdir ~/autobuilds || exit 1
fi
if [ -e ~/autobuilds/MacOSX_Installers ]
then
  rm -rf ~/autobuilds/MacOSX_Installers
fi
mkdir ~/autobuilds/MacOSX_Installers || exit 1
if [ -e ~/autobuilds/tartrunk ]
then
  rm -rf ~/autobuilds/tartrunk
fi
if [ -e ~/autobuilds/trunk ]
then
  rm -rf ~/autobuilds/trunk
fi
if [ -e ~/autobuilds/uploads ]
then
  rm -rf ~/autobuilds/uploads
fi

# Make sure path information is set up as it is needed for the stand alone
# python needed to create "standalone" packages
PATH=/Library/Frameworks/Python.framework/Versions/Current/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/usr/X11/bin
export PATH

# Make sure we're running with the python version expected.
PYTHON_VER=`python -c "import sys; print sys.version[:5]"`
if [ "$PYTHON_VER" != "2.4.4" ]
then
  echo "Running with incorrect python version"
  exit 1
fi

# Set up environment variables for later compiles.  This is probably not needed
# but is added just in case some individual builds don't do this properly
export CPPFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
export CFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
export LDFLAGS="-Wl,-syslibroot,/Developer/SDKs/MacOSX10.4u.sdk -isysroot /Developer/SDKs/MacOSX10.4u.sdk -L/usr/local/lib -L/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/lib"
export CXXFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
export FFLAGS="-isysroot /Developer/SDKs/MacOSX10.4u.sdk -mmacosx-version-min=10.3 -I/usr/local/include -I/Developer/SDKs/MacOSX10.4u.sdk/usr/X11R6/include"
export MACOSX_DEPLOYMENT_TARGET=10.3

#Change into the autobuilds directory and make sure it's world access
cd ~/autobuilds || exit 1
chmod 777 . || exit 1

# Download the svn tree
su - $WORK_AS -c "svn co http://polosims_svn-svn.cvsdude.com/polosims/trunk autobuilds/trunk > /tmp/svnstatus 2>&1" || exit 1

# Alternate way of getting the source tree (used for testing)
#cd ~/savedtrunk || exit 1
#mkdir ~/autobuilds/trunk || exit 1
#find . -print | cpio -pudvm ~/autobuilds/trunk || exit 1
#cd ~/autobuilds || exit 1

cp $HOME/trunks/trunk/packaging/MacOSX/SV_AB_Makefile ~/autobuilds/trunk/packaging/MacOSX/SV_AB_Makefile

# Copy versions.txt file for version information.  This will be in the trunk
# under packaging later.  When added, the script will check it out, change it, 
# and check it back in before building.
cp /Users/$WORK_AS/versions.txt ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
chmod 755 ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
. ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1

# Increment the version number for NE1.  Since this is for automatic snapshot
# builds, only the last digit should be changed
TN1=`echo $NE1_VERSION | cut -d "." -f 1`
TN2=`echo $NE1_VERSION | cut -d "." -f 2`
TN3=`echo $NE1_VERSION | cut -d "." -f 3`
TN4=`echo $NE1_VERSION | cut -d "." -f 4`
if [ "$TN3" = "" ]
then
  TN3="0"
fi
if [ "$TN4" = "" ]
then
  TN4="0"
fi
TN4=`expr $TN4 + 1`
NE1_VERSION="$TN1.$TN2.$TN3.$TN4"

# Rewrite the file for later and for checkin.  This is where the file will 
# later be in the tree.
echo "NE1_VERSION=$NE1_VERSION" > ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
echo "GMX_VERSION=$GMX_VERSION" >> ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
echo "QMX_VERSION=$QMX_VERSION" >> ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
echo "PREF_VERSION=$PREF_VERSION" >> ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1
echo "SIM_VERSION=$SIM_VERSION" >> ~/autobuilds/trunk/packaging/Suite/ver_info.sh || exit 1

# Get ready to do the tar builds
rm -rf /tmp/dist_tars
mkdir tartrunk || exit 1
cd trunk || exit 1
# Copy the trunk over so it can be worked on.
find . -print | cpio -pudvm ../tartrunk || exit 1
cd ../tartrunk || exit 1
cd packaging || exit 1
# Make sure the new tree has the right version numbers too.  Probably not needed
cp ~/autobuilds/trunk/packaging/Suite/ver_info.sh ~/autobuilds/tartrunk/packaging/Suite/ver_info.sh || exit 1
./buildTars.sh || exit 1
mv /tmp/dist_tars/*.tar.gz ~/autobuilds/MacOSX_Installers || exit 1
sync

# Get ready for doing the MacOSX builds
cd || exit 1
# See if there are any prebuilds and if so, stash the directory somewhere and
# reuse the installers that we are interested in reusing.
if [ -e MacOSX_Installers ]
then
  mv MacOSX_Installers MacOSX_Installers.autobuild.tmp || exit 1
  mkdir MacOSX_Installers || exit 1
  cd MacOSX_Installers.autobuild.tmp || exit 1
  if [ -e GROMACS_$GMX_VERSION.pkg ]
  then
    cp -R GROMACS_$GMX_VERSION.pkg ~/MacOSX_Installers || exit 1
  fi
  if [ -e QuteMolX_$QMX_VERSION.pkg ]
  then
    cp -R QuteMolX_$QMX_VERSION.pkg ~/MacOSX_Installers || exit 1
  fi
  if [ -e GROMACS_$GMX_VERSION.dmg ]
  then
    cp GROMACS_$GMX_VERSION.dmg ~/MacOSX_Installers || exit 1
  fi
  if [ -e QuteMolX_$QMX_VERSION.dmg ]
  then
    cp QuteMolX_$QMX_VERSION.dmg ~/MacOSX_Installers || exit 1
  fi
else
# Else, make the directory for later use.
  mkdir MacOSX_Installers || exit 1
fi

# Do the actual MacOSX builds now
cd ~/autobuilds || exit 1
cd trunk || exit 1
cd packaging/Suite || exit 1
env
./buildMacSuite.sh || exit 1
# After the builds are done, move them to the autobuilds area
mv ~/MacOSX_Installers/* ~/autobuilds/MacOSX_Installers || exit 1
cd ~ || exit 1
# If we stashed older builds, get them back so we can make sure not to 
# resend files we already sent.
if [ -e MacOSX_Installers.autobuild.tmp ]
then
  rm -rf MacOSX_Installers
  mv MacOSX_Installers.autobuild.tmp MacOSX_Installers || exit 1
fi
# If needed, create the directory needed for uploading to the website
if [ ! -e ~/autobuilds/uploads ]
then
  mkdir ~/autobuilds/uploads || exit 1
  chown $WORK_AS ~/autobuilds/uploads || exit 1
fi

# See which installers are new so we know what to upload and update on the site
cd ~/autobuilds/MacOSX_Installers || exit 1
for name in `ls *.tar.gz *.dmg`
do
 if [ ! -e ~/MacOSX_Installers/$name ]
  then
    cp $name ~/MacOSX_Installers || exit 1
    cp $name ~/autobuilds/uploads || exit 1
  fi
done
# Don't upload pkgs files, but we still want to store them so we don't
# have to recompile all the time.
for name in `ls | grep ".pkg" | grep -v pref_mod`
do
  if [ ! -e ~/MacOSX_Installers/$name ]
  then
    cp -R $name ~/MacOSX_Installers
  fi
done

# Exit here before sending files for test purposes
#exit 0

# Queue up all files for upload
cd ~/autobuilds/uploads || exit 1
~/bin/sendandverify --reset
~/bin/sendandverify *
# See if any failed, and resend them a maximum of MAXSEND tries.  MAXSEND
# includes the original send as try 1.
ERR_COUNT=$?
SEND_COUNT=1
while [ $SEND_COUNT -le MAXSEND ] && [ $ERR_COUNT -gt 0 ]
do
  echo "Resending $ERR_COUNT files."
  SEND_COUNT=`expr $SEND_COUNT + 1`
  ~/bin/sendandverify --resend-append
  ERR_COUNT=$?
done
if [ $ERR_COUNT -gt 0 ]
then
  echo "Error sending $ERR_COUNT files."
else
  echo "All files sent successfully."
fi
