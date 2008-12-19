# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_TextEdit.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrTextEdit out of PropMgrBaseClass.py into this
file and renamed it PM_TextEdit.
"""

from PM.PM_Constants import PM_MINIMUM_WIDTH

##from PM.PM_Colors    import getPalette
##from PM.PM_Colors    import pmMessageBoxColor

from PyQt4.Qt import Qt
from PyQt4.Qt import QLabel
from PyQt4.Qt import QSize
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QTextCursor
from PyQt4.Qt import QTextEdit
##from PyQt4.Qt import QPalette
from PyQt4.Qt import QWidget
from PyQt4.Qt import QTextCharFormat
from PyQt4.Qt import SIGNAL

class PM_TextEdit( QTextEdit ):
    """
    The PM_TextEdit widget provides a QTextEdit with a 
    QLabel for a Property Manager groupbox.
    
    @cvar defaultText: The default text of the textedit.
    @type defaultText: str
    
    @cvar setAsDefault: Determines whether to reset the value of the
                        textedit to I{defaultText} when the user clicks
                        the "Restore Defaults" button.
    @type setAsDefault: bool

    @cvar labelWidget: The Qt label widget of this textedit.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    """
    
    defaultText  = ""
    setAsDefault = True
    labelWidget  = None
    
    def __init__(self, 
                 parentWidget, 
                 label       = '', 
                 labelColumn = 0,
                 spanWidth   = False,
                 addToParent = True,
                 permit_enter_keystroke = True
                 ):
        """
        Appends a QTextEdit (Qt) widget to the bottom of I{parentWidget}, 
        a Property Manager group box.
        
        The QTextEdit is empty (has no text) by default. Use insertHtml() 
        to insert HTML text into the TextEdit.        
        
        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox
        
        @param label: The label that appears to the left of (or above) the 
                      spin box. To suppress the label, set I{label} to an 
                      empty string.
        @type  label: str
        
        @param spanWidth: If True, the spin box and its label will span the width
                          of the group box. The label will appear directly above
                          the spin box and is left justified. 
        @type  spanWidth: bool
        
        @param addToParent: If True (the default), self will be added to
                            parentWidget by passing it to
                            parentWidget.addPmWidget. If False, self will not
                            be added to parentWidget. Typically, when this is
                            False, the caller will add self to parent in some
                            other way.
        @type  addToParent: bool
        
        @param permit_enter_keystroke: If set to True, this PM_textEdit can have multiple
                               lines. Otherwise, it will block the 'Enter' keypress
                               within the text editor. Note that caller needs 
                               to make sure that linewrapping option is 
                               appropriately set, (in addition to this flag)
                               so as to permit/ not permit multiple lines 
                               in the text edit.
                               
        
        @see: U{B{QTextEdit}<http://doc.trolltech.com/4/qtextedit.html>}
        """
        
        if 0: # Debugging code
            print "QTextEdit.__init__():"
            print "  label       =", label
            print "  labelColumn =", labelColumn
            print "  spanWidth   =", spanWidth
        
        QTextEdit.__init__(self)
        
        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.spanWidth    = spanWidth
        self._permit_enter_keystroke = permit_enter_keystroke
        
        if label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(label)
        
        self._setHeight() # Default height is 4 lines high.
        
        
        
##        from PM.PM_MessageGroupBox import PM_MessageGroupBox
##        if isinstance(parentWidget, PM_MessageGroupBox):
##            # Add to parentWidget's vBoxLayout if <parentWidget> is a MessageGroupBox.
##            parentWidget.vBoxLayout.addWidget(self)
##            # We should be calling the PM's getMessageTextEditPalette() method,
##            # but that will take some extra work which I will do soon. Mark 2007-06-21
##            self.setPalette(getPalette( None, 
##                                        QPalette.Base,
##                                        pmMessageBoxColor))
##            self.setReadOnly(True)
##            #@self.labelWidget = None # Never has one. Mark 2007-05-31
##            parentWidget._widgetList.append(self)
##            parentWidget._rowCount += 1
##        else:
##            parentWidget.addPmWidget(self)
        # bruce 071103 refactored the above into the new addToParent option and
        # code added to PM_MessageGroupBox.__init__ after it calls this method.
        
        if addToParent:
            parentWidget.addPmWidget(self)
        
       
        return
    
    def keyPressEvent(self, event):
        """
        Overrides the superclass method. 
        """
        #If user hits 'Enter' key (return key), don't do anything. 
        if event.key() == Qt.Key_Return:
            #Urmi 20080724: emit a signal to indicate end of processing
            self.emit(SIGNAL("editingFinished()"))
            #there is no obvious way to allow only a single line in a 
            #QTextEdit (we can use some methods that restrict the columnt width
            #, line wrapping etc but this is untested when the line contains 
            # huge umber of characters. Anyway, the following always works 
            #and fixes bug 2713
            if not self._permit_enter_keystroke:
                return  
            
        QTextEdit.keyPressEvent(self, event)
                
        
    def insertHtml(self, 
                   text, 
                   setAsDefault = False, 
                   minLines     = 4, 
                   maxLines     = 6, 
                   replace      = True
                   ):
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
        
              
        #Don't call _setHeight after insertHtml, it increases the height of the
        #text widget and thus gives an undesirable visual effect.
        #This was seen in DnaSequenceEditor. Also tried using 'setSizePolicy' like 
        #done in PM_MessagegroupBox but that didn't work. 
        ##self._setHeight(minLines, maxLines)
        
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
        self.setMinimumSize(QSize(PM_MINIMUM_WIDTH * 0.5, new_height))
        self.setMaximumHeight(new_height)
    
    def restoreDefault(self):
        """
        Restores the default value.
        """
        if self.setAsDefault:
            self.insertHtml(self.defaultText, 
                            setAsDefault = True,
                            replace = True)
        
    def hide(self):
        """
        Hides the tool button and its label (if it has one).
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget: 
            self.labelWidget.hide()
            
    def show(self):
        """
        Unhides the tool button and its label (if it has one).
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget: 
            self.labelWidget.show()

# End of PM_TextEdit ############################
