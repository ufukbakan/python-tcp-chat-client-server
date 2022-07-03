import pickle
from socket import AF_INET, SOCK_STREAM, socket
import tkinter as tk
import tkinter.font as tkFont
from tkinter import Scrollbar, messagebox
from dependencies.client_assign_tag import TagForm

from dependencies.messages import Message, filterRows, rowToMessageStr

from dependencies.client_background import ClientBGThread
from dependencies.commands import Command
from dependencies.messages import rowsToLines

class MainWindow:
    def __init__(self, root, username):
        self.messages = {}
        self.tags = {}
        self.active_chat_window = ""
        self.activeUsers = []
        self.root = root
        self.username = username
        #setting title
        root.title("Chat App - %s" % (username,))
        #setting window size
        width=720
        height=440
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        #self.tags["ufuyum"] = "Aile"
        #self.activeUsers = ["ufuk", "alleyna", "ufuyum"]
        #self.updateUserListBox()
        self.UserListBox=tk.Listbox(root)
        ft = tkFont.Font(family='Calibri',size=12)
        listboxSB = Scrollbar(self.UserListBox)
        listboxSB.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.UserListBox.configure(yscrollcommand=listboxSB.set)
        listboxSB.configure(command=self.UserListBox.yview)
        self.UserListBox["font"] = ft
        self.UserListBox["foreground"] = "#ffffff"
        self.UserListBox["background"] = "#212121"
        self.UserListBox["selectbackground"] = "#ffffff"
        self.UserListBox["selectforeground"] = "#000000"
        self.UserListBox["activestyle"] = "none"
        self.UserListBox["justify"] = "left"
        self.UserListBox.place(x=570,y=0,width=150,height=440)
        self.UserListBox.bind('<Button-1>', self.loadMessages) #left click
        self.UserListBox.bind('<Button-3>', self.listBoxRightClick) #right click

        self.text = tk.Text(root, wrap=tk.WORD)
        self.text.insert(tk.END, "- Öncelikle server.py çalıştırın\n- Giriş yapan clientlar kendisi hariç kullanıcıların listesini sağdaki siyah listbox içerisinde görüntüleyebilecekler (Bağlantı Listesi)\n- Liste üzerinde gruplandırılmak istenen kullanıcı adına sağ tıklayın (Gruplandırma)\n- Mesaj filtreleme özelliği herhangi bir kullanıcıyla sohbete bağlandıktan sonra aktif olacaktır (Anahtar kelimeyle arama)\n- Sohbet eşler arasında gerçekleşecek sohbet odası şeklinde olmayacaktır (Gelen mesajların kullanıcı bazında kaydı)\n- Mesajlar önce sunucuya gönderilip veri tabanına kaydedildikten sonra alıcıya iletilecektir.\n- Alıcı ve gönderici geçmiş mesajları bir defa veri tabanından fetch edecek, çevrimiçi mesajlaşma esnasında yeni mesajları veri tabanından değil sunucuya bağlandıkları soket üzerinden alacaktır. (Geçmiş mesaj bilgilerine erişme)")
        self.text.configure(state="disabled")
        self.text.place(x=0,y=70,width=550,height=320)
        textSB = Scrollbar(root)
        #textSB.pack(side=tk.RIGHT, fill=tk.BOTH)
        textSB.place(x=550, y=70, width=15, height=320)
        textSB.configure(command=self.text.yview)
        self.text["yscrollcommand"] = textSB.set

        self.messageInput = tk.Entry(root)
        self.messageInput.place(x=0, y=400, width=490, height=25)

        self.sendButton = tk.Button(root, command=self.sendMessage)
        self.sendButton.configure(text="Send")
        self.sendButton.place(x=495, y=400, width=70, height=25)

        filterLabel = tk.Label(root)        
        filterLabel.configure(text="Mesajları filtrele:", justify="left")
        filterLabel.place(x=0, y=10, width=100, height=25)
        filterString = tk.StringVar()
        self.filterInput = tk.Entry(root, textvariable=filterString)
        filterString.trace("w", lambda name, index,mode, var=filterString: self.filterCallback(var))
        self.filterInput.place(x=110, y=10, width=200, height=25)

        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            self.clientSocket.connect(("localhost", 8080))
            bgThread = ClientBGThread(self.clientSocket, self)
            bgThread.start()
        except Exception as ex:
            messagebox.showerror("Connection Error", "Couldn't connect to server")
            self.root.destroy()

    def updateUserListBox(self):
        self.UpdateListBoxWithValues( self.tagUsers(self.activeUsers) )
    
    def filterCallback(self, var):
        if(len(self.active_chat_window) > 0):
            filteredRows = filterRows( self.messages[self.active_chat_window], var.get() )
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert(tk.END, rowsToLines(filteredRows) )
            self.text.configure(state="disabled")
        else:
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.insert(tk.END, rowsToLines( self.messages[self.active_chat_window] ) )
            self.text.configure(state="disabled")

    def listBoxRightClick(self, event):
        self.UserListBox.selection_clear(0,tk.END)
        self.UserListBox.selection_set(self.UserListBox.nearest(event.y))
        self.UserListBox.activate(self.UserListBox.nearest(event.y))
        try:
            targetUsername = self.getUserNameFromListBox( self.UserListBox.selection_get() )
            popupRoot = tk.Tk()
            TagForm(popupRoot, targetUsername, self)
        except:
            pass

    def tagUsers(self, userList:list):
        values = []
        for user in userList:
            if user != self.username:
                if user in self.tags.keys():
                    tag = self.tags[user]
                    if(len(tag) > 0):
                        values.append("#%s-@%s" % (tag, user) )
                    else:
                        values.append("@%s" % (user,))
                else:
                    values.append("@%s" % (user,))
        return values
    
    def UpdateListBoxWithValues(self, values:list):
        values.sort(reverse=True)
        self.UserListBox.delete(0, tk.END)
        for value in values:
            self.UserListBox.insert(0, value)

    def loadMessages(self, event):
        self.UserListBox.selection_clear(0,tk.END)
        self.UserListBox.selection_set(self.UserListBox.nearest(event.y))
        self.UserListBox.activate(self.UserListBox.nearest(event.y))
        try:
            targetUsername = self.getUserNameFromListBox( self.UserListBox.selection_get() )
            if( targetUsername not in self.messages.keys() ):
                self.clientSocket.sendall( pickle.dumps( Command("get-messages", (self.username, targetUsername) ) ) )
            else:
                self.text.configure(state="normal")
                self.text.delete("1.0", "end")
                self.text.insert(tk.END, rowsToLines(self.messages[targetUsername]) )
                self.text.see(tk.END)
                self.text.configure(state="disabled")

            self.active_chat_window = targetUsername
        except:
            pass
    
    def getUserNameFromListBox(self, text:str):
        if text[0] == '@':
            return text[1:len(text)]
        else:
            return self.getUserNameFromListBox(text[1:len(text)])

    def sendMessage(self):
        targetUsername:str = self.active_chat_window
        if(len(targetUsername) > 0 and len( self.messageInput.get() ) > 0 ):
            messageContent = self.messageInput.get()
            self.clientSocket.sendall( pickle.dumps( Command("send-message", Message(self.username, targetUsername, messageContent ) ) ) )
            row = (self.username, targetUsername, messageContent)
            self.messages[targetUsername].append( row )
            self.text.configure(state="normal")
            self.text.insert(tk.END, "\n"+rowToMessageStr(row) )
            self.text.see(tk.END)
            self.text.configure(state="disabled")
            # reset input box
            self.messageInput.delete(0, tk.END)
            

    def addUserToList(self, username):
        self.UserListBox.insert(0, username)
