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
  print("<" + str(now) + "> [Error " + str(errNum) + "]:", end=' ')
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
       print("Something went wrong in disconnecting. Closing connection.")
  elif(errNum == 15):
       print("Something went wrong in requesting file list. Closing connection.")
  elif(errNum == 16):
       print("Something went wrong in requesting active user list. Closing connection.")
  elif(errNum == 17):
       print("Something went wrong in requesting and downloading the file. Closing connection.")
  elif(errNum == 18):
       print("Something went wrong in registering the username. Closing connection.")
  elif(errNum == 19):
       print("Something went wrong with the server connection. Closing connection.")
  elif(errNum == 20):
       print("Something went wrong with sending a direct message. Closing connection.")
  elif(errNum == 21):
       print("Something went wrong with broadcasting the message. Closing connection.")
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
     while True:
          try:
               message = recv_data(client).decode()
               if(message):
                    print(message)
          except:
               return
    
def closingSocket(client):
     client.close()
     print_date("Successfully disconnected.")
########################################################################

os.system('cls')

# variables
currentUsername = ""
isConnected = False # is client connected?
hasQuit = False # has client used the command to quit the application?

print('Welcome to the file exchange system! Type /? for the list of commands.')

while(not hasQuit):

    time.sleep(0.5)
    userInput = input()

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
                         errorPrinting(9)
                         
                    else:
                         #client socket, TCP
                         command = command[1].split(" ")
                         host = command[0]
                         port = int(command[1])

                         try: 
                              clientSocket = socket(AF_INET, SOCK_STREAM)
                              clientSocket.connect((host, port))
                              thread = threading.Thread(target=listenMessages, args=(clientSocket,))
                              thread.start()
                              isConnected = True
                              print_date("You're now connected to the server.")

                         except:
                              errorPrinting(1)

               # user disconnects the server
               elif(command[0] == 'leave'):
                    # check if user is connected first before trying to disconnect
                    if(isConnected):
                         try:
                              clientSocket.close()
                              print_date("Successfully disconnected.")
                              isConnected = False
                         except:
                              errorPrinting(14)
                              closingSocket(clientSocket)
                              isConnected = False
                              
                    else:
                         errorPrinting(2)
                   

               
               # user registers a username
               elif(command[0] == 'register'):
                    # user is already connected but hasn't registered
                    if(isConnected):
                         username = command[1]
                         if (username != ' ' and username != ''):
                              try:
                                   # check if error or success
                                   send_data(clientSocket, 'register ' + username)
                                   currentUsername = username
                              except:
                                   errorPrinting(18)
                         else:
                              errorPrinting(12)

                    # not connected yet
                    if (not isConnected):
                         errorPrinting(10)

               elif(command[0] == 'store'):
                    # stop listening for incoming messages
                    if(isConnected):

                         # connecting a new socket to handle files; the problem with the current clientsocket
                         # is it only receives and prints messages, there's no certainty that we can receive
                         # and store the information we need
                         clientSocket2 = socket(AF_INET, SOCK_STREAM)
                         clientSocket2.connect((host, port))
                         send_data(clientSocket2, 'isregistered ' + clientSocket.getsockname()[0] + ' ' + str(clientSocket.getsockname()[1]))
                         isRegistered = recv_data(clientSocket2).decode()
                         
                         if(isRegistered == 'success'):
                              # check if file exists
                              filename = command[1]
                              fileExists = True
                              try:
                                   with open(filename, 'r') as f:
                                        fData = f.read()
                              except:
                                   errorPrinting(4)    
                                   fileExists = False
                                   clientSocket2.close()
                                   
                              if (fileExists):
                                   try:
                                        
                                        send_data(clientSocket2, 'store')
                                        send_data(clientSocket2, filename)
                                        send_data(clientSocket2, fData)
                                        print(recv_data(clientSocket2).decode())

                                   except:  
                                        closingSocket(clientSocket)
                                        isConnected = False
                                        currentUsername=''

                                   finally: 
                                        clientSocket2.close()
                         else:
                              errorPrinting(8)
                              clientSocket2.close()
                        
                    else:
                         errorPrinting(10)
               
               elif(command[0] == 'dir'):
                    # check if connected and registered, not done
                    if(isConnected):
                         try:
                              send_data(clientSocket, 'dir')
                         except:
                              errorPrinting(15)
                              closingSocket(clientSocket)
                              isConnected = False
                              currentUsername=''
                    else:
                         errorPrinting(10)
                    
               elif(command[0] == 'get'):
                    # not done yet...
                    if(isConnected):
                         # connecting a new socket to handle files; the problem with the current clientsocket
                         # is it only receives and prints messages, there's no certainty that we can receive
                         # and store the information we need
                         clientSocket2 = socket(AF_INET, SOCK_STREAM)
                         clientSocket2.connect((host, port))
                         send_data(clientSocket2, 'isregistered ' + clientSocket.getsockname()[0] + ' ' + str(clientSocket.getsockname()[1]))
                         isRegistered = recv_data(clientSocket2).decode()
 
                         if(isRegistered == "success"):
                              filename = command[1]
                              try:
                                   send_data(clientSocket2, 'get ' + filename)
                                   fileStatus = recv_data(clientSocket2).decode()
                                   
                                   if (fileStatus == 'success'):
                                        fData = recv_data(clientSocket2).decode()
                                        with open(filename, 'w') as fileCopy:
                                             fileCopy.write(fData)
                                        print(recv_data(clientSocket2).decode())
                                   else:       
                                        print(recv_data(clientSocket2).decode())  
                                   
                              except:
                                   errorPrinting(17)
                                   closingSocket(clientSocket)
                                   isConnected = False
                                   currentUsername=''
                              finally:
                                   clientSocket2.close()
                         else:
                              errorPrinting(8)
                              clientSocket2.close()
                              
                    else:
                         errorPrinting(10)
                    
               elif(command[0] == 'all'):
                    if(isConnected):
                         try:
                              now = datetime.datetime.now()
                              send_data(clientSocket, 'all')
                              message = '<' + str(now) + '> [Broadcast] ' + currentUsername + ': ' +  command[1]
                              send_data(clientSocket, message)
                         except:
                              errorPrinting(21)
                              closingSocket(clientSocket)
                              isConnected = False
                              currentUsername=''

                    elif (not isConnected):
                         errorPrinting(10)


               elif(command[0] == 'dm'):  
                    if(isConnected):
                         try:
                              command = command[1].split(" ", 1)
                              now = datetime.datetime.now()
                              send_data(clientSocket, 'dm')
                              message = '<' + str(now) + '> [Direct Message] ' + currentUsername + ': ' +  command[1]
                              send_data(clientSocket, command[0] + ' ' + message)
                         except:
                              errorPrinting(20)
                              closingSocket(clientSocket)
                              isConnected = False
                              currentUsername=''

                    elif (not isConnected):
                         errorPrinting(10)

               
               elif(command[0] == 'active'):
                    if(isConnected):
                         try:
                              send_data(clientSocket, "active")
                         except:
                              errorPrinting(16)
                              closingSocket(clientSocket)
                              isConnected = False
                              currentUsername=''
          
                    elif (not isConnected):
                         errorPrinting(10)

               elif(command[0] == '?'):
                    print_date('''\n
                    NOTE: For command get and store, you will not be able to receive any messages from anyone while executing the command.\n
                    \n
                    Command         Description                                                            Syntax                              Sample\n
                    join       // Join a server                                                   /join <server_ip_add> <port>        /join 192.168.1.1 12345\n
                    leave      // Leave a server you're already connected to                      /leave                          \n
                    register   // Register a username before you store or request a file          /register <name>                    /register Pikachu\n
                    store      // Store a file on the server                                      /store <filename>                   /store pokedex.txt\n
                    dir        // Get the directory file list of the server                       /dir\n
                    get        // Request a file from the server to download                      /get <filename>                     /get pikachu.png\n
                    all        // Message to all active users                                     /all <message>                      /all Hello to everyone! \n 
                    dm         // Message a specific user                                         /dm <username> <message>            /dm Alice What are you doing\n
                    active     // Get list of all active users                                    /active\n         
                    ?          // Display all available commands                                  /?\n
                    quit       // Quit the client application.                                    /quit\n
                               ''')
               # user quits the application
               elif (command[0] == 'quit'):
                    print_date("Quitting the application...")
                    if(isConnected):
                         try:
                              clientSocket.close()
                              print_date("Successfully disconnected.")
                              isConnected = False
                         except:
                              print_date(errorPrinting(14))
                    hasQuit = True

                    
     else:
          errorPrinting(6) # command not found error
          
sys.exit()