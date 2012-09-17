# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_PreviewGroupBox.py

The PM_PreviewGroupBox widget provides a preview pane for previewing
elements , clipboard items , library parts etc. from the element chooser
or list provided in the property manager. (The object being previewed can
then be deposited into the 3D workspace.)

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad 2007-08-29: Created.
"""

from PyQt4.Qt         import QSize
from graphics.widgets.ThumbView import MMKitView
from PM.PM_GroupBox   import PM_GroupBox

class PM_PreviewGroupBox(PM_GroupBox):
    """
    The PM_PreviewGroupBox widget provides a preview pane for previewing
    elements , clipboard items , library parts etc. from the element chooser
    or list provided in the property manager. (The object being previewed can
    then be deposited into the 3D workspace.)
    """
    elementViewer = None
    def __init__(self,
                 parentWidget,
                 glpane = None,
                 title = 'Preview'
                 ):
        """
        Appends a PM_PreviewGroupBox widget to I{parentWidget},a L{PM_Dialog}

        @param parentWidget: The parent dialog (Property manager) containing
                             this  widget.
        @type  parentWidget: L{PM_Dialog}

        @param glpane: GLPane object used in construction of the
                       L{self.elementViewer}
        @type  glpane: L{GLPane} or None

        @param title: The title (button) text.
        @type  title: str

        """
        PM_GroupBox.__init__(self, parentWidget, title)

        self.glpane = glpane
        self.parentWidget = parentWidget
        self._loadPreviewGroupBox()

    def _loadPreviewGroupBox(self):
        """
        Load the L{self.elementViewer} widget inside this preview groupbox.
        @attention: The L{self.elementViewer} widget is added to
                    L{self.previewGroupBox.gridLayout} in L{Thumbview.__init__}.
                    Based on  tests, it takes longer cpu time to complete this
                    operation (adding QGLWidget to a gridlayout. By doing this
                    inside L{Thumbview.__init__}, a time gain of ~ 0.1 sec
                    was noticed on Windows XP.
        """

        self.elementViewer = MMKitView(
                        self,
                        "MMKitView glPane",
                        self.glpane)
        self.elementViewer.setMinimumSize(QSize(150, 150))

        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        #Append to the widget list. This is important for expand - collapse
        #functions (of the groupbox) to work properly.
        self._widgetList.append(self.elementViewer)
        ##self.previewGroupBox.gridLayout.addWidget(self.elementViewer,
        ##                                          0, 0, 1, 1)


    def expand(self):
        """
        Expand this group box i.e. show all its contents and change the look
        and feel of the groupbox button. It also sets the gridlayout margin and
        spacing to 0. (necessary to get rid of the extra space inside the
        groupbox.)

        @see: L{PM_GroupBox.expand}
        """
        PM_GroupBox.expand(self)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)