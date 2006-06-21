# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
widget_controllers.py

$Id$
'''
__author__ = "bruce"


# a widget expr controller for a collapsible GroupBox

# (different default style on Windows/Linux and Mac -- but most of the difference
#  is in an earlier setup layer which makes the Qt widgets passed to this)

# wants access to 2 iconsets made from given imagenames in the "usual way for this env"
# (can that just be the program env as a whole?)

from qt import QIconSet, SIGNAL

def env_imagename_to_QIconSet(imagename, _cache = {}): ### to be replaced with env.imagename_to_QIconSet for global env or an arg env
    try:
        return _cache[imagename]
    except KeyError:
        pass
    
    ## pixmap_fname = imagename # stub
    from Utility import imagename_to_pixmap
    pixmap = imagename_to_pixmap(imagename)
    pixmap_fname = pixmap # will this arg work too?
    
    res = QIconSet()
    res.setPixmap(pixmap_fname, QIconSet.Automatic)
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
        ## self.env #e needs imagename_to_QIconSet

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
        "open is a boolean"
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
        iconset = env_imagename_to_QIconSet(imagename) # memoized
        self.groupbutton.setIconSet(iconset)
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

# end

