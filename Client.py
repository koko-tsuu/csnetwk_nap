from socket import *
import sys
import datetime
import time
import os
import threading
import struct


# command_dict -> dictionary for valid commands
# format for dictionary:
# command : [number of parameters needed, [data types]]
command_dict = {
     "join" :       [2, [str, int]],
     "leave" :      [0, []],
     "register" :   [1, [str]],
     "store" :      [1, [str]],
     "dir" :        [0, []],
     "get" :        [1, [str]],
     'all':         [1, [str]],       
     'dm':          [2, [str, str]],
     'active':      [0, []],
     "?" :          [0, []],
     "quit" :       [0, []],
}

# printing date with string passed
def print_date(message=""):
    now = datetime.datetime.now()
    print("<" + str(now) + "> " + message)

# printing errors, pass the number to display the respective error.
def errorPrinting(errNum):
  now = datetime.datetime.now()
  print("<" + str(now) + ">", end=" ")
  print("[Error " + str(errNum) + "] :", end = " ")
  if(errNum == 1):       # wrong ip address or port number
       print("Connection to the Server has failed! Please check IP Address and Port Number. Otherwise, the server may not be active at the moment.")
  elif(errNum == 2):     # disconnection failed, user hasn't connected yet
       print("Disconnection failed. Please connect to the server first.")
  elif(errNum == 3):     # username already exists
       print("Registration failed. Handle or alias already exists.")
  elif(errNum == 4):
       print("File not found.")
  elif(errNum == 5):
       print("File not found in the server.")
  elif(errNum == 6):
       print("Command not found.")
  elif(errNum == 7):
       print("Command parameters do not match or is not allowed.")
  elif(errNum == 8):
       print("Please register first before sending or requesting files.")
  elif(errNum == 9):
       print("You're already connected to a server.")
  elif(errNum == 10):
       print("To use this command, you need to be connected to a server first.")
  elif(errNum == 11):
       print("You have already registered.")
  elif(errNum == 12):
       print("Username is empty.")
  elif(errNum == 13):
       print("To use this command, you need to register first.")
  elif(errNum == 14):
       print("Something went wrong in disconnecting.")
  elif(errNum == 15):
       print("Something went wrong in requesting file list.")
  elif(errNum == 16):
       print("Something went wrong in requesting active user list.")
  elif(errNum == 17):
       print("Something went wrong in requesting and downloading the file.")
  elif(errNum == 18):
       print("Something went wrong in registering the username.")
  elif(errNum == 19):
       print("Something went wrong with the server connection. Closing socket.")
  elif(errNum == 20):
       print("Something went wrong with sending a direct message.")
  elif(errNum == 21):
       print("Something went wrong with broadcasting the message.")
  elif(errNum == 22):
       print("The user to be messaged does not exist. Please make sure to check if you wrote the username correctly.")

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


# checks if the user inputted the correct number of parameters
def parameterCheck(list):
    command = list[0]                                 # command

    if (len(list) > 1):
         copyList = list[1].split(" ")
    else:
         copyList = []

    len_command_parameters = len(copyList)             # num of command parameters
    len_dict_parameters = command_dict[command][0]     # num of dictionary parameters
    parameter_types = command_dict[command][1]         # data types of parameters
    
     # does the number of parameters in the command match with the command dictionary?
    if (len_command_parameters == len_dict_parameters):
        # if so, check if both are of equal data types
        for x in range(len(parameter_types)):
            # if not equal, return false
            if((not isinstance(copyList[x], parameter_types[x])) and (isinstance(parameter_types[1], int) and (not copyList[x].isdigit()))):
               errorPrinting(7)
               return False
        # otherwise, return true
        return True
    elif(command == 'all' or command == 'dm'):
         if (len_command_parameters >= len_dict_parameters):
              return True
    else:
         errorPrinting(7)
         return False

# checks if command is valid and is in the list of commands; also calls parameterCheck
def errorCheckCommand(list):
     command = list[0].lower()
     if(command in command_dict):
        if(parameterCheck(list)):
             return True
        else:
            return False
     else:
          errorPrinting(6) # command not found error
          return False

def listenMessages(client): # not done, threading needed
     try:
          while True:
               message = recv_data(client)
               if(message):
                    message = message.decode()
                    print(message)
                    if message != "username_alreadyregistered" and message != "username_taken" and message != 'success' and  message != 'broad_fail' and  message != 'dm_notexist' and message !='dm_msgfail' and message != 'pong':
                         print(message)
     except:
          return

