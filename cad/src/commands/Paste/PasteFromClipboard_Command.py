# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PasteFromClipboard_Command.py

PasteFromClipboard_Command allows depositing clipboard items into the 3D workspace.
Its property manager lists the'pastable' clipboard items and also shows the
current selected item in its 'Preview' box. User can return to previous mode by
hitting 'Escape' key or pressing 'Done' button in the Paste mode.

@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2007-08-29: Created.
Ninad 2008-01-02: Moved several methods originally in class depositMode to
                  PasteFromClipboard_Command.
Ninad 2008-08-02: refactored into command and graphics mode classes, other things
needed for the command stack refactoring project.

TODO:
- some methods in Command and GraphicsMode part are not appropriate in those classes
eg. deposit_from_MMKit method in the Graphicsmode class. This will need further
clanup.
- rename PasteFromClipboard_Command to PastFromClipboard_Command
"""

from foundation.Group import Group
from model.chem import Atom
from model.chunk import Chunk
from model.elements import Singlet
from operations.pastables import is_pastable

from operations.pastables import find_hotspot_for_pasting
from model.bonds import bond_at_singlets

from utilities.Comparison import same_vals

from commands.Paste.PastePropertyManager import PastePropertyManager
from commands.BuildAtoms.BuildAtoms_Command import BuildAtoms_Command
from ne1_ui.toolbars.Ui_PasteFromClipboardFlyout import PasteFromClipboardFlyout
from commands.Paste.PasteFromClipboard_GraphicsMode import PasteFromClipboard_GraphicsMode

_superclass = BuildAtoms_Command

class PasteFromClipboard_Command(BuildAtoms_Command):
    """
    PasteFromClipboard_Command allows depositing clipboard items into the 3D workspace.
    Its property manager lists the 'pastable' clipboard items and also shows the
    current selected item in its 'Preview' box. User can return to previous mode
    by hitting 'Escape' key  or pressing 'Done' button in the Paste mode.
    """
    commandName = 'PASTE'
    featurename = "Paste From Clipboard"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC


    #Don't resume previous mode (buggy if set to True) [ninad circa 080102]
    command_should_resume_prevMode = False

    #See Command.anyCommand for details about the following flag
    command_has_its_own_PM = True

    #GraphicsMode
    GraphicsMode_class = PasteFromClipboard_GraphicsMode

    #Property Manager
    PM_class = PastePropertyManager

    #Flyout Toolbar
    FlyoutToolbar_class = PasteFromClipboardFlyout

    def __init__(self, commandSequencer):
        """
        Constructor for the class PasteFromClipboard_Command. PasteFromClipboard_Command allows depositing
        clipboard items into the 3D workspace. Its property manager lists the
        'pastable' clipboard items and also shows the current selected item
        in its 'Preview' box. User can return to previous mode by hitting
        'Escape' key  or pressing 'Done' button in the Paste mode.
        @param commandSequencer: The command sequencer (GLPane) object
        """
        self.pastables_list = [] #@note: not needed here?
        self._previous_model_changed_params = None
        _superclass.__init__(self, commandSequencer)


    def command_entered(self):
        """
        Overrides superclass method
        @see: baseCommand.command_entered() for documentation.
        """
        _superclass.command_entered(self)
        self.pastable = None #k would it be nicer to preserve it from the past??
                # note, this is also done redundantly in init_gui.
        self.pastables_list = []
            # should be ok, since model_changed comes after this...

    def command_update_internal_state(self):
        """
        Extends superclass method.
        @see: baseCommand.command_update_internal_state()
        @see: PastePropertyManager._update_UI_do_updates()
        """
        _superclass.command_update_internal_state(self)

        currentParams = self._current_model_changed_params()

        #Optimization. Return from the model_changed method if the
        #params are the same.
        if same_vals(currentParams, self._previous_model_changed_params):
            return

        #update the self._previous_model_changed_params with this new param set.
        self._previous_model_changed_params = currentParams

        #This was earlier -- self.update_gui_0()
        self._update_pastables_list()

    def _current_model_changed_params(self):
        """
        Returns a tuple containing the parameters that will be compared
        against the previously stored parameters. This provides a quick test
        to determine whether to do more things in self.model_changed()
        @see: self.model_changed() which calls this
        @see: self._previous_model_changed_params attr.
        """
        params = None

        memberList = []

        try:
            ###@@@@ need this to avoid UnboundLocalError: local variable 'shelf'
            ##referenced before assignment
            # but that got swallowed the first time we entered mode!
            # but i can't figure out why, so neverind for now [bruce 050121]
            shelf = self.glpane.assy.shelf
            if hasattr(shelf, 'members'):
                memberList = list(shelf.members)
            else:
                memberList = [shelf]
        except AttributeError:
            # this is normal, until I commit new code to Utility and model tree!
            #[bruce 050121]
            pass

        params = (memberList)

        return params

    def _update_pastables_list(self): #bruce 050121 split this out and heavily revised it
        """
        """

        #UPDATE 2008-08-20:
        # This method was earlier update_gui_0() which was called from
        # 'def update_gui()'. All update_gui_* methods have been removed 080821.
        #See model_changed() method where this method is called.
        #Note that the code in this method is old and needs to be revised
        #-- [Ninad comment]


        # [Warning, bruce 050316: when this runs, new clipboard items might not
        # yet have
        # their own Part, or the correct Part! So this code should not depend
        # on the .part member of any nodes it uses. If this matters, a quick
        # (but inefficient) fix would be to call that method right here...
        # except that it might not be legal to do so! Instead, we'd probably
        # need
        # to arrange to do the actual updating (this method) only at the end of
        # the current user event. We'll need that ability pretty soon for other
        # reasons (probably for Undo), so it's ok if we need it a bit sooner.]

        # Subclasses update the contents of self.propMgr.clipboardGroupBox
        # (Note; earlier depositMode used to update self.w.pasteComboBox items,
        # but this implementation has been changed since 2007-09-04 after
        # introduction of L{PasteFromClipboard_Command})
        # to match the set of pastable objects on the clipboard,
        # which is cached in pastables_list for use,
        # and update the current item to be what it used to be (if that is
        # still available in the list), else the last item (if there are any
        # items).

        #First update self.pastable
        if not self.pastable:
            self.update_pastable()

        # update the list of pastable things - candidates are all objects
        # on the clipboard
        members = self.o.assy.shelf.members[:]
        ## not needed or correct since some time ago [bruce 050110]:
        ##   members.reverse() # bruce 041124 -- model tree seems to have them
        ##backwards
        self.pastables_list = filter( is_pastable, members)

        # experiment 050122: mark the clipboard items to influence their
        #appearance
        # in model tree... not easy to change their color, so maybe we'll let
        # this
        # change their icon (just in chunk.py for now). Not yet done. We'd
        # like the
        # one equal to self.pastable (when self.depositState == 'Clipboard'
        # and this is current mode)
        # to look the most special. But that needs to be recomputed more often
        # than this runs. Maybe we'll let the current mode have an
        # mtree-icon-filter??
        # Or, perhaps, let it modify the displayed text in the mtree,
        # from node.name. ###@@@
        for mem in members:
            mem._note_is_pastable = False # set all to false...
        for mem in self.pastables_list:
            mem._note_is_pastable = True # ... then change some of those to true

        if not self.pastables_list:
            # insert a text label saying why spinbox is empty [bruce 041124]
            if members:
                whynot = "(no clips are pastable)" # this text should not be
                #longer than the one below, for now
            else:
                whynot = "(clipboard is empty)"
            self.pastable = None
        else:
            # choose the best current item for self.pastable and spinbox
            # position
            # (this is the same pastable as before, if it's still available)
            if self.pastable not in self.pastables_list: # (works even if
                #self.pastable is None)
                self.pastable = self.pastables_list[-1]
                # use the last one (presumably the most recently added)
                # (no longer cares about selection of clipboard items
                #-- bruce 050121)
            assert self.pastable # can fail if None is in the list or "not in"
            #doesn't work right for None

        #e future: if model tree indicates self.pastable somehow, e.g. by color
        #of its name, update it. (It might as well also show "is_pastables"
        #that way.) ###@@@ good idea...

        return

    def update_pastable(self):
        """
        Update self.pastable based on current selected pastable
        in the clipboard
        """
        members = self.o.assy.shelf.members[:]
        self.pastables_list = filter( is_pastable, members)

        try:
            cx = self.propMgr.clipboardGroupBox.currentRow()
            self.pastable = self.pastables_list[cx]
        except: # various causes, mostly not errors
            self.pastable = None
        return

    def MMKit_clipboard_part(self): #bruce 060412; implem is somewhat of a
        #guess, based on the code of self.deposit_from_MMKit
        """
        If the MMKit is currently set to a clipboard item, return that item's
        Part, else return None.
        """
        if not self.pastable:
            return None
        return self.pastable.part

    def deposit_from_Clipboard_page(self, atom_or_pos):
        """
        Deposit the clipboard item being previewed into the 3D workspace
        Called in L{self.deposit_from_MMKit}
        @attention: This method needs renaming. L{depositMode} still uses this
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_MMKit}
        """
        self.update_pastable()

        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if self.pastable: # bond clipboard object to the singlet
                    # do the following before <a> (the singlet) is killed
                    a0 = a.singlet_neighbor()
                    chunk, desc = self.pasteBond(a)
                    if chunk:
                        status = "replaced bondpoint on %r with %s" % (a0, desc)
                    else:
                        status = desc
                else:
                    #Nothing selected from the Clipboard to paste, so do nothing
                    status = "nothing selected to paste" #k correct??
                    chunk = None
        else:
            if self.pastable:
                # deposit into empty space at the cursor position
                chunk, status = self.pasteFree(atom_or_pos)
            else:
                # Nothing selected from the Clipboard to paste, so do nothing
                status = "Nothing selected to paste"
                chunk = None

        return chunk, status

    # paste the pastable object where the cursor is (at pos)
    # warning: some of the following comment is obsolete (read all of it for
    # the details)
    # ###@@@ should clean up this comment and code
    # - bruce 041206 fix bug 222 by recentering it now --
    # in fact, even better, if there's a hotspot, put that at pos.
    # - bruce 050121 fixing bug in feature of putting hotspot on water
    # rather than center. I was going to remove it, since Ninad disliked it
    # and I can see problematic aspects of it; but I saw that it had a bug
    # of picking the "first singlet" if there were several (and no hotspot),
    # so I'll fix that bug first, and also call fix_bad_hotspot to work
    # around invalid hotspots if those can occur. If the feature still seems
    # objectionable after this, it can be removed (or made a nondefault
    # preference).
    # ... bruce 050124: that feature bothers me, decided to remove it
    #completely.
    def pasteFree(self, pos):
        self.update_pastable()
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable!
            # (if we're operating in the same clipboard item it's stored in,
            #  and if adding numol makes that item no longer pastable.)
            # And someday the copy operation itself might auto-addmol, for
            # some reason; so to be safe, save pastable here before we change
            # current part at all.

        chunk, status = self.o.assy.paste(pastable, pos)
        return chunk, status

    def pasteBond(self, sing):
        """
        If self.pastable has an unambiguous hotspot,
        paste a copy of self.pastable onto the given singlet;
        return (the copy, description) or (None, whynot)
        """
        self.update_pastable()
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable! See comments in
            #pasteFree.
        # bruce 041123 added return values (and guessed docstring).
        # bruce 050121 using subr split out from this code
        ok, hotspot_or_whynot = find_hotspot_for_pasting(pastable)
        if not ok:
            whynot = hotspot_or_whynot
            return None, whynot

        hotspot = hotspot_or_whynot

        if isinstance(pastable, Chunk):
            numol = pastable.copy_single_chunk(None)
            hs = numol.hotspot or numol.singlets[0]
                # todo: should use find_hotspot_for_pasting again
            bond_at_singlets(hs,sing) # this will move hs.molecule (numol) to match
            # bruce 050217 comment: hs is now an invalid hotspot for numol,
            # and that used to cause bug 312, but this is now fixed in getattr
            # every time the hotspot is retrieved (since it can become invalid
            # in many other ways too),so there's no need to explicitly forget
            # it here.
            if self.graphicsMode.pickit():
                numol.pickatoms()
                #bruce 060412 worries whether pickatoms is illegal or
                #ineffective (in both pasteBond and pasteFree)
                # given that numol.part is presumably not yet set (until after
                #addmol). But these seem to work
                # (assuming I'm testing them properly), so I'm not changing
                #this. [Why do they work?? ###@@@]
            self.o.assy.addmol(numol) # do this last, in case it computes bbox
            return numol, "copy of %r" % pastable.name
        elif isinstance(pastable, Group):
            msg = "Pasting a group with hotspot onto a bond point " \
                "is not implemented"
            return None, msg
            ##if debug_flags.atom_debug:
                ###@@@ EXPERIMENTAL CODE TO PASTE a GROUP WITH A HOTSPOT
                ##if 0:
                    ### hotspot neighbor atom
                    ##attch2Singlet = atom_or_pos
                    ##hotspot_neighbor = hotspot.singlet_neighbor()
                    ### attach to atom
                    ##attch2Atom = attch2Singlet.singlet_neighbor()
                    ##rotOffset = Q(hotspot_neighbor.posn() - hotspot.posn(),
                                    ##attch2Singlet.posn() - attch2Atom.posn())

                    ##rotCenter = newMol.center
                    ##newMol.rot(rotOffset)

                    ##moveOffset = attch2Singlet.posn() - hs.posn()
                    ##newMol.move(moveOffset)

                    ##self.graphicsMode._createBond(hotspot,
                                        ##hotspot_neighbor,
                                        ##attch2Singlet,
                                        ##attch2Atom)
                    ##self.o.assy.addmol(newMol)
                    ##########
                    ####newGroup = self.pasteGroup(pos, pastable)
                    ##return newGroup, "copy of %r" % newGroup.name
