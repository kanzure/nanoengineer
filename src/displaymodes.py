# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
displaymodes.py -- support for new modular display modes. [Not fully implemented, as of 060608.]

$Id$

Initially this only handles ChunkDisplayModes, which draw entire chunks (even if they are
highlighted or selected) without drawing their atoms or bonds in the usual way. (Such a
display mode might draw the atoms and bonds in its own custom way, or not at all.)

Someday it may also handle AtomDisplayModes, which (like our original hardcoded display modes)
draw atoms and bonds in their own way, but draw chunks as not much more than their set
of atoms and bonds. These are not yet implemented.

To make a new chunk display mode, make a new file which defines and registers a subclass
of our class ChunkDisplayMode. For an example, see CylinderChunks.py.
'''

__author__ = 'bruce'

# to make a new display mode for whole chunks, see the instructions in the module docstring above.

import constants
from debug import register_debug_menu_command
import env

_display_mode_handlers = {} # maps disp_name, and also its index in constants.dispNames, to a DisplayMode instance used for drawing

def get_display_mode_handler(disp):
    return _display_mode_handlers.get(disp)

class DisplayMode:
    "abstract class for any sort of display mode (except the 6 original built-in ones defined in constants.py)"
    chunk_only = False # default value of class constant; some subclasses override this (in fact, not doing so is not yet supported)
    def __init__(self, ind):
        self.ind = ind
        self._icon_name = getattr(self, "icon_name", "junk.png")
        self._hide_icon_name = getattr(self, "hide_icon_name", self._icon_name)
    def get_icon(self, hidden):
        from Utility import imagename_to_pixmap # I don't want to risk importing Utility at toplevel, just yet
        if hidden:
            return imagename_to_pixmap( self._hide_icon_name)
        else:
            return imagename_to_pixmap( self._icon_name)
        pass
    def _register_for_readmmp(clas): # staticmethod
        """private method called when setting up mmp reading code:
        register this class as a readmmp-helper,
        in whatever way differs for different classes of helpers
        """
        disp_name = clas.mmp_code # we treat this as a unique index; error if not unique, unless classname is the same
        disp_label = clas.disp_label
        if disp_name in constants.dispNames:
            # this is only legal if the classname is the same; in that case, replace things (useful for reload during debugging)
            assert 0, "reload during debug for display modes is not yet implemented; or, non-unique mmp_code %r" % (disp_name,)
        assert len(constants.dispNames) == len(constants.dispLabel)
        constants.dispNames.append(disp_name)
        constants.dispLabel.append(disp_label)
        ind = constants.dispNames.index(disp_name) # internal value used by setDisplay
        if clas.chunk_only:
            import chem
            chem.remap_atom_dispdefs[ind] = constants.diDEFAULT # kluge?
        inst = clas(ind)
        _display_mode_handlers[disp_name] = inst
        _display_mode_handlers[ind] = inst #k are both of these needed??
        return
    _register_for_readmmp = staticmethod( _register_for_readmmp)
    #e some of ChunkDisplayMode's code probably belongs in this class
    pass # end of class DisplayMode

class ChunkDisplayMode(DisplayMode): 
    "abstract class for display modes which only work for entire chunks"
    chunk_only = True
    def register_display_mode_class(clas): # staticmethod
        """Register the given subclass of ChunkDisplayMode as a new display mode for whole chunks,
        able to be drawn with, read/written in mmp files, and offered in the UI.
        """
        # Make sure we can read mmp files which refer to it as clas.mmp_code.
        # This also covers statusbar display and writemmp.
        # This works by calling _register_for_readmmp, which also stores clas.disp_label as needed
        # to show this display mode in the statusbar, when it's in use for the entire GLPane.
        # (As of 060608 there is no good reason to go through files_mmp to do this,
        #  but in the future it might need to keep its own record of this use of mmp_code.)
        # (It's probably a kluge that the registering of clas.disp_label goes through files_mmp in any way.
        #  The fault for that lies mainly with the requirement for constants.dispLabel and constants.dispNames
        #  to be lists with corresponding indices. If they were revamped, this could be cleaned up.
        #  But doing so is not trivial, assuming their ordering by bond cylinder radius is required.)
        import files_mmp
        files_mmp.register_for_readmmp( clas)
        # The above also made it possible to draw chunks in this display mode, via _display_mode_handlers
        # and special cases in Chunk draw-related methods.
        ###e highlighting not yet done
        # Now add something to the UI so users can change chunks, or the GLPane, to this display mode.
        # (As a quick hack, just add a debug menu command (always visible) which acts like pressing a toolbutton for this mode.)
        disp_name = clas.mmp_code
        inst = _display_mode_handlers[disp_name]
        register_debug_menu_command("setDisplay(%s)" % clas.disp_label, inst.setDisplay_command)
        ##e should we do something so users can use it as a prefs value for preferred display mode, too?
        return
    register_display_mode_class = staticmethod( register_display_mode_class)
    def setDisplay_command(self, widget):
        win = env.mainwindow()
        win.setDisplay(self.ind)
        if env.debug():
            print "setDisplay to %r.ind == %r" % (self, self.ind)
        return
    def _drawchunk(self, glpane, chunk, highlighted = False):
        """[private method for use only by Chunk.draw]
        Call the subclass's drawchunk method, with the same arguments (but supplying memo ourselves),
        in the proper way (whatever is useful for Chunk.draw). For now, the chunk has already done its pushMatrix
        and gotten us inside its OpenGL display list compiling/executing call, but it hasn't done a pushName.
        [###e possible future revisions: it might do pushName, or it might not put us in the display list unless we say that's ok.]
        """
        memo = self.getmemo(chunk)
        #e exceptions?
        #e pushname
        self.drawchunk( glpane, chunk, memo, highlighted = highlighted)
        return
    def _drawchunk_selection_frame(self, glpane, chunk, selection_frame_color, highlighted = False):
        "Call the subclass's drawchunk with the same arguments (but supplying memo ourselves), in the proper way"
        memo = self.getmemo(chunk)
        #e exceptions
        #e pushname
        #e highlight color for selection frame itself??
        self.drawchunk_selection_frame( glpane, chunk, selection_frame_color, memo, highlighted = highlighted)
        return
    def getmemo(self, chunk):
        """[needs doc]"""
        # Note: This is not yet optimized to let the memo be remade less often than the display list is,
        # but that can still mean we remake it a lot less often than we're called for drawing the selection frame,
        # since that is drawn outside the display list and the chunk might get drawn selected many times
        # without having to remake the display list.
        memo_dict = chunk.memo_dict
        our_key_there = id(self)
            # safer than using mmp_code, in case a developer reloads the class at runtime and the memo algorithm changed
        memoplace = memo_dict.setdefault(our_key_there, {})
        # memoplace is our own persistent mutable dict on this chunk, which lasts as long as the chunk does
        counter = chunk._havelist_inval_counter
        memo_validity_data = (counter,) # a tuple of everything which has to remain the same, for the memo data to remain valid
        if memoplace.get('memo_validity_data') != memo_validity_data:
            # need to compute or recompute memo, and save it
            memo = self.compute_memo(chunk)
            memoplace['memo_validity_data'] = memo_validity_data
            memoplace['memo'] = memo
        return memoplace['memo']
    pass # end of class ChunkDisplayMode
    
# end
##        chunk.pushMatrix() ###k or does caller do this?? (safer re exceptions)
##        try:
##            drawer.drawcylinder(color, end1, end2, radius)
##        except:
##            print_compact_traceback("exception in CylinderChunks.drawchunk ignored: ")
##            pass
##        chunk.popMatrix()
