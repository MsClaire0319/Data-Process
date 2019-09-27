# coding: utf8
# created by FeiFei Liu on Sep 17, 2019

import os.path
import subprocess
import time


VPN_PATH = r'c:\Root\ShadowsocksR-win-4.9.2\ShadowsocksR-dotnet4.0.exe'


def main():

    # ensure shadowsocks is turn on
    predicate_proxy()

    #========= your script here ==============
    #
    #=========================================

    # stop shadowsocks
    shutdown_proxy()

    print('ok')



def shutdown_proxy(vpnpath=VPN_PATH):
    '''Kill all vpn procedures (Shadowsocks, efan) and disable proxy'''

    killcmd = 'powershell Stop-Process -Name shadowsocks*,efan*'
    subprocess.call(killcmd)

    disproxy = "powershell Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' ProxyEnable -Value 0"
    subprocess.call(disproxy)

def invoke_proxy(vpnpath=VPN_PATH):
    '''Invoke the shadowsocks and pause for 5s.'''

    proc = subprocess.Popen(vpnpath, shell=False)
    time.sleep(5)
    return proc

def predicate_proxy(vpnpath=VPN_PATH):
    '''Ensure the Shadowsocks is invoked.'''

    exe = os.path.basename(vpnpath)
    listcmd = 'TASKLIST /FI "IMAGENAME EQ {}"'.format(exe)
    output = subprocess.check_output(listcmd).decode('gb18030')
    print(output)

    if 'PID' in output:
        print('{} already started!\n'.format(exe))
    else:
        invoke_proxy(vpnpath)


if __name__ == '__main__': main()
