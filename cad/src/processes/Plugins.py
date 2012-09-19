# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Plugins.py - a collection of general plugin helper functions for the purpose of
checking and/or verifying that a plugin is enabled and that the path pointed
to by its pref_key is the plugin.

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

mark 2007-12-01
- split out of qutemol.py

Module classification:  [bruce 071215, 080104]

Contains ui, operations or utility, and io code.
For now, classified as code type of ui, somewhat arbitrarily,
but filed into "processes" package, since it's all about letting
the user maintain info needed to run external processes.
"""

import foundation.env as env
import os
from PyQt4.Qt import QMessageBox
from processes.Process import Process

def _dialogToOfferPluginPrefsFixup(caption, text):
    """
    [private helper for _fixPluginProblem()]

    Offer the user a chance to fix a plugin problem.

    @param caption: The dialog border caption.
    @type  caption: text

    @param text: The dialog text.
    @type  text: text

    @return: 0 if they accept (after letting them try),
             1 if they decline.
    @rtype: int
    """

    win = env.mainwindow()

    ret = QMessageBox.warning(win, caption, text,
        "&OK", "Cancel", "",
        0, 1 )
    if ret == 0: # User clicked "OK"
        win.userPrefs.show(pagename = 'Plug-ins') # Show Preferences | Plug-in.
        return 0 # let caller figure out whether user fixed the problem
    elif ret == 1: # User clicked "Cancel"
        return 1
    pass

def _fixPluginProblem(plugin_name, errortext):
    """
    [private helper for checkPluginPreferences()]

    @param plugin_name: name of plug-in (i.e. "QuteMolX", "GROMACS", etc.)
    @type  plugin_name: text
    """
    caption = "%s Problem" % plugin_name
    text = "Error: %s.\n" % (errortext,) + \
        "  Select OK to fix this now in the Plugins page of\n" \
        "the Preferences dialog and retry rendering, or Cancel."
    return _dialogToOfferPluginPrefsFixup(caption, text)

def verifyExecutable(executable_path):
    if (os.access(executable_path, os.F_OK)):
        if (os.access(executable_path, os.X_OK)):
            return None
        return "%s exists, but is not executable" % executable_path
    return "%s: file does not exist" % executable_path

def _checkPluginPreferences_0(plugin_name,
                              plugin_prefs_keys,
                              insure_executable):
    """
    [private helper for checkPluginPreferences()]

    Checks <plugin_name> to make sure it is enabled and
    that its path points to a file.

    @param plugin_name: name of plug-in (i.e. "QuteMolX", "GROMACS", etc.)
    @type  plugin_name: text

    @param plugin_keys: list containing the plugin enable prefs key and the
                        path prefs key.
    @type  plugin_keys: List

    @return: 0, plugin path on success, or
             1, an error message indicating the problem.
    @rtype:  List
    """

    plugin_enabled_prefs_key, plugin_path_prefs_key = plugin_prefs_keys

    if env.prefs[plugin_enabled_prefs_key]:
        plugin_path = env.prefs[plugin_path_prefs_key]
    else:
        return 1, "%s is not enabled" % plugin_name

    if not plugin_path:
        return 1, "%s plug-in executable path is empty" % plugin_name

    # We'd like to allow arguments to an executable to be specified,
    # but perhaps the executable path itself contains a space in it.
    # So, we break the string at each space and check the first part.
    # If any of those substrings exists, accept it.  We start by
    # checking the whole string.
    executable_path = plugin_path
    while (not os.path.exists(executable_path)):
        last_space = executable_path.rfind(" ")
        # some platform might report that the empty string file name
        # exists, so we don't want to check for it.
        if (last_space <= 0):
            return 1, "%s executable not found at specified path %s" % (plugin_name, plugin_path)
        executable_path = executable_path[0:last_space]

    if (insure_executable):
        message = verifyExecutable(executable_path)
        if (message):
            return 1, message

    ##e should check version of plugin, if we know how

    return 0, plugin_path

def checkPluginPreferences(plugin_name,
                           plugin_prefs_keys,
                           ask_for_help = True,
                           extra_check = None,
                           insure_executable = False):
    """
    Checks I{plugin_name} to make sure it is enabled and that its path points
    to a file. I{ask_for_help} can be set to B{False} if the user shouldn't be
    given a chance to fix the problem via the "Plugin" page in the Preferences
    dialog.

    Note:  this should be refactored to use exceptions.

    Returns :0, plugin path on success, or
             1 and an error message indicating the problem.

    @param plugin_name: name of plug-in (i.e. "QuteMolX", "GROMACS", etc.)
    @type  plugin_name: text

    @param plugin_keys: list containing the plugin enable prefs key and the
                        path prefs key.
    @type  plugin_keys: List

    @param ask_for_help: If True (default), give the user a chance to fix
                         problems via the "Plugin" page of the Preferences
                         dialog (i.e. enable the plugin and set the path to
                         its executable).
    @type  ask_for_help: bool

    @param extra_check: If not None (default is None), is a routine to
                        perform extra validation checks on the plugin
                        path.
    @type extra_check: Function which takes path as argument, and
                       returns either an error message, or None if all
                       is ok.

    @return: 0, plugin path on success, or
             1, an error message indicating the problem.
    @rtype:  List
    """

    # Make sure the other prefs settings are correct; if not, maybe repeat
    # until user fixes them or gives up.
    while 1:
        errorcode, errortext_or_path = \
                 _checkPluginPreferences_0(plugin_name,
                                           plugin_prefs_keys,
                                           insure_executable)
        if (extra_check and not errorcode):
            extra_message = extra_check(errortext_or_path)
            if (extra_message):
                errorcode = 1
                errortext_or_path = extra_message
        if errorcode:
            if not ask_for_help:
                return errorcode, errortext_or_path
            ret = _fixPluginProblem(plugin_name, errortext_or_path)

            if ret == 0: # Subroutine has shown Preferences | Plug-in.
                continue # repeat the checks, to figure out whether user fixed
                         # the problem.
            elif ret == 1: # User declined to try to fix it now
                return errorcode, errortext_or_path
        else:
            return 0, errortext_or_path
    pass # end of checkPluginPreferences


def verifyPluginUsingVersionFlag(plugin_path, version_flag, vstring):
    """
    Verifies a plugin by running it with I{version_flag} as the only
    command line argument and matching the output to I{vstring}.

    @return: 0 if there is a match.  Otherwise, returns 1
    @rtype:  int

    @note: This is only useful if the plug-in supports a version flag arguments.
    """

    if not plugin_path:
        return 1

    if not os.path.exists(plugin_path):
        return 1

    args = [version_flag]

    arguments = []
    for arg in args:
        if arg != "":
            arguments.append(arg)

    p = Process()
    p.start(plugin_path, arguments)

    if not p.waitForFinished (10000): # Wait for 10000 milliseconds = 10 seconds
        return 1

    output = 'Not vstring'

    output = str(p.readAllStandardOutput())

    #print "output=", output
    #print "vstring=", vstring

    if output.find(vstring) == -1:
        return 1
    else:
        return 0 # Match found.
