import os
import urllib
import base64
from xml.dom.minidom import parseString
from wiki_help import WikiHelpBrowser
from platform import find_or_make_Nanorex_subdir
import socket
import re
import random
import time
from debug import print_compact_stack, print_compact_traceback

# Sponsor stuff
# (1) download the sponsor information
# (2) store the text and the logo in files somewhere in ~/Nanorex
# (3) use the logo to replace the button's existing logo
# (4) be ready, when the user clicks the sponsor button, to pop up the text

_sponsordir = find_or_make_Nanorex_subdir('Sponsors')
_magicUrl = 'http://willware.net/sponsors.xml'
_sponsors = { }

class Sponsor:
    def __init__(self, name, text, imgfile):
        self.name = name
        self.text = text
        self.imgfile = imgfile

    def configureSponsorButton(self, btn):
        from qt import QImage, QPixmap
        qimg = QImage(self.imgfile)
        qpxmp = QPixmap(qimg)
        btn.setPixmap(qpxmp)

    def wikiHelp(self):
        w = WikiHelpBrowser(self.text)
        w.show()

def fixHtml(rc,
            para=re.compile('\[P\]'),
            startUrl=re.compile('\['), middleUrl=re.compile(' '), finishUrl=re.compile('\]')):
    while True:
        m = para.search(rc)
        if m == None:
            break
        s, e = m.start(), m.end()
        rc = rc[:s] + '<p>' + rc[e:]
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

###############################################

_nanorexLogo = '''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
ZB4c8k4fONAAAAAASUVORK5CYII='''

_nanorexText = 'Creators of [http://www.nanoengineer-1.com nanoENGINEER-1]'
_defsp_png = base64.decodestring(_nanorexLogo)
_defsp_imgfile = os.path.join(_sponsordir, 'logo_nanorex.png')
open(_defsp_imgfile, 'wb').write(_defsp_png)
_defaultSponsor = Sponsor('Nanorex', fixHtml(_nanorexText), _defsp_imgfile)

###############################################

def downloadSponsorInfo():
    def getXmlText(doc, tag):
        parent = doc.getElementsByTagName(tag)[0]
        rc = ""
        for node in parent.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    xmlfile = os.path.join(_sponsordir, 'sponsors.xml')
    try:
        wantRefresh = False
        if os.path.exists(xmlfile):
            age = time.time() - os.path.getctime(xmlfile)
            # refresh every two days
            if age > 2 * 24 * 3600:
                wantRefresh = True
        else:
            wantRefresh = True
        if wantRefresh:
            # Don't waste more than five seconds trying to get a network
            # connection.
            socket.setdefaulttimeout(5)
            f = urllib.urlopen(_magicUrl)
            r = f.read()
            f.close()
            # If we got this far, we have info to replace whatever is
            # currently in the xml file. If we never got this far but
            # the file did exist, then we'll just use the old info.
            if os.path.exists(xmlfile):
                os.remove(xmlfile)
            f = open(xmlfile, 'w')
            f.write(r)
            f.close()
    except:
        print_compact_traceback("trouble getting sponsor info: ")
        print_compact_stack("trouble getting sponsor info: ")
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
                sp_text = fixHtml(getXmlText(sp_info, 'text'))
                if not os.path.exists(sp_imgfile) or \
                   os.path.getctime(sp_imgfile) < os.path.getctime(xmlfile):
                    sp_png = base64.decodestring(getXmlText(sp_info, 'logo'))
                    open(sp_imgfile, 'wb').write(sp_png)
                sp = Sponsor(sp_name, sp_text, sp_imgfile)
                for keyword in sp_keywords:
                    if not _sponsors.has_key(keyword):
                        _sponsors[keyword] = [ ]
                    _sponsors[keyword].append(sp)
        except:
            print_compact_traceback("trouble getting sponsor info: ")
            print_compact_stack("trouble getting sponsor info: ")

def findSponsor(keyword):
    if not _sponsors.has_key(keyword):
        return _defaultSponsor
    return random.choice(_sponsors[keyword])
