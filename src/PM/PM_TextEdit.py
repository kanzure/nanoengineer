# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_TextEdit.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrTextEdit out of PropMgrBaseClass.py into this file
                 and renamed it PM_TextEdit.
"""

from PM_Constants import pmMinWidth
from PM_Colors    import pmMessageBoxColor

from PyQt4.Qt import Qt
from PyQt4.Qt import QSize
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QTextCursor
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QPalette

from PM_WidgetMixin import PM_WidgetMixin

class PM_TextEdit( QTextEdit, PM_WidgetMixin ):
    """
    The PM_TextEdit widget provides a QTextEdit with a 
    QLabel for a Property Manager groupbox.
    """
    
    defaultText = '' # Default text.
    
    def __init__( self, 
                  parentWidget, 
                  label     = '', 
                  spanWidth = False ):
        """
        Appends a QTextEdit widget (with a QLabel widget) to <parentWidget>, 
        a property manager groupbox.
        
        The QTextEdit is empty (has no text) by default. Use insertHtml() 
        to insert HTML text into the TextEdit.        
        
        Arguments:
        
        @param parentWidget: the parent groupbox containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: label that appears to the left (or above) of the TextEdit.
        @type  label: str
        
        @param spanWidth: if True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool
        
        """
        
        if 0: # Debugging code
            print "QTextEdit.__init__():"
            print "  label=", label
            print "  spanWidth=",spanWidth
        
        QTextEdit.__init__(self)
        
        self.parentWidget = parentWidget
        
        self._setHeight() # Default height is 4 lines high.
        
        # Needed for Intel MacOS. Otherwise, the horizontal scrollbar
        # is displayed in the MessageGroupBox. Mark 2007-05-24.
        # Shouldn't be needed with _setHeight().
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        from PM_MessageGroupBox import PM_MessageGroupBox
        if isinstance(parentWidget, PM_MessageGroupBox):
            # Add to parentWidget's VBoxLayout if <parentWidget> is a MessageGroupBox.
            parentWidget.VBoxLayout.addWidget(self)
            # We should be calling the propmgr's getMessageTextEditPalette() method,
            # but that will take some extra work which I will do soon. Mark 2007-06-21
            self.setPalette(self._getPalette())
            self.setReadOnly(True)
            self.labelWidget = None # Never has one. Mark 2007-05-31
            parentWidget._widgetList.append(self)
            parentWidget._rowCount += 1
            self.setName()
        else:
            self.addWidgetAndLabelToParent(parentWidget, label, spanWidth)
        
    def insertHtml( self, 
                    text, 
                    setAsDefault = False, 
                    minLines     = 4, 
                    maxLines     = 6, 
                    replace      = True ):
        """
        Insert <text> (HTML) into the Prop Mgr's message groupbox.
        <minLines> is the minimum number of lines to
        display, even if the text takes up fewer lines. The default
        number of lines is 4.
        <maxLines> is the maximum number of lines to
        diplay before adding a vertical scrollbar.
        <replace> should be set to False if you do not wish
        to replace the current text. It will append <text> instead.
        """
        if setAsDefault:
            self.defaultText = text
            self.setAsDefault = True
    
        if replace:
            # Replace the text by selecting effectively all text and
            # insert the new text 'over' it (overwrite). :jbirac: 20070629
            cursor  =  self.textCursor()
            cursor.setPosition( 0, 
                                QTextCursor.MoveAnchor )
            cursor.setPosition( len(self.toPlainText()), 
                                QTextCursor.KeepAnchor )
            self.setTextCursor( cursor )
        
        QTextEdit.insertHtml(self, text)

        if replace:
            # Restore the previous cursor position/selection and mode.
            cursor.setPosition( len(self.toPlainText()), 
                                QTextCursor.MoveAnchor )
            self.setTextCursor( cursor )
            
        self._setHeight(minLines, maxLines)
        
    def _setHeight( self, 
                    minLines = 4, 
                    maxLines = 8 ):
        """
        Set the height just high enough to display
        the current text without a vertical scrollbar.
        <minLines> is the minimum number of lines to
        display, even if the text takes up fewer lines.
        <maxLines> is the maximum number of lines to
        diplay before adding a vertical scrollbar.
        """
        
        if minLines == 0:
            fitToHeight=True
        else:
            fitToHeight=False
        
        # Current width of PM_TextEdit widget.
        current_width = self.sizeHint().width()
        
        # Probably including Html tags.
        text = self.toPlainText()
        text_width = self.fontMetrics().width(text)
        
        num_lines = text_width/current_width + 1
            # + 1 may create an extra (empty) line on rare occasions.
                        
        if fitToHeight:
            num_lines = min(num_lines, maxLines)
                
        else:
            num_lines = max(num_lines, minLines)

        #margin = self.fontMetrics().leading() * 2 # leading() returned 0. Mark 2007-05-28
        margin = 10 # Based on trial and error. Maybe it is pm?Spacing=5 (*2)? Mark 2007-05-28
        new_height = num_lines * self.fontMetrics().lineSpacing() + margin
        
        if 0: # Debugging code for me. Mark 2007-05-24
            print "--------------------------------"
            print "Widget name = ", self.objectName()
            print "minLines =" , minLines
            print "maxLines = ", maxLines
            print "num_lines = ", num_lines
            print "New height = ", new_height
            print "text = ", text   
            print "Text width = ", text_width
            print "current_width (of PM_TextEdit)=", current_width
        
        # Reset height of PM_TextEdit.
        self.setMinimumSize(QSize(pmMinWidth * 0.5, new_height))
        self.setMaximumHeight(new_height)
    
    def restoreDefault( self ):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.insertHtml(self.defaultText, 
                            setAsDefault = True,
                            replace = True)
            
    def _getPalette( self ):
        """
        Return a palette with a yellow base. 
        """
        return self.getPalette(None, 
                               QPalette.Base,
                               pmMessageBoxColor)

# End of PM_TextEdit ############################