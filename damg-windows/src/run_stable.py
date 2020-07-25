import subprocess

cmd = 'C:\\dam' + 'g\\bin\\dam_collect.exe plan'
pip = subprocess.Popen(args=cmd,
                       shell=True,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)
