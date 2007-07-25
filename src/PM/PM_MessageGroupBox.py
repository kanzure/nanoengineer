# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_MessageGroupBox.py

The PM_MessageGroupBox widget provides a message group box with a 
collapse/expand button and a title.

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrMessageGroupBox out of PropMgrBaseClass.py 
                 into this file and renamed it PM_MessageGroupBox.
"""

from PM_Constants import pmMsgGrpBoxMargin
from PM_Constants import pmMsgGrpBoxSpacing

from PyQt4.Qt import QTextOption
from PyQt4.Qt import QSizePolicy

from PM_GroupBox    import PM_GroupBox
from PM_TextEdit    import PM_TextEdit
from PM_WidgetMixin import PM_WidgetMixin

class PM_MessageGroupBox( PM_GroupBox, PM_WidgetMixin ):
    """
    The PM_MessageGroupBox widget provides a message box with a 
    collapse/expand button and a title.
    """

    expanded      = True # Set to False when groupbox is collapsed.
    _widgetList   = []   # All widgets in the groupbox (except the title button).
    _rowCount     = 0    # Number of rows in the groupbox.
    
    def __init__( self, 
                  parentWidget, 
                  title ):
        """
        PM_MessageGroupBox constructor.
        
        @param parentWidget: the PM_Dialog containing this message groupbox.
        @type  parentWidget: PM_Dialog
        
        @param title: the title on the collapse button
        @type  title: str
        """
        PM_GroupBox.__init__(self, parentWidget, title, addTitleButton = True)
                
        self._widgetList = []
        
        self.VBoxLayout.setMargin(pmMsgGrpBoxMargin)
        self.VBoxLayout.setSpacing(pmMsgGrpBoxSpacing)
        
        self.GridLayout.setMargin(0)
        self.GridLayout.setSpacing(0)
        
        self.MessageTextEdit = PM_TextEdit(self, label='', spanWidth=True)
        
        # wrapWrapMode seems to be set to QTextOption.WrapAnywhere on MacOS,
        # so let's force it here. Mark 2007-05-22.
        self.MessageTextEdit.setWordWrapMode(QTextOption.WordWrap)
        
        parentWidget.MessageTextEdit = self.MessageTextEdit
        
        # These two policies very important. Mark 2007-05-22
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self.MessageTextEdit.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self.setWhatsThis("""<b>Messages</b>
            <p>This prompts the user for a requisite operation and/or displays 
            helpful messages to the user.</p>""")

        # Hide until insertHtmlMessage() loads a message.
        self.hide()
        
    def insertHtmlMessage( self, 
                           text, 
                           setAsDefault = False, 
                           minLines     = 4, 
                           maxLines     = 10, 
                           replace      = True ):
        """
        Insert text (HTML) into the message box. Displays the message box if it is hidden.
        
        Arguments:
        
        @param minLines: the minimum number of lines (of text) to display in the TextEdit.
            if <minLines>=0 the TextEdit will fit its own height to fit <text>. The
            default height is 4 (lines of text).
        @type  minLines: int
        
        @param maxLines: The maximum number of lines to display in the TextEdit widget.
        @type  maxLines: int
        
        @param replace: should be set to False if you do not wish to replace 
            the current text. It will append <text> instead.
        @type  replace: int

        @note: Displays the message box if it is hidden.
        """
        self.MessageTextEdit.insertHtml( text, 
                                         setAsDefault, 
                                         minLines = minLines, 
                                         maxLines = maxLines, 
                                         replace  = True )
        self.show()
        
# End of PM_MessageGroupBox ############################