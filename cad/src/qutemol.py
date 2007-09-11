# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
qutemol.py provides routines to support QuteMol as a plug-in.

$Id$

History:

mark 2007-06-02
- Created file. Much of the plug-in checking code was copied from 
povray.py, written by Bruce.
"""
__author__ = "Mark"

import env, os, sys
from prefs_constants import qutemol_enabled_prefs_key, qutemol_path_prefs_key
from PyQt4.Qt import QString, QStringList, QProcess, QMessageBox
from debug import print_compact_traceback
from debug_prefs import debug_pref, Choice_boolean_True
from constants import properDisplayNames, TubeRadius, diBALL_SigmaBondRadius

# To do list: Mark 2007-06-03
# - Move plug-in routines to Plugins.py.

# General plug-in helper functions. These should be put into Plugins.py. Mark 2007-06-02.
# I just tried to do this, but there was some type of import error due to 
# code in Plugins.py. I'll check with Bruce about this soon so I don't forget
# to move this code. Mark 2007-06-02

def _dialog_to_offer_plugin_prefs_fixup(caption, text):
    """
    Offer the user a chance to fix a plugin problem. 
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
    """
    [private helper for check_plugin_prefs]
    """
    caption = "%s Problem" % plugin_name
    text = "Error: %s.\n" % (errortext,) + \
        "  Select OK to fix this now in the Plugins page of\n" \
        "the Preferences dialog and retry rendering, or Cancel."
    return _dialog_to_offer_plugin_prefs_fixup(caption, text)

