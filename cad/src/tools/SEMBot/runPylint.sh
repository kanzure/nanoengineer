#!/bin/sh

# Usage: ./runPylint.sh &>Pylint.log

# Run Pylint 
pushd SVN-D/cad/src
BATCH_NUMBER=0
# Some files break Pylint, exclude them
CAPITAL_T_STAR=`ls T*.py|grep -v TreeView.py|grep -v TreeWidget.py`
PM_STAR=`ls PM/PM_*.py|grep -v PM_CheckBox|grep -v PM_Slider.py`
# Run in batches
for batch in \
  "a*.py A*.py b*.py B*.py c*.py C*.py d*.py D*.py e*.py E*.py f*.py F*.py" \
  "g*.py G*.py h*.py H*.py i*.py I*.py j*.py J*.py k*.py K*.py l*.py L*.py" \
  "m*.py M*.py n*.py N*.py o*.py O*.py p*.py P*.py q*.py Q*.py r*.py R*.py" \
  "s*.py S*.py t*.py $CAPITAL_T_STAR u*.py U*.py v*.py V*.py w*.py W*.py x*.py X*.py" \
  "y*.py Y*.py z*.py Z*.py" \
  "exprs/*.py" "$PM_STAR"; do
  echo Running batch $BATCH_NUMBER
  /usr/local/bin/pylint --rcfile=../../../Pylint.rcfile $batch

  # Post process results
  ../../../pylint_global.pl pylint_global.txt ${BATCH_NUMBER} pylint.${BATCH_NUMBER}.result > pylint_global.${BATCH_NUMBER}.html

  let BATCH_NUMBER=BATCH_NUMBER+1
done

# Aggregate code "grades"
echo "scale=3" > tmp.txt
echo "average=("`cat pylint.0.result`+`cat pylint.1.result`+`cat pylint.2.result`+`cat pylint.3.result`+`cat pylint.5.result`+`cat pylint.6.result`")/6" >> tmp.txt
echo "if (average > 2.5) {" >> tmp.txt
echo "  if (average > 5.0) {" >> tmp.txt
echo "    if (average > 7.5) {" >> tmp.txt
echo "      ;" >> tmp.txt
echo "    } else {" >> tmp.txt
echo "      \"<font style=\"; print \"\q\"; \"color: #ffffff; background: #3ab0b6\"; print \"\q\"; \">&nbsp;\"" >> tmp.txt
echo "    }" >> tmp.txt
echo "  } else {" >> tmp.txt
echo "    \"<font style=\"; print \"\q\"; \"color: #ffffff; background: #fd5053\"; print \"\q\"; \">&nbsp;\"" >> tmp.txt
echo "  }" >> tmp.txt
echo "} else {" >> tmp.txt
echo "  \"<font style=\"; print \"\q\"; \"color: #ffffff; background: #ff0000\"; print \"\q\"; \">&nbsp;\"" >> tmp.txt
echo "}" >> tmp.txt
echo "average; \"</font>\"" >> tmp.txt
echo "quit" >> tmp.txt
echo `bc -q tmp.txt` > ../../../Pylint.result
rm pylint.?.result tmp.txt

popd