#checks if server still alive, if it isn't, change status
def pingServer(conn):
     try:
          send_data(conn, "ping")
          data = recv_data(conn).decode()
          if len(data) == 0:
               return False
          return True
     except:
          return False

def pingError(socket):
     errorPrinting(19)
     try:
          socket.close()
     finally:
          return '', False, False
     
########################################################################

os.system('cls')

# variables
currentUsername = ""
isConnected = False # is client connected?
pingWorked = False # did ping work?
hasRegistered = False # has user registered?
hasQuit = False # has client used the command to quit the application?

print('Welcome to the file exchange system! Type /? for the list of commands.')

while(not hasQuit):

    time.sleep(0.5)
    userInput = input("Command: ")

    if (userInput != ""):
     isThereASlash = (userInput[0] == '/')

     # did user put a slash? if not, error
     if (isThereASlash): 

          # split the string
          userCommand = userInput[1:]
          command = userCommand.split(" ", 1)

          #error checking
          if (errorCheckCommand(command)):
               
               # user connects to server
               if (command[0] == 'join'):
                    if (isConnected):
                         try:
                              pingWorked = pingServer(clientSocket)
                         finally:
                               if (not pingWorked):
                                   currentUsername, isConnected, hasRegistered = pingError(clientSocket)
                             
                         if(pingWorked):
                             errorPrinting(9)
                         
                    else:
                         #client socket, TCP
                         command = command[1].split(" ")
                         host = command[0]
                         port = int(command[1])

                         try: 
                              clientSocket = socket(AF_INET, SOCK_STREAM)
                              clientSocket.settimeout(10.0)
                              clientSocket.connect((host, port))
                              threading.Thread(target=listenMessages, args=(clientSocket,)).start()
                              isConnected = True
                              print_date("Successfully connected to the server.")      

                         except Exception:
                              errorPrinting(1)

               # user disconnects the server
               elif(command[0] == 'leave'):
                    # check if user is connected first before trying to disconnect
                    if(isConnected):
                         try:
                              pingWorked = pingServer(clientSocket)
                         finally:
                               if (not pingWorked):
                                   currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                         if(pingWorked):
                              try:
                                   send_data(clientSocket, 'disconnect')
                                   clientSocket.close()
                                   print_date("Successfully disconnected.")
                                   isConnected = False
                                   hasRegistered = False
                              except:
                                   errorPrinting(14)
                    else:
                         errorPrinting(2)
                   

               
               # user registers a username
               elif(command[0] == 'register'):
                    # user is already connected but hasn't registered
                    if(isConnected):
                         try:
                              pingWorked = pingServer(clientSocket)
                         finally:
                               if (not pingWorked):
                                   currentUsername, isConnected, hasRegistered = pingError(clientSocket)
                         
                         # user has already registered
                         if (isConnected and hasRegistered and pingWorked):
                              errorPrinting(11)
                         # no username yet
                         elif(isConnected and not hasRegistered and pingWorked):
                              username = command[1]
                              if (username != ' ' and username != ''):
                                   try:
                                        # check if error or success
                                        send_data(clientSocket, 'register ' + username)
                                        result = recv_data(clientSocket).decode()
                                        if (result == 'success'):
                                             currentUsername = username
                                             hasRegistered = True
                                             print_date("Successfully registered. Welcome, " + currentUsername + "!")
                                        elif (result == 'username_taken'):
                                             errorPrinting(3)
                                        elif(result == 'username_alreadyregistered'):
                                             errorPrinting(11)
                                   except:
                                        errorPrinting(18)
                              else:
                                   errorPrinting(12)

                    # not connected yet
                    if (not isConnected):
                         errorPrinting(10)

               elif(command[0] == 'store'): #not yet done
                    filename = command[1]
                    # check if connected and registered, not done
                    if(isConnected):
                         try:
                              f = open(filename)
                              fData = f.read()

                              for x in range(0, len(fData)):
                                   clientSocket.send(fData[x].encode())
                              f.close()
                         except:
                              errorPrinting(4)
                    pass
               
               elif(command[0] == 'dir'):
                    # check if connected and registered, not done
                    if(isConnected):
                         try:
                              pingWorked = pingServer(clientSocket)
                         finally:
                               if (not pingWorked):
                                   currentUsername, isConnected, hasRegistered = pingError(clientSocket)
                         
                         if(isConnected and hasRegistered and pingWorked):
                              try:
                                   send_data(clientSocket, 'dir')
                                   print(recv_data(clientSocket).decode())
                                   send_data(clientSocket, 'success')
                              except:
                                   errorPrinting(15)
                         elif (not hasRegistered):
                              errorPrinting(13)
                    else:
                         errorPrinting(10)
               elif(command[0] == 'get'):
                    # not done yet...
                    try:
                         pingWorked = pingServer(clientSocket)
                    finally:
                         if (not pingWorked):
                              currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                    if(pingWorked):
                         if(isConnected):
                              try:
                                   clientSocket.send('get'.encode())
                              except:
                                   errorPrinting(17)
                    else:
                         errorPrinting(10)
                    
                    pass
               elif(command[0] == 'all'):
                    
                    try:
                         pingWorked = pingServer(clientSocket)
                    finally:
                         if (not pingWorked):
                              currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                    if(pingWorked and isConnected):
                         try:
                              string = command[1].replace('"', '')
                              now = datetime.datetime.now()
                              send_data(clientSocket, 'all')
                              message = '<' + str(now) + '> [Broadcast] ' + currentUsername + ': ' +  string
                              send_data(clientSocket, message)
                              
                              status = recv_data(clientSocket).decode()
                              if(status == 'broad_fail'):
                                   errorPrinting(21)
                         except:
                              errorPrinting(21)
                    elif (not isConnected):
                         errorPrinting(10)


               elif(command[0] == 'dm'):
                   
                    try:
                         pingWorked = pingServer(clientSocket)
                    finally:
                         if (not pingWorked):
                              currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                    if(pingWorked and isConnected):
                         try:
                              command = command[1].split(" ", 1)
                              string = command[1].replace('"', '')
                              now = datetime.datetime.now()
                              send_data(clientSocket, 'dm')
                              message = '<' + str(now) + '> [Direct Message]' + currentUsername + ': ' +  string
                              send_data(clientSocket, command[1] + ' ' + message)
                              
                              status = recv_data(clientSocket).decode()
                              if(status == 'success'):
                                   print(message)
                              elif(status == 'dm_notexist'):
                                   errorPrinting(22)
                              elif(status == 'dm_msgfail'):
                                   errorPrinting(20)
                         except:
                              errorPrinting(20)
                    elif (not isConnected):
                         errorPrinting(10)

               
               elif(command[0] == 'active'):
                    try:
                         pingWorked = pingServer(clientSocket)
                    finally:
                         if (not pingWorked):
                              currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                    if(pingWorked and isConnected):
                         try:
                              send_data(clientSocket, "active")
                              print(recv_data(clientSocket).decode())
                              send_data(clientSocket, 'success')     
                         except:
                              errorPrinting(16)
                         pass
                    elif (not isConnected):
                         errorPrinting(10)

               elif(command[0] == '?'):
                    print_date('''\n
                    Command         Description                                                            Syntax                              Sample\n
                    join       // Join a server                                                   /join <server_ip_add> <port>        /join 192.168.1.1 12345\n
                    leave      // Leave a server you're already connected to                      /leave                          \n
                    register   // Register a username before you store or request a file          /register <name>                    /register Pikachu\n
                    store      // Store a file on the server                                      /store <filename>                   /store pokedex.txt\n
                    dir        // Get the directory file list of the server                       /dir\n
                    get        // Request a file from the server to download                      /get <filename>                     /get pikachu.png\n
                    all        // Message to all active users                                     /all <message>                      /all "Hello to everyone!" or /all Hello to everyone! \n 
                    dm         // Message a specific user                                         /dm <username> <message>            /dm Alice "What are you doing" or /dm Alice What are you doing\n
                    active     // Get list of all active users                                    /active\n         
                    ?          // Display all available commands                                  /?\n
                    quit       // Quit the client application.                                    /quit\n
                               ''')
               # user quits the application
               elif (command[0] == 'quit'):
                    print_date("Quitting the application...")
                    if(isConnected):
                         try:
                              pingWorked = pingServer(clientSocket)
                         except:
                              currentUsername, isConnected, hasRegistered = pingError(clientSocket)

                         if(pingWorked and isConnected):
                              try:
                                   clientSocket.send("disconnect".encode())
                                   clientSocket.close()
                                   print_date("Successfully disconnected.")
                                   isConnected = False
                                   hasRegistered = False
                              except:
                                   errorPrinting(14)
                    hasQuit = True

                    
     else:
          errorPrinting(6) # command not found error

     pingWorked = False # reset
          
sys.exit()