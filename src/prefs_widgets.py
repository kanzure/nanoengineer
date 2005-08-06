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

from changes import Formula ###IMPLEM
from widgets import RGBf_to_QColor
from qt import QColorDialog

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
        # this calls the setter now and whenever the lambda-value changes, until it' destroyed
        # or until there's any exception in either arg that it calls.
    colorframe.__bgcolor_conn = conn
    return

# end
