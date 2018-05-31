import tkinter as tk
from tkinter import *
from tkinter import ttk
import requests, json, socket
import systrayicon
import datetime

mmw = Tk();
mmw.withdraw();

root = Toplevel(mmw);
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

# SHOWN
def report(*args):

    rr = requests.put('http://' + str_server.get() + '/clients/report/' + str_chash.get(), auth=(str_username.get(), str_password.get()), json={ 'ip': getNetworkIp(), 'interval': int(str_cinterval.get()) });

    if rr.status_code == 200:
        retrieve_settings();

def retrieve_settings():

    rr = requests.get('http://' + str_server.get() + '/clients/report/' + str_chash.get(), auth=(str_username.get(), str_password.get()));

    if rr.status_code == 200:
        str_cinterval.set(json.loads(rr.text)['interval']);

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
        str_cinterval.set(str(int(settings[4][:-1])));
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings():
    settings_file = open('settings.txt', 'w+');
    settings_file.write(str_server.get() + '\n' + str_username.get() + '\n' + str_password.get() + '\n' + str_cname.get() + '\n' + str_cinterval.get() + '\n');
    settings_file.close();
    reset_timer(int(str_cinterval.get())/1000);

# HIDDEN
def report_hidden(*args):

    settings = load_settings_hidden();

    rc = requests.get('http://' + settings[0][:-1] + '/clients/report/' + hashify(settings[3][:-1]), auth=(settings[1][:-1], settings[2][:-1]));
    if rc.status_code == 200:
        nd = json.loads(rc.text);

    rr = requests.put('http://' + settings[0][:-1] + '/clients/report/' + hashify(settings[3][:-1]), auth=(settings[1][:-1], settings[2][:-1]), json={ 'ip': getNetworkIp(), 'interval': nd['interval'] });

    if rr.status_code == 200:
        retrieve_settings_hidden(settings, rc.elapsed.total_seconds(), rr.elapsed.total_seconds());

def retrieve_settings_hidden(settings, time1, time2):

    rr = requests.get('http://' + settings[0][:-1] + '/clients/report/' + hashify(settings[3][:-1]), auth=(settings[1][:-1], settings[2][:-1]));

    if rr.status_code == 200:
        save_settings_hidden(settings, json.loads(rr.text), time1, time2, rr.elapsed.total_seconds());

def load_settings_hidden():

    try:
        settings_file = open('settings.txt', 'r+');
    except IOError:
        settings_file = open('settings.txt', 'w+');

    try:
        settings = settings_file.readlines();
        return settings
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings_hidden(settings, data, time1, time2, time3):
    settings_file = open('settings.txt', 'w+');
    settings_file.write(settings[0][:-1] + '\n' + settings[1][:-1] + '\n' + settings[2][:-1] + '\n' + settings[3][:-1] + '\n' + str(data['interval']) + '\n');
    settings_file.close();

    nin = int(data['interval'])/1000;
    nin -= time1;
    nin -= time2;
    nin -= time3;

    print(nin);

    reset_timer(nin);


# GUI
def build_gui(root):
    try:
        dummy = Frame(root);
    except:
        root = Toplevel(mmw);
        root.title("node-Godwatch Client")
        root.geometry("320x200");
        root.resizable(0, 0);

    config_page = Frame(root, width=300, height=110, pady=10);

    config_page_f1 = Frame(config_page);
    label_server = Label(config_page_f1, text="Server");
    input_server = Entry(config_page_f1, textvariable=str_server);
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

    button_minimize = Button(config_page_f2, text="SysTray", command=lambda arg=root: minimize_to_tray(root));
    button_minimize.grid(row=5,column=1);

    settings_page.grid(row=2,column=1);

    root.protocol("WM_DELETE_WINDOW", lambda arg=root: minimize_to_tray(root));

    #root.mainloop();

if __name__ == '__main__':
    import itertools, glob

    def quit_app():
        mmw.destroy();

    gui_up = False;

    def minimize_to_tray(root):
        global gui_up;
        gui_up = False;
        root.destroy();
        systrayicon.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1);

    def maximize_to_gui(sysTrayIcon):
        global gui_up;
        gui_up = True;
        sysTrayIcon.execute_menu_option(1025);
        build_gui(root);

    icons = itertools.cycle(glob.glob('*.ico'))
    hover_text = "Godwatch Client"
    menu_options = (
        ('View GUI', None, maximize_to_gui),
        ('Report Now', None, report),
    )

    from threading import Event, Thread
    def call_repeatedly(interval, func, *args):
        stopped = Event()
        def loop():
            while not stopped.wait(interval): # the first call is in `interval` secs
                func(*args)
        Thread(target=loop).start()
        return stopped.set

    def report_dummy():
        print("Report");

    def reset_timer(newdelay):
        global timer
        timer()
        timer = call_repeatedly(newdelay, report_hidden);

    def bye(sysTrayIcon):
        if not gui_up:
            timer()
            mmw.destroy();

    load_settings();

    timer = call_repeatedly(5, report_hidden);

    systrayicon.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1);
    mmw.mainloop();
