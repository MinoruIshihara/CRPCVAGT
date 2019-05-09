import os
import subprocess

os.system('sudo ip link set can0 up type can bitrate 500000')
os.system('python3 test0325.py')
