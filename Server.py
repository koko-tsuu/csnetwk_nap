from socket import *
import datetime
import os
import threading
import struct

# printing date with string passed, default string value is empty
def print_date(message=''):
    now = datetime.datetime.now()
    print("<" + str(now) + "> " + message)

# append 4-byte length to every message
# python does not know what is the end of a recv, so this method + recv_data was created
def send_data(s, data):
    data = struct.pack('>I', len(data)) + data.encode()
    s.sendall(data)

# unpack the message and get message length, recieve all data
def recv_data(s):
    raw_datalen = recv_all(s, 4)
    if not raw_datalen:
        return None
    data_len = struct.unpack('>I', raw_datalen)[0]
    return recv_all(s, data_len)

# helper function for recv_data, receives data until its length is equal to length of message
def recv_all(s, n):
    data = bytearray()
    while len(data) < n:
        packet = s.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

# check if username is taken
def username_taken(username):
    for i in range(len(listOfUsers)):
        if(listOfUsers[i][0] == username):
            return i
    return -1

# function to signal if something went wrong in sending a message
def send_msg(getClientSocket, msg): 
    try:
        send_data(getClientSocket, msg)
    except:
        return -1
    return 1

# for each user, send the message to them
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
  
# any input to close server
def shutServer(serverSocket):
    input()
    serverSocket.close()
    os._exit(0)

