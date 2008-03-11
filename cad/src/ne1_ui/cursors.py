# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
cursors.py - load all the custom cursors needed by NE1

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

mark 060427 - loadCursors() moved from MWsemantics.py.

To do: (Mark)
- Find and replace all uses of self.o.setCursor(QCursor(Qt.ArrowCursor)) with
self.o.setCursor(win.ArrowCursor)).
- Replace all bitmap cursors with color PNG cursors.
"""

from PyQt4.Qt import QCursor, QBitmap, Qt, QPainter
import os, sys

from icon_utilities import getCursorPixmap

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
    
    # Pencil symbols.
    w.addSymbol = QCursor(getCursorPixmap("symbols/PlusSign.png"), 0, 0)
    w.subtractSymbol = QCursor(getCursorPixmap("symbols/MinusSign.png"), 0, 0)
    
    # Selection lock symbol
    w.selectionLockSymbol = QCursor(getCursorPixmap("symbols/SelectionLock.png"), 0, 0)
    
    # Pencil symbols.
    horizontalSymbol = \
        QCursor(getCursorPixmap("symbols/HorizontalSnap.png"), 0, 0)
    verticalSymbol = \
        QCursor(getCursorPixmap("symbols/VerticalSnap.png"), 0, 0)
    
    # Pencil cursors
    w.colorPencilCursor = QCursor(getCursorPixmap("Pencil.png"), 0, 0)
    
    w.pencilHorizontalSnapCursor = \
        createCompositeCursor(w.colorPencilCursor, horizontalSymbol, 
                              offsetX = 22, offsetY = 22)
    w.pencilVerticalSnapCursor = \
        createCompositeCursor(w.colorPencilCursor, verticalSymbol, 
                              offsetX = 22, offsetY = 22)
    
    # Select Chunks cursors
    w.SelectArrowCursor = QCursor(getCursorPixmap("SelectArrowCursor"), 0, 0)
    w.SelectArrowAddCursor = \
     createCompositeCursor(w.SelectArrowCursor, w.addSymbol, 
                           offsetX = 12, offsetY = 0)
    w.SelectArrowSubtractCursor = \
     createCompositeCursor(w.SelectArrowCursor, w.subtractSymbol, 
                           offsetX = 12, offsetY = 0)

    # Build Atoms - normal cursors
    w.SelectAtomsCursor = \
     QCursor(getCursorPixmap("SelectAtomsCursor.png"), 0, 0)
    
    w.SelectAtomsAddCursor = \
     createCompositeCursor(w.SelectAtomsCursor, w.addSymbol, 
                           offsetX = 12, offsetY = 0)
    w.SelectSubtractCursor = \
     createCompositeCursor(w.SelectAtomsCursor, w.subtractSymbol, 
                           offsetX = 12, offsetY = 0)
    w.DeleteCursor = \
     QCursor(getCursorPixmap("DeleteCursor.png"), 0, 0)

    # Build Atoms - Atom Selection Filter cursors
    w.SelectAtomsFilterCursor = \
     QCursor(getCursorPixmap("SelectAtomsFilterCursor.png"), 0, 0)
    
    w.SelectAtomsAddFilterCursor = \
     createCompositeCursor(w.SelectAtomsFilterCursor, w.addSymbol, 
                           offsetX = 12, offsetY = 0)
    w.SelectAtomsSubtractFilterCursor = \
     createCompositeCursor(w.SelectAtomsFilterCursor, w.subtractSymbol, 
                           offsetX = 12, offsetY = 0)
    
    w.DeleteAtomsFilterCursor = \
     QCursor(getCursorPixmap("DeleteAtomsFilterCursor.png"), 0, 0)

    # Build Atoms - Bond Tool cursors with no modkey pressed
    w.BondToolCursor = []
    w.BondToolCursor.append(QCursor(getCursorPixmap("SelectAtomsCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("Bond1ToolCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("Bond2ToolCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("Bond3ToolCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("BondAToolCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("BondGToolCursor.png"), 0, 0))
    w.BondToolCursor.append(QCursor(getCursorPixmap("CutBondCursor.png"), 0, 0))

    # Build Atoms - Bond Tool cursors with Shift modkey pressed
    w.BondToolAddCursor = []
    for cursor in w.BondToolCursor:
        w.BondToolAddCursor.append(
            createCompositeCursor(cursor, w.addSymbol, 
                                  offsetX = 12, offsetY = 0))

    # Build Atoms - Bond Tool cursors with Control/Cmd modkey pressed
    w.BondToolSubtractCursor = []
    for cursor in w.BondToolCursor:
        w.BondToolSubtractCursor.append(
            createCompositeCursor(cursor, w.subtractSymbol, 
                                  offsetX = 12, offsetY = 0))

    # Translate selection cursors
    w.TranslateSelectionCursor = \
     QCursor(getCursorPixmap("TranslateSelectionCursor"), 0, 0)
    w.TranslateSelectionAddCursor = \
     createCompositeCursor(w.TranslateSelectionCursor, w.addSymbol, 
                           offsetX = 12, offsetY = 0)
    w.TranslateSelectionSubtractCursor = \
     createCompositeCursor(w.TranslateSelectionCursor, w.subtractSymbol, 
                           offsetX = 12, offsetY = 0)

    # Rotate selection cursors
    w.RotateSelectionCursor = QCursor(getCursorPixmap("RotateSelectionCursor"), 0, 0)
    
    w.RotateSelectionAddCursor = \
     createCompositeCursor(w.RotateSelectionCursor, w.addSymbol, 
                           offsetX = 12, offsetY = 0)
    w.RotateSelectionSubtractCursor = \
     createCompositeCursor(w.RotateSelectionCursor, w.subtractSymbol, 
                           offsetX = 12, offsetY = 0)

    # Axis translation/rotation cursor
    w.AxisTranslateRotateSelectionCursor = QCursor(getCursorPixmap("AxisTranslateRotateSelectionCursor"), 0, 0)

    # Build Crystal cursors
    w.CookieCursor = QCursor(getCursorPixmap("Pencil.png"), 0, 0)
    w.CookieAddCursor = \
     createCompositeCursor(w.colorPencilCursor, w.addSymbol, \
                           offsetX = 12, offsetY = 0)
    w.CookieSubtractCursor = \
     createCompositeCursor(w.colorPencilCursor, w.subtractSymbol, \
                           offsetX = 12, offsetY = 0)
    
    # View Zoom, Pan, Rotate cursors
    w.ZoomCursor = QCursor(getCursorPixmap("ZoomCursor.png"), 0, 0)
    w.ZoomInOutCursor = QCursor(getCursorPixmap("ZoomInOutCursor.png"), 0, 0)
    w.PanViewCursor = QCursor(getCursorPixmap("PanViewCursor.png"), 0, 0)
    w.RotateViewCursor = QCursor(getCursorPixmap("RotateViewCursor.png"), 0, 0)

    # Miscellaneous cursors
    w.RotateZCursor = QCursor(getCursorPixmap("RotateZCursor.png"), 0, 0)
    w.ZoomPovCursor = QCursor(getCursorPixmap("ZoomPovCursor.png"), -1, -1)
    w.ArrowWaitCursor = QCursor(getCursorPixmap("ArrowWaitCursor.png"), 0, 0)
    w.ArrowCursor = QCursor(Qt.ArrowCursor) #bruce 070627

    # Confirmation corner cursors [loaded by bruce 070626 from files committed by mark]
    w._confcorner_OKCursor = \
     QCursor(getCursorPixmap("OKCursor.png"), 0, 0)
    w.confcorner_TransientDoneCursor = \
     QCursor(getCursorPixmap("TransientDoneCursor.png"), 0, 0)
    w._confcorner_CancelCursor = \
     QCursor(getCursorPixmap("CancelCursor.png"), 0, 0)
    
    # Some Build Dna mode cursors
    w.rotateAboutCentralAxisCursor = \
     QCursor(getCursorPixmap("Rotate_About_Central_Axis.png"), 0, 0)
    w.translateAlongCentralAxisCursor = \
     QCursor(getCursorPixmap("Translate_Along_Central_Axis.png"), 0, 0)
    
    return # from loadCursors

def createCompositeCursor(cursor, overlayCursor, 
                          hotX = None, hotY = None, 
                          offsetX = 0, offsetY = 0):
    """
    Returns a composite 32x32 cursor using two other cursors.

    This is useful for creating composite cursor images from two (or more)
    cursors.
    
    For example, the pencil cursor includes a horizontal and vertical 
    symbol when drawing a horizontal or vertical line. This function can
    be used to create these cursors without having to create each one by hand.
    The payoff is when the developer/artist wants to change the base cursor 
    image (i.e. the pencil cursor) without having to redraw and save all the 
    other versions of the cursor in the set.
    
    @param cursor: The main cursor.
    @type  cursor: QCursor
    
    @param overlayCursor: The cursor to overlay on top of I{cursor}.
    @type  overlayCursor: QCursor
    
    @param hotX: The X coordinate of the hotspot. If none is given, the
                 hotspot of I{cursor} is used.
    @type  hotX: int
    
    @param hotY: The Y coordinate of the hotspot. If none is given, the
                 hotspot of I{cursor} is used.
    @type  hotY: int
    
    @param offsetX: The X offset in which to draw the overlay cursor onto
                    I{cursor}. The default is 0.
    @type  offsetX: int
    
    @param offsetY: The Y offset in which to draw the overlay cursor onto
                    I{cursor}. The default is 0.
    @type  offsetY: int
    
    @return: The composite cursor.
    @rtype:  QCursor
    
    @note: It would be easy and useful to allow overlayCursor to be a QPixmap.
           I'll add this when it becomes helpful. --Mark 2008-03-06.
    """
    # Method: 
    # 1. Get cursor's pixmap and create a painter from it.
    # 2. Get the pixmap from the overlay cursor and draw it onto the
    #    cursor pixmap to create the composite pixmap.
    # 3. Create and return a new QCursor from the composite pixmap.
    # Mark 2008-03-05
    
    assert isinstance(cursor, QCursor)
    assert isinstance(overlayCursor, QCursor)
    
    if hotX is None:
        hotX = cursor.hotSpot().x()
    if hotY is None:
        hotY = cursor.hotSpot().y()
    pixmap = cursor.pixmap()
    overlayPixmap = overlayCursor.pixmap()
    painter = QPainter(pixmap)
    painter.drawPixmap(offsetX, offsetY, overlayPixmap)
    painter.end()
    return QCursor(pixmap, hotX, hotY)
    

