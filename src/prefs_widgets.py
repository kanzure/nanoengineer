# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
prefs_widgets.py

Utilities related to both user preferences and Qt widgets.

$Id$

History:

Bruce 050805 started this module.
"""

__author__ = ['Bruce']

import env # for env.prefs
from debug import print_compact_traceback
import platform

from changes import Formula
from widgets import RGBf_to_QColor
from PyQt4.Qt import QColorDialog
from PyQt4.Qt import SIGNAL
from PyQt4.QtGui import QPalette

def colorpref_edit_dialog( parent, prefs_key, caption = "choose"): #bruce 050805; revised 070425 in Qt4 branch
    #bruce 050805: heavily modified this from some slot methods in UserPrefs.py.
    # Note that the new code for this knows the prefs key and that it's a color,
    # and nothing else that those old slot methods needed to know!
    # It no longer needs to know about the color swatch (if any) that shows this color in the UI,
    # or what/how to update anything when the color is changed,
    # or where the color is stored besides in env.prefs.
    # That knowledge now resides with the code that defines it, or in central places.
    
    old_color = RGBf_to_QColor( env.prefs[prefs_key] )
    c = QColorDialog.getColor(old_color, parent) # In Qt3 this also had a caption argument
    if c.isValid():
        new_color = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
        env.prefs[prefs_key] = new_color
            # this is change tracked, which permits the UI's color swatch
            # (as well as the glpane itself, or whatever else uses this prefs color)
            # to notice this and update its color
    return

def connect_colorpref_to_colorframe( pref_key, colorframe ): #bruce 050805; revised 070425/070430 in Qt4 branch
    """Cause the bgcolor of the given Qt "color frame" to be set to each new legal color value stored in the given pref."""
    # first destroy any prior connection trying to control the same thing
    try:
        conn = colorframe.__bgcolor_conn # warning: this is *not* name-mangled, since we're not inside a class.
        assert conn is not None
    except: # several kinds of exceptions are possible
        pass
    else:
        conn.destroy() # this removes any subscriptions that object held
    colorframe.__bgcolor_conn = None # in case of exceptions in the following
    # For Qt4, to fix bug 2320, we need to give the colorframe a unique palette, in which we can modify the background color.
    # To get this to work, it was necessary to make a new palette each time the color changes, modify it, and re-save into colorframe
    # (done below). This probably relates to "implicit sharing" of QPalette (see Qt 4.2 online docs).
    # [bruce 070425]
    def colorframe_bgcolor_setter(color):
        #e no convenient/clean way for Formula API to permit but not require this function to receive the formula,
        # unless we store it temporarily in env._formula (which we might as well do if this feature is ever needed)
        try:
            # make sure errors here don't stop the formula from running:
            # (Need to protect against certain kinds of erroneous color values? RGBf_to_QColor does it well enough.)
            ## Qt3 code used: colorframe.setPaletteBackgroundColor(RGBf_to_QColor(color))
            qcolor = RGBf_to_QColor(color)
            palette = QPalette() # QPalette(qcolor) would have window color set from qcolor, but that doesn't help us here
            qcolorrole = QPalette.Window
                ## http://doc.trolltech.com/4.2/qpalette.html#ColorRole-enum says:
                ##   QPalette.Window    10    A general background color.
            palette.setColor(QPalette.Active, qcolorrole, qcolor) # used when window is in fg and has focus
            palette.setColor(QPalette.Inactive, qcolorrole, qcolor) # used when window is in bg or does not have focus
            palette.setColor(QPalette.Disabled, qcolorrole, qcolor) # used when widget is disabled
            colorframe.setPalette(palette)
            colorframe.setAutoFillBackground(True)
            # [Note: the above scheme was revised again by bruce 070430, for improved appearance
            #  (now has thin black border around color patch), based on Ninad's change in UserPrefs.py.]
            ## no longer needed: set color for qcolorrole = QPalette.ColorRole(role) for role in range(14)
            ## no longer needed: colorframe.setLineWidth(500) # width of outline of frame (at least half max possible size)
        except:
            print "data for following exception: ",
            print "colorframe %r has palette %r" % (colorframe, colorframe.palette())
                # fyi: in Qt4, like in Qt3, colorframe is a QFrame
            print_compact_traceback( "bug (ignored): exception in formula-setter: " ) #e include formula obj in this msg?
        pass
    conn = Formula( lambda: env.prefs.get( pref_key) , colorframe_bgcolor_setter )
        # this calls the setter now and whenever the lambda-value changes, until it's destroyed
        # or until there's any exception in either arg that it calls.
    colorframe.__bgcolor_conn = conn
    return

class destroyable_Qt_connection:
    "holds a Qt signal/slot connection, but has a destroy method which disconnects it [#e no way to remain alive but discon/con it]"
    def __init__(self, sender, signal, slot, owner = None):
        if owner is None:
            owner = sender # I hope that's ok -- not sure it is -- if not, put owner first in arglist, or, use topLevelWidget
        self.vars = owner, sender, signal, slot
        owner.connect(sender, signal, slot)
    def destroy(self):
        owner, sender, signal, slot = self.vars
        owner.disconnect(sender, signal, slot)
        self.vars = None # error to destroy self again
    pass

class list_of_destroyables:
    "hold 0 or more objects, so that when we're destroyed, so are they"
    def __init__(self, *objs):
        self.objs = objs
    def destroy(self):
        for obj in self.objs:
            #e could let obj be a list and do this recursively
            obj.destroy()
        self.objs = None # error to destroy self again (if that's bad, set this to [] instead)
    pass

def connect_checkbox_with_boolean_pref( qcheckbox, pref_key ): #bruce 050810
    """Cause the checkbox to track the value of the given boolean preference,
    and cause changes to the checkbox to change the preference.
    (Use of the word "with" in the function name, rather than "to" or "from",
     is meant to indicate that this connection is two-way.)
    First remove any prior connection of the same type on the same checkbox.
    Legal for more than one checkbox to track and control the same pref [but that might be untested].
    """
    # first destroy any prior connection trying to control the same thing
    # [modified from code in connect_colorpref_to_colorframe; ##e should make this common code of some kind]
    try:
        conn = qcheckbox.__boolean_pref_conn # warning: this is *not* name-mangled, since we're not inside a class.
        assert conn is not None
    except: # several kinds of exceptions are possible
        pass
    else:
        conn.destroy() # this removes any subscriptions that object held
    qcheckbox.__boolean_pref_conn = None # in case of exceptions in the following
    setter = qcheckbox.setChecked #e or we might prefer a setter which wraps this with .blockSignals(True)/(False)
    conn1 = Formula( lambda: env.prefs.get( pref_key) , setter )
        # this calls the setter now and whenever the lambda-value changes, until it's destroyed
        # or until there's any exception in either arg that it calls.
    def prefsetter(val):
        #e should we assert val is boolean? nah, just coerce it:
        val = not not val
        env.prefs[pref_key] = val
    conn2 = destroyable_Qt_connection( qcheckbox, SIGNAL("toggled(bool)"), prefsetter )
    qcheckbox.__boolean_pref_conn = list_of_destroyables( conn1, conn2)
    return

# end
