# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""
debug_prefs.py -- user-settable flags to help with debugging;
serves as a prototype of general first-class-preference-variables system.

Also contains some general color/icon/pixmap utilities which should be refiled.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

By Bruce, 050614
"""

from utilities.constants import noop
from utilities.constants import black, white, red, green, blue, gray, orange, yellow, magenta, pink

from utilities.Comparison import same_vals

    # note: qt4transition imports debug_pref from this module, which is one reason this module can't import
    # print_compact_traceback at toplevel. This should be fixed; it should be ok for this
    # module to import from debug. (There may be other reasons it can't in the current code.)
    # [bruce 070613 comment]

import foundation.env as env
# see below for "import preferences" at runtime; we can't import it here due to errors caused by recursive import

_NOT_PASSED = [] # private object for use as keyword arg default [bruce 070110, part of fixing bug of None as Choice value]
    # (note, the same global name is used for different objects in preferences.py and debug_prefs.py)

debug_prefs = {} # maps names of debug prefs to "pref objects"

def debug_pref(name, dtype, **options ): #bruce 070613 added call_with_new_value
    """
    Public function for declaring and registering a debug pref and querying its value.
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
       If call_with_new_value is passed (as a named argument -- no positional call is supported),
    and is not None, it will be called with the new value whenever the value is changed from the
    debug menu. It will NOT be called immediately with the current value, since some debug prefs
    are called extremely often, and since the caller can easily do this if desired. If this option
    was passed before (for the same debug_pref), the old function will be discarded and not called again.
       WARNING: the call_with_new_value function is only called for changes caused by use of the debug menu;
    it probably should also be called for prefs db changes done by other means, but that's not yet
    implemented. (It will be easy to add when it's needed.)
    """
    call_with_new_value = options.pop('call_with_new_value', None)
    try:
        dp = debug_prefs[name]
    except KeyError:
        debug_prefs[name] = dp = DebugPref(name, dtype, **options)
    dp.set_call_with_new_value_function(call_with_new_value)
    return dp.current_value()

def debug_pref_object(name): #bruce 060213 experiment
    # might be useful for adding subscribers, but, this implem has error
    # if no one called debug_pref on name yet!
    # basic logic of scheme for this needs revision.
    return debug_prefs[name]

class Pref:
    # might be merged with the DataType (aka PrefDataType) objects;
    # only used in DebugPref as of long before 080215
    """
    Pref objects record all you need to know about a currently active
    preference lvalue [with optional persistence as of 060124]
    """
    # class constants or instance variable initial values (some might be overridden in subclasses)
    prefs_key = None
    print_changes = False
    non_debug = False # should this be True here and False in DebugPref subclass? decide when it matters.
    classname_for_repr = 'Pref' #bruce 070430
##    starts_out_from_where = "from prefs db"
    def __init__(self, name, dtype, prefs_key = False, non_debug = False, subs = ()): #bruce 060124 added prefs_key & non_debug options
        #e for now, name is used locally (for UI, etc, and maybe for prefs db);
        # whether/how to find this obj using name is up to the caller
        self.name = name
        assert name and type(name) == type("") #bruce 060124 added assert (don't know if this was already an implicit requirement)
        self.dtype = dtype # a DataType object
        self.value = self._dfltval = dtype.get_defaultValue() # might be changed below  #bruce 070228 added self._dfltval
        if prefs_key: #bruce 060124 new feature
            if prefs_key is True:
                prefs_key = "_debug_pref_key:" + name #e should prefix depend on release-version??
            assert type(prefs_key) == type(""), "prefs_key must be True or a string"
            assert prefs_key # implied by the other asserts/ifs
            self.prefs_key = prefs_key
            import foundation.preferences as preferences # make sure env.prefs is initialized [bruce 070110 precaution]
                # (evidently ok this early, but not sure if needed -- it didn't fix the bug in a Choice of None I commented on today)
            self.value = env.prefs.get( prefs_key, self.value ) ###k guess about this being a fully ok way to store a default value
                # Note: until I fixed preferences.py today, this failed to store a default value when self.value was None. [bruce 070110]
            # note: in this case, self.value might not matter after this, but in case it does we keep it in sync before using it,
            # or use it only via self.current_value() [bruce 060209 bugfix]
            if self.print_changes and not same_vals(self.value, self._dfltval): #bruce 070228 new feature for debug_pref
                # note: we use same_vals to avoid bugs in case of tuples or lists of Numeric arrays.
                # note: this only does printing of initial value being non-default;
                # printing of changes by user is done elsewhere, and presently goes
                # to both history widget and console print. We'll follow the same policy
                # here -- but if it's too early to print to history widget, env.history
                # will print to console, and we don't want it to get printed there twice,
                # so we check for that before printing it to console ourselves. [bruce 071018]
                msg = "Note: %s (default %r) starts out %r" % \
                      (self, self._dfltval, self.value) ## + " %s" % self.starts_out_from_where
                if not getattr(env.history, 'too_early', False):
                    print msg
                env.history.message(msg, quote_html = True, color = 'orange')
            pass
        self.non_debug = non_debug # show up in debug_prefs submenu even when ATOM-DEBUG is not set?
        self.subscribers = [] # note: these are only called for value changes due to debug menu
        for sub in subs:
            self.subscribe_to_changes(sub)
        self.subscribe_to_changes( self._fulfill_call_with_new_value )
            # note: creates reference cycle (harmless, since we're never destroyed)
        return
    __call_with_new_value_function = None
    def set_call_with_new_value_function(self, func):
        """
        Save func as our new "call with new value" function. If not None,
        it will be called whenever our value changes due to use of the debug menu.
        (In the future we may extend this to also call it if the value changes by other means.)
        It will be discarded if this method is called again (to set a new such function or None).
        """
        self.__call_with_new_value_function = func
        ## don't do this: self._fulfill_call_with_new_value()
        return
    def _fulfill_call_with_new_value(self):
        from utilities.debug import print_compact_traceback # do locally to avoid recursive import problem
        func = self.__call_with_new_value_function
        if func is not None:
            val = self.current_value()
            try:
                func(val)
            except:
                print_compact_traceback("exception ignored in %s's call_with_new_value function (%r): " % (self, func) )
                # (but don't remove func, even though this print might be verbose)
                # Note: if there are bugs where func becomes invalid after a relatively rare change
                # (like after a new file is loaded), we might need to make this a history error and make it non-verbose.
            pass
        return
    def subscribe_to_changes(self, func): #bruce 060216, untested, maybe not yet called, but intended to remain as a feature ###@@@
        """
        Call func with no arguments after every change to our value from the debug menu,
        until func() first returns true or raises an exception (for which we'll print a traceback).
           Note: Doesn't detect independent changes to env.prefs[prefs_key] -- for that, suggest using
        env.pref's subscription system instead.
        """
        self.subscribers.append(func)
    def unsubscribe(self, func):
        self.subscribers.remove(func) # error if not subscribed now
    def current_value(self):
        if self.prefs_key:
            # we have to look it up in env.prefs instead of relying on self.value,
            # in case it was independently changed in prefs db by other code [bruce 060209 bugfix]
            # (might also help with usage tracking)
            self.value = env.prefs[self.prefs_key] #k probably we could just return this and ignore self.value in this case
        return self.value
    def current_value_is_not_default(self): #bruce 080312
        return not same_vals( self.current_value(), self._dfltval)
    def changer_menuspec(self):
        """
        Return a menu_spec suitable for including in some larger menu (as item or submenu is up to us)
        which permits this pref's value to be seen and/or changed;
        how to do this depends on datatype (#e and someday on other prefs!)
        """
        def newval_receiver_func(newval):
            from utilities.debug import print_compact_traceback # do locally to avoid recursive import problem
            assert self.dtype.legal_value(newval), "illegal value for %r: %r" % (self, newval)
                ###e change to ask dtype, since most of them won't have a list of values!!! this method is specific to Choice.
            if self.current_value() == newval: #bruce 060126; revised 060209 to use self.current_value() rather than self.value
                if self.print_changes:
                    print "redundant change:",
                ##return??
            self.value = newval
            extra = ""
            if self.prefs_key:
                env.prefs[self.prefs_key] = newval
                # note: when value is looked up, this is the assignment that counts (it overrides self.value) [as of 060209 bugfix]
                extra = " (also in prefs db)"
            if self.print_changes:
                ## msg = "changed %r to %r%s" % (self, newval, extra)
                msg = "changed %s to %r%s" % (self, newval, extra) # shorter version for console too [bruce 080215]
                print msg
                msg = "changed %s to %r%s" % (self, newval, extra) # shorter version (uses %s) for history [bruce 060126]
                env.history.message(msg, quote_html = True, color = 'gray') #bruce 060126 new feature
            for sub in self.subscribers[:]:
                #bruce 060213 new feature; as of 070613 this also supports the call_with_new_value feature
                from utilities.debug import print_compact_traceback # do locally to avoid recursive import problem
                try:
                    unsub = sub()
                except:
                    print_compact_traceback("exception ignored in some subscriber to changes to %s: " % self)
                    unsub = 1
                if unsub:
                    self.subscribers.remove(sub) # should work properly even if sub is present more than once
                continue
            return # from newval_receiver_func
        return self.dtype.changer_menuspec(self.name, newval_receiver_func, self.current_value())
    def __repr__(self):
        extra = ""
        if self.prefs_key:
            extra = " (prefs_key %r)" % self.prefs_key
        return "<%s %r at %#x%s>" % (self.classname_for_repr, self.name, id(self), extra)
    def __str__(self):
        return "<%s %r>" % (self.classname_for_repr, self.name,)
    pass

# ==

class DebugPref(Pref):
    classname_for_repr = 'debug_pref' #bruce 070430, for clearer History messages
    print_changes = True
##    starts_out_from_where = "(from debug prefs submenu)"
    pass

# == datatypes

class DataType:
    """
    abstract class for data types for preferences
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
        """
        Return some default text for a menu meant to display and permit changes to a pref setting
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
        """
        most subclasses should override this; see comments in subclass methods;
        not yet decided whether it should be required to detect illegal values, and if so, what to do then;
        guess: most convenient to require nothing about calling it with illegal values; but not sure;
        ##e maybe split into public and raw forms, public has to detect illegals and raise ValueError (only).
        """
        return value # wrong for many subclasses, but not all (assuming value is legal)
    def legal_value(self, value):
        """
        Is value legal for this type? [Not sure whether this should include "after self.normalize_value" or not]
        """
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

class Choice(DataType):
    #e might be renamed ChoicePrefType, or renamed ChoicePref and merged
    # with Pref class to include a prefname etc
    """
    DataType for a choice between one of a few specific values,
    perhaps with names and comments and order and default.
    """
    # WARNING: before 070110, there was a bug if None was used as one of the choices, but it should be ok now,
    # except that the "API kluge: curval = None means curval not known, unless None's a legal value"
    # in docstring of self.changer_menu_text has not been reviewed regarding this. ###e [bruce 070110 comment]
    def __init__(self, values = None, names = None, names_to_values = None, defaultValue = _NOT_PASSED):
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
        self._defaultValue = self.values[0] # might be changed below
        self.values_to_comments = {}
        self.values_to_names = {}
        for name, value in zip(self.names, self.values):
            self.values_to_names[value] = name
            if defaultValue is not _NOT_PASSED and defaultValue == value: # even if defaultValue is None!
                # There used to be a bug when None was a legal value but no defaultValue was passed,
                # in which this code would change self._defaultValue to None. I fixed that bug using _NOT_PASSED.
                # This is one of two changes which makes None acceptable as a Choice value.
                # The other is in preferences.py dated today. [bruce 070110]
                self._defaultValue = value
    def name_of_value(self, value):
        return self.values_to_names[value]
    def get_defaultValue(self):
        # WARNING [can be removed soon if nothing goes wrong]:
        # When I renamed this to make it consistent in capitalization
        # with similar attributes, I also renamed it to be clearly a get method,
        # since in most code this name is used for a public attribute instead.
        # AFAIK it has only two defs and two calls, all in this file. [bruce 070831]
        return self._defaultValue
    def legal_value(self, value):
        """
        Is value legal for this type?
        [Not sure whether this should include "after self.normalize_value" or not]
        """
        return value in self.values
    def changer_menuspec( self, instance_name, newval_receiver_func, curval = None): # for Choice (aka ChoicePrefType)
        #e could have special case for self.values == [True, False] or the reverse
        text = self.changer_menu_text( instance_name, curval) # e.g. "instance_name: curval"
        submenu = submenu_from_name_value_pairs( zip(self.names, self.values),
                                                 newval_receiver_func,
                                                 curval = curval,
                                                 indicate_defaultValue = True, #bruce 070518 new feature
                                                 defaultValue = self._defaultValue
                                                )
        #e could add some "dimmed info" and/or menu commands to the end of submenu

        #e could use checkmark to indicate non_default = not same_vals(self._defaultValue, curval),
        # but too confusing if _defaultValue is True and curval is False...
        # so nevermind unless I figure out a nonfusing indication of that
        # that is visible outside the list of values submenu
        # and doesn't take too much room.
        # Maybe appending a very short string to the text, in changer_menu_text?
        # [bruce 080312 comment]
        return ( text, submenu )
    pass

Choice_boolean_False = Choice([False, True])
Choice_boolean_True =  Choice([False, True], defaultValue = True)

def submenu_from_name_value_pairs( nameval_pairs,
                                   newval_receiver_func,
                                   curval = None,
                                   mitem_value_func = None,
                                   indicate_defaultValue = False,
                                   defaultValue = None
                                   ):
    #bruce 080312 revised to use same_vals (2 places)
    from utilities.debug import print_compact_traceback # do locally to avoid recursive import problem
    submenu = []
    for name, value in nameval_pairs:
        text = name
        if indicate_defaultValue and same_vals(value, defaultValue):
            #bruce 070518 new feature
            text += " (default)"
        command = ( lambda ## event = None,
                           func = newval_receiver_func,
                           val = value :
                        func(val) )
        mitem = ( text,
                  command,
                  same_vals(curval, value) and 'checked' or None
                )
        if mitem_value_func is not None:
            try:
                res = "<no retval yet>" # for error messages
                res = mitem_value_func(mitem, value)
                if res is None:
                    continue # let func tell us to skip this item ###k untested
                assert type(res) == type((1, 2))
                mitem = res
            except:
                print_compact_traceback("exception in mitem_value_func, or error in retval (%r): " % (res,))
                    #e improve, and atom_debug only
                pass
        submenu.append(mitem)
    return submenu

class ColorType(DataType): #e might be renamed ColorPrefType or ColorPref
    """
    Pref Data Type for a color. We store all colors internally as a 3-tuple of floats
    (but assume ints in [0,255] are also enough -- perhaps that would be a better internal format #e).
    """
    #e should these classes all be named XxxPrefType or so? Subclasses might specialize in prefs-UI but not datatype per se...
    def __init__(self, defaultValue = None):
        if defaultValue is None:
            defaultValue = (0.5, 0.5, 0.5) # gray
        self._defaultValue = self.normalize_value( defaultValue)
    def normalize_value(self, value):
        """
        Turn any standard kind of color value into the kind we use internally -- a 3-tuple of floats from 0.0 to 1.0.
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
        r, g, b = value # assume floats
        return tuple(map( lambda component: int(component * 255 + 0.5), (r, g, b) ))
    def value_as_QColor(self, value = None): ###k untested??
        #e API is getting a bit klugy... we're using a random instance as knowing about the superset of colors,
        # and using its default value as the value here...
        if value is None:
            value = self.get_defaultValue()
        rgb = self.value_as_int_tuple(value)
        from PyQt4.Qt import QColor
        return QColor(rgb[0], rgb[1], rgb[2]) #k guess
    def get_defaultValue(self):
        return self._defaultValue
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
            """
            add options to mitem based on value and return new mitem
            """
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
        from PyQt4.Qt import QColorDialog
        color = QColorDialog.getColor( qcolor_from_anything(curval), dialog_parent)
        if color.isValid():
            newval = color.red()/255.0, color.green()/255.0, color.blue()/255.0
            newval_receiver_func(newval)
        return
    return func

def qcolor_from_anything(color):
    from PyQt4.Qt import QColor
    if isinstance(color, QColor):
        return color
    if color is None:
        color = (0.5, 0.5, 0.5) # gray
    return ColorType(color).value_as_QColor() ###k untested call

def contrasting_color(qcolor, notwhite = False ):
    """
    return a QColor which contrasts with qcolor;
    if notwhite is true, it should also contrast with white.
    """
    rgb = qcolor.red(), qcolor.green(), qcolor.blue() / 2 # blue is too dark, have to count it as closer to black
    from PyQt4.Qt import Qt
    if max(rgb) > 90: # threshhold is a guess, mostly untested; even blue=153 seemed a bit too low so this is dubiously low.
        # it's far enough from black (I hope)
        return Qt.black
    if notwhite:
        return Qt.cyan
    return Qt.white

def pixmap_from_color_and_size(color, size):
    """
    #doc; size can be int or (int,int)
    """
    if type(size) == type(1):
        size = size, size
    w,h = size
    qcolor = qcolor_from_anything(color)
    from PyQt4.Qt import QPixmap
    qp = QPixmap(w,h)
    qp.fill(qcolor)
    return qp

def iconset_from_color(color):
    """
    Return a QIcon suitable for showing the given color in a menu item or (###k untested, unreviewed) some other widget.
    The color can be a QColor or any python type we use for colors (out of the few our helper funcs understand).
    """
    # figure out desired size of a small icon
    from PyQt4.Qt import QIcon
    #size = QIcon.iconSize(QIcon.Small) # a QSize object
    #w, h = size.width(), size.height()
    w, h = 16, 16   # hardwire it and be done
    # get pixmap of that color
    pixmap = pixmap_from_color_and_size( color, (w,h) )
    # for now, let Qt figure out the Active appearance, etc. Later we can draw our own black outline, or so. ##e
    iconset = QIcon(pixmap)
    checkmark = ("checkmark" == debug_pref("color checkmark", Choice(["checkmark","box"])))

    modify_iconset_On_states( iconset, color = color, checkmark = checkmark )
    return iconset

def modify_iconset_On_states( iconset, color = white, checkmark = False, use_color = None):
    #bruce 050729 split this out of iconset_from_color
    """
    Modify the On states of the pixmaps in iconset, so they can be distinguished from the (presumably equal) Off states.
    (Warning: for now, only the Normal On states are modified, not the Active or Disabled On states.)
    By default, the modification is to add a surrounding square outline whose color contrasts with white,
    *and* also with the specified color if one is provided. If checkmark is true, the modification is to add a central
    checkmark whose color contrasts with white, *or* with the specified color if one is provided.
    Exception to all that: if use_color is provided, it's used directly rather than any computed color.
    """
    from PyQt4.Qt import QIcon, QPixmap
    if True:
        ## print 'in debug_prefs.modify_iconset_On_states : implement modify_iconset_On_states for Qt 4'
        return
    for size in [QIcon.Small, QIcon.Large]: # Small, Large = 1,2
        for mode in [QIcon.Normal]: # Normal = 0; might also need Active for when mouse over item; don't yet need Disabled
            # make the On state have a checkmark; first cause it to generate both of them, and copy them both
            # (just a precaution so it doesn't make Off from the modified On,
            #  even though in my test it treats the one we passed it as Off --
            #  but I only tried asking for Off first)
##            for state in [QIcon.Off, QIcon.On]: # Off = 1, On = 0, apparently!
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
            state = QIcon.On
            pixmap = iconset.pixmap(size, mode, state)
            #e should use QPainter.drawPixmap or some other way to get a real checkmark and add it,
            # but for initial test this is easiest and will work: copy some of this color into middle of black.
            # Warning: "size" localvar is in use as a loop iterator!
            psize = pixmap.width(), pixmap.height() #k guess
            w,h = psize
##            from utilities import debug_flags
##            if debug_flags.atom_debug:
##                print "atom_debug: pixmap(%s,%s,%s) size == %d,%d" % (size, mode, state, w,h)
            from PyQt4.Qt import copyBlt
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

#bruce 060124 changes: always called, but gets passed debug_flags.atom_debug as an arg to filter the prefs,
# and has new API to return a list of menu items (perhaps empty) rather than exactly one.

from utilities import debug_flags

def debug_prefs_menuspec( atom_debug): #bruce 080312 split this up
    """
    Return the debug_prefs section for the debug menu, as a list of zero or more
    menu items or submenus (as menu_spec tuples or lists).
    """

    # first exercise all our own debug_prefs, then get the sorted list
    # of all known ones.

    if debug_flags.atom_debug: #bruce 050808 (it's ok that this is not the atom_debug argument)
        testcolor = debug_pref("atom_debug test color", ColorType(green))

    max_menu_length = debug_pref(
        "(max debug prefs submenu length?)", #bruce 080215
             # initial paren or space puts it at start of menu
         Choice([10, 20, 30, 40, 50, 60, 70], defaultValue = 20),
             #bruce 080317 changed default from 40 to 20, and revised order
         non_debug = True, #bruce 080317
         prefs_key = "A10/max debug prefs submenu length" # revised, bruce 080317
     )

    non_default_submenu = True # could be enabled by its own debug_pref if desired

    items = [(name.lower(), name, pref) for name, pref in debug_prefs.items()]
        # use name.lower() as sortkey, in this function and some of the subfunctions;
        # name is included to disambiguate cases where sortkey is identical
    items.sort()

    # then let each subsection process this in its own way.

    if non_default_submenu:
        part1 = _non_default_debug_prefs_menuspec( items )
    else:
        part1 = []

    part2 = _main_debug_prefs_menuspec( items, max_menu_length, atom_debug)

    return part1 + part2

def _non_default_debug_prefs_menuspec( items): #bruce 080312 added this
    """
    [private helper for debug_prefs_menuspec]

    Return a submenu for the debug_prefs currently set to a non-default value,
    if there are any. Items have a private format coming from our caller.
    """
    non_default_items = [item for item in items if item[-1].current_value_is_not_default()]
    if not non_default_items:
        return []
    submenu = [pref.changer_menuspec() for (sortkey_junk, name_junk, pref) in non_default_items]
    text = "debug prefs currently set (%d)" % len(submenu)
    return [ (text, submenu) ]

def _main_debug_prefs_menuspec( items, max_menu_length, atom_debug):
    """
    [private helper for debug_prefs_menuspec]

    Return a list of zero or more menu items or submenus (as menu_spec tuples or lists)
    usable to see and edit settings of all active debug prefs (for atom_debug true)
    or all the ones that have their non_debug flag set (for atom_debug false).

    Items have a private format coming from our caller.
    """
    items_wanted = []
        # will become a list of (sortkey, menuspec) pairs
    for sortkey, name_junk, pref in items:
        if pref.non_debug or atom_debug:
            items_wanted.append( (sortkey, pref.changer_menuspec()) )
                # note: sortkey is not used below for sorting (that
                # happened in caller), but is used for determining ranges.
        # print name_junk, to see the list for determining good ranges below
    if not items_wanted:
        if atom_debug:
            return [ ( "debug prefs submenu", noop, "disabled" ) ]
        else:
            return []
    elif len(items_wanted) <= max_menu_length:
        submenu = [menuspec for sortkey, menuspec in items_wanted]
        return [ ( "debug prefs submenu", submenu) ]
    else:
        # split the menu into smaller sections;
        # use the first splitting scheme of the following which works
        # (or the last one even if it doesn't work)
        schemes = [
            # these ranges were made by evenly splitting 62 debug prefs
            # (there are a lot each of d, e, g, u, and a bunch each of c, m, p, t)
            ("a-e", "f-z"),
            ("a-d", "e-j", "k-z"),
            ("a-c", "d-e", "f-m", "n-z")
         ]
        best_so_far = None
        for scheme in schemes:
            # split according to scheme, then stop if it's good enough
            pointer = 0
            res = []
            good_enough = True # set to False if any submenu is still too long
            total = 0 # count items, for an assert
            for range in scheme:
                # grab the remaining ones up to the end of this range
                one_submenu = []
                while (pointer < len(items_wanted) and
                       (range == scheme[-1] or
                        items_wanted[pointer][0][0] <= range[-1])):
                    menuspec = items_wanted[pointer][1]
                    pointer += 1
                    one_submenu.append( menuspec )
                # and put them into a submenu labelled with the range
                good_enough = good_enough and len(one_submenu) <= max_menu_length
                total += len(one_submenu)
                res.append( ("debug prefs (%s)" % range, one_submenu) )
                    # (even if one_submenu is empty)
                continue # next range
            assert total == len(items_wanted)
            assert len(res) == len(scheme) # revise if we drop empty ones
            best_so_far = res
            if good_enough:
                break
            continue
        # good enough, or as good as we can get
        assert best_so_far
        return best_so_far
    pass

# ==

# specific debug_pref exerciser/access functions can go here,
# if they need to be imported early during startup or by several source files
# [this location is deprecated -- use GlobalPreferences.py instead. --bruce 080215]

def _permit_property_pane():
    """
    should we set up this session to look a bit worse,
    but permit experimental property pane code to be used?
    """
    return debug_pref("property pane debug pref offered? (next session)",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = "A8 devel/permit property pane")

_this_session_permit_property_pane = 'unknown' # too early to evaluate _permit_property_pane() during this import

def this_session_permit_property_pane():
    """
    this has to give the same answer throughout one session
    """
    global _this_session_permit_property_pane
    if _this_session_permit_property_pane == 'unknown':
        _this_session_permit_property_pane = _permit_property_pane()
        if _this_session_permit_property_pane:
            _use_property_pane() # get it into the menu right away, otherwise we can't change it until it's too late
    return _this_session_permit_property_pane

def _use_property_pane():
    return debug_pref("property pane (for HJ dialog)?", Choice_boolean_False, non_debug = True,
                      prefs_key = "A8 devel/use property pane")

def use_property_pane():
    """
    should we actually use a property pane?
    (only works if set before the first time a participating dialog is used)
    (only offered in debug menu if a property pane is permitted this session)
    """
    return this_session_permit_property_pane() and _use_property_pane()

def debug_pref_History_print_every_selected_object(): #bruce 070504
    res = debug_pref("History: print every selected object?",
                      Choice_boolean_False,
                      non_debug = True,
                      prefs_key = "A9/History/print every selected object?"
                     )
    return res

# == test code

if __name__ == '__main__':
    spinsign = debug_pref("spinsign",Choice([1,-1]))
    testcolor = debug_pref("test color", ColorType(green))
    print debug_prefs_menuspec(True)

# end
