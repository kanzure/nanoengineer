# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
assistant.py

$Id$
"""

import sys, string
from qt import *
from os import *

class AssistantWindow(QWidget):
    def __init__(self,home_,_path,parent=None,name=None,fl=0):
        QWidget.__init__(self,parent,name,fl)
  
        if name == None:
            self.setName("AssistantWindow")
        
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        #self.assistant = QAssistantClient("C:/Qt/3.3.3/bin/.",None,None) # Need to ask Bruce...
        self.assistant = QAssistantClient(filePath + "/../bin", self)

        list = QStringList()
        list.append("-profile")
        list.append(filePath + "/../doc/html/ne1assistant.adp")

        self.assistant.setArguments( list )
        self.connect( self.assistant, SIGNAL("error(const QString&)"),self.showAssistantErrors)
            
    def openNE1Assistant(self):
        if not self.assistant.isOpen(): self.assistant.openAssistant()
            
    def showAssistantErrors(self, errors):
        print "Error opening nanoENGINEER-1 Assistant :\n", errors
        
import os

def findIndexFile():
    "return the full pathname to our toplevel html docfile, or None if you can't find it"
    #e This should be extended to ask user for help in locating this pathname,
    # if it can't find it on its own;
    # and it's ok if it's extended to put error messages in a dialog
    # even though the callers also print something then.
    try:
        nedirenv = environ['NE1DIR']
        #e now make it an absolute pathname??
    except:
        # bruce 041105 bugfix -- should not need NE1DIR if user does not
        # set it -- just assume installation was standard, and find doc
        # files relative to this python source file.

        #e do we first need to make sure __file__ is an absolute pathname??
        dir, base = os.path.split(__file__)
            # e.g. "/.../cad/src" and "assistant.py" (or maybe ".pyc"?)
        # remove cad/src from end, in os-independent way
        dir, dir1 = os.path.split(dir)
        assert dir1 == "src" #e should have decent error message if this fails
        dir, dir1 = os.path.split(dir)
        assert dir1 == "cad"
        nedirenv = dir
    if nedirenv:
        home = os.path.join( nedirenv, 'cad/doc/html/index.html' )
        return home
    return None

# == code for when we're run standalone:

if __name__=='__main__':
    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)

    home = findIndexFile()
    if not home:
        print "can't find html docs for assistant"
        sys.exit(1) #bruce 041118
    foo = AssistantWindow(home,QStringList('.'),None,'help viewer')
    foo.assistant.openAssistant()

    QObject.connect(app,SIGNAL('lastWindowClosed()'),app,SLOT('quit()'))

    app.exec_loop()

# end of assistant.py
