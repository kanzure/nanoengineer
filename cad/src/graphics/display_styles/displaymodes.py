# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details.
"""
displaymodes.py -- support for new modular display modes.

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

Initially this only handles ChunkDisplayModes, which draw entire chunks (even if they are
highlighted or selected) without drawing their atoms or bonds in the usual way. (Such a
display mode might draw the atoms and bonds in its own custom way, or not at all.)

Someday it may also handle AtomDisplayModes, which (like our original hardcoded display modes)
draw atoms and bonds in their own way, but draw chunks as not much more than their set
of atoms and bonds. These are not yet implemented.

To make a new chunk display mode, make a new file which defines and registers a subclass
of our class ChunkDisplayMode. For an example, see CylinderChunks.py.
"""

# USAGE: to make a new display style for whole chunks,
# see the instructions in the module docstring above.

from utilities.constants import _f_add_display_style_code

from utilities.debug import register_debug_menu_command
import foundation.env as env

# global variables and accessors

_display_mode_handlers = {}
    # maps disp_name, and also its index in constants.dispNames,
    # to a DisplayMode instance used for drawing

def get_display_mode_handler(disp):
    return _display_mode_handlers.get(disp)

# ==

class DisplayMode:
    """
    abstract class for any sort of display mode
    (except the 6 original built-in ones defined in constants.py)
    """

    # Note: some subclasses assign a class constant featurename,
    # but as far as I know, this is not yet used. TODO: add a
    # get_featurename method like in class Command (or basicCommand)
    # and add code to use it (not sure where in the UI).
    # [bruce 071227 comment]
    featurename = ""

    chunk_only = False # default value of class constant; some subclasses override this (in fact, not doing so is not yet supported)

    def __init__(self, ind):
        self.ind = ind
        self._icon_name = getattr(self, "icon_name", "modeltree/junk.png")
        self._hide_icon_name = getattr(self, "hide_icon_name", self._icon_name)

    def get_icon(self, hidden):
        from utilities.icon_utilities import imagename_to_pixmap
        if hidden:
            return imagename_to_pixmap( self._hide_icon_name)
        else:
            return imagename_to_pixmap( self._icon_name)
        pass

    def _register_for_readmmp(clas): # staticmethod; name is misleading, but required by other code in this file
        """
        private method called when setting up mmp reading code:
        register this class as a readmmp-helper,
        in whatever way differs for different classes of helpers

        [update, bruce 071017: this docstring is misleading,
        since so far this has nothing to do with mmp reading;
        see code comments for details]
        """
        disp_name = clas.mmp_code # we treat this as a unique index; error if not unique, unless classname is the same
        disp_label = clas.disp_label

        #bruce 080324 refactored this:
        allowed_for_atoms = not clas.chunk_only
        ind = _f_add_display_style_code( disp_name, disp_label, allowed_for_atoms )
        inst = clas(ind)
        _display_mode_handlers[disp_name] = inst
        _display_mode_handlers[ind] = inst #k are both of these needed??
        return
    _register_for_readmmp = staticmethod( _register_for_readmmp)

    #e some of ChunkDisplayMode's code probably belongs in this class

    pass # end of class DisplayMode

