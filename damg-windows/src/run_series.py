import subprocess

cmd = 'C:\\dam' + 'g\\bin\\dam_high_frequency.exe series'
pip = subprocess.Popen(args=cmd,
                       shell=True,
                       creationflags=subprocess.CREATE_NEW_CONSOLE)