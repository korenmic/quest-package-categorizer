# quest-package-categorizer
Quest app launcher Packages json Categories Manager library


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
