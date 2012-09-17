#!/usr/bin/env python
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.

"""
 Users place files into the INPUT directory and run batchsim.
 After a while, results appear in the OUTPUT directory.

 Each time batchsim is run, it scans the INPUT directory.  Each .mmp
 file it finds is moved into a consecutively numbered subdirectory
 of QUEUE.

 The user is prompted for simulation parameters (temp, steps per
 frame, frames), which are used to build a command string.  This
 command string is placed in the file 'run' in the same directory as
 the .mmp file.  The batchsim script then starts the queue runner, and
 prints the status of all submitted jobs.

 It is safe to run batchsim as often as you like without providing
 any input files.  This will just show you the status of job
 processing.  It can be placed in a crontab with the --run-queue
 option to suppress the input scanning and status printing.  This
 will restart the queue runner if it happens to have exited.

 The queue runner process is started with 'batchsim --run-queue'.  It
 exits immediately if there is already a queue runner process.
 Otherwise, it scans the QUEUE directory and finds the first job.
 This is moved to the RUN directory, and the job's 'run' file is
 executed.  When it exits, the job directory is moved to the OUTPUT
 directory, and the queue runner scans the QUEUE directory again.
 When it finds nothing in the QUEUE directory, it exits.
"""

import sys
import os
import time
import fcntl

baseDirectory = "/tmp/batchsim"

INPUT   = os.path.join(baseDirectory, "input")
OUTPUT  = os.path.join(baseDirectory, "output")
QUEUE   = os.path.join(baseDirectory, "queue")
CURRENT = os.path.join(baseDirectory, "current")

def nextJobNumber():
    nextFileName = os.path.join(QUEUE, "next")
    try:
        f = open(nextFileName)
        n = int(f.readline())
        f.close()
    except IOError:
        n = 0
    f = open(nextFileName, 'w')
    print >>f, "%d" % (n + 1)
    return "%05d" % n

def ask(question, default):
    """
      Ask the user a question, presenting them with a default answer.
      Return their answer or the default if they just entered a blank
      line.
    """
    print
    print "%s [%s]? " % (question, default), # suppress newline
    try:
        reply = sys.stdin.readline()
    except KeyboardInterrupt:
        print
        print "Aborted"
        sys.exit(1)
    if (reply.isspace()):
        return default
    return reply

def askInt(question, default):
    while (True):
        reply = ask(question, default)
        try:
            result = int(reply)
            return result
        except ValueError:
            print
            print "reply was not an integer: " + reply.strip()

def askFloat(question, default):
    while (True):
        reply = ask(question, default)
        try:
            result = float(reply)
            return result
        except ValueError:
            print
            print "reply was not a float: " + reply.strip()

def runJob(jobNumber):
    queuePath = os.path.join(QUEUE, jobNumber)
    currentPath = os.path.join(CURRENT, jobNumber)
    outputPath = os.path.join(OUTPUT, jobNumber)
    os.rename(queuePath, currentPath)
    os.chdir(currentPath)

    childStdin = open("/dev/null")
    childStdout = open("stdout", 'w')
    childStderr = open("stderr", 'w')
    os.dup2(childStdin.fileno(), 0)
    childStdin.close()
    os.dup2(childStdout.fileno(), 1)
    childStdout.close()
    os.dup2(childStderr.fileno(), 2)
    childStderr.close()

    run = open("run")
    for command in run:
        status = os.system(command)
        if (status):
            print >>sys.stderr, "command: %s\nexited with status: %d" % (command, status)
            break

    os.close(0)
    os.close(1)
    os.close(2)
    os.chdir("/")
    os.rename(currentPath, outputPath)

def processQueue():
    # First, we move anything from the current directory into output,
    # and consider those jobs to have failed.  The processQueue that
    # started these should have moved them to output itself, so
    # something must have gone wrong.  We abort rather than retrying,
    # so we can make progress on other jobs.

    fileList = os.listdir(CURRENT)
    fileList.sort()
    for jobNumber in fileList:
        if (jobNumber.isdigit()):
            jobPath = os.path.join(CURRENT, jobNumber)
            failed = open(os.path.join(jobPath, "FAILED"), 'w')
            print >>failed, "The queue processor exited without completing this job."
            failed.close()
            os.rename(jobPath, os.path.join(OUTPUT, jobNumber))

    # Now, we check to see if there's anything in the queue directory.
    # If so, we move the first job to current, and execute it's run
    # file.  Move the results to the output directory and scan again
    # after the run file completes.

    while (True):
        gotOne = False
        fileList = os.listdir(QUEUE)
        fileList.sort()
        for jobNumber in fileList:
            if (jobNumber.isdigit()):
                gotOne = True
                runJob(jobNumber)
                break
        if (not gotOne):
            break

