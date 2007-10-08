# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
main_startup.py -- provides the startup_script function called by main.py

$Id$

History:

mostly unrecorded, except in cvs;
originally by Josh (under the name atom.py);
lots of changes by various developers at various times.

renamed from atom.py to main.py before release of A9, mid-2007,
and split out of main.py into this file (main_startup.py)
by bruce 070704.
"""

import sys, time
import startup_funcs # this has no side effects, it only defines functions we call in a certain order

# NOTE: all other imports MUST be added inside the following function,
# since they must not be done before startup_funcs.before_most_imports is executed.

def startup_script( main_globals):
    """This is the main startup script for NE1,
    described more fully in this module's docstring.
    It is intended to be run only once, and only by the code in main.py.
    When this function returns, the caller is intended to immediately exit
    normally.
       Parameter main_globals should be the value of globals() in __main__,
    which is needed in case .atom-debug-rc is executed, since it must be
    executed in that global namespace.
    """

    startup_funcs.before_most_imports( main_globals )
        # "Do things that should be done before anything that might possibly have side effects."

    ### NOTE: most imports in this file should be done here, or inside functions in startup_funcs.py.

    from PyQt4.Qt import QApplication, QSplashScreen
    
    startup_funcs.before_creating_app()
        # "Do whatever needs to be done before creating the application object, but after importing MWsemantics."
    
    QApplication.setColorSpec(QApplication.CustomColor)
    app = QApplication(sys.argv)
    
    # If the splash image is found in cad/images, put up a splashscreen. 
    # If you don't want the splashscreen, just rename the splash image.
    # mark 060131.
    import icon_utilities
    icon_utilities.initialize()

    splash_pixmap = icon_utilities.imagename_to_pixmap( "images/splash.png" ) # rename it if you don't want it.
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap) # create the splashscreen
        splash.show()
        MINIMUM_SPLASH_TIME = 3.0 
            # I intend to add a user pref for MINIMUM_SPLASH_TIME for A7. mark 060131.
        splash_start = time.time()
    else:
        print "note: splash.png was not found"
 
    from PyQt4.Qt import SIGNAL
    app.connect(app, SIGNAL("lastWindowClosed ()"), app.quit)

    from MWsemantics import MWsemantics # (this might have side effects other than defining things)

    from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
    ##########################################################################################################
    #
    # The debug preference menu is now working in Qt 4 but you can't effectively change this debug
    # preference after the program has already come up, as too much of the GUI is already in place
    # by then. To change it, manually edit it here.
    #
    # [note added later: I suspect we are now dependent on this value of True and should
    #  should not leave the appearance that the False value is supported. I don't know for sure.
    #  [bruce 071005 comment]]
    #
    debug_pref("Multipane GUI", Choice_boolean_True)
    #debug_pref("Multipane GUI", Choice_boolean_False)
    #
    ##########################################################################################################

    startup_funcs._call_module_init_functions()

    foo = MWsemantics() # This does a lot of initialization (in MainWindow.__init__)

    import __main__
    __main__.foo = foo
        # developers often access the main window object using __main__.foo when debugging,
        # so this is explicitly supported

    import CoNTubGenerator
    CoNTubGenerator.initialize()

    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_pre_main_show
    except:
        pass
    else:
        meth()

    startup_funcs.pre_main_show(foo) # this sets foo's geometry, among other things
    
    foo._init_after_geometry_is_set()
    
    if not splash_pixmap.isNull():
        # If the MINIMUM_SPLASH_TIME duration has not expired, sleep for a moment.
        while time.time() - splash_start < MINIMUM_SPLASH_TIME:
            time.sleep(0.1)
        splash.finish( foo ) # Take away the splashscreen
    
    foo.show() # show the main window

    if sys.platform != 'darwin': #bruce 070515 add condition to disable this on Mac, until Brian fixes the hang on Mac
        from Sponsors import PermissionDialog
##        print "start sponsors startup code"
        # Show the dialog that asks permission to download the sponsor logos, then
        # launch it as a thread to download and process the logos.
        #
        permdialog = PermissionDialog(foo)
        if permdialog.needToAsk:
            permdialog.exec_()
        permdialog.start()
##        print "end sponsors startup code"
        
    if not debug_pref("Multipane GUI", Choice_boolean_False):
        if foo.glpane.mode.modename == 'DEPOSIT':
            # Two problems are addressed here when nE-1 starts in Build (DEPOSIT) mode.
            # 1. The MMKit can cover the splashscreen (bug #1439).
            #   BTW, the other part of bug fix 1439 is in MWsemantics.modifyMMKit()
            # 2. The MMKit appears 1-3 seconds before the main window.
            # Both situations now resolved.  mark 060202
            # Should this be moved to startup_funcs.post_main_show()? I chose to leave
            # it here since the splashscreen code it refers to is in this file.  mark 060202.
            foo.glpane.mode.MMKit.show()        
    try:
        # do this, if user asked us to by defining it in .atom-debug-rc
        meth = atom_debug_post_main_show 
    except:
        pass
    else:
        meth()

    startup_funcs.post_main_show(foo)

    # If the user's .atom-debug-rc specifies PROFILE_WITH_HOTSHOT=True, use hotshot, otherwise
    # fall back to vanilla Python profiler.
    try:
        PROFILE_WITH_HOTSHOT
    except NameError:
        PROFILE_WITH_HOTSHOT = False
    
    # now run the main Qt event loop --
    # perhaps with profiling, if user requested this via .atom-debug-rc.
    try:
        # user can set this to a filename in .atom-debug-rc,
        # to enable profiling into that file
        atom_debug_profile_filename 
        if atom_debug_profile_filename:
            print "user's .atom-debug-rc requests profiling into file %r" % (atom_debug_profile_filename,)
            if not type(atom_debug_profile_filename) in [type("x"), type(u"x")]:
                print "error: atom_debug_profile_filename must be a string; running without profiling"
                assert 0 # caught and ignored, turns off profiling
            if PROFILE_WITH_HOTSHOT:
                try:
                    import hotshot
                except:
                    print "error during 'import hotshot'; running without profiling"
                    raise # caught and ignored, turns off profiling
            else:
                try:
                    import profile
                except:
                    print "error during 'import profile'; running without profiling"
                    raise # caught and ignored, turns off profiling
    except:
        atom_debug_profile_filename = None

    # bruce 041029: create fake exception, to help with debugging
    # (in case it's shown inappropriately in a later traceback)
    try:
        assert 0, "if you see this exception in a traceback, it is from the" \
            " startup script called by main.py, not the code that printed the traceback"
    except:
        pass

    from platform import atom_debug
    if atom_debug:
        # Use a ridiculously specific keyword, so this isn't triggered accidentally.
        if len(sys.argv) >= 3 and sys.argv[1] == '--initial-file':
            # fileOpen gracefully handles the case where the file doesn't exist.
            foo.fileOpen(sys.argv[2])
            if len(sys.argv) > 3:
                import env
                from utilities.Log import orangemsg
                env.history.message(orangemsg("We can only import one file at a time."))
  
    if atom_debug_profile_filename:
        if PROFILE_WITH_HOTSHOT:
            profile = hotshot.Profile(atom_debug_profile_filename)
            profile.run('app.exec_()')
        else:
            profile.run('app.exec_()', atom_debug_profile_filename)
        print "\nprofile data was presumably saved into %r" % (atom_debug_profile_filename,)
    else:
        # if you change this code, also change the string literal just above
        app.exec_() 

    return # from startup_script

# end
