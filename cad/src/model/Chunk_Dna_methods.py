# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Chunk_Dna_methods.py -- dna-related methods for class Chunk

@author: Bruce, Ninad
@version: $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090115 split this out of class Chunk. (Not long or old enough
for svn copy to be worthwhile, so see chunk.py for older svn history.)

TODO: Refactoring:

Some of the methods in this class are never used except on
Dna-related subclasses of Chunk, and should be moved into those
subclasses. Unfortunately it's not trivial to figure out for which ones
that's guaranteed to be the case.

There are some large hunks of duplicated code in this file
(pylint can detect them).

See also the REVIEW comments below, as always.
"""

from utilities.constants import noop
from utilities.constants import MODEL_PAM3, MODEL_PAM5

class Chunk_Dna_methods: ## (NodeWithAtomContents):
    # Someday: inherit NodeWithAtomContents (Chunk's main superclass) to
    # mollify pylint? It does mollify it somewhat and seemed initially to be
    # ok... but Chunk (as all Nodes) is still an old-style class, so it has no
    # __mro__ attribute and follows different inheritance rules than new-style
    # classes. It turns out that the old rules mess up in this case, if we use
    # that superclass on more than one pre-mixin class split out of class
    # Chunk, e.g. Chunk_mmp_methods, since then whichever one comes first
    # pulls in NodeWithAtomContents methods ahead of the other mixin's
    # methods, which prevents the other mixin from overriding those methods.
    # (This is exactly the "diamond-shaped inheritance diagram" issue that the
    # new-style mro rules fix.)
    #
    # The upside of this is that we can't inherit Chunk's main superclass in
    # its special-method-mixin classes until we make Chunk a new-style class
    # (which has issues of its own, common to all Nodes, described elsewhere).
    # Hopefully, before that happens, we'll have refactored Chunk further to
    # use cooperating objects rather than mixin classes. [bruce 090123]
    """
    Dna-related methods to be mixed in to class Chunk.
    """  
    
    # PAM3+5 attributes (these only affect PAM atoms in self, if any):
    #
    # ### REVIEW [bruce 090115]: can some of these be deprecated and removed?
    #
    # self.display_as_pam can be MODEL_PAM3 or MODEL_PAM5 to force conversion 
    #   on input
    #   to the specified PAM model for display and editing of self, or can be
    #   "" to use global preference settings. (There is no value which always
    #   causes no conversion, but there may be preference settings which disable
    #   ever doing conversion. But in practice, a PAM chunk will be all PAM3 or
    #   all PAM5, so this can be set to the model the chunk uses to prevent
    #   conversion for that chunk.)
    #
    #  The value MODEL_PAM3 implies preservation of PAM5 data when present
    #  (aka "pam3+5" or "pam3plus5"). 
    #  The allowed values are "", MODEL_PAM3, MODEL_PAM5.
    #
    # self.save_as_pam can be MODEL_PAM3 or MODEL_PAM5 to force conversion on save
    #   to the specified PAM model. When not set, global settings or save
    #   parameters determine which model to convert to, and whether to ever
    #   convert.
    #
    # [bruce 080321 for PAM3+5] ### TODO: use for conversion, and prevent
    # ladder merge when different

    display_as_pam = "" 
        # PAM model to use for displaying and editing PAM atoms in self (not
        # set means use user pref)

    save_as_pam = "" 
        # PAM model to use for saving self (not normally set; not set means
        # use save-op params)
        
    # this mixin's contribution to Chunk.copyable_attrs
    _dna_copyable_attrs = ('display_as_pam', 'save_as_pam', ) 

    
    def invalidate_ladder(self): #bruce 071203
        """
        Subclasses which have a .ladder attribute
        should call its ladder_invalidate_if_not_disabled method.
        """
        return

    def invalidate_ladder_and_assert_permitted(self): #bruce 080413
        """
        Subclasses which have a .ladder attribute
        should call its ladder_invalidate_and_assert_permitted method.
        """
        return

    def in_a_valid_ladder(self): #bruce 071203
        """
        Is this chunk a rail of a valid DnaLadder?
        [subclasses that might be should override]
        """
        return False

    
    def _make_glpane_cmenu_items_Dna(self, contextMenuList): # by Ninad
        """
        Private helper for Chunk.make_glpane_cmenu_items; 
        does the dna-related part.
        """
        #bruce 090115 split this out of Chunk.make_glpane_cmenu_items
        
        def _addDnaGroupMenuItems(dnaGroup):
            if dnaGroup is None:
                return
            item = (("DnaGroup: [%s]" % dnaGroup.name), noop, 'disabled')
            contextMenuList.append(item)   
            item = (("Edit DnaGroup Properties..."), 
                    dnaGroup.edit) 
            contextMenuList.append(item)
            return
        
        if self.isStrandChunk():
            strandGroup = self.parent_node_of_class(self.assy.DnaStrand)

            if strandGroup is None:
                strand = self
            else:
                #dna_updater case which uses DnaStrand object for 
                #internal DnaStrandChunks
                strand = strandGroup                

            dnaGroup = strand.parent_node_of_class(self.assy.DnaGroup)

            if dnaGroup is None:
                #This is probably a bug. A strand should always be contained
                #within a Dnagroup. But we'll assume here that this is possible. 
                item = (("%s" % strand.name), noop, 'disabled')
            else:
                item = (("%s of [%s]" % (strand.name, dnaGroup.name)),
                        noop,
                        'disabled')	
            contextMenuList.append(None) # adds a separator in the contextmenu
            contextMenuList.append(item)	    
            item = (("Edit DnaStrand Properties..."), 
                    strand.edit) 			  
            contextMenuList.append(item)
            contextMenuList.append(None) # separator
            
            _addDnaGroupMenuItems(dnaGroup)
            
            # add menu commands from our DnaLadder [bruce 080407]
            # REVIEW: should these be added regardless of command? 
            # [bruce 090115 question]
            # REVIEW: I think self.ladder is not valid except in dna-specific
            # subclasses of Chunk. Probably that means this code should be 
            # moved there. [bruce 090115]
            if self.ladder:
                menu_spec = self.ladder.dnaladder_menu_spec(self)
                    # note: this is empty when self (the arg) is a Chunk.
                    # [bruce 080723 refactoring a recent Mark change]
                if menu_spec:
                    # append separator?? ## contextMenuList.append(None)
                    contextMenuList.extend(menu_spec)

        elif self.isAxisChunk():
            segment = self.parent_node_of_class(self.assy.DnaSegment)
            dnaGroup = segment.parent_node_of_class(self.assy.DnaGroup)
            if segment is not None:
                contextMenuList.append(None) # separator
                if dnaGroup is not None:
                    item = (("%s of [%s]" % (segment.name, dnaGroup.name)),
                            noop,
                            'disabled')
                else:
                    item = (("%s " % segment.name),
                            noop,
                            'disabled')

                contextMenuList.append(item)
                item = (("Edit DnaSegment Properties..."), 
                        segment.edit)
                contextMenuList.append(item)
                contextMenuList.append(None) # separator
                # add menu commands from our DnaLadder [bruce 080407]
                # REVIEW: see comments for similar code above. [bruce 090115]
                if segment.picked:       
                    selectedDnaSegments = self.assy.getSelectedDnaSegments()
                    if len(selectedDnaSegments) > 0:
                        item = (("Resize Selected DnaSegments "\
                                 "(%d)..." % len(selectedDnaSegments)), 
                                self.assy.win.resizeSelectedDnaSegments)
                        contextMenuList.append(item)
                        contextMenuList.append(None)
                if self.ladder:
                    menu_spec = self.ladder.dnaladder_menu_spec(self)
                    if menu_spec:
                        contextMenuList.extend(menu_spec)
                        
                _addDnaGroupMenuItems(dnaGroup)
                pass
            pass
        return
    
    
    # START of Dna-Strand-or-Axis chunk specific code ==========================

    # Note: some of these methods will be removed from class Chunk once the
    # dna data model is always active. [bruce 080205 comment] [some removed, 090121]

    def _editProperties_DnaStrandChunk(self):
        """
        Private helper for Chunk.edit; 
        does the dna-related part.
        """
        # probably by Ninad; split out of Chunk.edit by Bruce 090115
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('DNA_STRAND')                
        assert commandSequencer.currentCommand.commandName == 'DNA_STRAND'
        commandSequencer.currentCommand.editStructure(self)
        return
    
    def isStrandChunk(self): # Ninad circa 080117, revised by Bruce 080117
        """
        Returns True if *all atoms* in this chunk are PAM 'strand' atoms
        or 'unpaired-base' atoms (or bondpoints), and at least one is a
        'strand' atom.

        Also resets self.iconPath (based on self.hidden) if it returns True.

        This method is overridden in dna-specific subclasses of Chunk.
        It is likely that this implementation on Chunk itself could now
        be redefined to just return False, but this has not been analyzed closely.
        
        @see: BuildDna_PropertyManager.updateStrandListWidget where this is used
              to filter out strand chunks to put those into the strandList 
              widget.        
        """
        # This is a temporary method that can be removed once dna_model is
        # fully functional.
        
        # bruce 090121 comment: REVIEW whether this can be redefined to return
        # False on this class, since it's implemented in our DnaStrandChunk
        # subclass.
        found_strand_atom = False
        for atom in self.atoms.itervalues():
            if atom.element.role == 'strand':
                found_strand_atom = True
                # side effect: use strand icon [mark 080203]
                if self.hidden:
                    self.iconPath = "ui/modeltree/Strand-hide.png"
                else:
                    self.iconPath = "ui/modeltree/Strand.png"
            elif atom.is_singlet() or atom.element.role == 'unpaired-base':
                pass
            else:
                # other kinds of atoms are not allowed
                return False
            continue

        return found_strand_atom

    #END of Dna-Strand chunk specific  code ==================================


    #START of Dna-Axis chunk specific code ==================================

    def isAxisChunk(self):
        """
        Returns True if *all atoms* in this chunk are PAM 'axis' atoms
        or bondpoints, and at least one is an 'axis' atom.

        Overridden in some subclasses.

        @see: isStrandChunk
        """
        # bruce 090121 comment: REVIEW whether this can be redefined to return
        # False on this class, since it's implemented in our DnaAxisChunk
        # subclass.
        found_axis_atom = False
        for atom in self.atoms.itervalues():
            if atom.element.role == 'axis':
                found_axis_atom = True
            elif atom.is_singlet():
                pass
            else:
                # other kinds of atoms are not allowed
                return False
            continue

        return found_axis_atom  

    #END of Dna-Axis chunk specific code ====================================


    #START of Dna-Strand-or-Axis chunk specific code ========================

    def isDnaChunk(self):
        """
        @return: whether self is a DNA chunk (strand or axis chunk)
        @rtype: boolean
        """
        return self.isAxisChunk() or self.isStrandChunk()
    

    def getDnaGroup(self): # ninad 080205
        """
        Return the DnaGroup of this chunk if it has one. 
        """
        return self.parent_node_of_class(self.assy.DnaGroup)
    
    def getDnaStrand(self):
        """
        Returns the DnaStrand(group) node to which this chunk belongs to. 
        
        Returns None if there isn't a parent DnaStrand group.
        
        @see: Atom.getDnaStrand()
        """
        if self.isNullChunk():
            return None
        
        dnaStrand = self.parent_node_of_class(self.assy.DnaStrand)
        
        return dnaStrand
    
    def getDnaSegment(self):
        """
        Returns the DnaStrand(group) node to which this chunk belongs to. 
        
        Returns None if there isn't a parent DnaStrand group.
        
        @see: Atom.getDnaStrand()
        """
        if self.isNullChunk():
            return None
        
        dnaSegment = self.parent_node_of_class(self.assy.DnaSegment)
        
        return dnaSegment

    #END of Dna-Strand-or-Axis chunk specific code ========================

    
    def _readmmp_info_chunk_setitem_Dna( self, key, val, interp ):
        """
        Private helper for Chunk.readmmp_info_chunk_setitem.
        
        @return: whether we handled this info record (depends only on key, 
                 not on success vs error)
        @rtype: boolean
        """
        if key == ['display_as_pam']:
            # val should be one of the strings "", MODEL_PAM3, MODEL_PAM5;
            # if not recognized, use ""
            if val not in ("", MODEL_PAM3, MODEL_PAM5):
                # maybe todo: use deferred_summary_message?
                print "fyi: info chunk display_as_pam with unrecognized value %r" % \
                      (val,) 
                val = ""
            #bruce 080523: silently ignore this, until the bug 2842 dust fully
            # settles. This is #1 of 2 changes (in the same commit) which
            # eliminates all ways of setting this attribute, thus fixing
            # bug 2842 well enough for v1.1. (The same change is not needed
            # for save_as_pam below, since it never gets set, or ever did,
            # except when using non-default values of debug_prefs. This means
            # someone setting those prefs could save a file which causes a bug
            # only seen by whoever loads it, but I'll live with that for now.)
            ## self.display_as_pam = val
            pass
        elif key == ['save_as_pam']:
            # val should be one of the strings "", MODEL_PAM3, MODEL_PAM5;
            # if not recognized, use ""
            if val not in ("", MODEL_PAM3, MODEL_PAM5):
                # maybe todo: use deferred_summary_message?
                print "fyi: info chunk save_as_pam with unrecognized value %r" % \
                      (val,)
                val = ""
            self.save_as_pam = val
        else:
            return False
        return True
    
    def _writemmp_info_chunk_before_atoms_Dna(self, mapping):
        """
        Private helper for Chunk.writemmp_info_chunk_before_atoms.
        
        @return: None
        """
        if self.display_as_pam:
            # Note: not normally set on most chunks, even when PAM3+5 is in use.
            # Future optim (unimportant since not normally set):
            # we needn't write this is self contains no PAM atoms.
            # and if we failed to write it when dna updater was off, 
            # that would be ok.
            # So we could assume we don't need it for ordinary chunks
            # (even though that means dna updater errors on atoms would discard it).
            mapping.write("info chunk display_as_pam = %s\n" % self.display_as_pam)
        if self.save_as_pam:
            # not normally set, even when PAM3+5 is in use
            mapping.write("info chunk save_as_pam = %s\n" % self.save_as_pam)
        return

    
    def _getToolTipInfo_Dna(self):
        """
        Return the dna-related part of the tooltip string for this chunk
        """
        # probably by Mark or Ninad
        # Note: As of 2008-11-09, this is only implemented for a DnaStrand.
        #bruce 090115 split this out of Chunk.getToolTipInfo
        strand = self.getDnaStrand()
        if strand:
            return strand.getDefaultToolTipInfo()   
        
        segment = self.getDnaSegment()
        if segment:
            return segment.getDefaultToolTipInfo()
                    
        return ""

    
    def _getAxis_of_self_or_eligible_parent_node_Dna(self, atomAtVectorOrigin = None):
        """
        Private helper for Chunk.getAxis_of_self_or_eligible_parent_node;
        does the dna-related part.
        """
        # by Ninad
        #bruce 090115 split this out of Chunk.getAxis_of_self_or_eligible_parent_node
        dnaSegment = self.parent_node_of_class(self.assy.DnaSegment)
        if dnaSegment and self.isAxisChunk():
            axisVector = dnaSegment.getAxisVector(
                atomAtVectorOrigin = atomAtVectorOrigin )
            if axisVector is not None:
                return axisVector, dnaSegment

        dnaStrand = self.parent_node_of_class(self.assy.DnaStrand)
        if dnaStrand and self.isStrandChunk():
            arbitraryAtom = self.atlist[0]
            dnaSegment = dnaStrand.get_DnaSegment_with_content_atom(
                arbitraryAtom)
            if dnaSegment:
                axisVector = dnaSegment.getAxisVector(
                    atomAtVectorOrigin = atomAtVectorOrigin )
                if axisVector is not None:
                    return axisVector, dnaSegment

        return None, None
    
    pass # end of class Chunk_Dna_methods

# end
