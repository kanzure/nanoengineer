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
from HistoryWidget import redmsg
from qt import QApplication, QCursor, Qt, QStringList, QProcess, QDir

def launch_povray_or_megapov(win, povray_ini):
    '''Launch POV-Ray or MegaPOV. POV-Ray must be installed to launch MegaPOV.
    POV-Ray does not run silently in the background on Windows, so we provide MegaPOV as
    an option since it does run silently in the background on Windows.
    <povray_ini> is a text file containing settings for what used to be called POV-Ray 'command-line options'.
    
    Return values:
        0 = successful
        1 = POV-Ray plug-in not enabled
        2 = POV-Ray plug-in path is empty
        3 = POV-Ray plug-in path points to a file that does not exist
        4 = POV-Ray plug-in is not Version 3.6 or higher (not currently supported) - Mark 060529.
        5 = MegaPOV plug-in not enabled
        6 = MegaPOV plug-in path is empty
        7 = MegaPOV plug-in path points to a file that does not exist
        8 = POV-Ray failed for some reason.
    '''
    
    errmsgs = ["Error: POV-Ray plug-in not enabled.",
                        "Error: POV-Ray Plug-in path is empty.",
                        "Error: POV-Ray plug-in path points to a file that does not exist.",
                        "Error: POV-Ray plug-in is not version 3.6",
                        "Error: MegaPOV plug-in not enabled.",
                        "Error: MegaPOV Plug-in path is empty.",
                        "Error: MegaPOV plug-in path points to a file that does not exist.",
                        "Error: Unsupported output image format: ",
                        "Error: POV-Ray failed."]
    
    # Validate that the POV-Ray plug-in is enabled.
    if not env.prefs[povray_enabled_prefs_key]:
        r = activate_plugin(win, "POV-Ray")
        if r:
            return 1, errmsgs[0] # POV-Ray plug-in not enabled.
        
    povray_exe = env.prefs[povray_path_prefs_key]   
    if not povray_exe:
        return 2, errmsgs[1] # POV-Ray plug-in path is empty
            
    if not os.path.exists(povray_exe):
        return 3, errmsgs[2] # POV-Ray plug-in path points to a file that does not exist
        
    raytracer = povray_exe
    
    #r = verify_povray_program() # Not yet sure how to verify POV-Ray program. Mark 060529.
    #if r:
    #    return 4, errmsgs[3]  # POV-Ray plug-in is not Version 3.6
    
    # Validate that the MegaPOV plug-in is enabled.
    #if not env.prefs[megapov_enabled_prefs_key]:
    #    r = activate_plugin(win, "MegaPOV")
    #    if r:
    #        return 5, errmsgs[4] # MegaPOV plug-in not enabled.
    
    megapov_exe = ''
    if env.prefs[megapov_enabled_prefs_key]:
        megapov_exe = env.prefs[megapov_path_prefs_key]   
        if not megapov_exe:
            return 6, errmsgs[5] # MegaPOV plug-in path is empty
            
        if not os.path.exists(megapov_exe):
            return 7, errmsgs[6] # MegaPOV plug-in path points to a file that does not exist
        
        raytracer = megapov_exe
    
    exit = ''
    if sys.platform == 'win32':
        program = "\""+raytracer+"\"" # Double quotes needed by Windows. Mark 060602.
	if raytracer == povray_exe:
	    exit = "/EXIT"
    else:
        program = raytracer # Double quotes not needed for Linux/MacOS.
    
    # Later we'll cd to the POV-Ray's INI file directory and use tmp_ini in the POV-Ray command-line.
    # This helps us get around POV-Ray's I/O Restrictions. Mark 060529.
    workdir, tmp_ini = os.path.split(povray_ini)
	
    # Render scene.
    try:
        
        args = [program] + [tmp_ini] + [exit]
        print "Launching POV-Ray: \n  working directory=",workdir,"\n  povray_exe=", povray_exe,  "\n  args are %r" % (args,)
        
        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)
    
        from Process import Process
        p = Process()
        p.setArguments(arguments)
        
        wd = QDir(workdir)
        p.setWorkingDirectory(wd) # This gets us around POV-Ray's 'I/O Restrictions' feature.

        p.start()
	        
        # Put up hourglass cursor to indicate we are busy. Restore the cursor below. Mark 060621.
	QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
	
	win.glpane.is_animating = True # This disables selection while rendering the image.
        
        import time
        msg = "Rendering image"
        while p.isRunning():
            # Display a message on the status bar that POV-Ray/MegaPOV is rendering.
            # I'd much rather display a progressbar and stop button by monitoring the size of the output file.
	    # This would require the output file to be written in PPM or BMP format, but not PNG format, since
	    # I don't believe a PNG's final filesize cannot be predicted. 
	    # Check out monitor_progress_by_file_growth() in runSim.py, which does this.
            time.sleep(0.25)
            env.history.statusbar_msg(msg)
            env.call_qApp_processEvents()
	    if 1:
		# Update the statusbar message while rendering.
		if len(msg) > 100:
		    msg = "Rendering image"
		else:
		    #msg = msg + "."
		    msg += "."
        
        QApplication.restoreOverrideCursor() # Restore the cursor. Mark 060621.
        env.history.statusbar_msg("Rendering finished!")
	win.glpane.is_animating = False
        
        # Display image in separate window here.

    except:
	QApplication.restoreOverrideCursor()
	win.glpane.is_animating = False
        from debug import print_compact_traceback
        print_compact_traceback( "exception in launch_povray_or_megapov(): " )
        return 8, errmsgs[7]
            
    return 0, "Rendering finished"

