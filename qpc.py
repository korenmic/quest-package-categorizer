#!/usr/bin/python
"""
Quest app launcher Packages json Categories Manager library

unofficial

Made by:

 __  __ _      _                _   _  __                    
|  \/  (_) ___| |__   __ _  ___| | | |/ /___  _ __ ___ _ __  
| |\/| | |/ __| '_ \ / _` |/ _ \ | | ' // _ \| '__/ _ \ '_ \ 
| |  | | | (__| | | | (_| |  __/ | | . \ (_) | | |  __/ | | |
|_|  |_|_|\___|_| |_|\__,_|\___|_| |_|\_\___/|_|  \___|_| |_|



Usage:
> qpm.py pull
> qpm.py "find_packages('<PARTIAL PACKAGES NAME>')"
FULL_PACKAGE_NAME1, FULL_PACKAGE_NAME2
> qpm.py 'categorize_names("<CATEGORY NAME>", "<PARTIAL PACKAGES NAME>")'
> qpm.py push

Now refresh Quest App Launcher's 'Cutstom Tabs' view by turning it 'Off' and on again
changes should apply.

Notes:
 * pull is only required for the first run.
 * qpm can be used as both a cli and a shell, when in cli '()' of funcs is optional
 * To leave qpm shell run 'c' 'continue' 'q' or CTRL+D just like in pdb

"""


import os as _os
from platform import release as _release
from sys import argv as _argv
import json as _json
import subprocess as _subprocess


def _jfy(path):
    return _json.loads(open(path, 'r').read())


_DEFAULT_CATEGORY = 'unsorted'
_APPNAMES_PATH = 'appnames_all.json'
_REMOTE_APPNAMES_FOLDER_PATH = '/sdcard/Android/data/aaa.QuestAppLauncher.App/files/download_cache'

_ADB_PATH = None

APPS = None


def list_categories():
    """ Get list of all categories currently in use """
    return tuple(set(APPS[k]['category'] for k in APPS))


def _get_adb_path():
    global _ADB_PATH
    if _ADB_PATH is not None:
        return _ADB_PATH
    adb_path = _os.getenv("ADB_PATH")
    if adb_path:
        _ADB_PATH = adb_path
    elif _os.name == 'nt' or 'Microsoft' in _release(): # windows or wsl
        appdata = _os.getenv("APPDATA", _os.path.join('/mnt/c/Users/', _os.getenv("USER"), 'AppData', 'Roaming'))
        sq_adb = _os.path.join(appdata, 'SideQuest', 'platform-tools', 'adb.exe')
        if _os.path.exists(sq_adb):
            _ADB_PATH = sq_adb
    else: # posix
        installed_adb = _os.popen('which adb').read().strip()
        if installed_adb:
            _ADB_PATH = installed_adb

    assert _ADB_PATH is not None, "Could not find adb, either install it or set ADB_PATH"
    print("Found adb at {}".format(_ADB_PATH))
    return _ADB_PATH


def _run_adb_command(command):
    command_line = '{} {}'.format(_get_adb_path(), command)
    process = _subprocess.Popen(
        command_line,
        stdout=_subprocess.PIPE,
        stderr=_subprocess.PIPE,
        stdin=_subprocess.PIPE,
        close_fds=True,
        shell=True)
    result = process.stdout.read()
    if not isinstance(result, str):
        # python3 support
        result = result.decode('utf-8')
    return result

def _adb_on_device(command):
    try:
        device_serial = _run_adb_command('devices').strip().splitlines()[-1].split()[0]
        assert device_serial
    except Exception as e:
        print(e.message)
        print("Could not find quest device via adb, make sure it is connected and that adb is installed")
        exit(1)
    command_line = "-s {} {}".format(device_serial, command)
    return _run_adb_command(command_line)


def list_all_packages():
    """ That are installed on the quest """
    packages_raw = _adb_on_device("shell 'pm list packages -f'")
    packages_list = [package_line.split('=')[-1] for package_line in packages_raw.splitlines()]
    print("Found {} packages on the quest".format(len(packages_list)))
    return packages_list


def get_unhandled_packages():
    """ Get list of packages that are new but aren't set in the json yet """
    print("Scanning for new unhandled packages...")
    packages_list = list_all_packages()
    handled_packages = tuple(APPS.keys())
    packages_to_ignore = ('aaa.QuestAppLauncher.App', )
    new_unhandled_packages = tuple(set(packages_list) - set(handled_packages) - set(packages_to_ignore))
    if not new_unhandled_packages:
        print("Nothing new")
    else:
        print("{} new packages".format(len(new_unhandled_packages)))
    return new_unhandled_packages


