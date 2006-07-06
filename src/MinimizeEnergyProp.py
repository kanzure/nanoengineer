# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
MinimizeEnergyProp.py - the MinimizeEnergyProp class, including all methods needed by the Minimize Energy dialog.

$Id$

History:

mark 060705 - Created for Alpha 8 NFR: "Simulator > Minimize Energy".
'''
__author__ = "Mark"

from qt import *
from HistoryWidget import greenmsg, redmsg, orangemsg, _graymsg, quote_html
from MinimizeEnergyPropDialog import MinimizeEnergyPropDialog
from GeneratorBaseClass import GroupButtonMixin
from Sponsors import SponsorableMixin

from prefs_constants import Minimize_watchRealtimeMinimization_prefs_key
from prefs_constants import Minimize_endRMS_prefs_key as endRMS_prefs_key
from prefs_constants import Minimize_endMax_prefs_key as endMax_prefs_key
from prefs_constants import Minimize_cutoverRMS_prefs_key as cutoverRMS_prefs_key
from prefs_constants import Minimize_cutoverMax_prefs_key as cutoverMax_prefs_key

from debug import print_compact_traceback
import env, platform
from UserPrefs import get_pref_or_optval
from widgets import double_fixup
import preferences
## from prefs_widgets import connect_checkbox_with_boolean_pref

class MinimizeEnergyProp(SponsorableMixin, GroupButtonMixin, MinimizeEnergyPropDialog):

    cmdname = greenmsg("Minimize Energy: ") # WARNING: self.cmdname might be used by one of the superclasses
    plain_cmdname = "Minimize Energy"
    sponsor_keyword = None

    def __init__(self, win):
        MinimizeEnergyPropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.previousParams = None
        self.setup_ruc()
        self.setup_validators()
        self.seltype = 'All'
        self.update_widgets() # to make sure self attrs are set
##        connect_checkbox_with_boolean_pref( self.watch_minimization_checkbox, Minimize_watchRealtimeMinimization_prefs_key )

    def setup_ruc(self):
        "#doc"
        #bruce 060705 use new common code, if it works
        from widget_controllers import realtime_update_controller
        self.ruc = realtime_update_controller( 
            ( self.update_btngrp, self.update_number_spinbox, self.update_units_combobox ),#k all names
            self.watch_minimization_checkbox,
            Minimize_watchRealtimeMinimization_prefs_key
        )
        ## can't do this yet: self.ruc.set_widgets_from_update_data( self.previous_movie._update_data ) # includes checkbox
        # for A8, only the checkbox will be persistent; the others will be sticky only because the dialog is not remade at runtime
        return

    def setup(self):
        """Setup and show the Minimize Energy dialog."""
        # Get widget parameters, update widgets, save previous parameters (for Restore Defaults) and show dialog.

        # use selection to decide if default is Sel or All
        selection = self.win.assy.selection_from_glpane() # compact rep of the currently selected subset of the Part's stuff
        if selection.nonempty():
            self.seltype = 'Sel'
        else:
            self.seltype = 'All'
        self.update_widgets() # only the convergence criteria, for A8, plus All/Sel command from self.seltype
        self.previousParams = self.gather_parameters() # only used in case Cancel wants to restore them; only conv crit for A8
        self.show()
           
    def gather_parameters(self): ###e should perhaps include update_data from ruc (not sure it's good) -- but no time for A8
        """Returns a tuple with the current parameter values from the widgets. Also sets those in env.prefs.
        Doesn't do anything about self.seltype, since that is a choice of command, not a parameter for a command.
        """
        self.change_endrms('notused')
        self.change_endmax('notused')
        self.change_cutoverrms('notused')
        self.change_cutovermax('notused')
        return tuple([env.prefs[key] for key in (endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key)])
    
    def update_widgets(self, update_seltype = True):
        """Update the widgets using the current env.prefs values and self attrs."""
        if update_seltype:
            if self.seltype == 'All':
                self.minimize_all_rbtn.setChecked(1)
            else:
                self.minimize_sel_rbtn.setChecked(1)

        # WARNING: some of the following code is mostly duplicated by UserPrefs code
        self.endrms = get_pref_or_optval(endRMS_prefs_key, -1.0, '')
        self.endrms_linedit.setText(str(self.endrms))
        
        self.endmax = get_pref_or_optval(endMax_prefs_key, -1.0, '')
        self.endmax_linedit.setText(str(self.endmax))
        
        self.cutoverrms = get_pref_or_optval(cutoverRMS_prefs_key, -1.0, '')
        self.cutoverrms_linedit.setText(str(self.cutoverrms))
        
        self.cutovermax = get_pref_or_optval(cutoverMax_prefs_key, -1.0, '')
        self.cutovermax_linedit.setText(str(self.cutovermax))

        ###e also watch in realtime prefs for this -- no, thats in another method for now
        return
        
    def ok_btn_clicked(self):
        'Slot for OK button.'
        QDialog.accept(self)
        if env.debug(): print 'ok'
        self.gather_parameters()
            ### kluge: has side effect on env.prefs
            # (should we pass these as arg to Minimize_CommandRun rather than thru env.prefs??)
        if platform.atom_debug:
            print "debug: reloading runSim on each use, for development"
            import runSim, debug
            debug.reload_once_per_event(runSim)
        from runSim import Minimize_CommandRun
        # do this in gather?
        if self.minimize_all_rbtn.isChecked():
            self.seltype = 'All'
            seltype_name = "All"
        else:
            self.seltype = 'Sel'
            seltype_name = "Selection"
        self.win.assy.current_command_info(cmdname = self.plain_cmdname + " (%s)" % seltype_name) # cmdname for Undo

        update_cond = self.ruc.get_update_cond_from_widgets()
        cmdrun = Minimize_CommandRun( self.win, self.seltype, type = 'Minimize', update_cond = update_cond)
        cmdrun.run()
        return
        
    def cancel_btn_clicked(self):
        'Slot for Cancel button.'
        if env.debug(): print 'cancel'
        # restore values we grabbed on entry.
        for key,val in zip((endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key), self.previousParams):
            env.prefs[key] = val
        self.update_widgets(update_seltype = False) #k might not matter since we're about to hide it, but can't hurt
        QDialog.reject(self)
        return
        
    def restore_defaults_btn_clicked(self):
        'Slot for Restore Defaults button.'
        # restore factory defaults # for A8, only for conv crit, not for watch motion settings
        env.prefs.restore_defaults([endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key])
        self.update_widgets(update_seltype = False)
        
    def whatsthis_btn_clicked(self):
        'Slot for the What\'s This button'
        QWhatsThis.enterWhatsThisMode()
        
    # Property Manager groupbox button slots

    def toggle_grpbtn_1(self):
        'Slot for first groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_1, self.line1,
                            self.minimize_all_rbtn, self.minimize_sel_rbtn)

    def toggle_grpbtn_2(self):
        'Slot for second groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_2, self.line2,
                            self.watch_minimization_checkbox, self.update_btngrp)
        
    def toggle_grpbtn_3(self):
        'Slot for third groupbox toggle button'
        self.toggle_groupbox(self.grpbtn_3, self.line3,
                            self.endrms_lbl, self.endrms_linedit,
                            self.endmax_lbl, self.endmax_linedit,
                            self.cutoverrms_lbl, self.cutoverrms_linedit,
                            self.cutovermax_lbl, self.cutovermax_linedit,
                            ##self.spacer_3 - had to be set to 1 pixel in ui file, since it's a local var, not a self attr
                            )

    # WARNING: some of the following code is mostly duplicated by UserPrefs code;
    # the docstrings are wrong in this context, since these methods have no signal connections

    def setup_validators(self):
        # Validator for the linedit widgets.
        self.endrms_validator = QDoubleValidator(self)
        self.endrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0.0 to 100, 2 decimal places
        self.endrms_linedit.setValidator(self.endrms_validator)
        
        self.endmax_validator = QDoubleValidator(self)
        self.endmax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.endmax_linedit.setValidator(self.endmax_validator)
        
        self.cutoverrms_validator = QDoubleValidator(self)
        self.cutoverrms_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutoverrms_linedit.setValidator(self.cutoverrms_validator)
        
        self.cutovermax_validator = QDoubleValidator(self)
        self.cutovermax_validator.setRange(0.0, 100.0, 2) # Range for linedits: 0 to 100, 2 decimal places
        self.cutovermax_linedit.setValidator(self.cutovermax_validator)

    def change_endrms(self, text):
        try:
            endrms_str = double_fixup(self.endrms_validator, self.endrms_linedit.text(), self.endrms)
            self.endrms_linedit.setText(endrms_str)
            if endrms_str:
                env.prefs[endRMS_prefs_key] = float(str(endrms_str))
            else:
                env.prefs[endRMS_prefs_key] = -1.0
            self.endrms = endrms_str
        except:
            print_compact_traceback("bug in change_endrms ignored: ") 
        
    def change_endmax(self, text):
        try:
            endmax_str = double_fixup(self.endmax_validator, self.endmax_linedit.text(), self.endmax)
            self.endmax_linedit.setText(endmax_str)
            if endmax_str:
                env.prefs[endMax_prefs_key] = float(str(endmax_str))
            else:
                env.prefs[endMax_prefs_key] = -1.0
            self.endmax = endmax_str
        except:
            print_compact_traceback("bug in change_endmax ignored: ") 
            
    def change_cutoverrms(self, text):
        try:
            cutoverrms_str = double_fixup(self.cutoverrms_validator, self.cutoverrms_linedit.text(), self.cutoverrms)
            self.cutoverrms_linedit.setText(cutoverrms_str)
            if cutoverrms_str:
                env.prefs[cutoverRMS_prefs_key] = float(str(cutoverrms_str))
            else:
                env.prefs[cutoverRMS_prefs_key] = -1.0
            self.cutoverrms = cutoverrms_str
        except:
            print_compact_traceback("bug in change_cutoverrms ignored: ") 
            
    def change_cutovermax(self, text):
        try:
            cutovermax_str = double_fixup(self.cutovermax_validator, self.cutovermax_linedit.text(), self.cutovermax)
            self.cutovermax_linedit.setText(cutovermax_str)
            if cutovermax_str:
                env.prefs[cutoverMax_prefs_key] = float(str(cutovermax_str))
            else:
                env.prefs[cutoverMax_prefs_key] = -1.0
            self.cutovermax = cutovermax_str
        except:
            print_compact_traceback("bug in change_cutovermax ignored: ") 

    pass # end of class MinimizeEnergyProp

# end
