"""Help system: at the moment it just pops up a crib-note window"""

__author__ = "Josh"

import sys
import qt

class Help(qt.QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        qt.QMainWindow.__init__(self,parent,name,fl)
        if name == None:
            self.setName("Help")

        self.resize(500,800)
        self.setCaption(self.trUtf8("Fiat Lux"))

        self.setCentralWidget(qt.QWidget(self,"qt_central_widget"))

        self.textLabel1 = qt.QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setGeometry(qt.QRect(2,2,496,796))
        textLabel1_font = qt.QFont(self.textLabel1.font())
        textLabel1_font.setFamily("Helvetica [Adobe]")
        textLabel1_font.setPointSize(14)
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setText(self.trUtf8("""Mouse controls:

General: 

Left button does something according to mode, see below

Middle button always controls motion (using ProE style:
  bare: trackball
  shift: Pan
  Cntl: Zoom (vertical mouse motion) / turn (horizontal)
  Wheel does zoom, half-speed with shift, double with cntl

Right button always pops up a menu appropriate to mode.

Default (selection) mode:

single click left button selects atoms (or parts if parts are selected)
bare left button selects / dragging does "rectangle" or "lasso" selection
shift left button unselects / dragging does "rectangle" or "lasso" unselection
control left button unselects what's outside the shape
double-click left button selects parts

Cookie cutter mode:
single click left button draws rubber-band lines
bare left button dragging does "rectangle" or "lasso" cutout
shift left button dragging does "rectangle" or "lasso" holes
control left button logical ANDs shape

Move mode:
bare left button moves object
shift left button trackballs object
cntl left button rotates or moves object on its own axis
double click goes back to select mode

modes to come:

deposit atoms
extrude
revolve
measure
"""))



if __name__=='__main__':
    qt.QApplication.setColorSpec(qt.QApplication.CustomColor)
    app=qt.QApplication(sys.argv)


    foo = Help()
#  app.setMainWidget(foo)
    app.connect(app,qt.SIGNAL("lastWindowClosed ()"),app.quit)
    foo.show()
    app.exec_loop()
