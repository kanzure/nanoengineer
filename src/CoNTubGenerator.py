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

__author__ = "bruce"

#k not all imports needed?
## from GeneratorDialogs import ParameterizedDialog ###IMPLEM file and class
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
from widgets import double_fixup
from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass



def add_insert_menu_item(win, command, name_of_what_to_insert, options = ()): ###e this should be a method of MWsemantics.py
    menuIndex = 2 ### kluge - right after Nanotube, at the moment (since indices start from 0)
    menu = win.Insert
    menutext = "%s" % (name_of_what_to_insert,)
    undo_cmdname = "Insert %s" % (name_of_what_to_insert,) ###e USE THIS -- pass as new option to insert_command_into_menu??
        ###e but need to translate it ourselves, ##qApp.translate("Main Window", "Recent Files", None)
    ## self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
    from widgets import insert_command_into_menu
    insert_command_into_menu( menu, menutext, command, options = options, position = menuIndex)
    return

class PluginlikeGenerator:
    """Superclass for generators whose code is organized similar to that of a (future) plugin.
    Subclasses contain data and methods which approximate the functionality
    of metadata and/or code that would ultimately be found in a plugin directory.
    See the example subclass in this file for details.
    """
    ok_to_install_in_UI = False # changed to True in instances which become ok to install into the UI
    # default values of subclass-specific class constants
    what_we_generate = "Something"
    def register(subclass): # staticmethod
        win = env.mainwindow()
        instance = subclass(win)
        if instance.ok_to_install_in_UI:
            instance.install_in_UI()
            print "registered",instance###
        else:
            print "didn't register",instance###
        return
    register = staticmethod(register)
    def __init__(self, win):
        self.win = win
        # using submethods:
        
        # find plugin dir -- if not, error, and don't install in UI
        # (as if we don't know the metadata needed to do so)

        self.ok_to_install_in_UI = True

        pass
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
    def install_in_UI(self):
        assert self.ok_to_install_in_UI
        #e create whatever we want to be persistent, like a dialog or pane, job dir...
        0
        #e install the necessary commands in the UI (eg in insert menu)
        ### WRONG -- menu text should not contain Insert, but undo cmdname should (so separate option is needed), and needs icon
        ###e add options for things like tooltip text, whatsthis text, iconset
        options = [('iconset','junk.png')]
        add_insert_menu_item( self.win, self.insert_menu_command, self.what_we_generate, options)
        pass
    def insert_menu_command(self):
        """Run an Insert Whatever menu command to let the user generate things using this plugin.
        """
        print 'ought to insert a', self.what_we_generate
        pass###e
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
    parameter_set_filename = "HJ_param_desc.txt" #e or .desc?
    executable = "HJ" # no .exe, we'll add that if necessary on Windows ## this might not be required of every class
    outputfiles_pattern = "$out1.mmp"
    executable_args_pattern = "$p1 $p2 $out1.mmp"
    
    pass # end of class HeterojunctionGenerator

PluginlikeGenerator.register(HeterojunctionGenerator)

# end
