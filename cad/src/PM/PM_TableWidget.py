# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
PM_TableWidget.py

Simple wrapper over Qt QtableWidget class.

@author: Piotr
@version: $Id$
@copyright: 2008 Nanorex, Inc.  All rights reserved.

History:

piotr 2008-07-15: Created this file.

"""

from PyQt4.Qt import Qt
from PyQt4.Qt import QTableWidget
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget

class PM_TableWidget( QTableWidget ):
    """
    The PM_TableWidget widget provides a table widget.
    """

    defaultState = Qt.Unchecked
    setAsDefault = True
    labelWidget = None

    def __init__(self,
                 parentWidget,
                 label          = '',
                 labelColumn  = 1,
                 setAsDefault  = True,
                 spanWidth = True
                 ):
        """
        Appends a QTableWidget (Qt) widget to the bottom of I{parentWidget},
        a Property Manager group box.
        """

        QTableWidget.__init__(self)
        self.parentWidget = parentWidget
        self.labelColumn = labelColumn
        self.setAsDefault = setAsDefault
        self.spanWidth = spanWidth

        self.label = QLabel(label)

        parentWidget.addPmWidget(self)


# End of PM_TableWidget ############################
