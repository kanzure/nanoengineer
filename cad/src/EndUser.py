
# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
  EndUser.py

  Some program features are intended specifically for developers, and
  are best left disabled for end users.  Examples might be debugging
  prints, and the ability to reload a changed module.  Such code is
  wrapped with a test which calls enableDeveloperFeatures() here.

  Early in startup, setDeveloperFeatures() should be called after
  detecting if this is an end user or developer run.  Until this is
  called, enableDeveloperFeatures() will default to False, indicating
  an end user run (but will print a bug warning if it's ever called then).

  @author: Eric Messick
  @version: $Id$
  @copyright: 2007 Nanorex, Inc.
  @license: GPL 
"""

_developerFeatures = False
_developerFeatures_set_yet = False

def enableDeveloperFeatures():
    """
       Returns True if developer features should be enabled.

       Call this to see if you should enable a particular developer feature.
    """
    if not _developerFeatures_set_yet:
        print "bug: enableDeveloperFeatures() queried before " \
              " setDeveloperFeatures() called; returning %r" % \
              _developerFeatures
    return _developerFeatures

def setDeveloperFeatures(developerFeatures):
    """
       Called at startup once we figure out if this is a developer run
       or and end user run.
    """
    global _developerFeatures, _developerFeatures_set_yet
    _developerFeatures = developerFeatures
    _developerFeatures_set_yet = True
    return

_alternateSourcePath = None

def getAlternateSourcePath():
    """
    Returns the path to a directory other than the one main.py was
    found in, which will be searched first for any imports, or None if
    not set.  Allows users to override any python files without
    modifing the released copies.
    """
    return _alternateSourcePath

def setAlternateSourcePath(path):
    """
    Called from main.py after adding the alternate source path to the
    front of the search path.  Allows other code to determine if this
    has been done, and to obtain the value via
    getAlternateSourcePath().
    """
    global _alternateSourcePath
    _alternateSourcePath = path
