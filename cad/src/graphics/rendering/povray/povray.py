# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
povray.py - routines to support POV-Ray rendering in nE-1.

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

mark 060529 - Created file to support "View > Raytrace Scene".

bruce 060711 major code clean up / bugfixing, in order to support
direct include_dir prefs setting for Mac A8

Module classification: has ui and graphics_io code, related
to external processes. Not sure what's best, ui or graphics_io.
For now, call this "graphics_io". [bruce 071215]
"""

import os, sys

from PyQt4.Qt import QApplication, QCursor, Qt, QStringList, QProcess, QMessageBox

import foundation.env as env
from utilities.Log import orangemsg ##, redmsg, greenmsg, _graymsg
from utilities.debug import print_compact_traceback
from processes.Plugins import verifyExecutable

from utilities.prefs_constants import megapov_enabled_prefs_key
from utilities.prefs_constants import megapov_path_prefs_key
from utilities.prefs_constants import povray_enabled_prefs_key
from utilities.prefs_constants import povray_path_prefs_key
from utilities.prefs_constants import povdir_enabled_prefs_key
from utilities.prefs_constants import povdir_path_prefs_key

def _dialog_to_offer_prefs_fixup(win, caption, text, macwarning_ok): #bruce 060710 [use Plugin.py instead?]
    """
    Offer the user a chance to fix a problem.
    Return 0 if they accept (after letting them try), 1 if they decline.
    """
    # modified from (now-removed) activate_plugin() which had similar code
    macwarning = ""
    if sys.platform == 'darwin' and macwarning_ok:
        macwarning = "\n"\
                   "  Warning: Mac GUI versions of POV-Ray or MegaPOV won't work,\n"\
                   "but the Unix command-line versions can be compiled on the Mac\n"\
                   "and should work. Contact support@nanorex.com for more info."
    ret = QMessageBox.warning( win, caption, text + macwarning,
                               "&OK", "Cancel", "",
                               0, 1 )
    if ret == 0: # OK
        win.userPrefs.show(pagename = 'Plug-ins') # Show Preferences | Plug-ins.
        return 0 # let caller figure out whether user fixed the problem
    elif ret == 1: # Cancel
        return 1
    pass

def fix_plugin_problem(win, name, errortext, macwarning_ok):
    caption = "%s Problem" % name
    text = "Error: %s.\n" % (errortext,) + \
         "  Select OK to fix this now in the Plugins page of\n" \
         "the Preferences dialog and retry rendering, or Cancel."
        # original code had <b>OK</b> but this was displayed directly (not interpreted), so I removed it [bruce 060711]
    return _dialog_to_offer_prefs_fixup( win, caption, text, macwarning_ok)

# ==

def decode_povray_prefs(win, ask_for_help, greencmd = None): #bruce 060710 ###@@@ review docstring
    """
    Look at the current state of Plugin Prefs (about POV-Ray and MegaPOV) to determine:
    - whether the user wants us to launch MegaPOV, POV-Ray, or neither [see below for retval format]
    - whether we can do what they ask
    Assume it's an error if we can't launch one of them, and return errorcode, errortext as appropriate.
    If <ask_for_help> is true, and we can't launch the one the user wants, offer to get them into the prefs dialog
    to fix the situation; if they fail, return the appropriate error (no second chances, perhaps unless
    they fixed part of it and we got farther in the setup process).
       If we can launch one, return the following:
    0, (program_nickname, program_path, include_dir), where program_nickname is "POV-Ray" or "MegaPOV",
    program_path points to an existing file (not necessarily checked for being executable),
    and include_dir points to an existing directory or (perhaps) is "" (not necessarily checked for including transforms.inc).
    We might [not yet decided ###k] permit include_dir to not include transforms.inc or be "", with a history warning,
    since this will sometimes work (as of 060710, I think it works when blue sky background is not used).
       If we can't launch one, return errorcode, errortext, with errorcode true and errortext an error message string.
    """
    #bruce 060710 created this from parts of write_povray_ini_file and launch_povray_or_megapov
    if greencmd is None:
        greencmd = "" # only used as a prefix for history warnings
    name = "POV-Ray or MegaPOV"

##    # If the user didn't enable either POV-Ray or MegaPOV, let them do that now.
##    if not (env.prefs[megapov_enabled_prefs_key] or env.prefs[povray_enabled_prefs_key]):
##        activate_povray_or_megapov(win, "POV-Ray or MegaPOV")
##        if not (env.prefs[megapov_enabled_prefs_key] or env.prefs[povray_enabled_prefs_key]):
##            return 1, "neither POV-Ray nor MegaPOV plugins are enabled"

    # Make sure the other prefs settings are correct; if not, maybe repeat until user fixes them or gives up.
    macwarning_ok = True # True once, false after that ##e might make it only true for certain warnings, not others
    while 1:
        errorcode, errortext_or_info = decode_povray_prefs_0(win, greencmd)
        if errorcode:
            if not ask_for_help:
                return errorcode, errortext_or_info
            ret = fix_plugin_problem(win, name, errortext_or_info, macwarning_ok)
            macwarning_ok = False
            if ret == 0: # Subroutine has shown Preferences | Plug-in.
                continue # repeat the checks, to figure out whether user fixed the problem
            elif ret == 1: # User declined to try to fix it now
                return errorcode, errortext_or_info
        else:
            (program_nickname, program_path, include_dir) = errortext_or_info # verify format (since it's in our docstring)
            return 0, errortext_or_info
    pass # end of decode_povray_prefs

def decode_povray_prefs_0(win, greencmd): #bruce 060710
    """
    [private helper for decode_povray_prefs]
    """
    # The one they want to use is the first one enabled out of MegaPOV or POV-Ray (in that order).
    if env.prefs[megapov_enabled_prefs_key]:
        want = "MegaPOV"
        wantpath = env.prefs[megapov_path_prefs_key]
    elif env.prefs[povray_enabled_prefs_key]:
        want = "POV-Ray"
        wantpath = env.prefs[povray_path_prefs_key]
    else:
        return 1, "neither POV-Ray nor MegaPOV plugins are enabled"

    if not wantpath:
        return 1, "%s plug-in executable path is empty" % want

    if not os.path.exists(wantpath):
        return 1, "%s executable not found at specified path" % want

    message = verifyExecutable(wantpath)
    if (message):
        return 1, message

    ##e should check version of plugin, if we know how

    # Figure out include dir to use.
    if env.prefs[povdir_enabled_prefs_key] and env.prefs[povdir_path_prefs_key]:
        include_dir = env.prefs[povdir_path_prefs_key]
    else:
        errorcode, include_dir = default_include_dir() # just figure out name, don't check it in any way [can it return ""?]
        if errorcode:
            return errorcode, include_dir
    errorcode, errortext = include_dir_ok(include_dir) # might just print warning if it's not clear whether it's ok
    if errorcode:
        return errorcode, errortext
    return 0, (want, wantpath, include_dir) # (program_nickname, program_path, include_dir)

# ==

def this_platform_can_guess_include_dir_from_povray_path():
    return sys.platform != 'darwin'

def default_include_dir(): #bruce 060710 split out and revised Mark's & Will's code for this in write_povray_ini_file
    """
    The user did not specify an include dir, so guess one from the POV-Ray path (after verifying it's set).
    Return 0, include_dir or errorcode, errortext.
    If not having one is deemed worthy of only a warning, not an error, emit the warning and return 0 [nim].
    """
    # Motivation:
    # If MegaPOV is enabled, the Library_Path option must be added and set to the POV-Ray/include
    # directory in the INI. This is so MegaPOV can find the include file "transforms.inc". Mark 060628.
    # : Povray also needs transforms.inc - wware 060707
    # : : [but when this is povray, it might know where it is on its own (its own include dir)? not sure. bruce 060707]
    # : : [it looks like it would not know that in the Mac GUI version (which NE1 has no way of supporting,
    #       since external programs can't pass it arguments); I don't know about Unix/Linux or Windows. bruce 060710]

    if not this_platform_can_guess_include_dir_from_povray_path():
        # this runs on Mac
        return 1, "Can't guess include dir from POV-Ray executable\npath on this platform; please set it explicitly"

    povray_path = env.prefs[povray_path_prefs_key]
    if not povray_path:
        return 1, "Either the POV include directory or the POV-Ray\nexecutable path must be set (even when using MegaPOV)"
        #e in future, maybe we could use one from POV-Ray, even if it was not enabled, so don't preclude this here

    try:
        # try to guess the include directory (include_dir) from povray_path; exception if you fail
        if sys.platform == 'win32':  # Windows
            povray_bin, povray_exe = os.path.split(povray_path)
            povray_dir, bin = os.path.split(povray_bin)
            include_dir = os.path.normpath(os.path.join(povray_dir, "include"))
        elif sys.platform == 'darwin':  # Mac
            assert 0
        else:  # Linux
            povray_bin = povray_path.split(os.path.sep) # list of pathname components
            assert povray_bin[-2] == 'bin' and povray_bin[-1] == 'povray' # this is the only kind of path we can do this for
            include_dir = os.path.sep.join(povray_bin[:-2] + ['share', 'povray-3.6', 'include'])
        return 0, include_dir
    except:
        if env.debug() and this_platform_can_guess_include_dir_from_povray_path():
            print_compact_traceback("debug fyi: this is the exception inside default_include_dir: ")
        msg = "Unable to guess POV include directory from\nPOV-Ray executable path; please set it explicitly"
        return 1, msg
    pass

def include_dir_ok(include_dir):
    """
    Is this include_dir acceptable (or maybe acceptable)? Return (0, "") or (errorcode, errortext).
    """
    if env.debug():
        print "debug: include_dir_ok(include_dir = %r)" % (include_dir,)
    if os.path.isdir(include_dir):
        # ok, but warn if transforms.inc is not inside it
        if not os.path.exists(os.path.join(include_dir, "transforms.inc")):
            msg = "Warning: transforms.inc not present in POV include directory [%s]; rendering might not work" % (include_dir,)
            env.history.message(orangemsg(msg))
        if env.debug():
            print "debug: include_dir_ok returns 0 (ok)"
        return 0, "" # ok
    else:
        if env.debug():
            print "debug: include_dir_ok returns 1 (Not found or not a directory)"
        return 1, "POV include directory: Not found or not a directory" #e pathname might be too long for a dialog
    pass

# ==

def write_povray_ini_file(ini, pov, out, info, width, height, output_type = 'png'): #bruce 060711 revised this extensively for Mac A8
    """
    Write the povray_ini file, <ini>, containing the commands necessary to render the povray scene file <pov>
    to produce an image in the output file <out>, using the rendering options width, height, output_type,
    and the renderer info <info> (as returned fom decode_povray_prefs).
       All these filenames should be given as absolute pathnames, as if returned from get_povfile_trio() in PovrayScene.
    (It is currently a requirement that they all be in the same directory -- I'm not sure how necessary that is.)
    <width>, <height> (ints) are used as the width and height of the rendered image.
    <output_type> is used as the extension of the output image (currently only 'png' and 'bmp' are supported).
    [WARNING: bmp may not be correctly supported on Mac.]
    (I don't know whether the rendering programs require that <output_type> matches
     the file extension of <out>. As currently called, it supposedly does.)
    """
    # Should this become a method of PovrayScene? I think so, but ask Bruce. Mark 060626.

    dir_ini, rel_ini = os.path.split(ini)
    dir_pov, rel_pov = os.path.split(pov)
    dir_out, rel_out = os.path.split(out)

    assert dir_ini == dir_pov == dir_out, "current code requires ini, pov, out to be in the same directory"
        # though I'm not sure why it needs to -- maybe this only matters on Windows? [bruce 060711 comment]

    (program_nickname, program_path, include_dir) = info #e rename this arg renderer_info?

    if output_type == 'bmp':
        output_ext = '.bmp'
        output_imagetype = 'S' # 'S' = System-specific such as Mac Pict or Windows BMP
        ####@@@@ that sounds to me like it will fail to write bmp as requested, on Mac OS [bruce 060711 comment]
    else: # default
        output_ext = '.png'
        output_imagetype = 'N' # 'N' = PNG (portable network graphics) format

    if 1:
        # output_ext is only needed for this debug warning; remove when works
        base, ext = os.path.splitext(rel_pov)
        if rel_out != base + output_ext:
            print "possible bug introduced in 060711 code cleanup: %r != %r" % (rel_out , base + output_ext)
        pass

    f = open(ini,'w') # Open POV-Ray INI file.

    f.write ('; POV-Ray INI file generated by NanoEngineer-1\n')
    f.write ('Input_File_Name="%s"\n' % rel_pov)
    f.write ('Output_File_Name="%s"\n' % rel_out)
    f.write ('Library_Path="%s"\n' % include_dir)
        # Library_Path is only needed if MegaPOV is enabled. Doesn't hurt anything always having it. Mark 060628.
        # According to Will, it's also needed for POV-Ray. Maybe this is only the case on some platforms. [bruce 060710]
    f.write ('+W%d +H%d\n' % (width, height))
    f.write ('+A\n') # Anti-aliasing
    f.write ('+F%s\n' % output_imagetype) # Output format.
    f.write ('Pause_When_Done=true\n') # MacOS and Linux only. User hits any key to make image go away.
    f.write ('; End\n')

    f.close()

    return # from write_povray_ini_file

def launch_povray_or_megapov(win, info, povray_ini): #bruce 060707/11 revised this extensively for Mac A8
    """
    Try to launch POV-Ray or MegaPOV, as specified in <info> (as returned from decode_povray_prefs, assumed already checked),
    on the given <povray_ini> file (which should already exist), and running in the directory of that file
    (this is required, since it may contain relative pathnames).
    <win> must be the main window object (used for .glpane.is_animating).
       Returns (errorcode, errortext), where errorcode is one of the following: ###k
        0 = successful
        8 = POV-Ray or MegaPOV failed for an unknown reason.
    """
    (program_nickname, program_path, include_dir) = info #e rename this arg renderer_info?

    exit = ''
    program = program_path

    if sys.platform == 'win32':
        program = "\""+program+"\"" # Double quotes needed by Windows. Mark 060602.
        if program_nickname == 'POV-Ray':
            exit = "/EXIT"

    # Later we'll cd to the POV-Ray's INI file directory and use tmp_ini in the POV-Ray command-line.
    # This helps us get around POV-Ray's I/O Restrictions. Mark 060529.
    workdir, tmp_ini = os.path.split(povray_ini)

    # Render scene.
    try:
        args = [tmp_ini]
        if exit:
            args += [exit]
        if env.debug():
            ## use env.history.message(_graymsg(msg)) ?
            print "debug: Launching %s: \n" % program_nickname,\
                  "working directory=",workdir,"\n  program_path=", program_path,  "\n  args are %r" % (args,)

        arguments = QStringList()
        for arg in args:
            if arg != "":
                arguments.append(arg)

        from processes.Process import Process
        p = Process()
            #bruce 060707: this doesn't take advantage of anything not in QProcess,
            # unless it matters that it reads and discards stdout/stderr
            # (eg so large output would not block -- unlikely that this matters).
            # It doesn't echo stdout/stderr. See also blabout/blaberr in other files. Maybe fix this? ###@@@
        p.setWorkingDirectory(workdir)
        p.start(program, arguments)

        # Put up hourglass cursor to indicate we are busy. Restore the cursor below. Mark 060621.
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )

        win.glpane.is_animating = True # This disables selection [do you mean highlighting? #k] while rendering the image.

        import time
        msg = "Rendering image"
        while p.state() == QProcess.Running:
            # Display a message on the status bar that POV-Ray/MegaPOV is rendering.
            # I'd much rather display a progressbar and stop button by monitoring the size of the output file.
            # This would require the output file to be written in PPM or BMP format, but not PNG format, since
            # I don't believe a PNG's final filesize can be predicted.
            # Check out monitor_progress_by_file_growth() in runSim.py, which does this. [mark]
            time.sleep(0.25)
            env.history.statusbar_msg(msg)
            env.call_qApp_processEvents()
            if 1:
                # Update the statusbar message while rendering.
                if len(msg) > 40: #bruce changed 100 -> 40 in case of short statusbar
                    msg = "Rendering image"
                else:
                    #msg = msg + "."
                    msg += "."

    except:
        #bruce 060707 moved print_compact_traceback earlier, and its import to toplevel (after Windows A8, before Linux/Mac A8)
        print_compact_traceback( "exception in launch_povray_or_megapov(): " )
        QApplication.restoreOverrideCursor()
        win.glpane.is_animating = False
        return 8, "%s failed for an unknown reason." % program_nickname

    #bruce 060707 moved the following outside the above try clause, and revised it (after Windows A8, before Linux/Mac A8)
    QApplication.restoreOverrideCursor() # Restore the cursor. Mark 060621.
    ## env.history.statusbar_msg("Rendering finished!") # this is wrong if it was not a normal exit. [bruce 060707 removed it]
    win.glpane.is_animating = False

    if 1:
        #bruce 060707 added this (after Windows A8, before Linux/Mac A8):
        # set an appropriate exitcode and msg
        if p.exitStatus() == QProcess.NormalExit:
            exitcode = p.exitStatus()
            if not exitcode:
                msg = "Rendering finished!"
            else:
                msg = "Rendering program had exitcode %r" % exitcode
                    # e.g. 126 for Mac failure; same as shell exitcode, which says "cannot execute binary file";
                    # but /usr/bin/open helps, so we'll try that above (but not in this commit, which is just to
                    # improve error reporting). ###@@@
                    # [bruce 060707]
        else:
            exitcode = p.exitStatus()
            exitcode = -1
            msg = "Abnormal exit (or failure to launch)"
        if exitcode or env.debug():
            print msg
        env.history.statusbar_msg(msg)
##        if env.debug():
##            env.history.message(_graymsg(msg)) # not needed, caller prints it
        if exitcode:
            return 8, "Error: " + msg # this breaks the convention of the other error returns
        pass

    # Display image in separate window here. [Actually I think this is done in the caller -- bruce 060707 comment]

    return 0, "Rendering finished" # from launch_povray_or_megapov

def verify_povray_program(): # not yet used, not yet correctly implemented
    """
    Returns 0 if povray_path_prefs_key is the path to the POV-Ray 3.6 executable.
    Otherwise, returns 1.
    Always return 0 for now until I figure out a way to verify POV-Ray. Mark 060527.
    """
    vstring = "POV-Ray 3.6" # or somthing like this.os
    #r = verify_program(env.prefs[povray_path_prefs_key], '-v', vstring)
    #return r
    return 0

# ==

# end
