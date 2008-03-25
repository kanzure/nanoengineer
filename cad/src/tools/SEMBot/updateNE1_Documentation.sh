#!/bin/sh

# Usage: ./updateNE1_Documentation.sh &>NE1_Docs.log

# Create timestamp
echo `date +"%a %b %e %T EDT %Y"` > NE1_Docs.timestamp

# Remove files used to check for command successes
rm -f NE1_Documentation/api-objects.txt

# Run Epydoc
pushd SVN-D/cad/src
/usr/local/bin/epydoc --config epydoc.config
popd

# Check if Epydoc was successful by checking for the existence of the file we
# deleted earlier.
if [ ! -e NE1_Documentation/api-objects.txt ]; then
  RESULT="<font color=red>Failed</font>"
else
  RESULT=Success
fi
echo ${RESULT} > NE1_Docs.result

# Format image tags to html
for file in `find NE1_Documentation -name "*.html"`; do
  sed 's/IMAGE(\([^"]\+\))/<img src="\1">/g' < $file > tmp.html
  mv tmp.html $file
done

