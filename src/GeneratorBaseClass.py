# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GeneratorBaseClass.py -- base class for generator dialogs or their controllers
which supplies ok/cancel/preview logic and some other common behavior.
Sometimes abbreviated as GBC in docstrings, comments, or identifier prefixes.

$Id$

History:

Originated by Will

PM code added later by Ninad and/or Mark

Some comments and docstrings clarified for upcoming code review [bruce 070719]

TODO (as of 070719):

Needs refactoring so that:

- a generator is a Command, but is never the same object
  as a PropertyManager (PM) -- at the moment, all GBC subclasses are also their
  own PMs except some experimental ones in test_commands.py. Our plans for the
  Command Sequencer and associated Command objects require this refactoring.
  (After this refactoring, GBC will be the base class for generator *commands*,
  not for generator *dialogs*.)

- no sponsor code appears here (it's an aspect of a PM, not of a Command, except
  insofar as a command needs a topic classification (e.g. sponsor keywords)
  which influences the choice of sponsor)

Also needs generalization in several ways (mentioned but not fully explained):

- extend API with subclasses to permit better error handling

- extend API with subclasses to permit modifying an existing structure

  - permitting use for Edit Properties

  - helping support turning existing generators into "regenerators" for use
    inside "featurelike nodes"

"""

__author__ = "Will"


from PyQt4.Qt import Qt
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QIcon
from PyQt4.Qt import QApplication
from PyQt4.Qt import QCursor
from PyQt4.Qt import QWhatsThis

import env
import platform

from Sponsors import SponsorableMixin
from PropertyManagerMixin import PropertyManagerMixin
from HistoryWidget import redmsg, orangemsg, greenmsg, quote_html
from debug import print_compact_traceback
from constants import gensym
from constants import permit_gensym_to_reuse_name

# == private definitions

# REVIEW: AbstractMethod should either be renamed to look private, or be moved
# to a more general place and used more widely. [bruce 070719 comment]

class AbstractMethod(Exception):
    def __init__(self):
        Exception.__init__(self, 'Abstract method - must be overloaded')

# == public exception classes for use by our client subclasses

# REVIEW: I think these would benefit from being renamed with a GBC_ prefix,
# unless we decide they're more general and can be used in any Command,
# in which case they should be moved, and some other prefix would be better.
# REVIEW: I suspect these exceptions are not handled in the best way, and in
# particular, I am not sure it's useful to have a CadBug exception class,
# given that any unexpected exception (of any class) also counts as a "bug
# in the cad code".
# [bruce 070719 comments]

class CadBug(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg=None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)

class PluginBug(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg=None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)

class UserError(Exception):
    """
    Useful for distinguishing between an exception from subclass
    code which is a bug in the cad, a report of an error in the
    plugin, or a report of a user error.
    """
    def __init__(self, arg=None):
        if arg is not None:
            Exception.__init__(self, arg)
        else:
            Exception.__init__(self)

# ==

class GeneratorBaseClass(SponsorableMixin):
    ### REVIEW: docstring needs reorganization, and clarification re whether all
    # generators have to inherit it
    """
    Superclass for generator commands.
       TODO: needs refactoring and generalization as described in module
    docstring. In particular, it should not inherit from SponsorableMixin, and
    subclasses should not be required to inherit from QDialog, though both of
    those are the case at present [070719].
       Background: There is some logic associated with Preview/OK/Abort for any
    structure generator command that's complicated enough to put in one place,
    so that individual generators can focus on building a structure, rather than
    on the generic logic of a generator or its GUI.
       Note: this superclass sets and maintains some attributes in self,
    including win, struct, previousParams, and name.
       Here are the things a subclass needs to do, to be usable with this
    superclass [as of 060621]:
    - have self.sponsor_btn, a Qt button of a suitable class.
    - bind or delegate button clicks from a generator dialog's standard buttons
      to all our xxx_btn_clicked methods (not sure about sponsor_btn). ###VERIFY
    - implement the abstract methods (see their docstrings herein for what they
      need to do):
      - gather_parameters
      - build_struct
    - provide self.prefix, apparently used to construct node names (or, override
      self._create_new_name())
    - either inherit from QDialog, or provide methods accept and reject which
      have the same effect on the actual dialog.
    [As of bruce 070719 I am not sure if not inheriting QDialog is possible.]
    There are some other methods here that merit mentioning: 
    enter_WhatsThisMode, whatsthis_btn_clicked, done_btn_clicked,
    abort_btn_clicked, cancel_btn_clicked, close.
    """
    # default values of class constants; subclasses should override these as
    # needed
    cmd = "" # DEPRECATED, but widely used [bruce 060616 comment]
        # WARNING: subclasses often set cmd to greenmsg(self.cmdname + ": "),
        # from which we have to klugily deduce self.cmdname! Ugh.
    cmdname = "" # subclasses should set this to their (undecorated) command
        # name, for use by Undo and history.
    create_name_from_prefix = True # whether we'll create self.name from
        # self.prefix (by appending a serial number)
    
    def __init__(self, win):
        """
        @param win: the main window object
        """
        self.win = win
        self.pw = None # pw = part window. Its subclasses will create their
            # partwindow objects (and destroy them after Done)
            ###REVIEW: I think this (assignment or use of self.pw) does not
            # belong in this class [bruce 070615 comment]
            
        self.struct = None
        self.previousParams = None
        #bruce 060616 added the following kluge to make sure both cmdname and
        # cmd are set properly.
        if not self.cmdname and not self.cmd:
            self.cmdname = "Generate something"
        if self.cmd and not self.cmdname:
            # deprecated but common, as of 060616
            self.cmdname = self.cmd # fallback value; usually reassigned below
            try:
                cmdname = self.cmd.split('>')[1]
                cmdname = cmdname.split('<')[0]
                cmdname = cmdname.split(':')[0]
                self.cmdname = cmdname
            except:
                if platform.atom_debug:
                    print "fyi: %r guessed wrong about format of self.cmd == %r" \
                          % (self, self.cmd,)
                pass
        elif self.cmdname and not self.cmd:
            # this is intended to be the usual situation, but isn't yet, as of
            # 060616
            self.cmd = greenmsg(self.cmdname + ": ")
        self.change_random_seed()
        return
    
    def build_struct(self, name, params, position):
        """
        Build the structure (model object) in question. This is an abstract
        method and must be overloaded in the specific generator.
           The arguments include the parameter tuple returned from
        self.gather_parameters(). The return value should be the new structure,
        i.e. some flavor of a Node, which has not yet been added to the model.
        Its structure should depend only on the values of the passed params,
        since if the user asks to build twice, this method may not be called if
        the params have not changed.
           By convention (and to fit with history messages emitted from this
        class), the new node's name should be set to name (or to self.name,
        always equal to name), which (if self.create_name_from_prefix is true)
        the caller will have set to self.prefix appended with a serial number.
        """
        raise AbstractMethod()

    def remove_struct(self):
        if platform.atom_debug: print 'Should we remove an existing structure?'
        if self.struct != None:
            if platform.atom_debug: print 'Yes, remove it'
            self.struct.kill()
            self.struct = None
            self.win.win_update() # includes mt_update
        else:
            if platform.atom_debug: print 'No structure to remove'

    def restore_defaults_btn_clicked(self):
        """Slot for the Restore Defaults button."""
        if platform.atom_debug: print 'restore defaults button clicked'
        
    def preview_btn_clicked(self):
        if platform.atom_debug: print 'preview button clicked'
        self.change_random_seed()
        self._ok_or_preview(previewing=True)
    
    def ok_btn_clicked(self):
        """Slot for the OK button."""
        if platform.atom_debug: print 'ok button clicked'
        self._gensym_data_for_reusing_name = None # make sure gensym-assigned
            # name won't be reused next time
        self._ok_or_preview(doneMsg = True)
        self.change_random_seed() # for next time
        if not self.pluginException:
            # if there was a (UserError, CadBug, PluginBug) then behave
            # like preview button - do not close the dialog
            ###REVIEW whether that's a good idea in case of bugs
            # [bruce 070615 comment]
            self.accept()
        self.struct = None
        
        # Close property manager
        ###REVIEW: I think this does not belong in this class
        # [bruce 070615 comment]
        if self.pw:
            self.pw.featureManager.setCurrentIndex(0)
            self.pw.featureManager.removeTab(
                self.pw.featureManager.indexOf(self) )
            self.pw = None
                    
        return

    def handlePluginExceptions(self, thunk):
        self.pluginException = False
        try:
            return thunk()
        except CadBug, e:
            explan = "Bug in the CAD system"
        except PluginBug, e:
            explan = "Bug in the plug-in"
        except UserError, e:
            explan = "User error"
        except Exception, e:
            #bruce 070518 revised the message in this case,
            # and revised subsequent code to set self.pluginException
            # even in this case (since I am interpreting it as a bug)
            explan = "Exception" #TODO: should improve, include exception name
        print_compact_traceback(explan + ": ")
        env.history.message(redmsg(explan + ": " +
                                   quote_html(" - ".join(map(str, e.args))) ))
        self.remove_struct()
        self.pluginException = True
        return
    
    def _ok_or_preview(self, doneMsg = False, previewing = False):
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.win.assy.current_command_info(cmdname = self.cmdname)
        def thunk():
            self._build_struct(previewing = previewing)
            if doneMsg:
                env.history.message(self.cmd + self.done_msg())
        self.handlePluginExceptions(thunk)
        QApplication.restoreOverrideCursor() # Restore the cursor
        self.win.win_update()

    def change_random_seed(self): #bruce 070518 added this to API
        """
        If the generator makes use of randomness in gather_parameters,
        it may do so deterministically based on a saved random seed;
        if so, this method should be overloaded in the specific generator
        to change the random seed to a new value (or do the equivalent).
        """
        return

    def gather_parameters(self):
        """
        Return a tuple of the current parameters. This is an
        abstract method and must be overloaded in the specific
        generator. This method must validate the parameters, or
        raise an exception if they are invalid.
        """
        raise AbstractMethod()

    def done_msg(self):
        """
        Return the message to print in the history when the structure has been
        built. This may be overloaded in the specific generator.
        """
        return "%s created." % self.name

    _gensym_data_for_reusing_name = None
    
    def _revert_number(self):
        ###TODO: this method needs a docstring. Once a good one is added,
        # the historical comments here should be removed. (They are probably
        # not very useful except to their author, but they might help their
        # author create a correct docstring.) [bruce 070723 comment]
        # 
        #bruce 070603-04: removing the Gno & ViewNum parts of revert_number,
        # since they won't work properly with the new gensym.
        # Instead, we do it differently now.
        #   Note: this only helps classes which set self.create_name_from_prefix
        # to cause our default _build_struct to set the private attr we use
        # here, self._gensym_data_for_reusing_name, or which set it themselves
        # in the same way (when they call gensym).
        if self._gensym_data_for_reusing_name:
            prefix, name = self._gensym_data_for_reusing_name
                # this came from our own call of gensym, or from a caller's if
                # it decides to set that attr itself when it calls gensym
                # itself.
            permit_gensym_to_reuse_name(prefix, name)
        self._gensym_data_for_reusing_name = None
        return

    def _build_struct(self, previewing = False):
        if platform.atom_debug:
            print '_build_struct'
        params = self.gather_parameters()

        if self.struct == None:
            if platform.atom_debug:
                print 'no old structure, we are making a new structure'
        elif params != self.previousParams:
            if platform.atom_debug:
                print 'parameters have changed, update existing structure'
            self._revert_number()
            # fall through, using old name
        else:
            if platform.atom_debug:
                print 'old structure, parameters same as previous, do nothing'
            return

        # self.name needed for done message
        if self.create_name_from_prefix:
            # DNA, Nanotubes and Graphene don't have a name yet. Let's create
            # it.
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
                #bruce 070604 new feature
            if platform.atom_debug:
                print "Created name from prefix. Name =", name
        else:
            # Jigs like the rotary and linear motors already created their name,
            # so we need to use it.
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
            if platform.atom_debug:
                print "Used existing (jig) name =", name
        
        if previewing:
            env.history.message(self.cmd + "Previewing " + name)
        else:
            env.history.message(self.cmd + "Creating " + name)
        self.remove_struct()
        self.previousParams = params
        if platform.atom_debug: print "build a new structure"
        self.struct = self.build_struct(name, params, -self.win.glpane.pov)
        self.win.assy.addnode(self.struct)
        # Do this if you want it centered on the previous center.
        # self.win.glpane.setViewFitToWindow(fast = True)
        # Do this if you want it centered on the origin.
        self.win.glpane.setViewRecenter(fast = True)
        self.win.win_update() # includes mt_update

    def enter_WhatsThisMode(self):
        "Slot for the What's This button"
        QWhatsThis.enterWhatsThisMode()

    def whatsthis_btn_clicked(self):
        "Slot for the What's This button"
        QWhatsThis.enterWhatsThisMode()
    
    def done_btn_clicked(self):
        "Slot for the Done button"
        if platform.atom_debug: print "done button clicked"
        self.ok_btn_clicked()

    def abort_btn_clicked(self):
        "Slot for the Abort button"
        self.cancel_btn_clicked()

    def cancel_btn_clicked(self):
        "Slot for the Cancel button"
        if platform.atom_debug: print "cancel button clicked"
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        self.remove_struct()
        self._revert_number()
        self.reject()
        
        # Close property manager
        ###REVIEW: I think this does not belong in this class
        # [bruce 070615 comment]
        if self.pw:
            self.pw.featureManager.setCurrentIndex(0)
            self.pw.featureManager.removeTab(
                self.pw.featureManager.indexOf(self.pw.propertyManagerScrollArea) )
            self.pw = None 
            
        return

    def close(self, e = None):
        """
        When the user closes the dialog by clicking the 'X' button
        on the dialog title bar, do whatever the cancel button does.
        """
        # Note: Qt wants the return value of .close to be of the correct type,
        # apparently boolean; it may mean whether to really close (just a guess)
        # [bruce 060719 comment]
        try:
            self.cancel_btn_clicked()
            return True
        except:
            #bruce 060719: adding this print, since an exception here is either
            # an intentional one defined in this file (and should be reported as
            # an error in history -- if this happens we need to fix this code to
            # do that, maybe like _ok_or_preview does), or is a bug. Not
            # printing anything here would always hide important info, whether
            # errors or bugs.
            print_compact_traceback("bug in cancel_btn_clicked, or in not reporting an error it detected: ")
            return False
        
    pass # end of class GeneratorBaseClass

# end
