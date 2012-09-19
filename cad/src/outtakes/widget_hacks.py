# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
'''
widget_hacks.py

Miscellaneous widget-related code (such as experimental code or
temporary bug workarounds) which needs cleanup before being suitable
for widgets.py.

$Id$

History:

Bruce 050809 moved the "Mac OS X 10.4 Tiger QToolButton bug workaround"
(and related code) from debug_prefs.py into this file, and improved the
bug workaround for Alpha6.
'''
__author__ = 'bruce'

# note: this is now obsolete; the same commit that moves this file into outtakes
# also removes commented-out calls into it from several files in cad/src. [bruce 071005]

# for QToolButton, we need the actual class, for isinstance and superclass-for-subclass-definition,
# not the class-as-perhaps-hacked-object-constructor (which might be a function rather than a class),
# so do this in case I'm hacking the constructor as part of the workaround:
try:
    from __main__ import original_QToolButton as QToolButton
except:
    from PyQt4.Qt import QToolButton

from PyQt4.Qt import QPainter, Qt, QPen, QColor

toolbutton_highlight_color = QColor(80,80,255) # light blue; should perhaps be a pref

_enable_hacked_QToolButton_paintEvent = False # set to True by a specific command

class hacked_QToolButton(QToolButton):
    is_hacked_class = True
    def paintEvent(self, event):
        res = QToolButton.paintEvent(self, event)
        if _enable_hacked_QToolButton_paintEvent and self.isChecked():
            r = event.rect()
            x,y = r.left(), r.top()
            w,h = r.width(), r.height()
            # There are at least three rect sizes: 30x35, 30x36, 32x33 (see debug-print below).
            # Not sure if this sometimes includes some padding around the icon.
            ## print r.top(),r.bottom(),r.height(), r.left(),r.right(),r.width()
            ## 0 29 30 0 34 35
            ## 0 29 30 0 35 36
            ## 0 31 32 0 32 33
            p = QPainter(self, True) # True claims to mean un-clipped -- not sure if this is good.
                ## Qt4 error: TypeError: too many arguments to QPainter(), 1 at most expected
            color = toolbutton_highlight_color
            p.setPen(QPen(color, 3)) # try 3 and 2
            p.drawRect(x+2,y+2,w-4,h-4) #e could also try drawRoundRect(r, xroundedness, yroundedness)
        return res
    pass

def replacement_QToolButton_constructor(*args): #e could probably just install the class instead of this function
    return hacked_QToolButton(*args)

def replace_QToolButton_constructor( func):
    "only call this once, and call it before any QToolButton is made"
    import PyQt4.Qt as qt #bruce 070425 bugfix in Qt4 port: added "as qt"
    import __main__
    __main__.original_QToolButton = qt.QToolButton
    qt.QToolButton = func
    ## print "replaced qt.QToolButton %r with %r" % ( __main__.original_QToolButton, func)
    # The following is needed for this to work on Qt4 [bruce 070425]:
    for attr in ('MenuButtonPopup',):
        val = getattr( __main__.original_QToolButton, attr)
        setattr(func, attr, val)
    return

def doit3():
    "this is called once very early in startup, on Qt3 Macs only"
    # Note: it might not be necessary to call this when using Qt4, since the Qt3 bug it was meant to work around
    # may have been fixed in Qt4. We've never tested this. The debug menu option it supports,
    # "Mac OS 10.4 QToolButton workaround", also doesn't yet work in Qt4 due to an incomplete port
    # (see the "Qt4 error" comments herein). For these reasons I'm disabling the call to this routine
    # and that debug menu command in Qt4. We'll need to test a built release on Tiger to find out if the
    # bug this worked around is still present. If so, we'll need to reenable this code and complete the port to Qt4.
    # [bruce 070425]
    replace_QToolButton_constructor( replacement_QToolButton_constructor)

# ==

