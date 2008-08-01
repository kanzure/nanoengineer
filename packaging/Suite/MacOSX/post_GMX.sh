#!/bin/sh
OUTFIL=/tmp/NE1_suite_scriptvars_GMX
GMXSPATH=$0
echo "GMXSPATH=$GMXSPATH" > $OUTFIL
GMXPPATH=$1
echo "GMXPPATH=$GMXPPATH" >> $OUTFIL
GMXTARGETLOC=$2
echo "GMXTARGETLOC=$GMXTARGETLOC" >> $OUTFIL
GMXTARGETVOL=$3
echo "GMXTARGETVOL=$GMXTARGETVOL" >> $OUTFIL
#env | grep -v "^_" >> $OUTFIL
PMTARGETLOC=`grep PMTARGETLOC /tmp/NE1_suite_scriptvars_pm| cut -c 13-`
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K gromacs_enabled -V True >> /dev/null"
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K gromacs_path -V \"$GMXTARGETLOC/bin/mdrun\" >> /dev/null"
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K cpp_enabled -V True >> /dev/null"
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K cpp_path -V \"$GMXTARGETLOC/mcpp/bin/mcpp\" >> /dev/null"


