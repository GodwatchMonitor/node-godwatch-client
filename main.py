import requests, json, socket
import systrayicon

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

    settings = load_settings_hidden();

    try:

        rr = requests.put('http://' + settings[0][:-1] + '/clients/report/' + hashify(settings[3][:-1]), auth=(settings[1][:-1], settings[2][:-1]), json={ 'ip': getNetworkIp() });

        if rr.status_code == 200:
            retrieve_settings_hidden(settings, rr.elapsed.total_seconds());

    except:
        print("Error in report_hidden()");

def retrieve_settings_hidden(settings, time1):

    try:

        rr = requests.get('http://' + settings[0][:-1] + '/clients/report/' + hashify(settings[3][:-1]), auth=(settings[1][:-1], settings[2][:-1]));

        if rr.status_code == 200:
            save_settings_hidden(settings, json.loads(rr.text), time1, rr.elapsed.total_seconds());

    except:
        print("Error in retrieve_settings_hidden()");

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

def save_settings_hidden(settings, data, time1, time2):
    settings_file = open('settings.txt', 'w+');
    settings_file.write(settings[0][:-1] + '\n' + settings[1][:-1] + '\n' + settings[2][:-1] + '\n' + settings[3][:-1] + '\n' + str(data['interval']) + '\n');
    settings_file.close();

    nin = int(data['interval'])/1000;
    nin -= time1;
    nin -= time2;

    reset_timer(nin);

if __name__ == '__main__':
    import itertools, glob

    icons = itertools.cycle(glob.glob('*.ico'))
    hover_text = "Godwatch Client"
    menu_options = (
        ('Report Now', None, report_hidden),
    )

    def switch_icon(icon):
        global sysicon
        sysicon.icon = icon;
        sysicon.refresh_icon();

    from threading import Event, Thread
    def call_repeatedly(interval, func, *args):
        stopped = Event()
        def loop():
            while not stopped.wait(interval): # the first call is in `interval` secs
                func(*args)
        Thread(target=loop).start()
        return stopped.set

    def reset_timer(newdelay):
        global timer
        timer()
        timer = call_repeatedly(newdelay, report_hidden);

    def bye(sysTrayIcon):
        timer()

    timer = call_repeatedly(0.1, report_hidden);

    systrayicon.SysTrayIcon(next(icons), hover_text, menu_options, on_quit=bye, default_menu_index=1);
