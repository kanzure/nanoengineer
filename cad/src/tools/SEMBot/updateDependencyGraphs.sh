#!/bin/sh

# $Id$

HERE=/home/httpd/vhosts/nanohive-1.org/httpdocs/Engineering

cd SVN-D/cad/src

echo creating color module graph
/usr/local/bin/python tools/PackageDependency.py `tools/AllPyFiles.sh` --justCycles --colorPackages > $HERE/dependcolor.dot 2> $HERE/packageloopcounts

echo creating bw module graph
/usr/local/bin/python tools/PackageDependency.py `tools/AllPyFiles.sh` --justCycles > $HERE/depend.dot 2> $HERE/packageloopcounts.in

echo creating color package graph
/usr/local/bin/python tools/PackageDependency.py `tools/AllPyFiles.sh` --byPackage --colorPackages > $HERE/dependpack.dot 2> $HERE/packagemodulemapping.in

echo "creating proposed source file listing based on package classification..."
cd tools
/usr/local/bin/python packageData_checker.py ../*.py > $HERE/proposed_file_listing.txt
echo " ... done"

cd $HERE

# dot is broken on the NHAH box
#
#echo dot depend.dot
#dot -Tpng dependcolor.dot > Depend.png
#echo dot dependpack.dot
#dot -Tpng dependpack.dot > DependPackage.png

#echo sort packageloopcounts
#sort -r packageloopcounts.in > packageloopcounts
#echo sort packagemodulemapping
#sort packagemodulemapping.in | uniq | sed '/undefined package color/d' > packagemodulemapping

#rm packagemodulemapping.in packageloopcounts.in
#rm dependcolor.dot dependpack.dot
rm packagemodulemapping.in packageloopcounts*
rm dependcolor.dot

grep "\->" depend.dot | wc -l > depend.dot.lines
grep "\->" dependpack.dot | wc -l > dependpack.dot.lines

