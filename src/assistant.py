import sys, string
from qt import *
from os import *

class AssistantWindow(QWidget):
    def __init__(self,home_,_path,parent=None,name=None,fl=0):
        QWidget.__init__(self,parent,name,fl)

        if name == None:
            self.setName("AssistantWindow")
        
        self.assistant = QAssistantClient("C:/Qt/3.3.3/bin/.",None,None) # Need to ask Bruce...
        list = QStringList()
        list.append("-profile")
        list.append("../doc/html/ne1assistant.adp")
        self.assistant.setArguments( list )
        self.connect( self.assistant, SIGNAL("error(const QString&)"),self.showAssistantErrors)
            
    def openNE1Assistant(self):
        if not self.assistant.isOpen(): self.assistant.openAssistant()
            
    def showAssistantErrors(self, errors):
        print "Error opening nanoENGINEER-1 Assistant :\n", errors