def runQueue():
    # fork and lock, exiting immediately if another process has the lock
    pid = os.fork()
    if (pid):
        # parent
        time.sleep(0.2) # seconds
        # by this time, a simulator sub-process should have been started
    else:
        # child
        lockFileName = os.path.join(QUEUE, "lock")
        lockFile = open(lockFileName, 'w')
        lockFD = lockFile.fileno()
        try:
            fcntl.flock(lockFD, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            os._exit(0)
        processQueue()
        os._exit(0)

def scanInput():
    fileList = os.listdir(INPUT)
    fileList.sort()
    for fileName in fileList:
        if (fileName.endswith(".mmp")):
            baseName = fileName[:-4]
            print "processing " + baseName

            dirInQueue = os.path.join(QUEUE, nextJobNumber())
            os.mkdir(dirInQueue)
            os.rename(os.path.join(INPUT, fileName), os.path.join(dirInQueue, fileName))
            runFile = open(os.path.join(dirInQueue, "run"), 'w')

            minimize = ask("[M]inimize or [D]ynamics", "D").strip().lower()
            if (minimize.startswith("m")):

                end_rms = askFloat("Ending force threshold (pN)", 50.0)
                useGromacs = ask("Use [G]romacs (required for DNA) or [N]D-1 (required for double bonds)", "G").strip().lower()
                if (useGromacs.startswith("g")):
                    hasPAM = ask("Does your model contain PAM atoms (DNA)? (Y/N)", "Y").strip().lower()
                    hasPAM = hasPAM.startswith("y")
                    if (hasPAM):
                        vdwCutoffRadius = 2
                    else:
                        vdwCutoffRadius = -1
                    doNS = ask("Enable neighbor searching? [Y]es (more accurate)/[N]o (faster)", "N").strip().lower()
                    if (doNS.startswith("y")):
                        neighborSearching = 1
                    else:
                        neighborSearching = 0
                    print >>runFile, "simulator -m --min-threshold-end-rms=%f --trace-file %s-trace.txt --write-gromacs-topology %s --path-to-cpp /usr/bin/cpp --system-parameters %s/control/sim-params.txt --vdw-cutoff-radius %f --neighbor-searching %d %s" \
                          % (end_rms, baseName, baseName, baseDirectory, vdwCutoffRadius, neighborSearching, fileName)

                    print >>runFile, "grompp -f %s.mdp -c %s.gro -p %s.top -n %s.ndx -o %s.tpr -po %s-out.mdp" \
                          % (baseName, baseName, baseName, baseName, baseName, baseName)

                    if (hasPAM):
                        tableFile = "%s/control/yukawa.xvg" % baseDirectory
                        table = "-table %s -tablep %s" % (tableFile, tableFile)
                    else:
                        table = ""

                    print >>runFile, "mdrun -s %s.tpr -o %s.trr -e %s.edr -c %s.xyz-out.gro -g %s.log %s" \
                          % (baseName, baseName, baseName, baseName, baseName, table)
                else:
                    print >>runFile, "simulator -m --system-parameters %s/control/sim-params.txt --output-format-3 --min-threshold-end-rms=%f --trace-file %s-trace.txt %s" \
                          % (baseDirectory, end_rms, baseName, fileName)
            else:
                temp = askInt("Temperature in Kelvins", 300)
                stepsPerFrame = askInt("Steps per frame", 10)
                frames = askInt("Frames", 900)
                print
                print "temp %d steps %d frames %d" % (temp, stepsPerFrame, frames)

                print >>runFile, "simulator  --system-parameters %s/control/sim-params.txt --temperature=%d --iters-per-frame=%d --num-frames=%d --trace-file %s-trace.txt %s" \
                      % (baseDirectory, temp, stepsPerFrame, frames, baseName, fileName)
        else:
            print "ignoring " + os.path.join(INPUT, fileName)

def showOneJob(dirName, jobNumber):
    fileList = os.listdir(dirName)
    fileList.sort()
    for fileName in fileList:
        if (fileName.endswith(".mmp")):
            print "    %s %s" % (jobNumber, fileName)

def showJobsInDirectory(dirName, header):
    gotOne = False
    fileList = os.listdir(dirName)
    fileList.sort()
    for jobNumber in fileList:
        if (jobNumber.isdigit()):
            if (not gotOne):
                print header
                gotOne = True
            showOneJob(os.path.join(dirName, jobNumber), jobNumber)

def showStatus():
    showJobsInDirectory(QUEUE, "\nJobs queued for later processing:\n")
    showJobsInDirectory(CURRENT, "\nCurrently executing job:\n")
    showJobsInDirectory(OUTPUT, "\nCompleted jobs:\n")
    gotProcess = False
    ps = os.popen("ps ax")
    header = ps.readline()
    for process in ps:
        if (process.find("simulator") > 0 or process.find("grompp") > 0 or process.find("mdrun") > 0):
            if (not gotProcess):
                print
                print "Currently running simulator processes:"
                print
                print header.strip()
                gotProcess = True
            print process.strip()
    if (not gotProcess):
        print
        print "No simulator processes running."

def makeDirectory(path):
    if (os.access(path, os.W_OK)):
        return
    os.makedirs(path)

def main():
    makeDirectory(INPUT)
    makeDirectory(QUEUE)
    makeDirectory(CURRENT)
    makeDirectory(OUTPUT)
    if (len(sys.argv) > 1 and sys.argv[1] == '--run-queue'):
        runQueue()
    else:
        print
        scanInput()
        runQueue()
        showStatus()
        print

if (__name__ == '__main__'):
    main()
