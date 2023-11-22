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

def send_msg(getClientSocket, msg): 
    try:
        send_data(getClientSocket, msg)
    except:
        return -1
    return 1

def broadcast_msg(msg):
    try:
        for i in listOfUsers:
            send_msg(i[2], msg)
        return True
    except:
        return False
    
# printing errors, pass the number to display the respective error.
def errorPrinting(errNum):
  now = datetime.datetime.now()
  msg = "<" + str(now) + "> [Error " + str(errNum) + "] : "
  error = ""
  if(errNum == 1):       # wrong ip address or port number
      error = "Connection to the Server has failed! Please check IP Address and Port Number. Otherwise, the server may not be active at the moment."
  elif(errNum == 2):     # disconnection failed, user hasn't connected yet
      error = "Disconnection failed. Please connect to the server first."
  elif(errNum == 3):     # username already exists
      error = "Registration failed. Handle or alias already exists."
  elif(errNum == 4):
      error = "File not found."
  elif(errNum == 5):
      error = "File not found in the server."
  elif(errNum == 6):
      error =  "Command not found."
  elif(errNum == 7):
       error = "Command parameters do not match or is not allowed."
  elif(errNum == 8):
       error = "Please register first before sending or requesting files."
  elif(errNum == 9):
       error = "You're already connected to a server."
  elif(errNum == 10):
       error = "To use this command, you need to be connected to a server first."
  elif(errNum == 11):
       error =  "You have already registered."
  elif(errNum == 12):
       error = "Username is empty."
  elif(errNum == 13):
       error = "To use this command, you need to register first."
  elif(errNum == 14):
       error = "Something went wrong in disconnecting."
  elif(errNum == 15):
       error = "Something went wrong in requesting file list."
  elif(errNum == 16):
       error = "Something went wrong in requesting active user list."
  elif(errNum == 17):
       error = "Something went wrong in requesting and downloading the file."
  elif(errNum == 18):
       error = "Something went wrong in registering the username."
  elif(errNum == 19):
       error = "Something went wrong with the server connection. Closing socket."
  elif(errNum == 20):
       error = "Something went wrong with sending a direct message."
  elif(errNum == 21):
       error = "Something went wrong with broadcasting the message."
  elif(errNum == 22):
       error = "The user to be messaged does not exist. Please make sure to check if you wrote the username correctly."
  msg = msg + error
  return msg

