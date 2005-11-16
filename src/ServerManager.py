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
    
    def __init__(self):
        ServerManagerDialog.__init__(self)
        self.server_listview.setSorting(-1)
        ## The ordered server list
        self.servers = self._loadServerList()
        
     
    def showDialog(self, selectedServer = 0):
        if not selectedServer: selectedServer = self.servers[0]
        self.setup(selectedServer)
        self.exec_loop()    
    
    
    def _fillServerProperties(self, s):
        """Display current server properties"""
        self.name_linedit.setText(s.hostname)
        self.ipaddress_linedit.setText(s.ipaddress)
        self.platform_combox.setCurrentText(s.platform)
        self.method_combox.setCurrentText(s.method)
        self.engine_combox.setCurrentText(s.engine)
        self.program_linedit.setText(s.program)
        self.username_linedit.setText(s.username)
        self.password_linedit.setText(s.password)
    
    
    def setup(self, selectedServer):
        self.server_listview.clear()
        self.items = []
        
        servers = self.servers[:]
        servers.reverse()
        for s in servers:
            item = QListViewItem(self.server_listview, str(s.server_id), s.engine)
            self.items += [item]
            if s == selectedServer:
                selectedItem = item 
        self.items.reverse()
        self.server_listview.setCurrentItem(selectedItem)
        
        self._fillServerProperties(selectedServer)
        
        
    def _applyChange(self):
        """Apply server property changes"""
        s = {'hostname':str(self.name_linedit.text()),
             'ipaddress':str(self.ipaddress_linedit.text()),
             'platform':str(self.platform_combox.currentText()),
             'method':str(self.method_combox.currentText()),
             'engine':str(self.engine_combox.currentText()),
             'program': str(self.program_linedit.text()),
             'username':str(self.username_linedit.text()),
             'password':str(self.password_linedit.text())}
        
        item = self.server_listview.currentItem()
        item.setText(1, s['engine'])
        
        self.servers[self.items.index(item)].set_parms(s)
     
    
    def engineChanged(self, newItem):
        item = self.server_listview.currentItem()
        sevr = self.servers[self.items.index(item)]
        sevr.engine = str(newItem) 
        item.setText(1, sevr.engine)       
    
                 
    def addServer(self):
        """Add a new server. """
        server = SimServer()
        self.servers[:0] = [server]
        self.setup(server)
    
    
    def deleteServer(self):
        """Delete a server. """
        if len(self.servers) == 1:
            QMessageBox.information(self, "Deleting a server",
                "At least 1 server is needed to exist, after deleting the last one, a default new server will be created.",
                                    QMessageBox.Ok) 
        
        item = self.server_listview.currentItem()
        self.server_listview.takeItem(item)
        del self.servers[self.items.index(item)]
        self.items.remove(item)
        
        print "After deleting."
     
        
    
    def changeServer(self, curItem):
        """Select a different server to display"""
        #print "curItem: ", curItem
        #print "servers: ", self.servers
        self._fillServerProperties(self.servers[self.items.index(curItem)])
    
     
    def closeEvent(self, event):
        """This is the closeEvent handler, it's called when press 'X' button
        on the title bar or 'Esc' key or 'Exit' button in the dialog """ 
        try:
            self._applyChange()
            self._saveServerList()
        except:
            print_compact_stack("Sim-server pickle exception.")
            self.accept()   
            
        self.accept()
    
    
    def getServer(self, indx):
        """Return the server for <indx>, the index of the server in 
        the server list. """
        #self._applyChange()
        assert type(indx) == type(1)
        
        assert  indx in range(len(self.servers))
        return self.servers[indx]
    
    
    def getServerById(self, ids):
        """Return the server with the server_id = ids """
        #self._applyChange()
        for s in self.servers:
            if s.server_id == ids:
                return s
        return None
    
    
    def getServers(self):
        """Return the list of servers."""
        #self._applyChange()
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
        self._applyChange()
        file = open(self.serverFile, "wb")
        pickle.dump(self.servers, file, pickle.HIGHEST_PROTOCOL)
        file.close()

##Test code
if __name__ == '__main__':
        from qt import QApplication
        
        
