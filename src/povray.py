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
import os, sys, shutil

def raytrace_scene_using_povray(assy, pov, png, width, height):
    '''Render the POV-Ray scene file <pov> and place the results in <png>.
    <width>, <height> are the width and height of the rendered image. (int)
    
    Return values:
        0 = successful
        1 = POV-Ray plug-in not enabled
        2 = POV-Ray plug-in path is empty
        3 = POV-Ray plug-in path points to a file that does not exist
        4 = POV-Ray plug-in is not Version 1.2b
        5 = POV-Ray failed for some reason.
    '''
    
    # Validate that the POV-Ray plug-in is enabled.
    if not env.prefs[povray_enabled_prefs_key]:
        r = activate_povray_plugin(assy.w)
        if r:
            return 1 # Nano-Hive plug-in not enabled.
        
    povray_exe = env.prefs[povray_path_prefs_key]   
    if not povray_exe:
        return 2 # POV-Ray plug-in path is empty
            
    if not os.path.exists(env.prefs[nanohive_path_prefs_key]):
        return 3 # POV-Ray plug-in path points to a file that does not exist
            
    #r = verify_povray_program() # Not yet sure how to verify POV-Ray program. Mark 060529.
    #if r:
    #    return 4 # POV-Ray plug-in is not Version 3.6
    
    program = "\""+povray_exe+"\"" # POV-Ray (pvengine.exe) or MegaPOV (mpengine.exe)
    
    # POV-Ray has a special feature introduced in v3.5 called "I/O Restrictions" which attempts
    # to at least partially protect a machine running POV-Ray from having files read or written 
    # outside of a given set of directories. This is a problem since we want all the POV-Ray (*.pov) 
    # and image (*.png) files to be placed in $HOME/Nanorex/POV-Ray.
    #
    # There are at least three ways around POV-Ray's "I/O Restrictions" feature:
    #
    # 1. read/write files from/to the current directory (which is allowed), then move the files where 
    #    you want them.
    # 2. change dir (cd) to a special directory (i.e. $HOME/Nanorex/POV-Ray), run POV-Ray, 
    #    and return to original directory.
    # 3. Create a POV-Ray "INI file" and have POV-Ray use it instead of command-line options. This
    #    is probably the best long-term solution, but I need to investigate it more. To learn more about
    #    this, search for "INI Files" in the POV-Ray Help Documentation.
    #
    # I went with option 1 since it seemed reasonable and the easiest thing to do for now.
    #
    # To learn more about this, search for "I/O Restrictions" in the POV-Ray Help Documentation.
    # Mark 060529.

    # tmp_pov and tmp_png get us around POV-Ray's  I/O Restrictions. After POV-Ray finishes, we can move these
    # files to the destination directory $HOME/Nanorex/POV-Ray. Mark 060529.
    tmp_pov = "nanoENGINEER-1_raytrace_scene.pov" 
    tmp_png = "nanoENGINEER-1_raytrace_scene.png"
    
    # POV-Ray command-line options.
    input_fn = "Input_File_Name=\'%s\'" % tmp_pov
    output_fn = "Output_File_Name=\'%s\'" % tmp_png
    w = "+W%d" % width
    h = "+H%d" % height
    aa="+A"
    filetype = "+FN" # 'N' = PNG (portable network graphics) format
        
    # Other POV-Ray command-line options:
    lib = "+L\'C:/Program Files/POV-Ray for Windows v3.6/include\'" 
        # Needed when program='megapov.exe', but not pvengine.exe or mgengine.exe. 
        # megapov.exe provides a way to render a scene without invoking the POV-Ray GUI on Windows.
        # megapov.exe may be the way to go on Windows when I figure out how to direct output
        # to the GLPane or a separate window. Mark 060529.
    exit = "/EXIT" 
        # This switch is available for Windows only. It causes the POV-Ray GUI to exist as soon as it finished
        # rendering the image. The problem with this is that the picture exits, too. Mark 060529.

    # Move POV-Ray scene file to the current directory (of the nE-1 process). We do this 
    # to get around the POV-Ray I/O Restrictions feature (see details above). Mark 060529.
    if os.path.exists(pov):
        try:
            if os.path.exists(tmp_pov):
                os.unlink(tmp_pov)
            shutil.move(pov, tmp_pov)
        except (IOError, os.error), why:
            print "Can't move %s to %s: %s" % (pov, tmp_pov, str(why))
    
    # Render scene.
    try:
        if 1:# Use os.spawnv().
            args = [program] + [input_fn] + [output_fn] + [w] + [h] + [aa] + [filetype]
            print "Spawning POV-Ray: \n  povray_exe=", povray_exe,  "\n  spawnv args are %r" % (args,)
            kid = os.spawnv(os.P_NOWAIT, povray_exe, args)
        
        else: # Use os.system().
            # The reason I don't like it is because it blocks nE-1 until it exits. Mark 060527.
            povray_cmdline = "%s %s %s %s %s %s %s" % (program, infile, outfile, w, h, aa, filetype)
            print "POV-Ray Command-line: ", povray_cmdline
            os.system(povray_cmdline)

    except:
        from debug import print_compact_traceback
        print_compact_traceback( "exception in raytrace_scene_using_povray(): " )
        r = 5
        
    # Move the two files. This is NIY since "View > Raytrace Scene" is simply a way to preview
    # the current scene. "Insert > POV-Ray Image" will be a new action that keeps the POV/PNG file(s)
    # and inserts a node in the model tree representing them. This will be implemented later. 
    # Mark 060529.
    if 0:
        if os.path.exists(pov):
            os.unlink(pov)
        shutil.move(tmp_pov, pov)
        
        if os.path.exists(png):
            os.unlink(png)
        shutil.move(tmp_png, png)
            
    return
        
def get_tmp_povray_filenames(basename):
    '''Return a tuple of full pathnames to be used as POV-Ray arguments:
        - a POV-Ray input filename
        - a PNG output filename
    '''
    if basename:
        from platform import find_or_make_Nanorex_subdir
        nhdir = find_or_make_Nanorex_subdir("POV-Ray")
        pov = os.path.normpath(os.path.join(nhdir,str(basename)+".pov"))
        png = os.path.normpath(os.path.join(nhdir,str(basename)+".png"))
        #print "get_tmp_povray_filename(): \n  pov = ", pov,"\n  png = ",png
        return pov, png
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