# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
cursors.py - load all the custom cursors needed by NE1

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

mark 060427 - loadCursors() moved from MWsemantics.py.
"""

from PyQt4.Qt import QCursor, QBitmap, Qt
import os, sys

from icon_utilities import getpixmap

def loadCursors(w):
    """
    This routine is called once to load all the custom cursors needed by NE1.
    To add a new cursor, two BMP files are placed in the cad/src/ui/cursors directory
    (or in another directory in cad/src/ui):
        <cursor_name>.bmp - the cursor bitmap file 
        <cursor_name>-bm.bmp - the cursor's bitmask file 
    Then you simply add a single line of code below to load the custom cursor.
    <w> is the main window (parent) object for all custom cursors.
    """

    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

    def loadCursor(cursor_name, hot_x, hot_y):
        """
        Returns a cursor built from two BMP files located (by default)
        in the cad/src/ui/cursors directory:
            <cursor_name>.bmp - the cursor bitmap file 
            <cursor_name>-bm.bmp - the cursor's bitmask file 

        <hot_x> and <hot_y> define the cursor's hotspot.

        If the cursor_name starts with ui/, then it is relative to cad/src,
        thus permitting some cursors to live in other directories besides cad/src/ui/cursors.
        """

        # I would like move all the custom cursor files an exclusive directory (i.e. cad/ui/cursors)
        # and then read that directory at startup to create the cursors from the files.
        # I'd also like to change the cursor filename format to the following:
        #     <cursor_name>_bitmap.bmp - the cursor bitmap file 
        #     <cursor_name>_bitmask.bmp - the cursor's bitmask file 
        # The existence of these two files would automatically create the cursor w.<cursor_name>
        # I need to discuss this with Bruce more, especially since I don't know how to
        # create the cursor_name from the filename. Mark 060428.
        #
        # [bruce 070626 comment on that proposal: I think it's better to define the set of cursor names
        #  in the python code, like we do now, for several reasons: so it's possible to find them by searching the code,
        #  and so you don't have to worry that the filesystem state (which might differ from what it is in cvs)
        #  can create arbitrarily-named attributes in the main window object, and to simplify life for code analysis tools.]

        if cursor_name.startswith("ui/"):
            #bruce 070626 new feature, needed for ui/confcorner cursors
            dirpath = filePath + "/../src/"
        else:
            dirpath = filePath + "/../src/ui/cursors/"

        cursor_bitmap = dirpath + cursor_name + ".bmp"
        cursor_bitmsk = dirpath + cursor_name + "-bm.bmp"

        if os.path.exists(cursor_bitmap) and os.path.exists(cursor_bitmsk):
            cursor = QCursor(
                QBitmap(cursor_bitmap),
                QBitmap(cursor_bitmsk),
                hot_x, hot_y)
        else:
            print "loadCursor: Cursor file(s) do not exist for cursor '", cursor_name, "'. Returning null cursor."
            cursor = None

        return cursor

    # Build mode - normal cursors
    w.SelectAtomsCursor = \
     QCursor(getpixmap("ui/cursors/SelectAtomsCursor.png"), 0, 0)
    w.SelectAtomsAddCursor = \
     QCursor(getpixmap("ui/cursors/SelectAtomsAddCursor.png"), 0, 0)
    w.SelectAtomsSubtractCursor = \
     QCursor(getpixmap("ui/cursors/SelectAtomsSubtractCursor.png"), 0, 0)
    w.DeleteCursor = \
     QCursor(getpixmap("ui/cursors/DeleteCursor.png"), 0, 0)

    # Build mode - Atom Selection cursors
    w.SelectAtomsFilterCursor = loadCursor("SelectAtomsFilterCursor", 0, 0)
    w.SelectAtomsAddFilterCursor = loadCursor("SelectAtomsAddFilterCursor", 0, 0)
    w.SelectAtomsSubtractFilterCursor = loadCursor("SelectAtomsSubtractFilterCursor", 0, 0)
    w.DeleteFilterCursor = loadCursor("DeleteFilterCursor", 0, 0)

    # Build mode - Bond Tool cursors with no modkey pressed
    w.BondToolCursor = []
    w.BondToolCursor.append(QCursor(getpixmap("ui/cursors/SelectAtomsCursor.png"), 0, 0))
    w.BondToolCursor.append(loadCursor("Bond1ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("Bond2ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("Bond3ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("BondAToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("BondGToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("CutBondCursor", 0, 0))    

    # Build mode - Bond Tool cursors with Shift modkey pressed
    w.BondToolAddCursor = []
    w.BondToolAddCursor.append(QCursor(getpixmap("ui/cursors/SelectAtomsAddCursor.png"), 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond1ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond2ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond3ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("BondAToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("BondGToolAddCursor", 0, 0))

    # Build mode - Bond Tool cursors with Control/Cmd modkey pressed
    w.BondToolSubtractCursor = []
    w.BondToolSubtractCursor.append(QCursor(getpixmap("ui/cursors/SelectAtomsSubtractCursor.png"), 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond1ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond2ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond3ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("BondAToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("BondGToolSubtractCursor", 0, 0))

    # Select Chunks mode - normal cursors
    w.MolSelCursor = loadCursor("MolSelCursor", 0, 0) # was SelectMolsCursor
    w.MolSelAddCursor = loadCursor("MolSelAddCursor", 0, 0) # was SelectMolsAddCursor
    w.MolSelSubCursor = loadCursor("MolSelSubCursor", 0, 0) # was SelectMolsSubCursor

    # Translate select cursors
    w.MolSelTransCursor = loadCursor("MolSelTransCursor", 0, 0) # was MoveSelectCursor
    w.MolSelTransAddCursor = loadCursor("MolSelTransAddCursor", 0, 0) # was MoveSelectAddCursor
    w.MolSelTransSubCursor = loadCursor("MolSelTransSubCursor", 0, 0) # was MoveSelectSubtractCursor

    # Rotate select cursors
    w.MolSelRotCursor = loadCursor("MolSelRotCursor", 0, 0) # was MoveSelectCursor
    w.MolSelRotAddCursor = loadCursor("MolSelRotAddCursor", 0, 0) # was MoveSelectAddCursor
    w.MolSelRotSubCursor = loadCursor("MolSelRotSubCursor", 0, 0) # was MoveSelectSubtractCursor

    # Misc rotate and translate cursors
    w.MolSelAxisRotTransCursor = loadCursor("MolSelAxisRotTransCursor", -1, -1) # Shift accel key - was MoveAxisRotateMolCursor
    #w.MolSelRotCursor = loadCursor("MolSelRotCursor", -1, -1) # Control/Cmd accel key - was MoveFreeRotateMolCursor

    # Cookie Cutter mode - normal cursors
    w.CookieCursor = loadCursor("CookieCursor", -1, -1)
    w.CookieAddCursor = loadCursor("CookieAddCursor", -1, -1)
    w.CookieSubtractCursor = loadCursor("CookieSubtractCursor", -1, -1)

    # View Zoom, Pan, Rotate cursors
    w.ZoomCursor = QCursor(getpixmap("ui/cursors/ZoomCursor.png"), 0, 0)
    w.PanViewCursor = QCursor(getpixmap("ui/cursors/PanViewCursor.png"), 0, 0)
    w.RotateViewCursor = QCursor(getpixmap("ui/cursors/RotateViewCursor.png"), 0, 0)

    # Miscellaneous cursors
    w.RotateZCursor = loadCursor("RotateZCursor", 0, 0)
    w.ZoomPOVCursor = loadCursor("ZoomPOVCursor", -1, -1)
    w.SelectWaitCursor = loadCursor("SelectWaitCursor", 0, 0)
    w.ArrowCursor = QCursor(Qt.ArrowCursor) #bruce 070627

    # Confirmation corner cursors [loaded by bruce 070626 from files committed by mark]
    w._confcorner_OKCursor = \
     QCursor(getpixmap("ui/confcorner/OKCursor.png"), 0, 0)
    w.confcorner_TransientDoneCursor = \
     QCursor(getpixmap("ui/confcorner/TransientDoneCursor.png"), 0, 0)
    w._confcorner_CancelCursor = \
     QCursor(getpixmap("ui/confcorner/CancelCursor.png"), 0, 0)

    # COLOR CURSORS!
    w.colorPencilCursor = \
     QCursor(getpixmap("ui/cursors/Pencil.png"), 0, 0)
    w.pencilHorizontalSnapCursor = \
     QCursor(getpixmap("ui/cursors/Pencil_HorizontalSnap.png"), 0, 0)
    w.pencilVerticalSnapCursor = \
     QCursor(getpixmap("ui/cursors/Pencil_VerticalSnap.png"), 0, 0)

    return # from loadCursors
