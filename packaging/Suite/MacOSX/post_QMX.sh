#!/bin/sh
OUTFIL=/tmp/NE1_suite_scriptvars_QMX
QMXSPATH=$0
echo "QMXSPATH=$QMXSPATH" > $OUTFIL
QMXPPATH=$1
echo "QMXPPATH=$QMXPPATH" >> $OUTFIL
QMXTARGETLOC=$2
echo "QMXTARGETLOC=$QMXTARGETLOC" >> $OUTFIL
QMXTARGETVOL=$3
echo "QMXTARGETVOL=$QMXTARGETVOL" >> $OUTFIL
#env | grep -v "^_" >> $OUTFIL
PMTARGETLOC=`grep PMTARGETLOC /tmp/NE1_suite_scriptvars_pm| cut -c 13-`
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K qutemol_enabled -V True >> /dev/null"
su $USER -c "$PMTARGETLOC/pref_modifier.app/Contents/MacOS/pref_modifier -K qutemol_path -V \"$QMXTARGETLOC/QuteMolX.app\" >> /dev/null"
rm /tmp/NE1_suite_scriptvars*
