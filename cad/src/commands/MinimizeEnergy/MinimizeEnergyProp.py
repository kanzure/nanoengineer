# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
MinimizeEnergyProp.py - the MinimizeEnergyProp class, including all
methods needed by the Minimize Energy dialog.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

mark 060705 - Created for Alpha 8 NFR: "Simulator > Minimize Energy".
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QAbstractButton
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QWhatsThis
from PyQt4.Qt import QDoubleValidator

from utilities.Log import greenmsg, redmsg, orangemsg, _graymsg, quote_html
from commands.MinimizeEnergy.MinimizeEnergyPropDialog import Ui_MinimizeEnergyPropDialog
from PM.GroupButtonMixin import GroupButtonMixin
from sponsors.Sponsors import SponsorableMixin
from utilities.icon_utilities import geticon

from utilities.prefs_constants import Minimize_watchRealtimeMinimization_prefs_key
from utilities.prefs_constants import Minimize_endRMS_prefs_key as endRMS_prefs_key
from utilities.prefs_constants import Minimize_endMax_prefs_key as endMax_prefs_key
from utilities.prefs_constants import Minimize_cutoverRMS_prefs_key as cutoverRMS_prefs_key
from utilities.prefs_constants import Minimize_cutoverMax_prefs_key as cutoverMax_prefs_key
from utilities.prefs_constants import Minimize_minimizationEngine_prefs_key
from utilities.prefs_constants import electrostaticsForDnaDuringMinimize_prefs_key
from utilities.prefs_constants import neighborSearchingInGromacs_prefs_key

from utilities.debug import print_compact_traceback
from utilities.debug import reload_once_per_event

import foundation.env as env
from utilities import debug_flags
from ne1_ui.prefs.Preferences import get_pref_or_optval
from widgets.widget_helpers import double_fixup
from utilities.debug_prefs import debug_pref, Choice_boolean_False
from widgets.prefs_widgets import connect_checkbox_with_boolean_pref

