TEMPLATE = subdirs 
CONFIG += warn_on \
          qt \
          thread \
 ordered
OPENBABEL_INCPATH = /usr/include/openbabel-2.0

SUBDIRS += Utility \
  Interface \
  Plugins \
  Testing \
 nv1
