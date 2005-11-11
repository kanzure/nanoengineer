#!/usr/bin/python

import os, smtplib

tarballURLs = {
    "cad.tar.gz": "http://cvsdude.org/download.pl?id=xAWFjEtta9XaU",
    "sim.tar.gz": "http://cvsdude.org/download.pl?id=nfOzBTt5Tc2SU",
    "Distribution.tar.gz": "http://cvsdude.org/download.pl?id=exfgjuyj9e1afuck4tpdnsdebayfj30y",
    "Bugzilla.tar.gz": "http://mirror1.cvsdude.com/download.pl?id=p3kowosctuqqfud82rzttmtfbey7ogb5"
    }

DEST_DIR = "/tmp/tarballs"
MYSELF = "Will Ware <wware@alum.mit.edu>"
LISTENERS = [
    MYSELF
    # whoever else might want to know
    ]

class BadDownload(Exception):
    pass

def system(cmd):
    if os.system(cmd) != 0:
        raise BadDownload, cmd

def getTarballs():
    system("rm -rf " + DEST_DIR)
    system("mkdir " + DEST_DIR)
    for tarball in tarballURLs.keys():
        url = tarballURLs[tarball]
        tarballPath = DEST_DIR + "/" + tarball
        cmd = "wget -O %s %s" % (tarballPath, url)
        system(cmd)

HAPPY_MESSAGE = {
    "Subject": "Your tarballs are ready!",
    "Text": "Tarballs available at " + DEST_DIR
    }

SAD_MESSAGE = {
    "Subject": "Your tarballs were NOT downloaded!",
    "Text": "Please run getTarballs.py by hand and investigate"
    }

def sendEmail(message, debug=False):
    smtpserver = "smtp.rcn.com"
    username = "wware1"
    password = "Grendel9"
    fromaddr = MYSELF
    toaddrs = LISTENERS
    msg = "From: %s\r\n" % fromaddr
    msg += "To: %s\r\n" % (", ".join(toaddrs))
    msg += "Subject: %s\r\n" % message["Subject"]
    msg += "\r\n"
    msg += "%s\r\n" % message["Text"]
    server = smtplib.SMTP(smtpserver)
    server.login(username, password)
    if debug: server.set_debuglevel(1)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()

try:
    getTarballs()
    sendEmail(HAPPY_MESSAGE)
except BadDownload, e:
    SAD_MESSAGE["Text"] = "Command failed in getTarballs.py: " + e.args[0]
    sendEmail(SAD_MESSAGE)
