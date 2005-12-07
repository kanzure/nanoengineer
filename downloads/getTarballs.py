#!/usr/bin/python

"""This is a script to make tarballs of the Nanorex CVS repositories
maintained at cvsdude.org.
"""

import os, sys, smtplib

tarballURLs = {
    "cad.tar.gz": "http://cvsdude.org/download.pl?id=xAWFjEtta9XaU",
    "sim.tar.gz": "http://cvsdude.org/download.pl?id=nfOzBTt5Tc2SU",
    "Distribution.tar.gz": "http://cvsdude.org/download.pl?id=exfgjuyj9e1afuck4tpdnsdebayfj30y",
    "Bugzilla.tar.gz": "http://mirror1.cvsdude.com/download.pl?id=p3kowosctuqqfud82rzttmtfbey7ogb5"
    }
fileList = tarballURLs.keys()

WEBSERVER_DIR = "webserver2:/var/www/html/nanorex-tarballs"
TMP_DIR = "/tmp/tarballs"
ISOFILE = "/tmp/backupTarballs.iso"
MYSELF = "Will Ware <wware@alum.mit.edu>"
LISTENERS = [
    MYSELF
    # whoever else might want to know
    ]

class Message:
    def __init__(self, subject, text=None):
        self.subject = subject
        self.text = text
    def send(self, debug=False):
        smtpserver = "smtp.rcn.com"
        username = "wware1"
        password = "Grendel9"
        fromaddr = MYSELF
        toaddrs = LISTENERS
        msg = "From: %s\r\n" % fromaddr
        msg += "To: %s\r\n" % (", ".join(toaddrs))
        msg += "Subject: %s\r\n" % self.subject
        msg += "\r\n"
        msg += "%s\r\n" % self.text
        server = smtplib.SMTP(smtpserver)
        server.login(username, password)
        if debug: server.set_debuglevel(1)
        server.sendmail(fromaddr, toaddrs, msg)
        server.quit()


RESULT = Message(":(  Your tarballs are NOT ready, please investigate",
                 "Nothing happened yet")

class BadDownload(Exception):
    pass

def system(cmd):
    if os.system(cmd) != 0:
        raise BadDownload, cmd

def getTarballs():
    """Attempt to fetch CVS tarballs from cvsdude server. If unsuccessful,
        place an error message in SAD_MESSAGE.
    """
    global RESULT
    try:
        happy = Message(":)  Your tarballs are ready",
                        "cdrecord -v -speed=4 dev=ATAPI:0,0,0 %s\n   or\n" % ISOFILE)
        for filename in fileList:
            happy.text += "wget http://willware.net:8080/nanorex-tarballs/" + filename + "\n"
        system("rm -rf " + TMP_DIR)
        system("mkdir " + TMP_DIR)
        for tarball in tarballURLs.keys():
            url = tarballURLs[tarball]
            tarballPath = TMP_DIR + "/" + tarball
            cmd = "wget -O %s %s" % (tarballPath, url)
            system(cmd)
        system("mkisofs -J -R -o %s %s" % (ISOFILE, TMP_DIR))
        for file in fileList:
            system("scp %s/%s %s" % (TMP_DIR, file, WEBSERVER_DIR))
        RESULT = happy
    except BadDownload, e:
        RESULT.text = "Command failed in getTarballs.py: " + e.args[0]

##############################################
# Process command line

if __name__ == "__main__":

    def sendReminder():
        """Send a reminder to the user to do getTarballs by hand. I find that on
        my own machine, I can't run the whole process from a cron job. I don't know
        why, but my network doesn't seem to like it.
        """
        reminder = Message("Reminder to fetch CVS tarballs",
                           "Run the Distribution/downloads/getTarballs.py script")
        reminder.send()

    def sendResult():
        """If an error message has been placed in SAD_MESSAGE, then
        send it to let the user know that he needs to investigate why
        the download failed.
        """
        RESULT.send()

    def help():
        """print help information
        """
        print __doc__
        global options
        for opt in options:
            print opt.__name__ + "\n        " + opt.__doc__
        sys.exit(0)

    options = (sendReminder,
               getTarballs,
               sendResult,
               help)

    # Default behavior is to just do the very slow tests
    defaultArgs = ("getTarballs", "sendResult")

    args = sys.argv[1:]
    if len(args) < 1:
        args = defaultArgs

    class Found(Exception): pass

    for arg in args:
        try:
            for opt in options:
                if opt.__name__ == arg:
                    opt()
                    raise Found
            print "Don't understand command line arg:", arg
            print "Type:  %s help" % sys.argv[0]
            sys.exit(1)
        except Found:
            pass
