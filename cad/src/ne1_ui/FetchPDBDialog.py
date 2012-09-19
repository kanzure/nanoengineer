"""
FetchPDBDialog.py
Qt Dialog for fetching pdb files from the interweb

@author: Urmi
@version: $Id$
@copyright:2008 Nanorex, Inc. See LICENSE file for details.
"""

from PyQt4.Qt import SIGNAL, SLOT
from PyQt4.QtGui import QDialog, QLineEdit, QPushButton, QLabel
from PyQt4.QtGui import QHBoxLayout, QVBoxLayout, QApplication


class FetchPDBDialog(QDialog):
    def __init__(self, parent = None):
        self.parentWidget = parent
        super(FetchPDBDialog, self).__init__(parent)
        self.text = ''
        self.setWindowTitle("Fetch PDB")

        layout = QVBoxLayout()

        idLayout = QHBoxLayout()
        self.label = QLabel("Enter PDB ID:")
        self.lineEdit = QLineEdit()
        #self.lineEdit.setMaxLength(8) # Check with Piotr about this.
        idLayout.addWidget(self.label)
        idLayout.addWidget(self.lineEdit)

        self.okButton = QPushButton("&OK")
        self.cancelButton = QPushButton("Cancel")
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)

        layout.addLayout(idLayout)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.getProteinCode)
        self.connect(self.okButton, SIGNAL("clicked()"), self.getProteinCode)
        self.connect(self.cancelButton, SIGNAL("clicked()"), self, SLOT("reject()"))
        self.show()
        return

    def getProteinCode(self):
        self.parentWidget.setPDBCode(str(self.lineEdit.text()))
        self.close()
        self.emit(SIGNAL("editingFinished()"))
        return
