import subprocess
from threading import Thread
import os, platform
import sys


PATH = os.path.dirname(os.path.realpath(__file__))

os_name = platform.system()

if os_name == "Windows":
    subprocess.run([PATH+'\\run.bat'])
elif os_name =="Linux":
    subprocess.run([PATH+"\\run.sh"])