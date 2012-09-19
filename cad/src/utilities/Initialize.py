
# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
  Initialize.py

  Routines for supporting initialization functions.

  An initialization function should look like this::

    def initialize():
      if (Initialize.startInitialization(__name__)):
        return
      ... initialization code here ...
      Initialize.endInitialization(__name__)

  This will prevent the initialization code from being run more than
  once.  Circular dependencies among initialization functions are also
  detected.  To break such loops, you can try dividing a single
  initialization function into early and late parts.  If you do this,
  pass the same identifing string as the 'extra' argument to each of
  startInitialization and endInitialization. [QUESTION: do you mean
  the same string in a single initialize function, but different
  strings in each initialize function, or the same string in both
  initialize functions? Guess: the former. [bruce 070702]]

  If you wish your initialization code to be rerun, you can call
  forgetInitialization, which will cause startInitialization with the
  same arguments to return False on its next call.

  Note that nothing in this module calls initialization functions in
  the first place, or helps determine when to call them. You must add
  at least one call to each one to an appropriate place in the code,
  and you are on your own to make sure it is called before its side
  effects were first needed, but not too early to work or be legal.
  (One way is to call it before every attempt to rely on its side
  effects, but this might be inefficient.)

  @author: Eric Messick
  @version: $Id$
  @copyright: 2007 Nanorex, Inc.
  @license: GPL
"""

_RUNNING = "Running"
"Constant for storing in _ms_initializationStatus"

_ms_initializationStatus = {}
"""
Dictionary mapping name+extra to the state of the given function.

Takes on one of three values::

  True:     Function has already completed.
  _RUNNING: Function is currently running.
  False:    Function has not started.

Note that a missing key means the same as False.
"""

_VERBOSE = False

import exceptions

class _InitializationLoop(exceptions.Exception):
    def __init__(self, args):
        self.args = args

def startInitialization(name, extra=""):
    """
    Called at the beginning of each initialization function.

    @param name: which module is being initialized (pass __name__).
    @type name: string

    @param extra: optional.  which function in this module.
    @type extra: string

    @return: True if this function is either running or completed.

    """
    key = name + extra
    currentState = False
    if (_ms_initializationStatus.has_key(key)):
        currentState = _ms_initializationStatus[key]
    if (currentState):
        if (currentState is _RUNNING):
            raise _InitializationLoop, key
        if (_VERBOSE):
            print "initialize recalled: " + key
        return True
    _ms_initializationStatus[key] = _RUNNING
    if (_VERBOSE):
        print "initializing " + key
    return False

def endInitialization(name, extra=""):
    """
    Called at the end of each initialization function.

    @param name: which module is being initialized (pass __name__).
    @type name: string

    @param extra: optional.  which function in this module.
    @type extra: string

    """
    key = name + extra
    if (_VERBOSE):
        print "done initializing: " + key
    _ms_initializationStatus[key] = True

def forgetInitialization(name, extra=""):
    """
    Called to allow an initialization function to run again.

    @param name: which module is being initialized (pass __name__).
    @type name: string

    @param extra: optional.  which function in this module.
    @type extra: string

    """
    key = name + extra
    _ms_initializationStatus[key] = False

