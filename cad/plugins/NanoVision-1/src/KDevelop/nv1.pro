TEMPLATE = subdirs 

CONFIG += warn_on \
          qt \
          thread \
 ordered \
 debug

SUBDIRS += Utility \
  Interface \
  Plugins \
 nv1 \
   Testing 

