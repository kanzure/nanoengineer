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
from debug import print_compact_traceback
from HistoryWidget import redmsg

def open_wiki_help_page( featurename, actually_open = True ): #e actually_open = False is not yet used (and untested) as of 051201
    """Open the wiki help page corresponding to the named nE-1 feature, in ways influenced by user preferences.
    Assume the featurename might contain blanks, but contains no other characters needing URL-encoding.
    [In the future, we might also accept options about the context or specific instance of the feature,
     which might turn into URL-anchors or the like.]
       If actually_open = False, don't open a web browser, but instead
    print a history message so the user can open it manually.
    Intended use is for a user preference setting to pass this, either always
    or when the feature is invoked in certain ways.
    """
    url = wiki_help_url( featurename)
    if url:
        if actually_open:
            env.history.message("Wiki help: opening " + url) # see module docstring re "wiki help" vs. "web help"
                # print this in case user wants to open it manually or debug the url prefix preference,
                # and to lessen their surprise if they didn't expect the help command to fire up their browser
            try:
                import webbrowser
                webbrowser.open( url)
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
        else:
            env.history.message("Help for %r is available at: %s" % (featurename, url))
    return

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
    from prefs_constants import wiki_help_prefix_prefs_key
    prefix = env.prefs[wiki_help_prefix_prefs_key]
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
        open_wiki_help_page( featurename)
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

#############################################

_keep_reference = None

class WikiHelpBrowser(QTextBrowser):
    def __init__(self,text,parent=None):
        class MimeFactory(QMimeSourceFactory):
            def data(self,name,context=None):
                # [obs comment:] You'll always get a warning like this:
                # QTextBrowser: no mimesource for http://....
                # This could be avoided with QApplication.qInstallMsgHandler,
                # but I don't think that's supported until PyQt 3.15. Also this falls
                # victim to all the problems swarming around webbrowser.open().
                import webbrowser
                webbrowser.open(str(name))
                self.owner.close()
                    # (remove this if you want the dialog to stay open after the link is clicked,
                    #  but its text will change to "link was clicked" due to the code below)
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
        # make it pale yellow like a post-it note
        self.setText("<qt bgcolor=\"#FFFF80\">" + text)
        self.mf = mf = MimeFactory()
        mf.owner = self
        self.setMimeSourceFactory(mf)

# This is a provisional stub. Feel free to edit.
def wikiPage(topic):
    fmt = "http://www.nanoengineer-1.net/mediawiki/index.php?title="
    topic1 = topic[:1].upper() + topic[1:]
    topic1 = topic1.replace(" ", "_")
    return " <a href=\"" + fmt + topic1 + "\">" + topic + "</a> "

def __testWikiHelpBrowser():
    import sys
    app = QApplication(sys.argv)
    w = WikiHelpBrowser("Here is a wiki page about " +
                        wikiPage("QWhatsThis and web links") +
                        " to click.")
    w.show()
    app.connect(app, SIGNAL("lastWindowClosed()"),
                app, SLOT("quit()"))
    app.exec_loop()

if __name__=="__main__":
    __testWikiHelpBrowser()
    
# end
