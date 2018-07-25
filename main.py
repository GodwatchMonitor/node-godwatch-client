import itertools, glob, timeit, requests, json, socket, os, sys, traceback, datetime
from threading import Event, Thread, Timer
from shutil import copyfile
from simplecrypt import encrypt, decrypt
import win32serviceutil, win32service, win32event, servicemanager
from pathlib import Path
import datetime

class GodwatchService(win32serviceutil.ServiceFramework):
    _svc_name_ = "GodwatchClient"
    _svc_display_name_ = "Godwatch Client Service"
    _svc_description_ = "Service for Godwatch Monitor Client"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args);
        self.hWaitStop = win32event.CreateEvent(None,0,0,None);
        socket.setdefaulttimeout(60);

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop);
        self.application.cancelled = True

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_,''))
        self.started = False;
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        rc = None;

        while rc != win32event.WAIT_OBJECT_0:

            if not self.started:
                self.application = GodwatchApp(None);
                self.started = True;

            rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)

    def templog(self, mess):
        log = open('C:\\temp\\gwlogfile.log','a+');
        log.write(str(datetime.datetime.now()) + ":  " + mess+"\n");
        log.close();

    def spit(self, mess):
        #print(mess);
        #servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_,'mess'))
        #self.templog(mess);
        pass;

