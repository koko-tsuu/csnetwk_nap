from socket import *
import sys


serverSocket = socket.socket(socket.AF_INET, socket.SOCKET_STREAM)
host = socket.hostname()
port = 6969

serverSocket.bind((host, port))
serverSocket.listen()

while True:
    connectSocket, address = serverSocket.accept()
    connectSocket.close()

serverSocket.close()
sys.exit()