def hack_QToolButton_1(qtoolbutton): #bruce 050729 experiment to work around QToolButton bug in Mac OS X 10.4 Tiger
    """Replace a QToolButton's icons with better ones (but they are not perfect -- the highlight rect is too small; don't know why).
    Only works for QToolButtons which don't have text (don't know why).
    """
    text = str( qtoolbutton.text() )
    if text:
        return # return early
    iconset = qtoolbutton.iconSet()
        ## Qt4 error: AttributeError: iconSet
    from utilities.debug_prefs import modify_iconset_On_states
    modify_iconset_On_states(iconset, use_color = toolbutton_highlight_color )
    qtoolbutton.setIcon(iconset) #k might not be needed
    return

def apply2allchildwidgets(widget, func):
    func(widget)
    kids = widget.children() # guess about how to call QObject.children()
    if kids: #k not sure if test is needed
        for kid in kids:
            apply2allchildwidgets( kid, func)
    return

def hack_if_toolbutton(widget):
    if isinstance(widget, QToolButton):
        try:
            widget.is_hacked_class
        except AttributeError:
            pass
        else:
            return
        hack_QToolButton_1(widget) # this one works for toolbars; hacked class works in MMTK; #e make them the same size/pos??
    return

def hack_every_QToolButton(win): #bruce 050806, revised 050809
    global _enable_hacked_QToolButton_paintEvent
    _enable_hacked_QToolButton_paintEvent = True # this gets the ones in the MMTK
    apply2allchildwidgets(win, hack_if_toolbutton) # and this is needed for the ones in toolbars
    # Warning about MMTK widget: this has no effect on it if it's not yet created (or maybe, not presently shown, I don't know).
    # If it is, then it messed up its toolbuttons by making the textual ones blank, though the iconic ones are ok.
    # So I exclude them by detecting the fact that they have text. This works, but then they don't benefit from the workaround.
    # As for its hybrid buttons, the ones visible at the time work, but if you change elements, they don't,
    # not even if you change back to the same element (I don't know why). [as of bruce 050806 6:45pm]
    #e It would be good to count how many we do this to, and return that, for printing into history,
    # so if you do it again you can see if you caught more that time.
    return

# this gets printed into history by caller of hack_every_QToolButton, unless it's "":
hack_every_QToolButton_warning = "(This might not be visible in dialogs until they're next used or reopened.)"
  ## older: "(As of 050806, this doesn't yet work perfectly for the MMTK buttons.)" ))

# == part of a hack to get another pref checkbox into A6. Not now used, but maybe useful in the future. [bruce 050806-09]

def find_layout(widget):
    "search all layouts under widget's toplevel widget to find the (first) (#e enabled?) layout controlling widget"
    win = widget.topLevelWidget()
    from PyQt4.Qt import QLayout
    res = []
    keep = [] # for making debug print addrs not be reused
    widgeo = widget.geometry() # QRect object
    # comparing geometries is the only way i can figure out to find which layout controls which widget;
    # I'll take the smallest area layout that contains the widget
    ##print "widget geom",widgeo,widgeo.left(),widgeo.right(),widgeo.top(),widgeo.bottom()
    def hmm(child):
        if not isinstance(child,QLayout):
            return
##        print "layout name:",str(child.name())
##            # they all say "unnamed" even though the source code gives them a name
        geo = child.geometry() # QRect object
        area = (geo.right() - geo.left()) * (geo.bottom() - geo.top())
        contains = geo.contains(widgeo)
        if not contains:
            return
        res.append(( area,child ))
        return
    apply2allchildwidgets(win, hmm)
    res.sort()
    return res[0][1]

def qlayout_items(qlayout):
    return qlayoutiterator_items( qlayout.iterator())

def qlayoutiterator_items(qlayoutiterator):
    res = []
    res.append(qlayoutiterator.current()) #k not sure if needed, but apparently doesn't cause redundant item
    while 1:
        n1 = qlayoutiterator.next()
        if not n1:
            break
        res.append(n1) # the ref to this might be needed to make the iterator keep going after it...
        # no, that's not it - my debug prints are explained this way:
        # if the ref is not kept, we reuse the same mem for each new python obj, so pyobj addr is same tho C obj is diff.
    return res

# ===

# end
