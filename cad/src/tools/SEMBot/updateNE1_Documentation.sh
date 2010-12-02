#!/bin/sh

# Usage: ./updateNE1_Documentation.sh &>NE1_Docs.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > NE1_Docs.timestamp

# Remove file from Epydoc-generated docs
rm -f NE1_Documentation/api-objects.txt

# Update codebase
CVS='cvs -d :pserver:bhelfrich@cvs2.cvsdude.com:/cvs/polosims'
pushd CVS-D
${CVS} update -d cad/src

# Run Epydoc
cd cad/src
/usr/local/bin/epydoc --config epydoc.config
popd

# Check if Epydoc was successfull by checking for the existence of the file we
# deleted earlier.
if [ ! -e NE1_Documentation/api-objects.txt ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > NE1_Docs.result

# Format image tags to html
for file in `find NE1_Documentation -name *.html`; do
  sed 's/IMAGE(\([^"]\+\))/<img src="\1">/g' < $file > tmp.html
  mv tmp.html $file
done