# Should write_povray_ini_file() become a method of PovrayScene. I think so, but ask Bruce. Mark 060626. 
def write_povray_ini_file(povray_ini_fname, povrayscene_file, width, height, output_type='png'):
    '''Write <povray_ini> file. The output image is placed next to the <povrayscene_file> file
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

    try:
        # If MegaPOV is enabled, the Library_Path option must be added and set to the POV-Ray/include
        # directory in the INI. This is so MegaPOV can find the include file "transform.inc". Mark 060628.
        # Povray also needs transforms.inc - wware 060707
        if sys.platform == 'win32':  # Windows
            povray_bin, povray_exe = os.path.split(env.prefs[povray_path_prefs_key])
            povray_dir, bin = os.path.split(povray_bin)
            povray_libpath = os.path.normpath(os.path.join(povray_dir, "include"))
        elif sys.platform == 'darwin':  # Mac
            raise Exception("Povray for the Mac is confusing because it doesn't appear to have a " +
                            "command-line interface as it does on Windows and Linux")
            # We should be figuring out povray_libpath here, if possible.
        else:  # Linux
            povray_bin = env.prefs[povray_path_prefs_key]
            if povray_bin == "":
                raise Exception("Please set your Povray path in Edit->Preferences->Plug-ins")
            povray_bin = env.prefs[povray_path_prefs_key].split(os.path.sep)
            try:
                assert povray_bin[-2] == 'bin' and povray_bin[-1] == 'povray'
                povray_libpath = os.path.sep.join(povray_bin[:-2] + ['share', 'povray-3.6', 'include'])
            except:
                raise Exception("don't know how to figure out povray_libpath on Linux" +
                                " if povray executable path doesn't end with 'bin/povray'")
    except Exception, e:
        povray_libpath = ''
        env.history.message(redmsg(e.args[0]))
        
    workdir, tmp_pov = os.path.split(povrayscene_file)
    base, ext = os.path.splitext(tmp_pov)
    tmp_out = base + output_ext

    f.write ('; POV-Ray INI file generated by NanoEngineer-1\n')
    f.write ('Input_File_Name="%s"\n' % tmp_pov)
    f.write ('Output_File_Name="%s"\n' % tmp_out)
    f.write ('Library_Path="%s"\n' % povray_libpath) 
        # Library_Path is only needed if MegaPOV is enabled. Doesn't hurt anything always having it. Mark 060628.
    f.write ('+W%d +H%d\n' % (width, height))
    f.write ('+A\n') # Anti-aliasing
    f.write ('+F%s\n' % output_imagetype) # Output format.
    f.write ('Pause_When_Done=true\n') # MacOS and Linux only. User hits any key to make image go away.
    f.write ('; End\n')
    
    f.close()
    
def activate_plugin(win, name=''):
    '''Opens a message box informing the user that the plugin <name>
    needs to be enabled and asking if they wish to do so.
    win is the main window object.
    '''
    
    if not name:
        print "activate_plugin(): No name provided"
        return 1

    from qt import QMessageBox
    ret = QMessageBox.warning( win, "Activate " + name + " Plug-in",
        name + " plug-in not enabled. Please select <b>OK</b> to \n" \
        "activate the " + name + " plug-in from the Preferences dialog.",
        "&OK", "Cancel", None,
        0, 1 )
            
    if ret==0: # OK
        win.uprefs.showDialog('Plug-ins') # Show Prefences | Plug-in.
        if not env.prefs[povray_enabled_prefs_key]:
            return 1 # Plugin was not enabled by user.
        
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

# This should probably be moved to somewhere else like Plugins.py
# Talk to Bruce about pros/cons of this.  Mark 060529.
def get_default_plugin_path(win32_path, darwin_path, linux_path):
    """Returns the plugin (executable) path to the standard location for each platform if it exists
    Otherwise, return an empty string.
    """
    if sys.platform == "win32": # Windows
        plugin_path = win32_path
    elif sys.platform == "darwin": # MacOS
        plugin_path = darwin_path
    else: # Linux
        plugin_path = linux_path
    if not os.path.exists(plugin_path):
        return ""
    return plugin_path
