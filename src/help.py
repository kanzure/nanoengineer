"""Help system: at the moment it just pops up a crib-note window"""

__author__ = "Josh"

import sys
import qt

class Help(qt.QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        qt.QMainWindow.__init__(self,parent,name,fl)
        if name == None:
            self.setName("Help")

        self.resize(443,212)
        self.setCaption(self.trUtf8("Fiat Lux"))

        self.setCentralWidget(qt.QWidget(self,"qt_central_widget"))

        self.textLabel1 = qt.QLabel(self.centralWidget(),"textLabel1")
        self.textLabel1.setGeometry(qt.QRect(7,9,430,190))
        textLabel1_font = qt.QFont(self.textLabel1.font())
        textLabel1_font.setFamily("Helvetica [Adobe]")
        textLabel1_font.setPointSize(12)
        self.textLabel1.setFont(textLabel1_font)
        self.textLabel1.setText(self.trUtf8("    (plain)  left button virtual trackball\n"
"             center button zooms scene (vertical) field of view (horiz)\n"
"             right button pans scene\n"
"    (shift)  left button draw loop to select (ccw to unselect)\n"
"             center button selects part\n"
"             right button selects atom\n"
"    (cntrl) left button trackballs selection\n"
"             middle button moves in horizontal plane (up is away)\n"
"             right button moves in vertical plane"))



if __name__=='__main__':
    qt.QApplication.setColorSpec(qt.QApplication.CustomColor)
    app=qt.QApplication(sys.argv)


    foo = Help()
#  app.setMainWidget(foo)
    app.connect(app,qt.SIGNAL("lastWindowClosed ()"),app.quit)
    foo.show()
    app.exec_loop()
