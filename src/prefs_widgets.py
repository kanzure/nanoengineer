# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
prefs_widgets.py

Utilities related to both user preferences and Qt widgets.

$Id$

History:

Bruce 050805 started this module.
'''

__author__ = ['Bruce']

import env # for env.prefs
from debug import print_compact_traceback
import platform

from changes import Formula
from widgets import RGBf_to_QColor
from qt import QColorDialog
from qt import SIGNAL

def colorpref_edit_dialog( parent, prefs_key, caption = "choose"): #bruce 050805
    #bruce 050805: heavily modified this from some slot methods in UserPrefs.py.
    # Note that the new code for this knows the prefs key and that it's a color,
    # and nothing else that those old slot methods needed to know!
    # It no longer needs to know about the color swatch (if any) that shows this color in the UI,
    # or what/how to update anything when the color is changed,
    # or where the color is stored besides in env.prefs.
    # That knowledge now resides with the code that defines it, or in central places.
    
    ## old_color = self.bond_vane_color_frame.paletteBackgroundColor()
    old_color = RGBf_to_QColor( env.prefs[prefs_key] )
    c = QColorDialog.getColor(old_color, parent, caption)
    if c.isValid():
        new_color = (c.red()/255.0, c.green()/255.0, c.blue()/255.0)
        ## self.bond_vane_color_frame.setPaletteBackgroundColor(c)
        # instead, subscribe that color swatch (whenever dialog is shown) to the prefs value for the color
        env.prefs[prefs_key] = new_color
        ## self.glpane.gl_update() [this was not enough anyway, and now it's not needed]
    return

def connect_colorpref_to_colorframe( pref_key, colorframe ): #bruce 050805
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
    def colorframe_bgcolor_setter(color):
        #e no convenient/clean way for Formula API to permit but not require this function to receive the formula,
        # unless we store it temporarily in env._formula (which we might as well do if this feature is ever needed)
        try:
            # make sure errors here don't stop the formula from running:
            # (Need to protect against certain kinds of erroneous color values? RGBf_to_QColor does it well enough.)
            colorframe.setPaletteBackgroundColor(RGBf_to_QColor(color))
            ## colorframe.update() ###@@@ guess at bugfix -- not sure if has an effect... after this, 2nd time and beyond, color changes,
                # but wrongly. before this? not sure. now it always sets to the prior color. hmm, check Formula code.
            if 0 and platform.atom_debug:
                print "atom_debug: fyi: colorframe %r set color %r for prefkey %r" % (colorframe,color,pref_key)
        except:
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
