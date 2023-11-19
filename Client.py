from socket import *
import sys
import datetime
import os


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
     "?" :          [0, []],
     "quit" :       [0, []],
}

# printing date with string passed
def print_date(message):
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
       print("You're not connected to a server yet.")
  elif(errNum == 11):
       print("You have already registered.")
  elif(errNum == 12):
       print("Username is empty.")

# checks if the user inputted the correct number of parameters
def parameterCheck(list):
    command = list[0]                                 # command
    len_command_parameters = len(list) - 1             # num of command parameters
    len_dict_parameters = command_dict[command][0]     # num of dictionary parameters
    parameter_types = command_dict[command][1]         # data types of parameters

     # does the number of parameters in the command match with the command dictionary?
    if (len_command_parameters == len_dict_parameters):
        # if so, check if both are of equal data types
        for x in range(len(parameter_types)):
            # if not equal, return false
            if((not isinstance(list[x+1], parameter_types[x])) and (isinstance(parameter_types[1], int) and (not list[x+1].isdigit()))):
               errorPrinting(7)
               return False
        # otherwise, return true
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

     
########################################################################

os.system('cls')

clientSocket = socket(AF_INET, SOCK_STREAM)

# variables
isConnected = False # is client connected?
currentUsername = ""
hasRegistered = False
hasQuit = False # has client used the command to quit the application?

print('Welcome to the file exchange system! Type /? for the list of commands.')

while(not hasQuit):

    userInput = input("Command: ")

    if (userInput != ""):
     isThereASlash = (userInput[0] == '/')

     # did user put a slash? if not, error
     if (isThereASlash): 

          # split the string
          userCommand = userInput[1:]
          command = userCommand.split(" ")

          #error checking
          if (errorCheckCommand(command)):
               
               # user connects to server
               if (command[0] == 'join'):
                    if (isConnected):
                         errorPrinting(9)
                    else:
                         #client socket, TCP
                         
                         host = command[1]
                         port = int(command[2])

                         try: 
                              clientSocket.connect((host, port))
                              isConnected = True
                              print_date("Successfully connected to the server.")      
                         except IOError:
                              errorPrinting(1)

               # user disconnects the server
               elif(command[0] == 'leave'):
                    # if user is already connected
                    if(isConnected):
                         try:
                              clientSocket.send("disconnect".encode())
                              clientSocket.close()
                              print_date("Successfully disconnected.")
                              isConnected = False
                              hasRegistered = False
                         except IOError:
                              print_date("Something went wrong in disconnecting.")
                    else:
                         errorPrinting(2)
               
               # user registers a username
               elif(command[0] == 'register'):
                    # user is already connected but hasn't registered
                    if(isConnected and not hasRegistered):
                         username = command[1]
                         if (username != ' ' and username != ''):
                              clientSocket.send(("register " + username).encode())

                              # check if error or success
                              result = clientSocket.recv(1024).decode()

                              if (result == 'success'):
                                   currentUsername = username
                                   hasRegistered = True
                                   print_date("Successfully registered. Welcome, " + currentUsername + "!")
                              elif (result == 'username_taken'):
                                   errorPrinting(3)
                              elif(result == 'username_alreadyregistered'):
                                   errorPrinting(11)
                         else:
                              errorPrinting(12)

                    # user has already registered
                    elif (isConnected and hasRegistered):
                         errorPrinting(11)
                    
                    # user hasn't connected yet
                    else:
                         errorPrinting(10)

               elif(command[0] == 'store'): ## not yet done
                    filename = command[1]
                    try:
                         f = open(filename)
                         fData = f.read()

                         for x in range(0, len(fData)):
                              clientSocket.send(fData[x].encode())
                         f.close()
                    except IOError:
                         errorPrinting(4)
                    pass
               elif(command[0] == 'dir'):
                    pass
               elif(command[0] == 'get'):
                    pass
               elif(command[0] == '?'):
                    print_date('''\n
                    Command         Description                                                           Syntax                              Sample\n
                    join       // Join a server                                                // /join <server_ip_add> <port>        /join 192.168.1.1 12345\n
                    leave      // Leave a server you're already connected to                   // /leave                          \n
                    register   // Register a username before you store or request a file       // /register <name>                    /register Pikachu\n
                    store      // Store a file on the server                                   // /store <filename>                   /store pokedex.txt\n
                    dir        // Get the directory file list of the server                    // /dir\n
                    get        // Request a file from the server to download                   // /get <filename>                     /get pikachu.png\n
                    ?          // Display all available commands                               // /?\n
                    quit       // Quit the client application.                                 // /quit\n
                               ''')
               # user quits the application
               elif (command[0] == 'quit'):
                    print_date("Quitting the application...")
                    hasQuit = True

     else:
          errorPrinting(6) # command not found error
          
          


sys.exit()