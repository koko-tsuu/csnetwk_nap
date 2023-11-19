from socket import *
import sys
import datetime
import os
import threading

os.system('cls')

def print_date(message):
    now = datetime.datetime.now()
    print("<" + str(now) + "> " + message)

def threadServer(conn, address):
    hasRegistered = False
    print_date(str(address) + " has connected to the server.")
    while True:
        userCommand = conn.recv(1024)
        if(userCommand == "register"):
            print_date(str(address) + " to register.")
            if (username in listOfUsers):
                print_date(username + " is taken. Sending error to client.")
                conn.send("username_taken".encode())
            elif (hasRegistered):
                print_date(username + " has already registered. Sending error to client.")
                conn.send("username_alreadyregistered".encode())
            else:
                username = conn.recv(1024).decode()
                conn.send("success".encode())
                conn(str(address) + " registered as " + username + ".")
            listOfUsers.append(username)
        elif(userCommand == "disconnect"):
            print_date(str(address) + " to disconnect.")
            conn.shutdown()
            conn.close()
            print_date("Closed " + address)

########################################################################

serverSocket = socket(AF_INET, SOCK_STREAM)

host = input("[Setup] Host: ")
port = input("[Setup] Port: ")
port = int(port)

setupCorrectly = False

try: 
    serverSocket.bind((host, port))
    setupCorrectly = True

 
except IOError:
    print("[Error]: Something wrong has occurred in the server setup. Please check if you typed your host and port correctly.")


if(setupCorrectly):
        now = datetime.datetime.now()
        serverSocket.listen()
        print("<" + str(now) + "> Listening for any incoming connections on " + host + ":" + str(port))
        
        listOfUsers = []

        while True:
            try:
                conn, address = serverSocket.accept()
                thread = threading.Thread(target=threadServer, args=(conn, address))
                thread.start()
            except IOError:
                break
              
                
sys.exit()
    
     
        

       

