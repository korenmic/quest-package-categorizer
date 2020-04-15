# quest-package-categorizer
Quest app launcher Packages json Categories Manager library


Discussion:

https://www.facebook.com/groups/vrmai/permalink/1433336956848923/


Share the project:
http://tinyurl.com/qpc-mk-py


For this to work, it is mandatory that your quest has this installed first:

https://sidequestvr.com/#/app/199 / https://github.com/tverona1/QuestAppLauncher

run it at least once before using this script.


To Install:

wget https://github.com/korenmic/quest-package-categorizer/raw/master/qpc.py


Before running make sure the quest is connected to your device and that adb is installed


Usage example:

$ ./qpc.py

qpclib> pull

qpclib> continue

$ ./qpc.py "find_packages('hearth')"

[u'com.blizzard.wtcg.hearthstone']

$ ./qpc.py

qpclib> push

Done push



Note:

To refresh currently open Quest App Launcher's custom categories,

click on the ⚙️ gear icon

set Custom Tabs to Off, click on X, click the ⚙ gear icon again and turn it back on.
