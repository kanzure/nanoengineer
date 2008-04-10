#!/bin/sh
rm -rf gromacs-3.3.2-joined
mkdir gromacs-3.3.2-joined
cd gromacs-3.3.2-i386
find . -type d -exec mkdir ../gromacs-3.3.2-joined/{} \;
find . -name "*.a" -exec cp {} ../gromacs-3.3.2-joined/{}-i386 \;
find . -name "*.a" -exec cp {} ../gromacs-3.3.2-joined/{} \;
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-3.3.2-joined/$name-i386
      cp $name ../gromacs-3.3.2-joined/$name
    fi
  fi
done
cd ../gromacs-3.3.2-ppc
find . -name "*.a" -exec cp {} ../gromacs-3.3.2-joined/{}-ppc \;
for name in `find . -type f`
do
  if [ -x "$name" ]
  then
    file $name | grep Mach-O > /tmp/stitch_gromacs_junk
    if [ "$?" == "0" ]
    then
      cp $name ../gromacs-3.3.2-joined/$name-ppc
    fi
  fi
done
cd ../gromacs-3.3.2-joined
echo "Starting joining process"
for name in `find . -type f ! -name "*-i386" ! -name "*-ppc" -print`
do
  rm $name
  echo $name
  lipo -create $name-i386 $name-ppc -output $name
  rm $name-i386 $name-ppc
done
mkdir ../gromacs-3.3.2-univ
cd gromacs-3.3.2-i386
find . -print | cpio -pudvm ../gromacs-3.3.2-univ
cd ../gromacs-3.3.2-joined
find . -type f -print -exec cp {} ../gromacs-3.3.2-univ/{} \;

