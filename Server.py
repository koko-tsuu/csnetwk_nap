from socket import *
import datetime
import os
import threading
import struct

# printing date with string passed
def print_date(message):
    now = datetime.datetime.now()
    print("<" + str(now) + "> " + message)

# append 4-byte length to every message
def send_data(s, data):
    data = struct.pack('>I', len(data)) + data.encode()
    s.sendall(data)

# unpack the message and get message length
def recv_data(s):
    raw_datalen = recv_all(s, 4)
    if not raw_datalen:
        return None
    data_len = struct.unpack('>I', raw_datalen)[0]
    return recv_all(s, data_len)

# helper function for recv_data
def recv_all(s, n):
    data = bytearray()
    while len(data) < n:
        packet = s.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def username_taken(username):
    for i in range(len(listOfUsers)):
        if(listOfUsers[i][0] == username):
            return i
    return -1

def send_msg(client_username, msg): 
    index = username_taken(client_username)
    if index != -1:
        getClientSocket = listOfUsers[index][2] # get the socket address for it
        try:
            send_data(getClientSocket, msg)
        except:
            return -2
        return 1
    else:
        return -1

def broadcast_msg(msg):
    try:
        for i in listOfUsers:
            if (i[0] != ''):
                send_msg(i[2], msg)
        return True
    except:
        return False

# function to be ran for the threading 
def threadServer(conn, address):

    # has the user registered?
    hasRegistered = False
    username = ''
    listOfUsers.append(('', address, conn))
    print_date(str(address[0]) + ' (' + str(address[1]) + "): Connected to the server.")

    while True:
        try:
            # get the command from the user
            userCommand = recv_data(conn).decode()
            userCommand = userCommand.split(" ")

            # user wants to disconnect from server
            if(userCommand[0] == "disconnect"):
                print_date(str(address[0]) + " (" + str(address[1]) + "): Received command to disconnect.")
                listOfUsers.remove((username, address, conn))
                conn.close()
                print_date(str(address[0]) + " (" + str(address[1]) + "): Closed connection.")

            # user wants to register
            elif(userCommand[0] == "register"):
                print_date(str(address[0]) + " (" + str(address[1]) + "): To register.")
                temp_username = userCommand[1]
                # user has already registered
                if (hasRegistered):
                    print_date(temp_username + " has already registered. Sending error to client.")
                    send_data(conn, "username_alreadyregistered")
                # username currently exists in active users
                elif (username_taken(temp_username) != -1):
                    print_date(temp_username + " is taken. Sending error to client.")
                    send_data(conn, "username_taken")
                # successfully registered
                else:
                    username = temp_username
                    print_date(str(address[0]) + " (" + str(address[1]) + "): Registered as " + username + ". Welcome!")
                    listOfUsers.remove(('', address, conn))
                    listOfUsers.append((username, address, conn))
                    send_data(conn, "success")

            elif(userCommand[0] == "store"):
                pass

            elif(userCommand[0] == "dir"):
                allFiles = [f for f in os.listdir(currentPath) if os.path.isfile(os.path.join(currentPath, f))]
                try:
                    index = 0
                    dirList = "\nFiles: " + str(len(allFiles)) + '\n'
                    if (len(allFiles) != 0):
                        for i in allFiles:
                            index += 1
                            dirList = dirList + '[' + str(index) + '] ' + (i) + '\n'
                    else:
                        dirList = dirList + 'No files in the server at the moment.\n'
                    send_data(conn, dirList)
                    print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Sent file list.")
                except:
                    print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Failed to send file list.")
            
            elif(userCommand[0] == "get"):
                pass

            elif(userCommand[0] == 'all'):
                try:
                    userMessage = recv_data(conn).decode()

                    status = broadcast_msg(userMessage)
                    if(status):
                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + "Sent message from " + username + ' to all active users.')
                        send_data(conn, 'success')
                    else:
                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message. Sending error.')
                        send_data(conn, 'broad_fail')
                except:
                    print_date(str(address[0]) + ' (' + str(address[1]) + '): Something went wrong in sending the message.')

            elif(userCommand[0] == 'active'):
                try:
                    index = 0
                    dirList = "\nCurrent users on the server: " + str(len(listOfUsers)) + '\n'
                    for i in listOfUsers:
                        index += 1
                        if (i[0] == ''):
                            dirList = dirList + '[' + str(index) + '] ' + '<no username>' + ' : ' + str(i[1][0]) + ' (' + str(i[1][1]) + ')' + '\n'
                        else:
                            dirList = dirList + '[' + str(index) + '] ' + str(i[0]) + ' : ' + str(i[1][0]) + ' (' + str(i[1][1]) + ')' + '\n'
                    send_data(conn, dirList)
                    print_date("Sent active user list to " + str(address[0]) + ' (' + str(address[1]) + ").")
                except:
                    print_date("Failed to send active user list to " + str(address[0]) + ' ' + str(address[1]) + ".")

            elif(userCommand[0] == 'dm'):
                try:
                    data = recv_data(conn).decode()
                    userMessage = data.split(" ")

                    status = send_msg(userMessage[0], userMessage[1])
                    if(status == 1):
                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + "Sent message from " + username + ' to  ' + userMessage[0])
                        send_data(conn, 'success')
                    elif(status == -1):
                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + userMessage[0] + ' does not exist. Sending error.')
                        send_data(conn, 'dm_notexist')
                    elif(status == -2):
                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the message. Sending error.')
                        send_data(conn, 'dm_msgfail')
                except:
                    print_date(str(address[0]) + ' (' + str(address[1]) + '): Something went wrong in sending the message.')
            
            # checking if server is alive for commands that need server connection
            elif(userCommand[0] == 'ping'):
                try:
                    send_data(conn, 'pong')
                except:
                    print_date("Something went wrong in pinging the client.")
                    conn.close()
                pass

        # client suddenly closed the connection
        except:
            print_date(str(address[0]) + ' (' + str(address[1]) + ") has unexpectedly disconnected. Socket will be closed.")
            try:
                listOfUsers.remove((username, address, conn))
                conn.close()
                print_date(str(address[0]) + ' (' + str(address[1]) + ") " +  "- Socket closed.")
                break
            except:
                print_date("Something went wrong in closing the socket.")
                break


        


########################################################################

os.system('cls')
currentPath = os.getcwd() + "\\server_directory"
pathExists = os.path.exists(currentPath)
if (not pathExists):
    os.makedirs(currentPath)
    print("[Setup] Server directory does not exist. Created a new directory server_directory.")


serverSocket = socket(AF_INET, SOCK_STREAM)

host = "localhost"
port = 6969

#host = input("[Setup] Host: ")
#port = input("[Setup] Port: ")
#port = int(port)

setupCorrectly = False
listOfUsers = []

try: 
    serverSocket.bind((host, port))
    setupCorrectly = True

 
except:
    print("[Error]: Something wrong has occurred in the server setup. Please check if you typed your host and port correctly.")

if(setupCorrectly):
        now = datetime.datetime.now()
        
        serverSocket.listen()
        print("<" + str(now) + "> Listening for any incoming connections on " + host + ":" + str(port))
        

        while True:
            try:
                conn, address = serverSocket.accept()

                # threading to serve multiple clients
                thread = threading.Thread(target=threadServer, args=(conn, address))
                thread.start()
            except:
                print('[Error]: Something went wrong in one of the client sockets.')
                