#!/bin/sh

# Usage: ./runPylint.sh &>Pylint.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > Pylint.timestamp

# Remove files used to check for command successes
#rm -f NE1_Documentation/api-objects.txt

# Run Pylint 
pushd SVN-D/cad/src
BATCH_NUMBER=0
for batch in \
  "a*.py A*.py b*.py B*.py c*.py C*.py d*.py D*.py e*.py E*.py f*.py F*.py" \
  "g*.py G*.py h*.py H*.py i*.py I*.py j*.py J*.py k*.py K*.py l*.py L*.py" \
  "m*.py M*.py n*.py N*.py o*.py O*.py p*.py P*.py q*.py Q*.py r*.py R*.py" \
  "s*.py S*.py t*.py T*.py u*.py U*.py v*.py V*.py w*.py W*.py x*.py X*.py" \
  "y*.py Y*.py z*.py Z*.py"; do
  echo Running batch $BATCH_NUMBER
  /usr/local/bin/pylint --rcfile=../../../Pylint.rcfile $batch

  # Post process results
  ../../../pylint_global.pl pylint_global.txt ${BATCH_NUMBER} pylint.${BATCH_NUMBER}.result > pylint_global.${BATCH_NUMBER}.html

  let BATCH_NUMBER=BATCH_NUMBER+1
done

# Aggregate code "grades"
echo "("`cat pylint.0.result`+`cat pylint.1.result`+`cat pylint.2.result`+`cat pylint.3.result`")/4" > tmp.txt;
echo "quit" >> tmp.txt
printf "%1.3f" `bc -l -q tmp.txt` > ../../../Pylint.result
rm pylint.?.result tmp.txt

popd

# Check if Epydoc was successfull by checking for the existence of the file we
# deleted earlier.
#if [ ! -e NE1_Documentation/api-objects.txt ]; then
#  RESULT="<font color=red>Failed</font>"
#else
#  RESULT=Success
#fi
#echo ${RESULT} > NE1_Docs.result