def commit_unhandled():
    """ Update local json object with new unhandled packages """
    for unhandled_package in get_unhandled_packages():
        # TODO - new names could be taken from actual downloadRepoUri from
        # config.json and be used as package only if missing from the repo
        APPS[unhandled_package] = dict(name=unhandled_package, category=_DEFAULT_CATEGORY)


def find_packages(*names):
    """ Show what is used when sending names to categorize_names """
    packages = []
    for name in names:
        for package in APPS:
            package_name = APPS[package]['name']
            if name.lower() in package.lower() or name.lower() in package_name.lower():
                packages.append(package)
    return packages
            

def categorize_names(category, *names):
    """
    Set category for all packages that partially match names
    categorize_names("Utils", "partial util name goes here")
    """
    for package in find_packages(*names):
        current_category = APPS[package].get('category')
        APPS[package]['category'] = category
        if not current_category:
            print("Set category of {package} to {category}".format(**locals()))
        elif current_category != category:
            print("Changed category of {package} from {current_category} to {category}".format(**locals()))


def update():
    """ Write json to the local file """
    with open(_APPNAMES_PATH, 'w') as f:
        import json
        f.write(json.dumps(APPS))
        f.flush()


def push():
    """ Write json file to the quest """
    update()
    _adb_on_device('push {} {}'.format(_APPNAMES_PATH, _REMOTE_APPNAMES_FOLDER_PATH))


def pull(quiet=False):
    """ Should only be done once at the first time used """
    global APPS
    if _os.path.exists(_APPNAMES_PATH):
        if not quiet:
            print("Can't pull, {} exists. to overwrite first manually delete the file.".format(_APPNAMES_PATH))
        APPS = _jfy(_APPNAMES_PATH)
        return
    remote_path = _os.path.join(_REMOTE_APPNAMES_FOLDER_PATH, _APPNAMES_PATH)
    result = _adb_on_device('pull {} ./'.format(remote_path))
    if not _os.path.exists(_APPNAMES_PATH):
        # Failed to pull because file does not exist on quest
        print("Never installed before, installing")
        APPS = dict()
        for json in 'appnames_quest.json', 'appnames_other.json':
            full_path = _os.path.join(_REMOTE_APPNAMES_FOLDER_PATH, json)
            _adb_on_device('pull {}'.format(full_path))
            new_apps = _jfy(json)
            #_os.
            [app.update(category=_DEFAULT_CATEGORY) for app in new_apps.values()]
            APPS.update(new_apps)
        commit_unhandled()
        update()
        print("Local installation complete, created a new json locally, to apply on quest run push()")
    else:
        APPS = _jfy(_APPNAMES_PATH)
        print("Pulled a new json")
    print("In total {} packages documented in json".format(len(APPS)))


FROZEN_LOCALS = [k for k in locals().keys() if not k.startswith('_')]
# Below this point it is safe to declare without '_' prefix as it won't be added to local_keys


from pdb import Pdb

class QPCCmd(Pdb, object):
    prompt = 'qpclib> '

    @staticmethod
    def _get_doc(at_name):
        at = globals().get(at_name)
        if not callable(at) or not getattr(at, '__doc__', None):
            return ''
        return ' - ' + at.__doc__.strip()
    
    @staticmethod
    def _get_help():
        return 'commands and variables:\n' + \
            '\n'.join((" " + at + QPCCmd._get_doc(at)) for at in FROZEN_LOCALS)

    @classmethod
    def get_intro(cls):
        new_packages = get_unhandled_packages()
        
        intro = 'categories:\n' + \
                '\n'.join(" '{}'".format(cat) for cat in list_categories()) + '\n' + \
                QPCCmd._get_help() + '\n' \
                "help for more commands (same as pdb's help)\n" + \
                (('New packages: \n' + '\n'.join(new_packages)) if new_packages else '')
        return intro.strip()

    def __init__(self, *args, **kwargs):
        super(QPCCmd, self).__init__(*args, **kwargs)
        pull(quiet=True)
        self.prompt = QPCCmd.prompt
        self.intro = self.get_intro()


def main():
    qpccmd = QPCCmd()
    if not _argv or __file__ == _argv[-1]:
        return qpccmd.set_trace()
    elif _argv[-1]:
        command = _argv[-1]
        if command == 'help':
            print(qpccmd.intro)
            return
        if command in FROZEN_LOCALS:
            if command != 'pull':
                # because it is already done in QPCCmd.__init__ anyways
                globals().get(command)()
        elif any(command.startswith(fl) for fl in FROZEN_LOCALS):
            exec("result = {}".format(command), globals(), locals())
            print(result)
        if not command.startswith('update'):
            update()
        print("Done {}".format(_argv[-1]))

if __name__ == '__main__':
    #current_folder = _os.path.split(_os.path.abspath(__file__))[0]
    main()
else:
    APPS = _jfy(_APPNAMES_PATH)