class ChunkDisplayMode(DisplayMode):
    """
    abstract class for display modes which only work for entire chunks
    """
    chunk_only = True

    def register_display_mode_class(clas): # staticmethod
        """
        Register the given subclass of ChunkDisplayMode as a new display mode for whole chunks,
        able to be drawn with, read/written in mmp files, and offered in the UI.

        @warning: The order in which this is called for different display styles
                  must correspond with the order in which disp index constants (diWhatever)
                  are defined for them in constants.py. (This needs cleanup.)
                  [bruce 080212 comment; related code has comments with same signature]
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

        # bruce 071017 -- remove register_for_readmmp and replace it with what it did,
        # since it's more confusing than worthwhile
        # (but see above comment for the motivation of the old way, which had some legitimacy):
        ## import files_mmp
        ## files_mmp.register_for_readmmp( clas)
        smethod = clas._register_for_readmmp
        smethod(clas)

        # The above also made it possible to draw chunks in this display mode, via _display_mode_handlers
        # and special cases in Chunk draw-related methods.
        ###e highlighting not yet done
        # Now add something to the UI so users can change chunks, or the GLPane, to this display mode.
        # (As a quick hack, just add a debug menu command (always visible) which acts like pressing a toolbutton for this mode.)
        disp_name = clas.mmp_code
        inst = _display_mode_handlers[disp_name]
        register_debug_menu_command("setDisplayStyle_of_selection(%s)" % clas.disp_label, inst.setDisplay_command)
        ##e should we do something so users can use it as a prefs value for preferred display mode, too?
        return
    register_display_mode_class = staticmethod( register_display_mode_class)

    def setDisplay_command(self, widget):
        win = env.mainwindow()
        win.setDisplayStyle_of_selection(self.ind)
            #bruce 080910 comment, upon renaming that method from setDisplay:
            # the new name says what it does, but when originally coded
            # this would set global style if nothing was selected
            # (since that method used to act that way).
        if env.debug():
            print "setDisplayStyle_of_selection to %r.ind == %r" % (self, self.ind)
        return

    def _f_drawchunk(self, glpane, chunk, highlighted = False):
        """
        [private method for use only by Chunk.draw]
        Call the subclass's drawchunk method, with the supplied arguments
        (but supplying memo ourselves), in the proper way (whatever is useful
        for Chunk.draw).

        In the calling code as it was when this method was written,
        the chunk has already done its pushMatrix and gotten us inside its
        OpenGL display list compiling/executing call, but it hasn't done a
        pushName. [later: chunks now do a pushName, probably (guess) before
        this call.]

        @note: possible future revisions: it might do pushName, or it might not
               put us in the display list unless we say that's ok.
        """
        memo = self.getmemo(chunk)
        #e exceptions?
        #e pushname
        self.drawchunk( glpane, chunk, memo, highlighted = highlighted)
        return

    def _f_drawchunk_selection_frame(self, glpane, chunk, selection_frame_color, highlighted = False):
        """
        Call the subclass's drawchunk_selection_frame method,
        with the supplied arguments (but supplying memo ourselves),
        in the proper way.
        """
        # note: as of long before now, this is never called. But it should
        # remain in the API in case we want to revive its use.
        # [bruce 081001 comment]
        memo = self.getmemo(chunk)
        #e exceptions
        #e pushname
        #e highlight color for selection frame itself??
        self.drawchunk_selection_frame( glpane, chunk, selection_frame_color, memo, highlighted = highlighted)
        return

    def _f_drawchunk_realtime(self, glpane, chunk, highlighted = False):
        """
        Call the drawing method that may depend on current view settings,
        e.g. orientation.
        """
        # piotr 080313
        # added the highlighted = False argument - piotr 080521
        # assume we don't need memo here
        ### memo = self.getmemo(chunk)
        self.drawchunk_realtime(glpane, chunk, highlighted)
        return

    def _writepov(self, chunk, file):
        """
        piotr 080314
        Render the chunk to a POV-Ray file
        """
        memo = self.getmemo(chunk)
        self.writepov(chunk, memo, file)

    def getmemo(self, chunk): # refactored, bruce 090213
        """
        [needs doc]
        """
        # Note: This is not yet optimized to let the memo be remade less often
        # than the display list is, but that can still mean we remake it a lot
        # less often than we're called for drawing the selection frame,
        # since that is drawn outside the display list and the chunk might get
        # drawn selected many times without having to remake the display list.

        our_key_in_chunk = id(self)
            # safer than using mmp_code, in case a developer reloads the class
            # at runtime and the memo algorithm changed
        counter = chunk.changeapp_counter()
        memo_validity_data = (counter,)
            # a tuple of everything which has to remain the same, for the memo
            # data to remain valid; if invalid, the following calls compute_memo
        memo = chunk.find_or_recompute_memo(
                         our_key_in_chunk,
                         memo_validity_data,
                         self.compute_memo )
        return memo

    pass # end of class ChunkDisplayMode

# end
