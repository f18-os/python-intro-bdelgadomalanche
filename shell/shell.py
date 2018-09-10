#! /usr/bin/env python3

import os, sys, time, re

pid = os.getpid()               # get and remember pid
#os.write(1, ("About to fork (pid=%d)\n" % pid).encode())
usrIn = input("$ ")

while usrIn != "exit":

    rc = os.fork()
    args = usrIn.split()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        print(args)
        
        if len(args) == 1:
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
            #    os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly

            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error
        
        elif len(args) == 2:
            #os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
            #     (os.getpid(), pid)).encode())
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
            #    os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly

            os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error

        elif args[2] == '>':
            #os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % 
            #            (os.getpid(), pid)).encode())

            os.close(1)                 # redirect child's stdout
            sys.stdout = open(args[3], "w")
            fd = sys.stdout.fileno() # os.open("p4-output.txt", os.O_CREAT)
            os.set_inheritable(fd, True)
            #os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            args = [args[0], args[1]]

            for dir in re.split(":", os.environ['PATH']): # try each directory in path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:             # ...expected
                    pass                              # ...fail quietly 

            os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
            sys.exit(1)                 # terminate with error
        
        elif args[2] == '<':
            sys.exit(1)
            
        else:
            os.write(2, ("Unknown Command").encode())
            sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        #os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" % 
        #            (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
                    childPidCode).encode())
        os.write(1, ("#########################################################\n").encode())
    usrIn = input("$ ")
