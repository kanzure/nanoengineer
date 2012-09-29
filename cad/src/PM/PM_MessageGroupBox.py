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

from PyQt4.Qt import QTextOption
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QPalette
from PyQt4.Qt import QString, QTextCursor
from PyQt4.Qt import Qt

from PM.PM_Colors    import getPalette
from PM.PM_Colors    import pmMessageBoxColor

from PM.PM_GroupBox    import PM_GroupBox
from PM.PM_TextEdit    import PM_TextEdit

from mock import Mock

class PM_MessageGroupBox( PM_GroupBox ):
    """
    The PM_MessageGroupBox widget provides a message box with a
    collapse/expand button and a title.
    """

    __metaclass__ = Mock()

    def __init__(self,
                 parentWidget,
                 title = "Message"
                 ):
        """
        PM_MessageGroupBox constructor.

        @param parentWidget: the PM_Dialog containing this message groupbox.
        @type  parentWidget: PM_Dialog

        @param title: The title on the collapse button
        @type  title: str
        """

        PM_GroupBox.__init__(self, parentWidget, title)

        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)

        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)


        self.MessageTextEdit = PM_TextEdit(self,
                                           label='',
                                           spanWidth = True,
                                           addToParent = False,
                                           ##cursorPosition = 'beginning'
                                       )
            # We pass addToParent = False to suppress the usual call by
            # PM_TextEdit.__init__ of self.addPmWidget(new textedit widget),
            # since we need to add it to self in a different way (below).
            # [bruce 071103 refactored this from what used to be a special case
            #  in PM_TextEdit.__init__ based on self being an instance of
            #  PM_MessageGroupBox.]

        # Needed for Intel MacOS. Otherwise, the horizontal scrollbar
        # is displayed in the MessageGroupBox. Mark 2007-05-24.
        # Shouldn't be needed with _setHeight() in PM_TextEdit.

        #Note 2008-06-17: We now permit a vertical scrollbar in message groupbox
        #--Ninad

        self.MessageTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Add self.MessageTextEdit to self's vBoxLayout.
        self.vBoxLayout.addWidget(self.MessageTextEdit)
        # We should be calling the PM's getMessageTextEditPalette() method,
        # but that will take some extra work which I will do soon. Mark 2007-06-21
        self.MessageTextEdit.setPalette(getPalette( None,
                                                    QPalette.Base,
                                                    pmMessageBoxColor))
        self.MessageTextEdit.setReadOnly(True)
        #@self.MessageTextEdit.labelWidget = None # Never has one. Mark 2007-05-31
        self._widgetList.append(self.MessageTextEdit)
        self._rowCount += 1


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

    def expand(self):
        """
        Expand this group box i.e. show all its contents and change the look
        and feel of the groupbox button. It also sets the gridlayout margin and
        spacing to 0. (necessary to get rid of the extra space inside the
        groupbox.)

        @see: L{PM_GroupBox.expand}
        """
        PM_GroupBox.expand(self)
        # If we don't do this, we get a small space b/w the
        # title button and the MessageTextEdit widget.
        # Extra code unnecessary, but more readable.
        # Mark 2007-05-21
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)


    def insertHtmlMessage(self,
                          text,
                          setAsDefault = False,
                          minLines     = 4,
                          maxLines     = 10,
                          replace      = True,
                          scrolltoTop =  True):
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
        if scrolltoTop:
            cursor  =  self.MessageTextEdit.textCursor()
            cursor.setPosition( 0,
                                QTextCursor.MoveAnchor )
            self.MessageTextEdit.setTextCursor( cursor )
            self.MessageTextEdit.ensureCursorVisible()

            ##self.MessageTextEdit.moveCursor(QTextCursor.Start)
            ##self.MessageTextEdit.ensureCursorVisible()
            #text2 = self.MessageTextEdit.toPlainText()
            #print "***PM = %s, len(text) =%s"%(self.parentWidget, len(text))
            #if len(text2) > 16:
                #anchorText = text2[:16]
                #print "***anchorText =", anchorText
                #self.MessageTextEdit.scrollToAnchor(anchorText)
                #self.MessageTextEdit.ensureCursorVisible()

        self.show()

# End of PM_MessageGroupBox ############################
