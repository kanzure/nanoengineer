# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
cursors.py

$Id$

mark 060427 - loadCursors() moved from MWsemantics.py.
"""

__author__ = "Mark" 

from qt import QCursor, QBitmap
import os, sys
        
def loadCursors(w):
    '''This routine is called once to load all the custom cursors needed by the program.
    To add a new cursor, two BMP files are placed in the cad/images directory:
        <cursor_name>.bmp - the cursor bitmap file 
        <cursor_name>-bm.bmp - the cursor's bitmask file 
    Then you simply add a single line of code below to load the custom cursor.
    <w> is the main window (parent) object for all custom cursors.
    '''
    
    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

    def loadCursor(cursor_name, hot_x, hot_y):
        '''Returns a cursor built from two BMP files located in the cad/images directory:
            <cursor_name>.bmp - the cursor bitmap file 
            <cursor_name>-bm.bmp - the cursor's bitmask file 
        
        <hot_x> and <hot_y> define the cursor's hotspot.
        
        I would like move all the custom cursor files an exclusive directory (i.e. cad/ui/cursors)
        and then read that directory at startup to create the cursors from the files.
        I'd also like to change the cursor filename format to the following:
            <cursor_name>_bitmap.bmp - the cursor bitmap file 
            <cursor_name>_bitmask.bmp - the cursor's bitmask file 
        The existence of these two files would automatically create the cursor w.<cursor_name>
        I need to discuss this with Bruce more, especially since I don't know how to
        create the cursor_name from the filename. Mark 060428.
        '''
        cursor_bitmap = filePath + "/../images/" + cursor_name + ".bmp"
        cursor_bitmsk = filePath + "/../images/" + cursor_name + "-bm.bmp"
        
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
    w.SelectAtomsCursor = loadCursor("SelectAtomsCursor", 0, 0)
    w.SelectAtomsAddCursor = loadCursor("SelectAtomsAddCursor", 0, 0)
    w.SelectAtomsSubtractCursor = loadCursor("SelectAtomsSubtractCursor", 0, 0)
    w.DeleteCursor = loadCursor("DeleteCursor", 0, 0)
        
    # Build mode - Atom Selection cursors
    w.SelectAtomsFilterCursor = loadCursor("SelectAtomsFilterCursor", 0, 0)
    w.SelectAtomsAddFilterCursor = loadCursor("SelectAtomsAddFilterCursor", 0, 0)
    w.SelectAtomsSubtractFilterCursor = loadCursor("SelectAtomsSubtractFilterCursor", 0, 0)
    w.DeleteFilterCursor = loadCursor("DeleteFilterCursor", 0, 0)
        
    # Build mode - Bond Tool cursors with no modkey pressed
    w.BondToolCursor = []
    w.BondToolCursor.append(loadCursor("SelectAtomsCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("Bond1ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("Bond2ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("Bond3ToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("BondAToolCursor", 0, 0))
    w.BondToolCursor.append(loadCursor("BondGToolCursor", 0, 0))
        
    # Build mode - Bond Tool cursors with Shift modkey pressed
    w.BondToolAddCursor = []
    w.BondToolAddCursor.append(loadCursor("SelectAtomsAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond1ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond2ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("Bond3ToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("BondAToolAddCursor", 0, 0))
    w.BondToolAddCursor.append(loadCursor("BondGToolAddCursor", 0, 0))
        
    # Build mode - Bond Tool cursors with Control/Cmd modkey pressed
    w.BondToolSubtractCursor = []
    w.BondToolSubtractCursor.append(loadCursor("SelectAtomsSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond1ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond2ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("Bond3ToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("BondAToolSubtractCursor", 0, 0))
    w.BondToolSubtractCursor.append(loadCursor("BondGToolSubtractCursor", 0, 0))
        
    # Select Chunks mode - normal cursors
    w.SelectMolsCursor = loadCursor("SelectMolsCursor", 0, 0)
    w.SelectMolsAddCursor = loadCursor("SelectMolsAddCursor", 0, 0)
    w.SelectMolsSubtractCursor = loadCursor("SelectMolsSubtractCursor", 0, 0)
        
    # Move mode - normal cursors
    w.MoveCursor = loadCursor("MoveCursor", 0, 0)
    w.MoveSelectCursor = loadCursor("MoveSelectCursor", -1, -1)
    #w.MoveAddCursor = loadCursor("MoveAddCursor", -1, -1) # Not used
    #w.MoveSubtractCursor = loadCursor("MoveSubtractCursor", -1, -1) # Not used
    w.MoveAxisRotateMolCursor = loadCursor("MoveRotateMolCursor", -1, -1) # Shift
    w.MoveFreeRotateMolCursor = loadCursor("RotateMolCursor", -1, -1) # Control/Cmd
        
    # Cookie Cutter mode - normal cursors
    w.CookieCursor = loadCursor("CookieCursor", -1, -1)
    w.CookieAddCursor = loadCursor("CookieAddCursor", -1, -1)
    w.CookieSubtractCursor = loadCursor("CookieSubtractCursor", -1, -1)
        
    # Miscellaneous cursors
    w.ZoomCursor = loadCursor("ZoomCursor", 10, 10)
    w.RotateCursor = loadCursor("RotateCursor", 0, 0)
    w.RotateZCursor = loadCursor("RotateZCursor", 0, 0)
    w.ZoomPOVCursor = loadCursor("ZoomPOVCursor", -1, -1)
    w.SelectWaitCursor = loadCursor("SelectWaitCursor", 0, 0)

    return # from loadCursors