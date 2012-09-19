# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
GeneratorBaseClass.py -- DEPRECATED base class for generator dialogs
or their controllers, which supplies ok/cancel/preview logic and some
other common behavior. Sometimes abbreviated as GBC in docstrings,
comments, or identifier prefixes.

@author: Will
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Originated by Will

PM code added later by Ninad and/or Mark

Some comments and docstrings clarified for upcoming code review [bruce 070719]

TODO (as of 070719):

Needs refactoring so that:

 - a generator is a Command, but is never the same object as a
   PropertyManager (PM) -- at the moment, all GBC subclasses are also
   their own PMs except some experimental ones in
   test_commands.py. Our plans for the Command Sequencer and
   associated Command objects require this refactoring.  (After this
   refactoring, GBC will be the base class for generator *commands*,
   not for generator *dialogs*.)

 - no sponsor code appears here (it's an aspect of a PM, not of a
   Command, except insofar as a command needs a topic classification
   (e.g. sponsor keywords) which influences the choice of sponsor)

After discussion during a code review on 070724, it became clear that GBC needs
to be split into two classes, "generator command" and "generator PM", with much
of the "generator PM" part then getting merged into PropMgrBaseClass (or its
successor, PM_Dialog). These will have new names (not containing "BaseClass",
which is redundant). Tentative new names: GeneratorCommand, GeneratorPM.
The GeneratorPM class will contain the generator-specific parts of the button
click slots; the button-click method herein need to be split into their PM
and command-logic parts, when they're split between these classes.

Also needs generalization in several ways (mentioned but not fully explained):

 - extend API with subclasses to permit better error handling

 - extend API with subclasses to permit modifying an existing structure

  - permitting use for Edit Properties

  - helping support turning existing generators into "regenerators" for use
    inside "featurelike nodes"

