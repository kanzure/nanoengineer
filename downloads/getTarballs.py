#!/usr/bin/python

import os, smtplib

tarballURLs = {
    "cad.tar.gz": "http://cvsdude.org/download.pl?id=xAWFjEtta9XaU",
    "sim.tar.gz": "http://cvsdude.org/download.pl?id=nfOzBTt5Tc2SU",
    "Distribution.tar.gz": "http://cvsdude.org/download.pl?id=exfgjuyj9e1afuck4tpdnsdebayfj30y",
    "Bugzilla.tar.gz": "http://mirror1.cvsdude.com/download.pl?id=p3kowosctuqqfud82rzttmtfbey7ogb5"
    }

WEBSERVER_DIR = "webserver2:/var/www/html/nanorex-tarballs"
DEST_DIR = "/tmp/tarballs"
ISOFILE = "/tmp/backupTarballs.iso"
MYSELF = "Will Ware <wware@alum.mit.edu>"
LISTENERS = [
    MYSELF
    # whoever else might want to know
    ]

HAPPY_MESSAGE = {
    "Subject": "Your tarballs are ready   :)",
    "Text": "cdrecord -v -speed=4 dev=ATAPI:0,0,0 %s/%s" % (DEST_DIR, ISOFILE)
    }

SAD_MESSAGE = {
    "Subject": "Your tarballs are NOT ready  :(",
    "Text": "Please run getTarballs.py by hand and investigate"
    }

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
    system("mkisofs -J -l -r -o %s %s" % (ISOFILE, DEST_DIR))
    system("mv %s %s" % (ISOFILE, DEST_DIR))
    system("scp %s/* %s" % (DEST_DIR, WEBSERVER_DIR))

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
