TEMPLATE = subdirs 

CONFIG += warn_on \
          qt \
          thread \
 ordered \
 debug_and_release

SUBDIRS += Utility \
  Interface \
  Plugins \
  Testing \
 nv1
