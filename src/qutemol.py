# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
'''
qutemol.py provides routines to support QuteMol as a plug-in.

$Id$

History:

mark 2007-06-02 - Created file. Much of the plug-in checking code was copied from 
                  povray.py, written by Bruce.

'''
__author__ = "Mark"

import env, os, sys
from prefs_constants import qutemol_enabled_prefs_key, qutemol_path_prefs_key
from PyQt4.Qt import QString, QStringList, QProcess, QMessageBox
from debug import print_compact_traceback

# To do list: Mark 2007-06-02
# - write_atomstable()
# - writepdb() should write ATOM records for bondpoints.

# General plug-in helper functions. These should be put into Plugins.py. Mark 2007-06-02.
# I just tried to do this, but there was some type of import error due to 
# code in Plugins.py. I'll check with Bruce about this soon so I don't forget
# to move this code. Mark 2007-06-02

def _dialog_to_offer_plugin_prefs_fixup(caption, text):
    """Offer the user a chance to fix a plugin problem. 
    Return 0 if they accept (after letting them try), 
    1 if they decline.
    [private helper for _fix_plugin_problem]
    """
    
    win = env.mainwindow()

    ret = QMessageBox.warning(win, caption, text, 
        "&OK", "Cancel", "",
        0, 1 )
    if ret==0: # OK
        win.uprefs.showDialog('Plug-ins') # Show Preferences | Plug-in.
        return 0 # let caller figure out whether user fixed the problem
    elif ret==1: # Cancel
        return 1
    pass

def _fix_plugin_problem(plugin_name, errortext):
    """[private helper for check_plugin_prefs]
    """
    caption = "%s Problem" % plugin_name
    text = "Error: %s.\n" % (errortext,) + \
        "  Select OK to fix this now in the Plugins page of\n" \
        "the Preferences dialog and retry rendering, or Cancel."
    return _dialog_to_offer_plugin_prefs_fixup(caption, text)

def _check_plugin_prefs_0(plugin_name, plugin_prefs_keys):
    """Checks <plugin_name> to make sure it is enabled and 
    that its path points to a file.
    
    Returns :0, plugin path on success, or
             1 and an error message indicating the problem.
            
    Arguments:
    <plugin_name> - name of plug-in (i.e. QuteMol)
    <plugin_keys> - the plugin enable prefs key and path prefs key.
    [private helper for check_plugin_prefs]
    """

    plugin_enabled_prefs_key, plugin_path_prefs_key = plugin_prefs_keys
    
    if env.prefs[plugin_enabled_prefs_key]:
        plugin_path = env.prefs[plugin_path_prefs_key]
    else:
        return 1, "%s is not enabled" % plugin_name

    if not plugin_path:
        return 1, "%s plug-in executable path is empty" % plugin_name
    
    if not os.path.exists(plugin_path):
        return 1, "%s executable not found at specified path %s" % plugin_name, plugin_path

    ##e should check version of plugin, if we know how

    return 0, plugin_path

def check_plugin_prefs(plugin_name, plugin_prefs_keys, ask_for_help):
    """Checks <plugin_name> to make sure it is enabled and 
    that its path points to a file.
    
    Returns :0, plugin path on success, or
             1 and an error message indicating the problem.
            
    Arguments:
    <plugin_name> - name of plug-in (i.e. QuteMol, GAMESS, etc.)
    <plugin_keys> - the plugin enable prefs key and path prefs key.
    """
    
    # Make sure the other prefs settings are correct; if not, maybe repeat until user fixes them or gives up.
    while 1:
        errorcode, errortext_or_path = _check_plugin_prefs_0(plugin_name, plugin_prefs_keys)
        if errorcode:
            if not ask_for_help:
                return errorcode, errortext_or_path
            ret = _fix_plugin_problem(plugin_name, errortext_or_path)

            if ret==0: # Subroutine has shown Preferences | Plug-in.
                continue # repeat the checks, to figure out whether user fixed the problem
            elif ret==1: # User declined to try to fix it now
                return errorcode, errortext_or_path
        else:
            return 0, errortext_or_path
    pass # end of check_plugin_prefs


def verify_plugin_using_version_flag(plugin_path, version_flag, vstring):
    '''Verifies a plugin by running it with <version_flag> as the only 
    command line argument and matching the output to <vstring>.
    Returns 0 if there is a match.  Otherwise, returns 1
    
    This is only useful if the plug-in supports a version flag arguments.
    '''
    
    if not plugin_path:
        return 1
    
    if not os.path.exists(plugin_path):
        return 1
        
    args = [version_flag]
    
    from Process import Process
    
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
    
