import configparser
from tkinter import Tk, Button
import tkinter.filedialog as tkfd

def choosefolder():
    config["CONFIG"]["webroot"] = tkfd.askdirectory(title="Web root")
    CFGwrite()

def CFGwrite():
    with open(CONFIG_FILE, "w") as cfg:
        config.write(cfg)

root = Tk()

Button(root, text="Choose web root", command=choosefolder).pack()

CONFIG_FILE = "config.cfg"

config = configparser.ConfigParser()

config["CONFIG"] = {
    "participants": [
        1,2,3,4
    ],
    "webroot": "",
}
CFGwrite()

root.mainloop()