# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
debug_prefs.py

Some prototype general-prefs code, useful now for "debugging prefs",
i.e. user-settable temporary flags to help with debugging.

$Id$
'''

__all__ = ['debug_pref', 'Choice', 'debug_prefs_menuspec'] # funcs to declare and access prefs; datatypes; UI funcs for prefs

__author__ = "bruce" # 050614

from constants import noop
from constants import black, white, red, green, blue, gray, orange, yellow, magenta, pink

import env

debug_prefs = {} # maps names of debug prefs to "pref objects"

def debug_pref(name, dtype, **options ): #bruce 050725 revised this; bruce 060124 added **options
    """Public function for declaring and registering a debug pref and querying its value.
       Example call: chem.py rev 1.151 (might not  be present in later versions).
       Details: If debug_prefs[name] is known (so far in this session),
    return its current value, and perhaps record the fact that it was used.
       If it's not known, record its existence in the list of active debug prefs
    (visible in a submenu of the debug menu [#e and/or sometimes on the dock])
    and set it to have datatype dtype, with an initial value of dtype's default value,
    or as determined from prefs db if prefs_key option is passed and if this pref has been stored there.
    (Treat dtype's default value as prefs db default value, in that case.)
    (And then record usage and return value, just as in the other case.)
       If prefs_key is passed, also arrange to store changes to its value in user prefs db.
    The prefs_key option can be True (meaning use the name as the key, after a hardcoded prefix),
    or a string (the actual prefs key).
       If non_debug option is true, pref is available even to users who don't set ATOM-DEBUG.
    """
    try:
        dp = debug_prefs[name]
    except KeyError:
        debug_prefs[name] = dp = DebugPref(name, dtype, **options)
    return dp.current_value()

class Pref: #e might be merged with the DataType (aka PrefDataType) objects
    "Pref objects record all you need to know about a currently active preference lvalue [with optional persistence as of 060124]"
    prefs_key = None
    print_changes = False
    non_debug = False # should this be True here and False in DebugPref subclass? decide when it matters.
    def __init__(self, name, dtype, prefs_key = False, non_debug = False): #bruce 060124 added prefs_key & non_debug options
        #e for now, name is used locally (for UI, etc, and maybe for prefs db);
        # whether/how to find this obj using name is up to the caller
        self.name = name
        assert name and type(name) == type("") #bruce 060124 added assert (don't know if this was already an implicit requirement)
        self.dtype = dtype # a DataType object
        self.value = dtype.default_value() # might be changed below
        if prefs_key: #bruce 060124 new feature
            if prefs_key is True:
                prefs_key = "_debug_pref_key:" + name #e should prefix depend on release-version??
            assert type(prefs_key) == type(""), "prefs_key must be True or a string"
            assert prefs_key # implied by the other asserts/ifs
            self.prefs_key = prefs_key
            self.value = env.prefs.get( prefs_key, self.value ) ###k guess about this being a fully ok way to store a default value
        if non_debug:
            self.non_debug = True # show up in debug_prefs submenu even when ATOM-DEBUG is not set
        return
    def current_value(self):
        #e should we look it up in env.prefs (for usage tracking) if self.prefs_key?? [no need to decide this until it matters]
        return self.value
    def changer_menuspec(self):
        """return a menu_spec suitable for including in some larger menu (as item or submenu is up to us)
        which permits this pref's value to be seen and/or changed;
        how to do this depends on datatype (#e and someday on other prefs!)
        """
        def newval_receiver_func(newval):
            assert self.dtype.legal_value(newval), "illegal value for %r: %r" % (self, newval)
                ###e change to ask dtype, since most of them won't have a list of values!!! this method is specific to Choice.
            if self.value == newval: #bruce 060126
                if self.print_changes:
                    print "redundant change:", 
                ##return??
            self.value = newval
            extra = ""
            if self.prefs_key:
                env.prefs[self.prefs_key] = newval
                extra = " (also in prefs db)"
            if self.print_changes:
                msg = "changed %r to %r%s" % (self, newval, extra)
                print msg
                msg = "changed %s to %r%s" % (self, newval, extra) # shorter version (uses %s) for history [bruce 060126]
                env.history.message(msg, quote_html = True, color = 'gray') #bruce 060126 new feature
        return self.dtype.changer_menuspec(self.name, newval_receiver_func, self.current_value())
    def __repr__(self):
        extra = ""
        if self.prefs_key:
            extra = " (prefs_key %r)" % self.prefs_key
        return "<Pref %r at %#x%s>" % (self.name, id(self), extra)
    def __str__(self):
        return "<Pref %r>" % (self.name,)
    pass

class DebugPref(Pref):
    print_changes = True
    pass

# == datatypes

class DataType:
    """abstract class for data types for preferences
    (subclasses are for specific kinds of data types;
     instances are for data types themselves,
     but are independent from a specific preference-setting
     that uses that datatype)
    (a DataType object might connote pref UI aspects, so it's not just
     about the data, but it's largely a datatype; nonetheless,
     consider renaming it to PrefDataType or so ###e)
    """
    #e some default method implems; more could be added
    ###e what did i want to put here??
    def changer_menu_text(self, instance_name, curval = None):
        """Return some default text for a menu meant to display and permit changes to a pref setting
        of this type and the given instance-name (of the pref variable) and current value.
        (API kluge: curval = None means curval not known, unless None's a legal value.
        Better to separate these into two args, perhaps optionally if that can be clean. #e)
        """
        if curval is None and not self.legal_value(curval): #####@@@@ use it in the similar-code place
            cvtext = ": ?" # I think this should never happen in the present calling code
        else:
            cvtext = ": %s" % self.short_name_of_value(curval)
        return "%s" % instance_name + cvtext
    def short_name_of_value(self, value):
        return self.name_of_value(value)
    def normalize_value(self, value):
        """most subclasses should override this; see comments in subclass methods;
        not yet decided whether it should be required to detect illegal values, and if so, what to do then;
        guess: most convenient to require nothing about calling it with illegal values; but not sure;
        ##e maybe split into public and raw forms, public has to detect illegals and raise ValueError (only).
        """
        return value # wrong for many subclasses, but not all (assuming value is legal)
    def legal_value(self, value):
        """Is value legal for this type? [Not sure whether this should include "after self.normalize_value" or not] """
        try:
            self.normalize_value(value) # might raise recursion error if that routine checks for value being legal! #e clean up
            return True # not always correct!
        except:
            # kluge, might hide bugs, but at least in this case (and no bugs)
            # we know we'd better not consider this value legal!
            return False
    pass

def autoname(thing):
    return `thing` # for now

class Choice(DataType): #e might be renamed ChoicePrefType, or renamed ChoicePref and merged with Pref class to include a prefname etc
    "DataType for a choice between one of a few specific values, perhaps with names and comments and order and default"
    def __init__(self, values = None, names = None, names_to_values = None, default_value = None):
        #e names_to_values should be a dict from names to values; do we union these inits or require no redundant ones? Let's union.
        if values is not None:
            values = list(values) #e need more ways to use the init options
        else:
            values = []
        if names is not None:
            assert len(names) <= len(values)
            names = list(names)
        else:
            names = []
        while len(names) < len(values):
            i = len(names) # first index whose value needs a name
            names.append( autoname(values[i]) )
        if names_to_values:
            items = names_to_values.items()
            items.sort()
            for name, value in items:
                names.append(name)
                values.append(value)
        self.names = names
        self.values = values
        #e nim: comments
        self._default_value = self.values[0] # might be changed below
        self.values_to_comments = {}
        self.values_to_names = {}
        for name, value in zip(self.names, self.values):
            self.values_to_names[value] = name
            if default_value == value: # even if it's None!
                self._default_value = value
    def name_of_value(self, value):
        return self.values_to_names[value]
    def default_value(self):
        return self._default_value
    def legal_value(self, value):
        """Is value legal for this type? [Not sure whether this should include "after self.normalize_value" or not] """
        return value in self.values
    def changer_menuspec( self, instance_name, newval_receiver_func, curval = None): # for Choice (aka ChoicePrefType)
        #e could have special case for self.values == [True, False] or the reverse
        text = self.changer_menu_text( instance_name, curval) # e.g. "instance_name: curval"
        submenu = submenu_from_name_value_pairs( zip(self.names, self.values), newval_receiver_func, curval = curval )
        #e could add some "dimmed info" and/or menu commands to the end of submenu
        return ( text, submenu )
    pass

Choice_boolean_False = Choice([False, True])
Choice_boolean_True =  Choice([False, True], default_value = True)

def submenu_from_name_value_pairs( nameval_pairs, newval_receiver_func, curval = None, mitem_value_func = None ):
    from debug import print_compact_traceback # do locally to avoid recursive import problem
    submenu = []
    for name, value in nameval_pairs:
        mitem = ( name,
                         lambda event = None, func = newval_receiver_func, val = value: func(val),
                         (curval == value) and 'checked' or None
                        )
        if mitem_value_func is not None:
            try:
                res = "<no retval yet>" # for error messages
                res = mitem_value_func(mitem, value)
                if res is None:
                    continue # let func tell us to skip this item ###k untested
                assert type(res) == type((1,2))
                mitem = res
            except:
                print_compact_traceback("exception in mitem_value_func, or error in retval (%r): " % (res,))
                    #e improve, and atom_debug only
                pass
        submenu.append(mitem)
    return submenu

class ColorType(DataType): #e might be renamed ColorPrefType or ColorPref
    """Pref Data Type for a color. We store all colors internally as a 3-tuple of floats
    (but assume ints in [0,255] are also enough -- perhaps that would be a better internal format #e).
    """
    #e should these classes all be named XxxPrefType or so? Subclasses might specialize in prefs-UI but not datatype per se...
    def __init__(self, default_value = None):
        if default_value is None:
            default_value = (0.5, 0.5, 0.5) # gray
        self._default_value = self.normalize_value( default_value)
    def normalize_value(self, value):
        """Turn any standard kind of color value into the kind we use internally -- a 3-tuple of floats from 0.0 to 1.0.
        Return the normalized value.
        If value is not legal, we might just return it or we might raise an exception.
        (Preferably ValueError, but for now this is NIM, it might be any exception, or none.)
        """
        #e support other python types for value? Let's support 3-seq of ints or floats, for now.
        # In future might want to support color name strings, QColor objects, ....
        r,g,b = value
        value = r,g,b # for error messages in assert
        assert type(r) == type(g) == type(b), \
               "color r,g,b components must all have same type (float or int), not like %r" % (value,)
        assert type(r) in (type(1), type(1.0)), "color r,g,b components must be float or int, not %r" % (value,)
        if type(r) == type(1):
            r = r/255.0 #e should check int range
            g = g/255.0
            b = b/255.0
        #e should check float range
        value = r,g,b # not redundant with above
        return value
    def name_of_value(self, value):
        return "Color(%0.3f, %0.3f, %0.3f)" # Color() is only used in this printform, nothing parses it (for now) #e could say RGB
    def short_name_of_value(self, value):
        return "%d,%d,%d" % self.value_as_int_tuple(value)
    def value_as_int_tuple(self, value):
        r,g,b = value # assume floats
        return tuple(map( lambda component: int(component * 255 + 0.5), (r,g,b) ))
    def value_as_QColor(self, value = None): ###k untested??
        #e API is getting a bit klugy... we're using a random instance as knowing about the superset of colors,
        # and using its default value as the value here...
        if value is None:
            value = self.default_value()
        rgb = self.value_as_int_tuple(value)
        from qt import QColor
        return QColor(rgb[0], rgb[1], rgb[2]) #k guess
    def default_value(self):
        return self._default_value
    def changer_menuspec( self, instance_name, newval_receiver_func, curval = None):
        # in the menu, we'd like to put up a few recent colors, and offer to choose a new one.
        # but in present architecture we have no access to any recent values! Probably this should be passed in.
        # For now, just use the curval and some common vals.
        text = self.changer_menu_text( instance_name, curval) # e.g. "instance_name: curval"
        values = [black, white, red, green, blue, gray, orange, yellow, magenta, pink] #e need better order, maybe submenus
            ##e self.recent_values()
            #e should be able to put color names in menu - maybe even translate numbers to those?
        values = map( self.normalize_value, values) # needed for comparison
        if curval not in values:
            values.insert(0, curval)
        names = map( self.short_name_of_value, values)
        # include the actual color in the menu item (in place of the checkmark-position; looks depressed when "checked")
        def mitem_value_func( mitem, value):
            "add options to mitem based on value and return new mitem"
            ###e should probably cache these things? Not sure... but it might be needed
            # (especially on Windows, based on Qt doc warnings)
            iconset = iconset_from_color( value)
                #e need to improve look of "active" icon in these iconsets (checkmark inside? black border?)
            return mitem + (('iconset',iconset),)
        submenu = submenu_from_name_value_pairs( zip(names, values),
                                                 newval_receiver_func,
                                                 curval = curval,
                                                 mitem_value_func = mitem_value_func )
        submenu.append(( "Choose...", pass_chosen_color_lambda( newval_receiver_func, curval ) ))
            #e need to record recent values somewhere, include some of them in the menu next time
        #k does that let you choose by name? If not, QColor has a method we could use to look up X windows color names.
        return ( text, submenu )
    pass

def pass_chosen_color_lambda( newval_receiver_func, curval, dialog_parent = None): #k I hope None is ok as parent
    def func():
        from qt import QColorDialog
        color = QColorDialog.getColor( qcolor_from_anything(curval), dialog_parent, "choose") #k what does "choose" mean?
        if color.isValid():
            newval = color.red()/255.0, color.green()/255.0, color.blue()/255.0
            newval_receiver_func(newval)
        return
    return func
        
def qcolor_from_anything(color):
    from qt import QColor
    if isinstance(color, QColor):
        return color
    if color is None:
        color = (0.5, 0.5, 0.5) # gray
    return ColorType(color).value_as_QColor() ###k untested call

def contrasting_color(qcolor, notwhite = False ):
    "return a QColor which contrasts with qcolor; if notwhite is true, it should also contrast with white."
    rgb = qcolor.red(), qcolor.green(), qcolor.blue() / 2 # blue is too dark, have to count it as closer to black
    from qt import Qt
    if max(rgb) > 90: # threshhold is a guess, mostly untested; even blue=153 seemed a bit too low so this is dubiously low.
        # it's far enough from black (I hope)
        return Qt.black
    if notwhite:
        return Qt.cyan
    return Qt.white
    
def pixmap_from_color_and_size(color, size):
    "#doc; size can be int or (int,int)"
    if type(size) == type(1):
        size = size, size
    w,h = size
    qcolor = qcolor_from_anything(color)
    from qt import QPixmap
    qp = QPixmap(w,h)
    qp.fill(qcolor)
    return qp

def iconset_from_color(color):
    """Return a QIconSet suitable for showing the given color in a menu item or (###k untested, unreviewed) some other widget.
    The color can be a QColor or any python type we use for colors (out of the few our helper funcs understand).
    """
    # figure out desired size of a small icon
    from qt import QIconSet
    size = QIconSet.iconSize(QIconSet.Small) # a QSize object
    w, h = size.width(), size.height()
    # get pixmap of that color
    pixmap = pixmap_from_color_and_size( color, (w,h) )
    # for now, let Qt figure out the Active appearance, etc. Later we can draw our own black outline, or so. ##e
    iconset = QIconSet(pixmap)
    checkmark = ("checkmark" == debug_pref("color checkmark", Choice(["checkmark","box"])))

    modify_iconset_On_states( iconset, color = color, checkmark = checkmark )
    return iconset

def modify_iconset_On_states( iconset, color = white, checkmark = False, use_color = None):
    #bruce 050729 split this out of iconset_from_color
    """Modify the On states of the pixmaps in iconset, so they can be distinguished from the (presumably equal) Off states.
    (Warning: for now, only the Normal On states are modified, not the Active or Disabled On states.)
    By default, the modification is to add a surrounding square outline whose color contrasts with white,
    *and* also with the specified color if one is provided. If checkmark is true, the modification is to add a central
    checkmark whose color contrasts with white, *or* with the specified color if one is provided.
    Exception to all that: if use_color is provided, it's used directly rather than any computed color.
    """
    from qt import QIconSet, QPixmap
    for size in [QIconSet.Small, QIconSet.Large]: # Small, Large = 1,2
        for mode in [QIconSet.Normal]: # Normal = 0; might also need Active for when mouse over item; don't yet need Disabled
            # make the On state have a checkmark; first cause it to generate both of them, and copy them both
            # (just a precaution so it doesn't make Off from the modified On,
            #  even though in my test it treats the one we passed it as Off --
            #  but I only tried asking for Off first)
##            for state in [QIconSet.Off, QIconSet.On]: # Off = 1, On = 0, apparently!
##                # some debug code that might be useful later:
##                ## pixmap = iconset.pixmap(size, mode, state) # it reuses the same pixmap for both small and large!!! how?
##                ## generated = iconset.isGenerated(size, mode, state) # only the size 1, state 1 (Small Off) says it's not generated
##                ## print "iconset pixmap for size %r, mode %r, state %r (generated? %r) is %r" % \
##                ##       (size, mode, state, generated, pixmap)
##                pixmap = iconset.pixmap(size, mode, state)
##                pixmap = QPixmap(pixmap) # copy it ###k this might not be working; and besides they might be copy-on-write
##                ## print pixmap # verify unique address
##                iconset.setPixmap(pixmap, size, mode, state)
            # now modify the On pixmap; assume we own it
            state = QIconSet.On
            pixmap = iconset.pixmap(size, mode, state)
            #e should use QPainter.drawPixmap or some other way to get a real checkmark and add it,
            # but for initial test this is easiest and will work: copy some of this color into middle of black.
            # Warning: "size" localvar is in use as a loop iterator!
            psize = pixmap.width(), pixmap.height() #k guess
            w,h = psize
##            import platform
##            if platform.atom_debug:
##                print "atom_debug: pixmap(%s,%s,%s) size == %d,%d" % (size, mode, state, w,h)
            from qt import copyBlt
            if checkmark:
                if use_color is None:
                    use_color = contrasting_color( qcolor_from_anything(color))
                pixmap2 = pixmap_from_color_and_size( use_color, psize)
                for x,y in [(-2,0),(-1,1),(0,2),(1,1),(2,0),(3,-1),(4,-2)]:
                    # this imitates Qt's checkmark on Mac; is there an official source?
                    # (it might be more portable to grab pixels from a widget or draw a QCheckListItem into a pixmap #e)
                    x1,y1 = x + w/2 - 1, y + h/2 - 1
                    copyBlt( pixmap, x1,y1, pixmap2, x1,y1, 1,3 )
                iconset.setPixmap(pixmap, size, mode, state) # test shows re-storing it is required (guess: copy on write)
            else:
                if use_color is None:
                    use_color = contrasting_color( qcolor_from_anything(color), notwhite = True)
                pixmap2 = pixmap_from_color_and_size( use_color, psize)
                    ###e needs to choose white if actual color is too dark (for a checkmark)
                    # or something diff than both black and white (for an outline, like we have now)
                copyBlt( pixmap2, 2,2, pixmap, 2,2, w-4, h-4 )
                    # args: dest, dx, dy, source, sx, sy, w,h. Doc hints that overwriting edges might crash.
                iconset.setPixmap(pixmap2, size, mode, state)
                # note: when I had a bug which made pixmap2 too small (size 1x1), copyBlt onto it didn't crash,
                # and setPixmap placed it into the middle of a white background.
            pass
        pass
    return # from modify_iconset_On_states

# ==

#bruce 060124 changes: always called, but gets passed platform.atom_debug as an arg to filter the prefs,
# and has new API to return a list of menu items (perhaps empty) rather than exactly one.

def debug_prefs_menuspec( atom_debug):
    """Return a list of zero or more menu items or submenus (as menu_spec tuples or lists)
    usable to see and edit settings of all active debug prefs (for atom_debug true)
    or all the ones that have their non_debug flag set (for atom_debug false).
    """
    import platform
    if platform.atom_debug: #bruce 050808 (it's ok that this is not the atom_debug argument)
        testcolor = debug_pref("atom_debug test color", ColorType(green))
    text = "debug prefs submenu"
    submenu = []
    items = debug_prefs.items()
    items.sort()
    for name, pref in items:
        if pref.non_debug or atom_debug:
            submenu.append( pref.changer_menuspec() )
    if submenu:
        return [ ( text, submenu) ]
    else:
        if atom_debug:
            return [ ( text, noop, "disabled" ) ]
        else:
            return []
    pass

# == test code

if __name__ == '__main__':
    spinsign = debug_pref("spinsign",Choice([1,-1]))
    testcolor = debug_pref("test color", ColorType(green))
    print debug_prefs_menuspec(True)
    
# end