def launch_qutemol(pdb_file):
    """Try to launch QuteMol and load <pdb_file>.
       Returns (errorcode, errortext), where errorcode is one of the following: ###k
        0 = successful
        8 = QuteMol failed for an unknown reason.
    """
    
    exit = ""
    plugin_name = "QuteMol"
    plugin_prefs_keys = (qutemol_enabled_prefs_key, qutemol_path_prefs_key)
    
    #program_nickname = "QuteMol"
    #program = env.prefs[qutemol_path_prefs_key]
    
    ask_for_help = True # give user the chance to fix problems in the prefs dialog
    errorcode, errortext_or_path = check_plugin_prefs(plugin_name, plugin_prefs_keys, ask_for_help)
    if errorcode:
	return errorcode, errortext_or_path
    
    program_path = errortext_or_path
    
    workdir, junk_exe = os.path.split(program_path)
    
    # Start QuteMol.
    try:
        args = [pdb_file]
        if exit:
            args += [exit]
        if 1 or env.debug():
            print "debug: Launching", plugin_name, \
                  "\n  working directory=",workdir,"\n  program_path=", program_path,  "\n  args are %r" % (args,)
        
        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)
    
	from Process import Process
        p = Process()
	
	# QuteMol must run from the directory its executable lives. Otherwise, it 
	# has serious problems (but still runs). Mark 2007-06-02.
        p.setWorkingDirectory(QString(workdir))
	
	# Tried p.startDetached() so that QuteMol would be its own process and continue to live
	# even if NE1 exits. Unfortunately, setWorkingDirectory() doesn't work. Seems like
	# a Qt bug to me. Mark 2007-06-02
        p.start(program_path, arguments)
        
    except:
        print_compact_traceback( "exception in launch_qutemol(): " )
        return 8, "%s failed for an unknown reason." % plugin_name
    
    # set an appropriate exitcode and msg
    if p.exitStatus() == QProcess.NormalExit:
	exitcode = p.exitStatus()
	if not exitcode:
	    msg = plugin_name + " launched."
	else:
	    msg = plugin_name + " had exitcode %r" % exitcode
    else:
	exitcode = p.exitStatus()
	exitcode = -1
	msg = "Abnormal exit (or failure to launch)"
	
    if exitcode:
	return 8, "Error: " + msg # this breaks the convention of the other error returns
            
    return 0, plugin_name + " launched." # from launch_qutemol

def write_atomstable(part, filename):
    """Write the atoms table text file for QuteMol to use.
    <filename> - the atoms table text filename.
    
    The atoms table contains the following information:
    - atom name (symbol)
    - covalent radius
    - atom color (of the current element colors)
    """
    print "write_atomstable() not implemented yet. Atoms Table filename:", filename
    return 

def write_qutemol_files(part):
    '''Writes a copy of <part> to a temp pdb in the Nanorex temp directory.
    Also writes an atoms attribute files to the Nanorex temp directory.
    (The atoms attribute file is not implemented yet.)
    
    Returns the name of the temp pdb file, or None if no atoms are in <part>.
    '''
    
    # Is there a better way to get the number of atoms in <part>.? Mark 2007-06-02
    from GroupProp import Statistics
    stats = Statistics(part.tree) 
	
    if 0:
	stats.num_atoms = stats.natoms - stats.nsinglets
        print "write_qutemol_files(): natoms =", stats.natoms, \
	      "nsinglets =", stats.nsinglets, \
	      "num_atoms =", stats.num_atoms
    
    if not stats.natoms:
	# There are no atoms in the current part.
	# writepdb() will create an empty file, which causes QuteMol to crash at launch.
	# Mark 2007-06-02
	return None
    
    pdb_basename = "qutemol.pdb"
    atomstable_basename = "atomstable.txt"
    
    # Make tmp_inputfile filename (i.e. ~/Nanorex/temp/jigname_parms_info.inp)
    from platform import find_or_make_Nanorex_subdir
    tmpdir = find_or_make_Nanorex_subdir('temp')
    qutemol_pdb_file = os.path.join(tmpdir, pdb_basename)
    atomstable_file = os.path.join(tmpdir, atomstable_basename)
        
    # Write PDB and Atoms Table files.
    from files_pdb import writepdb
    writepdb(part, qutemol_pdb_file) # Always overwrites existing file.
    write_atomstable(part, atomstable_basename) # NIY
    
    return qutemol_pdb_file