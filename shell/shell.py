# Copyright (c) 2020 Melina Salazar-Perez
#
# This program build a basic user shell for a Unix operating system
#
# Author Melina Salazar-Perez
# Version 1.0
# Lab 1

#! /usr/bin/env  python3

import re  # regular expression tools
import sys  # command line arguments
import os  # interacting with the operating system


def fork(args):
    pid = os.getpid()  # get and remember pid
    rc = os.fork()     # set rc to fork
    stby = True

    # handle background tasks
    if "&" in args:
        args.remove("&")
        stby = False

    if rc < 0:  # capture error during fork
        os.write(2, ("Fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:  # child process

        if ">" in args or "<" in args:
            redirection(args)
        else:
            for dir in re.split(":", os.environ['PATH']):  # check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)
                except FileNotFoundError:
                    pass  # fail quietly

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # if command not found print error
        sys.exit(1)

    else:
        if stby:
            childPid = os.wait()  # wait for child to fork. childPid[0] = teminated child's process child[1] = exit sta
            if childPid[1] != 0 and childPid[1] != 256:
                os.write(2, ("Program terminated with exit code: %d\n" % childPid[1]).encode())


def redirection(args):
    # 1 output >
    if ">" in args:
        fileIndex = args.index('>') + 1  # Check for index of output
        fileName = args[fileIndex]       # Command name
        os.close(1)
        os.open(fileName, os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1, True)
        args.remove(fileName)
        args.remove('>')

    # 0 input '<'
    else:
        fileIndex = args.index('<') + 1  # Check for index of output
        fileName = args[fileIndex]  #
        os.close(0)
        os.open(fileName, os.O_RDONLY)
        os.set_inheritable(0, True)
        args.remove(fileName)
        args.remove('<')

    for dir in re.split(":", os.environ["PATH"]):  # try each directory in the path
        program = "%s/%s" % (dir, args[0])
        try:
            os.execve(program, args, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly

    os.write(2, ("command %s not found \n" % (args[0])).encode())
    sys.exit(1)  # terminate with error


def pipe(args):
    pid = os.getpid()  # get and remember pid

    pipe = args.index("|")  # check for pipe in command, returns index of pipe symbol

    pr, pw = os.pipe()  # Create a pipe, 'pr' pipe read(input), 'pw' pipe write(output)
    for f in (pr, pw):
        os.set_inheritable(f, True)

    rc = os.fork()  # ready to fork

    if rc < 0:
        print("fork failed, returning %d\n" % rc, file=sys.stderr)
        sys.exit(1)

    elif rc == 0:  # write to pipe from child
        args = args[:pipe]  # left pipe
        os.close(1)  # redirect child's stdout
        fd = os.dup(pw)  # duplicate file descriptor output
        os.set_inheritable(fd, True)
        for fd in (pr, pw):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # try to execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # try to execute program
                except FileNotFoundError:
                    pass
        os.write(2, ("%s: command not goun\n" % args[0]).encode())
        sys.exit(1)

    else:
        args = args[pipe + 1:]
        os.close(0)
        fd = os.dup(pr)  # duplicate file descriptor for output
        os.set_inheritable(fd, True)
        for fd in (pw, pr):
            os.close(fd)  # close file descriptor

        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)  # execute program
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']):  # Check for environment variables
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # execute program
                except FileNotFoundError:
                    pass

        os.write(2, ("%s: command not found\n" % args[0]).encode())  # return error if command was not found
        sys.exit(1)


while True:

    if 'PS1' in os.environ:      # check if the variable PS1 is set
        os.write(1, (os.environ['PS1']).encode())

    userInput = os.read(0, 256)  # Get user input. 0 = standrd input (keyboard) 256 bytes to read

    args = userInput.decode().split()  # Split user input into array

    if "exit" in args:  # Exit command
        sys.exit(0)
    if not args:
        continue
    elif "cd" in args[0]:  # Change directory
        try:
            os.chdir(args[1])
        except IndexError:
            os.write(1, " Error: Please provide a directory".encode())
        except FileNotFoundError:
            os.write(1, ("cd: %s: No such file or directory\n" % args[1]).encode())
            pass
    elif "|" in args:  # Handle pipe
        pipe(args)
    else:
        fork(args)  # Manage commands
