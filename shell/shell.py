#! /usr/bin/env python3

import os, sys, time, re, fileinput

pid = os.getpid()               # get and remember pid
usrIn = input("$ ")
initDir = os.getcwd()

#check for exit Command
while usrIn != "exit":

    #check if CD Command
    args = usrIn.split()
    
    if len(args) == 0:
        os.write(2, ("Empty Command\n").encode())
    
    elif 'cd' in args:
        os.chdir(args[1])
    
    else:   
        rc = os.fork()

        #fork failure check
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)
        
        #child process
        elif rc == 0:                   # child
            #ouput redirection override
            if '>' in args:
                os.close(1)                 # redirect child's stdout
                sys.stdout = open(args[len(args) - 1], "w+")
                fd = sys.stdout.fileno() 
                os.set_inheritable(fd, True)
                
                i = 0
                temp = []
                while args[i] != '>':
                    temp.append(args[i])
                    i += 1
                args = temp

                for dir in re.split(":", os.environ['PATH']): # try each directory in path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 

                os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error
            
            #ouput redirection append
            elif '>>' in args:
                os.close(1)                 # redirect child's stdout
                sys.stdout = open(args[len(args) - 1], "a+")
                fd = sys.stdout.fileno() 
                os.set_inheritable(fd, True)
                
                i = 0
                temp = []
                while args[i] != '>>':
                    temp.append(args[i])
                    i += 1
                args = temp
                
                for dir in re.split(":", os.environ['PATH']): # try each directory in path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly 

                os.write(2, ("Child:    Error: Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error
            
            #input redirection 
            elif '<' in args:
                inFile = open(args[len(args) - 1], "r")
                #target = inFile.readline().rstrip("\n\r")#.split("\n")
                
                i = 0
                temp = []
                while args[i] != '<':
                    temp.append(args[i])
                    i += 1
                args = temp
                for line in inFile:
                    args.append(line.rstrip("\n\r"))

                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

                os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error
                
            #pipe handling
            elif '|' in args:
                r, w = os.pipe() 
                for f in (r, w):
                    os.set_inheritable(f, True)
                processid = os.fork()
                
                if processid < 0:
                    os.write(2, ("fork failed, returning %d\n" % rc).encode())
                    sys.exit(1)

                elif processid == 0:
                    os.close(1)
                    d = os.dup(w)
                    os.set_inheritable(d, True)
                    
                    i = 0
                    temp = []
                    while args[i] != '|':
                        temp.append(args[i])
                        i += 1
                    args = temp
                    
                    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                        program = "%s/%s" % (dir, args[0])
                        try:
                            os.execve(program, args, os.environ) # try to exec program
                        except FileNotFoundError:             # ...expected
                            pass                              # ...fail quietly

                    os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                    sys.exit(1)                 # terminate with error
                    
                else: 
                    os.wait()
                    os.close(0)
                    d = os.dup(r)
                    os.set_inheritable(d, True)
                    
                    i = 0
                    temp = []
                    while args[i] != '|':
                        i += 1
                    i+=1
                    
                    while i != len(args):
                        temp.append(args[i])
                        i += 1
                    args = temp
                    
                    for fd in (w, r):
                        os.close(fd)
                    for line in fileinput.input():
                        args.append(line.rstrip("\n\r"))
                   
                    for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                        program = "%s/%s" % (dir, args[0])
                        try:
                            os.execve(program, args, os.environ) # try to exec program
                        except FileNotFoundError:             # ...expected
                            pass                              # ...fail quietly

                    os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                    sys.exit(1)                 # terminate with error
               
            #commmands without any I/O redirection or piping
            else:
                for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                    program = "%s/%s" % (dir, args[0])
                    try:
                        os.execve(program, args, os.environ) # try to exec program
                    except FileNotFoundError:             # ...expected
                        pass                              # ...fail quietly

                os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
                sys.exit(1)                 # terminate with error

        #parent process
        else:                           # parent (forked ok)
            childPidCode = os.wait()
            #os.write(1, ("Parent: Child %d terminated with exit code %d\n" % 
            #            childPidCode).encode())
    
    os.write(1, ("#########################################################\n").encode())
    usrIn = input("$ ")

os.chdir(initDir)
