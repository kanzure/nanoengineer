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

def raytrace_scene_using_povray(assy, povray_ini):
    '''Render the POV-Ray scene file <pov_scene> using the <povray_ini> file.
    
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
        program = "\""+povray_exe+"\"" # Double quotes needed by Windows. Mark 060602.
            # POV-Ray (pvengine.exe) or MegaPOV (mpengine.exe) both work.
    else:
        program = povray_exe # Double quotes not needed for Linux/MacOS.
    
    # Later we'll cd to the POV-Ray's INI file directory and use tmp_ini in the POV-Ray command-line.
    # This helps us get around POV-Ray's I/O Restrictions. Mark 060529.
    workdir, tmp_ini = os.path.split(povray_ini)
    
    # Render scene.
    try:
        
        args = [program] + [tmp_ini]
        print "Launching POV-Ray: \n  working directory=",workdir,"\n  povray_exe=", povray_exe,  "\n  args are %r" % (args,)
        
        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)
    
        p = QProcess()
        p.setArguments(arguments)
        
        wd = QDir(workdir)
        p.setWorkingDirectory(wd) # This gets us around POV-Ray's 'I/O Restrictions' feature.

        p.start()

    except:
        from debug import print_compact_traceback
        print_compact_traceback( "exception in raytrace_scene_using_povray(): " )
        return 6, errmsgs[5]
            
    return 0, ''
    
def write_povray_ini_file(povray_ini_fname, povray_scene, width, height, output_type='png'):
    '''Write <povray_ini> file. The output image is placed next to the <povray_scene> file
    with the extension based on <output_type>.
    <width>, <height> are the width and height of the rendered image. (int)
    <output_type> is the extension of the output image (currently only 'png' and 'bmp' are supported).
    '''
    
    f = open(povray_ini_fname,'w') # Open POV-Ray INI file.
    
    if output_type == 'bmp':
        output_ext = '.bmp'
        output_imagetype = 'S' # 'S' = System-specific such as Mac Pict or Windows BMP
    else: # default
        output_ext = '.png'
        output_imagetype = 'N' # 'N' = PNG (portable network graphics) format
      
    #exit = "/EXIT" 
        # This commandline switch is available for Windows only. It causes the POV-Ray GUI to exit as 
        # soon as it finished rendering the image. The problem with this is that the POV-Ray GUI still  
        # "pops-up", then exits; the image window exits, too. Mark 060529.
    
    # This is needed if the POV-Ray plug-in is 'megapov.exe'. Mark 060609.
    povray_bin, povray_exe = os.path.split(env.prefs[povray_path_prefs_key])
    povray_dir, bin = os.path.split(povray_bin)
    if povray_exe == 'megapov.exe':
        # Needed when program='megapov.exe', but not pvengine.exe or mgengine.exe. 
        # megapov.exe provides a way to render a scene without invoking the POV-Ray GUI on Windows.
        # megapov.exe may be the way to go on Windows when someone figures out how to direct output
        # to the GLPane or a separate window. Mark 060529.
        povray_libpath  = os.path.normpath(os.path.join(povray_dir, "include"))
    else:
        povray_libpath = None
    
    workdir, tmp_pov = os.path.split(povray_scene)
    base, ext = os.path.splitext(tmp_pov)
    tmp_out = base + output_ext

    f.write ('; POV-Ray INI file generated by NanoEngineer-1\n')
    f.write ('Input_File_Name="%s"\n' % tmp_pov)
    f.write ('Output_File_Name="%s"\n' % tmp_out)
    if povray_libpath: f.write ('Library_Path="%s"\n' % povray_libpath) #'megapov.exe' only.
    f.write ('+W%d +H%d\n' % (width, height))
    f.write ('+A\n')
    f.write ('+F%s\n' % output_imagetype)
    f.write ('; End\n')
    
    f.close()
    
def get_raytrace_scene_filenames(assy, basename):
    '''Given <assy> and <basename>, returns a POV-Ray .ini and a .pov pathname.
    The caller can use these to write a POV-Ray INI file and the POV-Ray Scene file.
    For example, get_raytrace_scene_filename("POV-Ray Scene-1") returns
    './Partname Files/POV-Ray Files/POV-Ray Scene-1.pov' as the .pov path.
    '''
    if basename:
        r, povray_dir = find_or_make_povray_subdir(assy)
        if r:
            # There was a problem. povray_dir contains a description the problem.
            return None, povray_dir
        ini_filename = "NanoEngineer-1_raytrace_scene.ini"
            # Critically important: The INI filename cannot have any whitespace characters. Mark 060602.
        povray_ini = os.path.normpath(os.path.join(povray_dir, ini_filename))
        povray_scene = os.path.normpath(os.path.join(povray_dir,str(basename)))
        print "get_raytrace_scene_filenames():\n  povray_ini=", povray_ini,"\n  povray_scene=",povray_scene
        return povray_ini, povray_scene
    else:
        return None, "No POV-Ray name supplied."

def find_or_make_povray_subdir(assy):
    """Find or make the "POV-Ray files" subdirectory under the part files directory.
    Returns the full path of the "POV-Ray files" directory whether it already exists or was made here.
    """
    from platform import find_or_make_partfiles_subdir
    r, partfiles_dir = find_or_make_partfiles_subdir(assy)
    
    if r: 
        # There was a problem. Return the errorcode and description of problem.
        return r, partfiles_dir
    
    povray_subdir  = os.path.join(partfiles_dir, "POV-Ray Scene Files")
    
    if os.path.isdir(povray_subdir):
        return 0, povray_subdir
    elif os.path.exists(povray_subdir):
        return 1, "%s exists, but it is not a directory" % povray_subdir
    else:
        try:
            os.mkdir(povray_subdir)
        except:
            return 1, "find_or_make_povray_subdir(): Cannot create directory %s" % povray_subdir

    return 0, povray_subdir
        
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
    #r = verify_program(env.prefs[povray_path_prefs_key], '-v', vstring)
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