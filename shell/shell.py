# Copyright (c) 2020 Melina Salazar-Perez
#
# This program build a basic user shell for a Unix operating system
#
# Author Melina Salazar-Perez
# Version 1.0
# Lab 1

import re       # regular expression tools
import sys      # command line arguments
import os       # interacting with the operating system


def fork(args):
    pid = os.getpid()  # get and remember pid
    rc = os.fork()  # set rc to fork

    if rc < 0:  # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child
        for dir in re.split(":", os.environ['PATH']):  # check for environment variables
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)
            except FileNotFoundError:
                pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # if command not found print error
        sys.exit(1)

    else:
        childPid = os.wait()  # wait for child to fork


while True:
    if 'PS1' in os.environ:  # check and add prompt string to shell
        os.write(1, os.environ['PS1'].encode())
    try:
        userInput = input()  # Get user input
    except EOFError:
        sys.exit(1)
    except ValueError:
        sys.exit(1)

    args = userInput.split()  # Split user input into array

    if "exit" in userInput:  # Exit command
        sys.exit(0)

    if "cd" in args[0]:  # Change directories
        try:
            os.chdir(args[1])  # change directory
        except FileNotFoundError:
            os.write(1, ("cd: %s: No such file or directory\n" % args[1]).encode())
            pass
    else:
        fork(args)  # Handle commands
