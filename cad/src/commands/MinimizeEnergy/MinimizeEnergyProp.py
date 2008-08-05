# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
MinimizeEnergyProp.py - the MinimizeEnergyProp class, including all
methods needed by the Minimize Energy dialog.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

mark 060705 - Created for Alpha 8 NFR: "Simulator > Minimize Energy".

To do:
- implement/enforce constrains between all convergence values.
"""

from PyQt4.Qt import QDialog
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QAbstractButton
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QWhatsThis
from PyQt4.Qt import QSize

from utilities.Log import greenmsg, redmsg, orangemsg, _graymsg, quote_html
from commands.MinimizeEnergy.MinimizeEnergyPropDialog import Ui_MinimizeEnergyPropDialog
from PM.GroupButtonMixin import GroupButtonMixin
#@from sponsors.Sponsors import SponsorableMixin
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

#class MinimizeEnergyProp(QDialog, SponsorableMixin, GroupButtonMixin, Ui_MinimizeEnergyPropDialog):
class MinimizeEnergyProp(QDialog, Ui_MinimizeEnergyPropDialog):

    cmdname = greenmsg("Minimize Energy: ") # WARNING: self.cmdname might be used by one of the superclasses
    plain_cmdname = "Minimize Energy"

    def __init__(self, win):
        QDialog.__init__(self, win)  # win is parent.
        self.setupUi(self)
        self.watch_motion_buttongroup = QButtonGroup()
        self.watch_motion_buttongroup.setExclusive(True)
        for obj in self.watch_motion_groupbox.children():
            if isinstance(obj, QAbstractButton):
                self.watch_motion_buttongroup.addButton(obj)

        #fix some icon problems
        self.setWindowIcon(
            geticon('ui/border/MinimizeEnergy.png'))

        self.connect(self.cancel_btn,
                     SIGNAL("clicked()"),
                     self.cancel_btn_clicked)
        self.connect(self.ok_btn,
                     SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.connect(self.restore_btn,
                     SIGNAL("clicked()"),
                     self.restore_defaults_btn_clicked)

        self.whatsthis_btn.setIcon(
            geticon('ui/actions/Properties Manager/WhatsThis.png'))
        self.whatsthis_btn.setIconSize(QSize(22, 22))
        self.whatsthis_btn.setToolTip('Enter "What\'s This?" help mode')

        self.connect(self.whatsthis_btn,
                     SIGNAL("clicked()"),
                     QWhatsThis.enterWhatsThisMode)

        connect_checkbox_with_boolean_pref(
            self.electrostaticsForDnaDuringMinimize_checkBox,
            electrostaticsForDnaDuringMinimize_prefs_key)

        connect_checkbox_with_boolean_pref(
            self.enableNeighborSearching_check_box,
            neighborSearchingInGromacs_prefs_key)

        self.connect(self.minimize_engine_combobox, SIGNAL("activated(int)"), self.update_minimize_engine)

        self.minimize_engine_combobox.setCurrentIndex(
            env.prefs[Minimize_minimizationEngine_prefs_key])

        self.connect(self.endRmsDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeEndRms)
        self.connect(self.endMaxDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeEndMax)
        self.connect(self.cutoverRmsDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeCutoverRms)
        self.connect(self.cutoverMaxDoubleSpinBox, SIGNAL("valueChanged(double)"), self.changeCutoverMax)

        self.endRmsDoubleSpinBox.setSpecialValueText("Automatic")
        self.endMaxDoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverRmsDoubleSpinBox.setSpecialValueText("Automatic")
        self.cutoverMaxDoubleSpinBox.setSpecialValueText("Automatic")

        self.win = win
        self.previousParams = None
        self.setup_ruc()
        self.seltype = 'All'
        self.minimize_selection_enabled = True #bruce 080513

        # Assign "What's This" text for all widgets.
        from commands.MinimizeEnergy.WhatsThisText_for_MinimizeEnergyDialog import whatsThis_MinimizeEnergyDialog
        whatsThis_MinimizeEnergyDialog(self)

        self.update_widgets() # to make sure self attrs are set
        return

    def setup_ruc(self):
        """
        #doc
        """
        #bruce 060705 use new common code, if it works
        from widgets.widget_controllers import realtime_update_controller
        self.ruc = realtime_update_controller(
            #( self.update_btngrp, self.update_number_spinbox, self.update_units_combobox ),
            ( self.watch_motion_buttongroup, self.update_number_spinbox, self.update_units_combobox ),
            self.watch_motion_groupbox,
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
        self.exec_() # Show dialog as a modal dialog.
        return

    def gather_parameters(self): ###e should perhaps include update_data from ruc (not sure it's good) -- but no time for A8
        """
        Returns a tuple with the current parameter values from the widgets. Also sets those in env.prefs.
        Doesn't do anything about self.seltype, since that is a choice of command, not a parameter for a command.
        """
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

        # Convergence Criteria groupbox
        # WARNING: some of the following code is mostly duplicated by Preferences code
        self.endrms = get_pref_or_optval(endRMS_prefs_key, -1.0, 0.0)
        self.endRmsDoubleSpinBox.setValue(self.endrms)

        self.endmax = get_pref_or_optval(endMax_prefs_key, -1.0, 0.0)
        self.endMaxDoubleSpinBox.setValue(self.endmax)

        self.cutoverrms = get_pref_or_optval(cutoverRMS_prefs_key, -1.0, 0.0)
        self.cutoverRmsDoubleSpinBox.setValue(self.cutoverrms)

        self.cutovermax = get_pref_or_optval(cutoverMax_prefs_key, -1.0, 0.0)
        self.cutoverMaxDoubleSpinBox.setValue(self.cutovermax)

        self.update_minimize_engine()

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
        self.minimize_engine_combobox.setCurrentIndex(0) # ND1
        env.prefs.restore_defaults([endRMS_prefs_key, endMax_prefs_key, cutoverRMS_prefs_key, cutoverMax_prefs_key])
        self.update_widgets(update_seltype = False)
        return
    # Dialog slots

    def update_minimize_engine(self, ignoredIndex = 0):
        """
        Slot for the Minimize Engine comobox.
        """

        engineIndex = self.minimize_engine_combobox.currentIndex()

        if engineIndex == 0: # NanoDynamics-1

            # Minimize options widgets.
            self.electrostaticsForDnaDuringMinimize_checkBox.setEnabled(False)
            self.enableNeighborSearching_check_box.setEnabled(False)

            # Watch minimize in real time widgets.
            self.watch_motion_groupbox.setEnabled(True)

            # Converence criteria widgets
            self.endMaxDoubleSpinBox.setEnabled(True)
            self.cutoverRmsDoubleSpinBox.setEnabled(True)
            self.cutoverMaxDoubleSpinBox.setEnabled(True)
        else: # GROMACS

            # Minimize options widgets.
            self.electrostaticsForDnaDuringMinimize_checkBox.setEnabled(True)
            self.enableNeighborSearching_check_box.setEnabled(True)

            # Watch minimize in real time widgets.
            self.watch_motion_groupbox.setEnabled(False)

            # Converence criteria widgets
            self.endMaxDoubleSpinBox.setEnabled(False)
            self.cutoverRmsDoubleSpinBox.setEnabled(False)
            self.cutoverMaxDoubleSpinBox.setEnabled(False)
        return

    def changeEndRms(self, endRms):
        """
        Slot for EndRMS.
        """
        if endRms:
            env.prefs[endRMS_prefs_key] = endRms
        else:
            env.prefs[endRMS_prefs_key] = -1.0
        return

    def changeEndMax(self, endMax):
        """
        Slot for EndMax.
        """
        if endMax:
            env.prefs[endMax_prefs_key] = endMax
        else:
            env.prefs[endMax_prefs_key] = -1.0
        return

    def changeCutoverRms(self, cutoverRms):
        """
        Slot for CutoverRMS.
        """
        if cutoverRms:
            env.prefs[cutoverRMS_prefs_key] = cutoverRms
        else:
            env.prefs[cutoverRMS_prefs_key] = -1.0
        return

    def changeCutoverMax(self, cutoverMax):
        """
        Slot for CutoverMax.
        """
        if cutoverMax:
            env.prefs[cutoverMax_prefs_key] = cutoverMax
        else:
            env.prefs[cutoverMax_prefs_key] = -1.0
        return

    pass # end of class MinimizeEnergyProp

# end
