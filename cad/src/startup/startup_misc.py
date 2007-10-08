# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
startup_misc.py - miscellaneous application startup functions
which are free to do whatever imports they need to.

$Id$

History:

bruce 050902 made startup_funcs.py by moving some code out of main.py,
and adding some stub functions which will be filled in later.

bruce 071005 moved these functions from startup_funcs.py into
this new file startup/startup_misc.py.
"""

# note: toplevel imports are now ok in this module [bruce 071008 change]

def call_module_init_functions(): #bruce 071005 split this out of main_startup.startup_script
    """
    Call the module initialize functions that are needed
    before creating the main window object. This includes
    functions that need to be called before model data structures
    can be safely created or modified. These functions can assume
    that the main application object exists.
    """
    # [added by ericm 20070701, along with "remove import star", just after NE1
    #  A9.1 release, into main_startup.startup_script]

    # WARNING: the order of calling these matters, for many of them. We should document
    # that order dependency in their docstrings, and perhaps also right here.
    # One reason for order dependency is registration order of post_event_updater functions,
    # though this is mitigated now that we register model and ui updaters separately.
    # (We may decide to call those more directly here, not inside generic initialize methods,
    #  as a clarification. Likely desirable change (###TODO): register a model updater in assy,
    #  which calls the bond updater presently registered by bond_updater.initialize.)
    # [bruce 070925 comment]
    
    import bond_updater
    bond_updater.initialize()
    
    import assembly
    assembly.assembly.initialize()
    
    import GroupButtonMixin
    GroupButtonMixin.GroupButtonMixin.initialize()

    return

# (MWsemantics.__init__ is presumably run after the above functions and before the following ones.)

def pre_main_show( win):
    "Do whatever should be done after the main window is created but before it's first shown."

    # Determine the screen resolution and compute the normal window size for NE-1
    # [bruce 041230 corrected this for Macintosh, and made sure it never exceeds
    #  screen size even on a very small screen.]
    # [bruce 050118 further modified this and removed some older comments
    #  (see cvs for those); also split out some code into platform.py.]
    from PlatformDependent import screen_pos_size
    ((x0, y0), (screen_w, screen_h)) = screen_pos_size()
    # note: y0 is nonzero on mac, due to menubar at top of screen.
    
    # use 85% of screen width and 90% of screen height, or more if that would be
    # less than 780 by 560 pixels, but never more than the available space.
    norm_w = int( min(screen_w - 2, max(780, screen_w * 0.85)))
    norm_h = int( min(screen_h - 2, max(560, screen_h * 0.90)))
        #bruce 050118 reduced max norm_h to never overlap mac menubar (bugfix?)
    
    # determine normal window origin
    # [bruce 041230 changed this to center it, but feel free to change this back
    #  by changing the next line to center_it = 0]
    center_it = 1
    if center_it:
        # centered in available area
        norm_x = (screen_w - norm_w) / 2 + x0
        norm_y = (screen_h - norm_h) / 2 + y0
    else:
        # at the given absolute position within the available area
        # (but moved towards (0,0) from that, if necessary to keep it all on-screen)
        want_x = 4 # Left (4 pixels)
        want_y = 36 # Top (36 pixels)
        norm_x = min( want_x, (screen_w - norm_w)) + x0
        norm_y = min( want_y, (screen_h - norm_h)) + y0
    
    # Set the main window geometry, hopefully before the caller shows the window
    from PyQt4.Qt import QRect
    win.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))

    ###e it might be good to register this as the default geom. in the prefs system, and use that to implement "restore defaults"

    # After the above (whose side effects on main window geom. are used as defaults by the following code),
    # load any mainwindow geometry present in prefs db. [bruce 051218 new feature; see also new "save" features in UserPrefs.py]
    from debug import print_compact_stack
    try:
        # this code is similar to debug.py's _debug_load_window_layout
        from UserPrefs import load_window_pos_size
        from prefs_constants import mainwindow_geometry_prefs_key_prefix
        keyprefix = mainwindow_geometry_prefs_key_prefix
        load_window_pos_size( win, keyprefix)
        win._ok_to_autosave_geometry_changes = True
    except:
        print_compact_stack("exception while loading/setting main window pos/size from prefs db: ")
        win.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))

    _initialize_custom_display_modes(win)

    ### TODO: this would be a good place to add miscellaneous commands to the UI,
    # provided they are fully supported (not experimental, unlikely to cause bugs when added)
    # and won't take a lot of runtime to add. Otherwise they can be added after the
    # main window is shown. [bruce 071005 comment] ###@@@
    
    return # from pre_main_show

# This is debugging code used to find out the origin and size of the fullscreen window
#    foo = win
#    foo.setGeometry(QRect(600,50,1000,800)) # KEEP FOR DEBUGGING
#    fooge = QRect(foo.geometry())
#    print "Window origin = ",fooge.left(),",",fooge.top()
#    print "Window width =",fooge.width(),", Window height =",fooge.height()

def _initialize_custom_display_modes(win):
    import CylinderChunks #bruce 060609
    import SurfaceChunks #mark 060610
    from debug_prefs import debug_pref, Choice_boolean_False
    enable_SurfaceChunks = debug_pref("enable SurfaceChunks next session?",
                                      Choice_boolean_False, non_debug = True, prefs_key = True)
    win.dispSurfaceAction.setText("Surface (experimental, may be slow)")
    win.dispSurfaceAction.setEnabled(enable_SurfaceChunks)
    win.dispSurfaceAction.setVisible(enable_SurfaceChunks)
    return

# ==

def post_main_show( win):
    """
    Do whatever should be done after the main window is shown,
    but before the Qt event loop is started.

    @param win: the single Main Window object.
    @type  win: L{MWsemantics}
    """
    # NOTE: if possible, new code should be added into one of the following functions,
    # or into a new function called by this one, rather than directly into this function.
    
    # TODO: rebuild pyx modules if necessary and safe -- but only for developers, not end-users
    # TODO: initialize Python extensions: ## import extensions.py
    _initialize_plugin_generators()
    _init_experimental_commands()
    _set_mainwindow_splitter_position( win)
    return

def _init_experimental_commands():
    """
    Initialize experimental commands in the UI.
    This is called after the main window is shown.
    """
    # Note: if you are not sure where to add init code for a new command in the UI,
    # this is one possible place. But if it's more complicated than importing and calling
    # an initialize function, it's best if the complicated part is defined in some other
    # module and just called from here. See also the other places from which initialize
    # functions are called, for other places that might be better for adding new command
    # initializers. This place is mainly for experimental or slow-to-initialize commands.
    # [bruce 071005]
    _init_command_Atom_Generator()
    _init_command_Select_Bad_Atoms()
    _init_test_commands()
    return

def _init_command_Atom_Generator(): # TODO: this function should be moved into AtomGenerator.py
    # Atom Generator debug pref. Mark and Jeff. 2007-06-13
    from debug_prefs import debug_pref, Choice_boolean_False
    from AtomGenerator import enableAtomGenerator
    _atomGeneratorIsEnabled = debug_pref("Atom Generator example code: enabled?", Choice_boolean_False, 
                                       non_debug = True, prefs_key = "A9/Atom Generator Visible",
                                       call_with_new_value = enableAtomGenerator )
    enableAtomGenerator(_atomGeneratorIsEnabled)
    return

def _init_command_Select_Bad_Atoms():
    # note: I think this was imported at one point
    # (which initialized it), and then got left out of the startup code
    # by mistake for awhile, when init code was revised. [bruce 071008]
    import chem_patterns
    chem_patterns.initialize()
    return

def _init_test_commands():
    #bruce 070613 
    from debug_prefs import debug_pref, Choice_boolean_False
    if debug_pref("test_commands enabled (next session)", Choice_boolean_False, prefs_key = True):
        import test_commands
    return

def _set_mainwindow_splitter_position( win): # TODO: this function should be moved into some other module.
    """
    Set the position of the splitter between the MT and graphics area
    so that the starting width of the property manager is "pmDefaultWidth"
    pixels.

    This should be called after all visible changes to the main window.
    
    @param win: the single Main Window object.
    @type  win: L{MWsemantics}
    """
    # This code fixes bug 2424. Mark 2007-06-27.
    #
    # Bug 2424 was difficult to fix for many reasons:
    #
    # - QSplitter.sizes() does not return valid values until the main window
    #   is displayed. Specifically, the value of the second index (the glpane
    #   width) is always zero until the main window is displayed. I suspect 
    #   that the initial size of the glpane (in its constructor) is not set
    #   (or set to 0) and may be contributing to the confusion. This is only
    #   a theory.
    #
    # - QSplitter.setSizes() only works if width1 (the PropMgr width) and
    #   width2 (the glpane width) equal a "magic combined width". See 
    #   more about this in the Method description below.
    #
    # - Qt's QSplitter.moveSplitter() function doesn't work.
    #   
    # Method for bug fix:
    #
    # I get the widths of the MT/PropMgr and glpane using wHSplitter.sizes().
    # These (2) widths add up and equal a "magic value". You can only feed
    # pwHSplitter.setSizes() two values that add up to the "magic value".
    # Since we want the default width of the PropMgr to be <pmDefaultWidth>,
    # I compute the new glpane width = magic_combined_width - pmDefaultWidth.
    # Note: the resize is visible at startup.
    
    pw = win.activePartWindow()
    from PropMgr_Constants import pmDefaultWidth
    w1, w2 = pw.pwHSplitter.sizes()
    magic_combined_width = w1 + w2
    new_glpane_width = magic_combined_width - pmDefaultWidth
    pw.pwHSplitter.setSizes([pmDefaultWidth, new_glpane_width])
    return

def _initialize_plugin_generators(): #bruce 060621
    # The CoNTub generator isn't working - commented out until it's fixed.
    # Brian Helfrich, 2007/06/04
    pass
    #import CoNTubGenerator
        # note: this adds the Insert -> Heterojunction menu item.
        # kluge (sorry): as of 060621, it adds it at a hardcoded menu index.

# end
