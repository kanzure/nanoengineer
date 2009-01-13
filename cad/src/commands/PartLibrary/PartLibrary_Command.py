#Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
PartLibrary_Command.py 

Class PartLibrary_Command allows depositing parts from the partlib into the 3D 
workspace.Its property manager shows the current selected part in its 'Preview' 
box. The part can be deposited by doubleclicking on empty space in 3D workspace 
or if it has a hotspot, it can be deposited on a bondpoint of an existing model.  
User can return to previous mode by hitting  'Escape' key or pressing 'Done' 
button in the Part Library mode.

@author: Bruce, Huaicai, Mark, Ninad
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:
The Partlib existed as a tab in the MMKit of Build Atoms Command. (MMKit has been 
deprecated since 2007-08-29.) Now it has its own temporary mode. 

ninad 2007-09-06: Created. Split out some methods originally in depositMode.py 
                  to this file. 

"""

import os
from utilities.Log import  greenmsg, quote_html, redmsg
from model.chem import Atom
from model.elements import Singlet
from geometry.VQT import Q
from operations.ops_copy import copied_nodes_for_DND

from commands.Paste.PasteFromClipboard_Command import PasteFromClipboard_Command
from commands.PartLibrary.PartLibPropertyManager import PartLibPropertyManager
from ne1_ui.toolbars.Ui_PartLibraryFlyout import PartLibraryFlyout
from commands.PartLibrary.PartLibrary_GraphicsMode import PartLibrary_GraphicsMode

class PartLibrary_Command(PasteFromClipboard_Command):
    """
    The PartLibrary_Command allows depositing parts from the partlib into the 3D 
    workspace. Its property manager shows the current selected part in its 
    'Preview' box. The part can be deposited by doubleclicking on empty space 
    in 3D workspace or if it has a hotspot, it can be deposited on a bondpoint 
    of an existing model.  User can return to previous mode by hitting  'Escape' 
    key or pressing 'Done' button in this mode. 
    """    
    commandName = 'PARTLIB'
    featurename = "Part Library"
    from utilities.constants import CL_EDIT_GENERIC
    command_level = CL_EDIT_GENERIC
    
    GraphicsMode_class = PartLibrary_GraphicsMode
    
    #Property Manager
    PM_class = PartLibPropertyManager
    
    #Flyout Toolbar
    FlyoutToolbar_class = PartLibraryFlyout

    def deposit_from_Library_page(self, atom_or_pos): 
        """
        Deposit a copy of the selected part from the Property Manager.

        @param atom_or_pos: If user clicks on a bondpoint in 3D workspace,
                            this is that bondpoint. NE1 will try to bond the 
                            part to this bondpoint, by Part's hotspot(if exists)
                            If user double clicks on empty space, this gives 
                            the coordinates at that point. This data is then 
                            used to deposit the item.
        @type atom_or_pos: Array (vector) of coordinates or L{Atom}

        @return: (deposited_stuff, status_msg_text) Object deposited in the 3 D 
                workspace. (Deposits the selected  part as a 'Group'. The status
                message text tells whether the Part got deposited.
        @rtype: (L{Group} , str)
        """
        #Needs cleanup. Copying old code from deprecated 'depositMode.py'
        #-- ninad 2007-09-06

        newPart, hotSpot = self.propMgr.getPastablePart()

        if not newPart: # Make sure a part is selected in the MMKit Library.
            # Whenever the MMKit is closed with the 'Library' page open,
            # MMKit.closeEvent() will change the current page to 'Atoms'.
            # This ensures that this condition never happens if the MMKit is 
            # closed.
            # Mark 051213.

            return False, "No library part has been selected to paste." 

        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if hotSpot : # bond the part to the singlet.
                    return self._depositLibraryPart(newPart, hotSpot, a)                 
                else: # part doesn't have hotspot.
                    #if newPart.has_singlets(): # need a method like this so we 
                    # can provide more descriptive msgs.
                    #    msg = "To bond this part, you must pick a hotspot by \
                    #           left-clicking on a bondpoint  of the library \
                    #           part in the Modeling Kit's 3D thumbview."
                    #else:
                    #    msg = "The library part cannot be bonded because it \
                    #           has no bondpoints."

                    msg = "The library part cannot be bonded because either " \
                        "it has no bondpoints"\
                        " or its hotspot hasn't been specified"

                    return False, msg # nothing deposited
            else: 
                # atom_or_pos was an atom, but wasn't a singlet.  Do nothing.
                msg = "internal error: can't deposit onto a real atom %r" %a
                return False, msg

        else:
            # deposit into empty space at the cursor position
            #bruce 051227 note: looks like subr repeats these conds;
            #are they needed here?
            return self._depositLibraryPart(newPart, hotSpot, atom_or_pos) 

        assert 0, "notreached"

    #Method _depositLibraryPart moved from deprecated depositMode.py to here 
    #-- Ninad 2008-01-02
    def _depositLibraryPart(self, newPart, hotspotAtom, atom_or_pos): 
        # probably by Huaicai; revised by bruce 051227, 060627, 070501
        """
        This method serves as an overloaded method, <atom_or_pos> is 
        the Singlet atom or the empty position that the new part <newPart>
        [which is an assy, at least sometimes] will be attached to or placed at.
        [If <atom_or_pos> is a singlet, <hotspotAtom> should be an atom in some 
        chunk in <newPart>.]
        Currently, it doesn't consider group or jigs in the <newPart>. 
        Not so sure if my attempt to copy a part into another assembly is all
        right. [It wasn't, so bruce 051227 revised it.]
        Copies all molecules in the <newPart>, change their assy attribute to 
        current assembly, move them into <pos>.
        [bruce 051227 new feature:] return a list of new nodes created, and a 
        message for history (currently almost a stub).
        [not sure if subrs ever print history messages...
        if they do we'd want to return those instead.]
        """

        attach2Bond = False
        stuff = [] # list of deposited nodes [bruce 051227 new feature]

        if isinstance(atom_or_pos, Atom):
            attch2Singlet = atom_or_pos
            if hotspotAtom and hotspotAtom.is_singlet() and \
               attch2Singlet .is_singlet():

                newMol = hotspotAtom.molecule.copy_single_chunk(None)
                    # [this can break interchunk bonds,
                    #  thus it still has bug 2028]
                newMol.set_assy(self.o.assy)
                hs = newMol.hotspot
                ha = hs.singlet_neighbor() # hotspot neighbor atom
                attch2Atom = attch2Singlet.singlet_neighbor() # attach to atom

                rotCenter = newMol.center
                rotOffset = Q(ha.posn()-hs.posn(), 
                              attch2Singlet.posn()-attch2Atom.posn())
                newMol.rot(rotOffset)

                moveOffset = attch2Singlet.posn() - hs.posn()
                newMol.move(moveOffset)
    
                self.graphicsMode._createBond(hs, ha, attch2Singlet, attch2Atom)

                self.o.assy.addmol(newMol)
                stuff.append(newMol)

                #e if there are other chunks in <newPart>, 
                #they are apparently copied below. [bruce 060627 comment]

            else: ## something is wrong, do nothing
                return stuff, "internal error"
            attach2Bond = True
        else:
            placedPos = atom_or_pos
            if hotspotAtom:
                hotspotAtomPos = hotspotAtom.posn()
                moveOffset = placedPos - hotspotAtomPos
            else:
                if newPart.molecules:
                    moveOffset = placedPos - newPart.molecules[0].center #e not 
                    #the best choice of center [bruce 060627 comment]

        if attach2Bond: # Connect part to a bondpoint of an existing chunk
            for m in newPart.molecules:
                if not m is hotspotAtom.molecule: 
                    newMol = m.copy_single_chunk(None)
                        # [this can break interchunk bonds,
                        #  thus it still has bug 2028]
                    newMol.set_assy(self.o.assy)

                    ## Get each of all other chunks' center movement for the 
                    ## rotation around 'rotCenter'
                    coff = rotOffset.rot(newMol.center - rotCenter)
                    coff = rotCenter - newMol.center + coff 

                    # The order of the following 2 statements doesn't matter
                    newMol.rot(rotOffset)
                    newMol.move(moveOffset + coff)

                    self.o.assy.addmol(newMol)
                    stuff.append(newMol)
        else: # Behaves like dropping a part anywhere you specify, independent 
            #of existing chunks.
            # copy all nodes in newPart (except those in clipboard items), 
            # regardless of node classes;
            # put it in a new Group if more than one thing [bruce 070501]
            # [TODO: this should be done in the cases above, too, but that's 
            # not yet implemented,
            #  and requires adding rot or pivot to the Node API and revising
            #  the rot-calling code above,
            #  and also reviewing the definition of the "hotspot of a Part" and 
            # maybe of a "depositable clipboard item".]
            assert newPart.tree.is_group()
            nodes = list(newPart.tree.members) # might be []
            assy = self.o.assy
            newnodes = copied_nodes_for_DND(nodes, 
                                            autogroup_at_top = True, 
                                            assy = assy)
                # Note: that calls name_autogrouped_nodes_for_clipboard 
                # internally, if it forms a Group,
                # but we ignore that and rename the new node differently below,
                # whether or not it was autogrouped. We could just as well do 
                # the autogrouping ourselves...
                # Note [bruce 070525]: it's better to call copied_nodes_for_DND 
                # here than copy_nodes_in_order, even if we didn't need to 
                # autogroup. One reason is that if some node is not copied,
                # that's not necessarily an error, since we don't care about 1-1
                # orig-copy correspondence here.
            if not newnodes:
                if newnodes is None:
                    print "bug: newnodes should not be None; nodes was %r (saved in debug._bugnodes)" % (nodes,)
                        # TODO: This might be possible, for arbitrary partlib 
                        # contents, just not for legitimate ones...
                        # but partlib will probably be (or is) user-expandable, 
                        #so we should turn this into history message,
                        # not a bug print. But I'm not positive it's possible
                        #w/o a bug, so review first. ###FIX [bruce 070501 comment]
                    import utilities.debug as debug
                    debug._bugnodes = nodes
                    newnodes = []
                msg = redmsg( "error: nothing to deposit in [%s]" % quote_html(str(newPart.name)) )
                return [], msg
            assert len(newnodes) == 1 # due to autogroup_at_top = True
            # but the remaining code works fine regardless of len(newnodes), 
            #in case we make autogroup a preference
            for newnode in newnodes:
                # Rename newnode based on the partlib name and a unique number.
                # It seems best to let the partlib mmp file contents (not just 
                # filename)
                # control the name used here, so use newPart.tree.name rather 
                # than just newPart.name.
                # (newPart.name is a complete file pathname; newPart.tree.name 
                #is usually its basename w/o extension.)
                basename = str(newPart.tree.name)
                if basename == 'Untitled':
                    # kluge, for the sake of 3 current partlib files, and files 
                    #saved only once by users (due to NE1 bug in save)
                    dirjunk, base = os.path.split(newPart.name)
                    basename, extjunk = os.path.splitext(base)
                from utilities.constants import gensym
                newnode.name = gensym( basename, assy) # name library part
                    #bruce 080407 basename + " " --> basename, and pass assy
                    # (per Mark NFR desire)
                #based on basename recorded in its mmp file's top node
                newnode.move(moveOffset) #k not sure this method is correctly 
                #implemented for measurement jigs, named views
                assy.addnode(newnode)
                stuff.append(newnode)

##            #bruce 060627 new code: fix bug 2028 (non-hotspot case only) 
##            # about interchunk bonds being broken
##            nodes = newPart.molecules
##            newnodes = copied_nodes_for_DND(nodes)
##            if newnodes is None:
##                print "bug: newnodes should not be None; nodes was %r (saved in debug._bugnodes)" % (nodes,)
##                debug._bugnodes = nodes
##                newnodes = [] # kluge
##            for newMol in newnodes:
##                # some of the following probably only work for Chunks,
##                # though coding them for other nodes would not be hard
##                newMol.set_assy(self.o.assy)
##                newMol.move(moveOffset)
##                self.o.assy.addmol(newMol)
##                stuff.append(newMol)

        self.o.assy.update_parts() #bruce 051227 see if this fixes the 
                                    #atom_debug exception in checkparts

        msg = greenmsg("Deposited library part: ") + " [" + \
            quote_html(str(newPart.name)) + "]"  #ninad060924 fix bug 1164 

        return stuff, msg  ####@@@@ should revise this message 
                            ##(stub is by bruce 051227)

