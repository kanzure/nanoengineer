# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
cursors.py

$Id$

mark 060427 - loadCursors() moved from MWsemantics.py.
"""

__author__ = "Mark" 


def loadCursors(win):
    '''This subroutine is called once to load all the cursors needed by the program.
    <win> is the main window.
    '''

    # Build mode - normal cursors
    win.SelectAtomsCursor = loadCursor("SelectAtomsCursor", 0, 0)
    win.SelectAtomsAddCursor = loadCursor("SelectAtomsAddCursor", 0, 0)
    win.SelectAtomsSubtractCursor = loadCursor("SelectAtomsSubtractCursor", 0, 0)
    win.DeleteCursor = loadCursor("DeleteCursor", 0, 0)
        
    # Build mode - Atom Selection cursors
    win.SelectAtomsFilterCursor = loadCursor("SelectAtomsFilterCursor", 0, 0)
    win.SelectAtomsAddFilterCursor = loadCursor("SelectAtomsAddFilterCursor", 0, 0)
    win.SelectAtomsSubtractFilterCursor = loadCursor("SelectAtomsSubtractFilterCursor", 0, 0)
    win.DeleteFilterCursor = loadCursor("DeleteFilterCursor", 0, 0)
        
    # Build mode - Bond Tool cursors with no modkey pressed
    win.BondToolCursor = []
    win.BondToolCursor.append(loadCursor("SelectAtomsCursor", 0, 0))
    win.BondToolCursor.append(loadCursor("Bond1ToolCursor", 0, 0))
    win.BondToolCursor.append(loadCursor("Bond2ToolCursor", 0, 0))
    win.BondToolCursor.append(loadCursor("Bond3ToolCursor", 0, 0))
    win.BondToolCursor.append(loadCursor("BondAToolCursor", 0, 0))
    win.BondToolCursor.append(loadCursor("BondGToolCursor", 0, 0))
        
    # Build mode - Bond Tool cursors with Shift modkey pressed
    win.BondToolAddCursor = []
    win.BondToolAddCursor.append(loadCursor("SelectAtomsAddCursor", 0, 0))
    win.BondToolAddCursor.append(loadCursor("Bond1ToolAddCursor", 0, 0))
    win.BondToolAddCursor.append(loadCursor("Bond2ToolAddCursor", 0, 0))
    win.BondToolAddCursor.append(loadCursor("Bond3ToolAddCursor", 0, 0))
    win.BondToolAddCursor.append(loadCursor("BondAToolAddCursor", 0, 0))
    win.BondToolAddCursor.append(loadCursor("BondGToolAddCursor", 0, 0))
        
    # Build mode - Bond Tool cursors with Control/Cmd modkey pressed
    win.BondToolSubtractCursor = []
    win.BondToolSubtractCursor.append(loadCursor("SelectAtomsSubtractCursor", 0, 0))
    win.BondToolSubtractCursor.append(loadCursor("Bond1ToolSubtractCursor", 0, 0))
    win.BondToolSubtractCursor.append(loadCursor("Bond2ToolSubtractCursor", 0, 0))
    win.BondToolSubtractCursor.append(loadCursor("Bond3ToolSubtractCursor", 0, 0))
    win.BondToolSubtractCursor.append(loadCursor("BondAToolSubtractCursor", 0, 0))
    win.BondToolSubtractCursor.append(loadCursor("BondGToolSubtractCursor", 0, 0))
        
    # Select Chunks mode - normal cursors
    win.SelectMolsCursor = loadCursor("SelectMolsCursor", 0, 0)
    win.SelectMolsAddCursor = loadCursor("SelectMolsAddCursor", 0, 0)
    win.SelectMolsSubtractCursor = loadCursor("SelectMolsSubtractCursor", 0, 0)
        
    # Move mode - normal cursors
    win.MoveCursor = loadCursor("MoveCursor", 0, 0)
    win.MoveSelectCursor = loadCursor("MoveSelectCursor", -1, -1)
    #win.MoveAddCursor = loadCursor("MoveAddCursor", -1, -1) # Not used
    #win.MoveSubtractCursor = loadCursor("MoveSubtractCursor", -1, -1) # Not used
    win.MoveAxisRotateMolCursor = loadCursor("MoveRotateMolCursor", -1, -1) # Shift
    win.MoveFreeRotateMolCursor = loadCursor("RotateMolCursor", -1, -1) # Control/Cmd
        
    # Cookie Cutter mode - normal cursors
    win.CookieCursor = loadCursor("CookieCursor", -1, -1)
    win.CookieAddCursor = loadCursor("CookieAddCursor", -1, -1)
    win.CookieSubtractCursor = loadCursor("CookieSubtractCursor", -1, -1)
        
    # Miscellaneous cursors
    win.ZoomCursor = loadCursor("ZoomCursor", 10, 10)
    win.RotateCursor = loadCursor("RotateCursor", 0, 0)
    win.RotateZCursor = loadCursor("RotateZCursor", 0, 0)
    win.ZoomPOVCursor = loadCursor("ZoomPOVCursor", -1, -1)
    win.SelectWaitCursor = loadCursor("SelectWaitCursor", 0, 0)

    return # from loadCursors
        
def loadCursor(cursor_name, hot_x, hot_y):
    '''Returns a cursor built from a bitmap file <cursor_name>.bmp and a bitmask file 
    <cursor_name>-bm.bmp  located in the cad/images directory.
    <hot_x> and <hot_y> define the cursor's hotspot.
    '''
    
    from qt import QCursor, QBitmap
    import os, sys
    
    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    cursor = QCursor(
        QBitmap(filePath + "/../images/" + cursor_name + ".bmp"),
        QBitmap(filePath + "/../images/" + cursor_name + "-bm.bmp"),
        hot_x, hot_y)

    return cursor