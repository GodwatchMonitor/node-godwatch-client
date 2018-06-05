import requests, json, socket, os, sys
import systrayicon
from simplecrypt import encrypt, decrypt

os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

appdata = os.getenv('LOCALAPPDATA')+"\\Samusoidal\\Godwatch Client\\";

def hashify(st):
    ns = "";
    i = 0;
    for l in st:
        ns += chr(ord(l)*(i+1));
        i += 1;
    return ns;

# METHODS

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

# HIDDEN
def report_hidden(*args):

    start_time = timeit.default_timer();

    settings = load_settings_hidden();

    try:

        rr = requests.put('http://' + settings[0] + '/clients/report/' + hashify(settings[3]), auth=(settings[1], settings[2]), json={ 'ip': getNetworkIp() });

        if rr.status_code == 200:
            retrieve_settings_hidden(settings, start_time);

    except:
        print("Error in report_hidden()");

def retrieve_settings_hidden(settings, start_time):

    try:

        rr = requests.get('http://' + settings[0] + '/clients/report/' + hashify(settings[3]), auth=(settings[1], settings[2]));

        if rr.status_code == 200:
            print(json.loads(rr.text)['interval'])
            save_settings_hidden(settings, json.loads(rr.text), start_time);

    except:
        print("Error in retrieve_settings_hidden()");

def load_settings_hidden():

    print(appdata+'settings.cfg')
    try:
        settings_file = open(appdata+'settings.cfg', 'rb+');
    except IOError:
        settings_file = open(appdata+'settings.cfg', 'wb+');

    try:
        settingsdecrypt = str(decrypt('$adClub72!_gq%', settings_file.read()));
        settings = settingsdecrypt.split('\\r\\n');
        print(settings);
        settings[0] = settings[0][2:]
        return settings
    except:
        print("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def save_settings_hidden(settings, data, start_time):
    nin = int(data['interval'])/1000;

    copyfile(appdata+'settings.cfg',appdata+'settings.cfg.bak');

    try:

        settings_file = open(appdata+'settings.cfg', 'wb+');
        data = settings[0] + '\r\n' + settings[1] + '\r\n' + settings[2] + '\r\n' + settings[3] + '\r\n' + str(data['interval']) + '\r\n'
        settings_file.write(encrypt('$adClub72!_gq%', bytes(data, 'utf8')));
        settings_file.close();

        os.remove(appdata+'settings.cfg.bak');

    except:
        copyfile(appdata+'settings.cfg.bak',appdata+'settings.cfg');
        os.remove(appdata+'settings.cfg.bak');

    nin -= (timeit.default_timer() - start_time);
    print(nin);

    reset_timer(nin);

def encrypt_settings(): # Reads and writes in bytes
    isettings_file = open(appdata+'initsettings.txt', 'rb');
    settings = isettings_file.read();
    isettings_file.close();

    settings_file = open(appdata+'settings.cfg', 'wb+');
    settings_file.write(encrypt('$adClub72!_gq%',settings));
    settings_file.close();

    os.remove(appdata+"initsettings.txt");

if __name__ == '__main__':
    import itertools, glob
    from threading import Event, Thread, Timer
    import timeit
    from shutil import copyfile

    icons = glob.glob('ico/*.ico')
    print(icons[0]);
    hover_text = "Godwatch Client"
    menu_options = (
        ('Report Now', None, report_hidden),
    )

    def switch_icon(icon):
        global sysicon
        sysicon.icon = icon;
        sysicon.refresh_icon();

    def reset_timer(newdelay):
        st = timeit.default_timer();
        global timer
        timer.cancel();
        timer = Timer(newdelay, report_hidden);
        timer.start();
        print(timeit.default_timer()-st)

    def bye(sysTrayIcon):
        timer.cancel();

    def init_settings():
        encrypt_settings();

    from pathlib import Path
    if Path(appdata+"initsettings.txt").is_file():
        init_settings();

    timer = Timer(5, report_hidden);
    timer.start();

    import ctypes
    try:
        admin_priv = os.getuid() == 0;
    except:
        admin_priv = ctypes.windll.shell32.IsUserAnAdmin() != 0;

    if not admin_priv:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)

    if admin_priv:
        sf = open("d.txt", "w+");
        sf.write(str(admin_priv));
        sf.close();

    systrayicon.SysTrayIcon(icons[0], hover_text, menu_options, on_quit=bye, default_menu_index=1);
