# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
widget_controllers.py - miscellaneous widget-controller classes

@author: bruce
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""

# a widget expr controller for a collapsible GroupBox

# (different default style on Windows/Linux and Mac -- but most of the difference
#  is in an earlier setup layer which makes the Qt widgets passed to this)

# wants access to 2 iconsets made from given imagenames in the "usual way for this env"
# (can that just be the program env as a whole?)

from PyQt4.Qt import QIcon, SIGNAL
from utilities.qt4transition import qt4todo

import foundation.env as env


def _env_imagename_to_QIcon(imagename, _cache = {}): ### to be replaced with env.imagename_to_QIcon for global env or an arg env
    try:
        return _cache[imagename]
    except KeyError:
        pass

    ## pixmap_fname = imagename # stub
    from utilities.icon_utilities import imagename_to_pixmap
    pixmap = imagename_to_pixmap(imagename)
    pixmap_fname = pixmap # will this arg work too?

    res = QIcon()
    res.setPixmap(pixmap_fname, QIcon.Automatic)
    _cache[imagename] = res # memoize, and also keep permanent python reference
    return res


class CollapsibleGroupController_Qt:
    open = True #k maybe not needed
    def __init__(self, parent, desc, header_refs, hidethese, groupbutton):
##        print parent, header_refs
##        print hidethese, groupbutton
        self.parent = parent # the QDialog subclass with full logic
        self.desc = desc # group_desc
        self.header_refs = header_refs # just keep python refs to these qt objects in the group header, or other objs related to the group
        self.hidethese = hidethese # what to hide and show (and python refs to other objects in the group)
        self.groupbutton = groupbutton # the QPushButton in the group header (used in two ways: signal, and change the icon)

        self.style = 'Mac' ### set from env
        ## self.env #e needs imagename_to_QIcon

        self.options = self.desc.options
        expanded = self.options.get('expanded', True) # these options were set when the desc was interpreted, e.g. "expanded = True"
            ##e ideally, actual default would come from env
        ### kluge for now:
        if expanded == 'false':
            expanded = False
        self.set_open(expanded)
        # signal for button
        self.parent.connect(groupbutton,SIGNAL("clicked()"),self.toggle_open) # was toggle_nt_parameters_grpbtn

        return

    # runtime logic
    def toggle_open(self):
        open = not self.open
        self.set_open(open)
        self.parent.update() # QWidget.update()
            #bruce  - see if this speeds it up -- not much, but maybe a little, hard to say.
            #e would it work better to just change the height? try later.
        return
    def set_open(self, open):
        self.open = open
            #e someday, the state might be externally stored... let this be a property ref to self.stateref[self.openkey]
        self.set_openclose_icon( self.open )
        self.set_children_shown( self.open )
        return
    def set_openclose_icon(self, open):
        """
        #doc

        @param open:
        @type open: boolean
        """
        #e do we want to add a provision for not being collapsible at all?
        collapsed = not open
        if self.style == 'Mac':
            # on Mac, icon shows current state
            if collapsed:
                imagename = "mac_collapsed_icon.png"
            else:
                imagename = "mac_expanded_icon.png"
        else:
            # on Windows, it shows the state you can change it to
            if collapsed:
                imagename = "win_expand_icon.png"
            else:
                imagename = "win_collapse_icon.png"
        iconset = _env_imagename_to_QIcon(imagename) # memoized
        self.groupbutton.setIcon(iconset)
        return
    def set_children_shown(self, open):
        for child in self.hidethese:
            if open:
                child.show()
            else:
                child.hide()
        return
    pass

class FloatLineeditController_Qt:
    def __init__(self, parent, desc, lineedit):
        self.parent = parent # the QDialog subclass with full logic (note: not the Group it's in -- we don't need to know that)
        self.desc = desc # param_desc
        self.lineedit = lineedit # a QLineEdit

        param = self.desc
        # has suffix, min, max, default
        ### needs a controller to handle the suffix, min, and max, maybe using keybindings; or needs to be floatspinbox
        ### may need a precision argument, at least to set format for default value
        # note: see Qt docs for inputMask property - lets you set up patterns it should look like
        precision = 1
        format = "%0.1f"
        suffix = param.options.get('suffix', '')
        self.suffix = suffix #060601
        printer = lambda val, format = format, suffix = suffix: format % val + suffix ##e store this
        default = param.options.get('default', 0.0) ### will be gotten through an env or state
        text = printer(default)
        self.lineedit.setText(self.parent._tr(text)) # was "20.0 A" -- btw i doubt it's right to pass it *all* thru __tr

        self.default = default
    def get_value(self):
        text = str(self.lineedit.text())
        # remove suffix, or any initial part of it, or maybe any subsequence of it (except for numbers in it)...
        # ideal semantics are not very clear!
        removed_suffix = False
        text = text.strip()
        suffix = self.suffix.strip()
        if text.endswith(suffix):
            # this case is important to always get right
            removed_suffix = True
            text = text[:-len(suffix)]
            text = text.strip()
        # now it's either exactly right, or a lost cause -- forget about supporting partially-remaining suffix.
        #e should we visually indicate errors somehow? (yes, ideally by color of the text, and tooltip)
        try:
            return float(text)
        except:
            ### error message or indicator
            return self.default
        pass
    pass

