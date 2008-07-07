# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
prefs_widgets.py -- Utilities related to both user preferences and Qt widgets.
Note: also includes some code related to "connect with state"
which should be refiled.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 050805 started this module.

Module classification, and refactoring needed:

Needs splitting into at least two files. One of them is some widgets
or widget helpers. The other is some "connect with state" facilities.
Those might be used for pure model state someday (with at least some
of them getting classified in foundation and used in model), but for now,
they are probably only used with widgets, so we might get away with
calling this a "ui/widgets" module without splitting it -- we'll see.
[bruce 071215 comment]
"""

import foundation.env as env # for env.prefs
from utilities.debug import print_compact_traceback

from foundation.changes import Formula
from widgets.widget_helpers import RGBf_to_QColor
from PyQt4.Qt import QColorDialog
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPalette

from foundation.undo_manager import wrap_callable_for_undo

# public helper functions

# [this comment is probably obs:] ### colorframe prefs are UNTESTED since local old funcs rewritten to use these

def widget_destroyConnectionWithState(widget):
    """
    """
    conn = getattr(widget, '_ConnectionWithState__stored_connection', None)
        # warning: this is *not* name-mangled, since we're not inside a class. ### RENAME ATTR
    if conn is not None:
        # TODO: maybe assert it's of the expected class? or follows some api?
        conn.destroy() # this removes any subscriptions that object held
    widget._ConnectionWithState__stored_connection = None
    return

def widget_setConnectionWithState( widget, connection):
    """
    """
    assert getattr(widget, '_ConnectionWithState__stored_connection', None) is None, \
           "you must call widget_destroyConnectionWithState before making new connection on %r" % (widget,)
    widget._ConnectionWithState__stored_connection = connection
    ### TODO: arrange to destroy connection whenever widget gets destroyed.
    # Probably not needed except for widgets that get destroyed long before the app exits;
    # probably will be needed if we have any like that.
    return

def widget_connectWithState(widget, state, connection_class, **options):
    """
    Connect the given widget with the given state, using the given
    connection_class, which must be chosen to be correct for both
    the widget type and the state type / value format.
    
    @param widget: a QWidget of an appropriate type, or anything
                   which works with the given connection_class.
    @type widget: QWidget (usually).
    
    @param state: bla
    @type state: bla
    
    @param connection_class: the constructor for the connection. Must be correct for
                             both the widget type and state type / value format.
    @type connection_class: bla

    @param options: arbitrary options for connection_class.
    @type options: options dict, passed using **
    """
    widget_destroyConnectionWithState( widget)
    conn = connection_class( widget, state, **options)
    widget_setConnectionWithState( widget, conn)
    return

def widget_setAction(widget, aCallable, connection_class, **options):
    """
    """
    # kluge: use widget_connectWithState as a helper function,
    # since no widgets need both and the behavior is identical.
    # (If we add a type assertion to that func, we'll have to pass in
    # an alternative one here.)
    #
    # Assume the connection_class is responsible for turning aCallable
    # into the right form, applying options, etc (even if that ends up
    # meaning all connection_classes share common code in a superclass).
    widget_connectWithState(widget, aCallable, connection_class, **options)
    return

def set_metainfo_from_stateref( setter, stateref, attr, debug_metainfo = False):
    """
    If stateref provides a value for attr (a stateref-metainfo attribute
    such as 'defaultValue' or 'minimum'), pass it to the given setter function.
    If debug_metainfo is true, print debug info saying what we do and why.
    """
    if hasattr(stateref, attr):
        value = getattr( stateref, attr)
        if debug_metainfo:
            print "debug_metainfo: using %r.%s = %r" % (stateref, attr, value)
        setter(value)
    else:
        if debug_metainfo:
            print "debug_metainfo: %r has no value for %r" % (stateref, attr)
    return

# ==

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

def connect_colorpref_to_colorframe( prefs_key, colorframe ): #bruce 050805; revised 070425/070430 in Qt4 branch
    """
    Cause the bgcolor of the given Qt "color frame" to be set to
    each new legal color value stored in the given pref.
    """
    # first destroy any prior connection trying to control the same colorframe widget
    widget_destroyConnectionWithState( colorframe)
    
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
    
    conn = Formula( lambda: env.prefs.get( prefs_key) , colorframe_bgcolor_setter )
        # this calls the setter now and whenever the lambda-value changes, until it's destroyed
        # or until there's any exception in either arg that it calls.
    
    widget_setConnectionWithState( colorframe, conn)
    return

class destroyable_Qt_connection:
    """
    holds a Qt signal/slot connection, but has a destroy method which
    disconnects it [#e no way to remain alive but discon/con it]
    """
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
    """
    hold 0 or more objects, so that when we're destroyed, so are they
    """
    def __init__(self, *objs):
        self.objs = objs
    def destroy(self):
        for obj in self.objs:
            #e could let obj be a list and do this recursively
            obj.destroy()
        self.objs = None # error to destroy self again (if that's bad, set this to [] instead)
    pass

def connect_checkbox_with_boolean_pref_OLD( qcheckbox, prefs_key ): #bruce 050810, slightly revised 070814, DEPRECATED since being replaced
    """
    Cause the checkbox to track the value of the given boolean preference,
    and cause changes to the checkbox to change the preference.
    (Use of the word "with" in the function name, rather than "to" or "from",
     is meant to indicate that this connection is two-way.)
    First remove any prior connection of the same type on the same checkbox.
    Legal for more than one checkbox to track and control the same pref [but that might be untested].
    """
    # first destroy any prior connection trying to control the same thing
    widget_destroyConnectionWithState( qcheckbox)
    
    # make a one-way connection from prefs value to checkbox, using Formula (active as soon as made)
    setter = qcheckbox.setChecked #e or we might prefer a setter which wraps this with .blockSignals(True)/(False)
    conn1 = Formula( lambda: env.prefs.get( prefs_key) , setter )
        # this calls the setter now and whenever the lambda-value changes, until it's destroyed
        # or until there's any exception in either arg that it calls.

    # make a one-way connection from Qt checkbox to preference (active as soon as made)
    def prefsetter(val):
        #e should we assert val is boolean? nah, just coerce it:
        val = not not val
        env.prefs[prefs_key] = val
    conn2 = destroyable_Qt_connection( qcheckbox, SIGNAL("toggled(bool)"), prefsetter )
    
    # package up both connections as a single destroyable object, and store it
    conn = list_of_destroyables( conn1, conn2)
    widget_setConnectionWithState(qcheckbox, conn)
    return

class StateRef_API: ### TODO: FILL THIS IN, rename some methods
    """
    API for references to tracked state.
    """
    debug_name = ""
    
    # TODO: add support for queryable metainfo about type, whatsthis text, etc.
    # For example:
    # - self.defaultValue could be the default value (a constant value,
    #   not an expr, though in a *type* it might be an expr),
    #   and maybe some flag tells whether it's really known or just guessed.
    
    # TODO: add default implems of methods like set_value and get_value
    # (which raise NIM exceptions). But rename them as mentioned elsewhere
    pass

class Preferences_StateRef(StateRef_API): # note: compare to exprs.staterefs.PrefsKey_StateRef.
    """
    A state-reference object (conforming to StateRef_API),
    which represents the preferences value slot with the prefs_key
    and default value passed to our constructor.
       WARNING [071002]: this is not yet able to ask env.prefs for separately
    defined default values (in the table in preferences.py). For now,
    it is just for testing purposes when various kinds of staterefs
    should be tested, and should be used with newly made-up prefs keys.
    """
    def __init__(self, prefs_key, defaultValue = None, debug_name = "", pref_name = ""):
        # TODO: also let a value-filter function be passed, for type checking/fixing.
        self.prefs_key = prefs_key
        self.defaultValue = defaultValue
        if defaultValue is not None:
            env.prefs.get(prefs_key, defaultValue) # set or check the default value
            # REVIEW: need to disambiguate, if None could be a legitimate default value -- pass _UNSET_ instead?
            # REVIEW: IIRC, env.prefs provides a way to ask for the centrally defined or already initialized
            # default value. We should use that here if defaultValue is not provided, and set self.defaultValue
            # to it, or verify consistency if both are provided (maybe the env.prefs.get call does that already).
        if not debug_name:
            debug_name = "Preferences_StateRef(%r)" % (pref_name or prefs_key,)
                # this format is also important for __repr__
        self.debug_name = debug_name
        return
    def __repr__(self): #bruce 071002
        # assume self.debug_name includes class name,
        # as it does when made up by our own __init__ method
        assert self.debug_name.startswith(self.__class__.__name__)
            # if fails, might be legit, but we'll need to revise this code
        return "<%s at %#x>" % (self.debug_name, id(self))
    def set_value(self, value):
        # REVIEW: how can the caller tell that this is change-tracked?
        # Should StateRef_API define flags for client code queries about that?
        # e.g. self.tracked = true if set and get are fully tracked, false if not --
        # I'm not sure if this can differ for set and get, or if so, if that difference
        # matters to clients.
        env.prefs[self.prefs_key] = value
    def get_value(self):
        # REVIEW: how can the caller tell that this is usage-tracked?
        # (see also the related comment for set_value)
        return env.prefs[self.prefs_key]
    pass

def Preferences_StateRef_double( prefs_key, defaultValue = 0.0):
    # TODO: store metainfo about type, min, max, etc.
    return Preferences_StateRef( prefs_key, defaultValue)


def ObjAttr_StateRef( obj, attr, *moreattrs): #bruce 070815 experimental; plan: use it with connectWithState for mode tracked attrs
    ###e refile -- staterefs.py? StateRef_API.py? a staterefs package?
    """
    Return a reference to tracked state obj.attr, as a StateRef_API-conforming object
    of an appropriate class, chosen based on obj's class and how obj stores its state.
    """
    if moreattrs:
        assert 0, "a serial chain of attrs is not yet supported"
        ## ref1 = ObjAttr_StateRef( obj, attr)
        ## return ObjAttr_StateRef( ref1, *moreattrs) ### WRONG -- ref1 is a ref, not an obj which is its value!
    
    assert obj is not None #k might be redundant with checks below

    # Let's ask obj to do this. If it doesn't know how, use a fallback method.

    method = getattr(obj, '_StateRef__attr_ref', None)
    if method:
        stateref = method(attr) # REVIEW: pass moreattrs into here too?
        # print "ObjAttr_StateRef returning stateref %r" % (stateref,)
        if not getattr( stateref, 'debug_name', None):
            # TODO: do this below for other ways of finding a stateref
            # REVIEW: can we assume all kinds of staterefs have that attr, public for get and set?
            # This includes class Lval objects -- do they inherit stateref API? Not yet! ### FIX
            stateref.debug_name = "ObjAttr_StateRef(%r, %r)" % (obj, attr)
        return stateref

    # Use a fallback method. Note: this might produce a ref to a "delayed copy" of the state.
    # That's necessary if changes are tracked by polling and diff,
    # since otherwise the retval of get_value would change sooner than the change-track message was sent.
    # Alternatively, all get_value calls could cause it to be compared at that time... but I'm not sure that's a good idea --
    # it might cause invals at the wrong times (inside update methods calling get_value).
    assert 0, "ObjAttr_StateRef fallback is nim -- needed for %r" % (obj,)

    pass

# ==

### TODO:  val = not not val   before setting pref  - ie val = boolean(val), or pass boolean as type coercer

def connect_checkbox_with_boolean_pref( qcheckbox, prefs_key ): #bruce 050810, rewritten 070814
    """
    Cause the checkbox to track the value of the given boolean preference,
    and cause changes to the checkbox to change the preference.
    (Use of the word "with" in the function name, rather than "to" or "from",
     is meant to indicate that this connection is two-way.)
    First remove any prior connection of the same type on the same checkbox.
    Legal for more than one checkbox to track and control the same pref [but that might be untested].
    """
    stateref = Preferences_StateRef( prefs_key) # note: no default value specified
    widget_connectWithState( qcheckbox, stateref, QCheckBox_ConnectionWithState)
    return

def connect_doubleSpinBox_with_pref(qDoubleSpinBox, prefs_key):
    """
    Cause the QDoubleSpinbox to track the value of the given preference key AND
    causes changes to the Double spinbox to change the value of that prefs_key.
    
    @param qDoubleSpinBox: QDoublespinbox  object which needs to be 'connected'
        to the given <prefs_key> (preference key)
    @type qDoubleSpinBox: B{QDoubleSpinBox}
    
    @param prefs_key: The preference key to be assocuated with <qDoubleSpinBox>

    @see: B{connect_checkbox_with_boolean_pref()}
    @see: B{QDoubleSpinBox_ConnectionWithState}
    @see: Preferences._setupPage_Dna() for an example use.  
    @see: connect_spinBox_with_pref()
    """
    stateref = Preferences_StateRef( prefs_key) # note: no default value specified
    widget_connectWithState( qDoubleSpinBox, stateref, QDoubleSpinBox_ConnectionWithState)
    return

def connect_spinBox_with_pref(qSpinBox, prefs_key):
    """
    Cause the QSpinbox to track the value of the given preference key AND
    causes changes to the Double spinbox to change the value of that prefs_key.
    
    @param qSpinBox: QSpinBox  object which needs to be 'connected'
        to the given <prefs_key> (preference key)
    @type qSpinBox: B{QSpinBox}
    
    @param prefs_key: The preference key to be assocuated with <qSpinBox>

    @see: B{connect_checkbox_with_boolean_pref()}
    @see: B{QSpinBox_ConnectionWithState}
    @see: Preferences._setupPage_Dna() for an example use.  
    @see: connect_doubleSpinBox_with_pref()
    """
    stateref = Preferences_StateRef( prefs_key) # note: no default value specified
    widget_connectWithState( qSpinBox, stateref, QSpinBox_ConnectionWithState)
    return

    

# ==

class _twoway_Qt_connection: #bruce 070814, experimental, modified from destroyable_Qt_connection
    ### TODO: RENAME; REVISE init arg order
    ### TODO: try to make destroyable_Qt_connection a super of this class
    """
    Private helper class for various "connect widget with state" features (TBD).
    Holds a Qt signal/slot connection, with a destroy method which disconnects it,
    but also makes a connection in the other direction, using additional __init__ args,
    which disables the first connection during use.
    Only certified for use when nothing else is similarly connected to the same widget.

    Main experimental aspect of API is the StateRef_API used by the stateref arg...
    """
    def __init__(self, widget, signal, stateref, widget_setter, owner = None):
        """
        ...StateRef_API used by the stateref arg...
        """
        sender = self.widget = widget
        self.stateref = stateref
        self.debug = getattr(self.stateref, '_changes__debug_print', False)
        change_tracked_setter = stateref.set_value ### is set_value public for all kinds of staterefs? VERIFY or MAKE TRUE
        usage_tracked_getter = stateref.get_value ### DITTO -- BTW also MUST rename these to imply desired user contract,
            # i.e. about how they're tracked, etc -- set_value_tracked, get_value_tracked, maybe. or setValue_tracked etc.

        slot = change_tracked_setter
            # function to take a new value and store it in, full invals/tracks -- value needs to be in same format
            # as comes with the widget signal in a single arg
        if owner is None:
            owner = sender # I hope that's ok -- not sure it is -- if not, put owner first in arglist, or, use topLevelWidget
        #e destroy self if owner is destroyed?
        self.vars = owner, sender, signal, slot
        # these two will become aspects of one state object, whose api provides them...
        self.usage_tracked_getter = usage_tracked_getter
        self.widget_setter = widget_setter
        # only after setting those instance vars is it safe to do the following:
        self.connect()
        self.connect_the_other_way() #e rename
        if self.debug:
            print "\n_changes__debug_print: finished _twoway_Qt_connection.__init__ for %r containing %r" % (self, stateref)
                ###REVIEW: what if subclass init is not done, and needed for %r to work?
        return
    def connect(self):
        owner, sender, signal, slot = self.vars
        owner.connect(sender, signal, slot)
    def disconnect(self):
        owner, sender, signal, slot = self.vars
        owner.disconnect(sender, signal, slot)
    def destroy(self):
        assert self.vars, "error to destroy twice: %r" % self # maybe make it legal and noop instead?
        self.disconnect()
        self.vars = None # error to disconnect self again
        # and the other direction too
        self.conn1.destroy()
        return
    def connect_the_other_way(self):
        self.conn1 = Formula( self.usage_tracked_getter, self.careful_widget_setter, debug = self.debug )
        if self.debug:
            print "\n_changes__debug_print: %r connected from %r to %r using %r with %r" % \
                  ( self, self.stateref, self.widget, self.conn1, self.usage_tracked_getter )
            ## self.conn1._changes__debug_print = True # too late to tell Formula to notice initial stuff! Done with option instead.
    debug = False
    def careful_widget_setter(self, value):
        # Note: for some time we used self.widget_setter rather than this method,
        # by mistake, and it apparently worked fine. We'll still use this method
        # as a precaution; also it might be truly needed if the widget quantizes
        # the value, unless the widget refrains from sending signals when
        # programmatically set. [bruce 070815]
        if self.debug:
            print "\n_changes__debug_print: %r setting %r to %r using %r" % \
                  ( self, self.widget, value, self.widget_setter )
        self.disconnect() # avoid possible recursion
        self.widget_setter(value)
            ## TODO: protect from exception -- but do what when it happens? destroy self?
        self.connect()
            ### WARNING: .connect is slow, since it runs our Python code to set up an undo wrapper
            # around the slot! We should revise this to tell Qt to block the signals instead.
            # [We can use: bool QObject::blockSignals ( bool block ) ==> returns prior value of signalsBlocked,
            #  now used in a helper function setValue_with_signals_blocked]
            # This will matter for performance when this is used for state which changes during a drag.
            # Note: avoiding the slot call is needed not only for recursion, but to avoid the
            # Undo checkpoint in the wrapper.
            # [bruce comments 071015; see also bug 2564 in other code]
        return
    pass

class QCheckBox_ConnectionWithState( _twoway_Qt_connection):
    def __init__(self, qcheckbox, stateref):
        widget_setter = qcheckbox.setChecked
        _twoway_Qt_connection.__init__(self, qcheckbox, SIGNAL("toggled(bool)"),
                                       stateref,
                                       widget_setter)
        return
    pass

class QDoubleSpinBox_ConnectionWithState( _twoway_Qt_connection):
    def __init__(self, qspinbox, stateref):
        widget_setter = qspinbox.setValue
            # note: requires bugfix in PM_DoubleSpinBox.setValue,
            # or this will also set default value when used with a PM_DoubleSpinBox object.
        self.qspinbox = qspinbox
        _twoway_Qt_connection.__init__(self, qspinbox, SIGNAL("valueChanged(double)"),
                                       stateref,
                                       widget_setter)
        return
    
    
class QSpinBox_ConnectionWithState( _twoway_Qt_connection):
    def __init__(self, qspinbox, stateref):
        widget_setter = qspinbox.setValue           
        self.qspinbox = qspinbox
        _twoway_Qt_connection.__init__(self, qspinbox, SIGNAL("valueChanged(int)"),
                                       stateref,
                                       widget_setter)
        return


class QPushButton_ConnectionWithAction(destroyable_Qt_connection):
    def __init__(self, qpushbutton, aCallable, cmdname = None):
        sender = qpushbutton
        signal = SIGNAL("clicked()")
        slot = wrap_callable_for_undo( aCallable, cmdname = cmdname) # need to keep a ref to this
        destroyable_Qt_connection.__init__( self, sender, signal, slot) # this keeps a ref to slot
        return
    pass

# still needed:
# - StateRef_API, in an appropriate file.
# - state APIs, objects, maybe exprs... obj-with-state-attr apis...
# - refactor above to take the widget with known signal/setter as its own class, maybe... not sure...
# we know each widget needs special case, so maybe fine to do those as subclasses... or as new methods on existing widget subclasses...
# review how to do that
# - code to put at most one of these on one widget - can be grabbed from above - helper function, for use in methods
#   problem - might need two funcs, one to clear, one to add. since order should be clear (to deactivate), make (activates), add,
#   so never two active at once.

#### REVIEW: should we rename connectWithState setStateConnection or something else with set,
# to match setAction?

# end
