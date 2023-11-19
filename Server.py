from socket import *
import sys
import datetime
import os
import threading

# printing date with string passed
def print_date(message):
    now = datetime.datetime.now()
    print("<" + str(now) + "> " + message)

# function to be ran for the threading 
def threadServer(conn, address):

    # has the user registered?
    hasRegistered = False

    print_date(str(address) + " has connected to the server.")


    while True:
        # get the command from the user
        userCommand = conn.recv(1024).decode()
        userCommand = userCommand.split(" ")

        # user wants to disconnect from server
        if(userCommand[0] == "disconnect"):
            print_date(str(address) + " to disconnect.")
            conn.close()
            print_date("Closed connection to " + str(address) + ".")

        # user wants to register
        elif(userCommand[0] == "register"):
            print_date(str(address) + " to register.")
            username = userCommand[1]
            # username currently exists in active users
            if (username in listOfUsers):
                print_date(username + " is taken. Sending error to client.")
                conn.send("username_taken".encode())
            # user has already registered
            elif (hasRegistered):
                print_date(username + " has already registered. Sending error to client.")
                conn.send("username_alreadyregistered".encode())
            # successfully registered
            else:
                conn.send("success".encode())
                print_date(str(address) + " registered as " + username + ". Welcome!")
                listOfUsers.append(username)

        elif(userCommand[0] == "store"):
           pass

        elif(userCommand[0] == "dir"):
            pass
        
        elif(userCommand[0] == "get"):
            pass

########################################################################

os.system('cls')
currentPath = os.getcwd() + "\\server_directory"
pathExists = os.path.exists(currentPath)
if (not pathExists):
    os.makedirs(currentPath)
    print("[Setup] Server directory does not exist. Created a new directory server_directory.")


serverSocket = socket(AF_INET, SOCK_STREAM)

host = input("[Setup] Host: ")
port = input("[Setup] Port: ")
port = int(port)

setupCorrectly = False
listOfUsers = []

try: 
    serverSocket.bind((host, port))
    setupCorrectly = True

 
except IOError:
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
            except IOError:
                break
              
                
sys.exit()
    
     
        

       