class realtime_update_controller: #bruce 060705, consolidate code from runSim.py, SimSetup.py, and soon MinimizeEnergyProp.py
    """
    #doc
    """
    def __init__(self, widgets, checkbox = None, checkbox_prefs_key = None):
        """
        Set the data widgets, and if given, the checkbox widget and its prefs key, both optional.
        If checkbox and its prefs_key are both there, connect them. If neither is provided, always update.
        """
        self.watch_motion_buttongroup, self.update_number_spinbox, self.update_units_combobox = widgets
        self.checkbox = checkbox
        self.checkbox_prefs_key = checkbox_prefs_key
        if checkbox and checkbox_prefs_key:
            from widgets.prefs_widgets import connect_checkbox_with_boolean_pref
            connect_checkbox_with_boolean_pref(checkbox , checkbox_prefs_key)
    def set_widgets_from_update_data(self, update_data):
        if update_data:
            update_number, update_units, update_as_fast_as_possible_data, enable = update_data
            if self.checkbox:
                self.checkbox.setChecked(enable)
            if self.checkbox_prefs_key: #k could be elif, if we connected them above
                env.prefs[self.checkbox_prefs_key] = enable
            qt4todo('self.watch_motion_buttongroup.setButton( update_as_fast_as_possible_data')
            self.update_number_spinbox.setValue( update_number)
            for i in range(self.update_units_combobox.count()):
                if self.update_units_combobox.itemText(i) == update_units:
                    self.update_units_combobox.setCurrentIndex(i)
                    return
            raise Exception("update_units_combobox has no such option: " + update_units)
        else:
            pass # rely on whatever is already in them (better than guessing here)
        return
    def get_update_data_from_widgets(self):
        update_as_fast_as_possible_data = self.watch_motion_buttongroup.checkedId() # 0 means yes, 1 means no (for now)
            # ( or -1 means neither, but that's prevented by how the button group is set up, at least when it's enabled)
        update_number = self.update_number_spinbox.value() # 1, 2, etc (or perhaps 0??)
        update_units = str(self.update_units_combobox.currentText()) # 'frames', 'seconds', 'minutes', 'hours'
        if self.checkbox:
            enable = self.checkbox.isChecked()
        elif self.checkbox_prefs_key:
            enable = env.prefs[self.checkbox_prefs_key]
        else:
            enable = True
        return update_number, update_units, update_as_fast_as_possible_data, enable
    def update_cond_from_update_data(self, update_data): #e could be a static method
        update_number, update_units, update_as_fast_as_possible_data, enable = update_data
        if not enable:
            return False #e someday we might do this at the end, if the subsequent code is extended to save some prefs
        update_as_fast_as_possible = (update_as_fast_as_possible_data != 1)
        if env.debug():
            print "debug: using update_as_fast_as_possible = %r,  update_number, update_units = %r, %r" % \
                  ( update_as_fast_as_possible,  update_number, update_units )
            pass
        if update_as_fast_as_possible:
            # This radiobutton might be misnamed; it really means "use the old code,
            # i.e. not worse than 20% slowdown, with threshholds".
            # It's also ambiguous -- does "fast" mean "fast progress"
            # or "often" (which are opposites)? It sort of means "often".
            update_cond = ( lambda simtime, pytime, nframes:
                            simtime >= max(0.05, min(pytime * 4, 2.0)) )
        elif update_units == 'frames':
            update_cond = ( lambda simtime, pytime, nframes, _nframes = update_number:  nframes >= _nframes )
        elif update_units == 'seconds':
            update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number:  simtime + pytime >= _timelimit )
        elif update_units == 'minutes':
            update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 60:  simtime + pytime >= _timelimit )
        elif update_units == 'hours':
            update_cond = ( lambda simtime, pytime, nframes, _timelimit = update_number * 3600:  simtime + pytime >= _timelimit )
        else:
            print "don't know how to set update_cond from (%r, %r)" % (update_number, update_units)
            update_cond = None # some callers can tolerate this, though it's always a reportable error
        return update_cond
    def get_update_cond_from_widgets(self):
        update_data = self.get_update_data_from_widgets()
        return self.update_cond_from_update_data(update_data)
    pass # end of class realtime_update_controller

# end