class GodwatchApp(Thread):

    def __init__(self,args):

        Thread.__init__(self);
        self.cancelled = False;
        self.main()

    def log(self, mess):
        log = open(self.appdata+datetime.datetime.today().strftime('%Y-%m-%d')+'_logfile.log','a+');
        log.write(str(datetime.datetime.now()) + ":  " + mess+"\n");
        log.close();

    def templog(self, mess):
        log = open('C:\\temp\\gwlogfile.log','a+');
        log.write(str(datetime.datetime.now()) + ":  " + mess+"\n");
        log.close();

    def spit(self, mess):
        #print(mess);
        #servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE, servicemanager.PYS_SERVICE_STARTED, (self._svc_name_,''))
        #self.log(mess);
        self.log(mess);
        pass;

    # METHODS
    def getNetworkIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('<broadcast>', 0))
        return s.getsockname()[0]

    def get_new_version(self, settings):

        try:

            newver = requests.get('http://' + settings[0] + '/clients/executable', auth=(settings[1], settings[2]), stream=True);
            with open('newver.exe', 'wb+') as f:
                f.write(newver.content);

            fn = sys.argv[0];
            os.rename(fn, fn+'.bak');
            os.rename('newver.exe', fn);

            batch = open(self.appdata+"restart.bat", "a+");
            batch.write("%SYSTEMDRIVE%\n");
            batch.write("timeout /t 2\n");
            batch.write("sc start GodwatchClient");
            batch.close();

            try:
                from subprocess import DEVNULL
            except ImportError:
                DEVNULL = os.open(os.devnull, os.O_RDWR)

            import subprocess
            subprocess.Popen(["restart.bat"], stdout=DEVNULL, stdin=DEVNULL, stderr=DEVNULL, shell=True)

            os._exit(0);

            return True

        except Exception:

            self.spit(traceback.format_exc());

            return False

    def report_and_retrieve(self):

        self.spit("Beginning report...");

        start_time = timeit.default_timer();

        try:

            self.spit("Reporting...");
            report = self.report_hidden(self.settings);

            if report.status_code == 200:
                self.spit("OK");

                self.spit("Retrieving...");
                retrieve = self.retrieve_settings_hidden(self.settings);

                if retrieve.status_code == 200:
                    self.spit("OK");

                    self.spit("Saving...");
                    save = self.save_settings_hidden(self.settings, json.loads(retrieve.text)['interval']);
                    self.spit("OK");

                    if json.loads(retrieve.text)['version'] != self.version:

                        self.spit("New version available, installing...")
                        update = self.get_new_version(self.settings);

                        if update:
                            self.spit("OK");
                            self.reset_timer(start_time, int(save)/1000);

                        else:
                            self.spit("Update failed, please update manually.")
                            self.remove_previous_versions()
                            self.reset_timer(start_time, int(save)/1000);

                    else:
                        self.reset_timer(start_time, int(save)/1000);

                else:
                    self.reset_timer(start_time, int(self.settings[4])/1000);

            else:
                self.reset_timer(start_time, int(self.settings[4])/1000);

        except:
            self.spit(traceback.format_exc());
            self.reset_timer(start_time, int(self.settings[4])/1000);

        self.spit("Done");

    def report_hidden(self, settings):

        rr = requests.put('http://' + settings[0] + '/clients/report/' + settings[3], auth=(settings[1], settings[2]), json={ 'ip': self.getNetworkIp(), 'version': self.version });

        return rr;

    def retrieve_settings_hidden(self, settings):

        rr = requests.get('http://' + settings[0] + '/clients/report/' + settings[3], auth=(settings[1], settings[2]));
        self.spit("Retrieve: " + str(rr.status_code))
        return rr;

    def save_settings_hidden(self, settings, interval):

        copyfile(self.appdata+'settings.cfg',self.appdata+'settings.cfg.bak');

        try:

            settings_file = open(self.appdata+'settings.cfg', 'wb+');
            data = settings[0] + '\r\n' + settings[1] + '\r\n' + settings[2] + '\r\n' + settings[3] + '\r\n' + str(interval) + '\r\n'
            settings_file.write(encrypt('$adClub72!_gq%', bytes(data, 'utf8')));
            settings_file.close();

            os.remove(self.appdata+'settings.cfg.bak');

            return interval;

        except:

            copyfile(self.appdata+'settings.cfg.bak',self.appdata+'settings.cfg');
            os.remove(self.appdata+'settings.cfg.bak');

            return settings[4];

    def load_settings_hidden(self):

        try:
            settings_file = open(self.appdata+'settings.cfg', 'rb+');
        except IOError:
            settings_file = open(self.appdata+'settings.cfg', 'wb+');

        try:
            settingsdecrypt = str(decrypt('$adClub72!_gq%', settings_file.read()));
            settings = settingsdecrypt.split('\\r\\n');
            settings[0] = settings[0][2:]
            return settings
        except:
            self.spit("Invalid, missing, or corrupted settings file, ignoring...");
            blank = []
            return blank

        settings_file.close();

    def encrypt_settings(self): # Reads and writes in bytes
        isettings_file = open(self.appdata+'initsettings.txt', 'rb');
        settings = isettings_file.read();
        isettings_file.close();

        settings_file = open(self.appdata+'settings.cfg', 'wb+');
        settings_file.write(encrypt('$adClub72!_gq%',settings));
        settings_file.close();

        os.remove(self.appdata+"initsettings.txt");

    def reset_timer(self, start_time, interval):
        if self.cancelled:
            os._exit(0);
        else:
            self.timer.cancel();
            self.timer = Timer(abs(interval-(timeit.default_timer() - start_time)), self.report_and_retrieve);
            self.timer.start();

    def init_settings(self):
        self.spit('Encrypting initial settings file.');
        self.encrypt_settings();

    def remove_previous_versions(self):
        if Path(sys.argv[0]+'.bak').is_file():
            os.remove(sys.argv[0]+'.bak');
            self.spit('Removed previous version');
        else:
            self.spit('No previous versions found');

    def main(self):

        os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

        self.appdata = os.path.dirname(os.path.abspath(sys.argv[0]))+"\\"

        self.version = 0.43

        self.spit('Started Godwatch Client');
        self.spit('Set working directory, appdata, and version.')
        self.spit('Version: ' + str(self.version));
        self.spit('appdata: ' + self.appdata);

        if Path(self.appdata+"initsettings.txt").is_file():
            self.init_settings();

        if Path(self.appdata+"restart.bat").is_file():
            os.remove(self.appdata+"restart.bat");

        self.settings = self.load_settings_hidden()

        self.spit('Removing previous versions...')
        self.remove_previous_versions()

        self.spit('Initialize timer...');
        self.timer = Timer(2, self.report_and_retrieve);
        self.timer.start()
        self.spit('Done.');

        import ctypes, subprocess
        self.spit('Check administrator privileges.');
        try:
            admin_priv = os.getuid() == 0;
        except:
            admin_priv = ctypes.windll.shell32.IsUserAnAdmin() != 0;
        if not admin_priv:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "", None, 1)
            self.spit('Either I have been denied necessary sustenance or my heir apparent has inherited them. Either way, I shall die now.');
            # POST-prompt
            os._exit(0);
        else:
            self.spit('Already had admin priveleges. It seems I have more power than I thought.');

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(GodwatchService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(GodwatchService)
