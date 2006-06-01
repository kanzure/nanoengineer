# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
GeneratorBaseClass.py

$Id$
"""

import platform
import env
from qt import Qt, QApplication, QCursor, QDialog, QImage, QPixmap
from Sponsors import findSponsor
from HistoryWidget import redmsg, orangemsg, greenmsg

__author__ = "Will"

class AbstractMethod(Exception):
    def __init__(self):
        Exception.__init__(self, 'Abstract method - must be overloaded')

class GeneratorBaseClass:
    """There is some logic associated with Preview/OK/Abort that's
    complicated enough to put it in one place, so that individual
    generators can focus on what they need to do. As much as possible,
    the individual generator should not need to worry about the GUI.
    """

    sponsor_keyword = None

    # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        self.win = win
        self.struct = None
        self.previousParams = None
        assert self.sponsor_keyword != None
        self.sponsor = sponsor = findSponsor(self.sponsor_keyword)
        sponsor.configureSponsorButton(self.sponsor_btn)

    def build_struct(self):
        '''Build the structure in question. This is an abstract method
        and must be overloaded in the specific generator. The return
        value should be the structure, i.e. some flavor of a Node.
        '''
        raise AbstractMethod()

    def remove_struct(self):
        if self.struct != None:
            self.struct.kill()
            self.struct = None
            self.win.win_update()
            self.win.mt.mt_update()

    def preview_btn_clicked(self):
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self._build_struct()
        except Exception, e:
            env.history.message(self.cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
            if platform.atom_debug: raise
        QApplication.restoreOverrideCursor() # Restore the cursor
        self.win.win_update()
        self.win.mt.mt_update()

    def gather_parameters(self):
        '''Return a tuple of the current parameters. This is an
        abstract method and must be overloaded in the specific
        generator.'''
        raise AbstractMethod()

    def done_msg(self):
        '''Tell what message to print when the structure has been
        built. This is an abstract method and must be overloaded in
        the specific generator.
        '''
        raise AbstractMethod()

    def _build_struct(self):
        params = self.gather_parameters()
        if params != self.previousParams:
            self.remove_struct()
            self.previousParams = params
        self.struct = struct = self.build_struct(params)
        part = self.win.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(struct)
        self.win.win_update()
        self.win.mt.mt_update()

    def ok_btn_clicked(self):
        'Slot for the OK button'
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        try:
            self._build_struct()
            env.history.message(self.cmd + self.done_msg())
            self.struct = None
        except Exception, e:
            env.history.message(self.cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_struct()
            if platform.atom_debug: raise
        QApplication.restoreOverrideCursor() # Restore the cursor
        QDialog.accept(self)

    def done_btn_clicked(self):
        'Slot for the Done button'
        self.ok_btn_clicked()

    def abort_btn_clicked(self):
        'Slot for the Abort button'
        self.cancel_btn_clicked()

    def cancel_btn_clicked(self):
        'Slot for the Cancel button'
        self.remove_struct()
        QDialog.accept(self)

    def close(self, e=None):
        """When the user closes the dialog by clicking the 'X' button
        on the dialog title bar, do whatever the cancel button does.
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
