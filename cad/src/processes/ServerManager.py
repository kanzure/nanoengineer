# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ServerManager.py - persistent db and UI for list of servers & current server.
Unclear whether or not this is GAMESS-specific.
[bruce 071217 guess at description]

@author: Huaicai
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

from processes.ServerManagerDialog import Ui_ServerManagerDialog
from PyQt4.Qt import QDialog, QStringList, SIGNAL, QMessageBox
from simulation.SimServer import SimServer
import os
import cPickle as pickle
from utilities.debug import print_compact_stack
from utilities.qt4transition import qt4todo
from platform_dependent.PlatformDependent import find_or_make_Nanorex_directory

class ServerManager(QDialog, Ui_ServerManagerDialog):
    """
    Persistent db and UI for list of servers & current server.
    
    #doc more

    The servers in our list are SimServer objects.
    """
    serverFile = 'serverList'
    
    tmpFilePath = find_or_make_Nanorex_directory()
    serverFile = os.path.join(tmpFilePath, "JobManager", serverFile)
    
    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.connect(self.new_btn,SIGNAL("clicked()"),self.addServer)
        self.connect(self.exit_btn,SIGNAL("clicked()"),self.close)
        self.connect(self.server_listview,SIGNAL("currentChanged(QListViewItem*)"),self.changeServer)
        self.connect(self.engine_combox,SIGNAL("activated(const QString&)"),self.engineChanged)
        self.connect(self.del_btn,SIGNAL("clicked()"),self.deleteServer)
        qt4todo('self.server_listview.setSorting(-1)')
        ## The ordered server list
        self.servers = self._loadServerList()
        return
     
    def showDialog(self, selectedServer = 0):
        if not selectedServer:
            selectedServer = self.servers[0]
        self.setup(selectedServer)
        self.exec_()    
        return
    
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
        return
    
    def setup(self, selectedServer):
        self.server_listview.clear()
        self.items = []
        
        servers = self.servers[:]
        servers.reverse()
        for s in servers:
            item = QStringList()
            item.append(s.server_id)
            item.append(s.item)
            self.server_listview.addItems(item)
            #item = QListViewItem(self.server_listview, str(s.server_id), s.engine)
            self.items += [item]
            if s == selectedServer:
                selectedItem = item 
        self.items.reverse()
        self.server_listview.setCurrentIndex(selectedItem)
        
        self._fillServerProperties(selectedServer)
        return
        
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
        
        item = self.server_listview.currentIndex()
        item.setText(1, s['engine'])
        
        self.servers[self.items.index(item)].set_parms(s)
        return
    
    def engineChanged(self, newItem):
        item = self.server_listview.currentIndex()
        sevr = self.servers[self.items.index(item)]
        sevr.engine = str(newItem) 
        item.setText(1, sevr.engine)       
        return
                 
    def addServer(self):
        """Add a new server. """
        server = SimServer()
        self.servers[:0] = [server]
        self.setup(server)
        return
    
    def deleteServer(self):
        """Delete a server. """
        if len(self.servers) == 1:
            msg = "At least 1 server must exist. After deleting the last one, "\
                  "a default new server will be created."
            QMessageBox.information(self,
                                    "Deleting a server",
                                    msg,
                                    QMessageBox.Ok )
        item = self.server_listview.currentIndex()
        self.server_listview.takeItem(item)
        del self.servers[self.items.index(item)]
        self.items.remove(item)
        print "After deleting."
        return
    
    def changeServer(self, curItem):
        """Select a different server to display"""
        #print "curItem: ", curItem
        #print "servers: ", self.servers
        self._fillServerProperties(self.servers[self.items.index(curItem)])
        return
    
    def closeEvent(self, event):
        """
        This is the closeEvent handler, it's called when press 'X' button
        on the title bar or 'Esc' key or 'Exit' button in the dialog
        """ 
        try:
            self._applyChange()
            self._saveServerList()
        except:
            print_compact_stack("Sim-server pickle exception.")
            self.accept()   
            
        self.accept()
        return
    
    def getServer(self, indx):
        """
        Return the server for <indx>, the index of the server in 
        the server list.
        """
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
        return

    pass # end of class ServerManager

# == Test code [stub]

if __name__ == '__main__':
    from PyQt4.Qt import QApplication, QDialog
        
# end
