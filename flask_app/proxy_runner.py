import subprocess
import os

PROXY_PORT = 8080

def enable_proxy():
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
              '/v ProxyEnable /t REG_DWORD /d 1 /f')
    os.system(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
              f'/v ProxyServer /t REG_SZ /d 127.0.0.1:{PROXY_PORT} /f')

def disable_proxy():
    os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" '
              '/v ProxyEnable /t REG_DWORD /d 0 /f')

def start_mitm():
    enable_proxy()
    subprocess.Popen(['mitmproxy', '-s', 'proxy_logic.py'])
