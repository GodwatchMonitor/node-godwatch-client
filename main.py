import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json, socket
import systrayicon

root = Tk();
root.title("node-Godwatch Client")
root.geometry("320x200");
root.resizable(0, 0);

def hashify(st):
    ns = "";
    i = 0;
    for l in st:
        ns += chr(ord(l)*(i+1));
        i += 1;
    return ns;

str_cname = StringVar();
str_cname.set(socket.gethostname());
str_chash = StringVar();
str_chash.set(hashify(str_cname.get()));
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
    rr = requests.put('http://' + str_server.get() + '/clients/report/' + str_chash.get(), auth=(str_username.get(), str_password.get()), json={ 'ip': getNetworkIp(), 'interval': str_cinterval.get() });

    if rr.status_code == 200:
        retrieve_settings();

def retrieve_settings():
    rr = requests.get('http://' + str_server.get() + '/clients/report/' + str_chash.get(), auth=(str_username.get(), str_password.get()));

    if rr.status_code == 200:
        str_cinterval = json.loads(rr.text)['interval'];

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
        str_cname.set(settings[3][:-1]);
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n' + str_cname.get() + '\n');
    settings_file.close();

config_page = Frame(root, width=300, height=110, pady=10);

config_page_f1 = Frame(config_page);
label_server = Label(config_page_f1, text="Server");
input_server = Entry(config_page_f1, textvariable=str_server);
input_server.insert(0, "server:port");
label_server.grid(row=1,column=1);
input_server.grid(row=1,column=2);

label_username = Label(config_page_f1, text="Username");
input_username = Entry(config_page_f1, textvariable=str_username);
label_username.grid(row=2,column=1);
input_username.grid(row=2,column=2);

label_password = Label(config_page_f1, text="Password");
input_password = Entry(config_page_f1, textvariable=str_password, show="*");
label_password.grid(row=3,column=1);
input_password.grid(row=3,column=2);
config_page_f1.grid(row=1,column=1,sticky=W);

config_page_f2 = Frame(config_page, padx=20);
button_saveSettings = Button(config_page_f2, text="Save Settings", command=save_settings);
button_saveSettings.grid(row=1,column=1);
button_retrieveData = Button(config_page_f2, text="Retrieve Settings", command=save_settings);
button_retrieveData.grid(row=2,column=1);
config_page_f2.grid(row=1,column=2,sticky=E);

config_page.grid(row=1,column=1);

settings_page = Frame(root, width=300, height=110, pady=10);

label_cname = Label(settings_page, text="Name: ");
input_cname = Label(settings_page, textvariable=str_cname);
label_cname.grid(row=1,column=1,sticky=E);
input_cname.grid(row=1,column=2,sticky=W);

label_chash = Label(settings_page, text="Hash: ");
input_chash = Entry(settings_page, textvariable=str_chash, state='readonly', readonlybackground='white', fg='black');
label_chash.grid(row=2,column=1,sticky=E);
input_chash.grid(row=2,column=2,sticky=W);

label_cinterval = Label(settings_page, text="Interval: ");
input_cinterval = Entry(settings_page, textvariable=str_cinterval);
label_cinterval.grid(row=3,column=1,sticky=E);
input_cinterval.grid(row=3,column=2,sticky=W);

button_report = Button(config_page_f2, text="Report Now", command=report);
button_report.grid(row=4,column=1);

settings_page.grid(row=2,column=1);

load_settings();

root.mainloop();