def _check_plugin_prefs_0(plugin_name, plugin_prefs_keys):
    """
    Checks <plugin_name> to make sure it is enabled and 
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
    """
    Checks <plugin_name> to make sure it is enabled and 
    that its path points to a file.
    
    Returns :0, plugin path on success, or
             1 and an error message indicating the problem.
            
    Arguments:
    <plugin_name> - name of plug-in (i.e. QuteMol, GAMESS, etc.)
    <plugin_keys> - the plugin enable prefs key and path prefs key.
    """
    
    # Make sure the other prefs settings are correct; if not, maybe repeat
    # until user fixes them or gives up.
    while 1:
        errorcode, errortext_or_path = \
                 _check_plugin_prefs_0(plugin_name, plugin_prefs_keys)
        if errorcode:
            if not ask_for_help:
                return errorcode, errortext_or_path
            ret = _fix_plugin_problem(plugin_name, errortext_or_path)

            if ret==0: # Subroutine has shown Preferences | Plug-in.
                continue # repeat the checks, to figure out whether user fixed
                         # the problem.
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

# Everything above this line should be moved to Plugins.py (or another file).
# Mark 2007-06-03

def launch_qutemol(pdb_file, art_file):
    """
    Try to launch QuteMol and load <pdb_file>.
    <art_file> is the ART file pathname, supplied as a command line 
    argument to QuteMol. Only QuteMol version 0.4.1 or later can read the
    ART file.
    
    Returns (errorcode, errortext), where errorcode is one of the following: ###k
    0 = successful
    8 = QuteMol failed for an unknown reason.
    """
    
    plugin_name = "QuteMol"
    plugin_prefs_keys = (qutemol_enabled_prefs_key, qutemol_path_prefs_key)
        
    ask_for_help = True # give user the chance to fix problems 
                        # in the prefs dialog
    errorcode, errortext_or_path = \
             check_plugin_prefs(plugin_name, plugin_prefs_keys, ask_for_help)
    if errorcode:
        return errorcode, errortext_or_path
    
    program_path = errortext_or_path
    
    workdir, junk_exe = os.path.split(program_path)
    
    # This provides a way to tell NE1 which version of QuteMol is installed.
    if debug_pref("QuteMol 0.4.1 or later", 
                  Choice_boolean_True, 
                  prefs_key = True):
        version = "0.4.1"
    else:
        version = "0.4.0"
    
    # Start QuteMol.
    try:
        if version == "0.4.1":
            args = [pdb_file, "-a", art_file]
        else:
            args = [pdb_file]
        if env.debug():
            print "Debug: Launching", plugin_name, \
                  "\n  working directory=", workdir, \
                  "\n  program_path=", program_path,  \
                  "\n  args are %r" % (args,)
        
        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)
    
        from Process import Process
        p = Process()
        
        # QuteMol must run from the directory its executable lives. Otherwise,  
        # it has serious problems (but still runs). Mark 2007-06-02.
        p.setWorkingDirectory(QString(workdir))
        
        # Tried p.startDetached() so that QuteMol would be its own process and 
        # continue to live even if NE1 exits. Unfortunately, 
        # setWorkingDirectory() doesn't work. Seems like a Qt bug to me. 
        # Mark 2007-06-02
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
        return 8, "Error: " + msg 
        # this breaks the convention of the other error returns
            
    return 0, plugin_name + " launched." # from launch_qutemol


def write_art_file(filename):
    """
    Writes the Atom Rendering Table (ART) file, which contains all
    the atom rendering properties needed by QuteMol.
    Each atom is on a separate line.
    Lines starting with '#' are comment lines.
    <filename> - ART filename
    """
    assert type(filename) == type(" ")
    
    from elements import PeriodicTable
    elemTable = PeriodicTable.getAllElements()
    
    try:
        f = open(filename, "w")
    except:
        print "Exception occurred to open file %s to write: " % filename
        return None
    
    # QuteMol can use line 1 to validate the file format.
    # Added @ to help make it clear that line 1 is special.
    f.write("#@ NanoEngineer-1 Atom Rendering Table, \
            file format version 2007-06-04\n")
    # Lines after line 1 are only comments.
    f.write("#\n# File format:\n#\n")
    f.write("# Atom   NE1    Render Covlnt\n")
    f.write("# Symbol Number Radius Radius Red Green Blue\n")
    
    from prefs_constants import cpkScaleFactor_prefs_key
    cpk_sf = env.prefs[cpkScaleFactor_prefs_key] # Mark 2007-06-03
    
    for eleNum, elm in elemTable.items():
        col = elm.color
        r = int(col[0] * 255 + 0.5)
        g = int(col[1] * 255 + 0.5)
        b = int(col[2] * 255 + 0.5)
        
        f.write('%2s  %3d  %3.3f  %3.3f  %3d  %3d  %3d\n' % \
            (elm.symbol, eleNum, elm.rvdw * cpk_sf, 
             elm.atomtypes[0].rcovalent, 
             r, g, b)
            )
    
    f.write("# All Render Radii were calculated using a CPK scaling factor\n"\
            "# that can be modified by the user in \"Preference | Atoms\".\n"\
            "# CPK Scale Factor: %2.3f\n"\
            "# To computer the original VDW radii, use the formula:\n"\
            "# VDW Radius = Render Radius / CPK Scale Factor\n"\
             % cpk_sf)
    
    f.close()

    return 

def write_qutemol_pdb_file(part, filename):
    """
    Writes an NE1-QuteMol PDB file of <part> to <filename>. 
    """
    
    f = open(filename, "w")
    
    from prefs_constants import backgroundGradient_prefs_key
    from prefs_constants import backgroundColor_prefs_key
    from prefs_constants import diBALL_BondCylinderRadius_prefs_key
    
    skyBlue = env.prefs[ backgroundGradient_prefs_key ]
        
    bgcolor = env.prefs[ backgroundColor_prefs_key ]
    r = int (bgcolor[0] * 255 + 0.5)
    g = int (bgcolor[1] * 255 + 0.5)
    b = int (bgcolor[2] * 255 + 0.5)
    
    TubBond1Radius = TubeRadius
    BASBond1Radius = \
                   diBALL_SigmaBondRadius * \
                   env.prefs[diBALL_BondCylinderRadius_prefs_key]
    
    # Write the QuteMol REMARKS "header".
    # See the following wiki page for more information about
    # the format of all NE1-QuteMol REMARK records:
    # http://www.nanoengineer-1.net/mediawiki/index.php?title=NE1-QuteMol_PDB_REMARK_record_format

    f.write("REMARK   1 @ NanoEngineer-1/QuteMol PDB File Format\n")
    f.write("REMARK   2 @ Version 2007-07-01 required; 2007-07-01 preferred\n")
    f.write("REMARK   3 Csys=%1.6f %1.6f %1.6f %1.6f\n" 
            % (part.o.quat.w, part.o.quat.x, part.o.quat.y, part.o.quat.z))
    f.write("REMARK   4 Scale=%4.6f\n" 
            % part.o.scale)
    f.write("REMARK   5 POV=%6.6f %6.6f %6.6f\n" 
            % (part.o.pov[0], part.o.pov[1], part.o.pov[2]))
    f.write("REMARK   6 Zoom=%6.6f\n" 
            % part.o.zoomFactor)
    if skyBlue:
        f.write("REMARK   7 BGColor=SkyBlue\n")
    else:
        f.write("REMARK   7 BGColor=%3d,%3d,%3d\n" 
            % (r, g, b))
    f.write("REMARK   8 LaunchDisplay=%s\n" 
            % properDisplayNames[part.o.displayMode])
    f.write("REMARK   9 TubBond1Radius=%1.3f Angstroms\n" 
            % TubBond1Radius)
    f.write("REMARK  10 BASBond1Radius=%1.3f Angstroms\n"
            % BASBond1Radius)

    # Now write the REMARK records for each chunk (MOL) in the part.
    
    molNum = 1
    remarkIndex = 20
    
    for mol in part.molecules:        
        f.write("REMARK %3d MOL%s " % (remarkIndex, molNum))
        f.write("Display=%s " % properDisplayNames[mol.display])
        if mol.color:
            r = int (mol.color[0] * 255 + 0.5)
            g = int (mol.color[1] * 255 + 0.5)
            b = int (mol.color[2] * 255 + 0.5)
            f.write("Color=%3d,%3d,%3d " % (r, g, b))
        f.write("Name=\"%s\"\n" % mol.name)
        
        molNum+=1
        remarkIndex += 1
        
        if remarkIndex > 999:
            remarkIndex = 20
        
    f.close()
    
    # Write the "body" of PDB file.
    from files_pdb import writepdb, EXCLUDEHIDDENATOMS
    # Bondpoints are written to file. Mark 2007-06-11
    writepdb(part, filename, mode='a', excludeFlags=EXCLUDEHIDDENATOMS)
    
    
def write_qutemol_files(part):
    """
    Writes a PDB of the current <part> and an ART file to the Nanorex temp 
    directory.
    ART = Atom Rendering Table
    Returns the name of the temp pdb file, or None if no atoms are in <part>.
    """
    
    # Is there a better way to get the number of atoms in <part>.? 
    # Mark 2007-06-02
    from GroupProp import Statistics
    stats = Statistics(part.tree) 
        
    if 0:
        stats.num_atoms = stats.natoms - stats.nsinglets
        print "write_qutemol_files(): natoms =", stats.natoms, \
              "nsinglets =", stats.nsinglets, \
              "num_atoms =", stats.num_atoms
    
    if not stats.natoms:
        # There are no atoms in the current part.
        # writepdb() will create an empty file, which causes 
        # QuteMol to crash at launch.
        # Mark 2007-06-02
        return None
    
    pdb_basename = "qutemol.pdb"
    art_basename = "art.txt" # ART = Atom Rendering Table
    
    # Make full pathnames for PDB and ART files (in ~/Nanorex/temp/)
    from PlatformDependent import find_or_make_Nanorex_subdir
    tmpdir = find_or_make_Nanorex_subdir('temp')
    qutemol_pdb_file = os.path.join(tmpdir, pdb_basename)
    art_file = os.path.join(tmpdir, art_basename)
    
    # Write PDB and ART files.
    write_qutemol_pdb_file(part, qutemol_pdb_file)
    write_art_file(art_file)
    
    return qutemol_pdb_file, art_file
