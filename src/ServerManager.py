# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
ServerManager.py

$Id$
'''
__author__ = "Huaicai"

from ServerManagerDialog import ServerManagerDialog
from qt import QListViewItem
from SimServer import SimServer
import os
import cPickle as pickle
from debug import print_compact_stack

class ServerManager(ServerManagerDialog):
    serverFile = 'serverList'
    import platform
    
    tmpFilePath = platform.find_or_make_Nanorex_directory()
    serverFile = os.path.join(tmpFilePath, "JobManager", serverFile)
    
    def __init__(self, selectedItem=0):
        ServerManagerDialog.__init__(self)
        ## The ordered server list
        self.servers = self._loadServerList()
        self.selectedItem = selectedItem
     
     
    def showDialog(self):
        self.setup()
        self.exec_loop()    
    
    
    def _fillServerProperties(self, curItem):
        """Display current server properties"""
        s = self.servers[self.items.index(curItem)]
        
        self.name_linedit.setText(s.hostname)
        self.ipaddress_linedit.setText(s.ipaddress)
        self.platform_combox.setCurrentText(s.platform)
        self.method_combox.setCurrentText(s.method)
        self.engine_combox.setCurrentText(s.engine)
        self.program_linedit.setText(s.program)
        self.username_linedit.setText(s.username)
        self.password_linedit.setText(s.password)
    
    
    def setup(self):
        self.server_listview.clear()
        self.items = []
        for s in self.servers:
            self.items += [QListViewItem(self.server_listview, str(s.server_id), s.engine)]
        
        item = self.server_listview.currentItem()
        self._fillServerProperties(item)
        
        
    def applyChange(self):
        """Apply server property changes"""
        s = {'hostname':str(self.name_linedit.text()), 'ipaddress':str(self.ipaddress_linedit.text()), 'platform':str(self.platform_combox.currentText()), 'method':str(self.method_combox.currentText()), 'engine':str(self.engine_combox.currentText()), 'program': str(self.program_linedit.text()), 'username':str(self.username_linedit.text()), 'password':str(self.password_linedit.text())}
        
        item = self.server_listview.currentItem()
        item.setText(1, s['engine'])
        
        self.servers[self.items.index(item)].set_parms(s)
     
                 
    def addServer(self):
        """Add a new server. """
        server = SimServer()
        self.servers[:0] = [server]
        self.setup()
    
    
    def changeServer(self, curItem):
        """Select a different server to display"""
        self._fillServerProperties(curItem)
    
     
    def closeEvent(self, event):
        """This is the closeEvent handler, it's called when press 'X' button on the title bar or 'Esc' key or 'Exit' button in the dialog """ 
        try:
            self._saveServerList()
        except:
            print_compact_stack("Sim-server pickle exception.")
            self.accept()   
            
        self.accept()
    
    
    def getServer(self, indx):
        """Return the server for <indx>, the index of the server in 
        the server list. """
        assert type(indx) == type(1)
        
        assert  indx in range(len(self.servers))
        return self.servers[indx]
    
    
    def getServerById(self, ids):
        """Return the server with the server_id = ids """
        for s in self.servers:
            if s.server_id == ids:
                return s
        return None
    
    
    def getServers(self):
        """Return the list of servers."""
        return self.servers
    
    
    def _loadServerList(self):
        """Return the list of servers available, otherwise, create a default one. """
        if os.path.isfile(self.serverFile):
            try:
                file = open(self.serverFile, "rb")
                return pickle.load(file)
            except:
                print_compact_stack("Unpickle exception.")
                return [SimServer()]
        else:
              return [SimServer()]                   
    
        
    def _saveServerList(self):
        """Save the server list for future use when exit from current dialog."""
        file = open(self.serverFile, "wb")
        pickle.dump(self.servers, file, pickle.HIGHEST_PROTOCOL)
        file.close()

##Test code
if __name__ == '__main__':
        from qt import QApplication
        
        