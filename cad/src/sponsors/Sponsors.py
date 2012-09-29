# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Sponsors.py - sponsors system, exporting PermissionDialog and SponsorableMixin

@author: Will
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

Motivation and design rationale:

We want to recoup some of the costs of developing NanoEngineer-1 in a
way consistent with its GPL licensing. One way to do that is to have
sponsors, and to offer the sponsors advertising space in a way that
doesn't bother the user. Some UI dialogs will have buttons with
sponsor logos on them, and if you click on a sponsor logo button,
you'll get more information and maybe a link to their website. There
are no unsolicited pop-ups in this system.

We want to be able to update sponsor information without asking the
user to download a new version. So we have the program fetch recent
sponsor information from our server. We don't want this to annoy the
user, in terms of either network bandwidth or privacy concerns, so
we have a permission dialog that explains what we're doing and asks
the user for permission to do it.

Module classification:

Contains many levels of code, but exports only a widget and a widget-helper.
Still, functionally it may belong in its own toplevel package. [bruce 071217]
"""

import base64
import hashlib
import os
import random
import re
import socket
import string
import threading
import types
import urllib

from xml.dom.minidom import parseString

from PyQt4.Qt import QDialog
from PyQt4.Qt import QImage
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QSize
from PyQt4.Qt import QIcon
from PyQt4.Qt import QGridLayout
from PyQt4.Qt import QTextBrowser
from PyQt4.Qt import QPushButton
from PyQt4.Qt import SIGNAL

import foundation.env as env
from utilities import debug_flags

from platform_dependent.PlatformDependent import find_or_make_Nanorex_subdir
from foundation.wiki_help import WikiHelpBrowser
from utilities.debug import print_compact_stack, print_compact_traceback
from utilities.qt4transition import qt4todo
from utilities.prefs_constants import sponsor_download_permission_prefs_key
from utilities.prefs_constants import sponsor_permanent_permission_prefs_key
from utilities.prefs_constants import sponsor_md5_mismatch_flag_key
from utilities.Log import redmsg, orangemsg, greenmsg
from utilities.icon_utilities import geticon

_sponsordir = find_or_make_Nanorex_subdir('Sponsors')
_sponsors = { }

# Include a trailing slash in the following sponsor server URLs.
_sponsor_servers = \
    ['http://nanoengineer-1.com/NE1_Sponsors/',
     #'file:///transfers/',
     ]


def _fixHtml(rc): #bruce 071217 renamed this to be private
    startUrl=re.compile('\[')
    middleUrl=re.compile(' ')
    finishUrl=re.compile('\]')
    rc = string.replace(rc, '[P]', '<p>')
    rc = string.replace(rc, '[p]', '<p>')
    rc = string.replace(rc, '[ul]', '<ul>')
    rc = string.replace(rc, '[/ul]', '</ul>')
    rc = string.replace(rc, '[li]', '<li>')
    while True:
        m = startUrl.search(rc)
        if m == None:
            return rc
        s, e = m.start(), m.end()
        m = middleUrl.search(rc[e:])
        s2, e2 = m.start() + e, m.end() + e
        m = finishUrl.search(rc[e2:])
        s3, e3 = m.start() + e2, m.end() + e2
        mid = "<a href=\"%s\">%s</a>" % (rc[e:s2], rc[e2:s3])
        rc = rc[:s] + mid + rc[e3:]

class _Sponsor: #bruce 071217 renamed this to be private
    """
    """
    def __init__(self, name, text, imgfile):
        self.name = name
        self.text = text
        self.imgfile = imgfile

    def __repr__(self):
        return '<' + self.name + '>'

    def configureSponsorButton(self, btn):
        """
        Load the image in the Sponsor button I{btn} that is displayed at the
        top of the Property Manager.

        @param btn: The sponsor button.
        @type  btn: QToolButton
        """
        qimg = QImage(self.imgfile)
        pixmap = QPixmap.fromImage(qimg)
        size = QSize(pixmap.width(), pixmap.height())
        btn.setIconSize(size)
        btn.setIcon(QIcon(pixmap))

    def wikiHelp(self):
        parent = env.mainwindow()
        w = WikiHelpBrowser(self.text,parent,caption=self.name)
        w.show()

def _get_remote_file(filename, prefix):
    """
    Get file I{filename} from the sponsor server.

    @param filename: the name of the file to get
    @type  filename: string
    @param prefix: a short string that is expected at the beginning of the file
                   for the retrieval to be denoted as successful
    @type  prefix: string

    @return: gotContents, fileContents
    @rtype:  gotContents - True if the file contents were successfully retrieved,
                           False otherwise
             fileContents - the contents of the requested file
    """

    # Try to connect for up to five seconds per host
    socket.setdefaulttimeout(5)

    fileContents = ""
    gotContents = False
    for host in _sponsor_servers:
        url = host + filename
        try:
            fileHandle = urllib.urlopen(url)
            fileContents = fileHandle.read()
            fileHandle.close()
            if fileContents.startswith(prefix):
                gotContents = True
                break

        except IOError:
            pass # Fail silently

    return gotContents, fileContents


def _download_xml_file(xmlfile):
    (gotSponsorsFile, fileContents) = _get_remote_file("sponsors.xml", "<?xml")
    if gotSponsorsFile:
        # If we got this far, we have info to replace the local copy of
        # sponsors.xml. If we never got this far but a local copy exists,
        # then we'll just use the existing local copy.
        if os.path.exists(xmlfile):
            os.remove(xmlfile)
        fileHandle = open(xmlfile, 'w')
        fileHandle.write(fileContents)
        fileHandle.close()


def _load_sponsor_info(xmlfile, win):
    def getXmlText(doc, tag):
        parent = doc.getElementsByTagName(tag)[0]
        rc = ""
        for node in parent.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    if os.path.exists(xmlfile):
        try:
            f = open(xmlfile)
            r = f.read()
            f.close()
            info = parseString(r)
            for sp_info in info.getElementsByTagName('sponsor'):
                sp_name = getXmlText(sp_info, 'name')
                sp_imgfile = os.path.join(_sponsordir, 'logo_%s.png' % sp_name)
                sp_keywords = getXmlText(sp_info, 'keywords')
                sp_keywords = map(lambda x: x.strip(),
                                  sp_keywords.split(','))
                sp_text = _fixHtml(getXmlText(sp_info, 'text'))
                if not os.path.exists(sp_imgfile) or \
                   os.path.getctime(sp_imgfile) < os.path.getctime(xmlfile):
                    sp_png = base64.decodestring(getXmlText(sp_info, 'logo'))
                    open(sp_imgfile, 'wb').write(sp_png)
                sp = _Sponsor(sp_name, sp_text, sp_imgfile)
                for keyword in sp_keywords:
                    if not _sponsors.has_key(keyword):
                        _sponsors[keyword] = [ ]
                    _sponsors[keyword].append(sp)
        except:
            print_compact_traceback("trouble getting sponsor info: ")
            print_compact_stack("trouble getting sponsor info: ")
    for dialog in win.sponsoredList():
        try:
            dialog.setSponsor()
        except:
            pass

def _force_download():
    # Don't check if the MD5 matches. Don't check if the XML file is
    # older than two days old. Just download it unconditionally.
    env.history.message(orangemsg("FOR DEBUG ONLY! _force_download() " +
                                  "does not respect user privacy preferences."))
    xmlfile = os.path.join(_sponsordir, 'sponsors.xml')
    win = env.mainwindow()
    _download_xml_file(xmlfile)
    if not os.path.exists(xmlfile):
        raise Exception('_force_download failed')
    _load_sponsor_info(xmlfile, win)
    env.history.message(greenmsg("_force_download() is finished"))

############################################

class PermissionDialog(QDialog, threading.Thread):

    # Politely explain what we're doing as clearly as possible. This will be the
    # user's first experience of the sponsorship system and we want to use the
    # Google axiom of "Don't be evil".
    text = ("We would like to use your network connection to update a list of our " +
            "sponsors. This enables us to recoup some of our development costs " +
            "by putting buttons with sponsor logos on some dialogs. If you click " +
            "on a sponsor logo button, you will get a small window with some " +
            "information about that sponsor. May we do this? Otherwise we'll " +
            "just use buttons with our own Nanorex logo.")

    def __init__(self, win):
        self.xmlfile = os.path.join(_sponsordir, 'sponsors.xml')
        self.win = win

        self.needToAsk = False
        self.downloadSponsors = False
        threading.Thread.__init__(self)

        if not self.refreshWanted():
            return
        if env.prefs[sponsor_permanent_permission_prefs_key]:
            # We have a permanent answer so no need for a dialog
            if env.prefs[sponsor_download_permission_prefs_key]:
                self.downloadSponsors = True
            return

        self.needToAsk = True
        QDialog.__init__(self, None)
        self.setObjectName("Permission")
        self.setModal(True) #This fixes bug 2296. Mitigates bug 2297
        layout = QGridLayout()
        self.setLayout(layout)
        layout.setMargin(0)
        layout.setSpacing(0)
        layout.setObjectName("PermissionLayout")
        self.text_browser = QTextBrowser(self)
        self.text_browser.setObjectName("text_browser")
        layout.addWidget(self.text_browser,0,0,1,4)
        self.text_browser.setMinimumSize(400, 80)
        self.setWindowTitle('May we use your network connection?')
        self.setWindowIcon(geticon('ui/border/MainWindow.png'))
        self.text_browser.setPlainText(self.text)
        self.accept_button = QPushButton(self)
        self.accept_button.setObjectName("accept_button")
        self.accept_button.setText("Always OK")
        self.accept_once_button = QPushButton(self)
        self.accept_once_button.setObjectName("accept_once_button")
        self.accept_once_button.setText("OK now")
        self.decline_once_button = QPushButton(self)
        self.decline_once_button.setObjectName("decline_once_button")
        self.decline_once_button.setText("Not now")
        self.decline_always_button = QPushButton(self)
        self.decline_always_button.setObjectName("decline_always_button")
        self.decline_always_button.setText("Never")
        layout.addWidget(self.accept_button,1,0)
        layout.addWidget(self.accept_once_button,1,1)
        layout.addWidget(self.decline_once_button,1,2)
        layout.addWidget(self.decline_always_button,1,3)
        self.connect(self.accept_button,SIGNAL("clicked()"),self.acceptAlways)
        self.connect(self.accept_once_button,SIGNAL("clicked()"),self.acceptJustOnce)
        self.connect(self.decline_once_button,SIGNAL("clicked()"),self.declineJustOnce)
        self.connect(self.decline_always_button,SIGNAL("clicked()"),self.declineAlways)

    def acceptAlways(self):
        env.prefs[sponsor_download_permission_prefs_key] = True
        env.prefs[sponsor_permanent_permission_prefs_key] = True
        self.downloadSponsors = True
        self.close()

    def acceptJustOnce(self):
        env.prefs[sponsor_permanent_permission_prefs_key] = False
        self.downloadSponsors = True
        self.close()

    def declineAlways(self):
        env.prefs[sponsor_download_permission_prefs_key] = False
        env.prefs[sponsor_permanent_permission_prefs_key] = True
        self.close()

    def declineJustOnce(self):
        env.prefs[sponsor_permanent_permission_prefs_key] = False
        self.close()


    def run(self):
        #
        # Implements superclass's threading.Thread.run() function
        #
        if self.downloadSponsors:
            _download_xml_file(self.xmlfile)
        self.finish()
        env.prefs[sponsor_md5_mismatch_flag_key] = self.md5Mismatch()


    def refreshWanted(self):
        if not os.path.exists(self.xmlfile):
            return True

        if env.prefs[sponsor_md5_mismatch_flag_key]:
            return True

        return False


    def md5Mismatch(self):
        # Check the MD5 hash - if it hasn't changed, then there is
        # no reason to download sponsors.xml.
        try:
            (gotMD5_File, remoteDigest) = \
                _get_remote_file("sponsors.md5", "md5:")
            if gotMD5_File:
                m = hashlib.md5()
                m.update(open(self.xmlfile).read())
                localDigest = "md5:" + base64.encodestring(m.digest())
                remoteDigest = remoteDigest.rstrip()
                localDigest = localDigest.rstrip()
                return (remoteDigest != localDigest)

            else:
                return True
        except:
            return True


    def finish(self):
        _load_sponsor_info(self.xmlfile, self.win)

    pass

###############################################

# This is the default sponsor image (and text) for the PM sponsor button.

_nanorexText = """\
Nanorex created NanoEngineer-1, the program you're using right now.
<p>
See the <A HREF="http://www.nanoengineer-1.net/">NanoEngineer-1 wiki </A>
for tutorials and other information.</p>
<p>
See <A HREF="http://www.nanorex.com/">www.nanorex.com</A> for more information
about Nanorex.</p>
"""
from utilities.icon_utilities import image_directory
_sponsorImagePath = os.path.join( image_directory(), "ui/sponsors/nanorex.png")
_defaultSponsor = _Sponsor('Nanorex',
                           _fixHtml(_nanorexText), _sponsorImagePath)


###############################################

class SponsorableMixin:
    """
    To use this mixin class, instances of a main class which inherits it
    (which is typically a QDialog or PM_Dialog) should provide:

        - an attribute sponsor_keyword, which can be None, or a keyword
          string, or a list or tuple of sponsor keyword strings.
        - an attribute sponsor_btn, which must be a QPushButton object
          whose pixmap will be replaced with a sponsor logo during this
          mixin's __init__ or setSponsor methods. This button must
          already exist when our __init__ method is called.

    This mixin class then provides:
        - an __init__ method (which should only be called when the above
          attributes are ready)
        - a setSponsor method which may be called at any time after that,
          to change sponsors (might be useful whether or not
          sponsor_keyword has changed, since sponsors are sometimes chosen
          at random based on it, and the info used to choose them might
          have been updated)
        - an action method meant to be used by the caller as Qt slot
          methods, which can be named either 'sponsor_btn_clicked' or
          'open_sponsor_homepage'.
      """
    sponsor_keyword = None # Nanorex is the default sponsor.

    def __init__(self):
        self.setSponsor()

    def setSponsor(self):
        keyword = self.sponsor_keyword
        if type(keyword) in (types.ListType, types.TupleType):
            keyword = random.choice(keyword)
        try:
            sponsor = random.choice(_sponsors[keyword])
        except KeyError:
            sponsor = _defaultSponsor
        self.__sponsor = sponsor
        sponsor.configureSponsorButton(self.sponsor_btn)

    def sponsor_btn_clicked(self):
        self.__sponsor.wikiHelp()
    def open_sponsor_homepage(self):
        self.__sponsor.wikiHelp()
    pass

# end
