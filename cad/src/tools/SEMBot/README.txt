
# @author: Brian (of entire SEMBot), Bruce (of some readme text)
# @version: $Id$
#

How to run:

1. Login

2. $ cd httpdocs/Engineering

3a. $ ./runPylint.sh  to run pylint alone

   This doesn't include svn update, of source or tools.
   It prints a small amount of output and takes about 10 minutes.

  or

3b. $ ./runSEMBot.sh  to run everything

   This includes svn update of source and tools (even of that script file itself).
   It doesn't print anything except about the svn updates at the start --
   all output is stored in log files (visible on the web).
   Note: it doesn't update this overall log file --
     http://www.nanohive-1.org/Engineering/SEMBot.log
   instead it prints similar output.
   I guess that file is updated in the cron command line itself.
   
Make sure you don't run any of this at the same time 
as the nightly automatic run (5am ET) or as any other developer!

[end]