class MinimizeEnergyProp(QDialog, SponsorableMixin, GroupButtonMixin, Ui_MinimizeEnergyPropDialog):

    cmdname = greenmsg("Minimize Energy: ") # WARNING: self.cmdname might be used by one of the superclasses
    plain_cmdname = "Minimize Energy"
    sponsor_keyword = None

    def __init__(self, win):
        QDialog.__init__(self, win)  # win is parent.
        self.setupUi(self)
        self.update_btngrp_group = QButtonGroup()
        self.update_btngrp_group.setExclusive(True)
        for obj in self.update_btngrp.children():
            if isinstance(obj, QAbstractButton):
                self.update_btngrp_group.addButton(obj)
        
        #fix some icon problems
        self.setWindowIcon(
            geticon('ui/border/MinimizeEnergy.png'))
        self.done_btn.setIcon(
            geticon('ui/actions/Properties Manager/Done.png'))
        self.abort_btn.setIcon(
            geticon('ui/actions/Properties Manager/Abort.png'))
        self.restore_btn.setIcon(
            geticon('ui/actions/Properties Manager/Restore.png'))
        self.whatsthis_btn.setIcon(
            geticon('ui/actions/Properties Manager/WhatsThis.png'))
        
        self.connect(self.cancel_btn,
                     SIGNAL("clicked()"),
                     self.cancel_btn_clicked)
        self.connect(self.done_btn,
                     SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.connect(self.ok_btn,
                     SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.connect(self.restore_btn,
                     SIGNAL("clicked()"),
                     self.restore_defaults_btn_clicked)
        self.connect(self.sponsor_btn,
                     SIGNAL("clicked()"),
                     self.open_sponsor_homepage)
        self.connect(self.whatsthis_btn,
                     SIGNAL("clicked()"),
                     self.whatsthis_btn_clicked)
        self.connect(self.abort_btn,
                     SIGNAL("clicked()"),
                     self.cancel_btn_clicked)
        self.connect(self.grpbtn_1,
                     SIGNAL("clicked()"),
                     self.toggle_grpbtn_1)
        self.connect(self.grpbtn_2,
                     SIGNAL("clicked()"),
                     self.toggle_grpbtn_2)
        self.connect(self.grpbtn_3,
                     SIGNAL("clicked()"),
                     self.toggle_grpbtn_3)
        self.connect(self.grpbtn_4,
                     SIGNAL("clicked()"),
                     self.toggle_grpbtn_4)
        
        connect_checkbox_with_boolean_pref(
            self.electrostaticsForDnaDuringMinimize_checkBox,
            electrostaticsForDnaDuringMinimize_prefs_key)
        
        connect_checkbox_with_boolean_pref(
            self.enableNeighborSearching_check_box,
            neighborSearchingInGromacs_prefs_key)

        self.minimize_engine_combobox.setCurrentIndex(
            env.prefs[Minimize_minimizationEngine_prefs_key])

        self.win = win
        self.previousParams = None
        self.setup_ruc()
        self.setup_validators()
        self.seltype = 'All'
        self.minimize_selection_enabled = True #bruce 080513
        self.sponsor_btn.setWhatsThis("""<b>NanoEngineer-1 Sponsor</b>
        <p>Click on the logo to learn more
        about this NanoEngineer-1 sponsor.</p>""")
        self.minimize_all_rbtn.setWhatsThis("""<b>Minimize All</b><p>Perform energy minimization on all the
        atoms in the workspace.</p>""")
        self.minimize_sel_rbtn.setWhatsThis("""<b>Minimize Selection</b><p>Perform energy minimization on the
        atoms that are currently selected.</p>""")
        self.watch_minimization_checkbox.setWhatsThis("""<p><b>Watch Motion In Real Time</b></p>Enables real time graphical
        updates during minimization runs.""")
        self.update_asap_rbtn.setWhatsThis("""<b>Update as fast as possible</b>
        <p>
        Update every 2 seconds,
        or faster (up to 20x/sec) if it doesn't slow minimization by more than 20%</p>""")
        self.update_every_rbtn.setWhatsThis("""<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the minimization. This allows the user to monitor minimization results while the minimization is running.</p>""")
        self.update_number_spinbox.setWhatsThis("""<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the minimization. This allows the user to monitor minimization results while the minimization is running.</p>""")
        self.update_units_combobox.setWhatsThis("""<b>Update every <i>n units.</u></b>
        <p>Specify how often to update
        the model during the minimization. This allows the user to monitor minimization results while the minimization is running.</p>""")
        self.endrms_linedit.setWhatsThis("""<b>EndRMS</b>
        <p>Continue until this RMS force is reached.</p>""")
        self.endmax_linedit.setWhatsThis("""<b>EndMax</b>
        <p>Continue until the total force on each atom
        is less than this value.</p>""")
        self.cutoverrms_linedit.setWhatsThis("""<b>CutoverRMS</b>
        <p>Use steepest descent until this RMS force
        is reached.</p>""")
        self.cutovermax_linedit.setWhatsThis("""<b>CutoverMax</b>
        <p>Use steepest descent  until the total force
        on each atom is less than this value.</p>""")
        self.cancel_btn.setWhatsThis("""<b>Cancel</b><p>Dismiss this dialog without taking any action.</p>""")
        self.ok_btn.setWhatsThis("""<b>Minimize Energy</b><p>Using the parameters specified above,
        perform energy minimization on some or all of the atoms.</p>""")
        self.setWhatsThis("""<u><b>Minimize Energy</b></u>
        <p>The potential energy of a chemical
        structure is a function of the relative positions of its atoms. To obtain this energy with complete accuracy involves a lot
        of computer time spent on quantum mechanical calculations, which cannot be practically done on a desktop computer. To get
        an approximate potential energy without all that, we represent the energy as a series of terms involving geometric properties
        of the structure: lengths of chemical bonds, angles between pairs and triples of chemical bonds, etc.
        </p><p>As is generally
        the case with physical systems, the gradient of the potential energy represents the forces acting on various particles. The
        atoms want to move in the direction that most reduces the potential energy. Energy minimization is a process of adjusting
        the atom positions to try to find a global minimum of the potential energy. Each atom contributes three variables (its x,
        y, and z coordinates) so the search space is multi-dimensional. The global minimum is the configuration that the atoms will
        settle into if lowered to zero Kelvin.
        </p>""")
            
        self.update_widgets() # to make sure self attrs are set

    def setup_ruc(self):
        """
        #doc
        """
        #bruce 060705 use new common code, if it works
        from widgets.widget_controllers import realtime_update_controller
        self.ruc = realtime_update_controller( 
            #( self.update_btngrp, self.update_number_spinbox, self.update_units_combobox ),
            ( self.update_btngrp_group, self.update_number_spinbox, self.update_units_combobox ),
            self.watch_minimization_checkbox,
            Minimize_watchRealtimeMinimization_prefs_key
        )
        ## can't do this yet: self.ruc.set_widgets_from_update_data( self.previous_movie._update_data ) # includes checkbox
        # for A8, only the checkbox will be persistent; the others will be sticky only because the dialog is not remade at runtime
        return

    def setup(self):
        """
        Setup and show the Minimize Energy dialog.
        """
        # Get widget parameters, update widgets, save previous parameters (for Restore Defaults) and show dialog.

        # set up default & enabled choices for Minimize Selection vs. Min All
        # (details revised to fix nfr bug 2848, item 1, bruce 080513;
        #  prior code used selection nonempty to determine default seltype)
        selection = self.win.assy.selection_from_glpane()
            # a compact rep of the currently selected subset of the Part's stuff
        if selection.nonempty():
            ## self.seltype = 'Sel'
            self.seltype = 'All'
            self.minimize_selection_enabled = True
        else:
            self.seltype = 'All'
            self.minimize_selection_enabled = False
        self.update_widgets() # only the convergence criteria, for A8, plus All/Sel command from self.seltype
        self.previousParams = self.gather_parameters() # only used in case Cancel wants to restore them; only conv crit for A8
        self.show()
           
    def gather_parameters(self): ###e should perhaps include update_data from ruc (not sure it's good) -- but no time for A8
        """
        Returns a tuple with the current parameter values from the widgets. Also sets those in env.prefs.
        Doesn't do anything about self.seltype, since that is a choice of command, not a parameter for a command.
        """
        self.change_endrms('notused')
        self.change_endmax('notused')
        self.change_cutoverrms('notused')
        self.change_cutovermax('notused')
        return tuple([env.prefs[key] for key in (endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key)])
    
    def update_widgets(self, update_seltype = True):
        """
        Update the widgets using the current env.prefs values and self attrs.
        """
        if update_seltype:
            if self.seltype == 'All':
                self.minimize_all_rbtn.setChecked(1)
            else:
                # note: this case might no longer ever happen after today's
                # change, but I'm not sure. Doesn't matter. [bruce 080513]
                self.minimize_sel_rbtn.setChecked(1)
            self.minimize_sel_rbtn.setEnabled( self.minimize_selection_enabled)
            pass

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
        """
        Slot for OK button
        """
        QDialog.accept(self)
        if env.debug():
            print "ok"
        self.gather_parameters()
        ### kluge: has side effect on env.prefs
        # (should we pass these as arg to Minimize_CommandRun rather than thru env.prefs??)
        if debug_flags.atom_debug:
            print "debug: reloading runSim & sim_commandruns on each use, for development"
            import simulation.runSim as runSim
            reload_once_per_event(runSim)
                # bug: only works some of the times runSim.py is modified,
                # don't know why; might be that sim_commandruns.py
                # also needs to be modified, but touching them both
                # doesn't seem to work consistently either.
                # [bruce 080520]
            import simulation.sim_commandruns as sim_commandruns
            reload_once_per_event(sim_commandruns)
        from simulation.sim_commandruns import Minimize_CommandRun
        # do this in gather?
        if self.minimize_all_rbtn.isChecked():
            self.seltype = 'All'
            seltype_name = "All"
        else:
            self.seltype = 'Sel'
            seltype_name = "Selection"
        self.win.assy.current_command_info(cmdname = self.plain_cmdname + " (%s)" % seltype_name) # cmdname for Undo
    
        update_cond = self.ruc.get_update_cond_from_widgets()
        engine = self.minimize_engine_combobox.currentIndex()
        env.prefs[Minimize_minimizationEngine_prefs_key] = engine
        cmdrun = Minimize_CommandRun( self.win, self.seltype, type = 'Minimize', update_cond = update_cond, engine = engine)
        cmdrun.run()
        return
        
    def cancel_btn_clicked(self):
        """
        Slot for Cancel button
        """
        if env.debug():
            print "cancel"
        # restore values we grabbed on entry.
        for key,val in zip((endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key), self.previousParams):
            env.prefs[key] = val
        self.update_widgets(update_seltype = False) #k might not matter since we're about to hide it, but can't hurt
        QDialog.reject(self)
        return
        
    def restore_defaults_btn_clicked(self):
        """
        Slot for Restore Defaults button
        """
        # restore factory defaults # for A8, only for conv crit, not for watch motion settings
        env.prefs.restore_defaults([endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key])
        self.update_widgets(update_seltype = False)
        
    def whatsthis_btn_clicked(self):
        """
        Slot for the What's This button
        """
        QWhatsThis.enterWhatsThisMode()
        
    # Property Manager groupbox button slots

    def toggle_grpbtn_1(self):
        """
        Slot for first groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_1, self.line1,
                            self.minimize_all_rbtn, self.minimize_sel_rbtn)

    def toggle_grpbtn_2(self):
        """
        Slot for second groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_2, self.line2,
                            self.watch_minimization_checkbox, self.update_btngrp)
        
    def toggle_grpbtn_3(self):
        """
        Slot for third groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_3, self.line3,
                            self.endrms_lbl, self.endrms_linedit,
                            self.endmax_lbl, self.endmax_linedit,
                            self.cutoverrms_lbl, self.cutoverrms_linedit,
                            self.cutovermax_lbl, self.cutovermax_linedit,
                            ##self.spacer_3 - had to be set to 1 pixel in ui file, since it's a local var, not a self attr
                            )

    def toggle_grpbtn_4(self):
        """
        Slot for fourth groupbox toggle button
        """
        self.toggle_groupbox_in_dialogs(self.grpbtn_4, self.line4,
                            self.minimize_engine_combobox)

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
