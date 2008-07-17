# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
CommentProp.py - 

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

060520 mark: New feature for Alpha 8. Stores a comment in the MMP file,
accessible from the Model Tree as a node.

060522 bruce: minor changes, including changing representation of comment text.

080717 bruce, revise for coding standards
"""

from PyQt4.Qt import QDialog, QTextEdit, SIGNAL
from model.Comment import Comment
from commands.CommentProperties.CommentPropDialog import Ui_CommentPropDialog
import time
import foundation.env as env
from utilities.Log import redmsg, orangemsg, greenmsg, quote_html
from utilities.qt4transition import qt4todo
from utilities.debug import print_compact_traceback

cmd = greenmsg("Insert Comment: ") # TODO: rename this global

class CommentProp(QDialog, Ui_CommentPropDialog):
    """
    The Comment dialog allows the user to add a comment to the Model Tree, which
    is saved in the MMP file.
    """
    def __init__(self, win):
        QDialog.__init__(self, win) # win is parent.
        self.setupUi(self)
        self.win = win
        self.comment = None
        self.action = None
            # REVIEW, re self.action:
            # - if used only in messages (true in this file, but not yet
            #   analyzed re external files), should change initial value to "".
            # - if not used in external files, should make private.
            # [bruce 080717 comment]
    
    def setup(self, comment = None):
        """
        Show Comment dialog with current Comment text, for editing
        properties of an existing Comment node or creating a new one.
        
        @param comment: the comment node to edit, or None to create a new one.
        """
        self.comment = comment
        
        if self.comment:
            self.comment_textedit.setPlainText(self.comment.get_text())
                # Load comment text.
            qt4todo("self.comment_textedit.moveCursor(QTextEdit.MoveEnd, False)")
                # Sets cursor position to the end of the textedit document.
        
        QDialog.exec_(self)

    ###### Private methods ###############################
    
    def _create_comment(self):
        comment_text = self.comment_textedit.toPlainText()
        if not self.comment:
            self.comment = Comment(self.win.assy, None, comment_text)
            self.win.assy.addnode(self.comment)
            self.action = 'added'
        else: 
            self.comment.set_text(comment_text)
            self.action = 'updated'
            
    def _remove_comment(self):
        if self.comment:
            self.comment.kill()
            self.win.mt.mt_update()
            self.comment = None
            
    def insert_date_time_stamp(self):
        """
        Insert a date/time stamp in the comment at the current position.

        @note: slot method for self.date_time_btn, SIGNAL("clicked()").
        """
        timestr = "%s " % time.strftime("%m/%d/%Y %I:%M %p")
        self.comment_textedit.insertPlainText(timestr)
        
    def _done_history_msg(self):
        env.history.message(cmd + quote_html("%s %s." % (self.comment.name, self.action)))
                #bruce Qt4 070502 precaution: use quote_html
    
    #################
    # Cancel Button
    #################
    def reject(self):
        QDialog.reject(self)
        self.comment = None
        self.comment_textedit.setPlainText("") # Clear text.

    #################
    # OK Button
    #################
    def accept(self):
        """
        Slot for the OK button
        """
        try:
            self._create_comment()
            self._done_history_msg()
            self.comment = None
        except Exception, e:
            print_compact_traceback("Bug: exception in CommentProp.accept: ") #bruce Qt4 070502
            env.history.message(cmd + redmsg("Bug: " + quote_html(" - ".join(map(str, e.args)))))
                #bruce Qt4 070502 bugfixes: use quote_html, say it's a bug (could say "internal error" if desired)
            self._remove_comment()
        self.win.mt.mt_update()
        QDialog.accept(self)
        self.comment_textedit.setPlainText("") # Clear text.

    pass # end of class CommentProp

# end
