import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json, socket

root = Tk();
root.title("node-Godwatch Client")
root.geometry("300x100");
root.resizable(0, 0);

str_cname = StringVar();
str_cname.set("");
str_chash = StringVar();
str_chash.set("");
str_cinterval = StringVar();
str_cinterval.set("");
int_cenabled = IntVar();
int_cenabled.set(1);

str_server = StringVar();
str_server.set("");
str_username = StringVar();
str_password = StringVar();

# METHODS
def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

def report():
    pass

def load_settings():
    try:
        settings_file = open('settings.txt', 'r+');
    except IOError:
        settings_file = open('settings.txt', 'w+');

    try:
        settings = settings_file.readlines();
        str_server.set(settings[0][:-1]);
        str_username.set(settings[1][:-1]);
        str_password.set(settings[2][:-1]);
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n');
    settings_file.close();



root.mainloop();
