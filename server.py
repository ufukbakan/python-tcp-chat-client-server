from socket import *
from dependencies.server_thread import ClientHandlerThread, StatisticsThread

activeThreads = []
activeUsers = []

try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind( ("localhost", 8080) )
    serverSocket.listen()
    print("listening localhost:8080")

    pingerThread = StatisticsThread(activeThreads)
    pingerThread.start()

    while(True):
        clientSocket, adress = serverSocket.accept()
        thread = ClientHandlerThread(clientSocket, activeThreads, activeUsers)
        thread.start()
        activeThreads.append(thread)

except Exception as ex:
    print(ex)