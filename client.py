from functools import partial
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkFont

from dependencies.client_main_window import MainWindow

class LoginForm:
    def __init__(self, root):
        self.root = root
        #setting title
        root.title("Chat App Login")
        #setting window size
        width=430
        height=57
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.TkEntry=tk.Entry(root)
        self.TkEntry["borderwidth"] = "1px"
        ft = tkFont.Font(family='Calibri',size=12)
        self.TkEntry["font"] = ft
        self.TkEntry["fg"] = "#333333"
        self.TkEntry["justify"] = "left"
        self.TkEntry["text"] = "Entry"
        self.TkEntry.place(x=150,y=10,width=168,height=30)

        TkLabel=tk.Label(root)

        TkLabel["font"] = ft
        TkLabel["fg"] = "#333333"
        TkLabel["justify"] = "left"
        TkLabel["text"] = "Enter your name"
        TkLabel.place(x=10,y=10,width=130,height=30)

        LoginButton=tk.Button(root, command=self.enterApplicaiton)
        LoginButton["bg"] = "#efefef"

        LoginButton["font"] = ft
        LoginButton["fg"] = "#000000"
        LoginButton["justify"] = "center"
        LoginButton["text"] = "Login"
        LoginButton.place(x=330,y=10,width=90,height=30)

    def enterApplicaiton(self):
        username = self.TkEntry.get()
        if ( len(username) > 0 ):
            self.root.destroy()
            self.root = tk.Tk()
            MainWindow(self.root, username)
            self.root.mainloop()
        else:
            messagebox.showerror("Error","Username can not be empty")


if __name__ == "__main__":
    root = tk.Tk()
    LoginForm(root)
    root.mainloop()
