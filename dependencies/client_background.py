import pickle
from socket import socket
from threading import Thread
from tkinter import messagebox
import tkinter as tk

from dependencies.commands import Command
from dependencies.messages import rowToMessageStr, rowsToLines, rowsToStrings, Message

class ClientBGThread(Thread):
    def __init__(self, socket:socket, window):
        Thread.__init__(self, daemon=True)
        self.socket = socket
        self.window = window
        loginCommand = Command("login-user", window.username)
        socket.sendall( pickle.dumps(loginCommand) )
    
    def run(self):
        socketAlive = True
        while(socketAlive):
            try:
                command:Command = pickle.loads( self.socket.recv(4096) )
                self.handleCommand(command)
            except Exception as ex:
                socketAlive = False
                messagebox.showerror("Error", str(ex))
        self.window.root.destroy()

    def handleCommand(self, command:Command):
        if(command.action == "get-messages-response"):
            otherUsername = command.body[1]
            rows = command.body[2]
            self.window.messages[otherUsername] = rows
            self.window.text.configure(state="normal")
            self.window.text.delete("1.0", "end")
            self.window.text.insert(tk.END, rowsToLines(rows) )
            self.window.text.see(tk.END)
            self.window.text.configure(state="disabled")
        elif(command.action == "receive-message"):
            message:Message = command.body
            if(message.sender in self.window.messages.keys()):
                row = (message.sender, message.receiver, message.content)
                self.window.messages[message.sender].append( row )
                if(self.window.active_chat_window == message.sender):
                    self.window.text.configure(state="normal")
                    self.window.text.insert(tk.END, "\n"+rowToMessageStr(row) )
                    self.window.text.see(tk.END)
                    self.window.text.configure(state="disabled")
        elif(command.action == "update-active-users"):
            self.window.activeUsers = command.body
            self.window.updateUserListBox()