import tkinter as tk
from tkinter import font as tkFont

class TagForm:
    def __init__(self, root, forUser, window):
        self.root = root
        self.forUser = forUser
        self.window = window
        root.title("Assign tag for user %s" % (forUser,))
        width=310
        height=50
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.TkEntry=tk.Entry(root)
        self.TkEntry["borderwidth"] = "1px"
        ft = tkFont.Font(family='Calibri',size=11)
        self.TkEntry["font"] = ft
        self.TkEntry["fg"] = "#333333"
        self.TkEntry["justify"] = "left"
        if(forUser in window.tags.keys()):
            self.TkEntry.insert(tk.END, window.tags[forUser])
        self.TkEntry.place(x=5,y=12,width=180,height=25)

        AssignButton=tk.Button(root, command=self.assignTag)
        AssignButton["bg"] = "#efefef"
        AssignButton["font"] = ft
        AssignButton["fg"] = "#000000"
        AssignButton["justify"] = "center"
        AssignButton["text"] = "Assign"
        AssignButton.place(x=210,y=12,width=95,height=25)

        root.attributes('-topmost',True)
        #self.stayOnTop()
    
    def assignTag(self):
        self.window.tags[self.forUser] = self.TkEntry.get()
        self.window.updateUserListBox()
        self.root.destroy()

    def stayOnTop(self):
        self.root.lift()
        self.root.after(2000, self.stayOnTop)