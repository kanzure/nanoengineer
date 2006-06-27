# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
ParameterDialog.py -- generate dialogs for editing sets of parameters,
from descriptions of the parameters and of how to edit them,
encoded as data which can (in principle) be manipulated at a high level in python,
or which can be parsed from easily readable/editable text files.

$Id$
'''

__author__ = "bruce"

# Form implementation generated from reading ui file '.../nanotube_mac.ui'
#
# Created: Tue May 16 12:05:20 2006
#      by: The PyQt User Interface Compiler (pyuic) 3.14.1
#
# WARNING! All changes made in this file will be lost!
# Actually they won't be...


from qt import *

from generator_button_images import image0_data,  image1_data,  image2_data,  image3_data,  image4_data,  image5_data,  image6_data,  image7_data

from widget_controllers import CollapsibleGroupController_Qt, FloatLineeditController_Qt #e might be gotten from env instead...

from debug import print_compact_traceback


# image uses -- we should rename them ####@@@@
##self.heading_pixmap.setPixmap(self.image1) # should be: title_icon ####
##self.sponsor_btn.setPixmap(self.image2)
##self.done_btn.setIconSet(QIconSet(self.image3))
##self.abort_btn.setIconSet(QIconSet(self.image4))
##self.preview_btn.setIconSet(QIconSet(self.image5))
##self.whatsthis_btn.setIconSet(QIconSet(self.image6))
##self.nt_parameters_grpbtn.setIconSet(QIconSet(self.image7))
        
## class parameter_dialog(QDialog): # was nanotube_dialog
class parameter_dialog_or_frame:
    "use as a pre-mixin before QDialog or QFrame" ####@@@@
    def __init__(self, parent = None, desc = None, name = None, modal = 0, fl = 0, env = None, type = "QDialog"):
        if env is None:
            import env # this is a little weird... probably it'll be ok, and logically it seems correct.
        
        self.desc = desc

        self.typ = type
        if type == "QDialog":
            QDialog.__init__(self,parent,name,modal,fl)
        elif type == "QTextEdit":
            QTextEdit.__init__(self, parent, name)
        elif type == "QFrame":
            QFrame.__init__(self,parent,name)
        else:
            print "don't know about type == %r" % (type,)
        
        self.image1 = QPixmap()
        self.image1.loadFromData(image1_data,"PNG") # should be: title_icon ####
        self.image3 = QPixmap()
        self.image3.loadFromData(image3_data,"PNG")
        self.image4 = QPixmap()
        self.image4.loadFromData(image4_data,"PNG")
        self.image5 = QPixmap()
        self.image5.loadFromData(image5_data,"PNG")
        self.image6 = QPixmap()
        self.image6.loadFromData(image6_data,"PNG")
        self.image7 = QPixmap()
        self.image7.loadFromData(image7_data,"PNG")
        self.image0 = QPixmap(image0_data) # should be: border_icon ####
        self.image2 = QPixmap(image2_data) # should be: sponsor_pixmap ####

        try:
            ####@@@@
            title_icon_name = self.desc.options.get('title_icon')
            border_icon_name = self.desc.options.get('border_icon')
            if title_icon_name:
                self.image1 = env.imagename_to_pixmap(title_icon_name) ###@@@ pass icon_path
                    ###@@@ import imagename_to_pixmap or use env function
                    # or let that func itself be an arg, or have an env arg for it
                    ###e rename it icon_name_to_pixmap, or find_icon? (the latter only if it's ok if it returns an iconset)
                    ###e use iconset instead?
            if border_icon_name:
                self.image0 = env.imagename_to_pixmap(border_icon_name)
        except:
            print_compact_traceback("bug in icon-setting code, using fallback icons: ")
            pass

        if not name:
            self.setName("parameter_dialog_or_frame") ###

        ###k guess this will need: if type == 'QDialog'
        self.setIcon(self.image0) # should be: border_icon ####

        nanotube_dialogLayout = QVBoxLayout(self,0,0,"nanotube_dialogLayout")

        self.heading_frame = QFrame(self,"heading_frame")
        self.heading_frame.setPaletteBackgroundColor(QColor(122,122,122))
        self.heading_frame.setFrameShape(QFrame.NoFrame)
        self.heading_frame.setFrameShadow(QFrame.Plain)
        heading_frameLayout = QHBoxLayout(self.heading_frame,0,3,"heading_frameLayout")

        self.heading_pixmap = QLabel(self.heading_frame,"heading_pixmap")
        self.heading_pixmap.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed,0,0,self.heading_pixmap.sizePolicy().hasHeightForWidth()))
        self.heading_pixmap.setPixmap(self.image1) # should be: title_icon ####
        self.heading_pixmap.setScaledContents(1)
        heading_frameLayout.addWidget(self.heading_pixmap)

        self.heading_label = QLabel(self.heading_frame,"heading_label")
        self.heading_label.setPaletteForegroundColor(QColor(255,255,255))
        heading_label_font = QFont(self.heading_label.font())
        heading_label_font.setPointSize(12)
        heading_label_font.setBold(1)
        self.heading_label.setFont(heading_label_font)
        heading_frameLayout.addWidget(self.heading_label)
        nanotube_dialogLayout.addWidget(self.heading_frame)

        self.body_frame = QFrame(self,"body_frame")
        self.body_frame.setFrameShape(QFrame.StyledPanel)
        self.body_frame.setFrameShadow(QFrame.Raised)
        body_frameLayout = QVBoxLayout(self.body_frame,3,3,"body_frameLayout")

        self.sponsor_frame = QFrame(self.body_frame,"sponsor_frame")
        self.sponsor_frame.setPaletteBackgroundColor(QColor(255,255,255))
        self.sponsor_frame.setFrameShape(QFrame.StyledPanel)
        self.sponsor_frame.setFrameShadow(QFrame.Raised)
        sponsor_frameLayout = QHBoxLayout(self.sponsor_frame,0,0,"sponsor_frameLayout")

        self.sponsor_btn = QPushButton(self.sponsor_frame,"sponsor_btn")
        self.sponsor_btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.sponsor_btn.sizePolicy().hasHeightForWidth()))
        self.sponsor_btn.setPaletteBackgroundColor(QColor(255,255,255))
        self.sponsor_btn.setPixmap(self.image2) # should be: sponsor_pixmap #### [also we'll need to support >1 sponsor]
        self.sponsor_btn.setFlat(1)
        sponsor_frameLayout.addWidget(self.sponsor_btn)
        body_frameLayout.addWidget(self.sponsor_frame)

        layout59 = QHBoxLayout(None,0,6,"layout59")
        left_spacer = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(left_spacer)

        self.done_btn = QToolButton(self.body_frame,"done_btn")
        self.done_btn.setIconSet(QIconSet(self.image3))
        layout59.addWidget(self.done_btn)

        self.abort_btn = QToolButton(self.body_frame,"abort_btn")
        self.abort_btn.setIconSet(QIconSet(self.image4))
        layout59.addWidget(self.abort_btn)

        self.preview_btn = QToolButton(self.body_frame,"preview_btn")
        self.preview_btn.setIconSet(QIconSet(self.image5))
        layout59.addWidget(self.preview_btn)

        self.whatsthis_btn = QToolButton(self.body_frame,"whatsthis_btn")
        self.whatsthis_btn.setIconSet(QIconSet(self.image6))
        layout59.addWidget(self.whatsthis_btn)
        right_spacer = QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout59.addItem(right_spacer)
        body_frameLayout.addLayout(layout59)

        self.groups = []
        self.param_getters = {} # map from param name to get-function (which gets current value out of its widget or controller)

        for group_desc in self.desc.kids('group'):
            
            # == start parameters_grpbox ### this will differ for Windows style

            header_refs = [] # keep python refcounted refs to all objects we make (at least the ones pyuic stored in self attrs)
            
            self.parameters_grpbox = QGroupBox(self.body_frame,"parameters_grpbox")
            self.parameters_grpbox.setFrameShape(QGroupBox.StyledPanel)
            self.parameters_grpbox.setFrameShadow(QGroupBox.Sunken)
            self.parameters_grpbox.setMargin(0)
            self.parameters_grpbox.setColumnLayout(0,Qt.Vertical)
            self.parameters_grpbox.layout().setSpacing(1)
            self.parameters_grpbox.layout().setMargin(4)
            parameters_grpboxLayout = QVBoxLayout(self.parameters_grpbox.layout())
            parameters_grpboxLayout.setAlignment(Qt.AlignTop)

            layout20 = QHBoxLayout(None,0,6,"layout20")

            self.nt_parameters_grpbtn = QPushButton(self.parameters_grpbox,"nt_parameters_grpbtn")
            self.nt_parameters_grpbtn.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed,0,0,self.nt_parameters_grpbtn.sizePolicy().hasHeightForWidth()))
            self.nt_parameters_grpbtn.setMaximumSize(QSize(16,16))
            self.nt_parameters_grpbtn.setAutoDefault(0)
            self.nt_parameters_grpbtn.setIconSet(QIconSet(self.image7)) ### not always right, but doesn't matter
            self.nt_parameters_grpbtn.setFlat(1)
            layout20.addWidget(self.nt_parameters_grpbtn)

            self.parameters_grpbox_label = QLabel(self.parameters_grpbox,"parameters_grpbox_label")
            self.parameters_grpbox_label.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Minimum,0,0,self.parameters_grpbox_label.sizePolicy().hasHeightForWidth()))
            self.parameters_grpbox_label.setAlignment(QLabel.AlignVCenter)
            layout20.addWidget(self.parameters_grpbox_label)
            gbx_spacer1 = QSpacerItem(67,16,QSizePolicy.Expanding,QSizePolicy.Minimum)
            layout20.addItem(gbx_spacer1)
            parameters_grpboxLayout.addLayout(layout20)

            nt_parameters_body_layout = QGridLayout(None,1,1,0,6,"nt_parameters_body_layout") ### what is 6 -- is it related to number of items???
                # is it 6 in all the ones we got, but that could be a designer error so i better look it up sometime.

            # == start its kids

            # will use from above: self.parameters_grpbox, nt_parameters_body_layout
            
            nextrow = 0 # which row of the QGridLayout to start filling next (loop variable)
            hidethese = [] # set of objects to hide or show, when this group is closed or opened
            
            for param in group_desc.kids('parameter'):
                # param (a group subobj desc) is always a parameter, but we already plan to extend this beyond that,
                # so we redundantly test for this here.
                getter = None
                paramname = None
                if param.isa('parameter'):
                    self.members_label = QLabel(self.parameters_grpbox,"members_label")
                    self.members_label.setAlignment(QLabel.AlignVCenter | QLabel.AlignRight)
                    nt_parameters_body_layout.addWidget(self.members_label,nextrow,0)
                    hidethese.append(self.members_label)
                    thisrow = nextrow
                    nextrow += 1
                    #e following should be known in a place that knows the input language, not here
                    paramname = param.options.get('name') or (param.args and param.args[0]) or "?"
                    paramlabel = param.options.get('label') or paramname ##e wrong, label "" or none ought to be possible
                    self.members_label.setText(self.__tr(paramlabel))
                    
                if param.isa('parameter', widget = 'combobox', type = ('str',None)):
                    self.members_combox = QComboBox(0,self.parameters_grpbox,"members_combox") ###k  what's 0?
                    #### it probably needs a handler class, and then that could do this setup
                    self.members_combox.clear()
                    default = param.options.get('default', None) # None is not equal to any string
                    thewidgetkid = param.kids('widget')[-1] # kluge; need to think what the desc method for this should be
                    for item in thewidgetkid.kids('item'):
                        itemval = item.args[0]
                        itemtext = itemval
                        self.members_combox.insertItem(self.__tr(itemtext)) #k __tr ok??
                        if itemval == default: #k or itemtext?
                            pass ##k i find no setItem in our py code, so not sure yet what to do for this.
                    nt_parameters_body_layout.addWidget(self.members_combox,thisrow,1)
                    hidethese.append(self.members_combox)
                    getter = (lambda combobox = self.members_combox: str(combobox.currentText()))
                        ##e due to __tr or non-str values, it might be better to use currentItem and look it up in a table
                        # (though whether __tr is good here might depend on what it's used for)
                                    
                elif param.isa('parameter', widget = ('lineedit', None), type = ('str',None)):
                    # this covers explicit str|lineedit, and 3 default cases str, lineedit, neither.
                    # (i.e. if you say parameter and nothing else, it's str lineedit by default.)
                    self.length_linedit = QLineEdit(self.parameters_grpbox,"length_linedit")
                    nt_parameters_body_layout.addWidget(self.length_linedit,thisrow,1)
                    hidethese.append(self.length_linedit)
                    default = str(param.options.get('default', ""))
                    self.length_linedit.setText(self.__tr(default)) # __tr ok?
                    getter = (lambda lineedit = self.length_linedit: str(lineedit.text()))
                    
                elif param.isa('parameter', widget = ('lineedit', None), type = 'float'):
                    self.length_linedit = QLineEdit(self.parameters_grpbox,"length_linedit")
                    nt_parameters_body_layout.addWidget(self.length_linedit,thisrow,1)
                    hidethese.append(self.length_linedit)
                    controller = FloatLineeditController_Qt(self, param, self.length_linedit)
                    header_refs.append(controller)
                    getter = controller.get_value
                    
                elif param.isa('parameter', widget = ('spinbox', None), type = 'int') or \
                     param.isa('parameter', widget = ('spinbox'), type = None):
                    self.chirality_N_spinbox = QSpinBox(self.parameters_grpbox,"chirality_N_spinbox") # was chirality_m_spinbox, now chirality_N_spinbox
                    ### seems like Qt defaults for min and max are 0,100 -- way too small a range!
                    if param.options.has_key('min') or 1:
                        self.chirality_N_spinbox.setMinValue(param.options.get('min', -999999999)) # was 0
                    if param.options.has_key('max') or 1:
                        self.chirality_N_spinbox.setMaxValue(param.options.get('max', +999999999)) # wasn't in egcode, but needed
                    self.chirality_N_spinbox.setValue(param.options.get('default', 0)) # was 5
                        ##e note: i suspect this default 0 should come from something that knows this desc grammar.
                    # set tooltip (same one for editfield and label)
                    tooltip = param.options.get('tooltip', '')
                    ###e do it for more kinds of params; share the code somehow; do it in controller, or setup-aid?
                    ###k QToolTip appropriateness; tooltip option might be entirely untested
                    if tooltip:
                        QToolTip.add(self.chirality_N_spinbox,self.__tr(tooltip))
                        QToolTip.add(self.members_label,self.__tr(tooltip)) ##k ok?? review once not all params have same-row labels.
                    suffix = param.options.get('suffix', '')
                    if suffix:
                        self.chirality_N_spinbox.setSuffix(self.__tr(suffix))
                    else:
                        self.chirality_N_spinbox.setSuffix(QString.null) # probably not needed
                    nt_parameters_body_layout.addWidget(self.chirality_N_spinbox,thisrow,1)
                    hidethese.append(self.chirality_N_spinbox)
                    getter = self.chirality_N_spinbox.value # note: it also has .text, which includes suffix
                    
                else:
                    print "didn't match:",param ###e improve this
                if getter and paramname and paramname != '?':
                    self.param_getters[paramname] = getter
                ### also bind these params to actions...
                continue # next param

            header_refs.extend( [self.parameters_grpbox, self.nt_parameters_grpbtn, self.parameters_grpbox_label] )
            
            # now create the logic/control object for the group
            group = CollapsibleGroupController_Qt(self, group_desc, header_refs, hidethese, self.nt_parameters_grpbtn)
                ### maybe ask env for the class to use for this?
            self.groups.append(group) ### needed?? only for scanning the params, AFAIK -- oh, and to maintain a python refcount.

            # from languageChange:
            if 1: # i don't know if these are needed:
                self.parameters_grpbox.setTitle(QString.null)
                self.nt_parameters_grpbtn.setText(QString.null)
            self.parameters_grpbox_label.setText(self.__tr(group_desc.args[0])) # was "Nanotube Parameters"
                ##e note that it's questionable in the syntax design for this property of a group (overall group label)
                # to be in that position (desc arg 0).
        
            # == end its kids
            
            parameters_grpboxLayout.addLayout(nt_parameters_body_layout)
            body_frameLayout.addWidget(self.parameters_grpbox)

            # == end parameters groupbox
            
            continue # next group

        nanotube_dialogLayout.addWidget(self.body_frame)
        spacer14 = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        nanotube_dialogLayout.addItem(spacer14)

        layout42 = QHBoxLayout(None,4,6,"layout42")
        btm_spacer = QSpacerItem(59,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        layout42.addItem(btm_spacer)

        self.cancel_btn = QPushButton(self,"cancel_btn")
        layout42.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton(self,"ok_btn")
        layout42.addWidget(self.ok_btn)
        nanotube_dialogLayout.addLayout(layout42)

        self.languageChange()

        self.resize(QSize(246,618).expandedTo(self.minimumSizeHint())) ### this size will need to be adjusted (guess -- it's only place overall size is set)
        self.clearWState(Qt.WState_Polished)

        ## self.connect(self.nt_parameters_grpbtn,SIGNAL("clicked()"),self.toggle_nt_parameters_grpbtn) ####

        # new:
        for button, methodname in ((self.sponsor_btn, 'do_sponsor_btn'),  #e generalize to more than one sponsor button
                                   (self.done_btn, 'do_done_btn'),
                                   (self.abort_btn, 'do_abort_btn'),
                                   (self.preview_btn, 'do_preview_btn'),
                                   (self.whatsthis_btn, 'do_whatsthis_btn'),
                                   (self.cancel_btn, 'do_cancel_btn'),
                                   (self.ok_btn, 'do_ok_btn')):
            if hasattr(self, methodname):
                self.connect(button,SIGNAL("clicked()"),getattr(self, methodname))
        return


    def languageChange(self):
        opts = self.desc.option_attrs
        
        self.setCaption(self.__tr(opts.caption)) # was "Nanotube"
        self.heading_label.setText(self.__tr(opts.title)) # was "Nanotube"
        self.sponsor_btn.setText(QString.null)
        
        self.done_btn.setText(QString.null)
        QToolTip.add(self.done_btn,self.__tr("Done"))
        
        self.abort_btn.setText(QString.null)
        QToolTip.add(self.abort_btn,self.__tr("Cancel"))
        
        self.preview_btn.setText(QString.null)
        QToolTip.add(self.preview_btn,self.__tr("Preview"))
        
        self.whatsthis_btn.setText(QString.null)
        QToolTip.add(self.whatsthis_btn,self.__tr("What's This Help"))

        ### move these up:
##        if 0:
##            self.parameters_grpbox.setTitle(QString.null)
##            self.nt_parameters_grpbtn.setText(QString.null)
##            self.parameters_grpbox_label.setText(self.__tr("Nanotube Parameters"))

##        if 0:
##            self.members_label.setText(self.__tr("Members :"))
##            self.length_label.setText(self.__tr("Length :"))
##            self.chirality_n_label.setText(self.__tr("Chirality (n) :"))
##            self.members_combox.clear()
##            self.members_combox.insertItem(self.__tr("C - C"))
##            self.members_combox.insertItem(self.__tr("B - N"))
##            self.length_linedit.setText(self.__tr("20.0 A"))
##            self.chirality_N_spinbox.setSuffix(QString.null)

        self.cancel_btn.setText(self.__tr("Cancel"))
        self.ok_btn.setText(self.__tr("OK"))
        return
    
    def __tr(self,s,c = None):
        return qApp.translate("nanotube_dialog",s,c)

    _tr = __tr # for access from other objects

    pass # end of class parameter_dialog_or_frame -- maybe it should be renamed

# ==

class ParameterDialogBase(parameter_dialog_or_frame):
    "#doc"
    controller = None
    def __init__(self, parent, description, env = None):
        """If description is a string, it should be a filename.
        Or (someday) it could be a ThingData, or (someday) maybe a menu_spec_like python list.
           This initializes the dialog, a Qt widget (not sure if it will be a widget when we have a "pane" option --
         most likely we'll use some other class for that, not this one with an option).
        But it doesn't show it or connect it to a controller.
        """
        desc = get_description(description) # might raise exceptions on e.g. syntax errors in description file
        parameter_dialog_or_frame.__init__(self, parent, desc, env = env, type = self.type) # self.type is a subclass-constant
            # sets self.desc (buttons might want to use it)
    def set_controller(self, controller):
        if self.controller:
            self.controller.forget_dialog(self)
        self.controller = controller
        if self.controller:
            self.controller.meet_dialog(self)
        return
    def set_defaults(self, dict1):
        if 1:
            print "set_defaults is nim" ####k is it even sensible w/o a controller being involved??

    def show(self):
        if self.controller:
            self.controller.setSponsor()
        if self.typ == "QDialog":
            QDialog.show(self)
        elif self.typ == "QTextEdit":
            QTextEdit.show(self)
        elif self.typ == "QFrame":
            QFrame.show(self)
        else:
            print "don't know about self.typ == %r" % (self.typ,)

    # bindings for the buttons -- delegate them to controller if we have one.
    def do_sponsor_btn(self):
        print "do_sponsor_btn: delegating"
        # does SponsorableMixin have something like sponsor_btn_clicked? yes, under that name and open_sponsor_homepage.
        if self.controller:
            self.controller.sponsor_btn_clicked()
    def do_done_btn(self):
        print "do_done_btn: delegating"
        if self.controller:
            self.controller.done_btn_clicked()
    def do_abort_btn(self):
        print "do_abort_btn: delegating"
        if self.controller:
            self.controller.abort_btn_clicked()
    def do_preview_btn(self):
        print "do_preview_btn: delegating"
        if self.controller:
            self.controller.preview_btn_clicked()
    def do_whatsthis_btn(self):
        print "do_whatsthis_btn: delegating"
        if self.controller:
            self.controller.whatsthis_btn_clicked()
    def do_cancel_btn(self):
        print "do_cancel_btn: delegating"
        if self.controller:
            self.controller.cancel_btn_clicked()
    def do_ok_btn(self):
        print "do_ok_btn: printing then delegating"
        if 1:
            print "printing param values"
            getters = self.param_getters.items()
            getters.sort()
            for paramname, getter in getters:
                try:
                   print "param %s = %r" % (paramname, getter())
                except:
                    print_compact_traceback("exception trying to get param %s: " % (paramname,))
        if self.controller:
            self.controller.ok_btn_clicked()
    #e might need to intercept accept, reject and depend on type == 'QDialog' -- or, do in subclass
    pass

class ParameterDialog( ParameterDialogBase, QDialog):
    type = 'QDialog'
    pass

class ParameterPane(   ParameterDialogBase, QFrame):
    type = 'QFrame'
    def accept(self): pass
    def reject(self): pass
    pass

class ParameterPaneTextEditTest( ParameterDialogBase, QTextEdit): ##k see if this works any better
    type = 'QTextEdit'
    def accept(self): pass
    def reject(self): pass
    pass

# ==

debug_parse = True #####@@@@@

def get_description(filename):
    """For now, only the filename option is supported.
    Someday, support the other ones mentioned in ParameterDialog.__init__.__doc__.
    """
    assert type(filename) == type(""), "get_description only supports filenames for now (and not even unicode filenames, btw)"
    
    file = open(filename, 'rU')

    from parse_utils import generate_tokens, parse_top, Whole

    gentok = generate_tokens(file.readline)

    res, newrest = parse_top(Whole, list(gentok))
    if debug_parse:
        print len(` res `), 'chars in res' #3924
##        print res # might be an error message
    if newrest and debug_parse: # boolean test, since normal value is []
        print "res is", res # assume it is an error message
        print "newrest is", newrest
        print "res[0].pprint() :"
        print res[0].pprint() #k

    if debug_parse:
        print "parse done"

    desc = res[0] #k class ThingData in parse_utils - move to another file? it stays with the toplevel grammar...
    
    return desc # from get_description


# == TEST CODE, though some might become real

import time, sys, os

class NTdialog(parameter_dialog_or_frame, QDialog): # in real life this will be something which delegates to controller methods
    def __init__(self, parent = None, desc = None):
        parameter_dialog_or_frame.__init__(self, parent, desc) # sets self.desc (buttons might want to use it)
    def do_sponsor_btn(self):
        print "do_sponsor_btn: nim"
    def do_done_btn(self):
        print "do_done_btn: nim"
    def do_abort_btn(self):
        print "do_abort_btn: nim"
    def do_preview_btn(self):
        print "do_preview_btn: nim"
    def do_whatsthis_btn(self):
        print "do_whatsthis_btn: nim"
    def do_cancel_btn(self):
        print "do_cancel_btn: nim"
    def do_ok_btn(self):
        print "do_ok_btn: printing param values"
        getters = self.param_getters.items()
        getters.sort()
        for paramname, getter in getters:
            try:
               print "param %s = %r" % (paramname, getter())
            except:
                print_compact_traceback("exception trying to get param %s: " % (paramname,))
        print
    pass

if __name__ == '__main__': # this has the parsing calls
    
    a = QApplication(sys.argv)
        
    ## filename = "testui.txt"
    filename = "../plugins/CoNTub/HJ-params.desc"

    desc = get_description(filename)

    parent = None # should be win or app?
    
    w = NTdialog(parent, desc) ### also, env to supply prefs, state to control
    w.show()
    a.connect(a, SIGNAL('lastWindowClosed()'), a, SLOT('quit()'))
    print "about to exec_loop"
    a.exec_loop()
    
    print "exiting, test done"
    
# end
