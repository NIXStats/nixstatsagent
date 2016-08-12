import sys
import os


def run(config):
    disk = {}
    if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
        disk['df'] = [s.split() for s in os.popen("df -Pl").read().splitlines()]
        disk['di'] = [s.split() for s in os.popen("df -iPl").read().splitlines()]
    elif sys.platform == "win32":
        c = wmi.WMI ()
        for d in c.Win32_LogicalDisk():
            disk['windows'] = ( d.Caption, d.FreeSpace, d.Size, d.DriveType)
    return disk
