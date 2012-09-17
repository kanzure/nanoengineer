# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PM_StackedWidget.py

@author: Mark
@version: $Id$
@copyright: 2008 Nanorex, Inc.  All rights reserved.

History:

Mark 2008-05-07: Written for L{DnaDisplayStyle_PropertyManager} to deal with
the UI requirements imposed by adding all the DNA display style preferences
into a property manager.
"""

from PyQt4.Qt import QStackedWidget
from PyQt4.Qt import SIGNAL

from PM.PM_GroupBox         import PM_GroupBox
from PM.PM_ComboBox         import PM_ComboBox
from PM.PM_ListWidget       import PM_ListWidget

class PM_StackedWidget( QStackedWidget ):
    """
    The PM_StackedWidget widget provides a QStackedWidget for a
    Property Manager group box (PM_GroupBox).

    Detailed Description
    ====================
    The PM_StackedWidget class provides a stack of widgets where only one widget
    is visible at a time.

    PM_StackedWidget can be used to create a user interface similar to the one
    provided by QTabWidget. It is a convenience layout widget built on top
    of the QStackedLayout class.

    PM_StackedWidget can be constructed and populated with a number of
    child widgets ("pages").

    PM_StackedWidget can be supplied with a I{switchPageWidget} as a means
    for the user to switch pages. This is typically a PM_ComboBox or a
    PM_ListWidget that stores the titles of the PM_StackedWidget's pages.

    When populating a stacked widget, the widgets are added to an internal list.
    The indexOf() function returns the index of a widget in that list.
    The widgets can either be added to the end of the list using the
    addWidget() function, or inserted at a given index using the
    insertWidget() function. The removeWidget() function removes the widget
    at the given index from the stacked widget. The number of widgets
    contained in the stacked widget, can be obtained using the count()
    function.

    The widget() function returns the widget at a given index position.
    The index of the widget that is shown on screen is given by currentIndex()
    and can be changed using setCurrentIndex(). In a similar manner, the
    currently shown widget can be retrieved using the currentWidget() function,
    and altered using the setCurrentWidget() function.

    Whenever the current widget in the stacked widget changes or a widget is
    removed from the stacked widget, the currentChanged() and widgetRemoved()
    signals are emitted respectively.

    @see: U{B{QStackedWidget}<http://doc.trolltech.com/4/qstackedwidget.html>}

    @see: For an example, see L{DnaDisplayStyle_PropertyManager}.
    """

    labelWidget = None # Needed by the parentWidget (PM_GroupBox).
    _groupBoxCount = 0
    switchPageWidget = None

    def __init__(self,
                 parentWidget,
                 switchPageWidget  = None,
                 childWidgetList   = [],
                 label             = '',
                 labelColumn       = 0,
                 spanWidth         = True,
                 ):
        """
        Appends a QStackedWidget (Qt) widget to the bottom of I{parentWidget},
        which must be a Property Manager group box.

        @param parentWidget: the parent group box containing this widget.
        @type  parentWidget: PM_GroupBox

        @param switchPageWidget: The widget that is used to switch between
                                 pages. If None (the default), it is up to the
                                 caller to manage page switching.
        @type  switchPageWidget: PM_ComboBox or PM_ListWidget

        @param childWidgetList: a list of child widgets (pages), typically a
                                list of PM_GroupBoxes that contain multiple
                                widgets. Each child widget will get stacked onto
                                this stacked widget as a separate page.
        @type  childWidgetList: PM_GroupBox (or other PM widgets).

        @param label: label that appears above (or to the left of) this widget.
        @type  label: str

        @param labelColumn: The column number of the label in the group box
                            grid layout. The only valid values are 0 (left
                            column) and 1 (right column). The default is 0
                            (left column).
        @type  labelColumn: int

        @param spanWidth: If True, the widget and its label will span the width
                      of the group box. Its label will appear directly above
                      the widget (unless the label is empty) and is left justified.
        @type  spanWidth: bool (default True)

        @see: U{B{QStackedWidget}<http://doc.trolltech.com/4/qstackedwidget.html>}
        """

        QStackedWidget.__init__(self)

        assert isinstance(parentWidget, PM_GroupBox)

        self.parentWidget = parentWidget
        self.label        = label
        self.labelColumn  = labelColumn
        self.spanWidth    = spanWidth

        for widget in childWidgetList:
            self.addWidget(widget)

        self.setSwitchPageWidget(switchPageWidget)

        parentWidget.addPmWidget(self)

    def setSwitchPageWidget(self, switchPageWidget):
        """
        Sets the switch page widget to I{switchPageWidget}. This is the widget
        that controls switching between pages (child widgets) added to self.

        @param switchPageWidget: The widget to control switching between pages.
        @type switchPageWidget: PM_ComboBox or PM_ListWidget

        @note: Currently, we are only allowing PM_ComboBox or PM_ListWidget
        widgets to be switch page widgets. It would be straight forward to
        add support for other widgets if needed. Talk to me. --Mark.
        """
        if switchPageWidget:

            assert isinstance(switchPageWidget, PM_ComboBox) or \
                   isinstance(switchPageWidget, PM_ListWidget)

            self.connect(switchPageWidget,
                         SIGNAL("activated(int)"),
                         self.setCurrentIndex)

            self.switchPageWidget = switchPageWidget

# End of PM_StackedWidget ############################
