# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
GeneratorBaseClass.py

$Id$

There is some logic associated with Preview/OK/Abort that's complicated enough
to put it in one place, so that individual generators can focus on what they
need to do. As much as possible, the individual generator should not need to
worry about the GUI.
"""

import env
from qt import Qt, QApplication, QCursor, QDialog, QImage, QPixmap
from Sponsors import findSponsor
from HistoryWidget import redmsg, orangemsg, greenmsg

__author__ = "Will"

DEBUG = False

class GeneratorBaseClass:

    sponsor_keyword = None

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        self.win = win
        self.group = None
        self.previousParams = None
        assert self.sponsor_keyword != None
        self.sponsor = sponsor = findSponsor(self.sponsor_keyword)
        sponsor.configureSponsorButton(self.sponsor_btn)

    def build_struct(self):
        '''Build the structure in question. This is an abstract
        method and must be overloaded in the specific generator.
        The return value should
        '''
        raise Exception("Not implemented in the base class")

    def remove_struct(self):
        if self.group != None:
            part = self.win.assy.part
            part.ensure_toplevel_group()
            part.topnode.delmember(self.group)
            self.win.win_update()
            self.win.mt.mt_update()
            self.group = None

    def preview_btn_clicked(self):
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self._build_struct()
        except Exception, e:
            env.history.message(self.cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
            if DEBUG: raise
        QApplication.restoreOverrideCursor() # Restore the cursor
        self.win.win_update()
        self.win.mt.mt_update()

    def gather_parameters(self):
        '''Return a tuple of the current parameters'''
        raise Exception("Not implemented in the base class")

    def done_msg(self):
        raise Exception("Not implemented in the base class")

    def _build_struct(self):
        params = self.gather_parameters()
        if params != self.previousParams:
            self.remove_struct()
            self.previousParams = params
        self.group = grp = self.build_struct(params)
        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(grp)
        self.win.win_update()
        self.win.mt.mt_update()

    def ok_btn_clicked(self):
        'Slot for the OK button'
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self._build_struct()
            env.history.message(self.cmd + self.done_msg())
            self.group = None
        except Exception, e:
            env.history.message(self.cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
            if DEBUG: raise
        QApplication.restoreOverrideCursor() # Restore the cursor
        QDialog.accept(self)

    def done_btn_clicked(self):
        self.ok_btn_clicked()

    def abort_btn_clicked(self):
        self.cancel_btn_clicked()

    def cancel_btn_clicked(self):
        'Slot for the OK button'
        self.remove_struct()
        QDialog.accept(self)

    def close(self, e=None):
        """When the user closes dialog by clicking the 'X' button on
        the dialog title bar, this method is called.
        """
        try:
            self.cancel_btn_clicked()
            return True
        except:
            return False

    def open_sponsor_homepage(self):
        self.sponsor.wikiHelp()

    def enter_WhatsThisMode(self):
        env.history.message(orangemsg('WhatsThis: Not implemented yet'))
