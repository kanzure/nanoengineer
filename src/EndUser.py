
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
  an end user run.

  @author: Eric Messick
  @version: $Id$
  @copyright: 2007 Nanorex, Inc.
  @license: GPL 
"""

_developerFeatures = False

def enableDeveloperFeatures():
    """
       Returns True if developer features should be enabled.

       Call this to see if you should enable a particular developer feature.
    """
    global _developerFeatures
    return _developerFeatures

def setDeveloperFeatures(developerFeatures):
    """
       Called at startup once we figure out if this is a developer run or and end user run.
    """
    global _developerFeatures
    _developerFeatures = developerFeatures
