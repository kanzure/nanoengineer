# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
MinimizeEnergyProp.py - the MinimizeEnergyProp class, including all methods needed by the Minimize Energy dialog.

$Id$

History:

mark 060705 - Created for Alpha 8 NFR: "Simulator > Minimize Energy".
'''
__author__ = "Mark"

from qt import *
from HistoryWidget import greenmsg
from MinimizeEnergyPropDialog import MinimizeEnergyPropDialog
from GeneratorBaseClass import GroupButtonMixin
from Sponsors import SponsorableMixin

class MinimizeEnergyProp(SponsorableMixin, GroupButtonMixin, MinimizeEnergyPropDialog):

    cmdname = greenmsg("Minimize Energy: ")
    sponsor_keyword = None

    def __init__(self, win):
        MinimizeEnergyPropDialog.__init__(self, win)  # win is parent.
        self.win = win
        self.previousParams = None
        
    def setup(self):
        '''Show the Minimize Energy dialog.
        '''
        # Get widget parameters, update widgets, save previous parameters (for Restore Defaults) and show dialog.
        self.update_widgets()
        self.previousParams = self.gather_parameters()
        self.show()
           
    def gather_parameters(self):
        'Returns a tuple with the current parameter values from the widgets.'
        return
    
    def update_widgets(self):
        'Update the widgets using the current attr values.'
        return
        
    def ok_btn_clicked(self):
        'Slot for OK button.'
        QDialog.accept(self)
        
    def cancel_btn_clicked(self):
        'Slot for Cancel button.'
        QDialog.reject(self)
        
    def restore_defaults_btn_clicked(self):
        'Slot for Restore Defaults button.'
        # p1, p2, p3, ... pn = self.previousParams
        self.update_widgets()
        
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
                            self.spacer_3)
