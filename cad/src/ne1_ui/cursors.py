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

from PyQt4.Qt import QCursor, QBitmap, Qt, QPainter, QApplication
import os, sys

from utilities.icon_utilities import getCursorPixmap

def showWaitCursor(on_or_off):
    """
    Show the wait cursor or revert to the prior cursor if the current cursor
    is the wait cursor.

    For on_or_off True, set the main window waitcursor.
    For on_or_off False, revert to the prior cursor.

    [It might be necessary to always call it in matched pairs,
     I don't know [bruce 050401].]
    """
    if on_or_off:
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
    else:
        QApplication.restoreOverrideCursor() # Restore the cursor
    return

def loadCursors(w):
    """
    This routine is called once to load all the custom cursors needed by NE1.
    """

    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Pencil symbols.
    w.addSymbol = QCursor(getCursorPixmap("symbols/PlusSign.png"), 0, 0)
    w.subtractSymbol = QCursor(getCursorPixmap("symbols/MinusSign.png"), 0, 0)

    # Selection lock symbol
    w.selectionLockSymbol = \
     QCursor(getCursorPixmap("symbols/SelectionLock.png"), 0, 0)

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
    w.SelectArrowCursor = \
     QCursor(getCursorPixmap("SelectArrowCursor.png"), 0, 0)
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
    w.SelectAtomsSubtractCursor = \
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
     QCursor(getCursorPixmap("TranslateSelectionCursor.png"), 0, 0)
    w.TranslateSelectionAddCursor = \
     createCompositeCursor(w.TranslateSelectionCursor, w.addSymbol,
                           offsetX = 12, offsetY = 0)
    w.TranslateSelectionSubtractCursor = \
     createCompositeCursor(w.TranslateSelectionCursor, w.subtractSymbol,
                           offsetX = 12, offsetY = 0)

    # Rotate selection cursors
    w.RotateSelectionCursor = \
     QCursor(getCursorPixmap("RotateSelectionCursor.png"), 0, 0)

    w.RotateSelectionAddCursor = \
     createCompositeCursor(w.RotateSelectionCursor, w.addSymbol,
                           offsetX = 12, offsetY = 0)
    w.RotateSelectionSubtractCursor = \
     createCompositeCursor(w.RotateSelectionCursor, w.subtractSymbol,
                           offsetX = 12, offsetY = 0)

    # Axis translation/rotation cursor
    w.AxisTranslateRotateSelectionCursor = \
     QCursor(getCursorPixmap("AxisTranslateRotateSelectionCursor.png"), 0, 0)

    # Build Crystal cursors
    w.CookieCursor = QCursor(getCursorPixmap("Pencil.png"), 0, 0)
    w.CookieAddCursor = \
     createCompositeCursor(w.colorPencilCursor, w.addSymbol, \
                           offsetX = 12, offsetY = 0)
    w.CookieSubtractCursor = \
     createCompositeCursor(w.colorPencilCursor, w.subtractSymbol, \
                           offsetX = 12, offsetY = 0)

    # View Zoom, Pan, Rotate cursors

    # The zoom cursor(s). One is for a dark background, the other for a light bg.
    # See GLPane.setCursor() for more details about this list.
    w.ZoomCursor = []
    _cursor = QCursor(getCursorPixmap("darkbg/ZoomCursor.png"), 11, 11)
    w.ZoomCursor.append(_cursor)
    _cursor = QCursor(getCursorPixmap("litebg/ZoomCursor.png"), 11, 11)
    w.ZoomCursor.append(_cursor)

    w.ZoomInOutCursor = []
    _cursor = QCursor(getCursorPixmap("darkbg/ZoomCursor.png"), 11, 11)
    w.ZoomInOutCursor.append(_cursor)
    _cursor = QCursor(getCursorPixmap("litebg/ZoomCursor.png"), 11, 11)
    w.ZoomInOutCursor.append(_cursor)

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

    #Rotate about a point cursors
    w.rotateAboutPointCursor = \
     QCursor(getCursorPixmap("RotateAboutPointCursor.png"), 0, 0)

    w.rotateAboutPointHorizontalSnapCursor = \
        createCompositeCursor(w.rotateAboutPointCursor, horizontalSymbol,
                              offsetX = 22, offsetY = 22)
    w.rotateAboutPointVerticalSnapCursor = \
        createCompositeCursor(w.rotateAboutPointCursor, verticalSymbol,
                              offsetX = 22, offsetY = 22)

    #Add a segment to a list of segments to be resized (in Multiple_DnaSegments
    #command)
    w.addSegmentToResizeSegmentListCursor = \
     QCursor(getCursorPixmap("AddSegment_To_ResizeSegmentListCursor.png"), 0, 0)
    w.removeSegmentFromResizeSegmentListCursor = \
     QCursor(getCursorPixmap("RemoveSegment_From_ResizeSegmentList_Cursor.png"), 0, 0)

    w.specifyPlaneCursor = \
     QCursor(getCursorPixmap("SpecifyPlaneCursor.png"), 0, 0)

    w.clickToJoinStrandsCursor = QCursor(getCursorPixmap(
        "ClickToJoinStrands_Cursor.png"), 0, 0)

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


