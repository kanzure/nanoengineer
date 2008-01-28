TEMPLATE = subdirs 
CONFIG += warn_on \
          qt \
          thread 
OPENBABEL_INCPATH = /usr/include/openbabel-2.0
SUBDIRS += Plugins \
  Interface \
  Testing \
  Utility

