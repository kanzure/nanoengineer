# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
startup_misc.py - miscellaneous application startup functions
which are free to do whatever imports they need to.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050902 made startup_funcs.py by moving some code out of main.py,
and adding some stub functions which will be filled in later.

bruce 071005 moved these functions from startup_funcs.py into
this new file startup/startup_misc.py.
"""

# note: toplevel imports are now ok in this module [bruce 071008 change]

from utilities.debug import print_compact_traceback

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

    import model_updater.master_model_updater as master_model_updater
    master_model_updater.initialize()

    import model.assembly
    model.assembly.Assembly.initialize()

    import PM.GroupButtonMixin as GroupButtonMixin
    GroupButtonMixin.GroupButtonMixin.initialize()

    return

def register_MMP_RecordParsers(): #bruce 071019
    """
    Register MMP_RecordParser subclasses for the model objects that can be read
    from mmp files, and whose parsers are not hardcoded into files_mmp.py.
    """
    import model.Comment as Comment
    Comment.register_MMP_RecordParser_for_Comment()

    import analysis.GAMESS.jig_Gamess as jig_Gamess
    jig_Gamess.register_MMP_RecordParser_for_Gamess()

    import model.PovrayScene as PovrayScene
    PovrayScene.register_MMP_RecordParser_for_PovrayScene()

    try:
        import dna.model.DnaMarker as DnaMarker
        DnaMarker.register_MMP_RecordParser_for_DnaMarkers()
    except:
        print_compact_traceback("bug: ignoring exception in register_MMP_RecordParser_for_DnaMarkers: ")
        pass

    # TODO: add more of these.

    return

# (MWsemantics.__init__ is presumably run after the above functions and before the following ones.)

def pre_main_show( win):
    """
    Do whatever should be done after the main window is created
    but before it's first shown.
    """

    # Determine the screen resolution and compute the normal window size for NE-1
    # [bruce 041230 corrected this for Macintosh, and made sure it never exceeds
    #  screen size even on a very small screen.]
    # [bruce 050118 further modified this and removed some older comments
    #  (see cvs for those); also split out some code into platform.py.]
    from platform_dependent.PlatformDependent import screen_pos_size
    ((x0, y0), (screen_w, screen_h)) = screen_pos_size()
    # note: y0 is nonzero on mac, due to menubar at top of screen.

    # use 85% of screen width and 90% of screen height, or more if that would be
    # less than 780 by 560 pixels, but never more than the available space.
    try:
        norm_w = int( min(screen_w - 2, max(780, screen_w * 0.85)))
        norm_h = int( min(screen_h - 2, max(560, screen_h * 0.90)))
    except Exception as exception:
        norm_w = 800
        norm_h = 600

        #bruce 050118 reduced max norm_h to never overlap mac menubar (bugfix?)

    # determine normal window origin
    # [bruce 041230 changed this to center it, but feel free to change this back
    #  by changing the next line to center_it = 0]
    center_it = 1
    if center_it:
        # centered in available area
        try:
            norm_x = (screen_w - norm_w) / 2 + x0
            norm_y = (screen_h - norm_h) / 2 + y0
        except Exception as exception:
            norm_x = 800
            norm_y = 600
    else:
        # at the given absolute position within the available area
        # (but moved towards (0,0) from that, if necessary to keep it all on-screen)
        want_x = 4 # Left (4 pixels)
        want_y = 36 # Top (36 pixels)
        try:
            norm_x = min( want_x, (screen_w - norm_w)) + x0
            norm_y = min( want_y, (screen_h - norm_h)) + y0
        except Exception as exception:
            norm_x = 800
            norm_y = 600

    # Set the main window geometry, hopefully before the caller shows the window
    from PyQt4.Qt import QRect
    win.setGeometry(QRect(norm_x, norm_y, norm_w, norm_h))

    ###e it might be good to register this as the default geom. in the prefs system, and use that to implement "restore defaults"

    # After the above (whose side effects on main window geom. are used as defaults by the following code),
    # load any mainwindow geometry present in prefs db. [bruce 051218 new feature; see also new "save" features in UserPrefs.py]
    from utilities.debug import print_compact_stack
    try:
        # this code is similar to debug.py's _debug_load_window_layout
        from ne1_ui.prefs.Preferences import load_window_pos_size
        from utilities.prefs_constants import mainwindow_geometry_prefs_key_prefix
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
    # note (kluge): the following imports do side effects whose order matters.
    # They must match the order of related display style list-index definitions
    # in constants.py.
    # [bruce 080212 comment; related code has comments with same signature]

    # diDNACYLINDER
    import graphics.display_styles.DnaCylinderChunks as DnaCylinderChunks #mark 2008-02-11

    # diCYLINDER
    import graphics.display_styles.CylinderChunks as CylinderChunks #bruce 060609
    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    enable_CylinderChunks = debug_pref("enable CylinderChunks next session?",
                                       Choice_boolean_False,
                                       non_debug = True,
                                       prefs_key = True)
    win.dispCylinderAction.setText("Cylinder (experimental)")
    win.dispCylinderAction.setEnabled(enable_CylinderChunks)
    win.dispCylinderAction.setVisible(enable_CylinderChunks)
    if enable_CylinderChunks:
        win.displayStylesToolBar.addAction(win.dispCylinderAction)

    # diSURFACE
    import graphics.display_styles.SurfaceChunks as SurfaceChunks #mark 060610
    enable_SurfaceChunks = debug_pref("enable SurfaceChunks next session?",
                                      Choice_boolean_False,
                                      ## non_debug = True,
                                          # bruce 080416 hiding this since it's
                                          # broken at the moment when CSDL is
                                          # enabled and psurface.so is not found.
                                          # If/when it's fixed, it should be
                                          # made visible again.
                                      prefs_key = True)
    win.dispSurfaceAction.setText("Surface (experimental, may be slow)")
    win.dispSurfaceAction.setEnabled(enable_SurfaceChunks)
    win.dispSurfaceAction.setVisible(enable_SurfaceChunks)
    if enable_SurfaceChunks:
        win.displayStylesToolBar.addAction(win.dispSurfaceAction)

    # diPROTEIN display style
    # piotr 080624
    import graphics.display_styles.ProteinChunks as ProteinChunks

    return

# ==

def post_main_show( win):
    """
    Do whatever should be done after the main window is shown,
    but before the Qt event loop is started.

    @param win: the single Main Window object.
    @type  win: L{MWsemantics}
    """
    # NOTE: if possible, new code should be added into one of the following
    # functions, or into a new function called by this one, rather than
    # directly into this function.

    # TODO: rebuild pyx modules if necessary and safe -- but only for
    # developers, not end-users
    # TODO: initialize Python extensions: ## import experimental/pyrex_test/extensions.py
    _initialize_plugin_generators()
    _init_experimental_commands()
    _init_miscellaneous_commands()
    # Set default splitter position in the part window.
    pw = win.activePartWindow()
    pw.setSplitterPosition()
    return

def _init_experimental_commands():
    """
    Initialize experimental commands in the UI.
    This is called after the main window is shown.
    """
    # Note: if you are not sure where to add init code for a new command in
    # the UI, this is one possible place. But if it's more complicated than
    # importing and calling an initialize function, it's best if the
    # complicated part is defined in some other module and just called from
    # here. See also the other places from which initialize functions are
    # called, for other places that might be better for adding new command
    # initializers. This place is mainly for experimental or slow-to-initialize
    # commands.
    # [bruce 071005]
    _init_command_Atom_Generator()
    _init_command_Select_Bad_Atoms()
    _init_command_Peptide_Generator() # piotr 080304
    _init_test_commands()
    return

def _init_command_Atom_Generator():
    # TODO: this function should be moved into AtomGenerator.py
    # Atom Generator debug pref. Mark and Jeff. 2007-06-13
    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    from commands.BuildAtom.AtomGenerator import enableAtomGenerator
    _atomGeneratorIsEnabled = \
                            debug_pref("Atom Generator example code: enabled?",
                                       Choice_boolean_False,
                                       non_debug = True,
                                       prefs_key = "A9/Atom Generator Visible",
                                       call_with_new_value = enableAtomGenerator )
    enableAtomGenerator(_atomGeneratorIsEnabled)
    return

def _init_command_Peptide_Generator(): # piotr 080304
    # This function enables an experimental peptide generator.
    from utilities.debug_prefs import debug_pref, Choice_boolean_True
    from protein.commands.InsertPeptide.PeptideGenerator import enablePeptideGenerator
    _peptideGeneratorIsEnabled = \
                               debug_pref("Peptide Generator: enabled?",
                                          Choice_boolean_True,
                                          prefs_key = "A10/Peptide Generator Visible",
                                          call_with_new_value = enablePeptideGenerator )
    enablePeptideGenerator(_peptideGeneratorIsEnabled)
    return

def _init_command_Select_Bad_Atoms():
    # note: I think this was imported at one point
    # (which initialized it), and then got left out of the startup code
    # by mistake for awhile, when init code was revised. [bruce 071008]
    import operations.chem_patterns as chem_patterns
    chem_patterns.initialize()
    return

def _init_test_commands():
    #bruce 070613
    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    if debug_pref("test_commands enabled (next session)",
                  Choice_boolean_False,
                  prefs_key = True):
        import prototype.test_commands_init as test_commands_init
        test_commands_init.initialize()
    return

def _init_miscellaneous_commands():

    import model.virtual_site_indicators as virtual_site_indicators
    virtual_site_indicators.initialize() #bruce 080519

    import operations.ops_debug as ops_debug
    ops_debug.initialize() #bruce 080722

    return

def _initialize_plugin_generators(): #bruce 060621
    # The CoNTub generator isn't working - commented out until it's fixed.
    # Brian Helfrich, 2007/06/04
    # (see also some related code in main_startup.py)
    pass
    #import CoNTubGenerator
        # note: this adds the Insert -> Heterojunction menu item.
        # kluge (sorry): as of 060621, it adds it at a hardcoded menu index.

def just_before_event_loop():
    """
    do post-startup, pre-event-loop, non-profiled things, if any
    (such as run optional startup commands for debugging)
    """
    #bruce 081003
    from utilities.debug_prefs import debug_pref, Choice_boolean_False
    if debug_pref("startup in Test Graphics command (next session)?",
                  Choice_boolean_False,
                  prefs_key = True ):
        import foundation.env as env
        win = env.mainwindow()
        from commands.TestGraphics.TestGraphics_Command import enter_TestGraphics_Command_at_startup
        enter_TestGraphics_Command_at_startup( win)
        pass
    return

# end
