# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
povray.py provides routines to support POV-Ray rendering in nE-1.

$Id$

History:

mark 060529 - Created file to support "View > Raytrace Scene".

'''
__author__ = "Mark"

from constants import *
import preferences, env
import os, sys
from qt import QApplication, QCursor, Qt, QStringList, QProcess, QDir

def raytrace_scene_using_povray(assy, pov, width, height, output_type="png"):
    '''Render the POV-Ray scene file <pov>. The output image is placed next to <pov> 
    with the extension based on <output_type>.
    <width>, <height> are the width and height of the rendered image. (int)
    <output_type> is the extension of the output image (currently only 'png' and 'bmp' are supported).
    
    Return values:
        0 = successful
        1 = POV-Ray plug-in not enabled
        2 = POV-Ray plug-in path is empty
        3 = POV-Ray plug-in path points to a file that does not exist
        4 = POV-Ray plug-in is not Version 3.6 or higher (not currently supported) - Mark 060529.
        5 = Unsupported output image format.
        6 = POV-Ray failed for some reason.
    '''
    
    errmsgs = ["Error: POV-Ray plug-in not enabled.",
                        "Error: POV-Ray Plug-in path is empty.",
                        "Error: POV-Ray plug-in path points to a file that does not exist.",
                        "Error: POV-Ray plug-in is not version 3.6",
                        "Error: Unsupported output image format: ",
                        "Error: POV-Ray failed."]
    
    # Validate that the POV-Ray plug-in is enabled.
    if not env.prefs[povray_enabled_prefs_key]:
        r = activate_povray_plugin(assy.w)
        if r:
            return 1, errmsgs[0] # POV-Ray plug-in not enabled.
        
    povray_exe = env.prefs[povray_path_prefs_key]
    if not povray_exe:
        return 2, errmsgs[1] # POV-Ray plug-in path is empty
            
    if not os.path.exists(env.prefs[povray_path_prefs_key]):
        return 3, errmsgs[2] # POV-Ray plug-in path points to a file that does not exist
            
    #r = verify_povray_program() # Not yet sure how to verify POV-Ray program. Mark 060529.
    #if r:
    #    return 4, errmsgs[3]  # POV-Ray plug-in is not Version 3.6

    if sys.platform == 'win32':
        program = "\""+povray_exe+"\"" # POV-Ray (pvengine.exe) or MegaPOV (mpengine.exe)
    else:
        program = povray_exe  # Are the extra quotes a Windows requirement?
    
    # POV-Ray has a special feature introduced in v3.5 called "I/O Restrictions" which attempts
    # to at least partially protect a machine running POV-Ray from having files read or written 
    # outside of a given set of directories. This is a problem since we want POV-Ray (*.pov) 
    # and image (*.png) files to be placed in $HOME/Nanorex/POV-Ray.
    #
    # There are at least three ways around POV-Ray's "I/O Restrictions" feature:
    #
    # 1. read/write files from/to the current directory (which is allowed), then move the files where 
    #    you want them.
    # 2. change dir (cd) to the working directory (i.e. $HOME/Nanorex/POV-Ray), start POV-Ray 
    #    and return to original directory.
    # 3. Create a POV-Ray "INI file" and have POV-Ray use it instead of command-line options. This
    #    is probably the best long-term solution, but I need to investigate it more. To learn more about
    #    this, search for "INI Files" in the POV-Ray Help Documentation.
    #
    # I went with option 2. Option 3 may be something to look into later.
    #
    # To learn more about this, search for "I/O Restrictions" in the POV-Ray Help Documentation.
    # Mark 060529.
    
    if output_type == 'png':
        output_ext = '.png'
        pov_commandline_filetype = 'N' # 'N' = PNG (portable network graphics) format
    elif output_type == 'bmp':
        output_ext = '.bmp'
        pov_commandline_filetype = 'S' # 'S' = System-specific such as Mac Pict or Windows BMP
    else:
        return 5, errmsgs[4] + output_type

    # tmp_pov and tmp_out are the basenames of the pov and image output file.
    # Later we'll cd to the pov file's directory and use these filenames in the POV-Ray command-line.
    # This helps us get around POV-Ray's I/O Restrictions. Mark 060529.
    workdir, tmp_pov = os.path.split(pov)
    base, ext = os.path.splitext(tmp_pov)
    tmp_out = base + output_ext
    
    # POV-Ray command-line options.
    input_fn = "Input_File_Name=\'%s\'" % tmp_pov
    output_fn = "Output_File_Name=\'%s\'" % tmp_out
    w = "+W%d" % width
    h = "+H%d" % height
    aa="+A"
    filetype = "+F%s" % pov_commandline_filetype
        
    # Other POV-Ray command-line options (currently not used):
    lib = "+L\'C:/Program Files/POV-Ray for Windows v3.6/include\'" 
        # Needed when program='megapov.exe', but not pvengine.exe or mgengine.exe. 
        # megapov.exe provides a way to render a scene without invoking the POV-Ray GUI on Windows.
        # megapov.exe may be the way to go on Windows when I figure out how to direct output
        # to the GLPane or a separate window. Mark 060529.
    exit = "/EXIT" 
        # This switch is available for Windows only. It causes the POV-Ray GUI to exit as soon as it finished
        # rendering the image. The problem with this is that the picture exits, too. Mark 060529.
    
    # Render scene.
    try:
        
        args = [program] + [input_fn] + [output_fn] + [w] + [h] + [aa] + [filetype]
        print "Launching POV-Ray: \n  povray_exe=", povray_exe,  "\n  args are %r" % (args,)
        env.history.message('Writing ' + os.path.join(workdir, tmp_out))
        
        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)
    
        p = QProcess()
        p.setArguments(arguments)

        wd = QDir(workdir)
        p.setWorkingDirectory(wd) # This gets us around POV-Ray's 'I/O Restrictions' feature.
        
        #QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) ) # For later.
        p.start()

    except:
        from debug import print_compact_traceback
        print_compact_traceback( "exception in raytrace_scene_using_povray(): " )
        return 6, errmsgs[5]
    
    # QApplication.restoreOverrideCursor() # Restore the cursor. Later.
            
    return 0, ''
        
def get_raytrace_scene_filename(basename):
    '''Given <basename>, return a .pov pathname that the caller can use to write a pov file.
    For example, get_raytrace_scene_filename("raytrace_scene") ==> ('~/Nanorex/POV-Ray/raytrace_scene.pov').
    '''
    if basename:
        from platform import find_or_make_Nanorex_subdir
        povray_dir = find_or_make_Nanorex_subdir("POV-Ray")
        pov = os.path.normpath(os.path.join(povray_dir,str(basename)+".pov"))
        return pov
    else:
        return None
        
def activate_povray_plugin(win):
    '''Opens a message box informing the user that the POV-Ray plugin
    needs to be enabled and asking if they wish to do so.
    win is the main window object.
    '''

    from qt import QMessageBox
    ret = QMessageBox.warning( win, "Activate POV-Ray Plug-in",
        "POV-Ray plug-in not enabled. Please select <b>OK</b> to \n" \
        "activate the POV-Ray plug-in from the Preferences dialog.",
        "&OK", "Cancel", None,
        0, 1 )
            
    if ret==0: # OK
        win.uprefs.showDialog('Plug-ins') # Show Prefences | Plug-in.
        if not env.prefs[povray_enabled_prefs_key]:
            return 1 # POV-Ray was not enabled by user.
        
    elif ret==1: # Cancel
        return 1

    return 0

def verify_povray_program():
    '''Returns 0 if povray_path_prefs_key is the path to the POV-Ray 3.6 executable.
    Otherwise, returns 1. 
    Always return 0 for now until I figure out a way to verify POV-Ray. Mark 060527.
    '''
    vstring = "POV-Ray 3.6" # or somthing like this.os
    #r = verify_program(env.prefs[nanohive_path_prefs_key], '-v', vstring)
    #return r
    return 0

# This should probably be moved to somewhere else like prefs_constants.py 
# (to set the default value of povray_path_prefs_key) or platform.py.
# Same thing needs to be done for Nano-Hive and GAMESS.
# Talk to Bruce about pros/cons of this.  Mark 060529.
def get_default_povray_path():
    '''Returns the POV-Ray (executable) path to the standard location for each platform, 
    if it exists. Otherwise, return an empty string.
    '''
    if sys.platform == "win32": # Windows
        povray_path = "C:\\Program Files\\POV-Ray for Windows v3.6\\bin\\pvengine.exe"
    elif sys.platform == "darwin": # MacOS
        povray_path = "/usr/local/bin/pvengine"
    else: # Linux
        povray_path = "/usr/local/bin/pvengine"
    if not os.path.exists(povray_path):
        return ""
    return povray_path
