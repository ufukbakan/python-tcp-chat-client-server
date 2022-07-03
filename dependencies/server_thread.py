import pickle
from socket import AF_INET, SOCK_STREAM, socket
import sqlite3
from threading import Thread
from time import sleep

from dependencies.messages import Message
from dependencies.commands import Command

class StatisticsThread(Thread):
    def __init__(self, activeThreads):
        Thread.__init__(self, daemon=True)
        self.activeThreads = activeThreads
    
    def run(self):
        self.db = sqlite3.connect("./serverDB.db")
        self.sql = self.db.cursor()
        while(True):
            self.sql.execute("select * from activeUsers")
            rows = self.sql.fetchall()
            for row in rows:
                active = False
                for thread in self.activeThreads:
                    tsocket:socket = thread.socket
                    if( tsocket.getpeername()[0] == row[1] and tsocket.getpeername()[1] == row[2] ):
                        active = True
                        break
                if(not active):
                    try:
                        self.sql.execute("delete from activeUsers where username=?", (row[0],))
                        self.db.commit()
                    except:
                        pass
            print("Active threads: %d, active users: %d" % ( len(self.activeThreads), len(rows) ))
            sleep(10)


class ClientHandlerThread(Thread):
    def __init__(self, socket:socket, activeThreads: list, activeUsers:list):
        Thread.__init__(self, daemon=True)
        self.socket = socket
        self.username = ""
        self.activeThreads = activeThreads
        self.activeUsers = activeUsers
    
    def run(self):
        self.db = sqlite3.connect("./serverDB.db")
        self.sql = self.db.cursor()
        connection_alive = True
        while(connection_alive):
            try:
                command:Command = pickle.loads( self.socket.recv(4096) )
                self.handleCommand(command)
            except:
                connection_alive = False
        try:
            self.sql.execute("delete from activeUsers where username=?", (self.username,))
            self.db.commit()
        except:
            pass

        print("user '%s' logged out" % (self.username,))
        self.activeUsers.remove(self.username)
        self.activeThreads.remove(self)
        for thread in self.activeThreads:
            thread.updateUserList()

    def handleCommand(self, command:Command)->None:
        try:
            if(command.action == "login-user"):
                self.username = command.body
                clientIp = self.socket.getpeername()[0]
                clientPort = self.socket.getpeername()[1]
                self.sql.execute("insert into activeUsers (username, ip, port) values (?,?,?)", (self.username, clientIp, clientPort))
                self.db.commit()
                self.activeUsers.append(self.username)
                print("user '%s' logged in" % (self.username,))
                for thread in self.activeThreads:
                    thread.updateUserList()

            elif(command.action == "get-messages"):
                user1 = command.body[0]
                user2 = command.body[1]
                self.sql.execute("select sender, receiver, body from messages where (sender=? and receiver=?) or (sender=? and receiver=?)", (user1,user2,user2,user1))
                rows = self.sql.fetchall()
                responseCommand = Command("get-messages-response", (user1, user2, rows))
                self.socket.sendall( pickle.dumps(responseCommand) )
            elif (command.action == "send-message"):
                message:Message = command.body
                self.sql.execute("insert into messages (sender, receiver, body) values (?,?,?)", (message.sender, message.receiver, message.content))
                self.db.commit()
                for t in self.activeThreads:
                    thread:ClientHandlerThread = t
                    if(thread.username == message.receiver):
                        thread.receiveMessage(message)

        except Exception as ex:
            print(str(ex))

    def receiveMessage(self, message:Message)->None:
        self.socket.sendall( pickle.dumps( Command("receive-message", message) ) )

    def updateUserList(self)->None:
        self.socket.sendall( pickle.dumps( Command("update-active-users", self.activeUsers) ) )
