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
     "exit" :       [0, []],
}

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
hasExit = False # has client used the command to exit the application?

print('Welcome to the file exchange system! Type /? for the list of commands.')

while(not hasExit):

    userInput = input("Command: ")

    isThereASlash = (userInput[0] == '/')

    # did user put a slash? if not, error
    if (isThereASlash): 

        # split the string
        userCommand = userInput[1:].lower()
        command = userCommand.split(" ")
    
        #error checking
        if (errorCheckCommand(command)):
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

            elif(command[0] == 'leave'):
               if(isConnected):
                    try:
                         clientSocket.send("disconnect".encode())
                         clientSocket.close()
                         print_date("Successfully disconnected.")
                    except IOError:
                        print_date("Something went wrong in disconnecting.")
               else:
                   errorPrinting(2)
            elif(command[0] == 'register'):
                if(isConnected and not hasRegistered):
                    username = command[1]
                    clientSocket.send("register".encode())
                    clientSocket.send(username.encode())

                    # check if error or success
                    result = clientSocket.recv(1024).decode()
                    if (result == 'success'):
                         currentUsername = username
                         hasRegistered = True
                         print_date("Successfully registered. Welcome, " + currentUsername + "!")
                elif (isConnected and hasRegistered):
                    errorPrinting(11)
                else:
                    errorPrinting(10)
            elif (command[0] == 'exit'):
                print_date("Exiting the application...")
                hasExit = True
        else:
               errorPrinting(6)

    else:
         errorPrinting(6) # command not found error
       
         


sys.exit()