# function to be ran for the threading 
def threadServer(conn, address):

    # has the user registered?
    hasRegistered = False
    username = ''
    listOfUsers.append(('', address, conn))
    print_date(str(address[0]) + ' (' + str(address[1]) + "): Connected to the server.")
    now = datetime.datetime.now()
    broadcast_msg("<" + str(now) + "> " + str(address[0]) + ' (' + str(address[1]) + ") " + "has joined the server.")

    while True:
        try:
            # get the command from the user
            userCommand = recv_data(conn)

            if userCommand:
                userCommand = userCommand.decode()
                userCommand = userCommand.split(" ")

                # user wants to disconnect from server
                if(userCommand[0] == "disconnect"):
                    print_date(str(address[0]) + " (" + str(address[1]) + "): Received command to disconnect.")
                    listOfUsers.remove((username, address, conn))
                    conn.close()
                    print_date(str(address[0]) + " (" + str(address[1]) + "): Closed connection.")
                    now = datetime.datetime.now()
                    broadcast_msg("<" + str(now) + "> " + str(address[0]) + ' (' + str(address[1]) + ") has disconnected.")

                # user wants to register
                elif(userCommand[0] == "register"):
                    print_date(str(address[0]) + " (" + str(address[1]) + "): To register.")
                    temp_username = userCommand[1]
                    now = datetime.datetime.now()
                    # user has already registered
                    if (hasRegistered):
                        send_data(conn, "<" + str(now) + "> " + str(address[0]) + " (" + str(address[1]) + "): " + temp_username + " has already registered.")
                        print_date(str(address[0]) + " (" + str(address[1]) + "): You already have registered.")
                    # username currently exists in active users
                    elif (username_taken(temp_username) != -1):
                        send_data(conn, "<" + str(now) + "> " + str(address[0]) + " (" + str(address[1]) + "): " + temp_username + " is taken.")
                        print_date(str(address[0]) + " (" + str(address[1]) + "): " + temp_username + " is taken. Sending error to client.")
                    # successfully registered
                    else:
                        username = temp_username
                        hasRegistered = True
                        print_date(str(address[0]) + " (" + str(address[1]) + "): Registered as " + username + ". Welcome!")
                        broadcast_msg("<" + str(now) + ">" + " [Registration] Welcome, " + username + "!")
                        listOfUsers.remove(('', address, conn))
                        listOfUsers.append((username, address, conn))
                       

                elif(userCommand[0] == "store"):
                    pass

                elif(userCommand[0] == "dir"):
                    if(hasRegistered):
                        allFiles = [f for f in os.listdir(currentPath) if os.path.isfile(os.path.join(currentPath, f))]
                        now = datetime.datetime.now()
                        index = 0
                        dirList = "\n[Date & Time: " + str(now) +"]\n\nFiles: " + str(len(allFiles)) + '\n'
                        if (len(allFiles) != 0):
                            for i in allFiles:
                                index += 1
                                dirList = dirList + '[' + str(index) + '] ' + (i) + '\n'
                        else:
                            dirList = dirList + 'No files in the server at the moment.\n'

                        try:
                            send_data(conn, dirList)
                            print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Sent file list.")
                        except:
                            print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Failed to send file list.")
                    else:
                        send_data(conn, errorPrinting(13))
                      
                
                elif(userCommand[0] == "get"):
                    pass

                elif(userCommand[0] == 'all'):
                    if(hasRegistered):
                        try:
                            userMessage = recv_data(conn).decode()

                            status = broadcast_msg(userMessage)
                            if(not status):
                                send_data(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                                print_date(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                        except:
                            print_date(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                    else:
                        send_data(conn, errorPrinting(13))

                elif(userCommand[0] == 'active'):
                    if(hasRegistered):
                        try:
                            now = datetime.datetime.now()
                            index = 0
                            dirList = "\n[Date & Time: " + str(now) + "]\n\nCurrent users on the server: " + str(len(listOfUsers)) + '\n'
                            for i in listOfUsers:
                                index += 1
                                if (i[0] == ''):
                                    dirList = dirList + '[' + str(index) + '] ' + '<no username>' + ' : ' + str(i[1][0]) + ' (' + str(i[1][1]) + ')' + '\n'
                                else:
                                    dirList = dirList + '[' + str(index) + '] ' + str(i[0]) + ' : ' + str(i[1][0]) + ' (' + str(i[1][1]) + ')' + '\n'
                            send_data(conn, dirList)   
                        except:
                            print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Failed to send active user list.")
                    else:
                        send_data(conn, errorPrinting(13))

                elif(userCommand[0] == 'dm'):
                    if(hasRegistered):
                        try:
                            data = recv_data(conn).decode()
                            userMessage = data.split(" ", 1)
                            userIndex = username_taken(userMessage[0])
                        
                            if (userMessage[0] != username):
                                if(userIndex != -1):
                                    status = send_msg(listOfUsers[userIndex][2], userMessage[1])
                                    send_msg(conn, userMessage[1])
                                    if(status == 1):
                                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + "Sent message from " + username + ' to ' + userMessage[0] + '.')
                                    else:
                                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the message.')
                                        send_data(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the message.'))
                                else:
                                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + userMessage[0] + ' does not exist. Sending error.')
                                        send_data(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + userMessage[0] + ' does not exist. Check if you typed their username correctly. Usernames are case sensitive.'))
                            else:
                                send_data(conn, "<" + str(now) + "> " + str(address[0]) + ' (' + str(address[1]) + '): '+ 'Oops, you are messaging to yourself!') 
                            
                        except:
                            print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the message.')
                    else:
                        send_data(errorPrinting(13)) 


        # client suddenly closed the connection
        except:
            print_date(str(address[0]) + ' (' + str(address[1]) + ") has unexpectedly disconnected. Socket will be closed.")
            try:
                now = datetime.datetime.now()
                broadcast_msg("<" + str(now) + "> " + str(address[0]) + ' (' + str(address[1]) + ") has disconnected.")
                listOfUsers.remove((username, address, conn))
                conn.close()
                print_date(str(address[0]) + ' (' + str(address[1]) + ")" +  ": Socket closed.")
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
                