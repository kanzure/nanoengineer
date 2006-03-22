# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
wiki_help.py -- associate webpages (typically in a wiki) with program features,
and provide access to them. Pages typically contain feature-specific help info,
FAQ, forum, etc.

$Id$

Terminology note:

We use "web help" rather than "wiki help" in menu command text,
since more users will know what it means,
and since nothing in principle forces the web pages accessed this way to be wiki pages.

But we use "wiki help" in history messages, since we want people to think of the wiki
(rather than a rarely-changing web page) as an integral part of the idea.

History:

idea from Eric D

will 051010 added wiki help feature to Mode classes

bruce 051130 revised it

bruce 051201 made new source file for it, extended it to other kinds of objects (so far, some Node subclasses)
"""
__author__ = ["Will", "Bruce"]

from qt import *
import env
import webbrowser
from debug import print_compact_traceback
from HistoryWidget import redmsg

def webbrowser_open(url):
    if len(webbrowser._tryorder) == 0:
        # Sometimes webbrowser.py does not find a web browser. Also, its list
        # of web browsers is somewhat antiquated. Give it some help.
        def register(pathname, key):
            webbrowser._tryorder += [ key ]
            webbrowser.register(key, None,
                                webbrowser.GenericBrowser("%s '%%s'" % pathname))
        # Candidates are in order of decreasing desirability. Browser
        # names for different platforms can be mixed in this list. Where a
        # browser is not normally found on the system path (like IE on
        # Windows), give its full pathname. There is a working default for
        # Windows and Mac, apparently the only problem is when Linux has
        # neither "mozilla" nor "netscape".
        for candidate in [
            'firefox',
            'opera',
            'netscape',
            'konqueror',
            # 'c:/Program Files/Internet Explorer/iexplore.exe'
            ]:
            import os.path
            if os.path.exists(candidate):
                # handle candidates with full pathnames
                register(candidate, candidate)
                continue
            for dir in os.environ['PATH'].split(':'):
                pathname = os.path.join(dir, candidate)
                if os.path.exists(pathname):
                    register(pathname, candidate)
                    continue
    if False:
        # testing purposes only - simulate not finding a browser
        webbrowser._tryorder = [ ]
    # We should now have at least one browser available
    if len(webbrowser._tryorder) == 0:
        env.history.message(redmsg("Wiki Help cannot find a web browser"))
    webbrowser.open(url)

def open_wiki_help_dialog( featurename, actually_open = True ):
    #e actually_open = False is presently disabled in the implem
    """Show a dialog containing a link which can
    open the wiki help page corresponding to the named nE-1 feature, in ways influenced by user preferences.
    Assume the featurename might contain blanks, but contains no other characters needing URL-encoding.
    [In the future, we might also accept options about the context or specific instance of the feature,
     which might turn into URL-anchors or the like.]
       If actually_open = False [not yet implemented, probably won't ever be],
    don't open a web browser, but instead
    print a history message so the user can open it manually.
    Intended use is for a user preference setting to pass this, either always
    or when the feature is invoked in certain ways.
    """
    url = wiki_help_url( featurename)
    if url:
        #bruce 051215 experimental: always use the dialog with a link.
        # When this works, figure out how prefs should influence what to do, how to clean up the code, etc.
        # Other known issues:
        # - UI to access this is unfinished
        #   (F1 key, revise "web help" to "context help" in menu commands, access from Help menu)
        # - text is a stub;
        # - maybe need checkbox "retain dialog" so it stays open after the click
        # - doesn't put new dialog fully in front -- at least, closing mmkit brings main window in front of dialog
        # - dialog might be nonmodal, but if we keep that, we'll need to autoupdate its contents i suppose
        html = """Click one of the following links to launch your web browser
                  to a Nanorex wiki page containing help on the appropriate topic:<br>
                  * your current mode or selected jig: %s<br>
                  * nanoENGINEER-1 Wiki main page: %s
               """ % (HTML_link(url, featurename), HTML_link(wiki_prefix() + "Main_Page", "main page"))
                    #e in real life it'll be various aspects of your current context
        def clicked_func(url):
            worked = open_wiki_help_URL(url)
            ## close_dialog = worked # not good to not close it on error, unless text in dialog is preserved or replaced with error msg
            close_dialog = True
            return close_dialog
        parent = env.mainwindow() # WikiHelpBrowser now in a Dialog, so this works. Fixes bug 1235. mark060322
        w = WikiHelpBrowser(html, parent, clicked_func = clicked_func, caption = "Context Help")
        w.show()
        return
        ## if not actually_open: ## not yet used (and untested) as of 051201
        ##    env.history.message("Help for %r is available at: %s" % (featurename, url))
    return

def open_wiki_help_URL(url, whosdoingthis = "Wiki help"): #bruce 051229 split this out of open_wiki_help_dialog
    """Try to open the given url in the user's browser (unless they've set preferences to prevent this (NIM)),
    first emitting a history message containing the url
    (which is described as coming from whosdoingthis, which should be a capitalized string).
    Return True if there's no evidence of an error; print error message to history and return False if it definitely failed.
    """
    url = str(url) # precaution in case of QString
    ###e should check prefs to see if we should really open browser; if not, print different hist message
    env.history.message("%s: opening " % whosdoingthis + url) # see module docstring re "wiki help" vs. "web help"
        # print this in case user wants to open it manually or debug the url prefix preference
    try:
        webbrowser_open( url)
        worked = True
    except:
        #bruce 051201 catch exception to mitigate bug 1167
        # (e.g. when Linux user doesn't have BROWSER env var set).
        # Probably need to make this more intelligent, perhaps by
        # catching the specific exception in the bug report, knowing
        # the OS, passing options to webbrowser.open, etc.
        print_compact_traceback("webbrowser exception: ")
        env.history.message( redmsg("Problem opening web browser.") +
            "Suggest opening above URL by hand. "\
            "On some platforms, setting BROWSER environment variable might help."
         )
        worked = False
    return worked
    
def wiki_prefix():
    """Return the prefix to which wiki page titles should be appended, to form their urls.
    """
    from prefs_constants import wiki_help_prefix_prefs_key
    prefix = env.prefs[wiki_help_prefix_prefs_key]
    return prefix

def wiki_help_url( featurename):
    """Return a URL at which the wiki help page for the named feature (e.g. "Rotary Motor" or "Build Mode")
    might be found (or should be created), or '' if this is not a valid featurename for this purpose [NIM - validity not yet checked].
    Assume the featurename might contain blanks, but contains no other characters needing URL-encoding.
    [Note: in future, user prefs might include a series of wiki prefixes to try,
     so this API might need revision to return a series of URLs to try.]
    """
    # WARNING:
    # If this function's behavior is ever changed, lots of wiki pages might need to be renamed,
    # with both old and new names supported as long as the old code is in use.
    # (The same would be true for wiki pages about specific features whose featurenames are changed.)
    prefix = wiki_prefix()
    title = "Feature:" + featurename.replace(' ', '_') # e.g. Feature:Build_Mode
    return prefix + title # assume no URL-encoding needed in title, since featurenames so far are just letters and spaces

# ==

def featurename_for_object(object):
    """Return the standard "feature name" for the type of this object
    (usually for its class), or "" if none can be found.
       This is presently [051201] only used for wiki help,
    but in future might be used for other things requiring permanent feature names,
    like class-specific preference settings.
    """
    try:
        method = object.get_featurename
    except:
        return ""
    return method()

def wiki_help_menutext( featurename):
    "Return the conventional menu text for offering wiki help for the feature with the given name."
    return "web help: " + featurename # see module docstring re "wiki help" vs. "web help"

def wiki_help_lambda( featurename):
    "Return a callable for use as a menuspec command, which provides wiki help for featurename."
    def res(arg1=None, arg2=None, featurename = featurename):
        #k what args come in, if any? args of res might not be needed (though they would be if it was a lambda...)
        open_wiki_help_dialog( featurename)
    return res

def wiki_help_menuspec_for_object(object):
    fn = featurename_for_object(object)
    if fn:
        return wiki_help_menuspec_for_featurename( fn)
    return []

def wiki_help_menuspec_for_featurename( featurename):
    menutext = wiki_help_menutext( featurename)
    command = wiki_help_lambda( featurename)
    return [( menutext, command )]

# ==

_keep_reference = None

class WikiHelpBrowser(QDialog):
    """The WikiHelpBrowser Dialog.
    """
    def __init__(self, text, parent=None, clicked_func = None, caption = "(caption)"):
        QDialog.__init__(self,parent)

        self.setName("WikiHelpBrowser")
        TextBrowserLayout = QGridLayout(self,1,1,11,6,"WikiHelpBrowserLayout")
        self.text_browser = QTextBrowser(self,"text_browser")
        TextBrowserLayout.addMultiCellWidget(self.text_browser,0,0,0,1)
        
        class MimeFactory(QMimeSourceFactory):
            def data(self, name, context=None):
                # [obs comment:] You'll always get a warning like this:
                # QTextBrowser: no mimesource for http://....
                # This could be avoided with QApplication.qInstallMsgHandler,
                # but I don't think that's supported until PyQt 3.15. Also this falls
                # victim to all the problems swarming around webbrowser.open().
                name = str(name) # in case it's a QString
                if clicked_func:
                    close_dialog = clicked_func(name) #e might generalize to let clicked_func return new html to show, etc...
                else:
                    #bruce 051216 let this just be default clicked_func (for testing) -- let provided clicked_func do this itself
                    webbrowser_open(name) ###e should this be moved into clicked_func?
                    close_dialog = True
                if close_dialog:
                    # don't do this if you want the dialog to stay open after the link is clicked,
                    #  but its text will change to "link was clicked" due to the code below
                    ## self.owner.close() -- this caused hourglass cursor to remain in GLPane [bug 1233]
                    ## self.owner.hide() - also causes hourglass cursor
                    self.owner.deleteLater() # using deleteLater instead of close or hide fixed bug 1233 [bruce 051219]
                #bruce 051209 kluge:
                # one way to avoid the warning, in trusty old PyQt 3.12:
                ##   QMimeSourceFactory.defaultFactory().setText("arbuniqname","hi mom") 
                ##   res = QMimeSourceFactory.defaultFactory().data("arbuniqname") 
                # a simpler way, except that it doesn't work...
                ##   res = QTextDrag("hi")
                ##   print "res is",res
                ##   return res
                ## res is <__main__.qt.QTextDrag object at 0x1394120>
                ## pure virtual method called
                ## Abort
                ## Exit 134
                # let's try again and this time keep a reference to it -- ok, that works.
                # I didn't dare try to let the old one get discarded by a new one,
                # so we make at most one per apprun.
                global _keep_reference
                if _keep_reference is None:
                    _keep_reference = QTextDrag("link was clicked")
                return _keep_reference
        self.text_browser.setMinimumSize(400, 200)
        self.setCaption(caption) #bruce 051219 (fixes bug 1234)
        # make it pale yellow like a post-it note
        self.text_browser.setText("<qt bgcolor=\"#FFFF80\">" + text)
        self.mf = mf = MimeFactory()
        mf.owner = self
        self.text_browser.setMimeSourceFactory(mf)
        
        self.close_button = QPushButton(self,"close_button")
        self.close_button.setText("Close")
        TextBrowserLayout.addWidget(self.close_button,1,1)
        
        spacer = QSpacerItem(40,20,QSizePolicy.Expanding,QSizePolicy.Minimum)
        TextBrowserLayout.addItem(spacer,1,0)

        self.resize(QSize(300, 300).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.close_button,SIGNAL("clicked()"),self.close)
        

class WikiHelpBrowser_ORIG(QTextBrowser): # this is being used in real code as of bruce 051215
    def __init__(self, text, parent=None, clicked_func = None, caption = "(caption)"):
        class MimeFactory(QMimeSourceFactory):
            def data(self, name, context=None):
                # [obs comment:] You'll always get a warning like this:
                # QTextBrowser: no mimesource for http://....
                # This could be avoided with QApplication.qInstallMsgHandler,
                # but I don't think that's supported until PyQt 3.15. Also this falls
                # victim to all the problems swarming around webbrowser.open().
                name = str(name) # in case it's a QString
                if clicked_func:
                    close_dialog = clicked_func(name) #e might generalize to let clicked_func return new html to show, etc...
                else:
                    #bruce 051216 let this just be default clicked_func (for testing) -- let provided clicked_func do this itself
                    webbrowser_open(name) ###e should this be moved into clicked_func?
                    close_dialog = True
                if close_dialog:
                    # don't do this if you want the dialog to stay open after the link is clicked,
                    #  but its text will change to "link was clicked" due to the code below
                    ## self.owner.close() -- this caused hourglass cursor to remain in GLPane [bug 1233]
                    ## self.owner.hide() - also causes hourglass cursor
                    self.owner.deleteLater() # using deleteLater instead of close or hide fixed bug 1233 [bruce 051219]
                #bruce 051209 kluge:
                # one way to avoid the warning, in trusty old PyQt 3.12:
                ##   QMimeSourceFactory.defaultFactory().setText("arbuniqname","hi mom") 
                ##   res = QMimeSourceFactory.defaultFactory().data("arbuniqname") 
                # a simpler way, except that it doesn't work...
                ##   res = QTextDrag("hi")
                ##   print "res is",res
                ##   return res
                ## res is <__main__.qt.QTextDrag object at 0x1394120>
                ## pure virtual method called
                ## Abort
                ## Exit 134
                # let's try again and this time keep a reference to it -- ok, that works.
                # I didn't dare try to let the old one get discarded by a new one,
                # so we make at most one per apprun.
                global _keep_reference
                if _keep_reference is None:
                    _keep_reference = QTextDrag("link was clicked")
                return _keep_reference
        QTextBrowser.__init__(self,parent)
        self.setMinimumSize(400, 300)
        self.setCaption(caption) #bruce 051219 (fixes bug 1234)
        # make it pale yellow like a post-it note
        self.setText("<qt bgcolor=\"#FFFF80\">" + text)
        self.mf = mf = MimeFactory()
        mf.owner = self
        self.setMimeSourceFactory(mf)

def wiki_url_for_topic(topic, wikiprefix = None):
    wikiprefix = wikiprefix or "http://www.nanoengineer-1.net/mediawiki/index.php?title="
    topic1 = topic[:1].upper() + topic[1:]
    topic1 = topic1.replace(" ", "_") # assume no additional url-encoding is needed
    url = wikiprefix + topic1
    return url

def wikiPageHtmlLink(topic, text = None, wikiprefix = None):
    url = wiki_url_for_topic(topic, wikiprefix = wikiprefix)
    if text is None:
        text = topic
    return HTML_link(url, text)

def HTML_link(url, text): #e might need to do some encoding in url, don't know; certainly needs to in text, in principle
    # this is being used in real code as of bruce 051215
    return "<a href=\"" + url + "\">" + text + "</a>"

def __testWikiHelpBrowser():
    import sys
    app = QApplication(sys.argv)
    w = WikiHelpBrowser("Here is a wiki page about " +
                        wikiPageHtmlLink("QWhatsThis and web links") +
                        " to click.")
    w.show()
    app.connect(app, SIGNAL("lastWindowClosed()"),
                app, SLOT("quit()"))
    app.exec_loop()

if __name__=="__main__":
    __testWikiHelpBrowser()
    
# end