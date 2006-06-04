# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
$Id$

History:

060520 mark: New feature for Alpha 8. Stores a comment in the MMP file, accessible from the Model Tree as a node.

060522 bruce: minor changes, including changing representation of comment's text.

"""

__author__ = "Mark"

from qt import QDialog, QTextEdit
from Comment import Comment
from CommentPropDialog import CommentPropDialog
import time
import env
from HistoryWidget import redmsg, orangemsg, greenmsg

cmd = greenmsg("Insert Comment: ")

class CommentProp(CommentPropDialog):
    '''The Comment dialog allows the user to add a comment to the Model Tree, which
    is saved in the MMP file.
    '''
    def __init__(self, win):
        CommentPropDialog.__init__(self, win) # win is parent.
        self.win = win
        self.comment = None
        self.action = None
    
    def setup(self, comment=None):
        '''Show Comment dialog with currect comment text. 
        <comment> - the comment node object.
        '''
        self.comment = comment
        
        if self.comment:
            self.comment_textedit.setText(self.comment.get_text())
                # Load comment text.
            self.comment_textedit.moveCursor(QTextEdit.MoveEnd, False)
                # Sets cursor position to the end of the textedit document.
        
        QDialog.exec_loop(self)

    ###### Private methods ###############################
    
    def create_comment(self):
        '''Create comment'''
        comment_text = self.comment_textedit.text()
        
        if not self.comment:
            self.comment = Comment(self.win.assy, None, comment_text)
            self.win.assy.addnode(self.comment)
            self.action = 'added'
        else: 
            self.comment.set_text(comment_text)
            self.action = 'updated'
            
    def remove_comment(self):
        '''Removes comment'''
        if self.comment:
            self.comment.kill()
            self.win.mt.mt_update()
            self.comment = None
            
    def insert_date_time_stamp(self):
        ''' Inserts a date/time stamp in the comment at the current position.
        '''
        timestr = "%s " % time.strftime("%m/%d/%Y %I:%M %p")
        self.comment_textedit.insert(timestr)
        
    def done_history_msg(self):
        env.history.message(cmd + "%s %s." % (self.comment.name, self.action))
    
    #################
    # Cancel Button
    #################
    def reject(self):
        QDialog.reject(self)
        self.comment = None
        self.comment_textedit.setText('') # Clear text.

    #################
    # OK Button
    #################
    def accept(self):
        'Slot for the OK button'
        try:
            self.create_comment()
            self.done_history_msg()
            self.comment = None
        except Exception, e:
            env.history.message(cmd + redmsg(" - ".join(map(str, e.args))))
            self.remove_comment()
        self.win.mt.mt_update()
        QDialog.accept(self)
        self.comment_textedit.setText('') # Clear text.

# end of class Comment
