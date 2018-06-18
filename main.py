def log(mess):
    log = open(appdata+'logfile.log','a+');
    log.write(str(datetime.datetime.now()) + ":  " + mess+"\n");
    log.close();

def spit(mess):
    print(mess);
    log(mess);

# METHODS

def getNetworkIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]

def get_new_version(settings):

    try:

        newver = requests.get('http://' + settings[0] + '/clients/executable', auth=(settings[1], settings[2]), stream=True);
        with open('newver.exe', 'wb+') as f:
            f.write(newver.content);

        fn = sys.argv[0];
        os.rename(fn, fn+'.bak');
        os.rename('newver.exe', fn);

        os.startfile(fn);

        os._exit(0);

        return True

    except Exception:

        traceback.print_exc()

        return False


def report_and_retrieve(*args):

    start_time = timeit.default_timer();

    try:

        settings = load_settings_hidden();

        report = report_hidden(settings);

        if report.status_code == 200:

            retrieve = retrieve_settings_hidden(settings);

            if retrieve.status_code == 200:

                save = save_settings_hidden(settings, json.loads(retrieve.text)['interval']);

                if json.loads(retrieve.text)['version'] != version:

                    update = get_new_version(settings);

                    if update:
                        reset_timer(start_time, int(save)/1000);

                    else:
                        reset_timer(start_time, int(save)/1000);

                else:
                    reset_timer(start_time, int(save)/1000);

            else:

                reset_timer(start_time, int(settings[4])/1000);

        else:

            reset_timer(start_time, int(settings[4])/1000);

    except: # This is blocking sys.exit and any exceptions!!!

        reset_timer(start_time, int(settings[4])/1000);

def report_hidden(settings):

    rr = requests.put('http://' + settings[0] + '/clients/report/' + settings[3], auth=(settings[1], settings[2]), json={ 'ip': getNetworkIp(), 'version': version });

    return rr;

def retrieve_settings_hidden(settings):

    rr = requests.get('http://' + settings[0] + '/clients/report/' + settings[3], auth=(settings[1], settings[2]));

    return rr;

def save_settings_hidden(settings, interval):

    copyfile(appdata+'settings.cfg',appdata+'settings.cfg.bak');

    try:

        settings_file = open(appdata+'settings.cfg', 'wb+');
        data = settings[0] + '\r\n' + settings[1] + '\r\n' + settings[2] + '\r\n' + settings[3] + '\r\n' + str(interval) + '\r\n'
        settings_file.write(encrypt('$adClub72!_gq%', bytes(data, 'utf8')));
        settings_file.close();

        os.remove(appdata+'settings.cfg.bak');

        return interval;

    except:

        copyfile(appdata+'settings.cfg.bak',appdata+'settings.cfg');
        os.remove(appdata+'settings.cfg.bak');

        return settings[4];

def load_settings_hidden():

    try:
        settings_file = open(appdata+'settings.cfg', 'rb+');
    except IOError:
        settings_file = open(appdata+'settings.cfg', 'wb+');

    try:
        settingsdecrypt = str(decrypt('$adClub72!_gq%', settings_file.read()));
        settings = settingsdecrypt.split('\\r\\n');
        settings[0] = settings[0][2:]
        return settings
    except:
        spit("Invalid, missing, or corrupted settings file, ignoring...");

    settings_file.close();

def encrypt_settings(): # Reads and writes in bytes
    isettings_file = open(appdata+'initsettings.txt', 'rb');
    settings = isettings_file.read();
    isettings_file.close();

    settings_file = open(appdata+'settings.cfg', 'wb+');
    settings_file.write(encrypt('$adClub72!_gq%',settings));
    settings_file.close();

    os.remove(appdata+"initsettings.txt");

if __name__ == '__main__':
    import itertools, glob, timeit, requests, json, socket, os, sys, traceback, datetime
    from threading import Event, Thread, Timer
    from shutil import copyfile
    import systrayicon
    from simplecrypt import encrypt, decrypt

    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    appdata = os.getenv('LOCALAPPDATA')+"\\Samusoidal\\Godwatch Client\\";

    version = 0.2;

    spit('Started Godwatch Client');
    spit('Set working directory, appdata, and version.');
    spit('Version: ' + str(version));
    spit('appdata: ' + appdata);

    icons = glob.glob('ico/*.ico')
    hover_text = "Godwatch Client"
    menu_options = (
        ('Report Now', None, report_and_retrieve),
    )

    def switch_icon(icon):
        global sysicon
        sysicon.icon = icon;
        sysicon.refresh_icon();

    def reset_timer(start_time, interval):
        global timer
        timer.cancel();
        timer = Timer(abs(interval-(timeit.default_timer() - start_time)), report_and_retrieve);
        timer.start();
        print(timeit.default_timer())

    def bye(sysTrayIcon):
        timer.cancel();

    def init_settings():
        spit('Encrypting initial settings file.');
        encrypt_settings();

    from pathlib import Path
    if Path(appdata+"initsettings.txt").is_file():
        init_settings();

    spit('Removing previous versions...');
    if Path(sys.argv[0]+'.bak').is_file():
        os.remove(sys.argv[0]+'.bak');
        spit('Removed previous version');
    else:
        spit('No previous versions found');

    spit('Initialize timer...');
    timer = Timer(2, report_and_retrieve);
    timer.start()
    spit('Done.');

    import ctypes
    spit('Check administrator privileges.');
    try:
        admin_priv = os.getuid() == 0;
    except:
        admin_priv = ctypes.windll.shell32.IsUserAnAdmin() != 0;
    if not admin_priv:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
        spit('Either I have been denied necessary sustenance or my heir apparent has inherited them. Either way, I shall die now.');
        # POST-prompt
        os._exit(0);
    else:
        spit('Already had admin priveleges. It seems I have more power than I thought.');

    spit('Initialize the snazzy system tray icon...');
    systrayicon.SysTrayIcon(icons[0], hover_text, menu_options, on_quit=bye, default_menu_index=1);
