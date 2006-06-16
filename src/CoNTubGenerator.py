# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
CoNTubGenerator.py

Generator functions which use cad/plugins/CoNTub.

$Id$

Also intended as a prototype of code which could constitute the nE-1 side
of a "generator plugin API". Accordingly, the CoNTub-specific code should
as much as possible be isolated into small parts of this, with most of it
knowing nothing about CoNTub's specific functionality or parameters.
"""

###@@@ where i am -- see all the IMPLEMS far below [060615 eve]

__author__ = "bruce"

#k not all imports needed?
## from GeneratorDialogs import ParameterDialog ###IMPLEM file and class
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
##from widgets import double_fixup
##from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass
from debug import print_compact_traceback
import os, sys
from platform import find_or_make_Nanorex_subdir, find_or_make_any_directory, tempfiles_dir

### current bug: menu icon is nondeterministic. guess: need to keep a reference to the iconset that we make for it. #####@@@@@

# ==

def add_insert_menu_item(win, command, name_of_what_to_insert, options = ()): ###e this should be a method of MWsemantics.py
    menuIndex = 2 ### kluge - right after Nanotube, at the moment (since indices start from 0)
    menu = win.Insert
    menutext = "%s" % (name_of_what_to_insert,)
    undo_cmdname = "Insert %s" % (name_of_what_to_insert,) ## get this from caller, or, make it available to the command as it runs
        ###e but need to translate it ourselves, ##qApp.translate("Main Window", "Recent Files", None)
    ## self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
    from widgets import insert_command_into_menu
    insert_command_into_menu( menu, menutext, command, options = options, position = menuIndex, undo_cmdname = undo_cmdname)
    return

# ==

def builtin_plugins_dir(): # modified from sim_bin_dir_path in runSim.py; should move both that and this to platform.py ###e
    """Return pathname of built-in plugins directory. Should work for either developers or end-users on all platforms.
    (Doesn't check whether it exists.)
    """
    # filePath = the current directory NE-1 is running from.
    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.normpath(filePath + '/../plugins')

def user_plugins_dir():
    """Return pathname of user custom plugins directory, or None if it doesn't exist."""
    return find_or_make_Nanorex_subdir( 'Plugins', make = False)

def find_plugin_dir(plugin_name):
    "Return (True, dirname) or (False, errortext), with errortext wording chosen as if the requested plugin ought to exist."
    try:
        userdir = user_plugins_dir()
        if userdir and os.path.isdir(userdir):
            path = os.path.join(userdir, plugin_name)
            if os.path.isdir(path):
                return True, path
    except:
        print_compact_traceback("bug in looking for user-customized plugin %r; trying builtin plugins: ")
        pass
    try:
        appdir = builtin_plugins_dir()
        assert appdir
        if not os.path.isdir(appdir):
            return False, "error: can't find built-in plugins directory [%s] (or it's not a directory)" % (appdir,)
        path = os.path.join(appdir, plugin_name)
        if os.path.isdir(path):
            return True, path
        return False, "can't find plugin %r" % (plugin_name,)
    except:
        print_compact_traceback("bug in looking for built-in plugin %r: " % (plugin_name,))
        return False, "can't find plugin %r" % (plugin_name,)
    pass

# ==

class PluginlikeGenerator:
    """Superclass for generators whose code is organized similar to that of a (future) plugin.
    Subclasses contain data and methods which approximate the functionality
    of metadata and/or code that would ultimately be found in a plugin directory.
    See the example subclass in this file for details.
    """
    ok_to_install_in_UI = False # changed to True in instances which become ok to install into the UI; see also errorcode
    # default values of subclass-specific class constants
    what_we_generate = "Something"

    # init methods
    
    def register(subclass): # staticmethod
        win = env.mainwindow()
        try:
            instance = subclass(win)
            if instance.ok_to_install_in_UI:
                instance.install_in_UI()
                if env.debug(): print "debug: registered", instance
            else:
                if env.debug(): print "debug: didn't register", instance
        except:
            print_compact_traceback("bug in instantiating %r or installing its instance: " % subclass)
        return
    register = staticmethod(register)

    errorcode = 0
        # this gets set to something true (by self.fatal) if an error occurs which should
        # permanently disable this plugin (during setup or use)
    errortext = ""
        # this gets set to errortext for the first error that permanently disabled this plugin

    def fatal(self, errortext, errorcode = 1):
        """Our submethods call this to report a fatal setup/use error; it prints errortext appropriately
        and sets self.errorcode and self.errortext.
        """
        if not errorcode:
            print "bug: fatal errorcode must be a boolean-true value, not %r" % (errorcode,)
            errorcode = 1
        if self.errorcode:
            print "plugin %r bug: self.errorcode was already set before fatal was called" % (self.plugin_name,)
        if not self.errorcode or not self.errortext:
            self.errortext = errortext # permanent record for use by callers
        self.errorcode = errorcode
        msg = "plugin %r fatal error: %s" % (self.plugin_name, errortext,)
        print msg
        env.history.message(redmsg(msg)) # it might be too early for this to be seen
        return errorcode

    def __init__(self, win):
        self.win = win

        # All these submethods should call self.fatal to report permanent fatal errors.
        # And after calling the ones that can, we should check self.errorcode before continuing.
        
        # Find plugin dir -- if we can't, it has to be a fatal error,
        # since (once this is using a real plugin API) we won't have the metadata
        # needed to install the plugin in the UI.
        
        path = self.find_plugin_dir()
        if self.errorcode: return
        self.plugin_dir = path # for error messages, and used by runtime methods
        
        # make sure the stuff we need is in the plugin dir (and try to use it to set up the dialogs, commands, etc)
        self.setup_from_plugin_dir() # this prints error msgs if it needs to
        if self.errorcode: return

        # don't create a working directory until the plugin is first used
        # (since we don't want to create one at all, if it's not used in the session,
        #  since they might be created in a session-specific place)
        self.working_directory = None

        if env.debug(): print "plugin init is permitting ok_to_install_in_UI = True" ###@@@
        self.ok_to_install_in_UI = True
        return

    def find_plugin_dir(self):
        ok, path = find_plugin_dir(self.plugin_name)
        if ok:
            assert os.path.isdir(path)
            return path
        else:
            errortext = path
            self.fatal( errortext)
            return None
        pass
    
    def setup_from_plugin_dir(self):
        "Using self.plugin_dir, setup dialogs, commands, etc. Report errors to self.fatal as usual."
        param_desc_path = os.path.join(self.plugin_dir, self.parameter_set_filename)
        self.param_desc_path = param_desc_path
        if not os.path.isfile(param_desc_path):
            return self.fatal("can't find param description file [%s]" % (param_desc_path,))
        ###e get the param set, create the dialog, check the executable exists, etc
        # (even run a self test if it defines one? or wait 'til first used?)
        return

    def install_in_UI(self):
        """Create a menu command, or whatever other UI elements should invoke the plugin's generator.
        Report errors to self.fatal as usual.
        """
        assert self.ok_to_install_in_UI
        #e create whatever we want to be persistent which was not already done in setup_from_plugin_dir (nothing yet?)
        
        #e install the necessary commands in the UI (eg in insert menu)
        ### WRONG -- menu text should not contain Insert, but undo cmdname should (so separate option is needed), and needs icon
        ###e add options for things like tooltip text, whatsthis text, iconset
        options = [('iconset','junk.png')]
        self.menu_item_id = add_insert_menu_item( self.win, self.command_for_insert_menu, self.what_we_generate, options)
        ###e make that a menu item controller, and give it a method to disable the menu item, and do that on error(??) ###@@@
        pass

    # runtime methods
    
    def create_working_directory_if_needed(self):
        """If it hasn't been done already, create a temporary directory (fixed pathname per plugin per session)
        for this plugin to use. Report errors to self.fatal as usual.
        """
        if self.working_directory:
            return
        subdir = os.path.join( tempfiles_dir(), "plugin-" + self.plugin_name )
        errorcode, path = find_or_make_any_directory(subdir)
        if errorcode:
            # should never happen, but make sure caller checks self.errorcode (set by fatal) just in case #####@@@@@
            errortext = path
            return self.fatal(errortext)
        self.working_directory = subdir
        return

    dialog = None
    param_desc_path_modtime = None
    
    def make_dialog_if_needed(self):
        "Create self.dialog if necessary."
        # For developers, remake the dialog from its description file each time that file changes.
        # (The point of only remaking it then is not speed, but to test the code when it doesn't get remade,
        #  since that's what always happens for non-developers.)
        # (Someday, when remaking it, copy its window geometry from the old one. Then put that code into the MMKit too. ###e)        
        # For others, only make it the first time.

        import __main__
        if (not __main__._end_user or env.debug()) and self.dialog:
            # For developers, remake the dialog if its description file changed (by zapping the old dialog here).
            zapit = False
            modtime = os.stat(self.param_desc_path).st_mtime
            if modtime != self.param_desc_path_modtime:
                zapit = True
                self.param_desc_path_modtime = modtime
            if zapit:
                #e save geometry?
                self.dialog.hide()
                self.dialog.destroy() ###k
                self.dialog = None
            pass
        if not self.dialog:
            if env.debug(): print "making dialog from", self.parameter_set_filename
            self.dialog = ParameterDialog( self.param_desc_path )### IMPLEM
            #e set its geometry if that was saved (from above code or maybe in prefs db)
        return
    
    def command_for_insert_menu(self):
        """Run an Insert Whatever menu command to let the user generate things using this plugin.
        """
        if self.errorcode:
            env.history.message(redmsg("Plugin %r is permanently disabled due to this error, reported previously: %s" % \
                               (self.plugin_name, self.errortext)))
            return
        self.create_working_directory_if_needed()
        assert not self.errorcode
        print 'ought to insert a', self.what_we_generate ###@@@
        self.make_dialog_if_needed()
        dialog = self.dialog
        ###e Not yet properly handled: retaining default values from last time it was used. (Should pass dict of them to the maker.)
        dialog.set_defaults({}) ### IMPLEM 
        controller = PluginlikeGenerator_DialogController(self)### IMPLEM
        dialog.set_controller( controller )### IMPLEM; this should refdecr the prior controller and that should destroy it...
        dialog.show()
        # now it's able to take commands and run its callbacks; that does not happen inside this method, though, does it?
        # hmm, good question... if it's modal, this makes things easier (re preview and bug protection)...
        # and it means the undo wrapping was ok... but what do we do here to make it modal?
        # 1. find out by test if other generators are modal.
        # 2. find out from code, how.
        
        pass###e
        
##    def commandline_args(self, params):
##        "Return the arguments for the HJ commandline, not including the output filename..." ###
##        return "stub"###e
##    def run_command(self, args):
##        ""
##        # get executable
##        # make filename
##        # run it
##        # look at exitcode
##        # etc

    pass # end of class PluginlikeGenerator

class HeterojunctionGenerator(PluginlikeGenerator):
    """Encapsulate the plugin-specific data and code (or references to it)
    for the CoNTub plugin's heterojunction command.
       In a real plugin API, this data would come from the plugin directory,
    and this code would be equivalent to either code in nE-1 parameterized by metadata in the plugin directory,
    and/or actual code in the plugin directory.
       (The present example is clearly simple enough to be the contents of a metadata file,
    but not all of the other built-in generators are that simple.)
    """
    topic = 'Nanotubes' # for sponsor_keyword for GeneratorBaseClass's SponsorableMixin superclass (and for submenu?)
    what_we_generate = "Heterojunction"
        # used for insert menu item text, undo cmdname, history messages; not sure about wikihelp featurename
    menu_item_icon = "blablabla"
    plugin_name = "CoNTub"
        # used as directory name, looked for in ~/Nanorex/Plugins someday, and in cad/plugins now and someday...
    parameter_set_filename = "HJ_param.desc"
    executable = "HJ" # no .exe, we'll add that if necessary on Windows ## this might not be required of every class
    outputfiles_pattern = "$out1.mmp"
    executable_args_pattern = "$p1 $p2 $out1.mmp"
    
    pass # end of class HeterojunctionGenerator

PluginlikeGenerator.register(HeterojunctionGenerator)

# end
