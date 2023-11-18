from socket import *
import sys

# command_dict -> dictionary for valid commands
# format for dictionary:
# command : [number of parameters needed, []
command_dict = {
     "join" : [2, [type("String"), type(0)]],
     "leave" : 0,
     "register" : [1, [type("String")]],
     "store" : [1, [type("String")]],
     "dir" : 0,
     "get" : [1, [type("String")]],
     "?" : 0,
     "exit" : 0,
}

# printing errors, pass the number to display the respective error.
def error_printing(errNum):
  print("\nError " + str(errNum) + ":")
  if(errNum == 1):
       print("Connection to the Server has failed! Please check IP Address and Port Number.")
  elif(errNum == 2):
       print("Disconnection failed. Please connect to the server first.")
  elif(errNum == 3):
       print("Registration failed. Handle or alias already exists.")
  elif(errNum == 4):
       print("File not found.")
  elif(errNum == 5):
       print("File not found in the server.")
  elif(errNum == 6):
       print("Command not found.")
  elif(errNum == 7):
       print("Command parameters do not match or is not allowed.")

# checks if the user inputted the correct number of parameters
def parameterCheck(list):
    command = list[0]
    command_parameters = len(list) - 1 # num of command parameters
    dict_parameters = command_dict[command] # dictionary parameters

    if (command_parameters == dict_parameters):
        for x in range(dict_parameters):
            if(not isinstance(list[x+1], command_dict[1][x])):
                error_printing(7)
                return False 
        return True
    else:
         error_printing(7)
         return False

# checks if command is valid and is in the list of commands; also calls parameterCheck
def errorCheckCommand(list):
     command = list[0]
     if(command in command_dict):
        if(parameterCheck(list)):
             return True
        else:
            return False
     else:
          error_printing(6) # command not found error
          return False

     
########################################################################

#client socket, TCP
clientSocket = socket(AF_INET, SOCK_STREAM)

# boolean things
isConnected = False # is client connected?
hasExit = False # has client used the command to exit the application?

print('Welcome to the file exchange system! Type /? for the list of commands.')

while(not hasExit):

    userInput = input()
    isThereASlash = (userInput[0] == '/')

    # did user put a slash? if not, error
    if (isThereASlash): 

        # split the string
        command = userInput[1:]
        command = command.lower()
        splitCommand = command.split(" ")
    
        #error checking
        if (errorCheckCommand(splitCommand)):
            if (command == 'join'):

                host = splitCommand[1]
                port = splitCommand[2]

                try: 
                    clientSocket.connect((host, port))

                except IOError:
                        error_printing(1)
                        print(IOError)

            elif (command == 'exit'):
                print("Exiting the application...")
                hasExit = True


    else:
         error_printing(6) # command not found error
       
         

clientSocket.close()
sys.exit()