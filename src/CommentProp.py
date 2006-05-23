# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
$Id$

History:

060520 mark: New feature for Alpha 8. Stores a comment in the MMP file, accessible from the Model Tree as a node.

060522 bruce: minor changes, including changing representation of comment's text.

"""

__author__ = "Mark"

from qt import QDialog, QTextEdit
from CommentPropDialog import CommentPropDialog
import time

class CommentProp(CommentPropDialog):
    '''The Comment dialog allows the user to add a comment to the Model Tree, which
    is saved in the MMP file.
    '''
    
    def setup(self, comment):
        '''Show Comment dialog. 
        <comment> - the comment node object.
        '''
        self.comment = comment

#bruce 060522 removed this (not used, no longer correct)
##        if self.comment.text:
##            self.new_comment=False
##        else:
##            self.new_comment=True
            
        self.comment_textedit.setText(self.comment.get_text()) 
            # Load comment text.
        self.comment_textedit.moveCursor(QTextEdit.MoveEnd, False)
            # Sets cursor position to the end of the textedit document.
        
        QDialog.exec_loop(self)

    ###### Private methods ###############################
    
    def insert_date_time_stamp(self):
        ''' Inserts a date/time stamp in the comment at the current position.
        '''
        timestr = "%s " % time.strftime("%m/%d/%Y %I:%M %p")
        self.comment_textedit.insert(timestr)
    
    #################
    # Cancel Button
    #################
    def reject(self):
        QDialog.reject(self)

    #################
    # OK Button
    #################
    def accept(self):
        ## self.comment.text = self.comment_textedit.text()
        self.comment.set_text(self.comment_textedit.text())
        QDialog.accept(self)

    pass

# end