"""

from PyQt4.Qt import Qt
from PyQt4.Qt import QApplication
from PyQt4.Qt import QCursor
from PyQt4.Qt import QWhatsThis

import foundation.env as env
from utilities import debug_flags

from utilities.Log import redmsg, orangemsg, greenmsg, quote_html
from utilities.Comparison import same_vals
from utilities.debug import print_compact_traceback
from utilities.constants import gensym
from utilities.constants import permit_gensym_to_reuse_name

from utilities.exception_classes import CadBug, PluginBug, UserError, AbstractMethod

# ==

class GeneratorBaseClass:
    ### REVIEW: docstring needs reorganization, and clarification re whether all
    # generators have to inherit it
    """
    DEPRECATED, and no longer used for supported commands as of circa 080727.
    (Still used for some test/example commands.)

    Mixin-superclass for use in the property managers of generator commands.
    In spite of the class name, this class only works when inherited *after*
    a property manager class (e.g. PM_Dialog) in a class's list of superclasses.

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
    done_btn_clicked, cancel_btn_clicked, close.
    """
    # default values of class constants; subclasses should override these as
    # needed
    cmd = "" # DEPRECATED, but widely used [bruce 060616 comment]
        # WARNING: subclasses often set cmd to greenmsg(self.cmdname + ": "),
        # from which we have to klugily deduce self.cmdname! Ugh.
    cmdname = "" # subclasses should set this to their (undecorated) command
        # name, for use by Undo and history. (Note: this name is passed to Undo
        # by calls from some methods here to assy.current_command_info.)
        # TODO: this attribute should be renamed to indicate that it's part of
        # a specific interface. (Right now it's a standard attribute name
        # used by convention in many files, and that renaming should be done
        # consistently to all of them at once if possible. Note that it is
        # used for several purposes (with more planned in the future), not
        # only for Undo. Note that a "command metadata interface" might
        # someday include other attributes besides the name.)
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
                if debug_flags.atom_debug:
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
        Build the structure (model object) which this generator is supposed
        to generate. This is an abstract method and must be overloaded in
        the specific generator.

        (WARNING: I am guessing the standard type names for tuple and
        position.)

        @param name: The name which should be given to the toplevel Node of the
                     generated structure. The name is also passed in self.name.
                     (TODO: remove one of those two ways of passing that info.)
                     The caller will emit history messages which assume this
                     name is used. If self.create_name_from_prefix is true,
                     the caller will have set this name to self.prefix appended
                     with a serial number.
        @type  name: str

        @param params: The parameter tuple returned from
                       self.gather_parameters(). For more info,
                       see docstring of gather_parameters in this class.
        @type  params: tuple

        @param position: The position in 3d model space at which to
                         create the generated structure. (The precise
                         way this is used, if at all, depends on the
                         specific generator.)
        @type position:  position

        @return: The new structure, i.e. some flavor of a Node, which
                 has not yet been added to the model.  Its structure
                 should depend only on the values of the passed
                 params, since if the user asks to build twice, this
                 method may not be called if the params have not
                 changed.
        """
        raise AbstractMethod()

    def remove_struct(self):
        """
        Private method. Remove the generated structure, if one has been built.
        """
        ### TODO: rename to indicate it's private.
        if self.struct != None:
            self.struct.kill()
                # BUG: Ninad suspects this (or a similar line) might be
                # implicated in bug 2045. [070724 code review]
            self.struct = None
            self.win.win_update() # includes mt_update
        return

    # Note: when we split this class, the following methods will be moved into
    # GeneratorPM and/or PM_Dialog (or discarded if they are already overridden
    # correctly by PM_Dialog):
    # - all xxx_btn_clicked methods (also to be renamed, btn -> button)
    # - close
    # [070724 code review]

    def restore_defaults_btn_clicked(self):
        """Slot for the Restore Defaults button."""
        ### TODO: docstring needs to say under what conditions this should be
        # overridden.
        ### WARNING: Mark says this is never called in practice, since it's
        # overridden by the same method in PropMgrBaseClass, and that this
        # implementation is incorrect and can be discarded when we refactor
        # this class.
        # [070724 code review]
        if debug_flags.atom_debug:
            print 'restore defaults button clicked'

    def preview_btn_clicked(self):
        """Slot for the Preview button."""
        if debug_flags.atom_debug:
            print 'preview button clicked'
        self.change_random_seed()
        self._ok_or_preview(previewing = True)

    def ok_btn_clicked(self):
        """Slot for the OK button."""
        ### NEEDS RENAMING, ok -> done -- or merging with existing
        # done_btn_clicked method, below! The existence of both those methods
        # makes me wonder whether this one is documented correctly as being
        # the slot [bruce 070725 comment].
        ### WARNING: Mark says PropMgrBaseClass depends on its subclasses
        # inheriting this method. This should be fixed when we refactor.
        # (Maybe this is true for some other _btn_clicked methods as well.)
        # [070724 code review]
        if debug_flags.atom_debug:
            print 'ok button clicked'
        self._gensym_data_for_reusing_name = None # make sure gensym-assigned
            # name won't be reused next time
        self._ok_or_preview(doneMsg = True)
        self.change_random_seed() # for next time
        if not self.pluginException:
            # if there was a (UserError, CadBug, PluginBug) then behave
            # like preview button - do not close the dialog
            ###REVIEW whether that's a good idea in case of bugs
            # (see also the comments about return value of self.close(),
            #  which will be moved to GeneratorPM when we refactor)
            # [bruce 070615 comment & 070724 code review]
            self.accept()
        self.struct = None

        # Close property manager. Fixes bug 2524. [Mark 070829]
        # Note: this only works correctly because self.close comes from
        # a PM class, not from this class. [bruce 070829 comment]
        self.close()

        return

    def handlePluginExceptions(self, aCallable):
        """
        Execute aCallable, catching exceptions and handling them
        as appropriate.

        (WARNING: I am guessing the standard type name for a callable.)

        @param aCallable: any Python callable object, which when
                          called with no arguments implements some
                          operation within a generator.
        @type  aCallable: callable
        """
        # [bruce 070725 renamed thunk -> aCallable after code review]
        ### TODO: teach the exceptions caught here to know how to make these
        # messages in a uniform way, to simplify this code.
        # [070724 code review]
        self.pluginException = False
        try:
            return aCallable()
        except CadBug, e:
            reason = "Bug in the CAD system"
        except PluginBug, e:
            reason = "Bug in the plug-in"
        except UserError, e:
            reason = "User error"
        except Exception, e:
            #bruce 070518 revised the message in this case,
            # and revised subsequent code to set self.pluginException
            # even in this case (since I am interpreting it as a bug)
            reason = "Exception" #TODO: should improve, include exception name
        print_compact_traceback(reason + ": ")
        env.history.message(redmsg(reason + ": " +
                                   quote_html(" - ".join(map(str, e.args))) ))
        self.remove_struct()
        self.pluginException = True
        return

    def _ok_or_preview(self, doneMsg = False, previewing = False):
        """
        Private method. Do the Done or Preview operation (and set the
        Qt wait cursor while doing it), according to flags.
        """
        ### REVIEW how to split this between GeneratorCommand and GeneratorPM,
        # and how to rename it then
        # [070724 code review]
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.win.assy.current_command_info(cmdname = self.cmdname)
        def aCallable():
            self._build_struct(previewing = previewing)
            if doneMsg:
                env.history.message(self.cmd + self.done_msg())
        self.handlePluginExceptions(aCallable)
        QApplication.restoreOverrideCursor()
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
        abstract method which must be overloaded in the specific
        generator. Each subclass (specific generator) determines
        how many parameters are contained in this tuple, and in
        what order. The superclass code assumes only that the
        param tuple can be correctly compared by same_vals.

        This method must validate the parameters, and
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
        """
        Private method. Called internally when we discard the current structure
        and want to permit a number which was appended to its name to be reused.

        WARNING: the current implementation only works for classes which set
        self.create_name_from_prefix
        to cause our default _build_struct to set the private attr we use
        here, self._gensym_data_for_reusing_name, or which set it themselves
        in the same way (when they call gensym).
        """
        if self._gensym_data_for_reusing_name:
            prefix, name = self._gensym_data_for_reusing_name
                # this came from our own call of gensym, or from a caller's if
                # it decides to set that attr itself when it calls gensym
                # itself.
            permit_gensym_to_reuse_name(prefix, name)
        self._gensym_data_for_reusing_name = None
        return

    def _build_struct(self, previewing = False):
        """Private method. Called internally to build the structure
        by calling the (generator-specific) method build_struct
        (if needed) and processing its return value.
        """
        params = self.gather_parameters()

        if self.struct is None:
            # no old structure, we are making a new structure
            # (fall through)
            pass
        elif not same_vals( params, self.previousParams):
            # parameters have changed, update existing structure
            self._revert_number()
            # (fall through, using old name)
            pass
        else:
            # old structure, parameters same as previous, do nothing
            return

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix, self.win.assy) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name

        if previewing:
            env.history.message(self.cmd + "Previewing " + name)
        else:
            env.history.message(self.cmd + "Creating " + name)
        self.remove_struct()
        self.previousParams = params
        self.struct = self.build_struct(name, params, - self.win.glpane.pov)
        self.win.assy.addnode(self.struct)
        # Do this if you want it centered on the previous center.
        # self.win.glpane.setViewFitToWindow(fast = True)
        # Do this if you want it centered on the origin.
        self.win.glpane.setViewRecenter(fast = True)
        self.win.win_update() # includes mt_update

        return

    def done_btn_clicked(self):
        "Slot for the Done button"
        if debug_flags.atom_debug:
            print "done button clicked"
        self.ok_btn_clicked()

    def cancel_btn_clicked(self):
        "Slot for the Cancel button"
        if debug_flags.atom_debug:
            print "cancel button clicked"
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
        self.remove_struct()
        self._revert_number()
        self.reject()

        # Close property manager. Fixes bug 2524. [Mark 070829]
        # Note: this only works correctly because self.close comes from
        # a PM class, not from this class. [bruce 070829 comment]
        self.close()

        return

    def close(self, e = None):
        """
        When the user closes the dialog by clicking the 'X' button
        on the dialog title bar, do whatever the cancel button does.
        """
        print "\nfyi: GeneratorBaseClass.close(%r) was called" % (e,)
            # I think this is never called anymore,
            # and would lead to infinite recursion via cancel_btn_clicked
            # (causing bugs) if it was. [bruce 070829]

        # Note: Qt wants the return value of .close to be of the correct type,
        # apparently boolean; it may mean whether to really close (just a guess)
        # (or it may mean whether Qt needs to process the same event further,
        #  instead)
        # [bruce 060719 comment, updated after 070724 code review]
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