# function to be ran for the threading 
def threadServer(conn, address):

    hasRegistered = False                                                                   # has the user registered?
    username = ''                                                                           # current username
    listOfUsers.append(('', address, conn))                                                 # add to list of active users
    print_date(str(address[0]) + ' (' + str(address[1]) + "): Connected to the server.")    # status message

    while True:
        try:
            # get the command from the user
            userCommand = recv_data(conn)

            # if not empty
            if userCommand:
                userCommand = userCommand.decode()
                userCommand = userCommand.split(" ")         #[1:] is extra parameters

                # user wants to register
                if(userCommand[0] == "register"):
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
                       
                # store files of user
                elif(userCommand[0] == "store"):

                    try:
                        # get file name and file data
                        filename = recv_data(conn).decode()
                        fileData = recv_data(conn).decode()

                        # concat server directory path and filename
                        fileCopyPath = currentPath + '\\' + filename

                        # create a file and write the contents from file data
                        with open(fileCopyPath, 'w') as fileCopy:
                            fileCopy.write(fileData)

                        # status of file sendings
                        now = datetime.datetime.now()
                        send_data(conn, "<" + str(now) + "> Server has successsfully received " + filename + '.')
                        print_date(str(address[0]) + " (" + str(address[1]) + "): Received file from " + username + ". Stored file in server directory.")

                    # error in receiving file
                    except:
                        print_date(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in receiving the file from the user.'))

                # get file directory of server
                elif(userCommand[0] == "dir"):

                    # check if user is registered
                    if(hasRegistered):

                        # for everything in the server directory, if it's a file then add to the array
                        allFiles = [f for f in os.listdir(currentPath) if os.path.isfile(os.path.join(currentPath, f))]

                        # just some stuff to format the list better
                        now = datetime.datetime.now()
                        index = 0
                        dirList = "\n[Date & Time: " + str(now) +"]\n\nFiles: " + str(len(allFiles)) + '\n'

                        # print depending on the number of files in the directory
                        if (len(allFiles) != 0):
                            for i in allFiles:
                                index += 1
                                dirList = dirList + '[' + str(index) + '] ' + (i) + '\n'
                        else:
                            dirList = dirList + 'No files in the server at the moment.\n'

                        # send the file list to the client and print status
                        try:
                            send_data(conn, dirList)
                            print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Sent file list.")
                        except:
                            print_date(str(address[0]) + ' (' + str(address[1]) + "): " + "Failed to send file list.")

                    else:
                        send_data(conn, errorPrinting(13))
                      
                # send file to client
                elif(userCommand[0] == "get"):

                    # setup to get the file
                    filename = userCommand[1]
                    fileCopyPath = currentPath + '\\' + filename

                    # try to read the file from server directory
                    try:
                        with open(fileCopyPath, 'r') as fileCopy:
                            fData = fileCopy.read()

                        # inform client that server received the file
                        send_data(conn, 'success')
                        fileExists = True

                    except:

                        # inform client that server failed to receive the file
                        send_data(conn, 'fail')
                        send_data(conn, errorPrinting(5))
                        fileExists = False

                    if (fileExists):
                        try:
                            # send file over to client
                            send_data(conn, fData)
                            now = datetime.datetime.now()
                            send_data(conn, "<" + str(now) + "> " + 'Successfully sent over ' + filename + '.')
                        except:  
                            # failed to send
                            send_data(conn, errorPrinting(17))
                            print_date("Failed to send " + filename + ' to ' + username + ".")
                
                # broadcast message to all users (includes not registered)
                elif(userCommand[0] == 'all'):
                    # user needs to be registered first
                    if(hasRegistered):

                        try:
                            # get message and broadcast to all users
                            userMessage = recv_data(conn).decode()
                            status = broadcast_msg(userMessage)
                            print_date('Broadcasting a message from ' + username)
                            
                            # failed to broadcast messages
                            if(not status):
                                send_data(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                                print_date(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                        except:
                            print_date(conn, (str(address[0]) + ' (' + str(address[1]) + '): ' + ' Something went wrong in sending the broadcast message.'))
                    
                    else:
                        send_data(conn, errorPrinting(13))

                # get all current user names in the server
                elif(userCommand[0] == 'active'):

                    # registration check
                    if(hasRegistered):

                        try:
                            # just some stuff to format the list better
                            now = datetime.datetime.now()
                            index = 0
                            dirList = "\n[Date & Time: " + str(now) + "]\n\nCurrent users on the server: " + str(len(listOfUsers)) + '\n'

                            # get all users and append to current list
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

                # direct message to another user
                elif(userCommand[0] == 'dm'):

                    # registration check
                    if(hasRegistered):
                        try:
                            # get message from user
                            data = recv_data(conn).decode()
                            userMessage = data.split(" ", 1)
                            userIndex = username_taken(userMessage[0])
                        
                            # making sure that the user is not dming themselves
                            if (userMessage[0] != username):
                                # if the user exists in active user
                                if(userIndex != -1):
                                    # send message using the socket dedicated for that specific receipient's client
                                    status = send_msg(listOfUsers[userIndex][2], userMessage[1])
                                    send_msg(conn, userMessage[1])

                                    # successfully sent
                                    if(status == 1):
                                        print_date(str(address[0]) + ' (' + str(address[1]) + '): ' + "Sent message from " + username + ' to ' + userMessage[0] + '.')
                                    
                                    # something went wrong in sending
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

                # helper to check if user is already registered, specifically for store and get commands
                elif(userCommand[0] == 'isregistered'):
                    # remove because current socket is only being used for file sharing purposes
                    listOfUsers.remove(('', address, conn))
        
                    userHost = userCommand[1]
                    userPort = userCommand[2]

                    alreadyRegistered = "fail"
                    
                    # find the user in the active user list
                    for i in listOfUsers:

                        # does user have matching host and port?
                        if i[1][0] == userHost and str(i[1][1]) == userPort:   

                            # have they registered? (should be not a blank username)    
                            if i[0] != '':
                                username = i[0]
                                alreadyRegistered = "success"
                            break

                    send_data(conn, alreadyRegistered)


        # client suddenly closed the connection
        except:
             print_date(str(address[0]) + " (" + str(address[1]) + "): Closed connection.")
             listOfUsers.remove((username, address, conn))
             break

########################################################################

## setup
os.system('cls')

## server directory setup
currentPath = os.getcwd() + "\\server_directory"
pathExists = os.path.exists(currentPath)

# create a directory if server directory does not exist
if (not pathExists):
    os.makedirs(currentPath)
    print("[Setup] Server directory does not exist. Created a new directory server_directory.")

## server prep
serverSocket = socket(AF_INET, SOCK_STREAM)
setupCorrectly = False
failedHostPort = False

try:
    host = input("[Setup] Host: ")
    port = input("[Setup] Port: ")
    port = int(port)

    listOfUsers = []            # list of active users in the server
except:
    failedHostPort = True
    print("[Error]: One of the inputted values is invalid. Please check if you typed your host and port correctly.")


if(not failedHostPort):
    ## try to bind the server, else it fails
    try: 
        serverSocket.bind((host, port))
        setupCorrectly = True

    except:
        print("[Error]: Something wrong has occurred in the server setup. Please check if you typed your host and port correctly.")


if(setupCorrectly):
        
        # listening thread to shut down server
        shutThread = threading.Thread(target=shutServer, args=(serverSocket,))
        shutThread.start()

        now = datetime.datetime.now()
        serverSocket.listen()
        print("<" + str(now) + "> Listening for any incoming connections on " + host + ":" + str(port))
        

        while True:
            conn, address = serverSocket.accept()

            # threading to serve multiple clients
            thread = threading.Thread(target=threadServer, args=(conn, address))
            thread.start()
        
                